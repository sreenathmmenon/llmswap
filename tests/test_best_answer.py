"""Best Answer synthesis, privacy, and failure-path tests."""

import json
import threading
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from llmswap.app import cmd_best
from llmswap.best_answer import (
    BestAnswerResult,
    CandidateAnswer,
    ModelTarget,
    generate_best_answer,
    parse_target,
    synthesize_best_answer,
)
from llmswap.exceptions import BestAnswerError, CrossProviderSharingError
from llmswap.response import LLMResponse


class FakeClient:
    def __init__(self, provider, model, responses):
        self.provider = provider
        self.model = model
        self.responses = list(responses)
        self.prompts = []
        self.lock = threading.Lock()

    def get_current_provider(self):
        return self.provider

    def get_current_model(self):
        return self.model

    def query(self, prompt, **kwargs):
        with self.lock:
            self.prompts.append(prompt)
            response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return LLMResponse(
            content=response,
            provider=self.provider,
            model=self.model,
            usage={"prompt_tokens": 2, "completion_tokens": 3},
        )


def synthesis(answer="Use the combined answer"):
    return json.dumps(
        {
            "best_answer": answer,
            "agreement": ["Both support the main conclusion"],
            "disagreements": ["They differ on timing"],
            "cautions": ["Verify the external dependency"],
            "agreement_level": "medium",
        }
    )


def test_same_provider_multi_draft_produces_structured_best_answer():
    client = FakeClient(
        "openai",
        "gpt-5.6",
        ["Candidate one", "Candidate two", synthesis()],
    )

    result = generate_best_answer(client, "What should we do?", candidate_count=2)

    assert result.best_answer == "Use the combined answer"
    assert result.agreement_level == "medium"
    assert len(result.candidates) == 2
    assert result.cross_provider_sharing is False
    assert result.total_usage == {
        "input_tokens": 6,
        "output_tokens": 9,
        "total_tokens": 15,
    }


def test_cross_provider_synthesis_requires_explicit_consent():
    client = FakeClient("openai", "gpt-5.6", [])

    with pytest.raises(CrossProviderSharingError, match="Explicit consent"):
        generate_best_answer(
            client,
            "Question",
            models=["openai:gpt-5.6", "anthropic:claude-sonnet-5"],
        )


def test_cross_provider_synthesis_with_consent_keeps_candidates_anonymous():
    primary = FakeClient("openai", "gpt-5.6", ["First answer", synthesis()])
    other = FakeClient("anthropic", "claude-sonnet-5", ["Second answer"])
    factory = Mock(return_value=other)

    result = generate_best_answer(
        primary,
        "Question",
        models=["openai:gpt-5.6", "anthropic:claude-sonnet-5"],
        allow_cross_provider_sharing=True,
        client_factory=factory,
    )

    assert result.cross_provider_sharing is True
    assert [item.label for item in result.candidates] == ["A", "B"]
    assert [item.provider for item in result.candidates] == ["openai", "anthropic"]
    judge_prompt = primary.prompts[-1]
    assert '"label": "A"' in judge_prompt
    assert '"label": "B"' in judge_prompt
    assert "anthropic" not in judge_prompt.lower()


def test_partial_failure_requires_two_successful_candidates():
    primary = FakeClient("openai", "gpt-5.6", ["Only successful answer"])
    failing = FakeClient(
        "anthropic", "claude-sonnet-5", [RuntimeError("provider unavailable")]
    )

    with pytest.raises(BestAnswerError, match="at least two successful"):
        generate_best_answer(
            primary,
            "Question",
            models=["openai:gpt-5.6", "anthropic:claude-sonnet-5"],
            allow_cross_provider_sharing=True,
            client_factory=Mock(return_value=failing),
        )


