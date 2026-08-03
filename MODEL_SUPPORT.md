# Provider and Model Support

Last audited: **2026-08-03** for llmswap **5.6.0**.

LLMSwap has two layers of model support:

1. A provider adapter accepts an explicit model ID and passes it to that provider.
2. The built-in defaults and Arena catalog are a curated set of current models.

The catalog is intentionally conservative: retired models are removed, preview
models are labelled, and locally installed Ollama models are labelled `local`.
Provider availability, account entitlements, regional availability, and prices can
still change independently of an llmswap release.

## Provider defaults

| Provider | Default model | Built-in catalog | Notes |
| --- | --- | ---: | --- |
| Anthropic | `claude-sonnet-5` | 5 models | Tool calling |
| OpenAI | `gpt-5.6` | 7 models | Tool calling |
| Google Gemini | `gemini-3.6-flash` | 4 models | Tool calling; `google-genai` SDK |
| Cohere | `command-a-plus-05-2026` | 3 models | Chat V2 |
| Perplexity | `sonar-pro` | 4 models | Search-grounded chat |
| IBM watsonx | `ibm/granite-4-h-small` | 1 model | Optional `watsonx` extra |
| Groq | `openai/gpt-oss-120b` | 3 models | Tool calling |
| Ollama | `qwen3.5:9b` | 3 models | Local; model must be pulled first |
| xAI | `grok-4.5` | 2 models | Tool calling |
| Sarvam | `sarvam-105b` | 2 models | Indic-language chat |

The exact catalog lives in `llmswap/web/models.py`; defaults live in
`llmswap/provider_registry.py`.

## Compatibility changes in 5.6.0

| Previous built-in model | State found during audit | Replacement |
| --- | --- | --- |
| `claude-sonnet-4-20250514` | Retired 2026-06-15 | `claude-sonnet-5` |
| `claude-opus-4-20250514` | Retired 2026-06-15 | `claude-opus-5` |
| `claude-3-7-sonnet-20250219` | Retired 2026-02-19 | `claude-sonnet-5` |
| `gemini-3-pro-preview` | Shut down 2026-03-09 | `gemini-3.6-flash` |
| `ibm/granite-3-3-8b-instruct` | Withdrawn 2026-02-22 | `ibm/granite-4-h-small` |
| `ibm/granite-3-8b-instruct` | Withdrawn 2026-02-22 | `ibm/granite-4-h-small` |
| `mixtral-8x7b-32768` | Retired 2025-03-20 | `openai/gpt-oss-20b` |
| `command-r` alias | Deprecated 2025-09-15 | `command-a-03-2025` |
| `sarvam-m` | Deprecated; calls fail | `sarvam-30b` or `sarvam-105b` |

Groq's Llama 3.1 and 3.3 entries were also removed from the curated catalog
because their announced shutdown is 2026-08-16. Gemini 2.5 entries were removed
ahead of their announced 2026-10-16 shutdown. Explicit model IDs remain
pass-through values; LLMSwap does not rewrite user-selected models.

## Official sources

- [OpenAI model catalog](https://developers.openai.com/api/docs/models/all)
- [Anthropic model overview](https://platform.claude.com/docs/en/about-claude/models/overview) and [deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)
- [Gemini models](https://ai.google.dev/gemini-api/docs/models), [deprecations](https://ai.google.dev/gemini-api/docs/deprecations), and [pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Cohere models](https://docs.cohere.com/v1/docs/models) and [deprecations](https://docs.cohere.com/docs/deprecations)
- [Perplexity Sonar models](https://docs.perplexity.ai/docs/sonar/models/sonar-pro)
- [IBM watsonx supported models](https://www.ibm.com/docs/en/watsonx/saas?topic=solutions-supported-foundation-models) and [model lifecycle](https://www.ibm.com/docs/en/watsonx/saas?topic=models-foundation-model-lifecycle)
- [Groq models](https://console.groq.com/docs/models) and [deprecations](https://console.groq.com/docs/deprecations)
- [Ollama Qwen 3.5 library entry](https://ollama.com/library/qwen3.5)
- [xAI models](https://docs.x.ai/developers/models) and [Grok 4.5](https://docs.x.ai/developers/models/grok-4.5)
- [Sarvam API changelog](https://docs.sarvam.ai/api/getting-started/changelog) and [chat completions](https://docs.sarvam.ai/api-reference/chat/chat-completions)

## Maintenance checklist

Before changing a default or publishing a release:

1. Verify the exact API model ID in the provider's official model list.
2. Check its lifecycle/deprecation page and choose a stable model by default.
3. Update the registry, Arena catalog, pricing table, examples, and tests together.
4. Confirm every default occurs in the built-in catalog.
5. Run the full test suite and an opt-in live smoke test for configured providers.
