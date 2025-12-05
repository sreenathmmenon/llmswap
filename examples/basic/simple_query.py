"""
Simple Query Example

This is the most basic LLMSwap usage - send a query and get a response.

Before running:
    export ANTHROPIC_API_KEY=sk-ant-...
    # OR
    export OPENAI_API_KEY=sk-...
"""

from llmswap import LLMClient

def main():
    # Create a client (automatically detects available provider)
    client = LLMClient()
    
    # Send a simple query
    prompt = "Explain what LLMSwap is in one sentence."
    response = client.query(prompt)
    
    # Print the response
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    
    # You can also specify the provider explicitly
    client_anthropic = LLMClient(provider="anthropic")
    response2 = client_anthropic.query("What is 2+2?")
    print(f"\nAnthropicResponse: {response2}")

if __name__ == "__main__":
    main()
