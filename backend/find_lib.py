from llama_cpp import __file__ as llama_cpp_file
import os

# Print the package location
print("Package location:", os.path.dirname(llama_cpp_file))

# Print all files in the lib directory
lib_dir = os.path.join(os.path.dirname(llama_cpp_file), "lib")
print("\nContents of lib directory:")
if os.path.exists(lib_dir):
    for file in os.listdir(lib_dir):
        print(f"- {file}")
else:
    print("lib directory not found") 