# Changelog

## [5.1.1] - 2025-10-01

### Documentation & Installation

#### **Improved**
- Added Quick Start section (30-second setup guide) to README
- Added Homebrew installation instructions alongside pip
- Removed "(if available)" from Twitter/X link - account is live
- Improved Stats & Achievements section:
  - Removed generic "Growing developer community" line
  - Added "Installation: pip, Homebrew, or from source"
- Better visibility for new users with immediate examples

#### **Fixed**
- Documentation clarity improvements
- Installation method visibility

---

## [5.1.0] - 2025-09-28

### 🚀 **Project Workspace System - Memory & Context**

#### **New Features**
- **Project Workspaces**: Home directory-based workspace system (`~/.llmswap/workspaces/`)
  - Zero project directory clutter - all data stored in home directory
  - Registry-based detection for fast workspace discovery (< 50ms)
  - Stable workspace IDs using `{project-name}-{hash}` format
  
- **Auto-Learning Tracking**: Automatically extract and save key learnings
  - Uses Groq (llama-3.1-8b-instant) for intelligent learning extraction
  - Builds learning journal without manual effort
  - Tracks 3-5 key concepts per conversation
  
- **Context-Aware Eklavya**: WorkspaceAwareMentor with project context
  - Loads project description, learnings, and architecture decisions
  - Provides context-relevant teaching and guidance
  - Builds on previous learnings when teaching new concepts
  
- **CLI Workspace Commands**: Complete workspace management via CLI
  - `llmswap workspace init` - Initialize workspace for current project
  - `llmswap workspace info` - View workspace statistics and settings
  - `llmswap workspace list` - List all workspaces across system
  - `llmswap workspace journal` - View learning journal
  - `llmswap workspace decisions` - View architecture decisions
  - `llmswap workspace context` - Edit project context
  
- **SDK Integration**: Automatic workspace detection and learning tracking
  - LLMClient auto-detects workspace from current directory
  - Tracks learnings after each query (if workspace exists)
  - Non-breaking - everything works without workspace

#### **Files Created**
- `llmswap/workspace/__init__.py` - Workspace package
- `llmswap/workspace/manager.py` - Core workspace management (~200 lines)
- `llmswap/workspace/detector.py` - Fast registry-based workspace detection
- `llmswap/workspace/registry.py` - Global workspace tracking system
- `llmswap/workspace/learnings_tracker.py` - Auto-learning extraction
- `llmswap/workspace/templates.py` - Markdown file templates
- `llmswap/eklavya/workspace_mentor.py` - Context-aware mentor

#### **Files Modified**
- `llmswap/cli.py` - Added cmd_workspace function and argparse integration
- `llmswap/client.py` - Added workspace detection and learning tracking
- `pyproject.toml`, `llmswap/__init__.py` - Version bump to 5.1.0

#### **Technical Details**
- **Storage Location**: `~/.llmswap/workspaces/{workspace-id}/`
- **Registry File**: `~/.llmswap/registry.json`
- **Workspace Files**: `workspace.json`, `context.md`, `learnings.md`, `decisions.md`
- **Detection Algorithm**: Registry lookup from current directory to home
- **Non-Breaking**: All workspace features are optional

#### **New Claude Sonnet 4.5 Support**
- **Latest Model**: Added `claude-sonnet-4-5` - Anthropic's best coding model
- **Default Updated**: Changed default Anthropic model to Claude Sonnet 4.5
- **Pricing Added**: $3/$15 per million tokens (same as previous Sonnet)
- **Performance**: "Best coding model in the world" per Anthropic

#### **Search Console Improvements** (Based on user data)
- **Claude Model Examples**: Added specific model documentation and examples
- **FastAPI Integration**: Added complete FastAPI + HTTPBearer example
- **AsyncIO Support**: Enhanced async examples and documentation
- **Response Object**: Better documentation of `response.content` usage

#### **Usage Examples**
```bash
# Initialize workspace
cd /path/to/project
llmswap workspace init --name "My Project"

# Chat with new Claude Sonnet 4.5 (best for coding)
llmswap chat --provider anthropic --model claude-sonnet-4-5

# View workspace info
llmswap workspace info
```

