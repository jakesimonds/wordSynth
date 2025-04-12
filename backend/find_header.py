import os
import glob

def find_llama_header():
    print("\n=== Finding llama.h ===\n")
    
    # Base directory where we found the .dylib
    base_dir = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp"
    
    print(f"Searching in: {base_dir}")
    
    # Look for llama.h in several possible locations
    possible_paths = [
        os.path.join(base_dir, "llama.h"),
        os.path.join(base_dir, "include", "llama.h"),
        os.path.join(base_dir, "lib", "llama.h")
    ]
    
    # Also do a recursive search
    for root, dirs, files in os.walk(base_dir):
        if "llama.h" in files:
            possible_paths.append(os.path.join(root, "llama.h"))
    
    print("\nPossible locations found:")
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found: {path}")
            # Print first few lines to confirm it's the right file
            try:
                with open(path, 'r') as f:
                    print("\nFirst few lines of the file:")
                    for i, line in enumerate(f):
                        if i < 10:  # Print first 10 lines
                            print(line.strip())
                        else:
                            break
            except Exception as e:
                print(f"Error reading file: {e}")
        else:
            print(f"❌ Not found: {path}")

if __name__ == "__main__":
    find_llama_header() 