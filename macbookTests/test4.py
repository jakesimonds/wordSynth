# diagnostic.py
import sys
import platform
import llama_cpp

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"llama_cpp version: {llama_cpp.__version__}")

# Print how the library was compiled 
if hasattr(llama_cpp, "_LLAMA_CPP_LIB"):
    print(f"Library path: {llama_cpp._LLAMA_CPP_LIB}")

# Try the high-level API 
try:
    print("\nTesting high-level API (Llama class):")
    model = llama_cpp.Llama("../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf", n_ctx=512, verbose=True)
    
    # Test simple tokenization
    test_word = " the"
    tokens = model.tokenize(test_word.encode())
    print(f"Tokenizing '{test_word}' => {tokens}")
    
    # Test detokenization of single tokens
    for token in tokens:
        text = model.detokenize([token]).decode(errors='replace')
        print(f"Token {token} => '{text}'")
    
except Exception as e:
    print(f"High-level API error: {e}")

# Try the low-level API
try:
    print("\nTesting low-level API:")
    llama_cpp.llama_backend_init()
    
    params = llama_cpp.llama_model_default_params()
    model_ptr = llama_cpp.llama_load_model_from_file(b"../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf", params)
    print(f"Model pointer: {model_ptr}")
    
    if model_ptr:
        vocab = llama_cpp.llama_model_get_vocab(model_ptr)
        print(f"Vocab pointer: {vocab}")
        
        # Clean up
        llama_cpp.llama_free_model(model_ptr)
    
except Exception as e:
    print(f"Low-level API error: {e}")

print("\nDiagnostic complete")