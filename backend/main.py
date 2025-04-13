from fastapi import FastAPI, Query, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from typing import Dict
import asyncio
from llama_cpp import Llama
import os
import math
import ctypes
import llama_cpp
import random
import json
import platform
import sys
from pathlib import Path

# Determine the correct library extension based on platform
if platform.system() == "Darwin":
    lib_extension = "dylib"
elif platform.system() == "Linux":
    lib_extension = "so"
elif platform.system() == "Windows":
    lib_extension = "dll"
else:
    raise OSError(f"Unsupported platform: {platform.system()}")

# Try to find the library dynamically
try:
    # Method 1: Try using Python's package infrastructure
    import llama_cpp
    package_dir = Path(llama_cpp.__file__).parent
    
    # Check for lib64 on Linux (EC2)
    if platform.system() == "Linux":
        lib_path = str(package_dir / "lib64" / f"libllama.{lib_extension}")
        if not os.path.exists(lib_path):
            # Fallback to lib if lib64 doesn't exist
            lib_path = str(package_dir / "lib" / f"libllama.{lib_extension}")
    else:
        # Mac uses lib directory
        lib_path = str(package_dir / "lib" / f"libllama.{lib_extension}")
    
    print(f"Looking for library at: {lib_path}")
    if not os.path.exists(lib_path):
        print(f"WARNING: Library file not found at {lib_path}")
        
    lib = ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
    print(f"Successfully loaded C library from {lib_path}")
except Exception as e:
    print(f"Failed to load C library: {e}")
    print("Trying alternate loading method...")
    
    try:
        # Method 2: Try with sys.prefix to look in the current Python environment
        if platform.system() == "Darwin":
            search_path = Path(sys.prefix) / "lib" / f"libllama.{lib_extension}"
        else:
            search_path = Path(sys.prefix) / "lib" / f"libllama.{lib_extension}"
        
        if search_path.exists():
            lib = ctypes.CDLL(str(search_path), mode=ctypes.RTLD_GLOBAL)
            print(f"Successfully loaded C library from {search_path}")
        else:
            raise FileNotFoundError(f"Library not found at {search_path}")
    except Exception as e2:
        print(f"Failed second attempt: {e2}")
        print("Please install llama-cpp-python correctly for your platform")
        sys.exit(1)

# Define logit-related functions
llama_get_logits = lib.llama_get_logits
llama_get_logits.argtypes = [ctypes.c_void_p]
llama_get_logits.restype = ctypes.POINTER(ctypes.c_float)

llama_token_get_text = lib.llama_token_get_text
llama_token_get_text.argtypes = [ctypes.c_void_p, ctypes.c_int]
llama_token_get_text.restype = ctypes.c_char_p

llama_token_eos = lib.llama_token_eos
llama_token_eos.argtypes = [ctypes.c_void_p]
llama_token_eos.restype = ctypes.c_int

llama_token_bos = lib.llama_token_bos
llama_token_bos.argtypes = [ctypes.c_void_p]
llama_token_bos.restype = ctypes.c_int

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://wordsynth.latenthomer.com/", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backend once at startup
print("Initializing llama backend...")
llama_cpp.llama_backend_init(False)

# Load model once at startup
print("Loading model...")
model_path = os.environ.get("MODEL_PATH", "../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf")
model_params = llama_cpp.llama_model_default_params()
print("Model params created")
model = llama_cpp.llama_load_model_from_file(model_path.encode('utf-8'), model_params)
print("Model loaded")
ctx_params = llama_cpp.llama_context_default_params()
print("Context params created")
ctx = llama_cpp.llama_new_context_with_model(model, ctx_params)
print("Context created")

# Initialize Llama model
# llm = Llama(
#     model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
#     n_ctx=2048,
#     n_threads=4,
# )

# Add a lock for generation
generation_lock = asyncio.Lock()

