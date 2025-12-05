"""
Streaming Responses Example

Stream LLM responses token-by-token for better user experience.
Works with all providers!

Before running:
    export ANTHROPIC_API_KEY=sk-ant-...
"""

from llmswap import LLMClient
import time

def main():
    client = LLMClient(provider="anthropic")
    
    # Example 1: Basic streaming
    print("=== Basic Streaming ===")
    prompt = "Write a short story about a robot learning to paint."
    
    print(f"Prompt: {prompt}\n")
    print("Response: ", end="", flush=True)
    
    for chunk in client.stream(prompt):
        print(chunk, end="", flush=True)
        time.sleep(0.01)  # Simulate natural typing speed
    
    print("\n")
    
    # Example 2: Streaming with provider switching
    print("\n=== Streaming with Different Providers ===")
    
    providers = ["anthropic", "openai", "gemini"]
    prompt = "Count from 1 to 5."
    
    for provider in providers:
        if client.is_provider_available(provider):
            print(f"\n{provider.upper()}: ", end="", flush=True)
            client.set_provider(provider)
            
            for chunk in client.stream(prompt):
                print(chunk, end="", flush=True)
            
            print()  # New line after each provider

if __name__ == "__main__":
    main()
