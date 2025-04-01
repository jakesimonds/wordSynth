#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Colorrr

# Define model path and URL
MODEL_DIR="models"
MODEL_FILE="Llama-3.2-1B-Instruct-Q3_K_L.gguf"
MODEL_PATH="$MODEL_DIR/$MODEL_FILE"
#MODEL_URL="https://huggingface.co/TheBloke/Llama-3.2-1B-Instruct-GGUF/resolve/main/llama-3.2-1b-instruct.Q3_K_L.gguf"
MODEL_URL="https://huggingface.co/lmstudio-community/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q3_K_L.gguf"     
echo -e "${GREEN}=== WordSynth Startup Script ===${NC}"

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
else
    echo -e "${GREEN}Model found at $MODEL_PATH${NC}"
fi

# Start backend server in a new terminal window
echo -e "${GREEN}Starting backend server...${NC}"
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)' && source venv/bin/activate && cd backend && python -m uvicorn main:app --reload"'

# Start frontend server in a new terminal window
echo -e "${GREEN}Starting frontend server...${NC}"
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/frontend && npm run dev"'

echo -e "${GREEN}Both servers are starting in separate terminal windows.${NC}"
echo -e "${GREEN}Frontend will be available at: http://localhost:5173${NC}"
echo -e "${YELLOW}Note: It may take a moment for both servers to fully start.${NC}"