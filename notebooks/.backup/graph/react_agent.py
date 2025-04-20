"""
React Agent using A2A Tools

This module implements a React-style agent that can use A2A protocol-compatible agents as tools.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the graph package
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from typing import Dict, Any, List
from graph.a2a_tools import CurrencyTool, MathTool

# Load environment variables
load_dotenv()

# Initialize memory for the agent
memory = MemorySaver()

class A2AReactAgent:
    """ReAct agent that uses A2A protocol-compatible agents as tools."""
    
    SYSTEM_INSTRUCTION = """
    You are an intelligent assistant that can help with various tasks by using specialized tools.
    
    You have access to two tools:
    1. currency_tool: Use this when the user asks about currency conversions or exchange rates.
    2. math_tool: Use this when the user asks about mathematical calculations, specifically addition and multiplication.
    
    For all other types of questions, answer directly to the best of your knowledge without using tools.
    
    Always use the most appropriate tool for the task, and interpret the results for the user in a helpful way.
    """
    
    def __init__(self):
        # Check for API key
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        # Initialize the model
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        # Initialize the tools
        self.tools = [
            CurrencyTool(),
            MathTool()
        ]
        
        # Create the agent graph
        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION
        )
    
    def invoke(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Invoke the agent with a query."""
        config = {"configurable": {"thread_id": session_id}}
        response = self.graph.invoke({"messages": [("human", query)]}, config)
        
        return {
            "input": query,
            "output": response["messages"][-1].content,
            "full_response": response
        }
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get the chat history for a session."""
        config = {"configurable": {"thread_id": session_id}}
        current_state = self.graph.get_state(config)
        
        if current_state and "messages" in current_state.values:
            messages = current_state.values["messages"]
            return [
                {
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content
                }
                for msg in messages
            ]
        
        return []


# Simple test function
def test_agent():
    """Run some test queries against the agent."""
    agent = A2AReactAgent()
    
    # Test currency tool
    print("Test 1: Currency Question")
    result = agent.invoke("What is the exchange rate from USD to EUR?")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    print("-" * 50)
    
    # Test math tool
    print("Test 2: Math Question")
    result = agent.invoke("Calculate 25 + 17")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    print("-" * 50)
    
    # Test combination question
    print("Test 3: Combined Question")
    result = agent.invoke("If I have 100 USD, how many Euros would that be, and if I split it equally between 5 people, how much would each person get?")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    print("-" * 50)
    
    # Test direct knowledge question
    print("Test 4: General Knowledge Question")
    result = agent.invoke("What is the capital of Japan?")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    print("-" * 50)

if __name__ == "__main__":
    test_agent() 