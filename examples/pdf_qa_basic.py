#!/usr/bin/env python3
"""
Simple PDF Question-Answering with RAG (No Tools)
==================================================

This example shows basic RAG pattern:
1. Load PDF document
2. Embed and store in ChromaDB
3. Search for relevant context
4. Query LLM with context

Dependencies:
    pip install chromadb pypdf2 llmswap

Usage:
    python pdf_qa_basic.py path/to/document.pdf "Your question here"
"""

import sys
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
from llmswap import LLMClient


def load_pdf(pdf_path: str) -> list[str]:
    """Extract text from PDF and split into chunks."""
    reader = PdfReader(pdf_path)

    chunks = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        # Add page context to each chunk
        for para in paragraphs:
            chunks.append(f"[Page {page_num + 1}] {para}")

    return chunks


def create_vector_db(chunks: list[str], collection_name: str = "documents"):
    """Create ChromaDB collection and add document chunks."""
    client = chromadb.Client()

    # Use default embedding function
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    # Create collection
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )

    # Add documents
    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

    return collection


def search_documents(collection, query: str, n_results: int = 3) -> str:
    """Search vector DB and return relevant context."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    # Combine top results
    context = "\n\n".join(results['documents'][0])
    return context


def main():
    if len(sys.argv) < 3:
        print("Usage: python pdf_qa_basic.py <pdf_file> <question>")
        print("\nExample:")
        print('  python pdf_qa_basic.py report.pdf "What is the revenue?"')
        sys.exit(1)

    pdf_path = sys.argv[1]
    question = sys.argv[2]

    if not Path(pdf_path).exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    print(f"📄 Loading PDF: {pdf_path}")
    chunks = load_pdf(pdf_path)
    print(f"✅ Extracted {len(chunks)} chunks")

    print("🔍 Creating vector database...")
    collection = create_vector_db(chunks)
    print("✅ Vector DB ready")

    print(f"\n❓ Question: {question}")
    print("🔎 Searching relevant context...")

    context = search_documents(collection, question)
    print(f"✅ Found relevant context ({len(context)} chars)")

    # Build prompt with context
    prompt = f"""Based on the following context from the document, answer the question.
If the answer is not in the context, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:"""

    print("🤖 Querying LLM...")
    client = LLMClient(provider="anthropic")  # or "openai", "gemini"
    response = client.query(prompt)

    print(f"\n✨ Answer:\n{response.content}\n")


if __name__ == "__main__":
    main()
