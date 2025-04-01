from llama_cpp import Llama
import argparse

def run_llama_test(
    prompt: str,
    temperature: float = 0.4,
    top_p: float = 0.4,
    top_k: int = 30,
    num_predict: int = 48,
    repeat_penalty: float = 1.1,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    n_threads: int = 4
):
    # Initialize model
    llm = Llama(
        model_path="../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf",
        n_ctx=2048,
        n_threads=n_threads
    )

    print("\nGenerating with parameters:")
    print(f"temperature: {temperature}")
    print(f"top_p: {top_p}")
    print(f"top_k: {top_k}")
    print(f"num_predict: {num_predict}")
    print(f"repeat_penalty: {repeat_penalty}")
    print(f"presence_penalty: {presence_penalty}")
    print(f"frequency_penalty: {frequency_penalty}")
    print(f"n_threads: {n_threads}")
    print("\nPrompt:", prompt)
    print("\nResponse:")

    # Generate response
    response = llm.create_completion(
        prompt=prompt,
        max_tokens=num_predict,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        repeat_penalty=repeat_penalty,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        stream=False
    )

    print(response['choices'][0]['text'])
    print("\nGeneration complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Llama model with different parameters')
    parser.add_argument('prompt', type=str, help='The prompt to generate from')
    parser.add_argument('--temperature', type=float, default=0.4)
    parser.add_argument('--top_p', type=float, default=0.4)
    parser.add_argument('--top_k', type=int, default=30)
    parser.add_argument('--num_predict', type=int, default=48)
    parser.add_argument('--repeat_penalty', type=float, default=1.1)
    parser.add_argument('--presence_penalty', type=float, default=0.0)
    parser.add_argument('--frequency_penalty', type=float, default=0.0)
    parser.add_argument('--n_threads', type=int, default=4)

    args = parser.parse_args()
    
    run_llama_test(
        args.prompt,
        args.temperature,
        args.top_p,
        args.top_k,
        args.num_predict,
        args.repeat_penalty,
        args.presence_penalty,
        args.frequency_penalty,
        args.n_threads
    )