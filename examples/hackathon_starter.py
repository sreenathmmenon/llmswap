"""
Hackathon Starter Example for llmswap
Perfect for rapid prototyping and student projects
"""

from llmswap import LLMClient

def hackathon_demo():
    """Demo showing how easy it is to get started with llmswap"""
    
    print("Hackathon AI Demo with llmswap")
    print("=" * 50)
    
    # Zero-config setup - works with any API key you have set
    client = LLMClient(cache_enabled=True)  # Save money from the start
    
    print(f"Connected to: {client.get_current_provider()}")
    print(f"Using model: {client.get_current_model()}")
    print()
    
    # Example use cases perfect for hackathons
    demo_queries = [
        "Generate a creative business idea for a mobile app",
        "Write Python code to analyze social media sentiment", 
        "Explain blockchain technology in simple terms",
        "Create a marketing slogan for an eco-friendly product",
        "Generate test data for a user management system"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"Query {i}: {query[:50]}...")
        
        try:
            response = client.query(query)
            cache_status = "CACHED" if response.from_cache else "API CALL"
            
            print(f"   Status: {cache_status}")
            print(f"   Response: {response.content[:100]}...")
            print()
            
        except Exception as e:
            print(f"   Error: {e}")
            continue
    
    # Show cost savings
    stats = client.get_cache_stats()
    if stats and stats['hit_rate'] > 0:
        print(f"Cache Hit Rate: {stats['hit_rate']:.1f}%")
        print(f"Estimated Cost Savings: ~{stats['hit_rate']:.1f}%")
    
    print("\nPerfect for hackathons:")
    print("   Fast setup - focus on your idea")
    print("   Cost-effective with caching")
    print("   Switch providers instantly") 
    print("   Multi-user ready")

def quick_chatbot_example():
    """Simple chatbot example for hackathons"""
    
    print("\nQuick Chatbot Example")
    print("=" * 30)
    
    client = LLMClient(cache_enabled=True)
    
    # Simulate a simple chatbot interaction
    conversation = [
        "Hello! What can you help me with?",
        "I'm building a hackathon project. Any tips?",
        "What's the best way to validate my startup idea?"
    ]
    
    for user_message in conversation:
        print(f"User: {user_message}")
        
        # Add context for better responses
        prompt = f"You are a helpful chatbot. User says: {user_message}"
        
        try:
            response = client.query(prompt)
            status = "CACHED" if response.from_cache else "API CALL"
            
            print(f"Bot [{status}]: {response.content[:150]}...")
            print()
            
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    # Check if any API key is available
    import os
    
    api_keys = [
        "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"
    ]
    
    has_key = any(os.getenv(key) for key in api_keys)
    
    if not has_key:
        print("No API key found!")
        print("Set one of these environment variables:")
        for key in api_keys:
            print(f"   export {key}='your-key-here'")
        print("\nOr run Ollama locally for free!")
        print("   https://ollama.ai")
        exit(1)
    
    try:
        hackathon_demo()
        quick_chatbot_example()
        
        print("\nReady to build something amazing!")
        print("   More examples: https://github.com/sreenathmmenon/llmswap")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        print("Try: pip install llmswap")