```python
# NEW: Claude Sonnet 4.5 - Best coding model
from llmswap import LLMClient

# Use best coding model by default
client = LLMClient(provider="anthropic", model="claude-sonnet-4-5")
response = client.query("Write a Python function to sort files")
print(response.content)  # Access response easily

# FastAPI Integration (based on user searches)
from fastapi import FastAPI, HTTPBearer
app = FastAPI()
security = HTTPBearer()

@app.post("/chat")
async def chat_endpoint(request: dict, token = Depends(security)):
    client = LLMClient(provider="anthropic", model="claude-sonnet-4-5")
    response = client.query(request["message"])
    return {"response": response.content}

# Workspace auto-detection
client = LLMClient()  # Workspace auto-detected if available
response = client.query("Explain async/await")  # Learning auto-tracked
```

## [5.0.5] - 2025-09-27

### 📝 **Documentation & Messaging Update**

#### **SDK-First Positioning**
- **Enhanced README**: Updated to emphasize Python SDK as the primary feature with CLI as a bonus
- **Comparison Tables**: Added SDK vs single-provider tools and CLI vs vendor CLIs comparisons
- **Better Code Examples**: Enhanced SDK examples showing easy provider switching
- **Updated Description**: Clarified "build apps without vendor lock-in" positioning
- **SDK Keywords**: Added 21 new SDK-focused keywords for better discoverability

#### **Fixes**
- **Corrected Author Email**: Fixed author email from `zreenathmenon@gmail.com` to `sreenathmmmenon@gmail.com`
- **Consistent Naming**: Updated author name to "Sreenath M Menon" across all files

#### **Key Messages**
- llmswap started as a **Python SDK** to solve vendor lock-in for app developers
- CLI tool is a useful **bonus** built on top of the SDK
- One tool, two ways to use: SDK for apps, CLI for terminal
- Works with existing subscriptions (Claude, OpenAI, Gemini, etc.)

**No code changes** - This is purely a documentation and messaging update.

## [5.0.4] - 2025-09-24

### 🔧 **Critical Model Update**

#### **Anthropic Claude Model Update**
- **Updated Default Model**: Changed from deprecated `claude-3-5-sonnet-20241022` to latest `claude-3-5-sonnet-20241220`
- **Backward Compatibility**: Kept deprecated model in pricing table with deprecation notice
- **Cost Estimator Fix**: Updated default model selection for Anthropic provider
- **User Impact**: Prevents errors from using retired model (retiring October 22, 2025)

#### **Documentation & Discovery**
- **Website Launch**: Added llmswap.org documentation links to README
- **SEO Enhancement**: Added Eklavya/mentorship keywords for better discoverability
- **New Keywords**: ai-mentor, ai-teaching, personalized-ai, ai-persona, eklavya, ai-learning, coding-mentor, ai-tutor

#### **Links Added**
- Documentation: https://llmswap.org
- CLI Reference: https://llmswap.org/docs/cli.html  
- SDK Guide: https://llmswap.org/docs/sdk.html

## [4.2.0] - 2025-09-20

### 🚀 **Enhanced Conversational Chat Interface**

#### **Revolutionary Multi-Provider Chat**
- **Conversational Context**: Chat maintains context across entire conversation
- **Provider Switching**: Switch providers mid-conversation while keeping context
- **Enhanced Commands**: `/help`, `/switch`, `/clear`, `/stats`, `/provider`, `/quit`
- **Real-time Analytics**: Live token counts and cost tracking during chat
- **Memory Management**: Conversation stored only in memory (privacy-first)

#### **Chat Features**
- **Cross-Provider Context**: Start with Claude, continue with GPT-4, maintain full conversation
- **Session Statistics**: Track messages, tokens, and costs in real-time  
- **Smart Provider Info**: See which provider responded to each message
- **Improved UX**: Professional chat interface with message numbering and status
- **Graceful Interrupts**: Handle Ctrl+C elegantly without losing chat state

#### **Technical Enhancements**
- **Enhanced CLI**: Upgraded chat command with slash commands and provider management
- **Provider Discovery**: New `get_available_providers()` method for dynamic provider listing
- **Memory Optimization**: Efficient conversation history management
- **Error Handling**: Improved error messages and recovery in chat mode

