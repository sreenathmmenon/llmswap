"""
Latest Models Showcase (November 2025)

Demonstrates the newest models from all major providers:
- Claude Opus 4.5 (Anthropic) - Nov 24, 2025
- Gemini 3 Pro (Google) - Nov 18, 2025  
- GPT-5.1 (OpenAI) - Nov 13, 2025
- Grok 4.1 (xAI) - Nov 17, 2025
"""

from llmswap import LLMClient
import time

def test_claude_opus_45():
    """Test Anthropic's Claude Opus 4.5 - State-of-the-art coding model"""
    print("\n" + "="*60)
    print("🤖 Claude Opus 4.5 (Released Nov 24, 2025)")
    print("="*60)
    
    try:
        client = LLMClient(provider="anthropic", model="claude-opus-4-5")
        
        # Coding task - Opus 4.5's strength
        prompt = """Write a Python function that implements a rate limiter using 
        the token bucket algorithm. Include docstrings and type hints."""
        
        print(f"Prompt: {prompt[:80]}...")
        start = time.time()
        response = client.chat(prompt)
        elapsed = time.time() - start
        
        print(f"\n✅ Model: {response.model}")
        print(f"⏱️  Latency: {elapsed:.2f}s")
        print(f"📝 Response preview:\n{response.content[:300]}...")
        print(f"\n💰 Pricing: $5/$25 per million tokens (input/output)")
        print(f"🎯 Best for: Complex coding, software engineering, deep research")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Set ANTHROPIC_API_KEY environment variable")


def test_gemini_3_pro():
    """Test Google's Gemini 3 Pro - Advanced multimodal understanding"""
    print("\n" + "="*60)
    print("🌟 Gemini 3 Pro (Released Nov 18, 2025)")
    print("="*60)
    
    try:
        client = LLMClient(provider="gemini", model="gemini-3-pro")
        
        # Multimodal analysis task
        prompt = """Explain how transformer architecture enables parallel processing 
        in neural networks. Include technical details about attention mechanisms."""
        
        print(f"Prompt: {prompt[:80]}...")
        start = time.time()
        response = client.chat(prompt)
        elapsed = time.time() - start
        
        print(f"\n✅ Model: {response.model}")
        print(f"⏱️  Latency: {elapsed:.2f}s")
        print(f"📝 Response preview:\n{response.content[:300]}...")
        print(f"\n🎯 Features: Text, images, videos, audio, PDF processing")
        print(f"📊 Context: 1,048,576 input tokens, 65,536 output tokens")
        print(f"🎯 Best for: Multimodal understanding, large documents, batch API")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Set GEMINI_API_KEY environment variable")


def test_gpt_51():
    """Test OpenAI's GPT-5.1 - 2-3x faster with adaptive reasoning"""
    print("\n" + "="*60)
    print("⚡ GPT-5.1 (Released Nov 13, 2025)")
    print("="*60)
    
    try:
        client = LLMClient(provider="openai", model="gpt-5.1")
        
        # Adaptive reasoning task
        prompt = """Design a distributed caching system that handles 100K requests/sec
        with sub-10ms latency. Consider consistency, fault tolerance, and scalability."""
        
        print(f"Prompt: {prompt[:80]}...")
        start = time.time()
        response = client.chat(prompt)
        elapsed = time.time() - start
        
        print(f"\n✅ Model: {response.model}")
        print(f"⏱️  Latency: {elapsed:.2f}s")
        print(f"📝 Response preview:\n{response.content[:300]}...")
        print(f"\n⚡ Speed: 2-3x faster than GPT-5 for routine queries")
        print(f"🧠 Variants: GPT-5.1 Instant (speed) & GPT-5.1 Thinking (reasoning)")
        print(f"🎯 Best for: Fast responses, adaptive reasoning, complex problems")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Set OPENAI_API_KEY environment variable")


def test_grok_41():
    """Test xAI's Grok 4.1 - #1 on LMArena Text Leaderboard"""
    print("\n" + "="*60)
    print("🏆 Grok 4.1 (Released Nov 17, 2025) - #1 LMArena")
    print("="*60)
    
    try:
        client = LLMClient(provider="xai", model="grok-4.1")
        
        # Emotional intelligence / creative task
        prompt = """Write a thoughtful letter from a senior developer to a junior
        developer who's struggling with impostor syndrome. Be empathetic and encouraging."""
        
        print(f"Prompt: {prompt[:80]}...")
        start = time.time()
        response = client.chat(prompt)
        elapsed = time.time() - start
        
        print(f"\n✅ Model: {response.model}")
        print(f"⏱️  Latency: {elapsed:.2f}s")
        print(f"📝 Response preview:\n{response.content[:300]}...")
        print(f"\n🏆 LMArena: #1 on Text Leaderboard")
        print(f"💎 Preferred 64.78% vs predecessor in blind tests")
        print(f"🎭 High score on EQ-Bench (emotional intelligence)")
        print(f"🎯 Best for: Emotional intelligence, creative writing, collaboration")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Set XAI_API_KEY environment variable")


