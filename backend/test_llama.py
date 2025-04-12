import ctypes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load library
lib_path = "/Users/jakesimonds/.pyenv/versions/3.11.11/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib"
lib = ctypes.CDLL(lib_path)
logger.info("Library loaded")

# Print all available functions
logger.info("Available functions:")
for name in dir(lib):
    if not name.startswith('_'):
        logger.info(f"- {name}")

# Don't try to load the model yet
logger.info("Script completed successfully") 