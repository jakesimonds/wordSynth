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

# C Bindings setup
lib_path = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib"
try:
    lib = ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
    print("Successfully loaded C library")
except Exception as e:
    print(f"Failed to load C library: {e}")
    print("Trying alternate loading method...")
    try:
        # Try loading with absolute path resolution
        abs_path = os.path.abspath(lib_path)
        lib = ctypes.CDLL(abs_path, mode=ctypes.RTLD_GLOBAL)
        print(f"Successfully loaded C library from {abs_path}")
    except Exception as e2:
        print(f"Failed second attempt: {e2}")
        exit(1)

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
model_params = llama_cpp.llama_model_default_params()
print("Model params created")
model = llama_cpp.llama_load_model_from_file(b"../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf", model_params)
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

@app.on_event("startup")
async def startup_event():
    # Initialize the backend
    llama_cpp.llama_backend_init()
    
    # Load the model
    global model
    model = llama_cpp.llama_load_model_from_file(b"../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf", llama_cpp.llama_model_default_params())
    
    # Get the vocabulary
    global vocab
    vocab = llama_cpp.llama_model_get_vocab(model)  # Retrieve the vocabulary

@app.get("/stream")
async def stream_text(
    request: Request,
    context: str = Query(...),
    temperature: float = Query(0.7),
    top_p: float = Query(0.9),
    top_k: int = Query(40),
    num_predict: int = Query(4),
    repeat_penalty: float = Query(1.1)
):
    async def event_generator():
        async with generation_lock:
            try:
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
                    yield {
                        "event": "error",
                        "data": "No tokens generated from tokenization."
                    }
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
                    yield {
                        "event": "error",
                        "data": f"Decode failed with return code {ret}"
                    }
                    return

                # Keep track of generated tokens to apply repeat penalty
                last_n_tokens = [tokens[i] for i in range(n_tokens)]
                
                # Generate tokens with proper sampling
                for _ in range(num_predict):
                    # Get logits for sampling
                    logits_ptr = llama_cpp.llama_get_logits(ctx)
                    n_vocab = llama_cpp.llama_n_vocab(vocab)
                    
                    # Convert logits to a list we can manipulate
                    logits = [logits_ptr[i] for i in range(n_vocab)]
                    
                    # Apply repeat penalty
                    if repeat_penalty > 1.0:
                        for token_id in last_n_tokens:
                            if token_id < n_vocab:
                                logits[token_id] /= repeat_penalty
                    
                    # Apply temperature
                    if temperature > 0:
                        # Scale logits by temperature
                        for i in range(n_vocab):
                            logits[i] /= temperature
                    
                    # Convert logits to probabilities with softmax
                    max_logit = max(logits)
                    exp_logits = [math.exp(logit - max_logit) for logit in logits]
                    sum_exp_logits = sum(exp_logits)
                    probs = [exp_logit / sum_exp_logits for exp_logit in exp_logits]
                    
                    # Apply top-k filtering
                    if top_k > 0 and top_k < n_vocab:
                        indices_and_probs = [(i, p) for i, p in enumerate(probs)]
                        indices_and_probs.sort(key=lambda x: x[1], reverse=True)
                        indices_and_probs = indices_and_probs[:top_k]
                        top_indices = [idx for idx, _ in indices_and_probs]
                        top_probs = [probs[idx] for idx in top_indices]
                        # Renormalize probabilities
                        sum_top_probs = sum(top_probs)
                        top_probs = [p / sum_top_probs for p in top_probs]
                    else:
                        top_indices = list(range(n_vocab))
                        top_probs = probs
                    
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
                        top_probs = [probs[idx] for idx in top_indices]
                        # Renormalize probabilities
                        sum_top_probs = sum(top_probs)
                        top_probs = [p / sum_top_probs for p in top_probs]
                    
                    # Sample from the filtered distribution
                    next_token_index = 0
                    r = random.random()
                    cdf = 0.0
                    for i, p in enumerate(top_probs):
                        cdf += p
                        if r < cdf:
                            next_token_index = i
                            break
                    
                    next_token_id = top_indices[next_token_index]
                    
                    # Get token text
                    token_text = llama_cpp.llama_token_get_text(vocab, next_token_id).decode('utf-8', errors='replace')
                    
                    yield {
                        "event": "message",
                        "data": token_text
                    }
                    
                    # Update the context with the new token
                    last_n_tokens.append(next_token_id)
                    if len(last_n_tokens) > 64:  # Keep a reasonable number of tokens for repeat penalty
                        last_n_tokens.pop(0)
                    
                    # Create a new batch with just the generated token
                    next_batch = llama_cpp.llama_batch_init(1, 0, 1)
                    next_batch.n_tokens = 1
                    next_batch.token[0] = next_token_id
                    next_batch.pos[0] = n_tokens  # Correct position for the new token
                    next_batch.n_seq_id[0] = 1
                    next_batch.seq_id[0][0] = 0
                    next_batch.logits[0] = 1  # We want logits for this token
                    
                    # Decode with the new token
                    ret = llama_cpp.llama_decode(ctx, next_batch)
                    if ret != 0:
                        print(f"Warning: Decode failed for generated token with ret={ret}")
                        break
                    
                    n_tokens += 1  # Increment position counter for next token
                    
                    # Free the token batch
                    llama_cpp.llama_batch_free(next_batch)

                yield {
                    "event": "done",
                    "data": "complete"
                }
                
                # Free the main batch
                llama_cpp.llama_batch_free(batch)

            except Exception as e:
                print(f"Generation error: {str(e)}")
                yield {
                    "event": "error",
                    "data": str(e)
                }

    return EventSourceResponse(event_generator())

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("Cleaning up...")
    llama_cpp.llama_free(ctx)
    llama_cpp.llama_free_model(model)
