import ctypes
import os

# Load the library
lib_path = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib"
try:
    lib = ctypes.CDLL(lib_path)
    print("Successfully loaded library")
except Exception as e:
    print(f"Failed to load library: {e}")
    exit(1)

# Define the model parameters structure
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

# Define function signatures
llama_model_default_params = lib.llama_model_default_params
llama_model_default_params.restype = llama_model_params

llama_model_load_from_file = lib.llama_model_load_from_file
llama_model_load_from_file.argtypes = [ctypes.c_char_p, llama_model_params]
llama_model_load_from_file.restype = ctypes.c_void_p

llama_model_free = lib.llama_model_free
llama_model_free.argtypes = [ctypes.c_void_p]

# Test loading a model
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "Llama-3.2-1B-Instruct-Q3_K_L.gguf")
if not os.path.exists(model_path):
    print(f"Model file not found at {model_path}")
    exit(1)

print("Loading model...")
params = llama_model_default_params()
model = llama_model_load_from_file(model_path.encode('utf-8'), params)

if model:
    print("Successfully loaded model")
    llama_model_free(model)
    print("Freed model")
else:
    print("Failed to load model") 