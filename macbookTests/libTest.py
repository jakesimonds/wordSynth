import platform
import ctypes
import sys
from pathlib import Path

# Determine the correct library extension based on platform
if platform.system() == "Darwin":
    lib_extension = "dylib"
elif platform.system() == "Linux":
    lib_extension = "so"
elif platform.system() == "Windows":
    lib_extension = "dll"
else:
    raise OSError(f"Unsupported platform: {platform.system()}")

# Try to find the library dynamically
try:
    # Method 1: Try using Python's package infrastructure
    import llama_cpp
    package_dir = Path(llama_cpp.__file__).parent
    lib_path = str(package_dir / "lib" / f"libllama.{lib_extension}")
    
    lib = ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
    print(f"Successfully loaded C library from {lib_path}")
except Exception as e:
    print(f"Failed to load C library: {e}")
    print("Trying alternate loading method...")
    
    try:
        # Method 2: Try with sys.prefix to look in the current Python environment
        if platform.system() == "Darwin":
            search_path = Path(sys.prefix) / "lib" / f"libllama.{lib_extension}"
        else:
            search_path = Path(sys.prefix) / "lib" / f"libllama.{lib_extension}"
        
        if search_path.exists():
            lib = ctypes.CDLL(str(search_path), mode=ctypes.RTLD_GLOBAL)
            print(f"Successfully loaded C library from {search_path}")
        else:
            raise FileNotFoundError(f"Library not found at {search_path}")
    except Exception as e2:
        print(f"Failed second attempt: {e2}")
        print("Please install llama-cpp-python correctly for your platform")
        sys.exit(1)