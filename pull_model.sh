#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define model path and URL
MODEL_DIR="models"
MODEL_FILE="Llama-3.2-1B-Instruct-Q3_K_L.gguf"
MODEL_PATH="$MODEL_DIR/$MODEL_FILE"
MODEL_URL="https://huggingface.co/lmstudio-community/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q3_K_L.gguf"     

echo -e "${GREEN}=== WordSynth Model Download Script ===${NC}"

# Create models directory if it doesn't exist
mkdir -p "$MODEL_DIR"

# Check if model exists, download if not
if [ ! -f "$MODEL_PATH" ]; then
    echo -e "${YELLOW}Model not found. Downloading from HuggingFace...${NC}"
    echo -e "${YELLOW}This may take a few minutes depending on your internet connection.${NC}"
    
    # Download the model
    curl -L "$MODEL_URL" -o "$MODEL_PATH"
    
    # Check if download was successful
    if [ ! -f "$MODEL_PATH" ]; then
        echo -e "${RED}Error: Failed to download the model. Please check your internet connection and try again.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Model downloaded successfully!${NC}"
    echo -e "${GREEN}Model saved to: $MODEL_PATH${NC}"
else
    echo -e "${GREEN}Model already exists at: $MODEL_PATH${NC}"
fi

echo -e "${YELLOW}You can now start the backend and frontend servers manually.${NC}"
echo -e "${YELLOW}See the README.md for instructions.${NC}"