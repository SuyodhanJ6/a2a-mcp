#!/usr/bin/env python
"""
MCP Client using STDIO transport

This script demonstrates how to connect to MCP servers using STDIO transport
and use the tools with LangGraph agents.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
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
    Run a LangGraph agent with MCP tools.
    
    Args:
        query: The user query to send to the agent
    """
    # Check for API key first
    check_api_key()
    
    # Initialize the language model
    try:
        model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        
        # Set up the math server parameters
        math_server_params = StdioServerParameters(
            command="python",
            args=[os.path.abspath(os.path.join(os.path.dirname(__file__), "../server/math_server.py"))],
        )
        
        # Set up the currency server parameters
        currency_server_params = StdioServerParameters(
            command="python",
            args=[os.path.abspath(os.path.join(os.path.dirname(__file__), "../server/currency_server.py"))],
        )
        
        print("🚀 Starting MCP servers...")
        
        # Connect to math server
        math_client = None
        math_tools = []
        try:
            async with stdio_client(math_server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    print("✅ Connected to Math MCP server")
                    
                    # Get tools
                    math_tools = await load_mcp_tools(session)
                    print(f"📊 Loaded {len(math_tools)} math tools")
                    
                    # Now connect to currency server
                    try:
                        async with stdio_client(currency_server_params) as (read2, write2):
                            async with ClientSession(read2, write2) as session2:
                                # Initialize the connection
                                await session2.initialize()
                                print("✅ Connected to Currency MCP server")
                                
                                # Get tools
                                currency_tools = await load_mcp_tools(session2)
                                print(f"💱 Loaded {len(currency_tools)} currency tools")
                                
                                # Combine tools
                                all_tools = math_tools + currency_tools
                                
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
                        print(f"❌ Error connecting to Currency MCP server: {str(e)}")
        
        except Exception as e:
            print(f"❌ Error connecting to Math MCP server: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error initializing the agent: {str(e)}")


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
    
    parser = argparse.ArgumentParser(description="Test MCP client with STDIO transport")
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
        print("Example: python client_stdio.py --query 'What is 5 + 7?'")
        print("Example: python client_stdio.py --chat") 