@pytest.mark.parametrize("empty_response", [None, "", "   "])
def test_empty_provider_response_is_a_failed_candidate(empty_response):
    primary = FakeClient("openai", "gpt-5.6", ["Only successful answer"])
    empty = FakeClient("sarvam", "sarvam-105b", [empty_response])

    with pytest.raises(BestAnswerError, match="empty response"):
        generate_best_answer(
            primary,
            "Question",
            models=["openai:gpt-5.6", "sarvam:sarvam-105b"],
            allow_cross_provider_sharing=True,
            client_factory=Mock(return_value=empty),
        )


def test_unstructured_judge_output_is_returned_with_caution():
    client = FakeClient(
        "openai", "gpt-5.6", ["Candidate one", "Candidate two", "Plain final"]
    )

    result = generate_best_answer(client, "Question", candidate_count=2)

    assert result.best_answer == "Plain final"
    assert result.agreement_level == "unknown"
    assert "unstructured" in result.cautions[0]


def test_existing_candidates_can_be_synthesized_without_querying_them_again():
    judge = FakeClient("openai", "gpt-5.6", [synthesis("Reused answers")])
    candidates = [
        CandidateAnswer(
            label="A",
            provider="openai",
            model="gpt-5.6",
            content="First existing answer",
            latency=1.0,
            usage={"total_tokens": 10},
        ),
        CandidateAnswer(
            label="B",
            provider="openai",
            model="gpt-5.6",
            content="Second existing answer",
            latency=1.0,
            usage={"total_tokens": 12},
        ),
    ]

    result = synthesize_best_answer(judge, "Question", candidates)

    assert result.best_answer == "Reused answers"
    assert len(judge.prompts) == 1
    assert result.total_usage["total_tokens"] == 27


def test_empty_judge_response_fails_cleanly():
    client = FakeClient("openai", "gpt-5.6", ["One", "Two", None])

    with pytest.raises(BestAnswerError, match="judge model returned an empty"):
        generate_best_answer(client, "Question", candidate_count=2)


def test_model_target_preserves_colons_inside_model_name():
    assert parse_target("ollama:qwen3.5:9b") == ModelTarget(
        provider="ollama", model="qwen3.5:9b"
    )


def test_llm_client_best_answer_delegates_to_engine():
    from llmswap.client import LLMClient

    client = object.__new__(LLMClient)
    expected = object()
    with patch(
        "llmswap.best_answer.generate_best_answer", return_value=expected
    ) as run:
        result = client.best_answer("Question", candidate_count=2)

    assert result is expected
    run.assert_called_once_with(
        primary_client=client,
        prompt="Question",
        models=None,
        judge=None,
        candidate_count=2,
        allow_cross_provider_sharing=False,
    )


def test_best_answer_cli_prints_customer_facing_sections(capsys):
    result = BestAnswerResult(
        prompt="Question",
        best_answer="Combined answer",
        agreement=["Shared point"],
        disagreements=["Different detail"],
        cautions=["Verify date"],
        agreement_level="medium",
        candidates=[
            CandidateAnswer(
                label="A",
                provider="openai",
                model="gpt-5.6",
                content="Draft",
                latency=0.1,
                usage={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
            )
        ],
        judge_provider="openai",
        judge_model="gpt-5.6",
        cross_provider_sharing=False,
        total_usage={"input_tokens": 2, "output_tokens": 2, "total_tokens": 4},
        latency=0.2,
    )
    client = Mock()
    client.best_answer.return_value = result
    args = SimpleNamespace(
        provider="openai",
        best_model="gpt-5.6",
        format="text",
        quiet=True,
        models=None,
        candidates=2,
        question="Question",
        judge=None,
        allow_cross_provider_sharing=False,
        show_candidates=False,
    )

    with (
        patch("llmswap.app.LLMClient", return_value=client),
        patch("llmswap.best_answer.load_customer_env"),
    ):
        assert cmd_best(args) == 0

    output = capsys.readouterr().out
    assert "BEST ANSWER" in output
    assert "Combined answer" in output
    assert "AGREEMENT" in output
    assert "DISAGREEMENTS" in output
    assert "Cross-provider sharing: no" in output
