from ollama import Client
import sys

def generate_with_temp(prompt, temperature):
    client = Client()
    print(f"\n=== Generating with temperature = {temperature} ===\n")
    
    response = client.generate(
        model='llama3.2:1b',
        prompt=prompt,
        options={"temperature": temperature}
    )
    
    print(response['response'])
    print("\n=== Generation Complete ===\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a prompt as a command line argument")
        sys.exit(1)
        
    prompt = " ".join(sys.argv[1:])
    
    # Generate with temperature = 0 (conservative)
    generate_with_temp(prompt, 0.0)
    
    # Generate with temperature = 2 (creative)
    generate_with_temp(prompt, 2.0) 