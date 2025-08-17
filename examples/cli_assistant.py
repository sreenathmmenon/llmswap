#!/usr/bin/env python3
"""
CLI Assistant - Command-line interface for quick questions

Usage:
    python cli_assistant.py "What is Python?"
    python cli_assistant.py "Explain immutability"
    python cli_assistant.py "How to view functions of a package"

Or run without arguments for interactive mode.
"""

import sys
import argparse
from llmswap import LLMClient

def quick_ask(question, provider=None, cache=True):
    """Ask a quick question and get an answer"""
    try:
        client = LLMClient(provider=provider, cache_enabled=cache)
        response = client.query(question)
        return response.content, response.from_cache, response.provider
    except Exception as e:
        return f"Error: {e}", False, "none"

def interactive_mode():
    """Interactive CLI mode with commands"""
    client = LLMClient(cache_enabled=True)
    
    print("llmswap CLI Assistant")
    print(f"Provider: {client.get_current_provider()}")
    print("\nCommands:")
    print("  help - Show commands")
    print("  switch <provider> - Switch provider")
    print("  cache on/off - Toggle caching")
    print("  quit - Exit")
    print("\nAsk anything or use commands:")
    
    cache_enabled = True
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
                
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            elif user_input.lower() == 'help':
                print("\nCommands:")
                print("  help - Show this help")
                print("  switch anthropic/openai/gemini - Switch provider")
                print("  cache on/off - Toggle caching")
                print("  status - Show current settings")
                print("  quit - Exit")
                continue
                
            elif user_input.lower().startswith('switch '):
                provider = user_input[7:].strip()
                try:
                    client.set_provider(provider)
                    print(f"Switched to {provider}")
                except Exception as e:
                    print(f"Failed: {e}")
                continue
                
            elif user_input.lower() == 'cache on':
                cache_enabled = True
                client = LLMClient(cache_enabled=True)
                print("Caching enabled")
                continue
                
            elif user_input.lower() == 'cache off':
                cache_enabled = False
                client = LLMClient(cache_enabled=False)
                print("Caching disabled")
                continue
                
            elif user_input.lower() == 'status':
                print(f"Provider: {client.get_current_provider()}")
                print(f"Caching: {'on' if cache_enabled else 'off'}")
                continue
            
            # Regular question
            response = client.query(user_input)
            cache_indicator = "[cached]" if response.from_cache else "[fresh]"
            print(f"\n{cache_indicator} {response.content}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="CLI Assistant powered by llmswap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "What is Python?"
  %(prog)s "Explain immutability" --provider anthropic
  %(prog)s "How to view functions of a package" --no-cache
  %(prog)s  # Interactive mode
        """
    )
    
    parser.add_argument('question', nargs='?', help='Question to ask')
    parser.add_argument('--provider', '-p', 
                       choices=['anthropic', 'openai', 'gemini', 'ollama'],
                       help='LLM provider to use')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable caching for this query')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive mode')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive or not args.question:
        interactive_mode()
        return
    
    # Single question mode
    print(f"Question: {args.question}")
    
    answer, from_cache, provider = quick_ask(
        args.question, 
        provider=args.provider,
        cache=not args.no_cache
    )
    
    cache_indicator = "[cached]" if from_cache else "[fresh]"
    print(f"\n{cache_indicator} [{provider}] {answer}")
    
    if from_cache:
        print("\nTip: This answer was cached (free!)")

if __name__ == "__main__":
    main()