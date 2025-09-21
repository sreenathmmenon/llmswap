# llmswap v5.0 - Universal AI CLI & Python SDK

[![PyPI version](https://badge.fury.io/py/llmswap.svg)](https://badge.fury.io/py/llmswap)
[![PyPI Downloads](https://static.pepy.tech/badge/llmswap)](https://pepy.tech/projects/llmswap)
[![Homebrew](https://img.shields.io/badge/homebrew-available-blue?logo=homebrew)](https://github.com/llmswap/homebrew-tap)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Universal AI CLI & Python SDK**: One interface for 8+ providers (OpenAI GPT-4o/o1 | Claude 3.5 | Gemini Pro | Cohere | Perplexity | IBM watsonx | Groq | Together AI). Features: Multi-provider chat (Claude Code/Gemini CLI alternative), code generation (GitHub Copilot alternative), Python SDK integration, single-line CLI queries, cost optimization, age-appropriate AI. Switch providers instantly.

**Revolutionary v5.0**: First multi-provider conversational CLI with provider-native conversations, git-like configuration, zero vendor lock-in, and breakthrough age-appropriate AI explanations.

```bash
# 🆕 NEW v5.0: Age-Appropriate AI Explanations
llmswap ask "What is Docker?" --age 10
# Output: "Docker is like a magic lunch box! 🥪 When your mom packs..."

llmswap ask "What is blockchain?" --audience "business owner"
# Output: "Think of blockchain like your business ledger system..."

# 🆕 NEW v5.0: Teaching Personas & Personalization  
llmswap ask "Explain Python classes" --teach --mentor developer --alias "Sarah"
# Output: "[Sarah - Senior Developer]: Here's how we handle classes in production..."

# 🆕 NEW v5.0: Conversational Chat with Provider Switching
llmswap chat --age 25 --mentor tutor
# In chat: /switch anthropic  # Switch mid-conversation
# In chat: /provider         # See current provider
# Commands: /help, /switch, /clear, /stats, /quit

# 🆕 NEW v5.0: Provider Management & Configuration
llmswap providers                    # View all providers and their status
llmswap config set provider.models.cohere command-r-plus-08-2024
llmswap config set provider.default anthropic
llmswap config show

# Code Generation (GitHub Copilot CLI Alternative)
llmswap generate "sort files by size in reverse order"
# Output: du -sh * | sort -hr

llmswap generate "Python function to read JSON with error handling" --language python
# Output: Complete Python function with try/catch blocks

# Advanced Log Analysis with AI
llmswap logs --analyze /var/log/app.log --since "2h ago"
llmswap logs --request-id REQ-12345 --correlate

# Code Review & Debugging
llmswap review app.py --focus security
llmswap debug --error "IndexError: list index out of range"
```

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

## ⚠️ Privacy & Usage Disclaimers

**llmswap is an interface tool only** - all AI interactions and billing are handled directly by your chosen providers.

### 🔒 Context Privacy & Provider Switching
- **No context sharing**: When switching providers mid-conversation, NO conversation history is transferred between providers
- **Fresh start**: Each provider switch starts a completely new conversation thread
- **Legal compliance**: This protects your privacy and complies with provider Terms of Service
- **Your control**: You decide what each provider sees in their separate conversations

### 💰 Cost Information
**Cost estimates** (`~$X.XX estimated`) are approximate based on public pricing and common tokenizers. Actual costs may differ. **You are responsible for all provider costs and billing.**

**Legal Notice**: llmswap provides estimates and interface functionality for convenience only. We are not responsible for billing differences, provider charges, pricing changes, or data handling by individual providers. Always verify costs with your provider's billing dashboard.

## ⚡ Get Started in 30 Seconds

### 🍺 Homebrew (Recommended - macOS/Linux)
```bash
# Add our tap and install
brew tap llmswap/tap
brew install llmswap

# Ready to use immediately!
llmswap --help
```

### 🐍 PyPI (All platforms)
```bash
pip install llmswap
```

**Why Homebrew?** No virtualenv needed, global access, automatic dependency management, and easier updates.

## 📋 Quick Reference - New v5.0.3 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `llmswap providers` | View all providers and their status | Shows configured/missing API keys |
| `llmswap config set provider.models.<provider> <model>` | Update default model for any provider | `llmswap config set provider.models.cohere command-r-plus-08-2024` |
| `llmswap config list` | View current configuration | Shows all settings and models |
| `/switch` (in chat) | Switch providers mid-conversation | Privacy-compliant provider switching |
| `/provider` (in chat) | Show current provider and available options | Quick status check |

### 🔧 First-Time Setup (v5.0.3 NEW!)
```bash
# First run automatically creates ~/.llmswap/config.yaml with defaults
llmswap ask "Hello world"
# Output: 🔧 Creating config file at ~/.llmswap/config.yaml
#         ✅ Default configuration created

# View all providers and their configuration status
llmswap providers

# Set up your API keys and start using
export ANTHROPIC_API_KEY="your-key-here"
llmswap ask "Explain Docker in simple terms"
```

**💡 Smart Defaults:** llmswap comes pre-configured with sensible model defaults for all 8 providers. No configuration needed to get started!

```python
from llmswap import LLMClient

# Works with any provider you have configured
client = LLMClient()  # Auto-detects from environment/config
response = client.query("Explain quantum computing in 50 words")
print(response.content)
```

## 🎯 Why llmswap v5.0 for AI Development?

| Feature | llmswap v5.0 | Claude Code | Gemini CLI | LangChain | Direct APIs |
|---------|---------|-----------|---------|-----------|-------------|
| **AI Providers** | 8+ providers, instant switch | Claude only | Gemini only | 50+ complex setup | 1 per codebase |
| **Conversational Mode** | Provider-native, all providers | Yes, Claude only | Yes, Gemini only | Manual setup | Not available |
| **Memory Usage** | 99% reduction (provider-native) | Local storage | Local storage | Heavy framework | Manual |
| **Configuration** | Git-like, team-shareable | Basic settings | Basic settings | Complex files | None |
| **Cost Analytics** | Real-time tracking | No cost info | No cost info | External tools | Manual |
| **Provider Switching** | Mid-conversation switch | Locked to Claude | Locked to Gemini | Restart required | New session |
| **CLI Commands** | 10 powerful tools | Limited | Limited | Separate packages | None |
| **SDK + CLI** | Both included | CLI only | CLI only | SDK only | SDK only |
| **Open Source** | 100% MIT licensed | Proprietary | Proprietary | Open source | Varies |

## 🚀 Three Ways to Use llmswap:

**📚 1. Python Library/SDK**
```python
from llmswap import LLMClient
client = LLMClient()  # Import into any codebase
response = client.query("Analyze this data")
```

**⚡ 2. CLI Tools**  
```bash
llmswap generate "sort files by size"           # GitHub Copilot alternative
llmswap generate "Python function to read JSON" # Multi-language code generation
llmswap ask "Debug this error"                  # Terminal AI assistant
llmswap costs                                    # Cost optimization insights
```

**📊 3. Enterprise Analytics**
```python
stats = client.get_usage_stats()         # Track AI spend
comparison = client.get_provider_comparison()  # Compare costs
```

## 🎯 What's New in v5.0

### Revolutionary Teaching & Conversational Features
- **🎓 Age-Appropriate AI**: First CLI with age-targeted explanations (`--age 10`, `--audience "teacher"`)
- **🧑‍🏫 Teaching Personas**: 6 AI mentors (teacher, developer, tutor, professor, mentor, buddy)
- **👤 Personalized Aliases**: Custom AI names (`--alias "Sarah"` for your personal tutor)
- **💬 Multi-Provider Chat**: Provider-native conversational mode with mid-chat switching
- **🧠 Zero Local Storage**: 99% memory reduction, all context at provider level  
- **⚙️ Git-like Config**: Team-shareable configuration management
- **📊 Session Analytics**: Real-time cost and token tracking

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

# 🆕 v5.0: Conversational Sessions (Provider-Native)
client.start_chat_session()
response = client.chat("Tell me about Python")  # Context maintained
response = client.chat("What are its best features?")  # Remembers previous
client.end_chat_session()  # Clean provider-level cleanup

# 🆕 v5.0: Async Support for High Performance
import asyncio
from llmswap import AsyncLLMClient

async def main():
    async_client = AsyncLLMClient()
    response = await async_client.query_async("Process this data")
    
asyncio.run(main())
```

### 2️⃣ **CLI Suite** - 10 Powerful Terminal Commands
```bash
# 🆕 v5.0: Conversational Chat with Provider-Native Context
llmswap chat  # Interactive AI assistant with memory

# 🆕 v5.0: Configuration Management (Git-like)
llmswap config set provider.default anthropic
llmswap config export --file team-config.yaml

# Generate code from natural language (GitHub Copilot alternative)
llmswap generate "sort files by size in reverse order"
llmswap generate "Python function to read JSON file" --language python
llmswap generate "find large files over 100MB" --execute

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

### 3️⃣ **Provider Management & Model Configuration** (v5.0.3 NEW!)

**🎯 View All Providers and Models:**
```bash
# Beautiful table showing all providers, their status, and default models
llmswap providers
```

**Output Example:**
```
🤖 llmswap Provider Status Report
============================================================
| Provider   | Default Model              | Status            | Issue                    |
|============|============================|===================|==========================| 
| ANTHROPIC  | claude-3-5-sonnet-20241022 | ✅ CONFIGURED     |                          |
| OPENAI     | gpt-4o                     | ❌ NOT CONFIGURED | OPENAI_API_KEY missing   |
| GEMINI     | gemini-1.5-pro             | ✅ CONFIGURED     |                          |
| COHERE     | command-r-plus-08-2024     | ❌ NOT CONFIGURED | COHERE_API_KEY missing   |
| PERPLEXITY | sonar-pro                  | ✅ CONFIGURED     |                          |
| WATSONX    | granite-13b-chat           | ✅ CONFIGURED     |                          |
| GROQ       | llama-3.3-70b-versatile    | ✅ CONFIGURED     |                          |
| OLLAMA     | llama3.1                   | ⚠️ NOT RUNNING   | Local server not running |

📊 Summary: 5/8 providers available
```

**🔧 Model Configuration:**
```bash
# Update any provider's default model
llmswap config set provider.models.openai gpt-4o-mini
llmswap config set provider.models.cohere command-r-plus-08-2024
llmswap config set provider.models.anthropic claude-3-5-haiku-20241022

# Set default provider
llmswap config set provider.default anthropic

# View current configuration
llmswap config list

# Export/import team configurations
llmswap config export team-config.yaml
llmswap config import team-config.yaml --merge
```

**🚀 Handle Model Deprecations:**
When providers deprecate models (like Cohere's `command-r-plus` → `command-r-plus-08-2024`):
```bash
# Simply update your config - no code changes needed!
llmswap config set provider.models.cohere command-r-plus-08-2024
llmswap providers  # Verify the change
```

**⚙️ Configuration File Location:**
- **User config:** `~/.llmswap/config.yaml` (created automatically on first run)
- **Custom location:** Set `LLMSWAP_CONFIG_HOME` environment variable
- **Team sharing:** Export/import YAML configs for team standardization

**💬 Interactive Chat Commands:**
```bash
llmswap chat  # Start interactive conversation

# Available commands in chat:
/help      # Show all commands
/provider  # Show current provider and available providers
/switch    # Switch to different provider (privacy-compliant)
/clear     # Clear conversation history
/stats     # Show session statistics
/quit      # Exit chat

# Example session:
[0] > Hello, I'm working on a Python project
[anthropic] Hi! I'd be happy to help with your Python project...

[1] > /switch
📋 Available providers: anthropic, gemini, perplexity, watsonx, groq
Enter provider name: gemini

🔒 PRIVACY NOTICE: Switching to gemini
   ✅ NO conversation history will be shared with the new provider
   ✅ This protects your privacy and complies with provider Terms of Service
Continue? (y/n): y

✅ Switched to gemini
💬 Starting fresh conversation with gemini
```

### 4️⃣ **Analytics & Cost Optimization** (v4.0 NEW!)
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

### 🔧 **DevOps Engineers: Infrastructure as Code**
**Kubernetes and Docker automation:**
```bash
# Generate Kubernetes deployment
llmswap generate "Kubernetes deployment for React app with 3 replicas" --save k8s-deploy.yaml

# Docker multi-stage build
llmswap generate "Docker multi-stage build for Node.js app with Alpine" --language dockerfile

# Terraform AWS infrastructure
llmswap generate "Terraform script for AWS VPC with public/private subnets" --save main.tf
```

### 🎯 **Data Scientists: Analysis Workflows**
**Pandas, visualization, and ML pipeline generation:**
```bash
# Data analysis scripts
llmswap generate "Pandas script to clean CSV and handle missing values" --language python

# Visualization code
llmswap generate "Matplotlib script for correlation heatmap" --save plot.py

# ML pipeline
llmswap generate "scikit-learn pipeline for text classification with TF-IDF" --language python
```

### 💬 **App Developers: Full Applications**
**Complete app generation with modern frameworks:**
```bash
# Streamlit chatbot
llmswap generate "Streamlit chatbot app with session state and file upload" --save chatbot.py

# FastAPI REST API
llmswap generate "FastAPI app with CRUD operations for user management" --save api.py

# React component
llmswap generate "React component for data table with sorting and filtering" --language javascript --save DataTable.jsx
```

### 🤖 **AI/ML Engineers: Model Deployment**
**Production-ready ML workflows and deployments:**
```bash
# LangChain RAG pipeline
llmswap generate "LangChain RAG system with ChromaDB and OpenAI embeddings" --language python --save rag_pipeline.py

# Hugging Face model fine-tuning
llmswap generate "Script to fine-tune BERT for sentiment analysis with Hugging Face" --save finetune.py

# Gradio ML demo app
llmswap generate "Gradio app for image classification with drag and drop" --save demo.py

# Vector database setup
llmswap generate "Pinecone vector database setup for semantic search" --language python
```

### 🔒 **Security Engineers: Vulnerability Scanning**  
**Security automation and compliance scripts:**
```bash
# Security audit script
llmswap generate "Python script to scan for exposed API keys in codebase" --save security_scan.py

# OAuth2 implementation
llmswap generate "FastAPI OAuth2 with JWT tokens implementation" --language python

# Rate limiting middleware
llmswap generate "Redis-based rate limiting for Express.js" --language javascript
```

### 🛠️ **AI Agent Development: Tool Creation**
**Build tools and functions for AI agents (inspired by Anthropic's writing tools):**
```bash
# Create tool functions for agents
llmswap generate "Python function for web scraping with BeautifulSoup error handling" --save tools/scraper.py

# Database interaction tools
llmswap generate "SQLAlchemy functions for CRUD operations with type hints" --save tools/database.py

# File manipulation utilities
llmswap generate "Python class for safe file operations with context managers" --save tools/file_ops.py

# API integration tools
llmswap generate "Async Python functions for parallel API calls with rate limiting" --save tools/api_client.py

# Agent orchestration
llmswap generate "LangChain agent with custom tools for research tasks" --language python
```

### 🏆 **Hackathon Power Kit: Win Your Next Hackathon**
**Build complete MVPs in minutes, not hours:**
```bash
# RAG Chatbot for Document Q&A (Most requested hackathon project)
llmswap generate "Complete RAG chatbot with OpenAI embeddings, Pinecone vector store, and Streamlit UI for PDF document Q&A" --save rag_chatbot.py

# Full-Stack SaaS Starter (0 to production in 5 minutes)
llmswap generate "Next.js 14 app with Clerk auth, Stripe payments, Prisma ORM, and PostgreSQL schema for SaaS platform" --save saas_mvp.js
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