#!/usr/bin/env python3
"""
Example 1: Real-Time Weather API

Demonstrates why tool calling is essential - LLM needs YOUR function
to access real-time weather data it doesn't have.

WITHOUT tools: LLM says "I don't have access to real-time weather"
WITH tools: LLM calls YOUR API and gives actual current weather
"""

from llmswap import LLMClient, Tool
import requests


def create_weather_tool():
    """Create weather lookup tool."""
    return Tool(
        name="get_current_weather",
        description="Get real-time weather data for any city worldwide",
        parameters={
            "city": {
                "type": "string",
                "description": "City name (e.g., 'Tokyo', 'San Francisco', 'London')"
            },
            "units": {
                "type": "string",
                "description": "Temperature units: 'celsius' or 'fahrenheit'",
                "enum": ["celsius", "fahrenheit"]
            }
        },
        required=["city"]
    )


def get_current_weather(city: str, units: str = "celsius") -> str:
    """
    Fetch real-time weather from wttr.in API.

    This is YOUR function that accesses real data.
    LLM cannot do this without your help!
    """
    try:
        # Use free wttr.in API (no key needed)
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return f"Error: Could not fetch weather for {city}"

        data = response.json()
        current = data['current_condition'][0]

        # Convert temperature if needed
        temp_c = int(current['temp_C'])
        temp_f = int(current['temp_F'])
        temp = temp_f if units == "fahrenheit" else temp_c
        unit_symbol = "°F" if units == "fahrenheit" else "°C"

        weather_desc = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        wind_speed = current['windspeedKmph']

        return f"Weather in {city}: {temp}{unit_symbol}, {weather_desc}. Humidity: {humidity}%, Wind: {wind_speed} km/h"

    except Exception as e:
        return f"Error fetching weather: {str(e)}"


def demonstrate_without_tools():
    """Show what happens WITHOUT tool calling."""
    print("\n" + "="*60)
    print("WITHOUT Tool Calling")
    print("="*60)

    client = LLMClient(provider="anthropic")

    # Ask about real-time weather
    response = client.chat("What's the current weather in Tokyo right now?")

    print(f"\nUser: What's the current weather in Tokyo right now?")
    print(f"\nLLM: {response.content}")
    print(f"\n❌ Problem: LLM doesn't have access to real-time data!")


def demonstrate_with_tools():
    """Show what happens WITH tool calling."""
    print("\n" + "="*60)
    print("WITH Tool Calling")
    print("="*60)

    client = LLMClient(provider="anthropic")
    weather_tool = create_weather_tool()

    # Ask about real-time weather
    user_query = "What's the current weather in Tokyo right now?"
    print(f"\nUser: {user_query}")

    response = client.chat(user_query, tools=[weather_tool])

    # Check if LLM wants to use the tool
    tool_calls = response.metadata.get('tool_calls', [])

    if not tool_calls:
        print(f"\nLLM: {response.content}")
        return

    # LLM called the weather tool!
    tool_call = tool_calls[0]
    print(f"\n[LLM called: {tool_call.name}]")
    print(f"[Arguments: {tool_call.arguments}]")

    # Execute YOUR function to get real data
    weather_data = get_current_weather(**tool_call.arguments)
    print(f"\n[Your API returned: {weather_data}]")

    # Send result back to LLM for natural language response
    messages = [
        {"role": "user", "content": user_query},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": tool_call.id,
             "name": tool_call.name, "input": tool_call.arguments}
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tool_call.id, "content": weather_data}
        ]}
    ]

    final_response = client.chat(messages, tools=[weather_tool])
    print(f"\nLLM: {final_response.content}")
    print(f"\n✅ Success: LLM used YOUR function to get real weather data!")


def main():
    """Run the weather API example."""
    print("\n" + "="*60)
    print("Real-Time Weather API Example")
    print("="*60)
    print("\nThis shows why tool calling is essential:")
    print("- LLM doesn't have access to real-time weather")
    print("- LLM needs YOUR function to fetch current data")
    print("- Without tools, LLM can only say 'I don't know'")

    # Show the difference
    demonstrate_without_tools()
    demonstrate_with_tools()

    print("\n" + "="*60)
    print("Key Takeaway")
    print("="*60)
    print("\n💡 Tool calling lets LLM access YOUR real-time data")
    print("   - Weather APIs")
    print("   - Your database")
    print("   - Your business systems")
    print("   - External services")
    print("\nWithout tools, LLM is limited to its training data!\n")


if __name__ == "__main__":
    main()
