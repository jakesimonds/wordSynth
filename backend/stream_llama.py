from ollama import Client
import signal
import sys
from pynput import keyboard
import threading
import asyncio

MODEL = 'llama3.2:1b'

# Global parameters that can be modified by key listeners
PARAMS = {
    'temperature': {'value': 0.4, 'step': 0.1, 'min': 0.0, 'max': 2.0, 'up': 'w', 'down': 's'},
    'top_p': {'value': 0.4, 'step': 0.1, 'min': 0.0, 'max': 1.0, 'up': 'e', 'down': 'd'},
    'top_k': {'value': 30, 'step': 5, 'min': 1, 'max': 100, 'up': 'r', 'down': 'f'},
    'num_ctx': {'value': 1024, 'step': 128, 'min': 128, 'max': 4096, 'up': 't', 'down': 'g'},
    'num_predict': {'value': 48, 'step': 128, 'min': 128, 'max': 4096, 'up': 'y', 'down': 'h'}
}

def signal_handler(sig, frame):
    print('\n\nGracefully exiting...')
    sys.exit(0)

def on_press(key):
    try:
        # Check each parameter for its up/down keys
        for param_name, param_info in PARAMS.items():
            if key.char == param_info['up']:
                param_info['value'] = min(param_info['max'], 
                                        param_info['value'] + param_info['step'])
                print(f"\n\n=== {param_name.upper()} UP === (now {param_info['value']:.2f}) ===\n\n")
                return
            elif key.char == param_info['down']:
                param_info['value'] = max(param_info['min'], 
                                        param_info['value'] - param_info['step'])
                print(f"\n\n=== {param_name.upper()} DOWN === (now {param_info['value']:.2f}) ===\n\n")
                return
    except AttributeError:
        pass

def handle_parameter_controls():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def stream_continuously(prompt):
    client = Client()
    current_context = f"Generate continuous text. Topic: {prompt}"
    generation_count = 0
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start parameter control listener in separate thread
    control_thread = threading.Thread(target=handle_parameter_controls, daemon=True)
    control_thread.start()
    
    # Print control instructions
    print("\nStarting stream (Press Ctrl+C to exit)")
    print("Parameter controls:")
    for param_name, param_info in PARAMS.items():
        print(f"  {param_name}: '{param_info['up']}' to increase, '{param_info['down']}' to decrease")
    print()
    
    try:
        while True:
            generation_count += 1
            print(f"\n\n=== Starting generation #{generation_count} ===")
            print("Current parameters:")
            for param_name, param_info in PARAMS.items():
                print(f"  {param_name}: {param_info['value']:.2f}")
            print()
            
            stream = client.generate(
                model=MODEL,
                prompt=current_context,
                stream=True,
                options={
                    'temperature': PARAMS['temperature']['value'],
                    'top_p': PARAMS['top_p']['value'],
                    'top_k': int(PARAMS['top_k']['value']),
                    'num_ctx': int(PARAMS['num_ctx']['value']),
                    'num_predict': int(PARAMS['num_predict']['value'])
                }
            )
            
            new_text = ""
            for chunk in stream:
                text = chunk['response']
                print(text, end='', flush=True)
                new_text += text
                
                if chunk.get('done', False):
                    break
            
            print(f"\n\n=== Completed generation #{generation_count} ===\n")
            current_context = new_text[-1000:]
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)

# class LlamaStreamer:
#     def __init__(self, temperature=0.7, top_p=0.9):
#         self.temperature = temperature
#         self.top_p = top_p
#         self.top_k = top_k
#         # Initialize other parameters and your llama model

#     async def stream(self):
#         # Convert your existing streaming logic to be async
#         # You might need to modify how you interact with llama
#         # to make it work with async/await
#         # This is a placeholder example:
#         for chunk in your_existing_stream_logic():
#             yield chunk
#             await asyncio.sleep(0.1)  # Add small delays between chunks

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a prompt as a command line argument")
        sys.exit(1)
        
    initial_prompt = " ".join(sys.argv[1:])
    stream_continuously(initial_prompt)