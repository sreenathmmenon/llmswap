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
        print(response.content)
            
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
                
                # Get response with conversation context
                response = client.chat(user_input)
                print(f"\n{response.content}\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
                
    except LLMSwapError as e:
        print(f"Error: {e}")
        return 1

def apply_log_filters(content, args):
    """Apply various filters to log content"""
    lines = content.split('\n')
    filtered_lines = []
    
    for line in lines:
        # Skip empty lines and file separators
        if not line.strip() or line.startswith('=== '):
            filtered_lines.append(line)
            continue
            
        # Apply ID-based filters
        if args.request_id and args.request_id.lower() not in line.lower():
            continue
        if args.user_id and args.user_id.lower() not in line.lower():
            continue
        if args.session_id and args.session_id.lower() not in line.lower():
            continue
        if args.trace_id and args.trace_id.lower() not in line.lower():
            continue
        if args.transaction_id and args.transaction_id.lower() not in line.lower():
            continue
            
        # Apply IP filter
        if args.ip and args.ip not in line:
            continue
            
        # Apply component filter
        if args.component and args.component.lower() not in line.lower():
            continue
            
        # Apply log level filter
        if args.level:
            level_patterns = {
                'error': ['error', 'err', 'fatal', 'critical'],
                'warn': ['warn', 'warning'],
                'info': ['info', 'information'],
                'debug': ['debug', 'trace']
            }
            level_found = False
            if args.level.lower() in level_patterns:
                for pattern in level_patterns[args.level.lower()]:
                    if pattern.upper() in line.upper():
                        level_found = True
                        break
            if not level_found:
                continue
                
        # Apply term filters
        if args.terms:
            terms = [t.strip().lower() for t in args.terms.split(',')]
            if not any(term in line.lower() for term in terms):
                continue
                
        # Apply exclude terms
        if args.exclude_terms:
            exclude_terms = [t.strip().lower() for t in args.exclude_terms.split(',')]
            if any(term in line.lower() for term in exclude_terms):
                continue
        
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

def create_analysis_prompt(content, args, log_files):
    """Create analysis prompt based on filters and format"""
    
    # Build filter description
    filters_applied = []
    if args.request_id:
        filters_applied.append(f"Request ID: {args.request_id}")
    if args.user_id:
        filters_applied.append(f"User ID: {args.user_id}")
    if args.session_id:
        filters_applied.append(f"Session ID: {args.session_id}")
    if args.trace_id:
        filters_applied.append(f"Trace ID: {args.trace_id}")
    if args.transaction_id:
        filters_applied.append(f"Transaction ID: {args.transaction_id}")
    if args.terms:
        filters_applied.append(f"Terms: {args.terms}")
    if args.level:
        filters_applied.append(f"Level: {args.level}")
    if args.ip:
        filters_applied.append(f"IP: {args.ip}")
    if args.component:
        filters_applied.append(f"Component: {args.component}")
    
    filter_context = ""
    if filters_applied:
        filter_context = f"\nFilters applied: {', '.join(filters_applied)}"
    
    # Determine analysis focus based on format
    if args.format == 'timeline':
        analysis_focus = """
Focus on chronological sequence of events:
1. **Timeline**: Chronological order of events
2. **Event Sequence**: How events relate to each other over time
3. **Patterns**: Recurring time-based patterns
4. **Root Cause**: Trace issues back to initial causes
5. **Impact Timeline**: How issues evolved and spread
"""
    elif args.format == 'detailed':
        analysis_focus = """
Provide comprehensive detailed analysis:
1. **Complete Error Analysis**: Every error with context and impact
2. **Performance Metrics**: Detailed performance analysis
3. **Security Deep Dive**: Thorough security assessment
4. **System Behavior**: Detailed system interaction patterns
5. **Remediation Steps**: Step-by-step fix recommendations
6. **Prevention Strategies**: How to prevent similar issues
"""
    else:  # summary format
        analysis_focus = """
Provide concise executive summary:
1. **Key Issues**: Most critical problems requiring attention
2. **Impact Assessment**: Business/operational impact
3. **Priority Actions**: Top 3-5 actions needed immediately
4. **Quick Wins**: Easy fixes that can be implemented quickly
5. **Monitoring**: What to watch for next
"""
    
    # Add correlation context if enabled
    correlation_context = ""
    if args.correlate and len(log_files) > 1:
        correlation_context = """
CORRELATION ANALYSIS REQUESTED:
- Identify related events across different log files
- Track request flows between services
- Find patterns that span multiple systems
- Highlight timing relationships between different components
"""
    
    prompt = f"""
Analyze these log files with advanced filtering for debugging and troubleshooting.

Log files analyzed: {', '.join(log_files)}{filter_context}
{correlation_context}

Log content:
```
{content}
```

{analysis_focus}

Additional considerations:
- Focus on actionable insights for developers and operators
- Highlight patterns that indicate systemic issues
- Provide specific recommendations with context
- Group related issues together for clarity
- Include confidence levels for conclusions when uncertain

Output format: {args.format.capitalize()} analysis
"""
    
    return prompt

def print_analysis_header(args, log_files):
    """Print analysis header with context"""
    print(f"Advanced Log Analysis - {args.format.capitalize()} Format")
    print("=" * 70)
    print(f"Files: {', '.join(log_files)}")
    
    filters = []
    if args.request_id:
        filters.append(f"Request ID: {args.request_id}")
    if args.user_id:
        filters.append(f"User ID: {args.user_id}")
    if args.terms:
        filters.append(f"Terms: {args.terms}")
    if args.level:
        filters.append(f"Level: {args.level}")
    if args.ip:
        filters.append(f"IP: {args.ip}")
    
    if filters:
        print(f"Filters: {' | '.join(filters)}")
    
    if args.correlate:
        print("Mode: Cross-log correlation enabled")
    
    print("=" * 70)

def print_analysis_footer(args):
    """Print analysis footer"""
    print("\n" + "=" * 70)
    print("Analysis complete.")
    
    if args.format == 'summary':
        print("Use --format detailed for comprehensive analysis")
    if not args.correlate and ',' in args.analyze:
        print("Use --correlate for cross-log correlation analysis")

def cmd_logs(args):
    """Handle 'llmswap logs' command with advanced filtering"""
    if not args.analyze:
        print("Error: Log file path is required. Use --analyze /path/to/logfile")
        print("\nExamples:")
        print("  llmswap logs --analyze app.log --terms 'error,timeout'")
        print("  llmswap logs --analyze app.log --user-id user123 --since '2h ago'")
        print("  llmswap logs --analyze 'app.log,api.log' --request-id req-456 --correlate")
        return 1
    
    # Parse multiple log files
    log_files = [f.strip() for f in args.analyze.split(',')]
    all_content = ""
    
    # Read and combine log files
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(args.max_lines * 200)  # Estimate ~200 chars per log line
                all_content += f"\n=== {log_file} ===\n{content}\n"
        except FileNotFoundError:
            print(f"Warning: Log file '{log_file}' not found - skipping")
            continue
        except PermissionError:
            print(f"Warning: Permission denied reading '{log_file}' - skipping")
            continue
        except Exception as e:
            print(f"Warning: Error reading '{log_file}': {e} - skipping")
            continue
    
    if not all_content:
        print("Error: No readable log files found")
        return 1
    
    # Apply filtering
    filtered_content = apply_log_filters(all_content, args)
    
    if not filtered_content.strip():
        print("No log entries match the specified filters")
        return 0
    
    # Prepare analysis prompt based on filters and format
    prompt = create_analysis_prompt(filtered_content, args, log_files)
    
    try:
        client = LLMClient(
            provider=args.provider or "auto",
            cache_enabled=not args.no_cache
        )
        
        print_analysis_header(args, log_files)
        
        response = client.query(prompt)
        print(response.content)
        
        print_analysis_footer(args)
            
    except LLMSwapError as e:
        print(f"Error: {e}")
        return 1

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
        
        print(f"Code Review ({args.focus} focus):")
        print("=" * 60)
        print(response.content)
            
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
        
        print(f"Debug Analysis:")
        print("=" * 60)
        print(response.content)
            
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
    
    # logs command - Advanced log analysis
    logs_parser = subparsers.add_parser('logs', help='Advanced AI-powered log analysis')
    logs_parser.add_argument('--analyze', help='Log file(s) to analyze (comma-separated for multiple)')
    
    # Time-based filtering
    logs_parser.add_argument('--since', help='Time range: "2h ago", "10m ago", "1d ago"')
    logs_parser.add_argument('--between', help='Time range: "10:00-14:00" or "2025-01-17 10:00 to 2025-01-17 14:00"')
    logs_parser.add_argument('--timerange', help='Specific time range: "9AM-11AM", "last 4 hours"')
    
    # ID-based tracking
    logs_parser.add_argument('--request-id', help='Track specific request ID')
    logs_parser.add_argument('--user-id', help='Track specific user ID')
    logs_parser.add_argument('--session-id', help='Track specific session ID')
    logs_parser.add_argument('--trace-id', help='Track specific trace/correlation ID')
    logs_parser.add_argument('--transaction-id', help='Track specific transaction ID')
    
    # Term-based filtering
    logs_parser.add_argument('--terms', help='Search terms (comma-separated): "error,timeout,failed"')
    logs_parser.add_argument('--exclude-terms', help='Exclude terms (comma-separated)')
    logs_parser.add_argument('--level', help='Log level filter: "error", "warn", "info", "debug"')
    
    # Advanced filtering
    logs_parser.add_argument('--ip', help='Filter by IP address')
    logs_parser.add_argument('--component', help='Filter by component/service name')
    logs_parser.add_argument('--correlate', action='store_true', help='Enable cross-log correlation analysis')
    
    # Output options
    logs_parser.add_argument('--format', choices=['summary', 'detailed', 'timeline'], 
                           default='summary', help='Analysis output format')
    logs_parser.add_argument('--max-lines', type=int, default=10000, 
                           help='Maximum log lines to analyze (default: 10000)')
    
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