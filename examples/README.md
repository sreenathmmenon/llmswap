# llmswap Examples

This directory contains practical examples showing how to use llmswap in real-world scenarios.

## Quick Start

Make sure you have at least one API key set:
```bash
export ANTHROPIC_API_KEY="your-key"    # or
export OPENAI_API_KEY="your-key"       # or  
export GEMINI_API_KEY="your-key"
```

## Examples

### 🛠️ Tool Calling Examples (NEW in v5.2.0)

**Enable LLMs to access YOUR data and systems**

These examples show REAL use cases where LLM needs YOUR tools:
- LLM doesn't have real-time weather data
- LLM doesn't know YOUR database contents
- LLM doesn't know what products YOU sell

#### [01_weather_api.py](01_weather_api.py)
**Real-time weather data** - Shows before/after comparison:
- WITHOUT tools: LLM says "I don't have access to real-time weather"
- WITH tools: LLM calls YOUR API and returns actual current weather
```bash
python examples/01_weather_api.py
```

#### [02_database_query.py](02_database_query.py)
**Database access** - LLM queries YOUR customer database:
- WITHOUT tools: LLM says "I don't have access to your database"
- WITH tools: LLM queries YOUR data and analyzes results
```bash
python examples/02_database_query.py
```

#### [03_ecommerce_assistant.py](03_ecommerce_assistant.py)
**Shopping assistant** - LLM searches YOUR product catalog:
- WITHOUT tools: LLM can't help customers shop
- WITH tools: LLM becomes a knowledgeable sales assistant
```bash
python examples/03_ecommerce_assistant.py
```

📖 **[Complete Tool Calling Guide](../docs/TOOL_CALLING.md)**
🚀 **[Quick Start Guide](../docs/TOOL_CALLING_QUICKSTART.md)**

---

### 💰 [smart_cost_optimizer.py](smart_cost_optimizer.py)
**Save 50-90% on API costs with intelligent caching**

Demonstrates how llmswap automatically optimizes costs by caching responses and using smart provider selection. Perfect for production applications.

```bash
python examples/smart_cost_optimizer.py
```

### 🔄 [provider_comparison.py](provider_comparison.py)
**Compare responses from different LLM providers**

See how Anthropic, OpenAI, Gemini, and local models respond to the same question. Great for finding the best provider for your use case.

```bash
python examples/provider_comparison.py
```

### 💬 [quick_chat.py](quick_chat.py)
**Minimal chat interface in 10 lines**

A simple chat interface that shows llmswap's ease of use. Includes provider switching and caching indicators.

```bash
python examples/quick_chat.py
```

### 🚀 [hackathon_starter.py](hackathon_starter.py)
**Perfect for hackathons and rapid prototyping**

Ready-to-use chatbot template with caching, error handling, and conversation flow. Built for speed and reliability.

```bash
python examples/hackathon_starter.py
```

### 📚 [basic_usage.py](basic_usage.py)
**Learn the fundamentals**

Step-by-step introduction to llmswap features including provider switching, caching, and async operations.

```bash
python examples/basic_usage.py
```

### 🧪 [test_caching.py](test_caching.py)
**See caching in action**

Interactive demo showing how response caching works and how much money it saves.

```bash
python examples/test_caching.py
```

## Key Features Demonstrated

- **💰 Cost Optimization**: Intelligent caching reduces API costs by 50-90%
- **🔄 Provider Switching**: Seamlessly switch between different LLM providers
- **🛡️ Automatic Fallback**: Keep working even when one provider fails
- **⚡ Async Support**: Non-blocking operations for web applications
- **🎯 Zero Configuration**: Works with any API key you have
- **📊 Response Caching**: Same questions are answered for free

## Tips

1. **Enable caching** for repeated queries: `LLMClient(cache_enabled=True)`
2. **Use fallback** for reliability: `LLMClient(fallback=True)`
3. **Switch providers** based on cost or quality needs
4. **Check cache status** with `response.from_cache`
5. **Compare providers** to find the best fit for your use case

## Need Help?

- Check the main [README](../README.md) for full documentation
- Report issues on [GitHub](https://github.com/sreenathmmenon/llmswap/issues)
- See the [PyPI page](https://pypi.org/project/llmswap/) for latest updates