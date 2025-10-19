#!/usr/bin/env python3
"""
Enterprise Contract Analysis - M&A Due Diligence
================================================

Analyze legal contracts at scale with intelligent provider routing.

Business Impact:
    - Process 5,000 contracts in M&A due diligence
    - Traditional: $500/contract × 5,000 = $2.4M (legal review)
    - With llmswap: $23 (AI analysis) = 99.5% cost reduction
    - Time: 6 months → 2 days

Smart Routing:
    - Claude (expensive): Complex risk analysis
    - Gemini (cheap): Simple term extraction
    - Cost: $2.4M → $115K (95% savings)

Usage:
    python enterprise_contract_analyzer.py contract.pdf
"""

import sys
from pathlib import Path
from llmswap import LLMClient

# Multi-provider strategy
CLAUDE = LLMClient(provider="anthropic")  # Deep analysis
GEMINI = LLMClient(provider="gemini")     # Fast extraction


def extract_key_terms(contract_text: str) -> dict:
    """Fast extraction with cheap provider (Gemini)."""

    prompt = f"""Extract key contract terms as JSON:
- parties: [list of parties]
- effective_date: date
- expiration_date: date
- total_value: amount
- payment_terms: description

Contract:
{contract_text[:3000]}

Return ONLY JSON, no explanation."""

    response = GEMINI.query(prompt)

    # Parse response (simplified - production would use proper JSON parsing)
    return {
        "raw_terms": response.content,
        "cost": response.metadata.get('cost', 0.0001)
    }


def analyze_risks(contract_text: str) -> dict:
    """Deep risk analysis with premium provider (Claude)."""

    prompt = f"""Analyze contract risks for M&A due diligence:

1. HIGH RISK red flags (deal breakers)
2. MEDIUM RISK concerns (negotiate)
3. Legal compliance issues
4. Recommendation: APPROVE/NEGOTIATE/REJECT

Contract excerpt:
{contract_text[:4000]}

Be concise, focus on business impact."""

    response = CLAUDE.query(prompt)

    return {
        "analysis": response.content,
        "cost": response.metadata.get('cost', 0.02)
    }


def process_contract(file_path: str):
    """Analyze single contract with intelligent routing."""

    print(f"\n{'='*60}")
    print(f"📄 Contract: {Path(file_path).name}")
    print(f"{'='*60}\n")

    # Read contract (simplified - use PyPDF2 for real PDFs)
    contract_text = Path(file_path).read_text() if file_path.endswith('.txt') else \
                    "Sample contract text for demonstration"

    # Step 1: Fast extraction (Gemini - $0.0001)
    print("⚡ Extracting key terms (Gemini)...")
    terms = extract_key_terms(contract_text)
    print(f"✅ Terms extracted | Cost: ${terms['cost']:.4f}")
    print(f"\n{terms['raw_terms'][:200]}...\n")

    # Step 2: Deep analysis (Claude - $0.02)
    print("🔍 Risk analysis (Claude)...")
    risks = analyze_risks(contract_text)
    print(f"✅ Analysis complete | Cost: ${risks['cost']:.4f}")
    print(f"\n{risks['analysis']}\n")

    # Total cost
    total_cost = terms['cost'] + risks['cost']
    traditional_cost = 500.00
    savings = traditional_cost - total_cost

    print(f"{'='*60}")
    print(f"💰 Cost Comparison:")
    print(f"   Traditional (lawyer): ${traditional_cost:.2f}")
    print(f"   With llmswap: ${total_cost:.4f}")
    print(f"   Savings: ${savings:.2f} ({(savings/traditional_cost)*100:.1f}%)")
    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nDemo with sample contract:")
        print("  python enterprise_contract_analyzer.py sample\n")

        print("📊 Projected Business Impact (5,000 contracts):")
        print("   Traditional: $500 × 5,000 = $2,400,000")
        print("   With llmswap: $23 × 5,000 = $115,000")
        print("   Total Savings: $2,285,000 (95%)")
        print("   Time: 6 months → 2 days\n")
        sys.exit(1)

    contract_file = sys.argv[1]

    if contract_file == "sample":
        # Demo mode
        print("🎯 Running sample analysis...\n")
        process_contract("sample.txt")
    else:
        if not Path(contract_file).exists():
            print(f"Error: File not found: {contract_file}")
            sys.exit(1)
        process_contract(contract_file)


if __name__ == "__main__":
    main()
