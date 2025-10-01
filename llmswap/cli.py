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
import yaml
from pathlib import Path
from .client import LLMClient
from .exceptions import LLMSwapError
from .config import LLMSwapConfig, get_config

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
        
        # Check if age/audience targeting is requested
        has_age_targeting = args.age or args.audience or args.level or args.explain_to
        
        # Check if teaching mode is enabled
        teaching_mode = args.teach or args.explain
        
        if has_age_targeting or teaching_mode:
            try:
                # Import age adapter
                from .eklavya.age_adapter import AgeAdapter
                
                # Build appropriate prompt
                if has_age_targeting:
                    # Age-appropriate explanation
                    context_info = AgeAdapter.get_context_info(
                        age=args.age,
                        audience=args.audience, 
                        level=args.level,
                        explain_to=args.explain_to
                    )
                    print(f"🎯 Targeting: {context_info}")
                    
                    enhanced_question = AgeAdapter.build_targeted_prompt(
                        args.question,
                        age=args.age,
                        audience=args.audience,
                        level=args.level,
                        explain_to=args.explain_to
                    )
                    
                elif teaching_mode:
                    # Teaching mode with persona
                    from .eklavya.practical_personas import get_practical_persona_prompt
                    
                    persona = args.mentor or 'teacher'
                    alias = args.alias or persona.title()
                    
                    print(f"📚 Teaching Mode | {alias} ({persona})")
                    
                    persona_prompt = get_practical_persona_prompt(persona, alias)
                    enhanced_question = f"""
{persona_prompt}

Student's Question: {args.question}

Provide a detailed, educational response that helps the student understand both the answer and the underlying concepts. Include examples and practical applications where helpful.
"""
                
                response = client.query(enhanced_question)
                
            except ImportError:
                print("⚠️ Enhanced explanation mode not available - using standard mode")
                response = client.query(args.question)
        else:
            # Auto-detect if question seems like it wants explanation
            learning_keywords = ['how does', 'why', 'explain', 'understand', 'difference between', 'what is the']
            if any(keyword in args.question.lower() for keyword in learning_keywords):
                print("💡 Detected learning question. Try --teach or --age for tailored explanation")
            
            response = client.query(args.question)
        
        print(response.content)
        
        # Suggest teaching mode for quick answers that could benefit from explanation
        if not teaching_mode and len(response.content) < 200:
            print("\n💡 Want more detail? Try adding --teach")
            
    except LLMSwapError as e:
        print(f"Error: {e}")
        return 1

def _build_context_instruction(chat_context):
    """Build system instruction for age/audience context without breaking conversation flow"""
    if chat_context.age:
        return f"Respond as if explaining to a {chat_context.age}-year-old. Use appropriate vocabulary and examples for that age group."
    elif chat_context.audience or chat_context.explain_to:
        target = chat_context.audience or chat_context.explain_to
        return f"Respond as if explaining to {target}. Consider their background and interests."
    elif chat_context.level:
        level_instructions = {
            'beginner': "Assume no prior knowledge. Start with basics and define technical terms.",
            'intermediate': "Assume some background knowledge. Focus on practical applications.", 
            'advanced': "Assume strong foundation. Focus on depth, nuances, and complex aspects."
        }
        return level_instructions.get(chat_context.level, level_instructions['intermediate'])
    return ""

