"""Stream a weekly product brief from customer feedback."""

import asyncio
import json
from pathlib import Path

import llmswap
from dotenv import load_dotenv
from llmswap import AsyncLLMClient


PROJECT_DIR = Path(__file__).resolve().parent


async def main() -> None:
    load_dotenv(Path.home() / ".env", override=False)
    reviews = json.loads((PROJECT_DIR / "reviews.json").read_text())
    prompt = f"""
You are a product manager reviewing this customer feedback:
{json.dumps(reviews, indent=2)}

Write a Markdown brief with headings Executive Summary, Top Themes, and
Recommended Next Steps. Rank three themes and give three concrete actions.
Use only supplied feedback and stay under 220 words.
""".strip()

    client = AsyncLLMClient(
        provider="openai",
        model="gpt-5.6",
        fallback=False,
        workspace_enabled=False,
    )
    chunks = []
    print(f"LLMSwap {llmswap.__version__} | openai | gpt-5.6\n")
    async for chunk in client.stream(prompt):
        chunks.append(chunk)
        print(chunk, end="", flush=True)

    output = PROJECT_DIR / "outputs" / "product_brief.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(chunks).strip() + "\n")
    print(f"\n\nStreaming chunks: {len(chunks)}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    asyncio.run(main())
