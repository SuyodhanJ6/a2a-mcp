#!/usr/bin/env python
"""
Start MCP Servers with SSE transport

This script starts both the Math and Currency MCP servers using SSE transport
to be used with the client_sse.py script.
"""

import os
import sys
import subprocess
import time
import signal
import atexit
from dotenv import load_dotenv

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Store the subprocess handles
processes = []

def check_api_key():
    """Check if the API key is set and prompt for it if not."""
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable not set.")
        api_key = input("Please enter your Google API key: ")
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Also create an environment copy for subprocesses
        return True
    return False

def cleanup_processes():
    """Clean up any running server processes when the script exits."""
    print("\n🧹 Cleaning up server processes...")
    for p in processes:
        if p.poll() is None:  # If process is still running
            p.terminate()
            try:
                p.wait(timeout=5)
                print(f"✅ Successfully terminated process {p.pid}")
            except subprocess.TimeoutExpired:
                p.kill()
                print(f"⚠️ Had to forcibly kill process {p.pid}")


# Register the cleanup function to be called when the script exits
atexit.register(cleanup_processes)

def start_sse_servers():
    """Start the Math and Currency MCP servers using SSE transport."""
    # Check for API key first
    check_api_key()
    
    # Create an environment copy with the API key for subprocesses
    env = os.environ.copy()
    
    # Get the absolute paths to the server scripts
    math_server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "server/math_server.py"))
    currency_server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "server/currency_server.py"))
    
    # Check if the server scripts exist
    if not os.path.exists(math_server_path):
        print(f"❌ Math server script not found at {math_server_path}")
        sys.exit(1)
    if not os.path.exists(currency_server_path):
        print(f"❌ Currency server script not found at {currency_server_path}")
        sys.exit(1)
        
    print("🚀 Starting MCP servers with SSE transport...")
    
    # Start the Math server
    math_process = subprocess.Popen(
        [sys.executable, math_server_path, "sse", "8002"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    processes.append(math_process)
    print(f"✅ Started Math MCP server (PID: {math_process.pid}) on port 8002")
    
    # Start the Currency server
    currency_process = subprocess.Popen(
        [sys.executable, currency_server_path, "sse", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    processes.append(currency_process)
    print(f"✅ Started Currency MCP server (PID: {currency_process.pid}) on port 8001")
    
    # Wait a bit for the servers to start up
    time.sleep(2)
    
    # Check if the servers are still running
    all_running = True
    for i, p in enumerate(processes):
        if p.poll() is not None:
            all_running = False
            server_name = "Math" if i == 0 else "Currency"
            print(f"❌ {server_name} server exited with code {p.returncode}")
            stdout, stderr = p.communicate()
            print(f"--- STDOUT ---\n{stdout}")
            print(f"--- STDERR ---\n{stderr}")
    
    if all_running:
        print("✅ All MCP servers are running")
        print("\n🔗 Servers are ready for connection!")
        print("   You can now run: python client/client_sse.py --chat")
        print("\n⚠️  Press Ctrl+C to stop the servers")
        
        # Keep the script running to manage the subprocesses
        try:
            while all(p.poll() is None for p in processes):
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Received interrupt, shutting down servers...")
        
        # Any process that exited on its own
        for i, p in enumerate(processes):
            if p.poll() is not None:
                server_name = "Math" if i == 0 else "Currency"
                print(f"⚠️ {server_name} server exited with code {p.returncode}")
    else:
        print("❌ Some servers failed to start.")
        sys.exit(1)


if __name__ == "__main__":
    start_sse_servers() 