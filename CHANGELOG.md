# Changelog

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