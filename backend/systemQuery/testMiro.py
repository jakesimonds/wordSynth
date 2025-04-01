from llama_cpp import Llama
import argparse
from time import sleep
from datetime import datetime

def write_to_file(content: str, file):
    file.write(content + "\n")
    file.flush()  # Ensure content is written immediately

def run_llama_test(
    prompt: str,
    file,
    temperature: float = 0.4,
    mirostat_mode: int = 0,
    mirostat_tau: float = 5.0,
    mirostat_eta: float = 0.1,
    num_predict: int = 48,
    n_threads: int = 4
):
    # Initialize model
    llm = Llama(
        model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
        n_ctx=2048,
        n_threads=n_threads
    )

    divider = "="*80
    write_to_file(f"\n{divider}", file)
    write_to_file(f"TEST RUN - Mode: {mirostat_mode}", file)
    if mirostat_mode > 0:
        write_to_file(f"Tau: {mirostat_tau:.1f}, Eta: {mirostat_eta:.2f}", file)
    write_to_file(divider, file)
    
    write_to_file("\nParameters:", file)
    write_to_file(f"temperature: {temperature}", file)
    if mirostat_mode > 0:
        write_to_file(f"mirostat_mode: {mirostat_mode}", file)
        write_to_file(f"mirostat_tau: {mirostat_tau}", file)
        write_to_file(f"mirostat_eta: {mirostat_eta}", file)
    write_to_file(f"num_predict: {num_predict}", file)
    write_to_file(f"n_threads: {n_threads}", file)
    write_to_file(f"\nPrompt: {prompt}", file)
    write_to_file("\nResponse:", file)

    completion_params = {
        'prompt': prompt,
        'max_tokens': num_predict,
        'temperature': temperature,
        'stream': False
    }

    if mirostat_mode > 0:
        completion_params.update({
            'mirostat_mode': mirostat_mode,
            'mirostat_tau': mirostat_tau,
            'mirostat_eta': mirostat_eta
        })

    response = llm.create_completion(**completion_params)
    write_to_file(response['choices'][0]['text'], file)
    write_to_file("\nGeneration complete!", file)
    write_to_file(f"{divider}\n", file)
    sleep(1)  # Brief pause between generations

def run_test_suite(prompt: str):
    # Create timestamped results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results_{timestamp}.txt"
    
    configs = [
        # Mode 0 (standard sampling)
        {'mode': 0, 'tau': 0, 'eta': 0},
        {'mode': 0, 'tau': 0, 'eta': 0},
        {'mode': 0, 'tau': 0, 'eta': 0},
        {'mode': 0, 'tau': 0, 'eta': 0},
        {'mode': 0, 'tau': 0, 'eta': 0},
        
        # Mode 1 (Mirostat)
        {'mode': 1, 'tau': 3.0, 'eta': 0.1},
        {'mode': 1, 'tau': 4.0, 'eta': 0.1},
        {'mode': 1, 'tau': 5.0, 'eta': 0.1},
        {'mode': 1, 'tau': 5.0, 'eta': 0.2},
        {'mode': 1, 'tau': 5.0, 'eta': 0.3},
        
        # Mode 2 (Mirostat 2.0)
        {'mode': 2, 'tau': 3.0, 'eta': 0.1},
        {'mode': 2, 'tau': 4.0, 'eta': 0.1},
        {'mode': 2, 'tau': 5.0, 'eta': 0.1},
        {'mode': 2, 'tau': 5.0, 'eta': 0.2},
        {'mode': 2, 'tau': 5.0, 'eta': 0.3},
    ]
    
    with open(filename, 'w') as f:
        # Write test information header
        write_to_file(f"Mirostat Test Results - {timestamp}", f)
        write_to_file(f"Prompt: {prompt}\n", f)
        
        for config in configs:
            run_llama_test(
                prompt=prompt,
                file=f,
                mirostat_mode=config['mode'],
                mirostat_tau=config['tau'],
                mirostat_eta=config['eta']
            )
        
        print(f"Results written to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Llama model with different Mirostat configurations')
    parser.add_argument('prompt', type=str, help='The prompt to generate from')
    
    args = parser.parse_args()
    run_test_suite(args.prompt) 