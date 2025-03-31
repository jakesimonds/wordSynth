from fastapi import FastAPI, Query, Response
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
}

# Add a lock for generation
generation_lock = asyncio.Lock()

# Add near the top with other globals
PAUSE_STATE = {'is_paused': False}

# Add near the top with other globals
possible_contexts = [
    "Repeat the word hello over and over again 100 times.",
    "Describe how to implement a basic sorting algorithm.",
    "Explain what a hash table is and how it works.",
    "Describe the concept of recursion with a simple example.",
    "Explain how to find the largest number in an array."
]

# Default context
current_context = possible_contexts[0]

@app.get("/toggle-pause")
async def toggle_pause():
    PAUSE_STATE['is_paused'] = not PAUSE_STATE['is_paused']
    return {"is_paused": PAUSE_STATE['is_paused']}

@app.get("/stream")
async def stream_text(
    temperature: float = Query(0.4),
    top_p: float = Query(0.4),
    top_k: int = Query(30),
    num_predict: int = Query(48),
    repeat_penalty: float = Query(1.1),
    presence_penalty: float = Query(0.0),
    frequency_penalty: float = Query(0.0),
):
    if PAUSE_STATE['is_paused']:
        return Response(status_code=204)  # 204 No Content




    async def event_generator():
        async with generation_lock:
            try:
                for chunk in llm.create_completion(
                    prompt=current_context,
                    max_tokens=num_predict,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repeat_penalty=repeat_penalty,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
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

@app.post("/inject-tokens")
async def inject_tokens(data: dict):
    text = data.get("text", "")
    print(f"Would inject tokens: {text}")  # Just logging for now
    return {"status": "ok"}

# Add a new endpoint to get contexts and set current context
@app.get("/contexts")
async def get_contexts():
    return {"contexts": possible_contexts, "current": current_context}

@app.post("/set-context")
async def set_context(context_index: int = Query(...)):
    global current_context
    if 0 <= context_index < len(possible_contexts):
        current_context = possible_contexts[context_index]
        return {"current": current_context}
    return {"error": "Invalid context index"}, 400 