#### **Competitive Advantage**
- **Only multi-provider conversational CLI**: Claude Code (Anthropic only), Gemini CLI (Google only), llmswap (7 providers)
- **Cost optimization during chat**: Compare provider costs while chatting
- **Privacy-first**: No conversation storage, memory-only sessions
- **Professional UX**: Enterprise-grade chat interface with full provider control

## [4.1.4] - 2025-09-14

### 🏆 **Hackathon Power Kit Added**

#### **New Features**
- **Hackathon Section**: RAG chatbot and SaaS starter templates for winning hackathons
- **Vim Integration**: Highlighted vim editor integration in README (was undocumented!)
- **Enhanced Keywords**: Added terminal, vim, editor integration, RAG, and framework keywords

#### **Hackathon Examples**
- **RAG Document Q&A**: Complete chatbot with OpenAI embeddings and Pinecone
- **SaaS MVP Starter**: Full-stack with auth, payments, and database

#### **SEO Improvements**
- Added 14 new keywords: vim-integration, terminal-assistant, RAG, vector-database, etc.
- Better discoverability for hackathon participants and vim users

## [4.1.3] - 2025-09-14

### 📚 **Trending Use Cases Added**

#### **New Examples for Hot Topics**
- **AI/ML Engineers**: LangChain RAG, Hugging Face fine-tuning, Gradio apps, vector databases
- **Security Engineers**: API key scanning, OAuth2 implementation, rate limiting
- **AI Agent Development**: Tool creation for agents, database utilities, API clients, orchestration

#### **Impact**
- **Trending topics**: Covers RAG, agent tools, security automation
- **PyPI visibility**: Fresh examples for updated packages list
- **Developer reach**: Appeals to AI/ML and security engineers

## [4.1.2] - 2025-09-12

### 📚 **Enhanced Developer Examples**

#### **New Use Case Examples**
- **DevOps Engineers**: Added Kubernetes deployment, Docker multi-stage builds, Terraform infrastructure examples
- **Data Scientists**: Added Pandas data cleaning, Matplotlib visualization, scikit-learn ML pipeline examples
- **Infrastructure as Code**: Complete workflows for container orchestration and cloud infrastructure

#### **Developer Impact**
- **Broader appeal**: Examples now cover DevOps, data science, and infrastructure automation
- **Real-world scenarios**: Practical examples developers can immediately use
- **Enhanced discoverability**: More comprehensive use cases improve PyPI search visibility

## [4.1.1] - 2025-01-09

### 📚 **Documentation & SEO Updates**

#### **Enhanced README**
- **Prominent generate command**: Featured as primary CLI tool and GitHub Copilot alternative
- **Updated examples**: Show natural language to code generation capabilities
- **Improved positioning**: "Universal AI SDK + Code Generation CLI" title

#### **SEO Optimization**
- **Enhanced keywords**: Added code-generation, natural-language-to-code, copilot-cli-alternative
- **Better discoverability**: Improved search targeting for GitHub Copilot alternatives
- **IBM Watson keywords**: Added ibm-watson and watson-ai for enterprise search

## [4.1.0] - 2025-01-09

### 🚀 **New Feature: Natural Language Code Generation**

#### **Generate Command**
- **llmswap generate**: Transform natural language into executable commands and code
- **Multi-language support**: bash, python, javascript, and more
- **Project awareness**: Auto-detects Node.js, Python, Rust, Java project contexts
- **Safe execution**: Optional command execution with user confirmation
- **File output**: Save generated code with proper permissions

#### **Usage Examples**
```bash
llmswap generate "sort files by size in reverse order"
# Output: du -sh * | sort -hr

llmswap generate "Python function to read JSON file" --language python
llmswap generate "find large files" --execute  # Asks before running
llmswap generate "backup script" --save backup.sh  # Auto-executable
```

#### **Developer Impact** 
- **GitHub Copilot CLI alternative**: Works with any AI provider (OpenAI, Claude, Gemini, etc.)
- **Cross-platform**: Single tool for command generation across all operating systems
- **No vendor lock-in**: Switch between AI providers instantly
- **Cost optimization**: Use cheapest provider for code generation

## [4.0.5] - 2025-01-09

### 🐛 **Critical Fix: Complete Async Support**

