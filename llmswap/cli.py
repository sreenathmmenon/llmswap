#!/usr/bin/env python3
"""
llmswap CLI - Command-line interface for llmswap

Usage:
    llmswap ask "What is Python?"
    llmswap chat
    llmswap logs --analyze /var/log/app.log --since "2h ago"
    llmswap review myfile.py --focus security
    llmswap debug --error "IndexError: list index out of range"
"""

import sys
import argparse
import subprocess
from pathlib import Path
from .client import LLMClient
from .exceptions import LLMSwapError

def cmd_ask(args):
    """Handle 'llmswap ask' command"""
    if not args.question:
        print("Error: Question is required")
        return 1
    
    try:
        client = LLMClient(
            provider=args.provider or "auto",
            cache_enabled=not args.no_cache
        )
        response = client.query(args.question)
        
        cache_indicator = "[cached]" if response.from_cache else "[fresh]"
        print(f"{cache_indicator} {response.content}")
        
        if response.from_cache and not args.quiet:
            print("\nTip: This answer was cached (free!)")
            
    except LLMSwapError as e:
        print(f"Error: {e}")
        return 1

def cmd_chat(args):
    """Handle 'llmswap chat' command"""
    try:
        client = LLMClient(
            provider=args.provider or "auto",
            cache_enabled=not args.no_cache
        )
        
        print("llmswap Interactive Chat")
        print(f"Provider: {client.get_current_provider()}")
        print("Type 'quit' to exit, 'help' for commands\n")
        
        while True:
            try:
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                    
                elif user_input.lower() == 'help':
                    print("\nCommands:")
                    print("  help - Show this help")
                    print("  quit - Exit chat")
                    print("  provider - Show current provider")
                    continue
                    
                elif user_input.lower() == 'provider':
                    print(f"Current provider: {client.get_current_provider()}")
                    continue
                
                # Get response
                response = client.query(user_input)
                cache_indicator = "[cached]" if response.from_cache else "[fresh]"
                print(f"\n{cache_indicator} {response.content}\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
                
    except LLMSwapError as e:
        print(f"Error: {e}")
        return 1

def cmd_logs(args):
    """Handle 'llmswap logs' command"""
    print("Log analysis feature coming soon!")
    print("Will analyze logs with AI for error patterns and insights.")
    return 0

def cmd_review(args):
    """Handle 'llmswap review' command"""
    if not args.file:
        print("Error: File path is required")
        return 1
        
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        return 1
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1
    
    # Simple language detection
    language = args.language
    if not language:
        ext_map = {
            '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript', '.java': 'java',
            '.cpp': 'cpp', '.c': 'c', '.go': 'go', '.rs': 'rust'
        }
        for ext, lang in ext_map.items():
            if args.file.endswith(ext):
                language = lang
                break
        if not language:
            language = "code"
    
    focus_prompts = {
        "bugs": "Focus on finding potential bugs, edge cases, and runtime errors",
        "style": "Focus on code style, readability, and best practices", 
        "security": "Focus on security vulnerabilities and potential exploits",
        "performance": "Focus on performance optimizations and efficiency",
        "general": "Provide a comprehensive code review covering all aspects"
    }
    
    review_focus = focus_prompts.get(args.focus, focus_prompts["general"])
    
    prompt = f"""
Please review this {language} code and provide constructive feedback.

{review_focus}

Code to review:
```{language}
{code_content}
```

Please provide:
1. Overall assessment
2. Specific issues found
3. Suggestions for improvement
4. Any security concerns
5. Best practice recommendations

Keep feedback constructive and actionable.
"""
    
    try:
        client = LLMClient(
            provider=args.provider or "auto",
            cache_enabled=not args.no_cache
        )
        response = client.query(prompt)
        
        cache_indicator = "[cached]" if response.from_cache else "[fresh]"
        
        print(f"{cache_indicator} Code Review ({args.focus} focus):")
        print("=" * 60)
        print(response.content)
        
        if response.from_cache and not args.quiet:
            print("\nTip: This review was cached (free!)")
            
    except LLMSwapError as e:
        print(f"Error: {e}")
        return 1

def cmd_debug(args):
    """Handle 'llmswap debug' command"""
    if not args.error:
        print("Error: Error message is required")
        return 1
    
    prompt = f"""
I'm getting an error in my code. Please help me debug this issue.

Error message:
{args.error}

Please provide:
1. Explanation of what the error means
2. Most likely causes of this error
3. Step-by-step debugging approach
4. Specific code fixes or suggestions
5. How to prevent this error in the future

Be practical and specific in your recommendations.
"""
    
    try:
        client = LLMClient(
            provider=args.provider or "auto",
            cache_enabled=not args.no_cache
        )
        response = client.query(prompt)
        
        cache_indicator = "[cached]" if response.from_cache else "[fresh]"
        
        print(f"{cache_indicator} Debug Analysis:")
        print("=" * 60)
        print(response.content)
        
        if response.from_cache and not args.quiet:
            print("\nTip: This analysis was cached (free!)")
            
    except LLMSwapError as e:
        print(f"Error: {e}")
        return 1

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='llmswap',
        description='Universal LLM CLI for developers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  llmswap ask "What is Python?"
  llmswap chat
  llmswap review app.py --focus security
  llmswap debug --error "IndexError: list index out of range"
  llmswap logs --analyze /var/log/app.log --since "2h ago"
        """
    )
    
    # Global options
    parser.add_argument('--provider', '-p',
                       choices=['anthropic', 'openai', 'gemini', 'ollama'],
                       help='LLM provider to use')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable response caching')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress tips and extra output')
    parser.add_argument('--version', action='version',
                       version=f'llmswap {__import__("llmswap").__version__}')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a quick question')
    ask_parser.add_argument('question', help='Question to ask')
    
    # chat command  
    chat_parser = subparsers.add_parser('chat', help='Start interactive chat')
    
    # review command
    review_parser = subparsers.add_parser('review', help='Review code with AI')
    review_parser.add_argument('file', help='File to review')
    review_parser.add_argument('--focus', '-f',
                              choices=['bugs', 'style', 'security', 'performance', 'general'],
                              default='general', help='Review focus area')
    review_parser.add_argument('--language', '-l', help='Programming language')
    
    # debug command
    debug_parser = subparsers.add_parser('debug', help='Debug errors with AI')
    debug_parser.add_argument('--error', '-e', required=True,
                             help='Error message to analyze')
    
    # logs command (placeholder)
    logs_parser = subparsers.add_parser('logs', help='Analyze log files')
    logs_parser.add_argument('--analyze', help='Log file to analyze')
    logs_parser.add_argument('--since', help='Time range like "2h ago"')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handlers
    commands = {
        'ask': cmd_ask,
        'chat': cmd_chat,
        'review': cmd_review,
        'debug': cmd_debug,
        'logs': cmd_logs,
    }
    
    return commands[args.command](args)

if __name__ == '__main__':
    sys.exit(main())