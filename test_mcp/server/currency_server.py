#!/usr/bin/env python
"""
Currency MCP Server

This script creates an MCP server for currency conversion by wrapping
the existing Currency Agent from A2A protocol.
"""

import sys
import os
import httpx
import uuid
from typing import Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables from .env file
load_dotenv()

# Check for Google API key
if not os.getenv("GOOGLE_API_KEY"):
    print("Warning: GOOGLE_API_KEY environment variable not set.")
    print("The Currency Agent may not work correctly without it.")

# Create MCP server
mcp = FastMCP("Currency")

# Default port for our currency A2A service
A2A_HOST = "localhost"
A2A_PORT = 10000


@mcp.tool()
def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: Optional[float] = 1.0
) -> str:
    """
    Convert an amount from one currency to another.
    
    Args:
        from_currency: The source currency code (e.g., "USD", "EUR", "JPY")
        to_currency: The target currency code (e.g., "USD", "EUR", "JPY")
        amount: The amount to convert (defaults to 1.0 for just the exchange rate)
        
    Returns:
        A string containing the conversion result or error message
    """
    # Call the A2A Currency Agent
    prompt = f"Convert {amount} {from_currency} to {to_currency}"
    return _call_a2a_agent(prompt)


@mcp.tool()
def get_exchange_rate(
    from_currency: str,
    to_currency: str
) -> str:
    """
    Get the current exchange rate between two currencies.
    
    Args:
        from_currency: The source currency code (e.g., "USD", "EUR", "JPY")
        to_currency: The target currency code (e.g., "USD", "EUR", "JPY")
        
    Returns:
        A string containing the exchange rate information or error message
    """
    # Call the A2A Currency Agent
    prompt = f"What is the exchange rate from {from_currency} to {to_currency}?"
    return _call_a2a_agent(prompt)


def _call_a2a_agent(prompt: str) -> str:
    """
    Helper function to call the A2A Currency Agent.
    
    Args:
        prompt: The question to ask the Currency Agent
        
    Returns:
        The agent's response
    """
    session_id = uuid.uuid4().hex
    task_id = uuid.uuid4().hex
    
    url = f"http://{A2A_HOST}:{A2A_PORT}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tasks/send",
        "params": {
            "id": task_id,
            "sessionId": session_id,
            "acceptedOutputModes": ["text"],
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        
        # Extract the content from the response
        if "result" in result:
            if "artifacts" in result["result"] and result["result"]["artifacts"]:
                return result["result"]["artifacts"][0]["parts"][0]["text"]
            elif "status" in result["result"] and result["result"]["status"].get("message"):
                return result["result"]["status"]["message"]["parts"][0]["text"]
        
        # If we couldn't find the expected content, return the raw result
        return f"Unexpected response format"
        
    except httpx.HTTPError as e:
        return f"Error calling Currency Agent: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


if __name__ == "__main__":
    # Default to stdio transport
    transport = "stdio" if len(sys.argv) <= 1 else sys.argv[1]
    
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        port = 8001 if len(sys.argv) <= 2 else int(sys.argv[2])
        mcp.run(transport="sse", port=port)
    else:
        print(f"Unknown transport: {transport}")
        sys.exit(1) 