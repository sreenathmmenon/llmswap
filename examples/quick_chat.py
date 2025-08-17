"""
Quick Chat Interface

A minimal chat interface that shows llmswap's simplicity.
Just 10 lines of core logic for a full chat experience!
"""

from llmswap import LLMClient

def main():
    # Setup - automatically detects available provider
    client = LLMClient(cache_enabled=True)
    
    print("Quick Chat with llmswap")
    print(f"Using provider: {client.get_current_provider()}")
    print("Type 'quit' to exit, 'help' for commands\n")
    
    # Simple chat loop
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
            
        elif user_input.lower() == 'help':
            print("\nCommands:")
            print("  help - Show this help")
            print("  quit - Exit chat")
            print("  provider - Show current provider")
            print("  switch <provider> - Switch provider (anthropic/openai/gemini)")
            continue
            
        elif user_input.lower() == 'provider':
            print(f"Current provider: {client.get_current_provider()}")
            continue
            
        elif user_input.lower().startswith('switch '):
            provider = user_input[7:].strip()
            try:
                client.set_provider(provider)
                print(f"Switched to: {provider}")
            except Exception as e:
                print(f"Failed to switch: {e}")
            continue
            
        elif not user_input:
            continue
        
        # Get response
        try:
            response = client.query(user_input)
            cache_indicator = "[cached]" if response.from_cache else "[fresh]"
            print(f"AI {cache_indicator}: {response.content}\n")
            
        except Exception as e:
            print(f"Error: {e}")
            print("Try switching providers with 'switch <provider>'\n")

if __name__ == "__main__":
    main()