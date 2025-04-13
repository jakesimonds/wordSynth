FROM ghcr.io/abetlen/llama-cpp-python:latest

WORKDIR /app

# Install curl for downloading the model
RUN apt-get update && apt-get install -y curl

# Copy your application (excluding llama_cpp directory)
COPY . .
RUN rm -rf /app/llama_cpp

# Install other requirements
RUN pip install -r requirements.txt

# Make scripts executable
RUN chmod +x pull_model.sh

# Set model path
ENV MODEL_PATH="/app/models/Llama-3.2-1B-Instruct-Q3_K_L.gguf"

# Expose port
EXPOSE 8000

# Run model download and start app
CMD ["bash", "-c", "./pull_model.sh && uvicorn main:app --host 0.0.0.0 --port 8000"]