# Save as inspect_llama_cpp.py
import os
import sys
import llama_cpp
import inspect
import platform

# Print basic information
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"llama_cpp version: {llama_cpp.__version__}")
print(f"llama_cpp path: {llama_cpp.__file__}")

# List all available functions in the llama_cpp module
print("\nAvailable functions in llama_cpp module:")
for name in dir(llama_cpp):
    if name.startswith("llama_") and callable(getattr(llama_cpp, name)):
        print(f"  {name}")

# Specifically check for the vocabulary functions
print("\nChecking vocabulary-related functions:")
vocab_functions = [
    "llama_model_get_vocab",
    "llama_get_vocab", 
    "llama_vocab_get_text",
    "llama_n_vocab"
]

for func_name in vocab_functions:
    if hasattr(llama_cpp, func_name):
        print(f"  ✓ {func_name}")
    else:
        print(f"  ✗ {func_name}")

# Check library location
lib_path = os.path.join(os.path.dirname(llama_cpp.__file__), "lib")
print(f"\nLooking for libraries in: {lib_path}")
if os.path.exists(lib_path):
    libraries = [f for f in os.listdir(lib_path) if f.endswith('.dylib') or f.endswith('.so')]
    for lib in libraries:
        print(f"  Found: {lib}")
else:
    print("  Library directory not found!")

# Check C-API version if available
try:
    print(f"\nllama_cpp C-API information:")
    if hasattr(llama_cpp, "llama_version"):
        version = llama_cpp.llama_version()
        print(f"  API version: {version}")
    else:
        print("  No version information available")
except Exception as e:
    print(f"  Error getting API version: {e}")