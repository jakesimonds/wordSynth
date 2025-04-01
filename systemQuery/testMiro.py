from llama_cpp import Llama
import argparse
from time import sleep
from datetime import datetime
import random

def write_to_file(content: str, file):
    file.write(content + "\n")
    file.flush()  # Ensure content is written immediately

def run_llama_test(
    prompt: str,
    file,
    seed: int,
    temperature: float = 0.4,
    mirostat_mode: int = 0,
    mirostat_tau: float = 5.0,
    mirostat_eta: float = 0.1,
    num_predict: int = 256,
    n_threads: int = 4
):
    # Initialize model with seed
    llm = Llama(
        model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
        n_ctx=2048,
        n_threads=n_threads,
        seed=seed
    )

    divider = "="*80
    write_to_file(f"\n{divider}", file)
    write_to_file(f"TEST RUN - Mode: {mirostat_mode} (Seed: {seed})", file)
    if mirostat_mode > 0:
        write_to_file(f"Tau: {mirostat_tau:.1f}, Eta: {mirostat_eta:.3f}", file)
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results_{timestamp}.txt"
    
    configs = [
        # Mode 0 (standard sampling) - testing with different seeds
        {'mode': 0, 'tau': 0, 'eta': 0},
        {'mode': 0, 'tau': 0, 'eta': 0},
        
        # Mode 1 (Mirostat) - testing extreme eta values
        {'mode': 1, 'tau': 5.0, 'eta': 0.001},  # Very small adjustment
        {'mode': 1, 'tau': 5.0, 'eta': 0.01},
        {'mode': 1, 'tau': 5.0, 'eta': 0.1},    # Original
        {'mode': 1, 'tau': 5.0, 'eta': 0.5},    # Larger adjustment
        {'mode': 1, 'tau': 5.0, 'eta': 1.0},    # Maximum adjustment
        
        # Mode 2 (Mirostat 2.0) - testing extreme eta values
        {'mode': 2, 'tau': 5.0, 'eta': 0.001},
        {'mode': 2, 'tau': 5.0, 'eta': 0.01},
        {'mode': 2, 'tau': 5.0, 'eta': 0.1},
        {'mode': 2, 'tau': 5.0, 'eta': 0.5},
        {'mode': 2, 'tau': 5.0, 'eta': 1.0},
    ]
    
    with open(filename, 'w') as f:
        write_to_file(f"Mirostat Test Results - {timestamp}", f)
        write_to_file(f"Prompt: {prompt}\n", f)
        
        for config in configs:
            seed = random.randint(1, 1000000)  # Random seed for each run
            run_llama_test(
                prompt=prompt,
                file=f,
                seed=seed,
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