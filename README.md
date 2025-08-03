# llmswap

[![PyPI version](https://badge.fury.io/py/llmswap.svg)](https://badge.fury.io/py/llmswap)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Simple interface for any LLM provider. Switch between Anthropic, OpenAI, Google, and local models with one line of code.

## Why llmswap?

- Easy switching between LLM providers
- Zero configuration - works with environment variables  
- Automatic fallback when providers fail
- Simple API - same interface for all providers

## Quick Start

### Installation
```bash
pip install llmswap
```

### Basic Usage
```python
from any_llm import LLMClient

client = LLMClient()
response = client.query("What is Python?")
print(response.content)
```

### Set API Keys
```bash
# Choose your provider
export ANTHROPIC_API_KEY="your-key-here"
# OR
export OPENAI_API_KEY="your-key-here"  
# OR
export GEMINI_API_KEY="your-key-here"
# OR run Ollama locally
```

## Usage Examples

### Provider Auto-Detection
```python
from any_llm import LLMClient

client = LLMClient()
print(f"Using: {client.get_current_provider()}")

response = client.query("Explain machine learning")
print(response.content)
```

### Specify Provider  
```python
client = LLMClient(provider="anthropic")
client = LLMClient(provider="openai")
client = LLMClient(provider="gemini")
client = LLMClient(provider="ollama")
```

### Custom Models
```python
client = LLMClient(provider="anthropic", model="claude-3-opus-20240229")
client = LLMClient(provider="openai", model="gpt-4")
client = LLMClient(provider="gemini", model="gemini-1.5-pro")
```

### Provider Switching
```python
client = LLMClient(provider="anthropic")

client.set_provider("openai")
client.set_provider("gemini", model="gemini-1.5-flash")
```

### Response Details
```python
response = client.query("What is OpenStack?")

print(f"Content: {response.content}")
print(f"Provider: {response.provider}")
print(f"Model: {response.model}")
print(f"Latency: {response.latency:.2f}s")
```

### Automatic Fallback
```python
client = LLMClient(fallback=True)
response = client.query("Hello world")
print(f"Succeeded with: {response.provider}")
```


## Supported Providers

| Provider | Models | Setup |
|----------|---------|-------|
| **Anthropic** | Claude 3 (Sonnet, Haiku, Opus) | `export ANTHROPIC_API_KEY=...` |
| **OpenAI** | GPT-3.5, GPT-4, GPT-4o | `export OPENAI_API_KEY=...` |
| **Google** | Gemini 1.5 (Flash, Pro) | `export GEMINI_API_KEY=...` |
| **Ollama** | Llama, Mistral, etc. | Run Ollama locally |

## Real-World Example

### Chatbot Integration
```python
from any_llm import LLMClient

class SimpleChatbot:
    def __init__(self):
        self.llm = LLMClient()
        
    def chat(self, message):
        response = self.llm.query(f"User: {message}\nAssistant:")
        return response.content
        
    def get_provider(self):
        return f"Using {self.llm.get_current_provider()}"

# Usage
bot = SimpleChatbot()
print(bot.chat("Hello!"))
print(bot.get_provider())
```

### Migration from Existing Code
```python
# BEFORE: Direct provider usage
import openai
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
content = response.choices[0].message.content

# AFTER: any-llm (works with any provider!)
from any_llm import LLMClient
client = LLMClient()
response = client.query("Hello")
content = response.content
```

## Configuration

### Environment Variables
```bash
# API Keys (set at least one)
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"

# Ollama (if using local models)
export OLLAMA_URL="http://localhost:11434"  # default
```

### Programmatic Configuration
```python
# With API key
client = LLMClient(
    provider="anthropic", 
    api_key="your-key-here"
)

# With custom model
client = LLMClient(
    provider="openai",
    model="gpt-4-turbo-preview"
)

# Disable fallback
client = LLMClient(fallback=False)
```

## Advanced Features

### Check Available Providers
```python
client = LLMClient()

# List configured providers
available = client.list_available_providers()
print(f"Available: {available}")

# Check specific provider
if client.is_provider_available("anthropic"):
    client.set_provider("anthropic")
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **GitHub**: https://github.com/sreenathmmenon/llmswap
- **PyPI**: https://pypi.org/project/llmswap/
- **Issues**: https://github.com/sreenathmmenon/llmswap/issues

---

Star this repo if llmswap helps simplify your LLM integration.