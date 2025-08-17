"""
Debug Helper - AI assistant for troubleshooting code issues

Perfect for:
- Error analysis and solutions
- Stack trace interpretation
- Bug reproduction steps
- Performance debugging
- Environment issues
"""

import sys
import argparse
from llmswap import LLMClient

def analyze_error(error_message, code_context=None, language="python"):
    """Analyze error and provide debugging suggestions"""
    
    prompt = f"""
I'm getting an error in my {language} code. Please help me debug this issue.

Error message:
{error_message}
"""
    
    if code_context:
        prompt += f"""

Code context:
```{language}
{code_context}
```
"""
    
    prompt += """
Please provide:
1. Explanation of what the error means
2. Most likely causes of this error
3. Step-by-step debugging approach
4. Specific code fixes or suggestions
5. How to prevent this error in the future

Be practical and specific in your recommendations.
"""
    
    client = LLMClient(cache_enabled=True)
    response = client.query(prompt)
    
    return response.content, response.from_cache

def explain_stack_trace(stack_trace, language="python"):
    """Explain stack trace and suggest fixes"""
    
    prompt = f"""
Please help me understand this {language} stack trace and suggest how to fix the issue:

Stack trace:
{stack_trace}

Please provide:
1. Root cause analysis
2. Which line is actually causing the problem
3. Common reasons for this type of error
4. Specific fix recommendations
5. Code examples if helpful

Focus on actionable solutions.
"""
    
    client = LLMClient(cache_enabled=True)
    response = client.query(prompt)
    
    return response.content, response.from_cache

def suggest_debugging_approach(description, language="python"):
    """Suggest debugging strategies for a problem description"""
    
    prompt = f"""
I'm having an issue with my {language} code. Here's the problem description:

{description}

Please suggest a systematic debugging approach:
1. Initial diagnostic steps
2. Tools and techniques to use
3. Common places to look for issues
4. Step-by-step investigation plan
5. How to isolate the problem

Provide practical, actionable debugging strategies.
"""
    
    client = LLMClient(cache_enabled=True)
    response = client.query(prompt)
    
    return response.content, response.from_cache

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered debugging assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --error "IndexError: list index out of range"
  %(prog)s --stack-trace "$(cat error.log)"
  %(prog)s --problem "My API calls are timing out randomly"
  %(prog)s --error "TypeError: 'int' object is not callable" --code "x = 5; result = x()"
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--error', '-e', 
                      help='Error message to analyze')
    group.add_argument('--stack-trace', '-s',
                      help='Stack trace to explain')  
    group.add_argument('--problem', '-p',
                      help='Problem description for debugging approach')
    
    parser.add_argument('--code', '-c',
                       help='Code context (optional, for error analysis)')
    parser.add_argument('--language', '-l',
                       default='python',
                       help='Programming language (default: python)')
    
    args = parser.parse_args()
    
    # Process based on input type
    if args.error:
        print(f"Analyzing error: {args.error}")
        if args.code:
            print(f"With code context provided")
        
        analysis, from_cache = analyze_error(args.error, args.code, args.language)
        title = "Error Analysis"
        
    elif args.stack_trace:
        print("Analyzing stack trace...")
        analysis, from_cache = explain_stack_trace(args.stack_trace, args.language)
        title = "Stack Trace Analysis"
        
    elif args.problem:
        print(f"Problem: {args.problem}")
        analysis, from_cache = suggest_debugging_approach(args.problem, args.language)
        title = "Debugging Strategy"
    
    # Display results
    cache_indicator = "[cached]" if from_cache else "[fresh]"
    
    print(f"\n{cache_indicator} {title}:")
    print("=" * 60)
    print(analysis)
    
    if from_cache:
        print("\nTip: This analysis was cached (free!)")

if __name__ == "__main__":
    main()