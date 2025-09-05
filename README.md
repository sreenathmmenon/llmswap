# llmswap - Universal LLM Interface: OpenAI, Claude, Gemini, Ollama, IBM watsonx

[![PyPI version](https://badge.fury.io/py/llmswap.svg)](https://badge.fury.io/py/llmswap)
[![PyPI Downloads](https://static.pepy.tech/badge/llmswap)](https://pepy.tech/projects/llmswap)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Universal AI SDK for Developers**: Switch between 7 AI providers (OpenAI GPT-4o/o1, Claude, Gemini, Cohere, Perplexity, IBM watsonx, Groq) with cost optimization and enterprise analytics. The infrastructure layer for AI-powered applications.

**Save 50-90% on AI Costs**: Intelligent caching, provider comparison, usage analytics. Import into any Python project or use powerful CLI tools.

```python
# Before: Provider lock-in, complex setup
import openai  # Locked to OpenAI
client = openai.Client(api_key="...")
response = client.chat.completions.create(...)  # $$$ every API call

# After: Freedom + savings with llmswap
from llmswap import LLMClient
client = LLMClient()  # Auto-detects any provider
response = client.query("Hello")  # Automatic caching = 50-90% savings
```

## ⚡ Get Started in 30 Seconds

```bash
pip install llmswap
```

```python
from llmswap import LLMClient

# Works with any provider you have
client = LLMClient()  # Auto-detects from environment
response = client.query("Explain quantum computing in 50 words")
print(response.content)
```

## 🎯 Why llmswap for AI Development?

| Feature | llmswap | LangChain | LiteLLM | Direct APIs |
|---------|---------|-----------|---------|-------------|
| **AI Providers** | 7 providers, 1 line switch | 50+ complex setup | 20+ basic support | 1 per codebase |
| **Integration** | `pip install llmswap` | Complex framework | Moderate setup | Per-provider SDKs |
| **Cost Control** | Built-in optimization | Manual configuration | Basic tracking | No tracking |
| **Enterprise Analytics** | Native cost/usage tracking | External tools required | Limited insights | Manual logging |
| **CLI Tools** | 5 powerful commands | Separate packages | None included | None |
| **Caching** | Intelligent built-in | Manual implementation | Basic support | DIY solution |
| **Learning Curve** | 5 minutes | Hours of documentation | 30 minutes | Per-API learning |
| **Self-Hosted** | Full control | Complex deployment | Basic options | Manual setup |

## 🚀 Three Ways to Use llmswap:

**📚 1. Python Library/SDK**
```python
from llmswap import LLMClient
client = LLMClient()  # Import into any codebase
response = client.query("Analyze this data")
```

**⚡ 2. CLI Tools**  
```bash
llmswap ask "Debug this error"    # Terminal AI assistant
llmswap costs                     # Cost optimization insights
```

**📊 3. Enterprise Analytics**
```python
stats = client.get_usage_stats()         # Track AI spend
comparison = client.get_provider_comparison()  # Compare costs
```

## 🚀 Complete Feature Set

### 1️⃣ **Python SDK** - Multi-Provider Intelligence
```python
from llmswap import LLMClient

# Auto-detects available providers
client = LLMClient()  

# Or specify your preference
client = LLMClient(provider="anthropic")  # Claude 3 Opus/Sonnet/Haiku
client = LLMClient(provider="openai")     # GPT-4, GPT-3.5
client = LLMClient(provider="gemini")     # Google Gemini Pro/Flash
client = LLMClient(provider="watsonx")    # IBM watsonx.ai Granite
client = LLMClient(provider="ollama")     # Llama, Mistral, Phi, 100+ local
client = LLMClient(provider="groq")       # Groq ultra-fast inference
client = LLMClient(provider="cohere")     # Cohere Command models for RAG
client = LLMClient(provider="perplexity") # Perplexity web-connected AI

# Automatic failover
client = LLMClient(fallback=True)
response = client.query("Hello")  # Tries multiple providers

# Save 50-90% with intelligent caching
client = LLMClient(cache_enabled=True)
response1 = client.query("Expensive question")  # $$$ API call
response2 = client.query("Expensive question")  # FREE from cache
```

### 2️⃣ **CLI Suite** - 5 Powerful Terminal Tools
```bash
# Ask one-line questions
llmswap ask "How to optimize PostgreSQL queries?"

# Interactive AI chat
llmswap chat

# AI code review
llmswap review app.py --focus security

# Debug errors instantly
llmswap debug --error "ConnectionTimeout at line 42"

# Analyze logs with AI
llmswap logs --analyze app.log --since "2h ago"
```

### 3️⃣ **Analytics & Cost Optimization** (v4.0 NEW!)
```bash
# Compare provider costs before choosing
llmswap compare --input-tokens 1000 --output-tokens 500
# Output: Gemini $0.0005 | OpenAI $0.014 | Claude $0.011

# Track your actual usage and spending
llmswap usage --days 30 --format table
# Shows: queries, tokens, costs by provider, response times

# Get AI spend optimization recommendations
llmswap costs
# Suggests: Switch to Gemini, enable caching, use Ollama for dev
```

```python
# Python SDK - Full analytics suite
client = LLMClient(analytics_enabled=True)

# Automatic conversation memory
response = client.chat("What is Python?")
response = client.chat("How is it different from Java?")  # Remembers context

# Real-time cost tracking
stats = client.get_usage_stats()
print(f"Total queries: {stats['totals']['queries']}")
print(f"Total cost: ${stats['totals']['cost']:.4f}")
print(f"Avg response time: {stats['avg_response_time_ms']}ms")

# Cost optimization insights
analysis = client.get_cost_breakdown()
print(f"Potential savings: ${analysis['optimization_opportunities']['potential_provider_savings']:.2f}")
print(f"Recommended provider: {analysis['recommendations'][0]}")

# Compare providers for your specific use case
comparison = client.get_provider_comparison(input_tokens=1500, output_tokens=500)
print(f"Cheapest: {comparison['cheapest']} (${comparison['cheapest_cost']:.6f})")
print(f"Savings vs current: {comparison['max_savings_percentage']:.1f}%")
```

### 4️⃣ **Advanced Features**

**Async/Streaming Support**
```python
import asyncio
from llmswap import AsyncLLMClient

async def main():
    client = AsyncLLMClient()
    
    # Async queries
    response = await client.query("Explain AI")
    
    # Streaming responses
    async for chunk in client.stream("Write a story"):
        print(chunk, end="")
```

**Multi-User Security**
```python
# Context-aware caching for multi-tenant apps
response = client.query(
    "Get user data",
    cache_context={"user_id": "user123"}  # Isolated cache
)
```

**Provider Comparison**
```python
# Compare responses from different models
comparison = client.compare_providers(
    "Solve this problem",
    providers=["anthropic", "openai", "gemini"]
)
```

## 📊 Real-World Use Cases & Examples

### 🏢 **Enterprise: Content Generation at Scale**
**Netflix-style recommendation descriptions for millions of items:**
```python
from llmswap import LLMClient

# Start with OpenAI, switch to Gemini for 96% cost savings
client = LLMClient(provider="gemini", cache_enabled=True)

def generate_descriptions(items):
    for item in items:
        # Cached responses save 90% on similar content
        description = client.query(
            f"Create engaging description for {item['title']}",
            cache_context={"category": item['category']}
        )
        yield description.content

# Cost: $0.0005 per description vs $0.015 with OpenAI
```

### 👨‍💻 **Developers: AI-Powered Code Review**
**GitHub Copilot alternative for your team:**
```python
# CLI for instant code review
$ llmswap review api_handler.py --focus security

# Python SDK for CI/CD integration
from llmswap import LLMClient

client = LLMClient(analytics_enabled=True)
review = client.query(f"Review this PR for bugs: {pr_diff}")

# Track costs across your team
stats = client.get_usage_stats()
print(f"This month's AI costs: ${stats['totals']['cost']:.2f}")
```

### 🎓 **Education: AI Tutoring Platform**
**Khan Academy-style personalized learning:**
```python
client = LLMClient(provider="ollama")  # Free for schools!

def ai_tutor(student_question, subject):
    # Use watsonx for STEM, Ollama for general subjects
    if subject in ["math", "science"]:
        client.set_provider("watsonx")
    
    response = client.query(
        f"Explain {student_question} for a {subject} student",
        cache_context={"grade_level": student.grade}
    )
    return response.content

# Zero cost with Ollama, enterprise-grade with watsonx
```

### 🚀 **Startups: Multi-Modal Customer Support**
**Shopify-scale merchant assistance:**
```python
from llmswap import LLMClient

# Start with Anthropic, fallback to others if rate-limited
client = LLMClient(fallback=True, cache_enabled=True)

async def handle_support_ticket(ticket):
    # 90% of questions are similar - cache saves thousands
    response = await client.aquery(
        f"Help with: {ticket.issue}",
        cache_context={"type": ticket.category}
    )
    
    # Auto-escalate complex issues
    if response.confidence < 0.8:
        client.set_provider("anthropic")  # Use best model
        response = await client.aquery(ticket.issue)
    
    return response.content
```

### 📱 **Content Creators: Writing Assistant**
**Medium/Substack article generation:**
```bash
# Quick blog post ideas
llmswap ask "10 trending topics in AI for developers"

# Full article draft
llmswap chat
> Write a 1000-word article on prompt engineering
> Make it more technical
> Add code examples
```

## 🛠️ Installation & Setup

```bash
# Install package
pip install llmswap

# Set any API key (one is enough to get started)
export ANTHROPIC_API_KEY="sk-..."       # For Claude
export OPENAI_API_KEY="sk-..."          # For GPT-4
export GEMINI_API_KEY="..."             # For Google Gemini
export WATSONX_API_KEY="..."            # For IBM watsonx
export WATSONX_PROJECT_ID="..."         # watsonx project
export GROQ_API_KEY="gsk_..."           # For Groq ultra-fast inference
export COHERE_API_KEY="co_..."            # For Cohere Command models
export PERPLEXITY_API_KEY="pplx-..."      # For Perplexity web search
# Or run Ollama locally for 100% free usage
```

## 📈 Token Usage Guidelines

| Task Type | Input Tokens | Output Tokens | Estimated Cost |
|-----------|--------------|---------------|----------------|
| Simple Q&A | 100 | 50 | ~$0.001 |
| Code Review | 1000 | 300 | ~$0.010 |
| Document Analysis | 3000 | 800 | ~$0.025 |
| Creative Writing | 500 | 2000 | ~$0.020 |

## 🔗 Quick Links

- **GitHub**: [github.com/sreenathmmenon/llmswap](https://github.com/sreenathmmenon/llmswap)
- **Documentation**: [Full API Reference](https://github.com/sreenathmmenon/llmswap#readme)
- **PyPI**: [pypi.org/project/llmswap](https://pypi.org/project/llmswap)
- **Issues**: [Report bugs or request features](https://github.com/sreenathmmenon/llmswap/issues)

## 🚀 Get Started Now

```bash
pip install llmswap
```

```python
from llmswap import LLMClient
client = LLMClient()
print(client.query("Hello, AI!").content)
```

**That's it!** You're now using AI with automatic provider detection, failover support, and cost optimization.

---

Built with ❤️ for developers who value simplicity and efficiency. Star us on [GitHub](https://github.com/sreenathmmenon/llmswap) if llmswap saves you time or money!