#### **Missing Async Provider Implementations Added**
- **AsyncCoherProvider**: Complete async implementation for Cohere Command models
- **AsyncPerplexityProvider**: Async web-connected AI with real-time search
- **AsyncGroqProvider**: Async ultra-fast inference for high-throughput applications

#### **Usage Tracking Consistency**  
- **Fixed**: All async providers now properly track token usage (`input_tokens`, `output_tokens`)
- **Standardized**: Both `usage` and `metadata` fields populated consistently across sync/async
- **Analytics Ready**: Full cost tracking and optimization support in async mode

#### **Provider Integration**
- **AsyncLLMClient**: Updated with all 7 providers (Anthropic, OpenAI, Gemini, Cohere, Perplexity, watsonx, Groq, Ollama)
- **Auto-detection**: Async fallback and provider switching now supports all providers
- **Streaming**: Complete async streaming support for compatible providers

### 📊 **Impact**
- **Developer Experience**: Full feature parity between sync and async clients
- **Enterprise Ready**: Complete async support for high-performance applications
- **Cost Analytics**: Async usage tracking enables complete cost optimization

## [4.0.4] - 2025-09-05

### 🚀 **NEW PROVIDERS: Enterprise AI Expansion**

#### **Cohere Integration** 
- **Enterprise RAG Models**: command-r-03-2024, command-r-plus-08-2024, aya-expanse-8b/32b
- **Pricing**: Starting at $0.50/$1.50 per million tokens
- **Use Cases**: Enterprise retrieval-augmented generation, multilingual AI

#### **Perplexity Integration**
- **Web-Connected AI**: sonar-pro, pplx-7b-online, pplx-70b-online  
- **Real-time Data**: Up-to-date information with web search capabilities
- **Pricing**: Estimated $0.2-$4 per million tokens

#### **Enhanced Model Support**
- **OpenAI**: Added gpt-4o, gpt-4o-mini, o1-preview, o1-mini (reasoning models)
- **Anthropic**: Updated to claude-3-5-sonnet-20241022, added claude-3-5-haiku
- **Google**: Added gemini-2.0-flash-exp (experimental cutting-edge)

### 🎯 **Strategic Positioning Update**
- **Universal AI SDK**: Repositioned as infrastructure layer for AI applications
- **Enterprise Focus**: 7 providers, cost optimization, usage analytics
- **Developer Integration**: Library/SDK + CLI tools + enterprise metrics

### 🔧 **Improvements**
- **Cost Analytics**: Updated pricing for all 7 providers with 20+ models
- **Provider Defaults**: Optimized to latest cost-effective models
- **SEO Enhancement**: Strategic keywords for developer discovery
- **Documentation**: Clear 3-way usage patterns (Library, CLI, Analytics)

---

## [4.0.3] - 2025-09-05

### 🚀 **NEW PROVIDER: Groq Integration**

#### **Ultra-Fast Inference**
- **Groq Provider**: Complete integration with Groq's high-performance LPU inference
- **Models Supported**: llama-3.1-8b-instant, llama-3.3-70b-versatile, gpt-oss-20b
- **Speed**: Up to 840+ tokens/second (5-15x faster than other providers)
- **Cost-Effective**: Starting at $0.05/$0.08 per million tokens

#### **Enhanced Features**
- **Provider Priority**: Groq added to auto-detection and fallback chain
- **Cost Analytics**: Groq pricing integrated into cost comparison tools
- **CLI Support**: Full compatibility with all existing CLI commands
- **SDK Integration**: Seamless switching with `LLMClient(provider="groq")`

### 🔧 **Improvements**
- **SEO Optimization**: Enhanced discoverability with strategic keywords
- **Documentation**: Updated setup instructions and provider examples
- **Dependency Management**: Added groq>=0.4.0 for reliable API access

---

## [4.0.0] - 2025-09-04

### 🎉 Major Release: Analytics & Cost Optimization Suite

### ✨ **NEW FEATURES**

#### **Cost Analytics & Optimization**
- **Provider Cost Comparison**: Compare real-time costs across OpenAI, Claude, Gemini, watsonx, and Ollama
- **Usage Tracking**: Detailed analytics on queries, tokens, costs, and response times
- **Cost Optimization**: AI-powered recommendations to reduce API spending by 50-90%
- **Monthly Cost Estimation**: Budget planning with realistic usage patterns

