# save as correct_api_test.py
import llama_cpp
import os
import sys
import platform
import ctypes

print(f"Python version: {sys.version}")
print(f"Platform: {platform.system()}")
print(f"llama_cpp version: {llama_cpp.__version__}")

# Find model
model_path = "../../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf"
if not os.path.exists(model_path):
    model_path = "/home/ec2-user/wordSynth/models/Llama-3.2-1B-Instruct-Q3_K_L.gguf"
    if not os.path.exists(model_path):
        model_path = "/Users/jakesimonds/Documents/wordSynth/models/Llama-3.2-1B-Instruct-Q3_K_L.gguf"

print(f"Using model: {model_path}")
print(f"Model exists: {os.path.exists(model_path)}")

try:
    print("\nStep 1: Initialize backend")
    llama_cpp.llama_backend_init(False)
    print("✓ Backend initialized")
    
    print("\nStep 2: Create model params")
    model_params = llama_cpp.llama_model_default_params()
    print("✓ Model params created")
    
    print("\nStep 3: Load model")
    model = llama_cpp.llama_load_model_from_file(model_path.encode('utf-8'), model_params)
    print(f"✓ Model loaded: {model}")
    
    # Get the vocabulary to initialize the tokenizer
    print("\nStep 4: Get vocabulary to initialize tokenizer")
    vocab = llama_cpp.llama_model_get_vocab(model)
    print(f"✓ Got vocabulary: {vocab}")
    
    # Initialize tokenizer if there's a function for it
    try:
        if hasattr(llama_cpp, 'llama_init_tokenizer'):
            llama_cpp.llama_init_tokenizer(vocab)
            print("✓ Tokenizer initialized with llama_init_tokenizer")
        elif hasattr(llama_cpp, 'llama_vocab_init_tokenizer'):
            llama_cpp.llama_vocab_init_tokenizer(vocab)
            print("✓ Tokenizer initialized with llama_vocab_init_tokenizer")
        else:
            print("! No explicit tokenizer initialization function found - may have happened automatically")
    except Exception as tok_err:
        print(f"! Warning: Tokenizer initialization failed: {tok_err}")
    
    print("\nStep 5: Create context params")
    ctx_params = llama_cpp.llama_context_default_params()
    print("✓ Context params created")
    
    print("\nStep 6: Create context")
    ctx = llama_cpp.llama_new_context_with_model(model, ctx_params)
    print(f"✓ Context created: {ctx}")
    
    print("\nStep 7: Create token array")
    max_tokens = 4  # Use a small fixed size
    tokens = (llama_cpp.llama_token * int(max_tokens))()
    print(f"✓ Token array created with size {max_tokens}")
    
    print("\nStep 8: Tokenize with context")
    test_text = " the"
    try:
        # Try tokenizing with vocab first
        print("  Trying to tokenize with vocab")
        n_tokens = llama_cpp.llama_tokenize(
            vocab,  # Use vocab instead of ctx
            test_text.encode('utf-8'),
            len(test_text.encode('utf-8')),
            tokens,
            max_tokens,
            ctypes.c_bool(True),
            ctypes.c_bool(True)
        )
        print(f"  ✓ Tokenized with vocab: {n_tokens} tokens")
    except Exception as e:
        print(f"  ✗ Vocab tokenization failed: {e}")
        try:
            # Fall back to context tokenization
            print("  Trying to tokenize with context")
            n_tokens = llama_cpp.llama_tokenize(
                ctx,
                test_text.encode('utf-8'),
                len(test_text.encode('utf-8')),
                tokens,
                max_tokens,
                ctypes.c_bool(True),
                ctypes.c_bool(True)
            )
            print(f"  ✓ Tokenized with context: {n_tokens} tokens")
        except Exception as e2:
            print(f"  ✗ Context tokenization failed too: {e2}")
            raise
    
    print("\nStep 9: Check token values")
    for i in range(n_tokens):
        token_id = tokens[i]
        print(f"  Token {i}: ID {token_id}")
        
        # Get token text - try vocab first, then context
        try:
            token_text = llama_cpp.llama_vocab_get_text(vocab, token_id)
            print(f"    Text (vocab_get_text): '{token_text.decode('utf-8', errors='replace')}'")
        except Exception as e:
            print(f"    Failed with llama_vocab_get_text: {e}")
            try:
                token_text = llama_cpp.llama_token_to_str(ctx, token_id)
                print(f"    Text (token_to_str): '{token_text.decode('utf-8', errors='replace')}'")
            except Exception as e2:
                print(f"    Failed with llama_token_to_str too: {e2}")
    
    print("\nStep 10: Clean up resources")
    llama_cpp.llama_free(ctx)
    llama_cpp.llama_free_model(model)
    print("✓ Resources freed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nScript completed")