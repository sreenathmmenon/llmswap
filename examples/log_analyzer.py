#!/usr/bin/env python3
"""
Log Analyzer - AI-powered log analysis and error detection

Perfect for:
- Production debugging
- Error pattern analysis
- Log correlation across services
- Timeline-based investigation
- System health monitoring
"""

import os
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from llmswap import LLMClient

def parse_timestamp(line, timestamp_patterns):
    """Extract timestamp from log line"""
    for pattern in timestamp_patterns:
        match = re.search(pattern, line)
        if match:
            try:
                # Common timestamp formats
                timestamp_str = match.group(1) if match.groups() else match.group(0)
                
                # Try different datetime formats
                formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y/%m/%d %H:%M:%S",
                    "%d/%b/%Y:%H:%M:%S",
                    "%b %d %H:%M:%S",
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(timestamp_str, fmt)
                    except ValueError:
                        continue
            except:
                continue
    return None

def extract_errors_from_logs(log_paths, start_time=None, end_time=None):
    """Extract error lines from log files within time range"""
    
    # Common timestamp patterns
    timestamp_patterns = [
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # 2024-08-17 15:30:45
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',  # 2024-08-17T15:30:45
        r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})',  # 2024/08/17 15:30:45
        r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',  # 17/Aug/2024:15:30:45
        r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})',      # Aug 17 15:30:45
    ]
    
    # Error indicators
    error_patterns = [
        r'(?i)(error|fail|exception|critical|fatal|panic|traceback)',
        r'(?i)(500|404|timeout|connection.{0,10}refused)',
        r'(?i)(stack trace|segmentation fault|core dumped)',
    ]
    
    errors = []
    
    for log_path in log_paths:
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_error = []
                error_timestamp = None
                
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check for timestamp
                    timestamp = parse_timestamp(line, timestamp_patterns)
                    
                    # Check if line contains error indicators
                    is_error = any(re.search(pattern, line) for pattern in error_patterns)
                    
                    if is_error:
                        # Start new error block
                        if current_error and error_timestamp:
                            # Save previous error if in time range
                            if (not start_time or error_timestamp >= start_time) and \
                               (not end_time or error_timestamp <= end_time):
                                errors.append({
                                    'file': log_path,
                                    'timestamp': error_timestamp,
                                    'lines': current_error,
                                    'line_number': line_num - len(current_error)
                                })
                        
                        current_error = [line]
                        error_timestamp = timestamp or datetime.now()
                    
                    elif current_error and (line.startswith('\t') or line.startswith(' ') or 
                                          'at ' in line or 'File "' in line):
                        # Continuation of error (stack trace, etc.)
                        current_error.append(line)
                        if len(current_error) > 50:  # Limit error size
                            break
                    
                    elif current_error:
                        # End of current error block
                        if error_timestamp and \
                           (not start_time or error_timestamp >= start_time) and \
                           (not end_time or error_timestamp <= end_time):
                            errors.append({
                                'file': log_path,
                                'timestamp': error_timestamp,
                                'lines': current_error,
                                'line_number': line_num - len(current_error)
                            })
                        current_error = []
                        error_timestamp = None
                
                # Handle last error
                if current_error and error_timestamp:
                    if (not start_time or error_timestamp >= start_time) and \
                       (not end_time or error_timestamp <= end_time):
                        errors.append({
                            'file': log_path,
                            'timestamp': error_timestamp,
                            'lines': current_error,
                            'line_number': len(errors)
                        })
                        
        except Exception as e:
            print(f"Error reading {log_path}: {e}")
    
    return sorted(errors, key=lambda x: x['timestamp'])

