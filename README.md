# llmswap - Complete AI CLI Suite + Python SDK

[![PyPI version](https://badge.fury.io/py/llmswap.svg)](https://badge.fury.io/py/llmswap)
[![pip install llmswap](https://img.shields.io/badge/pip%20install-llmswap-brightgreen)](https://pypi.org/project/llmswap/)
[![PyPI Downloads](https://static.pepy.tech/badge/llmswap)](https://pepy.tech/projects/llmswap)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Two Powerful Interfaces: 5 AI CLI Tools + Complete Python SDK**

## 🚀 Terminal AI Suite - No Browser Required

```bash
# Install once, get 5 AI CLI tools
pip install llmswap

# 1. One-line AI assistant
llmswap ask "How to optimize PostgreSQL queries?"

# 2. Interactive AI chat  
llmswap chat

# 3. AI code reviewer
llmswap review app.py --focus security

# 4. AI debugger
llmswap debug --error "ConnectionTimeout: Connection timed out"

# 5. AI log analyzer
llmswap logs --analyze /var/log/app.log --since "2h ago"
```

## 📦 Python SDK for Applications

```python
pip install llmswap
from llmswap import LLMClient

client = LLMClient()  # Auto-detects OpenAI, Claude, Gemini, etc.
response = client.query("Analyze this data trend")
print(response.content)
```

**Complete AI-powered development workflow in your terminal + Python library for applications**

## What's New in v3.0.0

### Command Line Interface (NEW!)

```bash
# Install once, use everywhere
pip install llmswap

# Universal AI workflows for any use case
llmswap ask "Write a professional email response"
llmswap ask "Analyze this sales data trend"
llmswap ask "Explain quantum physics simply"
llmswap review myfile.py --focus security  
llmswap debug --error "ConnectionError: timeout"
llmswap chat  # Interactive AI assistant
```

### Python SDK Features

- **Multi-provider support** - Anthropic, OpenAI, Google Gemini, IBM watsonx, Ollama
- **Response caching** - Save 50-90% on API costs with intelligent caching
- **Auto-fallback** - Automatic provider switching when one fails
- **Zero configuration** - Works with environment variables out of the box
- **Async support** - Non-blocking operations with streaming responses
- **Thread-safe** - Safe for concurrent applications and multi-user environments

## Perfect for Hackathons & Students

**Built from hackathon experience to help developers ship faster:**

- **Move Fast** - One line setup, focus on your idea not infrastructure
- **Stay Within Budget** - Python SDK offers cost savings for repeated queries
- **Experiment Freely** - Switch between providers instantly, find what works
- **Scale Easily** - Start with free tiers, upgrade when needed
- **Multi-User Ready** - Build apps that serve your whole team/class
- **Learn Best Practices** - Production-ready patterns from day one

```python
# Perfect hackathon starter - works with any API key you have
from llmswap import LLMClient

client = LLMClient(cache_enabled=True)  # Save money from day 1
response = client.query("Help me build an AI-powered app")
print(response.content)
```

## CLI Quick Start

### Installation
```bash
pip install llmswap
```

### Set API Key
```bash
# Choose your provider (any one is enough)
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"  
export GEMINI_API_KEY="your-gemini-key"
```

### CLI Commands

```bash
# Ask questions
llmswap ask "What is Docker?"
llmswap ask "How to optimize SQL queries?" --provider openai

# Interactive chat
llmswap chat

# Code review with AI
llmswap review app.py --focus security
llmswap review script.js --focus performance  
llmswap review main.go --focus bugs

# Debug assistance
llmswap debug --error "TypeError: 'NoneType' object is not callable"
llmswap debug --error "ECONNREFUSED: Connection refused"

# Get help
llmswap --help
llmswap review --help
```

### Production Examples

```bash
# DevOps workflows
llmswap ask "Why is my Node.js app using too much memory?"
llmswap debug --error "Error: listen EADDRINUSE: address already in use :::3000"

# Code review automation
find . -name "*.py" -exec llmswap review {} --focus security --quiet \;

# Daily development
llmswap ask "Best practices for REST API design"
llmswap review pull_request.diff --focus style
```

## Python SDK Quick Start

### Installation  
```bash
pip install llmswap
```

### Basic Usage
```python
from llmswap import LLMClient

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
# OR
export WATSONX_API_KEY="your-ibm-api-key"
export WATSONX_PROJECT_ID="your-project-id"
# OR run Ollama locally
```

## Usage Examples

### Async Support (New in v2.0)

```python
import asyncio
from llmswap import AsyncLLMClient

async def main():
    client = AsyncLLMClient(provider="openai")
    
    # Async query
    response = await client.query("Explain quantum computing")
    print(response.content)
    
    # Streaming response
    print("Streaming: ", end="")
    async for chunk in client.stream("Write a haiku"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

### Response Caching (New in v2.1)

**What is Response Caching?**  
Intelligent caching stores LLM responses temporarily to avoid repeated expensive API calls for identical queries.

**Default State:** DISABLED (for security in multi-user environments)

**Key Advantages:**
- **Massive cost savings:** 50-90% reduction in API costs
- **Lightning speed:** 100,000x+ faster responses (0.001s vs 1-3s)
- **Rate limit protection:** Avoid hitting API limits
- **Reliability:** Serve cached responses even if API is down

#### Basic Usage

```python
from llmswap import LLMClient

# Step 1: Enable caching (disabled by default)
client = LLMClient(cache_enabled=True)

# First call: hits API ($$$)
response = client.query("What is machine learning?")
print(f"From cache: {response.from_cache}")  # False

# Identical call: returns from cache (FREE!)
response = client.query("What is machine learning?")  
print(f"From cache: {response.from_cache}")  # True
```

#### Advanced Configuration

```python
# Customize cache behavior
client = LLMClient(
    cache_enabled=True,
    cache_ttl=3600,        # 1 hour expiry
    cache_max_size_mb=50   # Memory limit
)

# Multi-user security: separate cache per user
response = client.query(
    "Show my account balance",
    cache_context={"user_id": "user123"}
)

# Per-query settings
response = client.query(
    "Current weather",
    cache_ttl=300,         # 5 minutes for weather
    cache_bypass=True      # Force fresh API call
)

# Monitor performance
stats = client.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']}%")
print(f"Cost savings: ~{stats['hit_rate']}%")
```

#### Security for Multi-User Applications

```python
# WRONG: Shared cache (security risk)
client = LLMClient(cache_enabled=True)
client.query("Show my private data")  # User A
client.query("Show my private data")  # User B gets User A's data!

# RIGHT: Context-aware caching
client.query("Show my private data", cache_context={"user_id": current_user.id})
```

**When to Use Caching:**
- Single-user applications
- Public/educational content queries  
- FAQ bots and documentation assistants
- Development and testing (save API costs)

**When NOT to Use:**
- Multi-user apps without context isolation
- Real-time data queries (stock prices, weather)
- Personalized responses without user context

### Request Logging (New in v2.0)

```python
from llmswap import AsyncLLMClient

# Enable logging to file
client = AsyncLLMClient(
    provider="anthropic",
    log_file="/tmp/requests.log",
    log_level="info"
)

# All requests and responses are logged with metadata
response = await client.query("Hello world")

# Logs include: timestamp, provider, model, latency, token counts
```

### Provider Auto-Detection
```python
from llmswap import LLMClient

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
| **Ollama** | 100+ local models (see below) | Run Ollama locally |
| **IBM watsonx** | Granite, Llama, and foundation models | `export WATSONX_API_KEY=...` |

### GPT-OSS Support (OpenAI's Open-Weight Models)

OpenAI's new open-source models are now supported via Ollama:

```python
# Pull the model first: ollama pull gpt-oss-20b
client = LLMClient(provider="ollama", model="gpt-oss-20b")
client = LLMClient(provider="ollama", model="gpt-oss-120b")

# Run reasoning tasks locally
response = client.query("Solve this step by step: What is 47 * 23?")
```

### Popular Ollama Models Supported

**GPT-OSS (OpenAI Open-Weight)**
- `gpt-oss-20b` - Efficient 20B reasoning model (16GB RAM)
- `gpt-oss-120b` - Advanced 120B model (80GB VRAM)

**Llama Family**  
- `llama3.2` (1B, 3B, 8B, 70B, 90B)
- `llama3.1` (8B, 70B, 405B)
- `llava-llama3` (Vision + Language)

**Mistral Models**
- `mistral` (7B)
- `mistral-nemo` (12B)
- `mistral-small` (22B)
- `codestral` (22B - Code specialist)

**Google Gemma**
- `gemma2` (2B, 9B, 27B)
- `gemma3` (Latest from Google)

**Qwen Series**  
- `qwen2.5` (0.5B, 1.5B, 3B, 7B, 14B, 32B)
- `qwen2.5-coder` (Code specialist)
- `qwq` (32B - Reasoning model)

**Microsoft Phi**
- `phi3` (3.8B - Efficient small model)
- `phi4` (14B - Advanced reasoning)

**Other Popular Models**
- `granite-code` (IBM - Code generation)
- `deepseek-coder` (Code specialist)
- `zephyr` (Assistant fine-tuned)
- `smollm2` (135M, 360M, 1.7B)

### Ollama Usage Examples

```python
# Any Ollama model works out of the box
client = LLMClient(provider="ollama", model="llama3.2")
client = LLMClient(provider="ollama", model="mistral-nemo")
client = LLMClient(provider="ollama", model="qwen2.5-coder")
client = LLMClient(provider="ollama", model="phi4")

# Check what models you have locally
# ollama list

# Pull new models
# ollama pull mistral-nemo
# ollama pull gpt-oss-20b
```

### IBM watsonx Integration

Enterprise-grade AI with IBM's foundation models:

```python
# Set environment variables
# export WATSONX_API_KEY="your-ibm-cloud-api-key"
# export WATSONX_PROJECT_ID="your-project-id"

client = LLMClient(provider="watsonx")
client = LLMClient(provider="watsonx", model="ibm/granite-3-8b-instruct")

# Popular watsonx models
client = LLMClient(provider="watsonx", model="ibm/granite-3-8b-instruct")
client = LLMClient(provider="watsonx", model="meta-llama/llama-3-70b-instruct")
client = LLMClient(provider="watsonx", model="mistralai/mixtral-8x7b-instruct-v01")

response = client.query("Analyze this business data and provide insights")
```

## Practical Examples & CLI Tools

The package includes ready-to-use examples and CLI tools for common developer workflows:

### Available Examples

#### Developer Workflow Tools
- **`cli_assistant.py`** - Full-featured CLI with interactive mode and commands
- **`code_reviewer.py`** - AI-powered code review with focus areas (bugs, security, style)
- **`debug_helper.py`** - Error analysis, stack trace interpretation, debugging strategies
- **`provider_comparison.py`** - Compare responses from different LLM providers

#### Cost Optimization & Performance  
- **`smart_cost_optimizer.py`** - Demonstrates cost savings through caching (Python SDK)
- **`quick_chat.py`** - Minimal chat interface showing llmswap simplicity
- **`ask`** - One-liner CLI script for quick questions

#### Getting Started
- **`basic_usage.py`** - Simple integration examples
- **`hackathon_starter.py`** - Perfect starting point for hackathons and student projects

### Quick CLI Usage

```bash
# One-liner questions  
./examples/ask "What is Python?"
./examples/ask "Explain machine learning"

# Interactive chat
python examples/cli_assistant.py

# Code review
python examples/code_reviewer.py myfile.py --focus security
python examples/code_reviewer.py --language javascript --focus bugs < script.js

# Debug assistance
python examples/debug_helper.py --error "IndexError: list index out of range"
python examples/debug_helper.py --stack-trace "$(cat error.log)"

# Provider comparison
python examples/provider_comparison.py

# Cost optimization demo
python examples/smart_cost_optimizer.py
```

### Integration Examples

#### Chatbot Integration
```python
from llmswap import LLMClient

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

# AFTER: llmswap (works with any provider!)
from llmswap import LLMClient
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

# IBM watsonx (enterprise models)
export WATSONX_API_KEY="your-ibm-cloud-api-key"
export WATSONX_PROJECT_ID="your-watsonx-project-id"

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

Star this repo if llmswap helps simplify your language model integration.