#### **Enhanced CLI Tools**
- `llmswap compare --input-tokens X --output-tokens Y` - Compare provider costs
- `llmswap usage --days N` - View usage statistics and trends
- `llmswap costs` - Get personalized cost optimization insights

#### **Python SDK Analytics**
- `client.get_usage_stats()` - Comprehensive usage analytics
- `client.get_cost_breakdown()` - Detailed cost analysis with optimization suggestions
- `client.get_provider_comparison()` - Real-time provider cost comparison
- `client.chat()` - Conversation memory for contextual interactions

#### **New Provider Support**
- **Enhanced watsonx Integration**: Full IBM watsonx.ai support with Granite models
- **Expanded Ollama Support**: 100+ local models including Llama, Mistral, Phi, Qwen
- **Groq Integration**: High-performance inference ✅ COMPLETED in v4.0.3

---

## [3.0.0] - 2024-08-17 - Major Release: Professional CLI Tool

### 🚀 Added - Revolutionary CLI Interface
- **Global `llmswap` command** - Professional command-line interface installed system-wide
- **Ask command** (`llmswap ask`) - Quick one-line questions with AI assistance
- **Interactive chat** (`llmswap chat`) - Full conversational AI sessions  
- **Code review** (`llmswap review`) - AI-powered code analysis with specialized focus areas
- **Debug assistant** (`llmswap debug`) - Error analysis and troubleshooting guidance
- **Log analysis** (`llmswap logs`) - Framework for future log file analysis capabilities

### 🛠️ CLI Features & Options
- **Focus areas for code review**: bugs, security, style, performance, general analysis
- **Provider selection** - Choose specific LLM provider via `--provider` flag
- **Caching control** - `--no-cache` flag for real-time queries
- **Quiet mode** - `--quiet` flag perfect for automation and scripting
- **Auto language detection** - Automatic programming language detection for code review
- **Comprehensive help** - Built-in help system for all commands and options

### 📚 Professional Documentation
- **CLI Usage Guide** - Complete documentation with real-world examples  
- **Production workflows** - DevOps, development, and automation use cases
- **Shell integration** - Aliases, scripting, and automation examples
- **Error handling** - Clear error messages and troubleshooting guidance

### 🏗️ Technical Implementation
- **Entry point** - `llmswap.cli:main` provides global `llmswap` command
- **Argument parsing** - Professional CLI with subcommands and global options
- **Error handling** - Graceful error handling with helpful user messages
- **Cross-platform** - Full compatibility with Linux, macOS, and Windows

### 📈 Enhanced Package Structure
- **README restructured** - CLI prominently featured as primary interface
- **Package scripts** - Added CLI entry point via `[project.scripts]`
- **Version management** - Updated to 3.0.0 across all project files

### ⚡ Backward Compatibility
- **No breaking changes** - All existing Python SDK functionality preserved
- **Seamless upgrade** - `pip install llmswap` provides both SDK and CLI
- **Migration friendly** - Existing Python code continues to work unchanged

## [2.1.5] - 2024-08-17
### Added
- New examples showing practical use cases and cost savings
- Smart cost optimizer example shows how caching reduces API bills
- Provider comparison tool helps users test different LLMs
- Simple chat interface example for quick testing
- Examples documentation with getting started guide

## [2.1.3] - 2025-08-16
### Added
- **Enhanced Model Keywords**: Added popular model names for better search discoverability
- Added keywords: llama, llama3, mistral, phi, phi3, qwen, gemma for local model searches
- Added OpenAI open-source model keywords: gpt-oss, openai-open-source
- Added general open-source keywords: open-source-llm, local-llm, free-llm
- Improved SEO coverage for developers seeking local and open-source AI models

## [2.1.2] - 2025-08-16
### Changed
- **Critical SEO Fix**: Added explicit IBM WatsonX mention to main package description
- Enhanced enterprise discoverability with WatsonX in primary PyPI description
- Improved B2B search visibility for IBM AI solution searches

