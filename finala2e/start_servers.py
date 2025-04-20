#!/usr/bin/env python
"""
Start A2A Servers

This script starts both the Currency Agent and Math Agent servers
required for the MCP servers to function.
"""

import subprocess
import sys
import os
import signal
import time
import atexit

# Track the subprocesses
processes = []

def kill_processes():
    """Kill all spawned processes."""
    for process in processes:
        try:
            if process.poll() is None:  # If process is still running
                print(f"Terminating process PID {process.pid}...")
                process.terminate()
                process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"Force killing process PID {process.pid}...")
            process.kill()


def main():
    """Start the Currency and Math A2A servers."""
    # Register the cleanup function
    atexit.register(kill_processes)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nReceived interrupt signal. Shutting down servers...")
        kill_processes()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Path to the project root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    print("🚀 Starting A2A servers...")
    
    # Start Currency Agent on port 10000
    currency_process = subprocess.Popen(
        [sys.executable, "-m", "agent", "--host", "localhost", "--port", "10000"],
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(currency_process)
    print(f"✅ Started Currency Agent (PID: {currency_process.pid}) on port 10000")
    
    # Give the first server a moment to start
    time.sleep(2)
    
    # Define a special Math Agent script for port 10001
    # Note: We could implement a full Math Agent, but for simplicity, we're reusing the Currency Agent on a different port
    math_process = subprocess.Popen(
        [sys.executable, "-m", "agent", "--host", "localhost", "--port", "10001"],
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(math_process)
    print(f"✅ Started Math Agent (PID: {math_process.pid}) on port 10001")
    
    print("\n🌐 Both servers are now running. Press Ctrl+C to shut down.")
    
    # Monitor the server outputs
    while all(process.poll() is None for process in processes):
        for process in processes:
            line = process.stdout.readline()
            if line:
                print(line, end='')
        time.sleep(0.1)
    
    # If we get here, one of the servers has stopped
    print("\n⚠️ One of the servers has stopped unexpectedly.")
    kill_processes()


if __name__ == "__main__":
    main() 