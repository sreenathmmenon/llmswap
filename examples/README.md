# LLMSwap examples

Runnable examples for learning the SDK and validating LLMSwap as a real
customer. Run commands from the repository root with the same Python environment
where LLMSwap is installed.

```bash
python -m pip install -e ".[web]"
llmswap doctor
```

If the package is installed in the repository virtual environment, resolve its
full Python path before changing directories:

```bash
"$(pwd)/.venv/bin/python" "$(pwd)/examples/basic_usage.py"
```

## Best Answer

Create a cross-checked result from three independent same-provider drafts:

```bash
python examples/best_answer.py \
  "Which rollout plan has the lowest operational risk?"
```

Choose distinct providers and explicitly consent to sharing candidate output
with the judge provider:

```bash
python examples/best_answer.py "Compare these options" \
  --models openai:gpt-5.6 sarvam:sarvam-105b \
  --allow-cross-provider-sharing
```

The script prints the Best Answer, agreement, disagreements, cautions, usage,
and latency. Use `python examples/best_answer.py --help` for all options.

## Customer-validation mini-products

The [`customer_demos/`](customer_demos/) directory contains three small but
complete workflows with sample input data:

### Support triage

Reads support tickets, sends each ticket to LLMSwap, parses the structured
response, and writes a triage report.

```bash
python examples/customer_demos/support_triage/triage.py
```

### Product-feedback analyst

Reads customer reviews and streams an analysis through `AsyncLLMClient`.

```bash
python examples/customer_demos/product_feedback/feedback_analyst.py
```

### MCP account agent

Starts a local filesystem MCP server and lets OpenAI inspect the included sample
account files using natural language tool selection.

```bash
python examples/customer_demos/mcp_account_agent/account_agent.py
```

This example requires Node.js/npm because it launches
`@modelcontextprotocol/server-filesystem` with `npx`.

See [`customer_demos/README.md`](customer_demos/README.md) for each input,
output artifact, and individual run command.

## SDK basics

```bash
python examples/basic_usage.py
python examples/basic/simple_query.py
python examples/basic/provider_switching.py
python examples/basic/streaming.py
```

Other focused scripts:

- [`01_weather_api.py`](01_weather_api.py): provider tool schema for a weather function
- [`02_database_query.py`](02_database_query.py): natural-language database query pattern
- [`03_ecommerce_assistant.py`](03_ecommerce_assistant.py): product-search assistant pattern
- [`code_reviewer.py`](code_reviewer.py): file review
- [`debug_helper.py`](debug_helper.py): error analysis
- [`log_analyzer.py`](log_analyzer.py): operational log analysis
- [`provider_comparison.py`](provider_comparison.py): compare configured providers
- [`smart_cost_optimizer.py`](smart_cost_optimizer.py): cost-routing example
- [`latest_models_aug_2026.py`](latest_models_aug_2026.py): audited 5.7.0 defaults
- [`gemini_3_multimodal.py`](gemini_3_multimodal.py): Gemini multimodal flow
- [`pdf_qa_basic.py`](pdf_qa_basic.py): PDF question answering
- [`enterprise_contract_analyzer.py`](enterprise_contract_analyzer.py): contract analysis workflow

Examples make real provider calls unless their source says otherwise. Provider
billing, data handling, and rate limits apply. Use sample data rather than
sensitive production data when evaluating a new workflow.
