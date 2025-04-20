#!/usr/bin/env python3
import httpx
import json
import uuid
import argparse

# Default settings
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 10001

def get_agent_card(host, port):
    """Get the agent's card metadata."""
    url = f"http://{host}:{port}/.well-known/agent.json"
    response = httpx.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Could not get agent card. Status code: {response.status_code}")
        return None

def send_task(host, port, query):
    """Send a synchronous task request to the agent."""
    url = f"http://{host}:{port}"
    session_id = uuid.uuid4().hex
    task_id = uuid.uuid4().hex
    
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
                        "text": query
                    }
                ]
            }
        }
    }
    
    headers = {"Content-Type": "application/json"}
    response = httpx.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Status code: {response.status_code}")
        print(response.text)
        return None

def send_streaming_task(host, port, query):
    """Send a streaming task request to the agent and print events as they arrive."""
    url = f"http://{host}:{port}"
    session_id = uuid.uuid4().hex
    task_id = uuid.uuid4().hex
    
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tasks/sendSubscribe",
        "params": {
            "id": task_id,
            "sessionId": session_id,
            "acceptedOutputModes": ["text"],
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        }
    }
    
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
    
    with httpx.Client(timeout=30.0) as client:
        with client.stream("POST", url, json=payload, headers=headers) as response:
            print(f"Stream started, status code: {response.status_code}")
            if response.status_code != 200:
                print(f"Error: {response.text}")
                return
            
            print("\nReceiving events:")
            print("-" * 50)
            for line in response.iter_lines():
                if line.startswith("data: "):
                    event_data = line[6:]  # Skip the "data: " prefix
                    try:
                        parsed_event = json.loads(event_data)
                        if "result" in parsed_event:
                            if "artifact" in parsed_event["result"]:
                                content = parsed_event["result"]["artifact"]["parts"][0]["text"]
                                print(f"Final result: {content}")
                            elif "status" in parsed_event["result"]:
                                if parsed_event["result"]["status"].get("message"):
                                    status_content = parsed_event["result"]["status"]["message"]["parts"][0]["text"]
                                    state = parsed_event["result"]["status"]["state"]
                                    print(f"Status [{state}]: {status_content}")
                                if parsed_event["result"].get("final", False):
                                    print("\nStream completed.")
                    except json.JSONDecodeError:
                        print(f"Could not parse event: {event_data}")

def chat_mode(host, port):
    """Interactive chat session with the math agent."""
    print(f"Math Agent Chat via A2A protocol ({host}:{port})")
    print("Type 'exit' to quit")
    print("-" * 50)
    
    session_id = uuid.uuid4().hex
    
    while True:
        query = input("You: ")
        if query.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
        
        # Create a new task ID for each message
        task_id = uuid.uuid4().hex
        
        url = f"http://{host}:{port}"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "sessionId": session_id,  # Reuse the same session ID for continuity
                "acceptedOutputModes": ["text"],
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": query
                        }
                    ]
                }
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = httpx.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "result" in result:
                    if "artifacts" in result["result"] and result["result"]["artifacts"]:
                        content = result["result"]["artifacts"][0]["parts"][0]["text"]
                        print(f"Agent: {content}")
                    elif "status" in result["result"] and result["result"]["status"].get("message"):
                        content = result["result"]["status"]["message"]["parts"][0]["text"]
                        print(f"Agent: {content}")
                    else:
                        print("Agent: No response content found.")
                else:
                    print(f"Error: {result.get('error', {}).get('message', 'Unknown error')}")
            except Exception as e:
                print(f"Error parsing response: {e}")
        else:
            print(f"Error: Status code: {response.status_code}")
            print(response.text)
        
        print("-" * 50)

def parse_args():
    parser = argparse.ArgumentParser(description="Test the Math Agent via A2A protocol")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host address (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port number (default: {DEFAULT_PORT})")
    parser.add_argument("--card", action="store_true", help="Get the agent card")
    parser.add_argument("--query", type=str, help="Send a single query to the agent")
    parser.add_argument("--stream", action="store_true", help="Use streaming mode for the query")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat mode")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.card:
        card = get_agent_card(args.host, args.port)
        if card:
            print(json.dumps(card, indent=2))
    
    elif args.query:
        if args.stream:
            send_streaming_task(args.host, args.port, args.query)
        else:
            result = send_task(args.host, args.port, args.query)
            if result:
                print(json.dumps(result, indent=2))
    
    elif args.chat:
        chat_mode(args.host, args.port)
    
    else:
        # Default to getting agent card if no action specified
        print("No action specified, displaying agent card:")
        card = get_agent_card(args.host, args.port)
        if card:
            print(json.dumps(card, indent=2))

if __name__ == "__main__":
    main() 