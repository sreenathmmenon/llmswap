"""Generate one cross-checked answer from independent LLM responses."""

import argparse
from pathlib import Path

from dotenv import load_dotenv

from llmswap import LLMClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="+", help="Question to answer")
    parser.add_argument("--provider", default="openai", help="Primary provider")
    parser.add_argument("--model", help="Primary model override")
    parser.add_argument(
        "--models",
        nargs="+",
        help="Explicit provider:model candidates (two to five)",
    )
    parser.add_argument(
        "--allow-cross-provider-sharing",
        action="store_true",
        help="Allow candidate outputs to be sent to another provider for synthesis",
    )
    args = parser.parse_args()

    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv(Path.home() / ".env", override=False)

    client = LLMClient(
        provider=args.provider,
        model=args.model,
        fallback=False,
        cache_enabled=False,
        workspace_enabled=False,
    )
    result = client.best_answer(
        " ".join(args.question),
        models=args.models,
        candidate_count=3,
        allow_cross_provider_sharing=args.allow_cross_provider_sharing,
    )

    print(result.best_answer)
    print(f"\nAgreement: {result.agreement_level}")
    for caution in result.cautions:
        print(f"Caution: {caution}")
    print(f"Total tokens: {result.total_usage['total_tokens']}")


if __name__ == "__main__":
    main()
