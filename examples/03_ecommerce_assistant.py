#!/usr/bin/env python3
"""
Example 3: E-commerce Shopping Assistant

Demonstrates a real shopping assistant that accesses YOUR product catalog
and inventory - data LLM cannot access without your tools.

WITHOUT tools: LLM says "I don't have access to your product catalog"
WITH tools: LLM searches YOUR products and helps customers shop
"""

from llmswap import LLMClient, Tool
from typing import List, Dict


# Mock product database
PRODUCTS = [
    {"id": "P001", "name": "Wireless Headphones", "price": 79.99, "category": "audio", "stock": 25, "rating": 4.5},
    {"id": "P002", "name": "Bluetooth Speaker", "price": 49.99, "category": "audio", "stock": 15, "rating": 4.3},
    {"id": "P003", "name": "USB-C Cable", "price": 12.99, "category": "accessories", "stock": 100, "rating": 4.7},
    {"id": "P004", "name": "Phone Case", "price": 19.99, "category": "accessories", "stock": 50, "rating": 4.4},
    {"id": "P005", "name": "Laptop Stand", "price": 34.99, "category": "accessories", "stock": 30, "rating": 4.6},
    {"id": "P006", "name": "Webcam HD", "price": 89.99, "category": "electronics", "stock": 8, "rating": 4.2},
    {"id": "P007", "name": "Mechanical Keyboard", "price": 129.99, "category": "electronics", "stock": 12, "rating": 4.8},
    {"id": "P008", "name": "Gaming Mouse", "price": 59.99, "category": "electronics", "stock": 20, "rating": 4.5},
]


def create_shopping_tools():
    """Create e-commerce tools."""
    return [
        Tool(
            name="search_products",
            description="Search product catalog by keywords, category, or price range",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search keywords (e.g., 'wireless', 'headphones', 'keyboard')"
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price filter (optional)"
                },
                "category": {
                    "type": "string",
                    "description": "Category filter: 'audio', 'accessories', or 'electronics' (optional)"
                }
            },
            required=["query"]
        ),
        Tool(
            name="check_stock",
            description="Check if a product is in stock and get availability details",
            parameters={
                "product_id": {
                    "type": "string",
                    "description": "Product ID (e.g., 'P001')"
                }
            },
            required=["product_id"]
        ),
        Tool(
            name="get_product_details",
            description="Get detailed information about a specific product",
            parameters={
                "product_id": {
                    "type": "string",
                    "description": "Product ID"
                }
            },
            required=["product_id"]
        )
    ]


def search_products(query: str, max_price: float = None, category: str = None) -> str:
    """
    Search YOUR product catalog.

    LLM doesn't know what products you sell!
    """
    query_lower = query.lower()
    results = []

    for product in PRODUCTS:
        # Check if query matches
        if query_lower not in product["name"].lower():
            continue

        # Check price filter
        if max_price and product["price"] > max_price:
            continue

        # Check category filter
        if category and product["category"] != category:
            continue

        results.append(product)

    if not results:
        return f"No products found matching '{query}'"

    # Format results
    response = f"Found {len(results)} product(s):\n\n"
    for p in results:
        response += f"- {p['name']} (ID: {p['id']})\n"
        response += f"  Price: ${p['price']}\n"
        response += f"  Rating: {p['rating']}⭐\n"
        response += f"  Stock: {p['stock']} units\n\n"

    return response


def check_stock(product_id: str) -> str:
    """Check stock for YOUR inventory."""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)

    if not product:
        return f"Product {product_id} not found"

    stock = product["stock"]

    if stock == 0:
        return f"{product['name']} is OUT OF STOCK"
    elif stock < 10:
        return f"{product['name']}: LOW STOCK - Only {stock} units remaining!"
    else:
        return f"{product['name']}: IN STOCK - {stock} units available"


def get_product_details(product_id: str) -> str:
    """Get details from YOUR product database."""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)

    if not product:
        return f"Product {product_id} not found"

    return f"""Product Details:
Name: {product['name']}
ID: {product['id']}
Price: ${product['price']}
Category: {product['category']}
Rating: {product['rating']}⭐
Stock: {product['stock']} units available
"""


def execute_tool(tool_call) -> str:
    """Execute the appropriate tool."""
    if tool_call.name == "search_products":
        return search_products(**tool_call.arguments)
    elif tool_call.name == "check_stock":
        return check_stock(**tool_call.arguments)
    elif tool_call.name == "get_product_details":
        return get_product_details(**tool_call.arguments)
    return "Unknown tool"


def demonstrate_without_tools():
    """Show what happens WITHOUT tool calling."""
    print("\n" + "="*60)
    print("WITHOUT Tool Calling")
    print("="*60)

    client = LLMClient(provider="anthropic")

    # Ask about YOUR products
    response = client.chat("Do you have wireless headphones under $80?")

    print(f"\nCustomer: Do you have wireless headphones under $80?")
    print(f"\nAssistant: {response.content}")
    print(f"\n❌ Problem: LLM doesn't know what products YOU sell!")


def demonstrate_with_tools():
    """Show what happens WITH tool calling."""
    print("\n" + "="*60)
    print("WITH Tool Calling")
    print("="*60)

    client = LLMClient(provider="anthropic")
    tools = create_shopping_tools()

    # Ask about YOUR products
    user_query = "Do you have wireless headphones under $80?"
    print(f"\nCustomer: {user_query}")

    response = client.chat(user_query, tools=tools)

    # Check if LLM wants to use tools
    tool_calls = response.metadata.get('tool_calls', [])

    if not tool_calls:
        print(f"\nAssistant: {response.content}")
        return

    # LLM called the search tool!
    tool_call = tool_calls[0]
    print(f"\n[LLM called: {tool_call.name}]")
    print(f"[Arguments: {tool_call.arguments}]")

    # Execute YOUR function to search YOUR catalog
    search_results = execute_tool(tool_call)
    print(f"\n[Your Catalog returned:]")
    print(search_results)

    # Send result back to LLM
    messages = [
        {"role": "user", "content": user_query},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": tool_call.id,
             "name": tool_call.name, "input": tool_call.arguments}
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tool_call.id, "content": search_results}
        ]}
    ]

    final_response = client.chat(messages, tools=tools)
    print(f"\nAssistant: {final_response.content}")
    print(f"\n✅ Success: LLM searched YOUR products and helped the customer!")


def main():
    """Run the e-commerce assistant example."""
    print("\n" + "="*60)
    print("E-commerce Shopping Assistant Example")
    print("="*60)
    print("\nThis shows why tool calling is essential:")
    print("- LLM doesn't know what products YOU sell")
    print("- LLM needs YOUR functions to search YOUR catalog")
    print("- Without tools, LLM can't help customers shop")

    # Show the difference
    demonstrate_without_tools()
    demonstrate_with_tools()

    print("\n" + "="*60)
    print("Key Takeaway")
    print("="*60)
    print("\n💡 Tool calling enables real shopping assistants:")
    print("   - Search YOUR product catalog")
    print("   - Check YOUR inventory in real-time")
    print("   - Access YOUR pricing and availability")
    print("   - Help customers find what they need")
    print("\nLLM becomes a knowledgeable sales assistant!\n")


if __name__ == "__main__":
    main()
