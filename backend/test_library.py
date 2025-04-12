import ctypes
import sys

def test_library():
    print("\n=== Library Test Script ===\n")
    
    # 1. Try to load the library
    lib_path = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib"
    try:
        print(f"Loading library from: {lib_path}")
        lib = ctypes.CDLL(lib_path)
        print("✅ Library loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load library: {e}")
        return

    # Test all the functions we need for text generation
    test_functions = [
        # Model loading functions we know exist
        'llama_load_model_from_file',
        'llama_new_context_with_model',
        'llama_context_default_params',
        'llama_free',
        
        # Text generation functions we need to check
        'llama_token_to_str',
        'llama_tokenize',
        'llama_get_logits',
        'llama_sample_token',  # New name to try
        'llama_decode',        # New name to try
        'llama_generate',      # New name to try
        'llama_batch_decode',  # New name to try
        'llama_get_vocab_size', # Might be useful
        
        # Sampling functions
        'llama_sample_top_p_top_k',
        'llama_sample_temperature',
        'llama_sample_repetition_penalty',
        
        # Context management
        'llama_get_kv_cache_token_count',
        'llama_get_state_size'
    ]

    print("\nTesting required functions:")
    for func_name in test_functions:
        try:
            func = getattr(lib, func_name)
            print(f"✅ Found: {func_name}")
            # Try to get function type if possible
            try:
                print(f"   Type: {func.argtypes} -> {func.restype}")
            except:
                pass
        except Exception as e:
            print(f"❌ Not found: {func_name}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_library() 