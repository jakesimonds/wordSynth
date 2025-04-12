import ctypes
from llama_cpp import Llama
import os
import math

# Load the library
lib_path = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib"
try:
    lib = ctypes.CDLL(lib_path)
    print("Successfully loaded library")
except Exception as e:
    print(f"Failed to load library: {e}")
    exit(1)

# Define the C bindings we want to test
llama_get_logits = lib.llama_get_logits
llama_get_logits.argtypes = [ctypes.c_void_p]
llama_get_logits.restype = ctypes.POINTER(ctypes.c_float)

llama_token_eos = lib.llama_token_eos
llama_token_eos.argtypes = [ctypes.c_void_p]
llama_token_eos.restype = ctypes.c_int

def test_streaming_with_logits():
    print("\nInitializing test...")
    
    # Initialize the model
    llm = Llama(
        model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
        n_ctx=2048,
        n_threads=4,
    )
    print("Model initialized")

    # Test parameters
    completion_params = {
        'prompt': "Say hello!",
        'max_tokens': 4,
        'temperature': 0.7,
        'stream': True
    }

    print("\nStarting streaming test...")
    
    # Try to access model information through the Python API first
    print("Testing Python API access...")
    try:
        # Try to use Python API methods instead of direct C calls
        vocab_size = llm.vocab_size()
        print(f"Vocabulary size: {vocab_size}")
        
        # Try to get the EOS token through the Python API
        eos_token = llm.token_eos()
        print(f"EOS token from Python API: {eos_token}")
    except Exception as e:
        print(f"Error accessing through Python API: {e}")

    # Test streaming without C bindings first
    print("\nTesting basic streaming...")
    try:
        for chunk in llm.create_completion(**completion_params):
            print(f"Received chunk: {chunk['choices'][0]['text']}")
            
            # Try to access token information through the Python API
            try:
                # Use the Python API's methods to get token information
                last_tokens = llm.get_state()['tokens']
                print(f"Last tokens: {last_tokens}")
            except Exception as e:
                print(f"Error accessing token information: {e}")
                
    except Exception as e:
        print(f"Error during streaming: {e}")

if __name__ == "__main__":
    test_streaming_with_logits() 