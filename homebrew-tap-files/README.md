# llmswap Homebrew Tap

Official Homebrew tap for [llmswap](https://github.com/sreenathmmenon/llmswap) - Universal AI CLI with multi-provider support, teaching features, and cost optimization.

## Installation

```bash
brew tap llmswap/tap
brew install llmswap
```

## Quick Start

```bash
# Get help
llmswap --help

# Basic usage (requires API keys)
llmswap ask "Explain quantum computing in simple terms"

# 🆕 NEW v5.0: Age-appropriate explanations
llmswap ask "What is Docker?" --age 10
llmswap ask "What is blockchain?" --audience "business owner"

# 🆕 NEW v5.0: Conversational chat mode
llmswap chat

# 🆕 NEW v5.0: Teaching mode with personas
llmswap ask "Explain Python classes" --teach --mentor developer

# Configuration
llmswap config show
llmswap config set provider.default anthropic

# Cost analysis
llmswap costs --input-tokens 1000 --output-tokens 500
```

## Features

- **8+ AI Providers**: OpenAI GPT-4o/o1, Claude, Gemini, Cohere, Perplexity, IBM watsonx, Groq, Ollama
- **Conversational Chat**: Provider-native conversations with mid-chat provider switching
- **Age-Appropriate Explanations**: Target responses for specific ages or audiences
- **Teaching Personas**: 6 different mentorship styles for enhanced learning
- **Cost Optimization**: Real-time cost tracking and provider comparison
- **Code Generation**: GitHub Copilot CLI alternative with multi-language support
- **Enterprise Analytics**: Usage tracking and cost analysis

## Requirements

- macOS 10.15+ or Linux
- Python 3.8+ (automatically managed by Homebrew)
- API keys for desired providers (set via environment variables)

## API Key Setup

```bash
# Set environment variables for your chosen providers
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AI..."
export GROQ_API_KEY="gsk_..."
export COHERE_API_KEY="..."
export PERPLEXITY_API_KEY="pplx-..."

# For IBM watsonx
export WATSONX_API_KEY="..."
export WATSONX_PROJECT_ID="..."
```

## Why Homebrew?

- ✅ **No virtualenv needed**: Global installation and access
- ✅ **Automatic dependencies**: Homebrew manages Python and packages
- ✅ **Easy updates**: `brew upgrade llmswap`
- ✅ **Clean uninstall**: `brew uninstall llmswap`
- ✅ **System integration**: Available from any directory

## Alternative Installation

If you prefer pip:
```bash
pip install llmswap
```

## Documentation

- **Main Repository**: [github.com/sreenathmmenon/llmswap](https://github.com/sreenathmmenon/llmswap)
- **PyPI Package**: [pypi.org/project/llmswap](https://pypi.org/project/llmswap/)
- **Issues**: [github.com/sreenathmmenon/llmswap/issues](https://github.com/sreenathmmenon/llmswap/issues)

## Updates

To update to the latest version:
```bash
brew update
brew upgrade llmswap
```

## Uninstall

```bash
brew uninstall llmswap
brew untap llmswap/tap  # Optional: remove the tap
```

## Support

For issues, feature requests, or questions:
- Create an issue: [github.com/sreenathmmenon/llmswap/issues](https://github.com/sreenathmmenon/llmswap/issues)
- Check documentation: [Main Repository](https://github.com/sreenathmmenon/llmswap)

---

**llmswap v5.0** - The world's first multi-provider conversational AI CLI with teaching features and cost optimization.