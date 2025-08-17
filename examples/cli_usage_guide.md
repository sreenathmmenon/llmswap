# llmswap CLI Usage Guide

The llmswap 3.0 CLI provides a professional command-line interface for AI-powered development workflows.

## Installation

```bash
pip install llmswap
```

After installation, the `llmswap` command is available globally.

## Quick Start

```bash
# Set up API key (choose one)
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key" 
export GEMINI_API_KEY="your-key"

# Basic usage
llmswap ask "What is Python?"
llmswap chat
```

## Commands Overview

### 1. Ask Questions (`llmswap ask`)

Quick one-line questions for immediate answers.

```bash
# Basic usage
llmswap ask "What is the difference between Git and GitHub?"
llmswap ask "How do I fix a merge conflict?"
llmswap ask "Explain Docker containers in simple terms"

# With specific provider
llmswap ask "Write a Python function to reverse a string" --provider openai
llmswap ask "What are the best practices for API design?" --provider anthropic

# Disable caching for real-time data
llmswap ask "What time is it now?" --no-cache

# Quiet mode (no tips)
llmswap ask "Explain recursion" --quiet
```

### 2. Interactive Chat (`llmswap chat`)

Start a conversation session with the AI.

```bash
# Start interactive session
llmswap chat

# With specific provider
llmswap chat --provider gemini

# Available commands in chat:
# - help: Show available commands
# - quit: Exit chat session  
# - provider: Show current provider
```

### 3. Code Review (`llmswap review`)

AI-powered code analysis and suggestions.

```bash
# Review any file
llmswap review app.py
llmswap review script.js --language javascript
llmswap review main.go --language go

# Focus on specific areas
llmswap review app.py --focus security
llmswap review api.py --focus performance
llmswap review utils.js --focus bugs
llmswap review styles.css --focus style

# Supported languages: python, javascript, typescript, java, cpp, c, go, rust, ruby, php
```

### 4. Debug Assistance (`llmswap debug`)

Get help with errors and debugging.

```bash
# Analyze error messages
llmswap debug --error "IndexError: list index out of range"
llmswap debug --error "TypeError: 'NoneType' object is not callable"
llmswap debug --error "SyntaxError: invalid syntax"

# Complex error analysis
llmswap debug --error "ConnectionError: HTTPSConnectionPool(host='api.example.com', port=443)"
```

### 5. Log Analysis (`llmswap logs`)

*Coming in v3.1.0 - Advanced log file analysis*

## Production Usage Examples

### DevOps Workflows

```bash
# Quick server troubleshooting
llmswap ask "Why might a Node.js server show high memory usage?"
llmswap debug --error "EADDRINUSE: address already in use :::3000"

# Code review in CI/CD
llmswap review src/auth.py --focus security --quiet
```

### Development Workflows

```bash
# Pre-commit code review
find . -name "*.py" -exec llmswap review {} --focus bugs \;

# Quick language help
llmswap ask "How to handle async errors in JavaScript?"
llmswap ask "Best practices for SQL injection prevention"
```

### Learning and Documentation

```bash
# Understand codebases
llmswap review legacy_code.php --focus style
llmswap ask "Explain this regex pattern: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Technology comparisons
llmswap ask "Kubernetes vs Docker Swarm comparison"
llmswap ask "When to use REST vs GraphQL?"
```

## Global Options

All commands support these global options:

- `--provider`, `-p`: Choose specific LLM provider (anthropic, openai, gemini, ollama)
- `--no-cache`: Disable response caching
- `--quiet`, `-q`: Suppress tips and extra output
- `--help`, `-h`: Show help for any command
- `--version`: Show version information

## Environment Variables

```bash
# Provider API keys
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"  
export GEMINI_API_KEY="your-gemini-key"

# IBM watsonx
export WATSONX_API_KEY="your-ibm-api-key"
export WATSONX_PROJECT_ID="your-project-id"

# Ollama (for local models)
export OLLAMA_URL="http://localhost:11434"
```

## Shell Integration

### Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ask="llmswap ask"
alias review="llmswap review"
alias debug="llmswap debug"

# Usage
ask "How to optimize database queries?"
review myfile.py --focus performance
```

### Scripting

```bash
#!/bin/bash
# Daily code review script
for file in $(find src/ -name "*.py" -mtime -1); do
    echo "Reviewing: $file"
    llmswap review "$file" --focus security --quiet
done
```

## Cost Optimization

llmswap automatically caches responses to save API costs:

- **First call**: Uses API (costs money)
- **Repeated calls**: Served from cache (free!)
- **Savings**: Typically 50-90% cost reduction

```bash
# These calls are cached automatically
llmswap ask "What is Python?"  # API call
llmswap ask "What is Python?"  # Cached (free!)

# Force fresh API call when needed
llmswap ask "Current Bitcoin price" --no-cache
```

## Error Handling

The CLI provides helpful error messages:

```bash
# Missing API keys
$ llmswap ask "Hello"
Error: No LLM providers available. Set at least one API key:
- ANTHROPIC_API_KEY
- OPENAI_API_KEY  
- GEMINI_API_KEY

# Invalid file
$ llmswap review nonexistent.py
Error: File 'nonexistent.py' not found
```

## Tips and Best Practices

1. **Use caching**: Leave caching enabled for repeated questions
2. **Choose providers**: Different providers excel at different tasks
3. **Focus reviews**: Use `--focus` for targeted code analysis
4. **Quiet mode**: Use `--quiet` in scripts and automation
5. **Provider switching**: Try different providers for better results

## Getting Help

```bash
llmswap --help                 # General help
llmswap ask --help            # Command-specific help
llmswap review --help         # Review options
llmswap debug --help          # Debug options
```

## What's Next

- **v3.1.0**: Advanced log analysis with `llmswap logs`
- **v3.2.0**: Shell completions and man pages
- **v3.x.x**: MCP protocol support for tool integration

---

**Documentation**: https://github.com/sreenathmmenon/llmswap
**Issues**: https://github.com/sreenathmmenon/llmswap/issues