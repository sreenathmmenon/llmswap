# LLMSwap Examples

Comprehensive examples demonstrating LLMSwap's capabilities across different use cases.

## 📁 Directory Structure

```
examples/
├── README.md (this file)
├── basic/                    # Getting started
│   ├── simple_query.py       # Basic LLM query
│   ├── provider_switching.py # Switch providers
│   └── streaming.py          # Streaming responses
│
├── advanced/                 # Advanced features
│   ├── tool_calling.py       # Function calling
│   ├── async_operations.py   # Async/await usage
│   ├── error_handling.py     # Error handling patterns
│   └── cost_tracking.py      # Track API costs
│
├── integrations/             # Framework integrations
│   ├── fastapi_app.py        # FastAPI integration
│   ├── django_app.py         # Django integration
│   ├── flask_app.py          # Flask integration
│   └── streamlit_app.py      # Streamlit app
│
├── enterprise/               # Enterprise features
│   ├── workspace_setup.py    # Workspace management
│   ├── analytics.py          # Usage analytics
│   └── multi_provider.py     # Provider fallback
│
└── mcp/                      # MCP protocol
    ├── basic_mcp.py          # Basic MCP usage
    ├── stdio_transport.py    # stdio transport
    └── http_transport.py     # HTTP transport
```

## 🚀 Quick Start

### 1. Basic Query

```python
from llmswap import LLMClient

client = LLMClient(provider="anthropic")
response = client.query("What is LLMSwap?")
print(response)
```

### 2. Provider Switching

```python
from llmswap import LLMClient

# Start with Anthropic
client = LLMClient(provider="anthropic")
response1 = client.query("Hello!")

# Switch to OpenAI
client.set_provider("openai")
response2 = client.query("Hello!")
```

### 3. Streaming Responses

```python
from llmswap import LLMClient

client = LLMClient(provider="anthropic")
for chunk in client.stream("Write a story"):
    print(chunk, end="", flush=True)
```

## 📚 Example Categories

### Basic Examples

Perfect for getting started with LLMSwap:
- `simple_query.py` - Your first LLMSwap query
- `provider_switching.py` - Switch between providers
- `streaming.py` - Stream responses in real-time

### Advanced Examples

Leverage powerful features:
- `tool_calling.py` - Function calling with all providers
- `async_operations.py` - High-performance async usage
- `error_handling.py` - Robust error handling
- `cost_tracking.py` - Track and optimize API costs

### Integration Examples

Integrate LLMSwap with popular frameworks:
- `fastapi_app.py` - Build REST APIs with FastAPI
- `django_app.py` - Add LLM features to Django
- `flask_app.py` - Flask web applications
- `streamlit_app.py` - Interactive Streamlit apps

### Enterprise Examples

Production-ready patterns:
- `workspace_setup.py` - Organize projects with workspaces
- `analytics.py` - Monitor usage and costs
- `multi_provider.py` - Automatic fallback strategies

### MCP Examples

Model Context Protocol usage:
- `basic_mcp.py` - Get started with MCP
- `stdio_transport.py` - Use stdio transport
- `http_transport.py` - HTTP-based MCP

## 🔧 Setup

1. **Install LLMSwap:**
   ```bash
   pip install llmswap
   ```

2. **Set up API keys:**
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   export OPENAI_API_KEY=sk-...
   export GEMINI_API_KEY=...
   ```

3. **Run an example:**
   ```bash
   cd examples/basic
   python simple_query.py
   ```

## 💡 Usage Tips

- **Start with basics** - Try `basic/` examples first
- **Copy and modify** - All examples are copy-paste ready
- **Check comments** - Each file has detailed comments
- **Mix and match** - Combine patterns for your use case

## 🐛 Troubleshooting

**Missing API key:**
```
ConfigurationError: No LLM providers available
```
→ Set at least one API key (see Setup above)

**Module not found:**
```
ModuleNotFoundError: No module named 'llmswap'
```
→ Install LLMSwap: `pip install llmswap`

**Rate limit errors:**
```
RateLimitError: Rate limit exceeded
```
→ Use provider fallback (see `enterprise/multi_provider.py`)

## 📖 Learn More

- **[Documentation](../README.md)** - Full documentation
- **[API Reference](../ARCHITECTURE.md)** - Architecture details
- **[Contributing](../CONTRIBUTING.md)** - Add your own examples

## 🤝 Contributing Examples

Have a useful example? Share it!

1. Create your example file
2. Add clear comments
3. Test it works
4. Submit a pull request

We especially welcome:
- Real-world use cases
- Integration examples
- Performance optimization patterns
- Error handling strategies

---

<p align="center">
  Made with ❤️ by the LLMSwap community
</p>
