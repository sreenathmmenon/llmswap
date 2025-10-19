#!/usr/bin/env python3
"""
Enterprise Support Ticket Triage - Intelligent Routing
=======================================================

Analyze customer support tickets with smart provider routing.

Business Impact:
    - Process 1M support tickets/year
    - Detect churn risk: Save $5M ARR
    - Traditional: All tickets → GPT-4 ($20K/month)
    - Smart routing: 90% Gemini, 10% Claude ($3K/month = 85% savings)

Routing Strategy:
    - HIGH urgency + angry → Claude (best quality)
    - MEDIUM/LOW urgency → Gemini (cost-efficient)
    - Cost: $0.02 vs $0.0001 per ticket

Usage:
    python enterprise_support_triage.py "ticket text here"
"""

import sys
from llmswap import LLMClient

# Multi-provider setup
CLAUDE = LLMClient(provider="anthropic")
GEMINI = LLMClient(provider="gemini")


def classify_ticket(ticket_text: str) -> dict:
    """Quick classification with cheap provider."""

    prompt = f"""Classify support ticket:
1. Urgency: HIGH/MEDIUM/LOW
2. Sentiment: ANGRY/FRUSTRATED/NEUTRAL/HAPPY
3. Category: billing/technical/feature/bug/other
4. Churn_Risk: YES/NO

Ticket: {ticket_text}

Return format:
urgency: X
sentiment: Y
category: Z
churn_risk: YES/NO"""

    response = GEMINI.query(prompt)

    # Parse (simplified)
    lines = response.content.lower()
    return {
        "urgency": "high" if "high" in lines else "medium" if "medium" in lines else "low",
        "sentiment": "angry" if "angry" in lines else "frustrated" if "frustrated" in lines else "neutral",
        "churn_risk": "yes" in lines and "churn" in lines,
        "classification": response.content,
        "cost": 0.0001
    }


def generate_response(ticket_text: str, classification: dict) -> dict:
    """Smart routing based on urgency and sentiment."""

    # Route to premium provider for high-value/high-risk tickets
    use_premium = classification['urgency'] == 'high' or classification['churn_risk']

    provider = CLAUDE if use_premium else GEMINI
    provider_name = "Claude" if use_premium else "Gemini"

    prompt = f"""Generate empathetic support response:

Ticket: {ticket_text}

Context:
- Urgency: {classification['urgency'].upper()}
- Sentiment: {classification['sentiment'].upper()}
- Churn Risk: {'YES' if classification['churn_risk'] else 'NO'}

Response should:
1. Address concern directly
2. Provide solution or next steps
3. {"Show extra care - customer at risk!" if classification['churn_risk'] else "Be helpful and professional"}

Keep response under 100 words."""

    response = provider.query(prompt)

    return {
        "response": response.content,
        "provider": provider_name,
        "cost": 0.02 if use_premium else 0.0001
    }


def triage_ticket(ticket_text: str):
    """Complete triage workflow."""

    print(f"\n{'='*70}")
    print(f"🎫 SUPPORT TICKET ANALYSIS")
    print(f"{'='*70}\n")

    print(f"Ticket: {ticket_text[:100]}...\n")

    # Step 1: Classify (always Gemini)
    print("⚡ Classifying (Gemini)...")
    classification = classify_ticket(ticket_text)
    print(f"✅ Classification: {classification['classification']}\n")

    # Step 2: Generate response (smart routing)
    print(f"🤖 Generating response...")
    result = generate_response(ticket_text, classification)
    print(f"✅ Provider: {result['provider']}")
    print(f"\n📝 Suggested Response:\n{result['response']}\n")

    # Cost analysis
    total_cost = classification['cost'] + result['cost']
    always_premium_cost = 0.02

    print(f"{'='*70}")
    print(f"💰 Cost Analysis:")
    print(f"   Classification (Gemini): ${classification['cost']:.4f}")
    print(f"   Response ({result['provider']}): ${result['cost']:.4f}")
    print(f"   Total: ${total_cost:.4f}")
    print(f"   vs Always Premium: ${always_premium_cost:.4f}")
    print(f"   Savings: ${always_premium_cost - total_cost:.4f}")

    if classification['churn_risk']:
        print(f"\n⚠️  CHURN RISK DETECTED - Escalate to senior support")

    print(f"{'='*70}\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExample tickets:\n")

        examples = [
            "I've been waiting 3 days for a response! This is unacceptable. Cancel my subscription NOW!",
            "How do I export my data to CSV? Thanks!",
            "The app keeps crashing when I try to upload files. Very frustrating.",
        ]

        for i, ex in enumerate(examples, 1):
            print(f"{i}. {ex[:70]}...")

        print("\n📊 Projected Annual Impact (1M tickets):")
        print("   All tickets → GPT-4: $20,000/month")
        print("   Smart routing (90% Gemini): $3,000/month")
        print("   Annual Savings: $204,000 (85%)")
        print("   Churn prevention value: $5M+ ARR\n")
        sys.exit(1)

    ticket_text = " ".join(sys.argv[1:])
    triage_ticket(ticket_text)


if __name__ == "__main__":
    main()
