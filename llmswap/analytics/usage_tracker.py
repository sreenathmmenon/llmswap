"""
Privacy-first usage analytics tracking.

This module tracks usage patterns and performance metrics WITHOUT
storing any user queries, file names, or sensitive information.
Only aggregated statistics and performance data are recorded.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from pathlib import Path
import hashlib


class UsageTracker:
    """Privacy-first usage analytics with zero query logging."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize usage tracker with local SQLite database."""
        if db_path:
            self.db_path = Path(db_path)
        else:
            analytics_dir = Path.home() / ".llmswap" / "analytics"
            analytics_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = analytics_dir / "usage_stats.db"
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with privacy-first schema."""
        with sqlite3.connect(self.db_path) as conn:
            # Main usage statistics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT,
                    provider TEXT NOT NULL,
                    model TEXT,
                    command_type TEXT,
                    
                    -- Token and cost metrics (no content)
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    total_tokens INTEGER,
                    estimated_cost REAL,
                    actual_cost REAL,
                    
                    -- Performance metrics
                    response_time_ms INTEGER,
                    time_to_first_token_ms INTEGER,
                    
                    -- Efficiency metrics
                    cache_hit BOOLEAN DEFAULT FALSE,
                    fallback_used BOOLEAN DEFAULT FALSE,
                    retry_count INTEGER DEFAULT 0,
                    
                    -- Success/error tracking (no details)
                    success BOOLEAN DEFAULT TRUE,
                    error_category TEXT,
                    
                    -- Optional context (no sensitive data)
                    file_type TEXT,  -- e.g., "python", "javascript" (extension only)
                    operation_type TEXT  -- e.g., "review", "debug", "chat"
                )
            """)
            
            # Daily aggregated statistics
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    total_queries INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    unique_sessions INTEGER DEFAULT 0,
                    
                    -- Provider breakdown (JSON)
                    provider_stats TEXT,
                    
                    -- Performance aggregates
                    avg_response_time_ms REAL,
                    cache_hit_rate REAL,
                    success_rate REAL,
                    
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Budget tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budget_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period_type TEXT NOT NULL,  -- 'daily', 'weekly', 'monthly'
                    period_start TEXT NOT NULL,
                    budget_limit REAL,
                    current_spend REAL DEFAULT 0.0,
                    query_count INTEGER DEFAULT 0,
                    
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_stats(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_provider ON usage_stats(provider)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date)")
    
    def record_usage(self, 
                    provider: str,
                    model: Optional[str] = None,
                    command_type: Optional[str] = None,
                    input_tokens: Optional[int] = None,
                    output_tokens: Optional[int] = None,
                    estimated_cost: Optional[float] = None,
                    actual_cost: Optional[float] = None,
                    response_time_ms: Optional[int] = None,
                    time_to_first_token_ms: Optional[int] = None,
                    cache_hit: bool = False,
                    fallback_used: bool = False,
                    retry_count: int = 0,
                    success: bool = True,
                    error_category: Optional[str] = None,
                    file_type: Optional[str] = None,
                    session_id: Optional[str] = None) -> str:
        """
        Record a usage event with privacy-first approach.
        
        IMPORTANT: This method NEVER stores user queries, file paths,
        or any sensitive information. Only aggregated metrics.
        
        Returns:
            Record ID for reference
        """
        timestamp = datetime.now().isoformat()
        
        # Validate and convert all inputs to proper types
        input_tokens = int(input_tokens) if input_tokens is not None else 0
        output_tokens = int(output_tokens) if output_tokens is not None else 0
        total_tokens = input_tokens + output_tokens
        
        # Ensure costs are proper numbers or None
        if estimated_cost is not None:
            try:
                estimated_cost = float(estimated_cost)
            except (ValueError, TypeError):
                estimated_cost = None
                
        if actual_cost is not None:
            try:
                actual_cost = float(actual_cost)
            except (ValueError, TypeError):
                actual_cost = None
                
        # Ensure timing values are proper integers or None
        if response_time_ms is not None:
            try:
                response_time_ms = int(response_time_ms)
            except (ValueError, TypeError):
                response_time_ms = None
                
        if time_to_first_token_ms is not None:
            try:
                time_to_first_token_ms = int(time_to_first_token_ms)
            except (ValueError, TypeError):
                time_to_first_token_ms = None
        
        # Generate session ID if not provided (for grouping related queries)
        if not session_id:
            session_id = self._generate_session_id()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO usage_stats (
                    timestamp, session_id, provider, model, command_type,
                    input_tokens, output_tokens, total_tokens,
                    estimated_cost, actual_cost, response_time_ms,
                    time_to_first_token_ms, cache_hit, fallback_used,
                    retry_count, success, error_category, file_type, operation_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, session_id, provider, model, command_type,
                input_tokens, output_tokens, total_tokens,
                estimated_cost, actual_cost, response_time_ms,
                time_to_first_token_ms, cache_hit, fallback_used,
                retry_count, success, error_category, file_type, command_type
            ))
            
            record_id = cursor.lastrowid
        
        # Update daily aggregates
        self._update_daily_stats(timestamp, total_tokens, actual_cost or estimated_cost or 0, 
                                provider, success, response_time_ms, cache_hit, session_id)
        
        # Update budget tracking
        self._update_budget_tracking(actual_cost or estimated_cost or 0)
        
        return str(record_id)
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID for grouping related queries."""
        # Create a session ID based on time and some randomness
        # This helps group related queries without identifying users
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _update_daily_stats(self, timestamp: str, tokens: int, cost: float,
                          provider: str, success: bool, response_time_ms: Optional[int],
                          cache_hit: bool, session_id: str):
        """Update daily aggregated statistics."""
        date = timestamp.split('T')[0]  # Extract date part
        
        # Validate inputs to prevent corruption
        tokens = int(tokens) if tokens is not None else 0
        cost = float(cost) if cost is not None else 0.0
        response_time_ms = int(response_time_ms) if response_time_ms is not None else 0
        
        with sqlite3.connect(self.db_path) as conn:
            # Get existing daily stats
            existing = conn.execute(
                "SELECT * FROM daily_stats WHERE date = ?", (date,)
            ).fetchone()
            
            if existing:
                # Update existing record with proper validation
                try:
                    current_stats = json.loads(existing[5]) if existing[5] else {}
                except (json.JSONDecodeError, TypeError):
                    current_stats = {}
                
                # Update provider stats
                if provider not in current_stats:
                    current_stats[provider] = {"queries": 0, "tokens": 0, "cost": 0.0}
                
                current_stats[provider]["queries"] += 1
                current_stats[provider]["tokens"] += tokens
                current_stats[provider]["cost"] += cost
                
                # Calculate new aggregates with safe conversion
                try:
                    new_total_queries = int(existing[1]) + 1
                    new_total_tokens = int(existing[2]) + tokens
                    new_total_cost = float(existing[3]) + cost
                except (ValueError, TypeError):
                    # If existing data is corrupted, start fresh
                    new_total_queries = 1
                    new_total_tokens = tokens
                    new_total_cost = cost
                
                # Update averages with safe conversion
                try:
                    existing_avg_time = float(existing[6]) if existing[6] is not None else 0.0
                    if response_time_ms and existing_avg_time > 0:
                        new_avg_response_time = (existing_avg_time + response_time_ms) / 2
                    elif response_time_ms:
                        new_avg_response_time = response_time_ms
                    else:
                        new_avg_response_time = existing_avg_time
                except (ValueError, TypeError):
                    new_avg_response_time = response_time_ms or 0.0
                
                try:
                    new_cache_hit_rate = float(existing[7]) if existing[7] is not None else 0.0
                    existing_success_rate = float(existing[8]) if existing[8] is not None else 0.0
                    existing_queries = int(existing[1]) if existing[1] is not None else 0
                    new_success_rate = ((existing_success_rate * existing_queries) + (1 if success else 0)) / new_total_queries
                except (ValueError, TypeError):
                    new_cache_hit_rate = 0.0
                    new_success_rate = 1.0 if success else 0.0
                
                conn.execute("""
                    UPDATE daily_stats SET
                        total_queries = ?, total_tokens = ?, total_cost = ?,
                        provider_stats = ?, avg_response_time_ms = ?,
                        cache_hit_rate = ?, success_rate = ?, updated_at = ?
                    WHERE date = ?
                """, (
                    new_total_queries, new_total_tokens, new_total_cost,
                    json.dumps(current_stats), new_avg_response_time,
                    new_cache_hit_rate, new_success_rate, datetime.now().isoformat(), date
                ))
            else:
                # Create new daily record
                provider_stats = {provider: {"queries": 1, "tokens": tokens, "cost": cost}}
                
                conn.execute("""
                    INSERT INTO daily_stats (
                        date, total_queries, total_tokens, total_cost,
                        unique_sessions, provider_stats, avg_response_time_ms,
                        cache_hit_rate, success_rate, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date, 1, tokens, cost, 1, json.dumps(provider_stats),
                    response_time_ms or 0, 1.0 if cache_hit else 0.0, 
                    1.0 if success else 0.0, datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
    
    def _update_budget_tracking(self, cost: float):
        """Update budget tracking for current period."""
        today = datetime.now().date()
        
        # Update monthly budget
        month_start = today.replace(day=1).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute("""
                SELECT * FROM budget_tracking 
                WHERE period_type = 'monthly' AND period_start = ?
            """, (month_start,)).fetchone()
            
            if existing:
                new_spend = existing[4] + cost
                new_count = existing[5] + 1
                conn.execute("""
                    UPDATE budget_tracking SET
                        current_spend = ?, query_count = ?, updated_at = ?
                    WHERE id = ?
                """, (new_spend, new_count, datetime.now().isoformat(), existing[0]))
            else:
                conn.execute("""
                    INSERT INTO budget_tracking (
                        period_type, period_start, current_spend, query_count,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    'monthly', month_start, cost, 1,
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Get daily stats
            daily_data = conn.execute("""
                SELECT * FROM daily_stats 
                WHERE date >= ? ORDER BY date DESC
            """, (start_date.date().isoformat(),)).fetchall()
            
            # Get provider breakdown
            provider_stats = conn.execute("""
                SELECT provider, 
                       COUNT(*) as queries,
                       SUM(total_tokens) as total_tokens,
                       SUM(actual_cost) as total_cost,
                       AVG(response_time_ms) as avg_response_time,
                       AVG(CASE WHEN cache_hit THEN 1.0 ELSE 0.0 END) as cache_hit_rate,
                       AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
                FROM usage_stats 
                WHERE timestamp >= ?
                GROUP BY provider
            """, (start_date.isoformat(),)).fetchall()
            
            # Get command type breakdown
            command_stats = conn.execute("""
                SELECT command_type, 
                       COUNT(*) as queries,
                       AVG(total_tokens) as avg_tokens,
                       AVG(actual_cost) as avg_cost
                FROM usage_stats 
                WHERE timestamp >= ? AND command_type IS NOT NULL
                GROUP BY command_type
            """, (start_date.isoformat(),)).fetchall()
        
        # Format results
        formatted_daily = []
        for row in daily_data:
            formatted_daily.append({
                "date": row[0],
                "queries": int(row[1]) if row[1] is not None else 0,
                "tokens": int(row[2]) if row[2] is not None else 0, 
                "cost": float(row[3]) if row[3] is not None else 0.0,
                "provider_breakdown": json.loads(row[5]) if row[5] else {},
                "avg_response_time_ms": float(row[6]) if row[6] is not None else 0.0,
                "cache_hit_rate": float(row[7]) if row[7] is not None else 0.0,
                "success_rate": float(row[8]) if row[8] is not None else 0.0
            })
        
        formatted_providers = []
        for row in provider_stats:
            formatted_providers.append({
                "provider": row[0],
                "queries": int(row[1]) if row[1] is not None else 0,
                "tokens": int(row[2]) if row[2] is not None else 0,
                "cost": float(row[3]) if row[3] is not None else 0.0,
                "avg_response_time_ms": float(row[4]) if row[4] is not None else 0.0,
                "cache_hit_rate": float(row[5]) if row[5] is not None else 0.0,
                "success_rate": float(row[6]) if row[6] is not None else 0.0
            })
        
        formatted_commands = []
        for row in command_stats:
            formatted_commands.append({
                "command": row[0],
                "queries": int(row[1]) if row[1] is not None else 0,
                "avg_tokens": float(row[2]) if row[2] is not None else 0.0,
                "avg_cost": float(row[3]) if row[3] is not None else 0.0
            })
        
        # Calculate totals
        total_queries = sum(day["queries"] for day in formatted_daily)
        total_cost = sum(day["cost"] for day in formatted_daily)
        total_tokens = sum(day["tokens"] for day in formatted_daily)
        
        return {
            "period": {
                "days": days,
                "start_date": start_date.date().isoformat(),
                "end_date": end_date.date().isoformat()
            },
            "totals": {
                "queries": total_queries,
                "tokens": total_tokens,
                "cost": round(total_cost, 4),
                "avg_cost_per_query": round(total_cost / total_queries, 4) if total_queries > 0 else 0
            },
            "daily_breakdown": formatted_daily,
            "provider_breakdown": formatted_providers,
            "command_breakdown": formatted_commands,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_cost_analysis(self) -> Dict[str, Any]:
        """Analyze cost patterns and provide optimization suggestions."""
        stats = self.get_usage_stats(30)
        
        if not stats["provider_breakdown"]:
            return {"error": "No usage data available for analysis"}
        
        # Find most expensive provider
        providers = stats["provider_breakdown"]
        most_expensive = max(providers, key=lambda p: p["cost"])
        cheapest = min(providers, key=lambda p: p["cost"]) if len(providers) > 1 else most_expensive
        
        # Calculate potential savings
        potential_savings = 0
        if len(providers) > 1 and cheapest["cost"] < most_expensive["cost"]:
            cost_per_query_expensive = most_expensive["cost"] / most_expensive["queries"]
            cost_per_query_cheap = cheapest["cost"] / cheapest["queries"]
            savings_per_query = cost_per_query_expensive - cost_per_query_cheap
            potential_savings = savings_per_query * most_expensive["queries"]
        
        # Analyze cache effectiveness
        overall_cache_rate = sum(p["cache_hit_rate"] * p["queries"] for p in providers) / sum(p["queries"] for p in providers)
        cache_savings_estimate = stats["totals"]["cost"] * overall_cache_rate * 0.5  # Rough estimate
        
        return {
            "current_spend": {
                "monthly_total": round(stats["totals"]["cost"], 2),
                "most_expensive_provider": most_expensive["provider"],
                "cheapest_provider": cheapest["provider"]
            },
            "optimization_opportunities": {
                "potential_provider_savings": round(potential_savings, 2),
                "cache_savings_estimate": round(cache_savings_estimate, 2),
                "overall_cache_hit_rate": round(overall_cache_rate, 3)
            },
            "recommendations": self._generate_cost_recommendations(providers, overall_cache_rate),
            "analysis_date": datetime.now().isoformat()
        }
    
    def _generate_cost_recommendations(self, providers: List[Dict], cache_rate: float) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        if len(providers) > 1:
            # Provider switching recommendation
            cheapest = min(providers, key=lambda p: p["cost"] / p["queries"])
            most_expensive = max(providers, key=lambda p: p["cost"] / p["queries"])
            
            if cheapest["provider"] != most_expensive["provider"]:
                savings_pct = ((most_expensive["cost"]/most_expensive["queries"]) - 
                             (cheapest["cost"]/cheapest["queries"])) / (most_expensive["cost"]/most_expensive["queries"]) * 100
                
                recommendations.append(
                    f"Switch from {most_expensive['provider']} to {cheapest['provider']} "
                    f"to save {savings_pct:.1f}% per query"
                )
        
        # Cache recommendations
        if cache_rate < 0.3:
            recommendations.append(
                f"Enable caching to potentially save 20-40% on costs "
                f"(current cache hit rate: {cache_rate*100:.1f}%)"
            )
        elif cache_rate < 0.6:
            recommendations.append(
                f"Increase cache TTL to improve hit rate from {cache_rate*100:.1f}%"
            )
        
        # High usage recommendations
        total_queries = sum(p["queries"] for p in providers)
        if total_queries > 1000:
            recommendations.append(
                "Consider bulk processing or batching requests to reduce API overhead"
            )
        
        return recommendations
    
    def export_usage_report(self, output_file: str, format: str = "json", days: int = 30):
        """Export usage report for analysis or compliance."""
        stats = self.get_usage_stats(days)
        
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(stats, f, indent=2)
        
        elif format == "csv":
            import csv
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write summary
                writer.writerow(["Summary"])
                writer.writerow(["Total Queries", stats["totals"]["queries"]])
                writer.writerow(["Total Tokens", stats["totals"]["tokens"]])
                writer.writerow(["Total Cost", f"${stats['totals']['cost']:.4f}"])
                writer.writerow([])
                
                # Write daily breakdown
                writer.writerow(["Daily Breakdown"])
                writer.writerow(["Date", "Queries", "Tokens", "Cost"])
                for day in stats["daily_breakdown"]:
                    writer.writerow([day["date"], day["queries"], day["tokens"], f"${day['cost']:.4f}"])
                writer.writerow([])
                
                # Write provider breakdown
                writer.writerow(["Provider Breakdown"])
                writer.writerow(["Provider", "Queries", "Tokens", "Cost", "Avg Response Time (ms)", "Success Rate"])
                for provider in stats["provider_breakdown"]:
                    writer.writerow([
                        provider["provider"], provider["queries"], provider["tokens"],
                        f"${provider['cost']:.4f}", f"{provider['avg_response_time_ms']:.1f}",
                        f"{provider['success_rate']*100:.1f}%"
                    ])
        
        return f"Usage report exported to {output_file}"
    
    def clear_old_data(self, days_to_keep: int = 90):
        """Clear old usage data to prevent database growth."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with sqlite3.connect(self.db_path) as conn:
            # Clear old detailed usage stats
            result = conn.execute(
                "DELETE FROM usage_stats WHERE timestamp < ?", 
                (cutoff_date.isoformat(),)
            )
            
            # Keep daily stats (they're much smaller)
            daily_cutoff = cutoff_date - timedelta(days=365)  # Keep daily stats for 1 year
            conn.execute(
                "DELETE FROM daily_stats WHERE date < ?",
                (daily_cutoff.date().isoformat(),)
            )
            
            # Vacuum database to reclaim space
            conn.execute("VACUUM")
        
        return f"Cleared {result.rowcount} old records older than {days_to_keep} days"