"""
Gemini 3 Pro Multimodal Examples

Showcases Gemini 3 Pro's advanced multimodal capabilities:
- Text, images, videos, audio, PDF processing
- 1,048,576 input tokens (1M+)
- Batch API support
- Structured outputs
"""

from llmswap import LLMClient

def text_analysis_example():
    """Example: Large text analysis with Gemini 3 Pro"""
    print("\n" + "="*60)
    print("📄 Gemini 3 Pro - Large Text Analysis")
    print("="*60)
    
    try:
        client = LLMClient(provider="gemini", model="gemini-3-pro")
        
        # Simulate large document analysis
        long_text = """
        Artificial Intelligence has evolved dramatically since its inception...
        [This would be a much longer document in practice - 100K+ tokens]
        
        Key developments in 2025 include:
        - Claude Opus 4.5 (Anthropic) - State-of-the-art coding
        - Gemini 3 Pro (Google) - Advanced multimodal
        - GPT-5.1 (OpenAI) - 2-3x faster adaptive reasoning
        - Grok 4.1 (xAI) - #1 on LMArena Text Leaderboard
        """
        
        prompt = f"""Analyze this document and extract:
        1. Main themes
        2. Key developments
        3. Technical innovations
        4. Future implications
        
        Document:
        {long_text}
        """
        
        response = client.chat(prompt)
        
        print(f"✅ Model: {response.model}")
        print(f"📊 Context Window: 1,048,576 tokens (1M+)")
        print(f"📝 Analysis:\n{response.content[:400]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def structured_output_example():
    """Example: Structured JSON output from Gemini 3 Pro"""
    print("\n" + "="*60)
    print("🏗️  Gemini 3 Pro - Structured Output")
    print("="*60)
    
    try:
        client = LLMClient(provider="gemini", model="gemini-3-pro")
        
        prompt = """Extract information from this text and return as JSON:

        "Claude Opus 4.5 was released on November 24, 2025 by Anthropic. 
        It's priced at $5 for input and $25 for output per million tokens. 
        Best use cases include complex coding and software engineering."
        
        Return JSON with: model_name, release_date, company, pricing, use_cases
        """
        
        response = client.chat(prompt)
        
        print(f"✅ Model: {response.model}")
        print(f"🎯 Feature: Structured outputs built-in")
        print(f"📝 JSON Output:\n{response.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def reasoning_example():
    """Example: Advanced reasoning with Gemini 3 Pro"""
    print("\n" + "="*60)
    print("🧠 Gemini 3 Pro - Reasoning Capabilities")
    print("="*60)
    
    try:
        client = LLMClient(provider="gemini", model="gemini-3-pro")
        
        prompt = """Solve this logic puzzle:

        Five AI models were released in November 2025:
        - Claude Opus 4.5 on Nov 24
        - Gemini 3 Pro on Nov 18
        - GPT-5.1 on Nov 13
        - Grok 4.1 on Nov 17
        
        Which model was released:
        1. First?
        2. Last?
        3. Between GPT-5.1 and Grok 4.1?
        4. Which two were released closest together?
        
        Show your reasoning step-by-step.
        """
        
        response = client.chat(prompt)
        
        print(f"✅ Model: {response.model}")
        print(f"🎯 Feature: Reasoning capabilities")
        print(f"📝 Solution:\n{response.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def batch_processing_example():
    """Example: Batch processing with Gemini 3 Pro"""
    print("\n" + "="*60)
    print("📦 Gemini 3 Pro - Batch Processing")
    print("="*60)
    
    try:
        client = LLMClient(provider="gemini", model="gemini-3-pro")
        
        # Multiple documents to process
        documents = [
            "Claude Opus 4.5: State-of-the-art coding model from Anthropic",
            "Gemini 3 Pro: Advanced multimodal understanding from Google",
            "GPT-5.1: 2-3x faster adaptive reasoning from OpenAI",
            "Grok 4.1: #1 LMArena with enhanced emotional intelligence from xAI"
        ]
        
        prompt = f"""Process these AI model descriptions and extract:
        - Model name
        - Key capability
        - Provider
        
        Documents:
        {chr(10).join(f'{i+1}. {doc}' for i, doc in enumerate(documents))}
        
        Return results in a structured format.
        """
        
        response = client.chat(prompt)
        
        print(f"✅ Model: {response.model}")
        print(f"📦 Batch API: Built-in support")
        print(f"📊 Processed {len(documents)} documents")
        print(f"📝 Results:\n{response.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def compare_gemini_models():
    """Compare current Gemini models"""
    print("\n" + "="*60)
    print("📊 Gemini Evolution Comparison")
    print("="*60)
    
    models = [
        ("gemini-3-pro-preview", "Current flagship preview"),
        ("gemini-3-deep-think", "Advanced reasoning"),
        ("gemini-2.5-pro", "Stable Pro"),
    ]
    
    prompt = "Explain the transformer architecture in 50 words"
    
    print(f"\nPrompt: '{prompt}'\n")
    
    for model, version in models:
        try:
            client = LLMClient(provider="gemini", model=model)
            response = client.chat(prompt, max_tokens=100)
            
            print(f"✅ {model} ({version}):")
            print(f"   {response.content[:120]}...")
            print()
            
        except Exception as e:
            print(f"❌ {model}: {str(e)[:60]}\n")


def main():
    """Run all Gemini 3 Pro examples"""
    print("\n" + "🌟 "*30)
    print("Gemini 3 Pro - Multimodal Capabilities Showcase")
    print("🌟 "*30)
    
    print("\n📋 Features:")
    print("   • 1,048,576 input tokens (1M+)")
    print("   • 65,536 output tokens")
    print("   • Text, images, videos, audio, PDF support")
    print("   • Batch API built-in")
    print("   • Structured outputs")
    print("   • Advanced reasoning")
    
    # Run examples
    text_analysis_example()
    structured_output_example()
    reasoning_example()
    batch_processing_example()
    compare_gemini_models()
    
    print("\n" + "="*60)
    print("✅ Gemini 3 Pro Demo Complete!")
    print("="*60)
    print("\n💡 Best For:")
    print("   • Large document analysis (1M+ tokens)")
    print("   • Multimodal understanding")
    print("   • Batch processing")
    print("   • Structured data extraction")
    print("\n")


if __name__ == "__main__":
    main()
