"""Turn customer-support tickets into a structured triage queue."""

import json
from pathlib import Path

import llmswap
from dotenv import load_dotenv
from llmswap import LLMClient


PROJECT_DIR = Path(__file__).resolve().parent


def parse_json_array(text: str) -> list:
    """Extract JSON if a provider surrounds it with Markdown."""
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"The model did not return a JSON array: {text}")
    return json.loads(text[start : end + 1])


def main() -> None:
    load_dotenv(Path.home() / ".env", override=False)
    tickets = json.loads((PROJECT_DIR / "tickets.json").read_text())
    prompt = f"""
You are a support operations lead. Triage these customer tickets:
{json.dumps(tickets, indent=2)}

Return only a JSON array. Each object must contain ticket_id, category,
priority (Critical, High, Medium, or Low), sentiment, and one next_action.
Preserve every ticket_id and do not add tickets.
""".strip()

    client = LLMClient(
        provider="openai",
        model="gpt-5.6",
        fallback=False,
        cache_enabled=True,
        workspace_enabled=False,
    )
    first = client.query(prompt)
    cached = client.query(prompt)
    report = {
        "llmswap_version": llmswap.__version__,
        "provider": first.provider,
        "model": first.model,
        "usage": first.usage,
        "cache_verified": cached.from_cache,
        "triage": parse_json_array(first.content),
    }

    output = PROJECT_DIR / "outputs" / "triage_report.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")

    print(f"LLMSwap {llmswap.__version__} | {first.provider} | {first.model}")
    for item in report["triage"]:
        print(f"{item['ticket_id']}: {item['priority']} — {item['category']}")
        print(f"  Next: {item['next_action']}")
    print(f"Cache verified: {cached.from_cache}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
