import ctypes
import os

# 1. Load the C library
lib_path = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib"
try:
    lib = ctypes.CDLL(lib_path)
    print("1. Successfully loaded C library")
except Exception as e:
    print(f"Failed to load C library: {e}")
    exit(1)

# 2. Define the C functions we need
llama_get_logits = lib.llama_get_logits
llama_get_logits.argtypes = [ctypes.c_void_p]
llama_get_logits.restype = ctypes.POINTER(ctypes.c_float)

llama_token_eos = lib.llama_token_eos
llama_token_eos.argtypes = [ctypes.c_void_p]
llama_token_eos.restype = ctypes.c_int

# 3. Initialize the model (we still need this from Python to get the model pointer)
from llama_cpp import Llama
llm = Llama(
    model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
    n_ctx=2048,
    n_threads=4,
)
print("2. Model initialized")

# 4. Get the raw C model pointer
model_ptr = llm.model
print(f"3. Got raw C model pointer: {model_ptr}")

# 5. Test the C functions
try:
    # Test EOS token
    eos_token = llama_token_eos(model_ptr)
    print(f"4. Successfully got EOS token from C function: {eos_token}")
    
    # Test logits
    logits_ptr = llama_get_logits(model_ptr)
    print(f"5. Got logits pointer from C function: {logits_ptr}")
    
    if logits_ptr:
        # Try to read the logit value for the EOS token
        eos_logit = logits_ptr[eos_token]
        print(f"6. Successfully read EOS logit value: {eos_logit}")
        
except Exception as e:
    print(f"Error using C functions: {e}")

print("\nTest complete") 