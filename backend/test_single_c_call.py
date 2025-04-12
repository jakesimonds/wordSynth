import ctypes
from llama_cpp import Llama

# 1. Load C library
lib_path = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib"
lib = ctypes.CDLL(lib_path)
print("1. Library loaded")

# 2. Define just ONE C function
llama_token_eos = lib.llama_token_eos
llama_token_eos.argtypes = [ctypes.c_void_p]
llama_token_eos.restype = ctypes.c_int
print("2. Function defined")

# 3. Initialize model
llm = Llama(
    model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
    n_ctx=2048,
    n_threads=4,
)
print("3. Model initialized")

# 4. Get pointer and try ONE call
model_ptr = llm.model
print(f"4. Model pointer: {model_ptr}")
print("5. About to make C call...")
result = llama_token_eos(model_ptr)
print(f"6. Result: {result}") 