"""
Code Review Assistant - AI-powered code analysis and suggestions

Perfect for:
- Pull request reviews
- Code quality checks
- Bug detection
- Style improvements
- Security analysis
"""

import sys
import argparse
from llmswap import LLMClient

def review_code(code_content, language="python", focus=None):
    """Review code and provide suggestions"""
    
    focus_prompts = {
        "bugs": "Focus on finding potential bugs, edge cases, and runtime errors",
        "style": "Focus on code style, readability, and best practices",
        "security": "Focus on security vulnerabilities and potential exploits",
        "performance": "Focus on performance optimizations and efficiency",
        "general": "Provide a comprehensive code review covering all aspects"
    }
    
    review_focus = focus_prompts.get(focus, focus_prompts["general"])
    
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
    
    client = LLMClient(cache_enabled=True)
    response = client.query(prompt)
    
    return response.content, response.from_cache

def review_file(file_path, language=None, focus=None):
    """Review code from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        if not language:
            # Simple language detection based on file extension
            ext_map = {
                '.py': 'python',
                '.js': 'javascript', 
                '.jsx': 'javascript',
                '.ts': 'typescript',
                '.tsx': 'typescript',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.go': 'go',
                '.rs': 'rust',
                '.rb': 'ruby',
                '.php': 'php'
            }
            
            for ext, lang in ext_map.items():
                if file_path.endswith(ext):
                    language = lang
                    break
            
            if not language:
                language = "code"
        
        return review_code(code_content, language, focus)
        
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found", False
    except Exception as e:
        return f"Error reading file: {e}", False

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered code review assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s app.py
  %(prog)s --focus bugs main.js
  %(prog)s --language python --focus security < code.py
  echo "def func(): pass" | %(prog)s --language python
        """
    )
    
    parser.add_argument('file', nargs='?', help='File to review (or use stdin)')
    parser.add_argument('--language', '-l', 
                       help='Programming language (auto-detected from extension)')
    parser.add_argument('--focus', '-f',
                       choices=['bugs', 'style', 'security', 'performance', 'general'],
                       default='general',
                       help='Review focus area')
    
    args = parser.parse_args()
    
    # Get code content
    if args.file:
        print(f"Reviewing file: {args.file}")
        review_text, from_cache = review_file(args.file, args.language, args.focus)
    else:
        # Read from stdin
        print("Reading code from stdin...")
        try:
            code_content = sys.stdin.read().strip()
            if not code_content:
                print("Error: No code provided")
                return
            
            language = args.language or "code"
            review_text, from_cache = review_code(code_content, language, args.focus)
        except KeyboardInterrupt:
            print("\nReview cancelled")
            return
    
    # Display results
    cache_indicator = "[cached]" if from_cache else "[fresh]"
    
    print(f"\n{cache_indicator} Code Review ({args.focus} focus):")
    print("=" * 60)
    print(review_text)
    
    if from_cache:
        print("\nTip: This review was cached (free!)")

if __name__ == "__main__":
    main()