# Helper function to get token ID from text
def get_token_id(text: str) -> tuple:
    """Convert a text string to a token ID and return debug info"""
    text_bytes = text.encode('utf-8')
    max_tokens = 4  # Allow up to 4 tokens
    tokens = (llama_cpp.llama_token * max_tokens)()
    
    n = llama_cpp.llama_tokenize(
        vocab,
        text_bytes,
        len(text_bytes),
        tokens,
        max_tokens,
        ctypes.c_bool(True),
        ctypes.c_bool(True)
    )
    
    token_info = []
    for i in range(n):
        token_bytes = llama_cpp.llama_vocab_get_text(vocab, tokens[i])
        token_text = token_bytes.decode('utf-8', errors='replace').replace('Ġ', ' ').replace('Ċ', '\n')
        token_info.append((tokens[i], token_text))
    
    if n == 1:
        return tokens[0], token_info
    elif n > 1:
        return None, token_info  # Not a single token
    else:
        return None, []  # Tokenization failed

# Keep the default for when no hot word is provided
#DEFAULT_HOT_WORD = "the"
#DEFAULT_HOT_WORD_ID = 1820  # Known token ID for "the"

# Improved token identification for the hot word
def get_hot_word_token(word: str) -> int:
    """Get the token ID for a given word, properly handling tokenization"""
    # Try both with and without space prefix
    versions_to_try = [word, " " + word]
    
    for version in versions_to_try:
        version_bytes = version.encode('utf-8')
        max_tokens = 8
        tokens = (llama_cpp.llama_token * max_tokens)()
        
        n_tokens = llama_cpp.llama_tokenize(
            vocab,
            version_bytes,
            len(version_bytes),
            tokens,
            max_tokens,
            ctypes.c_bool(True),
            ctypes.c_bool(True)
        )
        
        print(f"Tokenizing '{version}' gave {n_tokens} tokens:")
        
        if n_tokens == 1:
            # Found a single-token representation!
            token_bytes = llama_cpp.llama_vocab_get_text(vocab, tokens[0])
            token_text = token_bytes.decode('utf-8', errors='replace').replace('Ġ', ' ').replace('Ċ', '\n')
            print(f"  Found perfect match: ID {tokens[0]} = '{token_text}'")
            return tokens[0]
        
        # If we get here with the space-prefixed version, we need to look at all tokens
        if version.startswith(" "):
            for i in range(n_tokens):
                token_bytes = llama_cpp.llama_vocab_get_text(vocab, tokens[i])
                token_text = token_bytes.decode('utf-8', errors='replace').replace('Ġ', ' ').replace('Ċ', '\n')
                print(f"  Token {i}: ID {tokens[i]} = '{token_text}'")
                
                # If this token contains just the word we're looking for (ignoring spaces)
                if token_text.strip() == word:
                    print(f"  Found matching token: ID {tokens[i]} = '{token_text}'")
                    return tokens[i]
    
    # If we get here, we couldn't find a suitable token
    print(f"  Could not find a suitable token for '{word}'")
    return None

@app.on_event("startup")
async def startup_event():
    # Initialize the backend
    llama_cpp.llama_backend_init()
    
    # Load the model
    global model
    #model = llama_cpp.llama_load_model_from_file(b"../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf", llama_cpp.llama_model_default_params())
    model = llama_cpp.llama_load_model_from_file(model_path.encode('utf-8'), llama_cpp.llama_model_default_params())
    # Get the vocabulary
    global vocab
    vocab = llama_cpp.llama_model_get_vocab(model)  # Retrieve the vocabulary
    
    # Use the hardcoded hot word ID
    #global DEFAULT_HOT_WORD_ID
    # No need to tokenize - we hardcoded it above
    #print(f"Using hardcoded token ID for '{DEFAULT_HOT_WORD}': {DEFAULT_HOT_WORD_ID}")
    
    # Verify it's correct
    #hot_word_bytes = llama_cpp.llama_vocab_get_text(vocab, DEFAULT_HOT_WORD_ID)
    #hot_word_text = hot_word_bytes.decode('utf-8', errors='replace').replace('Ġ', ' ').replace('Ċ', '\n')
    #print(f"Token text for ID {DEFAULT_HOT_WORD_ID}: '{hot_word_text}'")

