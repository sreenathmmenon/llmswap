# Security policy

## Reporting a vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability
reporting for this repository. Do not include live API keys, customer prompts,
provider responses, or other sensitive data in a public issue.

For ordinary bugs and feature requests, use the public issue tracker.

## Data flow

LLMSwap is a local client, not a hosted relay operated by the project. A normal
remote-provider request follows this path:

```text
Your process -> LLMSwap -> provider API selected by you
```

Your prompt and any supplied tool results are sent to that provider. Provider
retention, training, regional, and compliance terms are controlled by your
provider account and contract. Ollama requests can remain local when the Ollama
server itself is local.

Provider clients read API keys from environment variables. Best Answer and
`doctor` additionally discover a project `.env` or `~/.env` without overriding
exported values. Keep those files outside version control and restrict their
file permissions. Diagnostic output reports whether a key exists but does not
print its value.

## Best Answer

Best Answer has two phases:

```text
Prompt -> 2–5 candidate requests (parallel)
       -> anonymized candidate text + original prompt -> judge request
       -> Best Answer + agreement + disagreements + cautions
```

By default, candidates and judge use the same provider/model. If selected
candidates would cause their outputs to be sent to a judge on another provider,
LLMSwap stops unless `allow_cross_provider_sharing=True` or
`--allow-cross-provider-sharing` is explicitly set.

Candidate names are replaced with neutral labels before judging and candidate
text is delimited and treated as untrusted data in the synthesis prompt. This
reduces bias and prompt-injection risk but does not eliminate it. LLMSwap does
not automatically redact personal, confidential, regulated, or secret content.
Do not use cross-provider mode for data that every selected provider is not
authorized to receive.

Model agreement is not a factual guarantee. For medical, legal, financial,
safety-critical, or other high-impact decisions, verify claims against primary
sources and use qualified human review.

## MCP and tools

An MCP server or tool can read data or perform actions with the permissions of
the process running it. Use trusted MCP servers, inspect their source and
requested arguments, grant the narrowest filesystem/network permissions, and
avoid exposing credential directories. Local stdio MCP is the verified path;
legacy remote transport support remains experimental.

Tool output is untrusted input to the model. Validate tool arguments before
execution and validate model-produced data before it reaches a sensitive system.

## Logs, cache, and workspace files

Prompts, responses, tool results, and project context may be sensitive. Review
local cache, analytics, logs, and `.llmswap/` workspace files before sharing a
project or diagnostic artifact. Add `.env` and any sensitive workspace or
generated output files to source-control ignore rules as appropriate.

## Dependency and release hygiene

- Install from the official `llmswap` PyPI project or this repository.
- Pin versions in controlled environments and review release notes before
  upgrading.
- Run `llmswap doctor` after installation; use `--live` only when real provider
  calls are acceptable.
- Keep provider SDKs and MCP servers current, and remove credentials that are no
  longer required.