def analyze_errors_with_ai(errors, analysis_type="summary"):
    """Analyze errors using LLM"""
    
    if not errors:
        return "No errors found in the specified time range."
    
    # Prepare error summary for AI
    error_summary = f"Found {len(errors)} error(s) in logs:\n\n"
    
    for i, error in enumerate(errors[:10], 1):  # Limit to 10 errors
        error_summary += f"=== Error {i} ===\n"
        error_summary += f"File: {error['file']}\n"
        error_summary += f"Time: {error['timestamp']}\n"
        error_summary += f"Content:\n"
        error_summary += "\n".join(error['lines'][:10])  # Limit lines
        error_summary += "\n\n"
    
    if len(errors) > 10:
        error_summary += f"... and {len(errors) - 10} more errors\n"
    
    # Create analysis prompt
    if analysis_type == "summary":
        prompt = f"""
Analyze these system errors and provide:

1. Root cause analysis
2. Error patterns and correlations
3. Severity assessment
4. Recommended fixes
5. Prevention strategies

Log errors:
{error_summary}

Focus on actionable insights for system administrators and developers.
"""
    
    elif analysis_type == "timeline":
        prompt = f"""
Analyze the timeline of these errors:

{error_summary}

Provide:
1. Chronological pattern analysis
2. Error cascading effects
3. System health timeline
4. Critical incident identification
5. Recovery recommendations

Focus on understanding the sequence of events.
"""
    
    elif analysis_type == "correlation":
        prompt = f"""
Find correlations and patterns in these errors:

{error_summary}

Analyze:
1. Common error sources
2. Frequency patterns
3. Related system components
4. Potential cascading failures
5. Infrastructure dependencies

Identify systemic issues vs isolated incidents.
"""
    
    client = LLMClient(cache_enabled=True)
    response = client.query(prompt)
    
    return response.content, response.from_cache

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered log analysis and error detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /var/log/app.log --since "2h ago"
  %(prog)s /var/log/*.log --from "2024-08-17 14:00" --to "2024-08-17 16:00"
  %(prog)s /logs/ --analysis correlation --since "1d ago"
  %(prog)s app.log nginx.log --analysis timeline
        """
    )
    
    parser.add_argument('logs', nargs='+', 
                       help='Log files or directories to analyze')
    parser.add_argument('--from', '--start', dest='start_time',
                       help='Start time (YYYY-MM-DD HH:MM or "1h ago")')
    parser.add_argument('--to', '--end', dest='end_time', 
                       help='End time (YYYY-MM-DD HH:MM)')
    parser.add_argument('--since', 
                       help='Relative time like "2h ago", "1d ago"')
    parser.add_argument('--analysis', '-a',
                       choices=['summary', 'timeline', 'correlation'],
                       default='summary',
                       help='Type of analysis to perform')
    parser.add_argument('--errors-only', action='store_true',
                       help='Show only error extraction (no AI analysis)')
    
    args = parser.parse_args()
    
    # Parse time arguments
    start_time = None
    end_time = None
    
    if args.since:
        # Parse relative time
        if 'ago' in args.since:
            match = re.match(r'(\d+)([hmd])', args.since)
            if match:
                value = int(match.group(1))
                unit = match.group(2)
                
                if unit == 'h':
                    start_time = datetime.now() - timedelta(hours=value)
                elif unit == 'm':
                    start_time = datetime.now() - timedelta(minutes=value)
                elif unit == 'd':
                    start_time = datetime.now() - timedelta(days=value)
    
    if args.start_time:
        try:
            start_time = datetime.strptime(args.start_time, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Invalid start time format: {args.start_time}")
            return
    
    if args.end_time:
        try:
            end_time = datetime.strptime(args.end_time, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Invalid end time format: {args.end_time}")
            return
    
    # Collect log files
    log_files = []
    for log_path in args.logs:
        path = Path(log_path)
        if path.is_file():
            log_files.append(str(path))
        elif path.is_dir():
            # Find log files in directory
            for ext in ['*.log', '*.txt', '*.out', '*.err']:
                log_files.extend(str(p) for p in path.glob(ext))
        else:
            # Try glob pattern
            from glob import glob
            log_files.extend(glob(log_path))
    
    if not log_files:
        print("No log files found!")
        return
    
    print(f"Analyzing {len(log_files)} log file(s)...")
    if start_time:
        print(f"Time range: {start_time} onwards")
    if end_time:
        print(f"Until: {end_time}")
    
    # Extract errors
    errors = extract_errors_from_logs(log_files, start_time, end_time)
    
    if args.errors_only:
        # Just show errors
        print(f"\nFound {len(errors)} error(s):")
        for error in errors:
            print(f"\n=== {error['file']}:{error['line_number']} at {error['timestamp']} ===")
            for line in error['lines']:
                print(f"  {line}")
        return
    
    # AI Analysis
    print(f"\nAnalyzing {len(errors)} error(s) with AI ({args.analysis} analysis)...")
    
    analysis, from_cache = analyze_errors_with_ai(errors, args.analysis)
    
    cache_indicator = "[cached]" if from_cache else "[fresh]"
    
    print(f"\n{cache_indicator} Log Analysis Results:")
    print("=" * 60)
    print(analysis)
    
    if from_cache:
        print("\nTip: This analysis was cached (free!)")

if __name__ == "__main__":
    main()