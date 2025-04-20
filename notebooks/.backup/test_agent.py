from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize memory for the agent
memory = MemorySaver()

# Define the tools for our agent
@tool
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers together.
    
    Args:
        a: The first number.
        b: The second number.
    
    Returns:
        The sum of the two numbers.
    """
    return a + b

@tool
def multiply_numbers(a: int, b: int) -> int:
    """Multiplies two numbers together.
    
    Args:
        a: The first number.
        b: The second number.
    
    Returns:
        The product of the two numbers.
    """
    return a * b

# Define our agent class
class MathAgent:
    SYSTEM_INSTRUCTION = (
        "You are a specialized math assistant. "
        "Your sole purpose is to help with addition and multiplication. "
        "Use the 'add_numbers' tool to add two numbers, "
        "or the 'multiply_numbers' tool to multiply two numbers. "
        "If the user asks about anything other than addition or multiplication, "
        "politely state that you cannot help with that topic and can only assist with "
        "addition and multiplication. "
        "Do not attempt to answer unrelated questions or use tools for other purposes."
    )
    
    def __init__(self):
        # Initialize the model - use environment variable for the API key
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.tools = [add_numbers, multiply_numbers]
        
        # Create the agent graph
        self.graph = create_react_agent(
            self.model, 
            tools=self.tools, 
            checkpointer=memory, 
            prompt=self.SYSTEM_INSTRUCTION
        )
    
    def invoke(self, query, session_id="default") -> Dict[str, Any]:
        """Invoke the agent with a query."""
        config = {"configurable": {"thread_id": session_id}}
        response = self.graph.invoke({"messages": [("user", query)]}, config)
        return {
            "input": query,
            "output": response["messages"][-1].content,
            "full_response": response
        }

# Simple test function
def test_agent():
    # Create the agent
    agent = MathAgent()
    
    # Test with valid math questions
    print("Test 1: Addition")
    result = agent.invoke("What is 5 + 7?")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    print("-" * 50)
    
    print("Test 2: Multiplication")
    result = agent.invoke("Calculate 8 * 12")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    print("-" * 50)
    
    print("Test 3: Non-math question")
    result = agent.invoke("What's the weather like today?")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    print("-" * 50)

if __name__ == "__main__":
    test_agent() 