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
llm = Llama(
    model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
    n_ctx=2048,
    n_threads=4,
)

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
                for chunk in llm.create_completion(
                    prompt=context,
                    max_tokens=num_predict,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repeat_penalty=repeat_penalty,
                    stream=True
                ):
                    if chunk['choices'][0]['finish_reason'] is not None:
                        yield {
                            "event": "done",
                            "data": "complete"
                        }
                        break
                    
                    yield {
                        "event": "message",
                        "data": chunk['choices'][0]['text']
                    }
                        
            except Exception as e:
                print(f"Generation error: {str(e)}")
                yield {
                    "event": "error",
                    "data": str(e)
                }
    
    return EventSourceResponse(event_generator())

@app.post("/update-params")
async def update_parameters(new_params: Dict):
    global ctx_params
    ctx_params.update(new_params)
    return {"status": "success", "params": ctx_params}

@app.get("/token-probs")
async def get_token_probabilities():
    try:
        # Get the BOS and EOS token IDs using the Python API
        bos_token = llm.token_bos()
        eos_token = llm.token_eos()
        
        # Get logits using the Python API
        logits = llm.eval_logits()
        if logits is None:
            return {"status": "error", "message": "Could not get logits"}
        
        # Get the logit values for BOS and EOS tokens
        bos_logit = logits[bos_token]
        eos_logit = logits[eos_token]
        
        # Convert logits to probabilities using softmax
        bos_prob = math.exp(bos_logit) / (math.exp(bos_logit) + math.exp(eos_logit))
        eos_prob = math.exp(eos_logit) / (math.exp(bos_logit) + math.exp(eos_logit))
        
        print(f"BOS token (id={bos_token}) probability: {bos_prob}")
        print(f"EOS token (id={eos_token}) probability: {eos_prob}")
        
        return {
            "status": "success",
            "bos_token_id": bos_token,
            "bos_probability": bos_prob,
            "eos_token_id": eos_token,
            "eos_probability": eos_prob
        }
    except Exception as e:
        print(f"Error getting token probabilities: {str(e)}")
        return {
            "status": "error",
            "message": f"Error getting token probabilities: {str(e)}"
        }

@app.get("/logits")
async def get_logits():
    try:
        # Get the context pointer
        ctx_ptr = llm.context
        if not ctx_ptr:
            return {"status": "error", "message": "Context not initialized"}
        
        # Get logits pointer
        logits_ptr = llama_get_logits(ctx_ptr)
        if not logits_ptr:
            return {"status": "error", "message": "Could not get logits"}
            
        # Get specific token IDs we care about
        eos_token = llama_token_eos(ctx_ptr)
        bos_token = llama_token_bos(ctx_ptr)
        
        # Get their logit values
        eos_logit = logits_ptr[eos_token]
        bos_logit = logits_ptr[bos_token]
        
        # Convert to probabilities
        total = math.exp(eos_logit) + math.exp(bos_logit)
        eos_prob = math.exp(eos_logit) / total
        bos_prob = math.exp(bos_logit) / total
        
        return {
            "status": "success",
            "logits": {
                "eos": {
                    "token_id": eos_token,
                    "logit": float(eos_logit),
                    "probability": float(eos_prob)
                },
                "bos": {
                    "token_id": bos_token,
                    "logit": float(bos_logit),
                    "probability": float(bos_prob)
                }
            }
        }
    except Exception as e:
        print(f"Error accessing logits: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/test-c-bindings")
async def test_c_bindings():
    try:
        # First, let's print what we have
        print(f"Model type: {type(llm._model)}")
        print(f"Context type: {type(llm._ctx)}")
        print(f"Model value: {llm._model}")
        print(f"Context value: {llm._ctx}")
        
        # Get the model pointer
        model_ptr = ctypes.c_void_p(llm._model)
        if not model_ptr:
            return {"status": "error", "message": "Model not initialized"}
            
        # Get the context pointer
        ctx_ptr = ctypes.c_void_p(llm._ctx)
        if not ctx_ptr:
            return {"status": "error", "message": "Context not initialized"}
        
        # Test getting BOS and EOS tokens
        bos_token = llama_token_bos(model_ptr)  # Try with model pointer instead
        eos_token = llama_token_eos(model_ptr)  # Try with model pointer instead
        print(f"BOS token: {bos_token}, EOS token: {eos_token}")
        
        # Test getting logits
        logits_ptr = llama_get_logits(ctx_ptr)
        if logits_ptr:
            print("Successfully got logits pointer")
            # Try to read a value to make sure it's accessible
            test_logit = logits_ptr[0]
            print(f"First logit value: {test_logit}")
            return {
                "status": "success", 
                "message": "C bindings test successful",
                "details": {
                    "bos_token": bos_token,
                    "eos_token": eos_token,
                    "first_logit": float(test_logit)
                }
            }
        else:
            return {"status": "error", "message": "Failed to get logits"}
            
    except Exception as e:
        print(f"C bindings test error: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/test-tokenize")
async def test_tokenize(text: str = Query(default="Hello, world!")):
    try:
        # Convert input text to bytes
        text_bytes = text.encode('utf-8')
        
        # Create token array
        max_tokens = ctx_params.n_ctx
        tokens = (llama_cpp.llama_token * int(max_tokens))()
        
        # Tokenize
        n_tokens = llama_cpp.llama_tokenize(
            ctx,
            text_bytes,
            tokens,
            max_tokens,
            llama_cpp.c_bool(True)
        )
        
        # Convert token array to list for response
        token_list = [tokens[i] for i in range(n_tokens)]
        
        return {
            "status": "success",
            "text": text,
            "n_tokens": n_tokens,
            "tokens": token_list
        }
        
    except Exception as e:
        print(f"Error in tokenization: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/test-low-level")
async def test_low_level(text: str = Query(default="Hello, world!")):
    try:
        print(f"Testing with input: {text}")
        
        # Convert input text to bytes
        text_bytes = text.encode('utf-8')
        text_len = len(text_bytes)  # Get the length of the input text
        
        # Create token array
        max_tokens = llama_cpp.llama_n_ctx(model)  # Get the context size from the model
        tokens = (llama_cpp.llama_token * int(max_tokens))()  # Create an array of tokens
        
        # Tokenize
        n_tokens = llama_cpp.llama_tokenize(
            vocab,  # Pass the vocabulary pointer
            text_bytes,
            text_len,  # Pass the length of the text
            tokens,
            max_tokens,
            ctypes.c_bool(True),  # Add special tokens
            ctypes.c_bool(True)   # Parse special tokens
        )
        
        print(f"Tokenization complete. Number of tokens: {n_tokens}")
        
        # Get token strings
        token_strs = []
        for i in range(n_tokens):
            token_str = llama_cpp.llama_token_get_text(vocab, tokens[i])
            if token_str:
                token_strs.append(token_str.decode('utf-8', errors='ignore'))
        
        return {
            "status": "success",
            "text": text,
            "n_tokens": n_tokens,
            "tokens": [int(tokens[i]) for i in range(n_tokens)],
            "token_strings": token_strs
        }
        
    except Exception as e:
        print(f"Error in low-level test: {str(e)}")
        return {"status": "error", "message": str(e)}

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("Cleaning up...")
    llama_cpp.llama_free(ctx)
    llama_cpp.llama_free_model(model)