def compare_coding_task():
    """Compare all latest models on a coding task"""
    print("\n" + "="*60)
    print("⚙️  CODING COMPARISON - All Latest Models")
    print("="*60)
    
    prompt = """Write a Python decorator that implements retry logic with 
    exponential backoff. Include type hints and handle edge cases."""
    
    models = [
        ("anthropic", "claude-opus-4-5", "Claude Opus 4.5"),
        ("gemini", "gemini-3-pro", "Gemini 3 Pro"),
        ("openai", "gpt-5.1", "GPT-5.1"),
        ("xai", "grok-4.1", "Grok 4.1"),
    ]
    
    print(f"\nTask: {prompt[:60]}...")
    print("\nResults:\n")
    
    for provider, model, name in models:
        try:
            client = LLMClient(provider=provider, model=model)
            start = time.time()
            response = client.chat(prompt, max_tokens=500)
            elapsed = time.time() - start
            
            print(f"✅ {name:20s} - {elapsed:5.2f}s - {len(response.content):4d} chars")
            
        except Exception as e:
            print(f"❌ {name:20s} - Error: {str(e)[:40]}")


def compare_creative_task():
    """Compare all latest models on a creative writing task"""
    print("\n" + "="*60)
    print("✍️  CREATIVE WRITING COMPARISON")
    print("="*60)
    
    prompt = """Write a haiku about artificial intelligence that captures both 
    its power and its limitations. Be creative and thoughtful."""
    
    models = [
        ("anthropic", "claude-opus-4-5", "Claude Opus 4.5"),
        ("gemini", "gemini-3-pro", "Gemini 3 Pro"),
        ("openai", "gpt-5.1", "GPT-5.1"),
        ("xai", "grok-4.1", "Grok 4.1"),
    ]
    
    print(f"\nTask: {prompt[:60]}...")
    print("\nResults:\n")
    
    for provider, model, name in models:
        try:
            client = LLMClient(provider=provider, model=model)
            start = time.time()
            response = client.chat(prompt, max_tokens=200)
            elapsed = time.time() - start
            
            print(f"{name} ({elapsed:.2f}s):")
            print(f"{response.content}\n")
            
        except Exception as e:
            print(f"❌ {name} - Error: {str(e)[:40]}\n")


def speed_comparison():
    """Compare response speed across all latest models"""
    print("\n" + "="*60)
    print("⚡ SPEED COMPARISON - Simple Query")
    print("="*60)
    
    prompt = "What is the capital of France?"
    
    models = [
        ("anthropic", "claude-opus-4-5", "Claude Opus 4.5"),
        ("gemini", "gemini-3-pro", "Gemini 3 Pro"),
        ("openai", "gpt-5.1", "GPT-5.1"),
        ("xai", "grok-4.1", "Grok 4.1"),
    ]
    
    print(f"\nQuery: '{prompt}'\n")
    
    results = []
    for provider, model, name in models:
        try:
            client = LLMClient(provider=provider, model=model)
            
            # Warm-up
            client.chat("Hello")
            
            # Actual test
            start = time.time()
            response = client.chat(prompt)
            elapsed = time.time() - start
            
            results.append((name, elapsed, len(response.content)))
            
        except Exception as e:
            results.append((name, None, str(e)[:30]))
    
    # Sort by speed
    results_sorted = sorted([r for r in results if r[1] is not None], key=lambda x: x[1])
    
    print("Rankings (fastest first):\n")
    for i, (name, latency, chars) in enumerate(results_sorted, 1):
        print(f"{i}. {name:20s} - {latency:5.2f}s - {chars:3d} chars")
    
    # Show errors
    errors = [r for r in results if r[1] is None]
    if errors:
        print("\nNot available:")
        for name, _, error in errors:
            print(f"   {name}: {error}")


def main():
    """Run all demos"""
    print("\n" + "🚀 "*30)
    print("LLMSwap - Latest Models Showcase (November 2025)")
    print("🚀 "*30)
    
    print("\n📋 Demonstrating:")
    print("   • Claude Opus 4.5 (Anthropic) - Nov 24, 2025")
    print("   • Gemini 3 Pro (Google) - Nov 18, 2025")
    print("   • GPT-5.1 (OpenAI) - Nov 13, 2025")
    print("   • Grok 4.1 (xAI) - Nov 17, 2025 - #1 LMArena")
    
    # Individual model showcases
    test_claude_opus_45()
    test_gemini_3_pro()
    test_gpt_51()
    test_grok_41()
    
    # Comparisons
    compare_coding_task()
    compare_creative_task()
    speed_comparison()
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print("\n💡 Tips:")
    print("   • All models support pass-through architecture")
    print("   • New models work day-one without SDK updates")
    print("   • Choose model based on task (coding, creative, speed)")
    print("   • Use provider fallback for production reliability")
    print("\n")


if __name__ == "__main__":
    main()
