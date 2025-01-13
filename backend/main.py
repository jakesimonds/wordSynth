from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from typing import Dict
import asyncio
from llama_cpp import Llama
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Llama model
llm = Llama(
    model_path="./models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
    n_ctx=2048,
    n_threads=4
)

params = {
    'temperature': 0.4,
    'top_p': 0.4,
    'top_k': 30,
    'num_predict': 48
}

@app.get("/stream")
async def stream_text():
    async def event_generator():
        current_context = "Describe Homer Simpson using colorful, memorable adjectives. Alliteration encouraged but not required. Be accurate."
        
        try:
            # Generate stream using llama.cpp
            for chunk in llm.create_completion(
                prompt=current_context,
                max_tokens=params['num_predict'],
                temperature=params['temperature'],
                top_p=params['top_p'],
                top_k=params['top_k'],
                stream=True
            ):
                if chunk['choices'][0]['finish_reason'] is not None:
                    yield {
                        "event": "done",
                        "data": "complete"
                    }
                    break
                
                yield {
                    "event": "message",
                    "data": chunk['choices'][0]['text']
                }
                await asyncio.sleep(0.1)
                
        except Exception as e:
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