#!/usr/bin/env python3
from notebooks.test_agent import MathAgent
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

def check_api_key():
    """Check if the API key is set and prompt for it if not."""
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable is not set.")
        api_key = input("Please enter your Google API key: ")
        os.environ["GOOGLE_API_KEY"] = api_key

def run_tests():
    """Run a series of tests to verify the agent works correctly."""
    agent = MathAgent()
    print("Running tests...")
    print("=" * 50)
    
    # Test addition
    print("Test 1: Addition")
    result = agent.invoke("What is 42 + 28?")
    print(f"Question: {result['input']}")
    print(f"Answer: {result['output']}")
    print("-" * 50)
    
    # Test multiplication
    print("Test 2: Multiplication")
    result = agent.invoke("What is 7 * 9?")
    print(f"Question: {result['input']}")
    print(f"Answer: {result['output']}")
    print("-" * 50)
    
    # Test combination
    print("Test 3: Combination")
    result = agent.invoke("I need to add 15 and 27, then multiply the result by 2")
    print(f"Question: {result['input']}")
    print(f"Answer: {result['output']}")
    print("-" * 50)
    
    # Test non-math question
    print("Test 4: Non-math question")
    result = agent.invoke("What is the capital of Japan?")
    print(f"Question: {result['input']}")
    print(f"Answer: {result['output']}")
    print("=" * 50)
    print("Tests completed.")

def chat_mode():
    """Run the agent in interactive chat mode."""
    agent = MathAgent()
    session_id = "interactive-session"
    
    print("Math Agent Chat (type 'exit' to quit)")
    print("This agent can only help with addition and multiplication!")
    print("-" * 50)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
            
        result = agent.invoke(user_input, session_id=session_id)
        print(f"Agent: {result['output']}")
        print("-" * 50)

def single_query(query):
    """Run the agent with a single query."""
    agent = MathAgent()
    result = agent.invoke(query)
    print(f"Question: {result['input']}")
    print(f"Answer: {result['output']}")

def main():
    parser = argparse.ArgumentParser(description="Run the Math Agent")
    parser.add_argument("--test", action="store_true", help="Run test suite")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat mode")
    parser.add_argument("--query", type=str, help="Run a single query")
    
    args = parser.parse_args()
    
    # Check for API key
    check_api_key()
    
    if args.test:
        run_tests()
    elif args.chat:
        chat_mode()
    elif args.query:
        single_query(args.query)
    else:
        # Default to chat mode if no arguments provided
        chat_mode()

if __name__ == "__main__":
    main() 