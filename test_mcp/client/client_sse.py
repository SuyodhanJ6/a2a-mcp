#!/usr/bin/env python
"""
MCP Client using SSE transport

This script demonstrates how to connect to MCP servers using SSE transport
and use the tools with LangGraph agents.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_api_key():
    """Check if the API key is set and prompt for it if not."""
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable not set.")
        api_key = input("Please enter your Google API key: ")
        os.environ["GOOGLE_API_KEY"] = api_key


async def run_agent_with_mcp_tools(query: str):
    """
    Run a LangGraph agent with MCP tools using SSE transport.
    
    Args:
        query: The user query to send to the agent
    """
    # Check for API key first
    check_api_key()
    
    # Initialize the language model
    try:
        model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        
        # Start the servers in the background before connecting
        print("🚀 Make sure you have started the MCP servers with SSE transport:")
        print("   python ../server/math_server.py sse 8002")
        print("   python ../server/currency_server.py sse 8001")
        print("-----------------------------------")
        
        # Use MultiServerMCPClient for convenient connection to multiple servers
        server_config = {
            "math": {
                "url": "http://localhost:8002/sse",
                "transport": "sse",
            },
            "currency": {
                "url": "http://localhost:8001/sse",
                "transport": "sse",
            }
        }
        
        async with MultiServerMCPClient(server_config) as client:
            # Get all tools from both servers
            all_tools = client.get_tools()
            print(f"🔧 Loaded {len(all_tools)} tools from MCP servers")
            
            # Create the agent
            agent = create_react_agent(model, all_tools)
            print(f"🤖 Created agent with {len(all_tools)} tools")
            
            # Run the agent
            print("\n💬 Running query:", query)
            print("-----------------------------------")
            response = await agent.ainvoke({"messages": [("human", query)]})
            
            # Print the final response
            print("\n🔮 Agent response:")
            print("-----------------------------------")
            print(response["messages"][-1].content)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def chat_mode():
    """Run an interactive chat session with the MCP agent."""
    print("🤖 Starting interactive chat mode (type 'exit' to quit)")
    print("-----------------------------------")
    
    while True:
        query = input("\n💬 You: ")
        if query.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break
            
        await run_agent_with_mcp_tools(query)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MCP client with SSE transport")
    parser.add_argument("--query", type=str, help="Query to send to the agent")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat mode")
    
    args = parser.parse_args()
    
    # Check for API key at startup
    check_api_key()
    
    if args.chat:
        asyncio.run(chat_mode())
    elif args.query:
        asyncio.run(run_agent_with_mcp_tools(args.query))
    else:
        print("Please provide either --query or --chat arguments")
        print("Example: python client_sse.py --query 'What is 5 + 7?'")
        print("Example: python client_sse.py --chat") 