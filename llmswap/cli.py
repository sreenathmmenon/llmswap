#!/usr/bin/env python3
"""
llmswap CLI - Command-line interface for llmswap

Usage:
    llmswap ask "What is Python?"
    llmswap chat
    llmswap generate "sort files by size in reverse order"
    llmswap generate "Python function to read JSON file" --language python
    llmswap logs --analyze /var/log/app.log --since "2h ago"
    llmswap review myfile.py --focus security  
    llmswap debug --error "IndexError: list index out of range"
    llmswap compare --input-tokens 500 --output-tokens 300
    llmswap usage --days 7
    llmswap costs
"""

import sys
import argparse
import subprocess
import json
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

def cmd_compare(args):
    """Handle 'llmswap compare' command - Provider cost comparison"""
    try:
        from .metrics import CostEstimator
        estimator = CostEstimator()
        
        comparison = estimator.compare_provider_costs(
            input_tokens=args.input_tokens,
            output_tokens=args.output_tokens
        )
        
        if args.format == 'json':
            print(json.dumps(comparison, indent=2))
        elif args.format == 'csv':
            print("provider,model,total_cost,input_cost,output_cost,confidence")
            for provider, data in comparison['comparison'].items():
                print(f"{provider},{data.get('model','')},{data['total_cost']},{data.get('input_cost',0)},{data.get('output_cost',0)},{data.get('confidence','')}")
        else:  # table format (default)
            print(f"💰 Provider Cost Comparison ({args.input_tokens} input + {args.output_tokens} output tokens)")
            print("=" * 80)
            print(f"{'Provider':<12} {'Model':<20} {'Total Cost':<12} {'Savings':<12} {'Confidence'}")
            print("-" * 80)
            
            # Sort by cost for better comparison
            providers = [(k, v) for k, v in comparison['comparison'].items()]
            providers.sort(key=lambda x: x[1]['total_cost'])
            
            max_cost = comparison['most_expensive_cost']
            for provider, data in providers:
                savings = ((max_cost - data['total_cost']) / max_cost * 100) if max_cost > 0 else 0
                savings_str = f"{savings:.1f}%" if savings > 0 else "-"
                cost_str = f"${data['total_cost']:.6f}"
                
                print(f"{provider:<12} {data.get('model','')[:19]:<20} {cost_str:<12} {savings_str:<12} {data.get('confidence','')}")
            
            print("-" * 80)
            print(f"🏆 Cheapest: {comparison['cheapest']} (${comparison['cheapest_cost']:.6f})")
            print(f"💸 Most Expensive: {comparison['most_expensive']} (${comparison['most_expensive_cost']:.6f})")
            print(f"💡 Max Savings: {comparison['max_savings_percentage']:.1f}%")
            
    except ImportError:
        print("Error: Analytics features not available. Please check installation.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

def cmd_usage(args):
    """Handle 'llmswap usage' command - Usage statistics"""
    try:
        client = LLMClient(analytics_enabled=True)
        stats = client.get_usage_stats()
        
        if not stats:
            print("No usage data available. Make some queries with analytics enabled first.")
            return 1
            
        if args.format == 'json':
            print(json.dumps(stats, indent=2))
        elif args.format == 'csv':
            print("date,queries,tokens,cost,provider")
            for day in stats['daily_breakdown']:
                for provider, data in day['provider_breakdown'].items():
                    print(f"{day['date']},{data['queries']},{data['tokens']},{data['cost']},{provider}")
        else:  # table format (default)
            print("📊 Usage Statistics")
            print("=" * 60)
            print(f"Period: {stats['period']['days']} days ({stats['period']['start_date']} to {stats['period']['end_date']})")
            print()
            
            # Totals
            totals = stats['totals']
            print("📈 Summary:")
            print(f"  Total Queries: {totals['queries']}")
            print(f"  Total Tokens:  {totals['tokens']:,}")
            print(f"  Total Cost:    ${totals['cost']:.4f}")
            print(f"  Avg per Query: ${totals['avg_cost_per_query']:.4f}")
            print()
            
            # Provider breakdown
            if stats['provider_breakdown']:
                print("🏢 By Provider:")
                print(f"{'Provider':<12} {'Queries':<8} {'Tokens':<10} {'Cost':<10} {'Avg Response'}")
                print("-" * 55)
                for provider in stats['provider_breakdown']:
                    tokens_str = f"{provider['tokens']:,}" if provider['tokens'] else "0"
                    cost_str = f"${provider['cost']:.4f}"
                    response_str = f"{provider['avg_response_time_ms']:.0f}ms"
                    print(f"{provider['provider']:<12} {provider['queries']:<8} {tokens_str:<10} {cost_str:<10} {response_str}")
                    
    except Exception as e:
        print(f"Error: {e}")
        return 1

def cmd_generate(args):
    """Handle 'llmswap generate' command"""
    if not args.description:
        print("Error: Description is required")
        return 1
    
    # Detect project context
    cwd = Path.cwd()
    project_context = ""
    
    if (cwd / 'package.json').exists():
        project_context = "Node.js project"
    elif (cwd / 'requirements.txt').exists() or (cwd / 'setup.py').exists():
        project_context = "Python project"
    elif (cwd / 'Cargo.toml').exists():
        project_context = "Rust project"
    elif (cwd / 'pom.xml').exists():
        project_context = "Java project"
    
    # Build prompt
    prompt = f"""Generate a {args.language} command/code for: {args.description}
    
    Context: {project_context if project_context else "Generic command line"}
    
    Requirements:
    - Provide ONLY the command/code, no extra explanation
    - Make it safe and practical
    - Consider the project context if relevant
    - If it's a bash command, make sure it's executable
    """
    
    if args.explain:
        prompt += "\n- After the code, add a brief explanation"
    
    try:
        client = LLMClient(
            provider=args.provider or "auto",
            cache_enabled=not args.no_cache
        )
        response = client.query(prompt)
        
        # Extract code from response (remove markdown if present)
        content = response.content.strip()
        
        # Clean up markdown code blocks
        import re
        code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', content, re.DOTALL)
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = content
        
        # Display the generated command/code
        print(generated_code)
        
        # Execute option for bash commands
        if args.execute and args.language == 'bash':
            try:
                confirm = input(f"\nExecute this command? [y/N]: ").lower().strip()
                if confirm == 'y' or confirm == 'yes':
                    import subprocess
                    result = subprocess.run(generated_code, shell=True, capture_output=True, text=True)
                    if result.stdout:
                        print("Output:")
                        print(result.stdout)
                    if result.stderr:
                        print("Errors:")
                        print(result.stderr)
                    print(f"Exit code: {result.returncode}")
            except KeyboardInterrupt:
                print("\nCommand execution cancelled.")
        
        # Save option
        if args.save:
            save_path = Path(args.save)
            save_path.write_text(generated_code)
            print(f"Saved to: {save_path}")
            
            # Make executable if it's a bash script
            if args.language == 'bash' and save_path.suffix == '.sh':
                import stat
                save_path.chmod(save_path.stat().st_mode | stat.S_IEXEC)
                print("Made executable")
        
    except LLMSwapError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

def cmd_costs(args):
    """Handle 'llmswap costs' command - Cost analysis and optimization"""
    try:
        client = LLMClient(analytics_enabled=True)
        analysis = client.get_cost_breakdown()
        
        if not analysis:
            print("No cost data available. Make some queries with analytics enabled first.")
            return 1
            
        if args.format == 'json':
            print(json.dumps(analysis, indent=2))
        else:  # table format (default)
            print("💡 Cost Analysis & Optimization")
            print("=" * 50)
            
            # Current spend
            spend = analysis.get('current_spend', {})
            print(f"📊 Current Spend: ${spend.get('monthly_total', 0):.2f}/month")
            print(f"🏆 Cheapest Provider: {spend.get('cheapest_provider', 'N/A')}")
            print(f"💸 Most Expensive: {spend.get('most_expensive_provider', 'N/A')}")
            print()
            
            # Optimization opportunities
            opt = analysis.get('optimization_opportunities', {})
            print("💰 Optimization Opportunities:")
            print(f"  Provider Savings:    ${opt.get('potential_provider_savings', 0):.2f}")
            print(f"  Cache Savings Est:   ${opt.get('cache_savings_estimate', 0):.2f}")
            print(f"  Cache Hit Rate:      {opt.get('overall_cache_hit_rate', 0)*100:.1f}%")
            print()
            
            # Recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                print("🎯 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
                    
    except Exception as e:
        print(f"Error: {e}")
        return 1

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='llmswap',
        description='Universal LLM CLI for developers with cost analytics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  llmswap ask "What is Python?"
  llmswap chat
  llmswap review app.py --focus security
  llmswap debug --error "IndexError: list index out of range"
  llmswap logs --analyze /var/log/app.log --since "2h ago"
  
  # Cost comparison examples
  llmswap compare --input-tokens 100 --output-tokens 50      # Simple Q&A
  llmswap compare --input-tokens 1000 --output-tokens 300    # Code review
  llmswap compare --input-tokens 3000 --output-tokens 800    # Document analysis
  llmswap compare --input-tokens 500 --output-tokens 2000    # Creative writing
  
  llmswap usage --days 7 --format table
  llmswap costs
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
    
    # Analytics commands - new v4.0.0 features
    
    # compare command - Provider cost comparison
    compare_parser = subparsers.add_parser('compare', help='Compare provider costs')
    compare_parser.add_argument('--input-tokens', type=int, default=500,
                               help='Input tokens: Simple Q&A=100, Code review=1000, Document analysis=3000')
    compare_parser.add_argument('--output-tokens', type=int, default=300, 
                               help='Output tokens: Brief answer=50, Explanation=300, Detailed analysis=800')
    compare_parser.add_argument('--format', choices=['table', 'json', 'csv'],
                               default='table', help='Output format')
    
    # usage command - Usage statistics  
    usage_parser = subparsers.add_parser('usage', help='Show usage statistics')
    usage_parser.add_argument('--format', choices=['table', 'json', 'csv'],
                             default='table', help='Output format')
    usage_parser.add_argument('--days', type=int, default=30,
                             help='Number of days to analyze (default: 30)')
    
    # generate command - Generate commands/code from description
    generate_parser = subparsers.add_parser('generate', help='Generate commands or code from natural language')
    generate_parser.add_argument('description', help='Natural language description of what you want to generate')
    generate_parser.add_argument('--language', '-l', default='bash', 
                                help='Target language/type (bash, python, javascript, etc.)')
    generate_parser.add_argument('--execute', '-x', action='store_true',
                                help='Ask to execute the generated command (bash only)')
    generate_parser.add_argument('--explain', action='store_true',
                                help='Include explanation with the generated code')
    generate_parser.add_argument('--save', '-s',
                                help='Save generated code to file')
    
    # costs command - Cost analysis and optimization
    costs_parser = subparsers.add_parser('costs', help='Analyze costs and get optimization suggestions')  
    costs_parser.add_argument('--format', choices=['table', 'json'],
                             default='table', help='Output format')
    
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
        'compare': cmd_compare,
        'usage': cmd_usage,
        'generate': cmd_generate,
        'costs': cmd_costs,
    }
    
    return commands[args.command](args)

if __name__ == '__main__':
    sys.exit(main())