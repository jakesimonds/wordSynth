from fastapi import FastAPI, Query, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from typing import Dict
import asyncio
from llama_cpp import Llama
import os
import ctypes
import math

# C Bindings setup
lib_path = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib"
try:
    lib = ctypes.CDLL(lib_path)
    print("Successfully loaded C library")
except Exception as e:
    print(f"Failed to load C library: {e}")
    exit(1)

class llama_model_params(ctypes.Structure):
    _fields_ = [
        ("n_gpu_layers", ctypes.c_int),
        ("main_gpu", ctypes.c_int),
        ("tensor_split", ctypes.POINTER(ctypes.c_float)),
        ("progress_callback", ctypes.c_void_p),
        ("progress_callback_user_data", ctypes.c_void_p),
        ("kv_overrides", ctypes.c_void_p),
        ("vocab_only", ctypes.c_bool),
        ("use_mmap", ctypes.c_bool),
        ("use_mlock", ctypes.c_bool),
        ("check_tensors", ctypes.c_bool),
    ]

# Token data structures
class llama_token_data(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("logit", ctypes.c_float),
        ("p", ctypes.c_float),
    ]

class llama_token_data_array(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(llama_token_data)),
        ("size", ctypes.c_size_t),
        ("sorted", ctypes.c_bool),
    ]

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

llama_model_default_params = lib.llama_model_default_params
llama_model_default_params.restype = llama_model_params

llama_model_load_from_file = lib.llama_model_load_from_file
llama_model_load_from_file.argtypes = [ctypes.c_char_p, llama_model_params]
llama_model_load_from_file.restype = ctypes.c_void_p

llama_model_free = lib.llama_model_free
llama_model_free.argtypes = [ctypes.c_void_p]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://wordsynth.latenthomer.com/","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Llama model
llm = Llama(
    model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
    n_ctx=2048,
    n_threads=4,
)

params = {
    'temperature': 0.4,
    'top_p': 0.4,
    'top_k': 30,
    'num_predict': 4,
    'repeat_penalty': 1.1,
    'presence_penalty': 0.0,
    'frequency_penalty': 0.0,
    'mirostat_mode': 0,     # Default to disabled
    'mirostat_tau': 5.0,    # Default tau value
    'mirostat_eta': 0.1,    # Default eta value
}

# Add a lock for generation
generation_lock = asyncio.Lock()

@app.get("/stream")
async def stream_text(
    request: Request,
    context: str = Query(...),
    temperature: float = Query(0.4),
    top_p: float = Query(0.4),
    top_k: int = Query(30),
    num_predict: int = Query(48),
    repeat_penalty: float = Query(1.1),
    presence_penalty: float = Query(0.0),
    frequency_penalty: float = Query(0.0),
    mirostat_mode: int = Query(0),
    mirostat_tau: float = Query(5.0),
    mirostat_eta: float = Query(0.1),
):
    async def event_generator():
        async with generation_lock:
            try:
                # Create base completion parameters
                completion_params = {
                    'prompt': context,
                    'max_tokens': num_predict,
                    'temperature': temperature,
                    'repeat_penalty': repeat_penalty,
                    'presence_penalty': presence_penalty,
                    'frequency_penalty': frequency_penalty,
                    'stream': True
                }
                
                # Add sampling strategy parameters based on mirostat_mode
                if mirostat_mode > 0:
                    completion_params.update({
                        'mirostat_mode': mirostat_mode,
                        'mirostat_tau': mirostat_tau,
                        'mirostat_eta': mirostat_eta
                    })
                else:
                    completion_params.update({
                        'top_p': top_p,
                        'top_k': top_k
                    })
                
                for chunk in llm.create_completion(**completion_params):
                    if chunk['choices'][0]['finish_reason'] is not None:
                        yield {
                            "event": "done",
                            "data": "complete"
                        }
                        break
                    
                    # Get the logits for THIS SPECIFIC token
                    try:
                        model_ptr = llm._model
                        if model_ptr:
                            logits_ptr = llama_get_logits(model_ptr)
                            if logits_ptr:
                                eos_token = llama_token_eos(model_ptr)
                                eos_logit = logits_ptr[eos_token]
                                eos_prob = math.exp(eos_logit) / (1 + math.exp(eos_logit))
                                
                                yield {
                                    "event": "message",
                                    "data": {
                                        "text": chunk['choices'][0]['text'],
                                        "probabilities": {
                                            "eos": eos_prob
                                        }
                                    }
                                }
                    except Exception as e:
                        # If we fail to get logits, at least send the text
                        yield {
                            "event": "message",
                            "data": {
                                "text": chunk['choices'][0]['text']
                            }
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
    global params
    params.update(new_params)
    return {"status": "success", "params": params}

@app.get("/test-c-bindings")
async def test_c_bindings():
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "Llama-3.2-1B-Instruct-Q3_K_L.gguf")
    if not os.path.exists(model_path):
        return {"status": "error", "message": f"Model file not found at {model_path}"}
    
    print("Testing C bindings - loading model...")
    params = llama_model_default_params()
    model = llama_model_load_from_file(model_path.encode('utf-8'), params)
    
    if model:
        print("C bindings test successful - model loaded")
        llama_model_free(model)
        print("C bindings test - model freed")
        return {"status": "success", "message": "C bindings test successful"}
    else:
        print("C bindings test failed - model not loaded")
        return {"status": "error", "message": "Failed to load model via C bindings"}

@app.get("/token-probs")
async def get_token_probabilities():
    try:
        # Get the model pointer from our Python Llama instance
        model_ptr = llm.model
        if not model_ptr:
            return {"status": "error", "message": "Model not initialized"}
        
        # Get the BOS and EOS token IDs
        bos_token = llama_token_bos(model_ptr)
        eos_token = llama_token_eos(model_ptr)
        
        # Get logits pointer
        logits_ptr = llama_get_logits(model_ptr)
        if not logits_ptr:
            return {"status": "error", "message": "Could not get logits"}
        
        # Get the logit values for BOS and EOS tokens
        bos_logit = logits_ptr[bos_token]
        eos_logit = logits_ptr[eos_token]
        
        # Convert logits to probabilities using softmax (simplified for just two tokens)
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
        # Get the raw model pointer
        model_ptr = llm._model  # This is the C pointer to the model
        if not model_ptr:
            return {"status": "error", "message": "Model not initialized"}
        
        # Get logits pointer
        logits_ptr = llama_get_logits(model_ptr)
        if not logits_ptr:
            return {"status": "error", "message": "Could not get logits"}
            
        # Get specific token IDs we care about
        eos_token = llama_token_eos(model_ptr)
        bos_token = llama_token_bos(model_ptr)
        
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
