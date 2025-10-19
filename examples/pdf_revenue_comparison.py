#!/usr/bin/env python3
"""
Agentic RAG: Compare Company Revenues from Quarterly Reports
==============================================================

This example demonstrates agentic RAG with tool calling:
- LLM decides which documents to search
- Multi-hop reasoning (search → extract → compare)
- Works with ANY LLM provider (Anthropic, OpenAI, Gemini, Groq, xAI)

Use Case:
    Compare financial metrics from multiple company quarterly reports.
    Example: "Which company had higher revenue in Q3 2024: Tesla or Ford?"

Dependencies:
    pip install chromadb pypdf2 llmswap

Usage:
    # Download quarterly reports first:
    # Tesla Q3 2024: https://ir.tesla.com/sec-filings
    # Ford Q3 2024: https://shareholder.ford.com/Investors/financials/quarterly-results/default.aspx

    python pdf_revenue_comparison.py tesla_q3_2024.pdf ford_q3_2024.pdf

Example Questions:
    - "Which company had higher revenue?"
    - "What was Tesla's operating income?"
    - "Compare the gross profit margins"
    - "What are the year-over-year growth rates?"
"""

import sys
import json
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
from llmswap import LLMClient, Tool


# Global storage for vector databases
DOCUMENT_COLLECTIONS = {}


def load_pdf_to_vectordb(pdf_path: str, company_name: str):
    """Load PDF and create vector database for searching."""
    reader = PdfReader(pdf_path)

    chunks = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        for para in paragraphs:
            chunks.append(f"[{company_name} - Page {page_num + 1}] {para}")

    # Create ChromaDB collection
    client = chromadb.Client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name=f"{company_name.lower()}_docs",
        embedding_function=embedding_fn
    )

    collection.add(
        documents=chunks,
        ids=[f"{company_name}_chunk_{i}" for i in range(len(chunks))]
    )

    DOCUMENT_COLLECTIONS[company_name] = collection
    print(f"✅ Loaded {len(chunks)} chunks from {company_name} report")


def search_company_document(company: str, query: str) -> str:
    """
    Tool function: Search a specific company's quarterly report.

    Args:
        company: Company name (e.g., "Tesla", "Ford")
        query: Search query (e.g., "revenue", "operating income")

    Returns:
        Relevant excerpts from the company's report
    """
    if company not in DOCUMENT_COLLECTIONS:
        return f"Error: No document loaded for {company}. Available: {list(DOCUMENT_COLLECTIONS.keys())}"

    collection = DOCUMENT_COLLECTIONS[company]
    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    # Return top results
    excerpts = "\n\n".join(results['documents'][0])
    return f"Results from {company} report:\n{excerpts}"


def calculate(expression: str) -> str:
    """
    Tool function: Perform mathematical calculations.

    Args:
        expression: Math expression (e.g., "125.6 - 112.3")

    Returns:
        Calculation result
    """
    try:
        # Safe eval for basic math
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    # Parse command line
    company1_pdf = sys.argv[1]
    company2_pdf = sys.argv[2]

    # Extract company names from filenames
    company1 = Path(company1_pdf).stem.split('_')[0].title()
    company2 = Path(company2_pdf).stem.split('_')[0].title()

    print(f"📊 Company Revenue Comparison Agent")
    print(f"="*50)
    print(f"Company A: {company1}")
    print(f"Company B: {company2}")
    print()

    # Load both PDFs into vector databases
    print("📄 Loading quarterly reports...")
    load_pdf_to_vectordb(company1_pdf, company1)
    load_pdf_to_vectordb(company2_pdf, company2)
    print()

    # Define tools for the LLM
    search_tool = Tool(
        name="search_company_document",
        description=f"Search quarterly reports. Available companies: {company1}, {company2}. Use this to find financial metrics like revenue, income, expenses, etc.",
        parameters={
            "company": {
                "type": "string",
                "description": f"Company name: either '{company1}' or '{company2}'"
            },
            "query": {
                "type": "string",
                "description": "What to search for (e.g., 'total revenue', 'operating income', 'gross profit')"
            }
        },
        required=["company", "query"]
    )

    calculator_tool = Tool(
        name="calculate",
        description="Perform mathematical calculations for comparing numbers or computing percentages",
        parameters={
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate (e.g., '(125.6 - 112.3) / 112.3 * 100' for percentage change)"
            }
        },
        required=["expression"]
    )

    # Initialize LLM client (works with any provider)
    client = LLMClient(provider="anthropic")  # Try: "openai", "gemini", "groq", "xai"

    # Interactive loop
    print("🤖 Agent ready! Ask questions about the reports.")
    print("Examples:")
    print(f'  - "Which company had higher revenue?"')
    print(f'  - "What was {company1}\'s operating income?"')
    print(f'  - "Compare their gross profit margins"')
    print()
    print("Type 'exit' to quit\n")

    while True:
        question = input("❓ Your question: ").strip()

        if question.lower() in ['exit', 'quit', 'q']:
            break

        if not question:
            continue

        print("\n🔄 Agent thinking...\n")

        # Build conversation
        messages = [
            {"role": "user", "content": question}
        ]

        # Agent loop: LLM can call tools multiple times
        max_iterations = 5
        for iteration in range(max_iterations):
            # Call LLM with tools
            response = client.chat(messages, tools=[search_tool, calculator_tool])

            # Check if LLM wants to use tools
            tool_calls = response.metadata.get('tool_calls', [])

            if not tool_calls:
                # No more tools to call, LLM has final answer
                print(f"✨ Answer:\n{response.content}\n")
                print("-" * 50 + "\n")
                break

            # Execute tool calls
            for tool_call in tool_calls:
                tool_name = tool_call.name
                tool_args = tool_call.arguments

                print(f"🔧 Using tool: {tool_name}")
                print(f"   Args: {json.dumps(tool_args, indent=2)}")

                # Execute the tool
                if tool_name == "search_company_document":
                    result = search_company_document(
                        tool_args.get("company"),
                        tool_args.get("query")
                    )
                elif tool_name == "calculate":
                    result = calculate(tool_args.get("expression"))
                else:
                    result = f"Unknown tool: {tool_name}"

                print(f"   Result: {result[:200]}...")
                print()

                # Add tool result to conversation (format depends on provider)
                # For Anthropic:
                if hasattr(tool_call, 'id'):
                    messages.append({
                        "role": "assistant",
                        "content": [
                            {"type": "tool_use", "id": tool_call.id, "name": tool_name, "input": tool_args}
                        ]
                    })
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "tool_result", "tool_use_id": tool_call.id, "content": result}
                        ]
                    })
        else:
            print("⚠️  Max iterations reached. Agent might need more steps.")
            print()


if __name__ == "__main__":
    main()
