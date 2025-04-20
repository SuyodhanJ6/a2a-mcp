#!/usr/bin/env python
"""
A2E Client using direct invocation

This script demonstrates how to use the A2E agent directly without going through the A2A server.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from finala2e.agent import A2EMathCurrencyAgent

# Load environment variables from .env file
load_dotenv()

def check_api_key():
    """Check if the API key is set and prompt for it if not."""
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable not set.")
        api_key = input("Please enter your Google API key: ")
        os.environ["GOOGLE_API_KEY"] = api_key


async def run_agent_with_query(query: str):
    """
    Run the A2E agent with a given query.
    
    Args:
        query: The user query to send to the agent
    """
    # Check for API key first
    check_api_key()
    
    try:
        print("🚀 Initializing A2E Math & Currency Agent...")
        
        # Initialize the agent
        agent = A2EMathCurrencyAgent()
        
        print(f"🤖 Agent initialized with {len(agent.tools)} tools")
        
        # Run the agent
        print("\n💬 Processing query:", query)
        print("-----------------------------------")
        
        # Create a unique session ID
        session_id = f"session_{os.urandom(4).hex()}"
        
        # Stream the response
        try:
            async for chunk in agent.stream(query, session_id):
                if chunk.get("is_task_complete", False):
                    print("\n🔮 Final response:")
                    print("-----------------------------------")
                    print(chunk["content"])
                else:
                    print(f"[Processing] {chunk['content']}")
        except Exception as e:
            print(f"❌ Stream error: {str(e)}")
            print("Falling back to non-streaming invoke...")
            result = agent.invoke(query, session_id)
            print("\n🔮 Final response:")
            print("-----------------------------------")
            print(result["content"])
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def chat_mode():
    """Run an interactive chat session with the A2E agent."""
    print("🤖 Starting interactive chat mode (type 'exit' to quit)")
    print("-----------------------------------")
    
    # Initialize the agent once
    check_api_key()
    
    try:
        agent = A2EMathCurrencyAgent()
        print(f"🤖 Agent initialized with {len(agent.tools)} tools")
        
        # Create a session ID for this chat
        session_id = f"session_{os.urandom(4).hex()}"
        
        while True:
            query = input("\n💬 You: ")
            if query.lower() in ["exit", "quit", "q"]:
                print("👋 Goodbye!")
                break
                
            try:
                # Stream the response
                async for chunk in agent.stream(query, session_id):
                    if chunk.get("is_task_complete", False):
                        print("\n🔮 Agent: ", end="")
                        print(chunk["content"])
                    else:
                        print(f"[Processing] {chunk['content']}")
            except Exception as e:
                print(f"❌ Stream error: {str(e)}")
                print("Falling back to non-streaming invoke...")
                result = agent.invoke(query, session_id)
                print("\n🔮 Agent: ", end="")
                print(result["content"])
    except Exception as e:
        print(f"❌ Error initializing agent: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test A2E Math & Currency Agent")
    parser.add_argument("--query", type=str, help="Query to send to the agent")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat mode")
    
    args = parser.parse_args()
    
    # Check for API key at startup
    check_api_key()
    
    if args.chat:
        asyncio.run(chat_mode())
    elif args.query:
        asyncio.run(run_agent_with_query(args.query))
    else:
        print("Please provide either --query or --chat arguments")
        print("Example: python client_stdio.py --query 'What is 5 + 7?'")
        print("Example: python client_stdio.py --chat") 