@app.get("/stream")
async def stream_text(
    request: Request,
    context: str = Query(...),
    temperature: float = Query(0.7),
    top_p: float = Query(0.9),
    top_k: int = Query(40),
    num_predict: int = Query(4),
    repeat_penalty: float = Query(1.1),
    presence_penalty: float = Query(0.0),
    frequency_penalty: float = Query(0.0),
    mirostat_mode: int = Query(0),  # 0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0
    mirostat_tau: float = Query(5.0),  # Target entropy (higher = more diverse)
    mirostat_eta: float = Query(0.1),  # Learning rate (lower = more stable)
    hot_word: str = Query(None),  # User-specified hot word (optional)
    hot_word_boost: float = Query(1.0)  # Multiplier for hot word (1.0 = no boost, 2.0 = double, etc.)
):
    async def event_generator():
        async with generation_lock:
            try:
                # Comment out all hot word related code
                actual_hot_word = hot_word if hot_word is not None else "the"
                actual_hot_word_id = get_hot_word_token(actual_hot_word)
                
                if actual_hot_word_id is None:
                    print(f"Warning: Could not find token for hot word '{actual_hot_word}'. Hot word boost will be disabled.")
                else:
                    # Get text representation for logging
                    hot_word_bytes = llama_cpp.llama_vocab_get_text(vocab, actual_hot_word_id)
                    hot_word_text = hot_word_bytes.decode('utf-8', errors='replace').replace('Ġ', ' ').replace('Ċ', '\n')
                    print(f"Using hot word: '{actual_hot_word}' => Token ID {actual_hot_word_id} ('{hot_word_text.strip()}')")
                
                # Ensure hot_word_boost is at least 1.0 (no negative effect)
                hot_word_boost_value = max(1.0, hot_word_boost)
                
                # Clear KV cache before starting a new request
                llama_cpp.llama_kv_cache_clear(ctx)
                
                # Convert input context to bytes
                context_bytes = context.encode('utf-8')
                context_len = len(context_bytes)

                # Create token array
                max_tokens = llama_cpp.llama_n_ctx(model)
                tokens = (llama_cpp.llama_token * int(max_tokens))()

                # Tokenize the input context using vocab
                n_tokens = llama_cpp.llama_tokenize(
                    vocab,
                    context_bytes,
                    context_len,
                    tokens,
                    max_tokens,
                    ctypes.c_bool(True),
                    ctypes.c_bool(True)
                )

                print(f"Tokenization complete. Number of tokens: {n_tokens}")

                if n_tokens == 0:
                    yield {"event": "error", "data": "No tokens generated from tokenization."}
                    return

                # Create and prepare the batch
                batch = llama_cpp.llama_batch_init(n_tokens, 0, 1)
                
                # Set n_tokens in the batch
                batch.n_tokens = n_tokens
                
                # Fill the batch with tokens
                for i in range(n_tokens):
                    batch.token[i] = tokens[i]
                    batch.pos[i] = i
                    batch.n_seq_id[i] = 1
                    batch.seq_id[i][0] = 0
                    batch.logits[i] = 0
                
                # Set logits flag for the last token
                batch.logits[n_tokens-1] = 1
                
                # Process the batch
                ret = llama_cpp.llama_decode(ctx, batch)
                print(f"Decode result: {ret}, batch n_tokens: {batch.n_tokens}")
                
                if ret != 0:
                    yield {"event": "error", "data": f"Decode failed with return code {ret}"}
                    # Clean up resources
                    llama_cpp.llama_batch_free(batch)
                    llama_cpp.llama_kv_cache_clear(ctx)
                    return

                # Track tokens to implement repeat penalty
                last_tokens = [tokens[i] for i in range(n_tokens)]
                generated_text = ""
                token_count = {}  # Dictionary to track token frequencies
                
                # Mirostat variables
                mirostat_mu = 2.0 * mirostat_tau  # Initialize mu (2 * tau is a reasonable starting point)
                
                # Generate tokens with proper sampling
                pos = n_tokens
                for token_idx in range(num_predict):
                    try:
                        # Synchronize the context after each decode
                        llama_cpp.llama_synchronize(ctx)
                        
                        # Get logits for sampling
                        logits_ptr = llama_cpp.llama_get_logits(ctx)
                        n_vocab = llama_cpp.llama_n_vocab(vocab)
                        
                        # Convert logits to a list we can manipulate
                        logits = [logits_ptr[i] for i in range(n_vocab)]
                        
                        # Apply penalties first (existing code)
                        # ... repeat penalty, presence penalty, frequency penalty code ...
                        
                        # Apply hot word boost when generating tokens
                        if actual_hot_word_id is not None and hot_word_boost_value > 1.0:
                            # Get the original logit value
                            original_logit = logits[actual_hot_word_id]
                            
                            # Simple boost - just multiply the logit by the boost factor
                            # This increases probability without needing complex calculations
                            boosted_logit = original_logit * hot_word_boost_value
                            
                            # Apply the boosted logit
                            logits[actual_hot_word_id] = boosted_logit
                            
                            print(f"Boosting hot word '{hot_word_text}': {original_logit:.4f} → {boosted_logit:.4f} (factor: {hot_word_boost_value})")
                        
                        # First convert the raw logits to probabilities for display
                        max_logit = max(logits)
                        exp_logits = [math.exp(logit - max_logit) for logit in logits]
                        sum_exp_logits = sum(exp_logits)
                        raw_probs = [exp_logit / sum_exp_logits for exp_logit in exp_logits]
                        
                        # Get the top 5 tokens by raw probability BEFORE token selection
                        top5_indices = sorted(range(n_vocab), key=lambda i: raw_probs[i], reverse=True)[:5]
                        top5_probs = [raw_probs[i] for i in top5_indices]
                        top5_tokens = [llama_cpp.llama_vocab_get_text(vocab, i).decode('utf-8', errors='replace') for i in top5_indices]
                        top5_clean = [t.replace('Ġ', ' ').replace('Ċ', '\n') for t in top5_tokens]
                        
                        # Build array of top 5 tokens for frontend
                        top5_data = [
                            {
                                "text": text,
                                "id": int(idx),
                                "prob": float(prob)  # Convert to Python float for JSON serialization
                            } for text, idx, prob in zip(top5_clean, top5_indices, top5_probs)
                        ]
                        
                        # Determine how to sample based on parameters and mirostat mode
                        if mirostat_mode > 0:
                            # Mirostat sampling
                            if mirostat_mode == 1:
                                # Mirostat 1.0 implementation
                                # Calculate entropy of raw probabilities for info display
                                entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in raw_probs)
                                
                                # Use mu to adjust the logits
                                k = mirostat_mu
                                for i in range(n_vocab):
                                    logits[i] -= k
                                
                                # Convert adjusted logits to probabilities
                                max_adj_logit = max(logits)
                                adj_exp_logits = [math.exp(logit - max_adj_logit) if logit - max_adj_logit > -100 else 0 for logit in logits]
                                adj_sum_exp_logits = sum(adj_exp_logits)
                                
                                if adj_sum_exp_logits > 0:
                                    adj_probs = [adj_exp / adj_sum_exp_logits for adj_exp in adj_exp_logits]
                                else:
                                    # Fallback to raw probs if adjustment produces all zeros
                                    adj_probs = raw_probs
                                
                                # Sample from the adjusted distribution
                                r = random.random()
                                cdf = 0.0
                                next_token_id = None
                                for i, p in enumerate(adj_probs):
                                    cdf += p
                                    if r < cdf:
                                        next_token_id = i
                                        break
                                
                                if next_token_id is None:
                                    next_token_id = top5_indices[0]  # Fallback to most likely
                                
                                # Update mu based on the surprise value of the chosen token
                                surprise = -math.log2(raw_probs[next_token_id]) if raw_probs[next_token_id] > 0 else 100
                                mirostat_mu = mirostat_mu + mirostat_eta * (surprise - mirostat_tau)
                                
                                # Clip mu to a reasonable range (prevent extreme values)
                                mirostat_mu = max(0, min(100, mirostat_mu))
                                
                                print(f"Mirostat 1.0: mu={mirostat_mu:.4f}, surprise={surprise:.4f}, entropy={entropy:.4f}")
                                
                                sel_prob = raw_probs[next_token_id]
                                
                            else:  # mirostat_mode == 2
                                # Mirostat 2.0 implementation (simpler, adjusts temperature directly)
                                # Get probabilities with current temperature
                                temp = 1.0  # Start with temp=1.0
                                
                                # Calculate entropy of the current distribution
                                entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in raw_probs)
                                
                                # Binary search to find the right temperature
                                temp_min = 0.01
                                temp_max = 2.0
                                target_entropy = mirostat_tau
                                iterations = 7  # Number of binary search iterations
                                
                                for _ in range(iterations):
                                    temp = 0.5 * (temp_min + temp_max)
                                    
                                    # Apply temperature
                                    temp_logits = [logit / temp for logit in logits]
                                    
                                    # Convert to probabilities
                                    max_temp_logit = max(temp_logits)
                                    exp_temp_logits = [math.exp(logit - max_temp_logit) for logit in temp_logits]
                                    sum_exp_temp_logits = sum(exp_temp_logits)
                                    temp_probs = [exp_logit / sum_exp_temp_logits for exp_logit in exp_temp_logits]
                                    
                                    # Calculate entropy
                                    entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in temp_probs)
                                    
                                    # Adjust temperature based on entropy
                                    if entropy < target_entropy:
                                        temp_min = temp  # Temperature is too low
                                    else:
                                        temp_max = temp  # Temperature is too high
                                
                                print(f"Mirostat 2.0: temperature={temp:.4f}, entropy={entropy:.4f}")
                                
                                # Apply the final temperature and sample
                                for i in range(n_vocab):
                                    logits[i] /= temp
                                
                                # Convert to probabilities
                                max_temp_logit = max(logits)
                                exp_temp_logits = [math.exp(logit - max_temp_logit) for logit in logits]
                                sum_exp_temp_logits = sum(exp_temp_logits)
                                temp_probs = [exp_logit / sum_exp_temp_logits for exp_logit in exp_temp_logits]
                                
                                # Sample from the adjusted distribution
                                r = random.random()
                                cdf = 0.0
                                next_token_id = None
                                for i, p in enumerate(temp_probs):
                                    cdf += p
                                    if r < cdf:
                                        next_token_id = i
                                        break
                                
                                if next_token_id is None:
                                    next_token_id = top5_indices[0]  # Fallback to most likely
                                
                                sel_prob = raw_probs[next_token_id]
                                
                        elif top_k == 1 or temperature <= 0.0:
                            # Deterministic selection - just pick the highest probability token
                            next_token_id = top5_indices[0]  # The first token is the most likely
                            sel_prob = top5_probs[0]
                        else:
                            # Apply temperature to logits for sampling
                            for i in range(n_vocab):
                                logits[i] /= temperature
                            
                            # Convert to temperature-adjusted probabilities
                            max_temp_logit = max(logits)
                            exp_temp_logits = [math.exp(logit - max_temp_logit) for logit in logits]
                            sum_exp_temp_logits = sum(exp_temp_logits)
                            temp_probs = [exp_logit / sum_exp_temp_logits for exp_logit in exp_temp_logits]
                            
                            # Apply top-k filtering
                            if top_k < n_vocab:
                                indices_and_probs = [(i, p) for i, p in enumerate(temp_probs)]
                                indices_and_probs.sort(key=lambda x: x[1], reverse=True)
                                indices_and_probs = indices_and_probs[:top_k]
                                top_indices = [idx for idx, _ in indices_and_probs]
                                top_probs = [temp_probs[idx] for idx in top_indices]
                                # Renormalize probabilities
                                sum_top_probs = sum(top_probs)
                                top_probs = [p / sum_top_probs for p in top_probs]
                            else:
                                top_indices = list(range(n_vocab))
                                top_probs = temp_probs
                            
                            # Apply top-p (nucleus) sampling
                            if 0.0 < top_p < 1.0:
                                indices_and_probs = sorted(zip(top_indices, top_probs), key=lambda x: x[1], reverse=True)
                                cumulative_prob = 0.0
                                cutoff_index = 0
                                for i, (_, p) in enumerate(indices_and_probs):
                                    cumulative_prob += p
                                    if cumulative_prob >= top_p:
                                        cutoff_index = i + 1
                                        break
                                indices_and_probs = indices_and_probs[:cutoff_index]
                                top_indices = [idx for idx, _ in indices_and_probs]
                                top_probs = [temp_probs[idx] for idx in top_indices]
                                # Renormalize probabilities
                                sum_top_probs = sum(top_probs)
                                top_probs = [p / sum_top_probs for p in top_probs]
                            
                            # Sample from the filtered distribution
                            r = random.random()
                            cdf = 0.0
                            next_token_index = 0
                            for i, p in enumerate(top_probs):
                                cdf += p
                                if r < cdf:
                                    next_token_index = i
                                    break
                            
                            next_token_id = top_indices[next_token_index]
                            sel_prob = raw_probs[next_token_id]  # Get the raw probability of the selected token
                        
                        # Get token text using llama_vocab_get_text
                        token_bytes = llama_cpp.llama_vocab_get_text(vocab, next_token_id)
                        token_text = token_bytes.decode('utf-8', errors='replace')
                        
                        # Clean up special tokens
                        clean_text = token_text.replace('Ġ', ' ').replace('Ċ', '\n')
                        
                        # Fix first token if needed
                        if token_idx == 0 and clean_text.startswith(' '):
                            clean_text = clean_text[1:]
                            
                        # Build up the running text
                        generated_text += clean_text
                        
                        # Create the data structure for the frontend
                        token_data = {
                            "text": clean_text,
                            "id": int(next_token_id),
                            "prob": float(sel_prob),
                            "top5": top5_data
                        }
                        
                        # Convert to JSON string for the event data
                        json_data = json.dumps(token_data)
                        
                        # Print for server-side logging
                        print(f"\nToken {token_idx+1}/{num_predict}:")
                        print(f"Selected: '{clean_text}' (ID: {next_token_id}, Prob: {sel_prob:.4f})")
                        print("Top 5 candidates:")
                        for i, item in enumerate(top5_data):
                            print(f"  {i+1}. '{item['text']}' (ID: {item['id']}, Prob: {item['prob']:.4f})")
                        
                        # Send the plain text for compatibility
                        yield {"event": "message", "data": clean_text}
                        
                        # Send the detailed token data as a separate event
                        yield {"event": "token_data", "data": json_data}
                        
                        # Update the context with the new token
                        last_tokens.append(next_token_id)
                        
                        # Create a new batch with just the generated token
                        next_batch = llama_cpp.llama_batch_init(1, 0, 1)
                        next_batch.n_tokens = 1
                        next_batch.token[0] = next_token_id
                        next_batch.pos[0] = pos  # Position for the new token
                        next_batch.n_seq_id[0] = 1
                        next_batch.seq_id[0][0] = 0
                        next_batch.logits[0] = 1  # We want logits for this token
                        
                        # Decode with the new token
                        ret = llama_cpp.llama_decode(ctx, next_batch)
                        if ret != 0:
                            print(f"Warning: Decode failed for token {token_idx+1} with ret={ret}")
                            # Free resources and exit gracefully
                            llama_cpp.llama_batch_free(next_batch)
                            break
                        
                        pos += 1  # Increment position counter for next token
                        
                        # Free the token batch
                        llama_cpp.llama_batch_free(next_batch)
                        
                    except Exception as e:
                        import traceback
                        import sys
                        error_trace = traceback.format_exc()
                        error_type = type(e).__name__
                        print(f"GENERATION ERROR: {str(e)}")
                        print(f"Error type: {error_type}")
                        print(f"Detailed traceback:\n{error_trace}")
                        
                        # Debug model and context status
                        print(f"Using model path: {model_path}")
                        print(f"Model pointer is null: {model is None}")
                        print(f"Context pointer is null: {ctx is None}")
                        
                        # Check variables in the current scope
                        local_vars = locals()
                        print(f"Local variables available: {', '.join(local_vars.keys())}")
                        
                        # Try to access the C error message if available
                        try:
                            last_error = llama_cpp.llama_last_error()
                            if last_error:
                                print(f"Last llama.cpp error: {last_error}")
                        except:
                            print("Could not retrieve last llama.cpp error")
                        
                        # Check the vocabulary
                        try:
                            print(f"Vocab size: {llama_cpp.llama_n_vocab(vocab)}")
                        except:
                            print("Could not access vocabulary size")
                        
                        yield {"event": "error", "data": f"{error_type}: {str(e)}"}
                        # Ensure KV cache is cleared even on error
                        try:
                            llama_cpp.llama_kv_cache_clear(ctx)
                        except:
                            print("Could not clear KV cache")
                
                print(f"\nGenerated full text: {generated_text}")
                yield {"event": "done", "data": "complete"}
                
                # Free the main batch
                llama_cpp.llama_batch_free(batch)
                
                # Clear KV cache after completing the request
                llama_cpp.llama_kv_cache_clear(ctx)
                        
            except Exception as e:
                print(f"Generation error: {str(e)}")
                yield {"event": "error", "data": str(e)}
                # Ensure KV cache is cleared even on error
                llama_cpp.llama_kv_cache_clear(ctx)
    
    return EventSourceResponse(event_generator())

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("Cleaning up...")
    llama_cpp.llama_free(ctx)
    llama_cpp.llama_free_model(model)