## [2.1.1] - 2025-08-16
### Changed
- **SEO Optimization**: Enhanced PyPI discoverability with trending keywords
- Updated package description to "Universal LLM SDK | OpenAI GPT-4, Claude, Gemini, IBM WatsonX API Wrapper with Cost Optimization"
- Added quick install badge to README for improved GitHub visual appeal
- Enhanced documentation with more targeted keyword optimization for better search visibility
- Added explicit IBM WatsonX mention in main description for enterprise SEO

## [2.1.0] - 2025-08-10
### Added
- **Response Caching**: Built-in memory caching for cost savings and performance
  - Disabled by default for security (multi-user safety)
  - Configurable TTL (time-to-live) for cached responses
  - Context-aware caching with user/session isolation support
  - Memory limit protection with LRU eviction
  - Cache statistics and management APIs
- Cache methods: `clear_cache()`, `invalidate_cache()`, `get_cache_stats()`
- `from_cache` attribute in LLMResponse to identify cached responses
- Thread-safe cache operations

### Changed
- Enhanced LLMClient and AsyncLLMClient constructors with cache parameters
- Updated query methods to support cache_context, cache_ttl, and cache_bypass options

## [2.0.2] - 2025-08-09
### Fixed
- Fixed Anthropic model compatibility issues with claude-3-5-sonnet-20241022
- Resolved async provider initialization and parameter handling
- Fixed streaming functionality for all async providers
- Corrected logging system implementation

### Added
- Complete async/await support with AsyncLLMClient
- Real-time streaming responses for OpenAI, Anthropic, and Ollama
- Comprehensive JSON logging system with privacy protection
- Enhanced error handling and retry mechanisms

### Changed
- Updated default Anthropic model to latest version
- Improved package stability and production readiness
- Maintained full backward compatibility with v1.x API

## [2.0.1] - 2025-08-09
### Added
- Async support with AsyncLLMClient for non-blocking operations
- Real-time streaming responses for OpenAI, Anthropic, and Ollama
- Request logging system with JSON format and privacy protection
- Enhanced performance for production workloads

### Changed
- Updated default Anthropic model to claude-3-5-sonnet-20241022
- Package status upgraded to Production/Stable
- Added async dependencies (aiohttp, aiofiles, httpx)
- Maintained full backward compatibility with v1.x API

### Fixed
- Fixed model parameter handling in AnthropicProvider
- Resolved async provider initialization issues

## [1.5.1] - 2025-08-07
### Changed
- Enhanced PyPI metadata with watsonx and IBM keywords for better discoverability
- Updated package description to highlight enterprise capabilities

## [1.5.0] - 2025-08-07
### Added
- **IBM watsonx Integration** - Native support for IBM watsonx foundation models
  - Complete WatsonxProvider implementation with authentication
  - Support for IBM Granite models and other watsonx foundation models
  - Environment variable configuration (WATSONX_API_KEY, WATSONX_PROJECT_ID)
  - Auto-detection and fallback support for watsonx

## [1.4.0] - 2025-08-07
### Added
- GPT-OSS support via Ollama integration
  - gpt-oss-20b model support (16GB RAM requirement)
  - gpt-oss-120b model support (80GB VRAM requirement)
- Complete documentation for Ollama model support
  - Llama 3.1 and 3.2 model families (1B to 405B parameters)
  - Mistral models including Codestral and Nemo variants
  - Google Gemma 2 and 3 model series
  - Qwen 2.5 models with coder-specific variants
  - Microsoft Phi 3 and 4 models
  - IBM Granite Code models and other specialized options
- Updated documentation with model specifications and usage examples

## [1.0.4] - 2025-08-07
### Added
- Comprehensive pytest test suite
- GitHub Actions CI/CD pipeline
- Enhanced SEO keywords and package description
### Changed
- Improved project documentation and professionalism
### Added
- GPT-OSS provider support

## [1.5.0] - Planned  
### Added
- IBM watsonx provider support

## [1.0.3] - 2025-08-03
### Changed
- Renamed package from any-llm to llmswap

## [1.0.2] - 2025-08-02
### Fixed
- PyPI naming conflict with existing package

## [1.0.1] - 2025-08-02
### Added
- Automatic fallback to next available provider
- Method to check provider availability

## [1.0.0] - 2025-08-01
### Added
- Initial release
- Support for Anthropic, OpenAI, Google Gemini, and Ollama
- Auto-detection of providers via environment variables