def cmd_chat(args):
    """Handle 'llmswap chat' command - Enhanced conversational interface"""
    try:
        client = LLMClient(
            provider=args.provider or "auto",
            cache_enabled=not args.no_cache,
            analytics_enabled=True
        )
        
        # Start provider-native chat session
        client.start_chat_session()
        
        # Set up age/audience context if provided
        chat_context = None
        if args.age or args.audience or args.level:
            try:
                from .eklavya.age_adapter import ChatContextManager
                chat_context = ChatContextManager()
                
                if args.age:
                    chat_context.set_age(args.age)
                elif args.audience:
                    chat_context.set_audience(args.audience)
                elif args.level:
                    chat_context.set_level(args.level)
                
                # Store context manager in client for access during chat
                client._chat_context = chat_context
            except ImportError:
                pass
        
        # Display welcome message
        current_provider = client.get_current_provider()
        print(f"🤖 llmswap Interactive Chat v5.1.0")
        print(f"📡 Provider: {current_provider}")
        print(f"💬 Conversational mode: ON (context maintained)")
        
        if chat_context and chat_context.has_context():
            print(f"🎯 Context: {chat_context.get_context_display()}")
        
        print("\nCommands: /help, /provider, /switch, /clear, /stats, /quit")
        if chat_context:
            print("          /age <number>, /audience <type>, /level <level>, /reset-context")
        
        try:
            from llmswap.workspace.detector import WorkspaceDetector
            from llmswap.workspace.manager import WorkspaceManager
            from llmswap.workspace.registry import WorkspaceRegistry
            from pathlib import Path
            
            workspace_dir = WorkspaceDetector.detect()
            
            if workspace_dir:
                workspace_id = workspace_dir.name
                registry = WorkspaceRegistry()
                all_workspaces = registry.list_workspaces()
                
                for ws in all_workspaces:
                    if ws["workspace_id"] == workspace_id:
                        project_path = Path(ws["project_path"])
                        manager = WorkspaceManager(project_path)
                        data = manager.load_workspace()
                        
                        print(f"\n📁 Workspace: {data['project_name']}")
                        print(f"📊 Learnings: {data['statistics']['learnings_count']} tracked")
                        break
            else:
                print("\n💡 Tip: Run 'llmswap workspace init' to enable project memory")
        except Exception:
            pass
        
        print("─" * 50)
        
        message_count = 0
        conversation_history = []  # In-memory conversation history for this session
        
        while True:
            try:
                user_input = input(f"\n[{message_count}] > ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    command = user_input[1:].lower()
                    
                    if command in ['quit', 'exit', 'q']:
                        # End provider-native chat session
                        client.end_chat_session()
                        stats = client.get_usage_stats()
                        if stats:
                            total_cost = stats.get('totals', {}).get('cost', 0)
                            print(f"\n💰 Session cost: ~${total_cost:.4f} (estimated)")
                        print("👋 Chat session ended.")
                        break
                        
                    elif command == 'help':
                        print("\n🔧 Chat Commands:")
                        print("  /help     - Show this help")
                        print("  /provider - Show current provider") 
                        print("  /switch   - Switch to different provider")
                        print("  /clear    - Clear conversation history")
                        print("  /stats    - Show session statistics")
                        print("  /quit     - Exit chat")
                        print("\n🎯 Age/Audience Commands:")
                        print("  /age <number>      - Set age context (e.g., /age 12)")
                        print("  /audience <type>   - Set audience (e.g., /audience student)")
                        print("  /level <level>     - Set level (beginner/intermediate/advanced)")
                        print("  /reset-context     - Clear age/audience context")
                        print("\n💡 Tips:")
                        print("  • Conversation context is maintained automatically")
                        print("  • Switch providers mid-conversation to compare responses")
                        print("  • Provider switching starts fresh conversations (privacy protection)")
                        print("  • Use age/audience commands for tailored explanations")
                        continue
                        
                    elif command == 'provider':
                        current = client.get_current_provider()
                        available = client.get_available_providers()
                        print(f"\n📡 Current: {current}")
                        print(f"📋 Available: {', '.join(available)}")
                        continue
                        
                    elif command == 'switch':
                        available = client.get_available_providers()
                        print(f"\n📋 Available providers: {', '.join(available)}")
                        new_provider = input("Enter provider name: ").strip()
                        if new_provider in available:
                            try:
                                # LEGAL COMPLIANCE: No context transfer between providers
                                print(f"\n🔒 PRIVACY NOTICE: Switching to {new_provider}")
                                print("   ✅ NO conversation history will be shared with the new provider")
                                print("   ✅ This protects your privacy and complies with provider Terms of Service")
                                print("   ⚠️  You'll start a completely fresh conversation")
                                confirm = input("Continue? (y/n): ").strip().lower()
                                if confirm in ['y', 'yes']:
                                    # Use safe provider switching method
                                    result = client.switch_provider_safe(new_provider)
                                    if result['success']:
                                        # Show previous session stats if available
                                        if result.get('previous_session'):
                                            prev = result['previous_session']
                                            if prev['session_cost'] > 0 or prev['session_tokens'] > 0:
                                                print(f"\n📊 Previous session ({prev['provider']}):")
                                                print(f"   Model: {prev['model']}")
                                                print(f"   Tokens: {prev['session_tokens']}")
                                                print(f"   Cost: ~${prev['session_cost']:.4f} (est.)")
                                        
                                        # Show new provider info
                                        print(f"\n✅ Switched to {result['new_provider']}")
                                        print(f"   Model: {result['new_model']}")
                                        if result.get('new_pricing'):
                                            pricing = result['new_pricing']
                                            print(f"   Pricing: ${pricing.get('input', 0):.6f}/1K input, ${pricing.get('output', 0):.6f}/1K output")
                                        print(f"💬 Starting fresh conversation with {new_provider}")
                                        conversation_history.clear()  # Clear conversation history for new provider
                                        message_count = 0  # Reset message counter
                                    else:
                                        print(f"❌ Failed to switch: {result.get('error', 'Unknown error')}")
                                else:
                                    print("❌ Switch cancelled")
                            except Exception as e:
                                print(f"❌ Failed to switch: {e}")
                        else:
                            print(f"❌ Invalid provider. Choose from: {', '.join(available)}")
                        continue
                        
                    elif command == 'clear':
                        # End current session and start new one (provider-native reset)
                        client.end_chat_session()
                        client.start_chat_session()
                        conversation_history.clear()  # Clear our conversation history
                        message_count = 0
                        print("🧹 Chat session reset (starting fresh conversation)")
                        continue
                        
                    elif command == 'stats':
                        session_info = client.get_chat_session_info()
                        print(f"\n📊 Current Session Statistics:")
                        print(f"  Provider: {session_info['provider']}")
                        print(f"  Model: {client.get_current_model()}")
                        print(f"  Messages: {message_count} exchanges")
                        print(f"  Session Tokens: {session_info['session_tokens']}")
                        print(f"  Session Cost: ~${session_info['session_cost']:.6f} (estimated)")
                        
                        # Show duration
                        duration = session_info['duration_seconds']
                        if duration > 0:
                            mins = duration // 60
                            secs = duration % 60
                            print(f"  Duration: {mins}m {secs}s")
                        
                        # Show pricing for current provider
                        # TODO: Re-enable pricing info when analytics module is ready
                        # if client._analytics_enabled and client._cost_estimator:
                        #     from llmswap.analytics.price_manager import PROVIDER_PRICING
                        #     provider_key = session_info['provider'].lower()
                        #     model = client.get_current_model()
                        #     if provider_key in PROVIDER_PRICING and model in PROVIDER_PRICING[provider_key]:
                        #         pricing = PROVIDER_PRICING[provider_key][model]
                        #         print(f"\n💰 Current Pricing:")
                        #         print(f"  Input: ${pricing.get('input', 0):.6f}/1K tokens")
                        #         print(f"  Output: ${pricing.get('output', 0):.6f}/1K tokens")
                        continue
                        
                    # Age/Audience context commands
                    elif command.startswith('age '):
                        try:
                            age = int(command.split()[1])
                            if not hasattr(client, '_chat_context'):
                                from .eklavya.age_adapter import ChatContextManager
                                client._chat_context = ChatContextManager()
                            
                            client._chat_context.set_age(age)
                            print(f"🎯 Age context set to: {age} years old")
                        except (ValueError, IndexError):
                            print("❌ Usage: /age <number> (e.g., /age 12)")
                        continue
                        
                    elif command.startswith('audience '):
                        try:
                            audience = ' '.join(command.split()[1:])
                            if not hasattr(client, '_chat_context'):
                                from .eklavya.age_adapter import ChatContextManager
                                client._chat_context = ChatContextManager()
                            
                            client._chat_context.set_audience(audience)
                            print(f"🎯 Audience context set to: {audience}")
                        except IndexError:
                            print("❌ Usage: /audience <type> (e.g., /audience student)")
                        continue
                        
                    elif command.startswith('level '):
                        try:
                            level = command.split()[1]
                            if level not in ['beginner', 'intermediate', 'advanced']:
                                print("❌ Level must be: beginner, intermediate, or advanced")
                                continue
                                
                            if not hasattr(client, '_chat_context'):
                                from .eklavya.age_adapter import ChatContextManager
                                client._chat_context = ChatContextManager()
                            
                            client._chat_context.set_level(level)
                            print(f"🎯 Knowledge level set to: {level}")
                        except IndexError:
                            print("❌ Usage: /level <level> (beginner/intermediate/advanced)")
                        continue
                        
                    elif command == 'reset-context':
                        if hasattr(client, '_chat_context'):
                            client._chat_context.clear_all()
                            print("🧹 Age/audience context cleared")
                        else:
                            print("ℹ️ No context was set")
                        continue
                        
                    else:
                        print(f"❌ Unknown command: /{command}")
                        print("Type /help for available commands")
                        continue
                
                # Handle age/audience context ONLY when explicitly enabled
                if hasattr(client, '_chat_context') and client._chat_context.has_context():
                    # Apply age/audience enhancement to this specific message
                    enhanced_input = client._chat_context.enhance_question(user_input)
                    conversation_history.append({"role": "user", "content": enhanced_input})
                else:
                    # Default: Pure conversation like Claude CLI
                    conversation_history.append({"role": "user", "content": user_input})
                
                # Send conversation history to maintain context 
                # Always bypass cache for conversations (each conversation is unique)
                response = client.chat(conversation_history, cache_bypass=True)
                message_count += 1
                
                # Add assistant response to conversation history
                conversation_history.append({"role": "assistant", "content": response.content})
                
                # Display response with provider info
                provider_info = f"[{client.get_current_provider()}]"
                print(f"\n{provider_info} {response.content}")
                
                # Show token usage if available
                if hasattr(response, 'usage') and response.usage:
                    tokens = response.usage.get('total_tokens', 0)
                    if tokens > 0:
                        print(f"📊 {tokens} tokens")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Use /quit to exit properly.")
                continue
                
    except LLMSwapError as e:
        if not args.quiet:
            print(f"❌ Error: {e}")
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
            print(f"💰 Provider Cost Comparison ({args.input_tokens} input + {args.output_tokens} output tokens)\n⚠️  Estimates only - actual billing may vary")
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
            print(f"🏆 Cheapest: {comparison['cheapest']} (~${comparison['cheapest_cost']:.6f})")
            print(f"💸 Most Expensive: {comparison['most_expensive']} (~${comparison['most_expensive_cost']:.6f})")
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
            print(f"  Total Cost:    ~${totals['cost']:.4f} (estimated)")
            print(f"  Avg per Query: ~${totals['avg_cost_per_query']:.4f} (estimated)")
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

def cmd_providers(args):
    """Handle 'llmswap providers' command"""
    import os
    
    try:
        # Initialize client to get provider order
        config = get_config()
        provider_order = config.get('provider.fallback_order', [])
        provider_models = config.get('provider.models', {})
        
        # Check each provider status
        providers_data = []
        available_count = 0
        
        for provider in provider_order:
            # Check if provider has required credentials
            status = "❌ NOT CONFIGURED"
            status_detail = ""
            
            if provider == "anthropic":
                if os.getenv("ANTHROPIC_API_KEY"):
                    status = "✅ CONFIGURED"
                    available_count += 1
                else:
                    status_detail = "ANTHROPIC_API_KEY missing"
                    
            elif provider == "openai":
                if os.getenv("OPENAI_API_KEY"):
                    status = "✅ CONFIGURED"
                    available_count += 1
                else:
                    status_detail = "OPENAI_API_KEY missing"
                    
            elif provider == "gemini":
                if os.getenv("GEMINI_API_KEY"):
                    status = "✅ CONFIGURED"
                    available_count += 1
                else:
                    status_detail = "GEMINI_API_KEY missing"
                    
            elif provider == "cohere":
                if os.getenv("COHERE_API_KEY"):
                    status = "✅ CONFIGURED"
                    available_count += 1
                else:
                    status_detail = "COHERE_API_KEY missing"
                    
            elif provider == "perplexity":
                if os.getenv("PERPLEXITY_API_KEY"):
                    status = "✅ CONFIGURED"
                    available_count += 1
                else:
                    status_detail = "PERPLEXITY_API_KEY missing"
                    
            elif provider == "watsonx":
                if os.getenv("WATSONX_API_KEY") and os.getenv("WATSONX_PROJECT_ID"):
                    status = "✅ CONFIGURED"
                    available_count += 1
                else:
                    missing = []
                    if not os.getenv("WATSONX_API_KEY"):
                        missing.append("WATSONX_API_KEY")
                    if not os.getenv("WATSONX_PROJECT_ID"):
                        missing.append("WATSONX_PROJECT_ID")
                    status_detail = f"{', '.join(missing)} missing"
                    
            elif provider == "groq":
                if os.getenv("GROQ_API_KEY"):
                    status = "✅ CONFIGURED"
                    available_count += 1
                else:
                    status_detail = "GROQ_API_KEY missing"
                    
            elif provider == "ollama":
                # Check if Ollama is running
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=2)
                    if response.status_code == 200:
                        status = "✅ AVAILABLE"
                        available_count += 1
                    else:
                        status = "⚠️ NOT RUNNING"
                        status_detail = "Local server not responding"
                except:
                    status = "⚠️ NOT RUNNING"
                    status_detail = "Local server not running"
            
            # Get default model
            default_model = provider_models.get(provider, "NOT CONFIGURED")
            
            providers_data.append([
                provider.upper(),
                default_model,
                status,
                status_detail
            ])
        
        if args.format == 'json':
            import json
            result = {
                "providers": providers_data,
                "summary": {
                    "total": len(provider_order),
                    "available": available_count,
                    "configured": available_count
                }
            }
            print(json.dumps(result, indent=2))
        else:
            try:
                from tabulate import tabulate
                print(f"🤖 llmswap Provider Status Report")
                print(f"{'='*60}")
                
                headers = ["Provider", "Default Model", "Status", "Issue"]
                table = tabulate(providers_data, headers=headers, tablefmt="grid")
                print(table)
            except ImportError:
                # Fallback to simple formatting if tabulate not available
                print(f"🤖 llmswap Provider Status Report")
                print(f"{'='*60}")
                print(f"{'Provider':<12} {'Default Model':<25} {'Status':<15} {'Issue'}")
                print("-" * 60)
                for row in providers_data:
                    print(f"{row[0]:<12} {row[1]:<25} {row[2]:<15} {row[3]}")
            
            print(f"\n📊 Summary: {available_count}/{len(provider_order)} providers available")
            print(f"💡 Use: llmswap config set provider.models.<provider> <model> to change defaults")
            print(f"💡 Use: export <PROVIDER>_API_KEY=<key> to configure providers")
            
        return 0
        
    except Exception as e:
        print(f"❌ Error checking providers: {e}")
        return 1

