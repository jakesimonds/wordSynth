from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from typing import Dict
import asyncio
from ollama import Client

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store current parameters (using your existing defaults)
params = {
    'temperature': 0.4,
    'top_p': 0.4,
    'top_k': 30,
    'num_ctx': 1024,
    'num_predict': 48
}

@app.get("/stream")
async def stream_text():
    async def event_generator():
        client = Client()
        current_context = "Describe Homer Simpson using adjectives"  # You can make this configurable
        
        try:
            stream = client.generate(
                model='llama3.2:1b',
                prompt=current_context,
                stream=True,
                options={
                    'temperature': params['temperature'],
                    'top_p': params['top_p'],
                    'top_k': int(params['top_k']),
                    'num_ctx': int(params['num_ctx']),
                    'num_predict': int(params['num_predict'])
                }
            )
            
            for chunk in stream:
                if chunk.get('done', False):
                    break
                yield {
                    "event": "message",
                    "data": chunk['response']
                }
                await asyncio.sleep(0.1)  # Small delay between chunks
                
        except Exception as e:
            print(f"Error in stream: {e}")
            yield {
                "event": "error",
                "data": str(e)
            }

    return EventSourceResponse(event_generator())

@app.post("/update-params")
async def update_parameters(new_params: Dict):
    global params
    params.update(new_params)
    return {"status": "success", "params": params} 