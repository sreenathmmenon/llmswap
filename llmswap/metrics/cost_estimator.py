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
                with open(self.pricing_file, "r") as f:
                    data = json.load(f)
                    if data.get("version") != "5.6.0":
                        self._initialize_default_pricing()
                    else:
                        self.pricing = data.get("pricing", {})
                        self.last_updated = data.get("last_updated")
            except Exception:
                self._initialize_default_pricing()
        else:
            self._initialize_default_pricing()

    def _initialize_default_pricing(self):
        """Initialize with default pricing audited on 2026-08-03."""
        # These prices will be automatically updated when online
        self.pricing = {
            "openai": {
                "gpt-5.6": {"input": 0.005, "output": 0.030},
                "gpt-5.6-terra": {"input": 0.0025, "output": 0.015},
                "gpt-5.6-luna": {"input": 0.001, "output": 0.006},
                "gpt-5.5": {"input": 0.005, "output": 0.030},
                "gpt-5.4": {"input": 0.0025, "output": 0.015},
                "gpt-5.4-mini": {"input": 0.00075, "output": 0.0045},
                "gpt-4.1": {"input": 0.002, "output": 0.008},
            },
            "anthropic": {
                "claude-fable-5": {"input": 0.010, "output": 0.050},
                "claude-opus-5": {"input": 0.005, "output": 0.025},
                "claude-sonnet-5": {"input": 0.003, "output": 0.015},
                "claude-sonnet-4-6": {"input": 0.003, "output": 0.015},
                "claude-haiku-4-5": {"input": 0.001, "output": 0.005},
            },
            "gemini": {
                "gemini-3.6-flash": {"input": 0.0015, "output": 0.0075},
                "gemini-3.5-flash": {"input": 0.0015, "output": 0.009},
                "gemini-3.5-flash-lite": {"input": 0.0003, "output": 0.0025},
                "gemini-3.1-pro-preview": {"input": 0.002, "output": 0.012},
            },
            "watsonx": {
                "ibm/granite-4-h-small": {
                    "input": 0.0000636,
                    "output": 0.000265,
                },
                "openai/gpt-oss-120b": {"input": 0.000159, "output": 0.000636},
            },
            "groq": {
                "openai/gpt-oss-120b": {
                    "input": 0.00015,
                    "output": 0.0006,
                },
                "openai/gpt-oss-20b": {
                    "input": 0.000075,
                    "output": 0.0003,
                },
                "qwen/qwen3.6-27b": {"input": 0.0006, "output": 0.003},
            },
            "cohere": {
                "command-a-plus-05-2026": {
                    "input": 0,
                    "output": 0,
                },
                "command-a-03-2025": {"input": 0.0025, "output": 0.010},
                "command-a-reasoning-08-2025": {
                    "input": 0.0025,
                    "output": 0.010,
                },
            },
            "perplexity": {
                "sonar": {"input": 0.001, "output": 0.001},
                "sonar-pro": {"input": 0.003, "output": 0.015},
                "sonar-reasoning-pro": {
                    "input": 0.002,
                    "output": 0.008,
                },
                "sonar-deep-research": {
                    "input": 0.002,
                    "output": 0.008,
                },
            },
            "xai": {
                "grok-4.5": {"input": 0.002, "output": 0.006},
                "grok-4.3": {"input": 0.00125, "output": 0.0025},
            },
            "sarvam": {
                "sarvam-105b": {"input": 0.0005, "output": 0.0015},
                "sarvam-30b": {"input": 0.00025, "output": 0.00075},
            },
            "ollama": {"all_models": {"input": 0, "output": 0}},
        }

        self.last_updated = datetime.now().isoformat()
        self._save_pricing()

    def _save_pricing(self):
        """Save current pricing to disk."""
        data = {
            "pricing": self.pricing,
            "last_updated": self.last_updated,
            "version": "5.6.0",
        }

        with open(self.pricing_file, "w") as f:
            json.dump(data, f, indent=2)

    def estimate_cost(
        self, input_tokens: int, output_tokens: int, provider: str, model: str = None
    ) -> Dict[str, Any]:
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
                "error": f"Pricing not available for provider: {provider}",
            }

        if provider == "ollama":
            return {
                "total_cost": 0.0,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "confidence": "high",
                "provider": provider,
                "model": model,
                "note": "Local model - no API costs",
            }

        if provider == "gemini":
            # Check if model uses char-based or token-based pricing
            provider_pricing = self.pricing[provider]
            model_pricing = provider_pricing.get(model) or next(
                iter(provider_pricing.values())
            )
            if "per_char" in model_pricing:
                return self._estimate_gemini_cost(input_tokens, output_tokens, model)
            else:
                return self._estimate_token_based_cost(
                    input_tokens, output_tokens, provider, model
                )

        return self._estimate_token_based_cost(
            input_tokens, output_tokens, provider, model
        )

    def _estimate_token_based_cost(
        self, input_tokens: int, output_tokens: int, provider: str, model: str
    ) -> Dict[str, Any]:
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
            "pricing_date": self.last_updated,
        }

    def _estimate_gemini_cost(
        self, input_tokens: int, output_tokens: int, model: str
    ) -> Dict[str, Any]:
        """Estimate cost for Gemini models."""
        gemini_pricing = self.pricing["gemini"]
        model_key = model if model in gemini_pricing else "gemini-3.6-flash"

        if "input" in gemini_pricing[model_key] and "output" in gemini_pricing[model_key]:
            return self._estimate_token_based_cost(
                input_tokens, output_tokens, "gemini", model_key
            )

        # Convert tokens back to approximate character count
        input_chars = input_tokens * 4  # Rough conversion
        output_chars = output_tokens * 4
        total_chars = input_chars + output_chars

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
            "pricing_date": self.last_updated,
        }

    def compare_provider_costs(
        self,
        input_tokens: int,
        output_tokens: int,
        models: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
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
                "openai": "gpt-5.6",
                "anthropic": "claude-sonnet-5",
                "gemini": "gemini-3.6-flash",
                "cohere": "command-a-plus-05-2026",
                "perplexity": "sonar-pro",  # Main model
                "watsonx": "ibm/granite-4-h-small",
                "groq": "openai/gpt-oss-120b",
                "ollama": "qwen3.5:9b",  # Free local
                "xai": "grok-4.5",
                "sarvam": "sarvam-105b",
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
            savings_percentage = (
                (savings_vs_most_expensive / most_expensive[1] * 100)
                if most_expensive[1] > 0
                else 0
            )
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
            "compared_at": datetime.now().isoformat(),
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
                "age_days": age_days,
            }
        except Exception:
            return {"confidence": "low", "reason": "Invalid pricing timestamp"}

    def estimate_monthly_cost(
        self,
        daily_queries: int,
        avg_input_tokens: int,
        avg_output_tokens: int,
        provider: str,
        model: str = None,
    ) -> Dict[str, Any]:
        """
        Estimate monthly costs based on usage patterns.

        Useful for budget planning and provider comparison.
        """
        daily_cost = self.estimate_cost(
            avg_input_tokens, avg_output_tokens, provider, model
        )

        if daily_cost.get("total_cost", 0) == 0:
            return {
                "daily_cost": 0,
                "monthly_cost": 0,
                "provider": provider,
                "model": model,
                "note": "Free or pricing unavailable",
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
            "estimated_at": datetime.now().isoformat(),
        }

    def track_price_change(
        self,
        provider: str,
        model: str,
        old_price: Dict[str, float],
        new_price: Dict[str, float],
    ):
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
            "change_percentage": {},
        }

        # Calculate percentage changes
        for price_type in ["input", "output"]:
            if price_type in old_price and price_type in new_price:
                old_val = old_price[price_type]
                new_val = new_price[price_type]
                if old_val > 0:
                    change_pct = ((new_val - old_val) / old_val) * 100
                    change_record["change_percentage"][price_type] = round(
                        change_pct, 2
                    )

        # Save to history
        history_file = (
            self.history_dir / f"price_changes_{datetime.now().strftime('%Y_%m')}.json"
        )

        changes = []
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    changes = json.load(f)
            except Exception:
                changes = []

        changes.append(change_record)

        with open(history_file, "w") as f:
            json.dump(changes, f, indent=2)

        return change_record