def cmd_config(args):
    """Handle 'llmswap config' command - Configuration management"""
    try:
        config = get_config()
        
        if args.config_action == 'set':
            if not args.key or args.value is None:
                print("Error: Both key and value required for 'set'")
                return 1
            
            # Handle different value types
            value = args.value
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
            
            config.set(args.key, value)
            print(f"✅ Set {args.key} = {value}")
            
        elif args.config_action == 'get':
            if args.key:
                value = config.get(args.key)
                if value is not None:
                    print(value)
                else:
                    print(f"Key '{args.key}' not found")
                    return 1
            else:
                print("Error: Key required for 'get'")
                return 1
                
        elif args.config_action == 'unset':
            if not args.key:
                print("Error: Key required for 'unset'")
                return 1
            config.unset(args.key)
            print(f"✅ Unset {args.key}")
            
        elif args.config_action == 'show' or args.config_action == 'list':
            if args.key:
                # Show specific section
                section = config.get_section(args.key)
                if section:
                    print(yaml.dump({args.key: section}, default_flow_style=False))
                else:
                    print(f"Section '{args.key}' not found")
                    return 1
            else:
                # Show all config
                all_config = config.list_all()
                print(yaml.dump(all_config, default_flow_style=False))
                
        elif args.config_action == 'reset':
            if args.key:
                config.reset(args.key)
                print(f"✅ Reset section '{args.key}' to defaults")
            else:
                if not args.confirm:
                    confirm = input("Reset all configuration to defaults? (y/N): ")
                    if confirm.lower() not in ['y', 'yes']:
                        print("Reset cancelled")
                        return 0
                config.reset()
                print("✅ Reset all configuration to defaults")
                
        elif args.config_action == 'export':
            file_path = args.file or 'llmswap-config.yaml'
            config.export_config(file_path)
            print(f"✅ Exported configuration to {file_path}")
            
        elif args.config_action == 'import':
            if not args.file:
                print("Error: File path required for 'import'")
                return 1
            config.import_config(args.file, merge=args.merge)
            action = "Merged" if args.merge else "Imported"
            print(f"✅ {action} configuration from {args.file}")
            
        elif args.config_action == 'validate':
            issues = config.validate()
            if issues:
                print("❌ Configuration issues found:")
                for issue in issues:
                    print(f"  • {issue}")
                return 1
            else:
                print("✅ Configuration is valid")
                
        elif args.config_action == 'doctor':
            diagnosis = config.doctor()
            print("🔍 Configuration Health Check")
            print("=" * 40)
            print(f"Config file: {diagnosis['config_path']}")
            print(f"Config exists: {'✅' if diagnosis['config_exists'] else '❌'}")
            print()
            
            if diagnosis['issues']:
                print("❌ Issues found:")
                for issue in diagnosis['issues']:
                    print(f"  • {issue}")
                print()
            
            if diagnosis['suggestions']:
                print("💡 Suggestions:")
                for suggestion in diagnosis['suggestions']:
                    print(f"  • {suggestion}")
            else:
                print("✅ No issues found")
                
    except Exception as e:
        print(f"Config error: {e}")
        return 1

