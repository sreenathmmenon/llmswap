"""
Provider cost comparison for LLM API calls.

This module provides pricing data across providers for cost comparison.
Focused on ACTUAL costs, not pre-query estimation.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from pathlib import Path


class CostEstimator:
    """Compare costs across LLM providers using current pricing."""
    
    def __init__(self):
        """Initialize cost estimator with current pricing data."""
        self.pricing_dir = Path.home() / ".llmswap" / "pricing"
        self.pricing_dir.mkdir(parents=True, exist_ok=True)
        
        self.pricing_file = self.pricing_dir / "current_pricing.json"
        self.history_dir = self.pricing_dir / "history"
        self.history_dir.mkdir(exist_ok=True)
        
        self._load_pricing()
    
    def _load_pricing(self):
        """Load current pricing data, initialize if needed."""
        if self.pricing_file.exists():
            try:
                with open(self.pricing_file, 'r') as f:
                    data = json.load(f)
                    self.pricing = data.get("pricing", {})
                    self.last_updated = data.get("last_updated")
            except Exception:
                self._initialize_default_pricing()
        else:
            self._initialize_default_pricing()
    
    def _initialize_default_pricing(self):
        """Initialize with default pricing (as of January 2025)."""
        # These prices will be automatically updated when online
        self.pricing = {
            "openai": {
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-4-turbo": {"input": 0.01, "output": 0.03},
                "gpt-4o": {"input": 0.0025, "output": 0.01},
                "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
                "o1-preview": {"input": 0.015, "output": 0.06},
                "o1-mini": {"input": 0.003, "output": 0.012},
                "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
            },
            "anthropic": {
                "claude-sonnet-4-5": {"input": 0.003, "output": 0.015},  # NEW: Best coding model
                "claude-3-opus": {"input": 0.015, "output": 0.075},
                "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
                "claude-3-5-sonnet-20241220": {"input": 0.003, "output": 0.015},
                "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},  # Deprecated Oct 22, 2025
                "claude-3-5-haiku": {"input": 0.001, "output": 0.005},
                "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
            },
            "gemini": {
                "gemini-1.5-pro": {"per_char": 0.0000003125},                 # Legacy char-based pricing
                "gemini-1.5-flash": {"per_char": 0.00000015625},               # Legacy char-based pricing
                "gemini-1.5-pro-token": {"input": 0.00125, "output": 0.005},  # $1.25/$5.00 per million 
                "gemini-1.5-flash-token": {"input": 0.00015, "output": 0.0006}, # $0.15/$0.60 per million
                "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},      # $0.10/$0.40 per million
                "gemini-2.0-flash-exp": {"input": 0.0001, "output": 0.0004},  # Experimental model
                "gemini-2.5-pro": {"input": 0.00125, "output": 0.01}          # $1.25/$10.00 per million
            },
            "watsonx": {
                "granite-3.1-8b-instruct": {"input": 0.0002, "output": 0.0002},  # $0.20 per million tokens
                "granite-3.1-2b-instruct": {"input": 0.0001, "output": 0.0001},  # Lower cost for smaller model
                "granite-13b": {"input": 0.0002, "output": 0.0002},  # Updated pricing
                "granite-7b": {"input": 0.0002, "output": 0.0002}   # Updated pricing
            },
            "groq": {
                "llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},    # $0.05/$0.08 per M
                "llama-3.3-70b-versatile": {"input": 0.00059, "output": 0.00079}, # $0.59/$0.79 per M  
                "gpt-oss-20b": {"input": 0.0001, "output": 0.0005}               # $0.10/$0.50 per M
            },
            "cohere": {
                "command-r-03-2024": {"input": 0.0005, "output": 0.0015},        # $0.50/$1.50 per million
                "command-r-plus-04-2024": {"input": 0.003, "output": 0.015},     # $3.00/$15.00 per million
                "command-r-plus-08-2024": {"input": 0.0025, "output": 0.01},     # $2.50/$10.00 per million
                "aya-expanse-8b": {"input": 0.0005, "output": 0.0015},           # $0.50/$1.50 per million
                "aya-expanse-32b": {"input": 0.0005, "output": 0.0015}           # $0.50/$1.50 per million
            },
            "perplexity": {
                "sonar-pro": {"input": 0.001, "output": 0.003},                  # Estimated $1/$3 per million
                "pplx-7b-online": {"input": 0.0002, "output": 0.0008},           # Estimated low-end pricing
                "pplx-70b-online": {"input": 0.001, "output": 0.004}             # Estimated mid-range pricing  
            },
            "ollama": {
                "all_models": {"input": 0, "output": 0}
            }
        }
        
        self.last_updated = datetime.now().isoformat()
        self._save_pricing()
    
    def _save_pricing(self):
        """Save current pricing to disk."""
        data = {
            "pricing": self.pricing,
            "last_updated": self.last_updated,
            "version": "4.0.0"
        }
        
        with open(self.pricing_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def estimate_cost(self, 
                     input_tokens: int, 
                     output_tokens: int,
                     provider: str, 
                     model: str = None) -> Dict[str, Any]:
        """
        Estimate cost for a query with given token counts.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            provider: Provider name
            model: Specific model name
            
        Returns:
            Dict with cost breakdown and metadata
        """
        provider = provider.lower()
        
        if provider not in self.pricing:
            return {
                "total_cost": 0.0,
                "input_cost": 0.0, 
                "output_cost": 0.0,
                "confidence": "unknown",
                "provider": provider,
                "model": model,
                "error": f"Pricing not available for provider: {provider}"
            }
        
        if provider == "ollama":
            return {
                "total_cost": 0.0,
                "input_cost": 0.0,
                "output_cost": 0.0, 
                "confidence": "high",
                "provider": provider,
                "model": model,
                "note": "Local model - no API costs"
            }
        
        if provider == "gemini":
            # Check if model uses char-based or token-based pricing
            provider_pricing = self.pricing[provider]
            model_pricing = provider_pricing.get(model) or next(iter(provider_pricing.values()))
            if "per_char" in model_pricing:
                return self._estimate_gemini_cost(input_tokens, output_tokens, model)
            else:
                return self._estimate_token_based_cost(input_tokens, output_tokens, provider, model)
        
        return self._estimate_token_based_cost(input_tokens, output_tokens, provider, model)
    
    def _estimate_token_based_cost(self, input_tokens: int, output_tokens: int, 
                                 provider: str, model: str) -> Dict[str, Any]:
        """Estimate cost for token-based pricing (OpenAI, Anthropic, etc.)."""
        provider_pricing = self.pricing[provider]
        
        # Find the right model pricing
        model_pricing = None
        if model and model in provider_pricing:
            model_pricing = provider_pricing[model]
        else:
            # Use the first available model as default
            model_pricing = next(iter(provider_pricing.values()))
            if not model:
                model = next(iter(provider_pricing.keys()))
        
        input_rate = model_pricing["input"] / 1000  # Convert to per-token rate
        output_rate = model_pricing["output"] / 1000
        
        input_cost = input_tokens * input_rate
        output_cost = output_tokens * output_rate
        total_cost = input_cost + output_cost
        
        return {
            "total_cost": round(total_cost, 6),
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_rate_per_1k": model_pricing["input"],
            "output_rate_per_1k": model_pricing["output"],
            "confidence": "high",
            "provider": provider,
            "model": model,
            "pricing_date": self.last_updated
        }
    
    def _estimate_gemini_cost(self, input_tokens: int, output_tokens: int, 
                            model: str) -> Dict[str, Any]:
        """Estimate cost for Gemini (character-based pricing)."""
        # Convert tokens back to approximate character count
        input_chars = input_tokens * 4  # Rough conversion
        output_chars = output_tokens * 4
        total_chars = input_chars + output_chars
        
        gemini_pricing = self.pricing["gemini"]
        model_key = model if model in gemini_pricing else "gemini-1.5-pro"
        
        rate_per_char = gemini_pricing[model_key]["per_char"]
        total_cost = total_chars * rate_per_char
        
        return {
            "total_cost": round(total_cost, 6),
            "input_cost": round(input_chars * rate_per_char, 6),
            "output_cost": round(output_chars * rate_per_char, 6),
            "total_characters": total_chars,
            "rate_per_char": rate_per_char,
            "confidence": "medium",
            "provider": "gemini",
            "model": model_key,
            "note": "Converted from tokens to characters",
            "pricing_date": self.last_updated
        }
    
    def compare_provider_costs(self, input_tokens: int, output_tokens: int, 
                             models: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Compare costs across all providers for the same query.
        
        Args:
            input_tokens: Input token count
            output_tokens: Output token count  
            models: Optional dict of provider -> model mappings
            
        Returns:
            Dict with cost comparison across providers
        """
        if models is None:
            models = {
                "openai": "gpt-4o-mini",           # Latest cost-effective model
                "anthropic": "claude-sonnet-4-5",  # Latest: Best coding model
                "gemini": "gemini-2.0-flash-exp",  # Latest experimental
                "cohere": "command-r-plus-08-2024", # Latest Command-R+
                "perplexity": "sonar-pro",         # Main model
                "watsonx": "granite-13b",          # Use existing model name
                "groq": "llama-3.1-8b-instant",   # Fast and cost-effective
                "ollama": "llama3"                 # Free local
            }
        
        comparison = {}
        costs = []
        
        for provider, model in models.items():
            cost_info = self.estimate_cost(input_tokens, output_tokens, provider, model)
            comparison[provider] = cost_info
            
            if cost_info.get("total_cost", 0) > 0:
                costs.append((provider, cost_info["total_cost"]))
        
        # Sort by cost
        costs.sort(key=lambda x: x[1])
        
        if costs:
            cheapest = costs[0]
            most_expensive = costs[-1] if len(costs) > 1 else costs[0]
            
            savings_vs_most_expensive = most_expensive[1] - cheapest[1]
            savings_percentage = (savings_vs_most_expensive / most_expensive[1] * 100) if most_expensive[1] > 0 else 0
        else:
            cheapest = ("ollama", 0)
            most_expensive = ("unknown", 0)
            savings_vs_most_expensive = 0
            savings_percentage = 0
        
        return {
            "comparison": comparison,
            "cheapest": cheapest[0],
            "cheapest_cost": cheapest[1],
            "most_expensive": most_expensive[0], 
            "most_expensive_cost": most_expensive[1],
            "max_savings": round(savings_vs_most_expensive, 6),
            "max_savings_percentage": round(savings_percentage, 1),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "compared_at": datetime.now().isoformat()
        }
    
    def get_pricing_confidence(self) -> Dict[str, Any]:
        """Check how current our pricing data is."""
        if not self.last_updated:
            return {"confidence": "low", "reason": "No pricing data available"}
        
        try:
            last_update = datetime.fromisoformat(self.last_updated)
            age_days = (datetime.now() - last_update).days
            
            if age_days == 0:
                confidence = "high"
                message = "Pricing updated today"
            elif age_days <= 7:
                confidence = "high"
                message = f"Pricing updated {age_days} days ago"
            elif age_days <= 30:
                confidence = "medium" 
                message = f"Pricing updated {age_days} days ago - may have changed"
            else:
                confidence = "low"
                message = f"Pricing is {age_days} days old - likely outdated"
            
            return {
                "confidence": confidence,
                "message": message,
                "last_updated": self.last_updated,
                "age_days": age_days
            }
        except Exception:
            return {"confidence": "low", "reason": "Invalid pricing timestamp"}
    
    def estimate_monthly_cost(self, daily_queries: int, avg_input_tokens: int, 
                            avg_output_tokens: int, provider: str, 
                            model: str = None) -> Dict[str, Any]:
        """
        Estimate monthly costs based on usage patterns.
        
        Useful for budget planning and provider comparison.
        """
        daily_cost = self.estimate_cost(avg_input_tokens, avg_output_tokens, provider, model)
        
        if daily_cost.get("total_cost", 0) == 0:
            return {
                "daily_cost": 0,
                "monthly_cost": 0,
                "provider": provider,
                "model": model,
                "note": "Free or pricing unavailable"
            }
        
        daily_total = daily_cost["total_cost"] * daily_queries
        monthly_total = daily_total * 30
        
        return {
            "daily_queries": daily_queries,
            "avg_tokens_per_query": avg_input_tokens + avg_output_tokens,
            "cost_per_query": round(daily_cost["total_cost"], 6),
            "daily_cost": round(daily_total, 2),
            "monthly_cost": round(monthly_total, 2),
            "provider": provider,
            "model": model,
            "breakdown": daily_cost,
            "estimated_at": datetime.now().isoformat()
        }
    
    def track_price_change(self, provider: str, model: str, 
                          old_price: Dict[str, float], new_price: Dict[str, float]):
        """
        Track a price change for historical analysis.
        
        This helps users understand how pricing volatility affects their costs.
        """
        change_record = {
            "provider": provider,
            "model": model,
            "old_price": old_price,
            "new_price": new_price,
            "change_date": datetime.now().isoformat(),
            "change_percentage": {}
        }
        
        # Calculate percentage changes
        for price_type in ["input", "output"]:
            if price_type in old_price and price_type in new_price:
                old_val = old_price[price_type]
                new_val = new_price[price_type]
                if old_val > 0:
                    change_pct = ((new_val - old_val) / old_val) * 100
                    change_record["change_percentage"][price_type] = round(change_pct, 2)
        
        # Save to history
        history_file = self.history_dir / f"price_changes_{datetime.now().strftime('%Y_%m')}.json"
        
        changes = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    changes = json.load(f)
            except Exception:
                changes = []
        
        changes.append(change_record)
        
        with open(history_file, 'w') as f:
            json.dump(changes, f, indent=2)
        
        return change_record