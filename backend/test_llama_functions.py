import ctypes
import os

def test_llama_functions():
    print("\n=== Testing llama.cpp Functions ===\n")
    
    # 1. Load library
    lib_path = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib"
    try:
        lib = ctypes.CDLL(lib_path)
        print("✅ Library loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load library: {e}")
        return

    # 2. Test core functions we need based on the docs
    test_functions = [
        # Model loading
        'llama_load_model_from_file',
        'llama_new_context_with_model',
        'llama_context_default_params',
        
        # Token handling
        'llama_token_get_text',
        'llama_token_to_str',
        'llama_tokenize',
        
        # Generation
        'llama_get_logits',
        'llama_sample_top_p_top_k',
        'llama_eval',
        
        # Context management
        'llama_free',
        'llama_free_model',
        
        # Sampling methods
        'llama_sample_temperature',
        'llama_sample_repetition_penalty',
        'llama_sample_frequency_and_presence_penalties',
        
        # New functions from the docs
        'llama_decode',
        'llama_batch_decode',
        'llama_generate',
        'llama_sample',
        'llama_token_eos',
        'llama_token_bos'
    ]

    print("\nChecking for required functions:")
    available_functions = []
    for func_name in test_functions:
        try:
            func = getattr(lib, func_name)
            print(f"✅ Found: {func_name}")
            available_functions.append(func_name)
        except Exception as e:
            print(f"❌ Not found: {func_name}")

    print("\n=== Summary ===")
    print(f"Total functions tested: {len(test_functions)}")
    print(f"Functions available: {len(available_functions)}")
    print("\nAvailable functions:", ", ".join(available_functions))

if __name__ == "__main__":
    test_llama_functions() 