
import os
import sys
import llama_cpp
import subprocess

# Basic info
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"llama_cpp version: {llama_cpp.__version__}")
print(f"llama_cpp path: {llama_cpp.__file__}")

# Find the library
lib_dir = os.path.join(os.path.dirname(llama_cpp.__file__), "lib")
print(f"\nSearching for libraries in {lib_dir}:")
if os.path.exists(lib_dir):
    libraries = [f for f in os.listdir(lib_dir) if f.endswith('.dylib') or f.endswith('.so')]
    for lib in libraries:
        lib_path = os.path.join(lib_dir, lib)
        print(f"  Found: {lib}")
        # Check what the library links to
        result = subprocess.run(["otool", "-L", lib_path], capture_output=True, text=True)
        print(f"  Dependencies:\n    " + "\n    ".join(result.stdout.strip().split("\n")[1:]))

# Check function existence
print("\nChecking available functions:")
for func in ["llama_model_get_vocab", "llama_get_vocab"]:
    print(f"  {func}: {'✓' if hasattr(llama_cpp, func) else '✗'}")

# Check important paths
venv_path = os.path.dirname(os.path.dirname(sys.executable))
print(f"\nVirtual env: {venv_path}")
print(f"Python executable: {sys.executable}")

# Module search paths
print("\nPython module search paths:")
for p in sys.path:
    print(f"  {p}")

# Environment variables that might affect build
print("\nRelevant environment variables:")
env_vars = ["CMAKE_ARGS", "LLAMA_CUBLAS", "LLAMA_METAL", "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH"]
for var in env_vars:
    print(f"  {var}: {os.environ.get(var, 'not set')}")