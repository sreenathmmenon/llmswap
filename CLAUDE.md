# Claude Memory: llmswap Project Journey

## Project Overview
**Project Name:** llmswap (originally planned as "any-llm")
**Purpose:** Multi-LLM provider Python package for seamless switching between AI providers
**Status:** ✅ Successfully published on PyPI and GitHub

## Package Evolution Timeline

### 1. Naming Journey
- **Original name:** any-llm (conflicted with existing PyPI package)
- **Second attempt:** ezllm (also taken on PyPI)
- **Final name:** llmswap (successfully published)

### 2. Package Structure
```
llmswap/
├── __init__.py          # Package exports and metadata
├── client.py           # Main LLMClient class
├── exceptions.py       # Custom exception classes
├── providers.py        # Provider implementations (Anthropic, OpenAI, Gemini, Ollama)
└── response.py         # LLMResponse data class
```

### 3. Key Features Implemented
- **Multi-provider support:** Anthropic, OpenAI, Google Gemini, Ollama
- **Zero-configuration:** Auto-detection via environment variables
- **Automatic fallback:** When primary provider fails
- **Unified interface:** Same API for all providers
- **Simple integration:** One-line provider switching

## User Information
**Name:** Sreenath Menon
**Email:** zreenathmenon@gmail.com (Note: starts with 'z' not 's')
**Role:** Advisory Software Engineer at IBM
**Experience:** 13+ years in software development
**Current Focus:** Transitioning to AI/ML field, seeking IC and product developer roles

## Technical Specifications

### Dependencies
- **Core:** anthropic, openai, google-generativeai, requests
- **Python:** 3.8+
- **Build:** setuptools, wheel, twine

### Installation
```bash
pip install llmswap
```

### Basic Usage
```python
from llmswap import LLMClient

client = LLMClient()  # Auto-detects provider
response = client.query("Hello, world!")
print(response.content)
```

## Publishing Details
- **PyPI Package:** https://pypi.org/project/llmswap/
- **Version:** 1.0.3 (aligned across PyPI and Git)
- **GitHub Repo:** https://github.com/sreenathmmenon/llmswap
- **License:** MIT

## Resume Integration
**Project added to Personal Projects section:**
- **llmswap - Multi-LLM Provider Interface:** Published Python package enabling seamless switching between Anthropic, OpenAI, Google Gemini, and Ollama with zero-configuration setup and automatic fallback.

## User Preferences & Guidelines
1. **No AI references:** Never mention Claude or AI-generated content
2. **No assumptions:** Don't add metrics or achievements without explicit request  
3. **Email precision:** Always use zreenathmenon@gmail.com (with 'z')
4. **Keep it simple:** Focus on functionality over complex features
5. **Open source focus:** Package intended for public use and contribution

## Career Context
- **Current salary:** 48L INR/annum
- **Target roles:** IC (Individual Contributor), Product Developer in AI field
- **Companies targeting:** FAANG, AI companies, product companies, startups
- **Resume rating:** 9.4/10 for AI/ML transitions
- **Salary expectations (India):** 80-90L INR
- **Salary expectations (UAE):** 25,000-32,000 AED/month

## Project Commands
```bash
# Development
pip install -e .

# Testing
python examples/basic_usage.py

# Building
python -m build

# Publishing
twine upload dist/*

# Git operations
git tag v1.0.3
git push origin v1.0.3
git push origin main
```

## Package Removal History
- **Cost tracking:** Removed per user request for simplicity
- **PowerVC references:** All removed for open-source release
- **Emojis:** Removed from README and documentation
- **AI attribution:** All Claude/AI references removed

## Technical Achievements
- ✅ Zero-configuration LLM switching
- ✅ Automatic provider fallback
- ✅ Clean, consistent API across providers
- ✅ Proper error handling and custom exceptions
- ✅ Complete documentation and examples
- ✅ MIT license for open source contribution
- ✅ PyPI publication with proper metadata
- ✅ GitHub repository with version alignment

## Key Learnings
1. **PyPI naming conflicts** are common - have backup names ready
2. **Package renaming** requires careful attention to all import statements
3. **Version alignment** between PyPI and Git is crucial for consistency
4. **User preferences** (like email spelling) must be precisely followed
5. **Open source preparation** requires removing all proprietary references

---
*Last updated: Current session*
*Status: Project complete and successfully deployed*