from fastapi import FastAPI, Query, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from typing import Dict
import asyncio
from llama_cpp import Llama
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://wordsynth.latenthomer.com/","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Llama model
llm = Llama(
    model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
    n_ctx=2048,
    n_threads=4, # see systemQuery/multi.py for physical and logical cores
    #seed=33 # unimpressive results 
)

params = {
    'temperature': 0.4,
    'top_p': 0.4,
    'top_k': 30,
    'num_predict': 4,
    'repeat_penalty': 1.1,
    'presence_penalty': 0.0,
    'frequency_penalty': 0.0,
    'mirostat_mode': 0,     # Default to disabled
    'mirostat_tau': 5.0,    # Default tau value
    'mirostat_eta': 0.1,    # Default eta value
}

# Add a lock for generation
generation_lock = asyncio.Lock()

@app.get("/stream")
async def stream_text(
    request: Request,
    context: str = Query(...),
    temperature: float = Query(0.4),
    top_p: float = Query(0.4),
    top_k: int = Query(30),
    num_predict: int = Query(48),
    repeat_penalty: float = Query(1.1),
    presence_penalty: float = Query(0.0),
    frequency_penalty: float = Query(0.0),
    mirostat_mode: int = Query(0),
    mirostat_tau: float = Query(5.0),
    mirostat_eta: float = Query(0.1),
):
    async def event_generator():
        async with generation_lock:
            try:
                # Create base completion parameters
                completion_params = {
                    'prompt': context,
                    'max_tokens': num_predict,
                    'temperature': temperature,
                    'repeat_penalty': repeat_penalty,
                    'presence_penalty': presence_penalty,
                    'frequency_penalty': frequency_penalty,
                    'stream': True
                }
                
                # Add sampling strategy parameters based on mirostat_mode
                if mirostat_mode > 0:
                    # If Mirostat is enabled, use Mirostat parameters
                    completion_params.update({
                        'mirostat_mode': mirostat_mode,
                        'mirostat_tau': mirostat_tau,
                        'mirostat_eta': mirostat_eta
                    })
                else:
                    # If Mirostat is disabled, use top_p and top_k
                    completion_params.update({
                        'top_p': top_p,
                        'top_k': top_k
                    })
                
                for chunk in llm.create_completion(**completion_params):
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
                    
            except Exception as e:
                print(f"Generation error: {str(e)}")
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
