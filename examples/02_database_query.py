#!/usr/bin/env python3
"""
Example 2: Database Query Tool

Demonstrates accessing YOUR database - something LLM cannot do without tools.

WITHOUT tools: LLM says "I don't have access to your database"
WITH tools: LLM queries YOUR database and returns actual results
"""

from llmswap import LLMClient, Tool
import sqlite3
import os


def setup_demo_database():
    """Create a demo database with sample data."""
    db_path = "/tmp/demo_store.db"

    # Remove old database if exists
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            total_orders INTEGER,
            lifetime_value REAL
        )
    """)

    # Insert sample data
    customers = [
        (1, "Alice Johnson", "alice@email.com", 15, 2450.00),
        (2, "Bob Smith", "bob@email.com", 8, 890.50),
        (3, "Carol White", "carol@email.com", 23, 4200.00),
        (4, "David Brown", "david@email.com", 3, 180.00),
        (5, "Eve Davis", "eve@email.com", 31, 5100.00),
    ]

    cursor.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
        customers
    )

    conn.commit()
    conn.close()

    return db_path


def create_database_tool():
    """Create database query tool."""
    return Tool(
        name="query_customer_database",
        description="Query customer database to get information about customers, orders, and sales",
        parameters={
            "question": {
                "type": "string",
                "description": "Natural language question about customers (e.g., 'top customers', 'total customers', 'customer with most orders')"
            }
        },
        required=["question"]
    )


def query_customer_database(question: str, db_path: str) -> str:
    """
    Query YOUR customer database.

    LLM cannot access this data without your tool!
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Simple logic to convert question to SQL
        # In production, you'd use more sophisticated query generation
        question_lower = question.lower()

        if "top" in question_lower and "customer" in question_lower:
            cursor.execute("""
                SELECT name, lifetime_value, total_orders
                FROM customers
                ORDER BY lifetime_value DESC
                LIMIT 5
            """)
            results = cursor.fetchall()
            response = "Top customers by lifetime value:\n"
            for name, value, orders in results:
                response += f"- {name}: ${value:.2f} ({orders} orders)\n"

        elif "how many" in question_lower or "total customer" in question_lower:
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0]
            response = f"Total customers: {count}"

        elif "most orders" in question_lower:
            cursor.execute("""
                SELECT name, total_orders, lifetime_value
                FROM customers
                ORDER BY total_orders DESC
                LIMIT 1
            """)
            name, orders, value = cursor.fetchone()
            response = f"Customer with most orders: {name} ({orders} orders, ${value:.2f} lifetime value)"

        elif "total revenue" in question_lower or "total sales" in question_lower:
            cursor.execute("SELECT SUM(lifetime_value) FROM customers")
            total = cursor.fetchone()[0]
            response = f"Total revenue from all customers: ${total:.2f}"

        else:
            # Default: return all customers
            cursor.execute("SELECT name, email, total_orders, lifetime_value FROM customers")
            results = cursor.fetchall()
            response = "All customers:\n"
            for name, email, orders, value in results:
                response += f"- {name} ({email}): {orders} orders, ${value:.2f}\n"

        conn.close()
        return response

    except Exception as e:
        return f"Error querying database: {str(e)}"


def demonstrate_without_tools(db_path: str):
    """Show what happens WITHOUT tool calling."""
    print("\n" + "="*60)
    print("WITHOUT Tool Calling")
    print("="*60)

    client = LLMClient(provider="anthropic")

    # Ask about YOUR database
    response = client.chat("Who are my top 5 customers by revenue?")

    print(f"\nUser: Who are my top 5 customers by revenue?")
    print(f"\nLLM: {response.content}")
    print(f"\n❌ Problem: LLM doesn't have access to YOUR database!")


def demonstrate_with_tools(db_path: str):
    """Show what happens WITH tool calling."""
    print("\n" + "="*60)
    print("WITH Tool Calling")
    print("="*60)

    client = LLMClient(provider="anthropic")
    db_tool = create_database_tool()

    # Ask about YOUR database
    user_query = "Who are my top 5 customers by revenue?"
    print(f"\nUser: {user_query}")

    response = client.chat(user_query, tools=[db_tool])

    # Check if LLM wants to use the tool
    tool_calls = response.metadata.get('tool_calls', [])

    if not tool_calls:
        print(f"\nLLM: {response.content}")
        return

    # LLM called the database tool!
    tool_call = tool_calls[0]
    print(f"\n[LLM called: {tool_call.name}]")
    print(f"[Question: {tool_call.arguments['question']}]")

    # Execute YOUR function to query YOUR database
    db_results = query_customer_database(
        tool_call.arguments['question'],
        db_path
    )
    print(f"\n[Your Database returned:]")
    print(db_results)

    # Send result back to LLM for natural language response
    messages = [
        {"role": "user", "content": user_query},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": tool_call.id,
             "name": tool_call.name, "input": tool_call.arguments}
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tool_call.id, "content": db_results}
        ]}
    ]

    final_response = client.chat(messages, tools=[db_tool])
    print(f"\nLLM: {final_response.content}")
    print(f"\n✅ Success: LLM queried YOUR database and analyzed the results!")


def main():
    """Run the database query example."""
    print("\n" + "="*60)
    print("Database Query Tool Example")
    print("="*60)
    print("\nThis shows why tool calling is essential:")
    print("- LLM doesn't have access to YOUR data")
    print("- LLM needs YOUR function to query YOUR database")
    print("- Without tools, LLM can only say 'I don't have access'")

    # Setup demo database
    print("\n[Setting up demo database...]")
    db_path = setup_demo_database()
    print("[Created database with 5 sample customers]")

    # Show the difference
    demonstrate_without_tools(db_path)
    demonstrate_with_tools(db_path)

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

    print("\n" + "="*60)
    print("Key Takeaway")
    print("="*60)
    print("\n💡 Tool calling lets LLM work with YOUR data:")
    print("   - Customer databases")
    print("   - Order systems")
    print("   - Analytics platforms")
    print("   - Internal tools")
    print("\nLLM becomes your data analysis assistant!\n")


if __name__ == "__main__":
    main()
