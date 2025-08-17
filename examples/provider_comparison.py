"""
Provider Comparison Tool

See how different LLM providers respond to the same question.
Great for testing which provider works best for your use case.
"""

from llmswap import LLMClient

def compare_providers(question):
    """Compare responses from all available providers"""
    
    # List of providers to try
    providers = ["anthropic", "openai", "gemini", "ollama"]
    
    print(f"Comparing providers for: '{question}'\n")
    
    results = {}
    
    for provider in providers:
        try:
            print(f"Testing {provider.upper()}...", end=" ")
            client = LLMClient(provider=provider)
            response = client.query(question)
            
            results[provider] = {
                'content': response.content,
                'model': response.model,
                'latency': response.latency
            }
            print("OK")
            
        except Exception as e:
            print(f"FAILED ({str(e)[:30]}...)")
            results[provider] = None
    
    # Display results
    print(f"\nResults for: '{question}'")
    print("=" * 60)
    
    for provider, result in results.items():
        if result:
            print(f"\n{provider.upper()} ({result['model']}):")
            print(f"   Response: {result['content'][:150]}...")
            print(f"   Speed: {result['latency']:.2f}s")
        else:
            print(f"\n{provider.upper()}: Not available")

def main():
    print("LLM Provider Comparison Tool")
    print("See how different providers respond to the same question\n")
    
    # Example questions
    questions = [
        "What is artificial intelligence?",
        "Write a haiku about coding",
        "Explain quantum computing in simple terms"
    ]
    
    # Interactive mode
    while True:
        print("\nChoose an option:")
        print("1. Use example question")
        print("2. Ask your own question")
        print("3. Quit")
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == "1":
            print("\nExample questions:")
            for i, q in enumerate(questions, 1):
                print(f"{i}. {q}")
            
            try:
                q_choice = int(input("\nSelect question (1-3): ")) - 1
                if 0 <= q_choice < len(questions):
                    compare_providers(questions[q_choice])
                else:
                    print("Invalid choice!")
            except ValueError:
                print("Please enter a number!")
                
        elif choice == "2":
            question = input("Your question: ").strip()
            if question:
                compare_providers(question)
            else:
                print("Please enter a question!")
                
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()