def cmd_workspace(args):
    from llmswap.workspace.manager import WorkspaceManager
    from llmswap.workspace.detector import WorkspaceDetector
    from llmswap.workspace.registry import WorkspaceRegistry
    from tabulate import tabulate
    
    if args.workspace_action == 'init':
        project_path = Path.cwd()
        manager = WorkspaceManager(project_path)
        
        try:
            workspace_data = manager.init_workspace(project_name=args.name)
            
            print(f"✅ Workspace initialized: {workspace_data['project_name']}")
            print(f"📁 Workspace ID: {workspace_data['workspace_id']}")
            print(f"💾 Location: ~/.llmswap/workspaces/{workspace_data['workspace_id']}/")
            print(f"\nCreated files:")
            print(f"  - workspace.json (metadata)")
            print(f"  - context.md (project description)")
            print(f"  - learnings.md (learning journal)")
            print(f"  - decisions.md (architecture decisions)")
            print(f"\n💡 Tip: Your project directory stays clean!")
            print(f"   All workspace data is in ~/.llmswap/workspaces/")
            
        except FileExistsError:
            print("❌ Workspace already exists for this project")
            print(f"   Workspace ID: {manager.workspace_id}")
            return 1
    
    elif args.workspace_action == 'info':
        workspace_dir = WorkspaceDetector.detect()
        
        if not workspace_dir:
            print("❌ No workspace found in current directory or parents")
            print("   Run 'llmswap workspace init' to create one")
            return 1
        
        workspace_id = workspace_dir.name
        registry = WorkspaceRegistry()
        all_workspaces = registry.list_workspaces()
        
        project_path = None
        for ws in all_workspaces:
            if ws["workspace_id"] == workspace_id:
                project_path = Path(ws["project_path"])
                break
        
        if not project_path:
            print("❌ Workspace found but not in registry")
            return 1
        
        manager = WorkspaceManager(project_path)
        
        try:
            data = manager.load_workspace()
            
            print(f"📊 Workspace: {data['project_name']}")
            print(f"📁 Project Path: {project_path}")
            print(f"💾 Workspace Location: ~/.llmswap/workspaces/{workspace_id}/")
            print(f"🆔 Workspace ID: {data['workspace_id']}")
            print(f"\n📈 Statistics:")
            print(f"  Total queries: {data['statistics']['total_queries']}")
            print(f"  Learnings tracked: {data['statistics']['learnings_count']}")
            print(f"  Decisions recorded: {data['statistics']['decisions_count']}")
            print(f"\n⚙️  Settings:")
            print(f"  Default mentor: {data.get('default_mentor', 'guru')}")
            if data.get('mentor_alias'):
                print(f"  Mentor alias: {data['mentor_alias']}")
            if data.get('tags'):
                print(f"  Tags: {', '.join(data['tags'])}")
            
        except Exception as e:
            print(f"❌ Error loading workspace: {e}")
            return 1
    
    elif args.workspace_action == 'list':
        registry = WorkspaceRegistry()
        workspaces = registry.list_workspaces()
        
        if not workspaces:
            print("No workspaces found.")
            print("Run 'llmswap workspace init' in a project directory to create one.")
            return
        
        table_data = []
        for ws in workspaces:
            table_data.append([
                ws['project_name'],
                ws['project_path'],
                ws['last_accessed'][:10]
            ])
        
        headers = ["Project", "Path", "Last Used"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    elif args.workspace_action == 'journal':
        workspace_dir = WorkspaceDetector.detect()
        
        if not workspace_dir:
            print("❌ No workspace found")
            return 1
        
        learnings_file = workspace_dir / "learnings.md"
        
        if not learnings_file.exists():
            print("No learnings recorded yet.")
            return
        
        content = learnings_file.read_text()
        print(content)
    
    elif args.workspace_action == 'decisions':
        workspace_dir = WorkspaceDetector.detect()
        
        if not workspace_dir:
            print("❌ No workspace found")
            return 1
        
        decisions_file = workspace_dir / "decisions.md"
        
        if not decisions_file.exists():
            print("No decisions recorded yet.")
            return
        
        content = decisions_file.read_text()
        print(content)
    
    elif args.workspace_action == 'context':
        workspace_dir = WorkspaceDetector.detect()
        
        if not workspace_dir:
            print("❌ No workspace found")
            return 1
        
        context_file = workspace_dir / "context.md"
        
        import subprocess
        import os
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.call([editor, str(context_file)])

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
  llmswap providers                                           # View all providers status
  llmswap config set provider.models.cohere command-r-plus-08-2024
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
                       choices=['anthropic', 'openai', 'gemini', 'cohere', 'perplexity', 'watsonx', 'groq', 'ollama'],
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
    ask_parser.add_argument('--teach', action='store_true',
                           help='Enable teaching mode for detailed explanations')
    ask_parser.add_argument('--explain', action='store_true', 
                           help='Provide detailed explanation (alias for --teach)')
    ask_parser.add_argument('--mentor', choices=['teacher', 'mentor', 'tutor', 'developer', 'professor', 'buddy'],
                           help='Choose teaching style')
    ask_parser.add_argument('--alias', type=str,
                           help='Custom name for your mentor')
    
    # Age-appropriate explanations
    ask_parser.add_argument('--age', type=int, 
                           help='Target age for explanation (e.g., 10, 25, 50)')
    ask_parser.add_argument('--audience', type=str,
                           help='Target audience (e.g., "business owner", "student", "child")')
    ask_parser.add_argument('--level', choices=['beginner', 'intermediate', 'advanced'],
                           help='Knowledge level for explanation')
    ask_parser.add_argument('--explain-to', type=str, dest='explain_to',
                           help='Custom audience description')
    
    # chat command  
    chat_parser = subparsers.add_parser('chat', help='Start interactive chat')
    chat_parser.add_argument('--teach', action='store_true',
                            help='Start in teaching mode')
    chat_parser.add_argument('--mentor', choices=['teacher', 'mentor', 'tutor', 'developer', 'professor', 'buddy'],
                            help='Choose teaching style')
    chat_parser.add_argument('--alias', type=str,
                            help='Custom name for your mentor')
    
    # Age-appropriate explanations for chat
    chat_parser.add_argument('--age', type=int,
                            help='Set default age context for explanations')
    chat_parser.add_argument('--audience', type=str,
                            help='Set default audience context')
    chat_parser.add_argument('--level', choices=['beginner', 'intermediate', 'advanced'],
                            help='Set default knowledge level')
    
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
    
    # config command - Configuration management
    config_parser = subparsers.add_parser('config', help='Manage llmswap configuration')
    config_parser.add_argument('config_action', 
                              choices=['set', 'get', 'unset', 'show', 'list', 'reset', 
                                      'export', 'import', 'validate', 'doctor'],
                              help='Configuration action to perform')
    config_parser.add_argument('key', nargs='?', help='Configuration key (e.g., provider.default)')
    
    # providers command - Show provider status table
    providers_parser = subparsers.add_parser('providers', help='Show all providers and their status')
    providers_parser.add_argument('--format', choices=['table', 'json'], 
                                 default='table', help='Output format')
    config_parser.add_argument('value', nargs='?', help='Configuration value for set action')
    
    # workspace command - Manage project workspaces
    workspace_parser = subparsers.add_parser('workspace', help='Manage project workspaces')
    workspace_parser.add_argument('workspace_action',
                                 choices=['init', 'info', 'list', 'journal', 'decisions', 'context'],
                                 help='Workspace action to perform')
    workspace_parser.add_argument('--name', '-n', help='Project name for init')
    config_parser.add_argument('--file', '-f', help='File path for import/export operations')
    config_parser.add_argument('--merge', action='store_true', 
                              help='Merge imported config instead of replacing')
    config_parser.add_argument('--confirm', action='store_true',
                              help='Skip confirmation prompts')
    
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
        'config': cmd_config,
        'providers': cmd_providers,
        'workspace': cmd_workspace,
    }
    
    return commands[args.command](args)

if __name__ == '__main__':
    sys.exit(main())