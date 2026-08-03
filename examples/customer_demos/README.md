# Real Customer Demo Projects

These three small products make real LLMSwap requests and are designed for live
demonstrations. They use OpenAI `gpt-5.6` by default and load `OPENAI_API_KEY`
from the environment or `~/.env`.

Install and configure:

```bash
python -m venv .venv
source .venv/bin/activate
pip install llmswap
```

Add `OPENAI_API_KEY=...` to `~/.env`, then run any demo from the repository root:

```bash
python examples/customer_demos/support_triage/triage.py
python examples/customer_demos/product_feedback/feedback_analyst.py
python examples/customer_demos/mcp_account_agent/account_agent.py
```

The MCP demo additionally requires Node.js/npm because it launches
`@modelcontextprotocol/server-filesystem` through `npx`.

Each project reads the included sample data, prints its result, and saves a
generated artifact under that project's ignored `outputs/` directory.
