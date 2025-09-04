"""
Price change monitoring and historical tracking system.

This module handles price volatility across LLM providers by maintaining
price history and providing alerts when significant changes occur.
"""

import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging


class PriceManager:
    """Monitor and track LLM pricing changes across providers."""
    
    def __init__(self):
        """Initialize price manager with storage directories."""
        self.config_dir = Path.home() / ".llmswap" / "analytics" 
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.price_history_file = self.config_dir / "price_history.json"
        self.alerts_file = self.config_dir / "price_alerts.json"
        self.config_file = self.config_dir / "price_config.json"
        
        self.price_history = self._load_price_history()
        self.alert_config = self._load_alert_config()
        
        # Setup logging
        self.logger = logging.getLogger("llmswap.price_manager")
    
    def _load_price_history(self) -> Dict[str, List[Dict]]:
        """Load historical price data."""
        if self.price_history_file.exists():
            try:
                with open(self.price_history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load price history: {e}")
                return {}
        return {}
    
    def _save_price_history(self):
        """Save price history to disk."""
        try:
            with open(self.price_history_file, 'w') as f:
                json.dump(self.price_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save price history: {e}")
    
    def _load_alert_config(self) -> Dict[str, Any]:
        """Load price alert configuration."""
        default_config = {
            "alert_threshold_percentage": 5.0,
            "check_interval_hours": 24,
            "enabled_providers": ["openai", "anthropic", "gemini", "watsonx"],
            "alert_methods": ["console"],  # Could add email, webhook later
            "last_check": None
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
            except Exception as e:
                self.logger.warning(f"Failed to load alert config: {e}")
        
        return default_config
    
    def _save_alert_config(self):
        """Save alert configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.alert_config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save alert config: {e}")
    
    def record_price_point(self, provider: str, model: str, pricing: Dict[str, float], 
                          source: str = "manual"):
        """
        Record a new price point in history.
        
        Args:
            provider: Provider name (e.g., 'openai')
            model: Model name (e.g., 'gpt-4')
            pricing: Price data (e.g., {'input': 0.03, 'output': 0.06})
            source: Source of the price data ('api', 'manual', 'scraped')
        """
        provider_key = f"{provider}:{model}"
        
        price_point = {
            "provider": provider,
            "model": model,
            "pricing": pricing,
            "timestamp": datetime.now().isoformat(),
            "source": source
        }
        
        if provider_key not in self.price_history:
            self.price_history[provider_key] = []
        
        # Check if this is different from the last recorded price
        history = self.price_history[provider_key]
        if history and self._is_price_change(history[-1]["pricing"], pricing):
            # Calculate change percentage
            change_info = self._calculate_price_change(history[-1]["pricing"], pricing)
            price_point["change_from_previous"] = change_info
            
            # Trigger alerts if significant change
            if abs(change_info["max_change_percentage"]) >= self.alert_config["alert_threshold_percentage"]:
                self._trigger_price_alert(provider, model, history[-1], price_point)
        
        history.append(price_point)
        
        # Keep only last 100 price points per model to avoid huge files
        if len(history) > 100:
            self.price_history[provider_key] = history[-100:]
        
        self._save_price_history()
    
    def _is_price_change(self, old_pricing: Dict[str, float], new_pricing: Dict[str, float]) -> bool:
        """Check if there's a meaningful price change."""
        for key in ["input", "output", "per_char"]:
            old_val = old_pricing.get(key, 0)
            new_val = new_pricing.get(key, 0)
            if old_val != new_val:
                return True
        return False
    
    def _calculate_price_change(self, old_pricing: Dict[str, float], 
                              new_pricing: Dict[str, float]) -> Dict[str, Any]:
        """Calculate percentage change between old and new pricing."""
        changes = {}
        max_change = 0
        
        for price_type in ["input", "output", "per_char"]:
            if price_type in old_pricing and price_type in new_pricing:
                old_val = old_pricing[price_type]
                new_val = new_pricing[price_type]
                
                if old_val > 0:
                    change_pct = ((new_val - old_val) / old_val) * 100
                    changes[price_type] = {
                        "old": old_val,
                        "new": new_val,
                        "change_percentage": round(change_pct, 2),
                        "direction": "increase" if change_pct > 0 else "decrease"
                    }
                    
                    if abs(change_pct) > abs(max_change):
                        max_change = change_pct
        
        return {
            "changes": changes,
            "max_change_percentage": round(max_change, 2),
            "overall_direction": "increase" if max_change > 0 else "decrease"
        }
    
    def _trigger_price_alert(self, provider: str, model: str, 
                           old_price_point: Dict, new_price_point: Dict):
        """Trigger price change alert."""
        alert = {
            "provider": provider,
            "model": model,
            "alert_type": "price_change",
            "old_pricing": old_price_point["pricing"],
            "new_pricing": new_price_point["pricing"],
            "change_info": new_price_point["change_from_previous"],
            "timestamp": datetime.now().isoformat(),
            "severity": self._get_alert_severity(new_price_point["change_from_previous"]["max_change_percentage"])
        }
        
        # Save alert
        self._save_alert(alert)
        
        # Console notification (could be enhanced with other methods)
        if "console" in self.alert_config["alert_methods"]:
            self._print_price_alert(alert)
    
    def _get_alert_severity(self, change_percentage: float) -> str:
        """Determine alert severity based on change percentage."""
        abs_change = abs(change_percentage)
        if abs_change >= 50:
            return "critical"
        elif abs_change >= 25:
            return "high"
        elif abs_change >= 10:
            return "medium"
        else:
            return "low"
    
    def _save_alert(self, alert: Dict):
        """Save price alert to disk."""
        alerts = []
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r') as f:
                    alerts = json.load(f)
            except Exception:
                alerts = []
        
        alerts.append(alert)
        
        # Keep only last 50 alerts
        if len(alerts) > 50:
            alerts = alerts[-50:]
        
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save alert: {e}")
    
    def _print_price_alert(self, alert: Dict):
        """Print price alert to console."""
        change = alert["change_info"]["max_change_percentage"]
        direction = "increased" if change > 0 else "decreased"
        
        print(f"\n🚨 PRICE ALERT: {alert['provider']} {alert['model']}")
        print(f"   Price has {direction} by {abs(change):.1f}%")
        print(f"   Severity: {alert['severity'].upper()}")
        
        if alert["severity"] in ["high", "critical"]:
            if change > 0:
                print(f"   💰 Your costs will increase - consider switching providers")
            else:
                print(f"   💸 Great news! Your costs just decreased")
    
    def get_price_history(self, provider: str, model: str, 
                         days: int = 30) -> List[Dict]:
        """Get price history for a specific provider/model."""
        provider_key = f"{provider}:{model}"
        
        if provider_key not in self.price_history:
            return []
        
        history = self.price_history[provider_key]
        
        if days:
            # Filter to last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_history = []
            
            for point in history:
                try:
                    point_date = datetime.fromisoformat(point["timestamp"])
                    if point_date >= cutoff_date:
                        filtered_history.append(point)
                except Exception:
                    # Include points with invalid timestamps (better than losing data)
                    filtered_history.append(point)
            
            return filtered_history
        
        return history
    
    def get_recent_alerts(self, days: int = 7) -> List[Dict]:
        """Get recent price alerts."""
        if not self.alerts_file.exists():
            return []
        
        try:
            with open(self.alerts_file, 'r') as f:
                all_alerts = json.load(f)
        except Exception:
            return []
        
        if not days:
            return all_alerts
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_alerts = []
        
        for alert in all_alerts:
            try:
                alert_date = datetime.fromisoformat(alert["timestamp"])
                if alert_date >= cutoff_date:
                    recent_alerts.append(alert)
            except Exception:
                recent_alerts.append(alert)
        
        return recent_alerts
    
    def analyze_price_trends(self, provider: str, model: str) -> Dict[str, Any]:
        """Analyze price trends for a provider/model."""
        history = self.get_price_history(provider, model, days=90)
        
        if len(history) < 2:
            return {
                "provider": provider,
                "model": model,
                "trend": "insufficient_data",
                "data_points": len(history)
            }
        
        # Calculate trend over time
        first_price = history[0]["pricing"]
        last_price = history[-1]["pricing"]
        
        trends = {}
        for price_type in ["input", "output", "per_char"]:
            if price_type in first_price and price_type in last_price:
                old_val = first_price[price_type]
                new_val = last_price[price_type]
                
                if old_val > 0:
                    change_pct = ((new_val - old_val) / old_val) * 100
                    trends[price_type] = {
                        "start_price": old_val,
                        "current_price": new_val,
                        "total_change_percentage": round(change_pct, 2),
                        "direction": "increasing" if change_pct > 0 else "decreasing"
                    }
        
        # Determine overall trend
        if trends:
            max_change = max([abs(t["total_change_percentage"]) for t in trends.values()])
            avg_change = sum([t["total_change_percentage"] for t in trends.values()]) / len(trends)
            
            if avg_change > 5:
                overall_trend = "increasing"
            elif avg_change < -5:
                overall_trend = "decreasing"
            else:
                overall_trend = "stable"
        else:
            overall_trend = "unknown"
            max_change = 0
            avg_change = 0
        
        return {
            "provider": provider,
            "model": model,
            "overall_trend": overall_trend,
            "max_change_percentage": round(max_change, 2),
            "average_change_percentage": round(avg_change, 2),
            "price_trends": trends,
            "data_points": len(history),
            "analysis_period_days": 90,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def get_cheapest_provider(self, input_tokens: int, output_tokens: int) -> Dict[str, Any]:
        """Find the cheapest provider based on current prices."""
        from ..metrics.cost_estimator import CostEstimator
        
        cost_estimator = CostEstimator()
        comparison = cost_estimator.compare_provider_costs(input_tokens, output_tokens)
        
        # Add price trend information
        enhanced_comparison = {}
        for provider, cost_info in comparison["comparison"].items():
            model = cost_info.get("model", "")
            trend = self.analyze_price_trends(provider, model)
            
            enhanced_comparison[provider] = {
                **cost_info,
                "price_trend": trend["overall_trend"],
                "trend_confidence": "high" if trend["data_points"] > 5 else "low"
            }
        
        return {
            **comparison,
            "comparison": enhanced_comparison,
            "recommendation": self._get_provider_recommendation(enhanced_comparison, comparison)
        }
    
    def _get_provider_recommendation(self, enhanced_comparison: Dict, 
                                   basic_comparison: Dict) -> Dict[str, str]:
        """Generate provider recommendation based on cost and trends."""
        cheapest_provider = basic_comparison["cheapest"]
        cheapest_info = enhanced_comparison[cheapest_provider]
        
        if cheapest_info["price_trend"] == "increasing":
            recommendation = f"{cheapest_provider} is cheapest now but prices are rising"
            strategy = "Use now but monitor for better alternatives"
        elif cheapest_info["price_trend"] == "decreasing":
            recommendation = f"{cheapest_provider} is cheapest and getting cheaper"
            strategy = "Excellent choice - costs likely to decrease further"
        else:
            recommendation = f"{cheapest_provider} is cheapest with stable pricing"
            strategy = "Safe choice for budget planning"
        
        return {
            "recommended_provider": cheapest_provider,
            "reason": recommendation,
            "strategy": strategy
        }
    
    def configure_alerts(self, threshold_percentage: float = None,
                        enabled_providers: List[str] = None,
                        check_interval_hours: int = None):
        """Configure price change alerts."""
        if threshold_percentage is not None:
            self.alert_config["alert_threshold_percentage"] = threshold_percentage
        
        if enabled_providers is not None:
            self.alert_config["enabled_providers"] = enabled_providers
        
        if check_interval_hours is not None:
            self.alert_config["check_interval_hours"] = check_interval_hours
        
        self._save_alert_config()
    
    def export_price_data(self, output_file: str, format: str = "json"):
        """Export price history data for analysis."""
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(self.price_history, f, indent=2)
        elif format == "csv":
            import csv
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Provider", "Model", "Timestamp", "Input_Price", "Output_Price", "Source"])
                
                for provider_model, history in self.price_history.items():
                    provider, model = provider_model.split(":", 1)
                    for point in history:
                        pricing = point["pricing"]
                        writer.writerow([
                            provider,
                            model,
                            point["timestamp"],
                            pricing.get("input", pricing.get("per_char", "")),
                            pricing.get("output", ""),
                            point["source"]
                        ])
        
        return f"Price data exported to {output_file}"