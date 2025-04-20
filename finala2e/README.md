# A2E Math & Currency Agent

This is a final implementation of an Agent-to-Everything (A2E) agent that combines multiple capabilities:

1. Math operations (addition, multiplication)
2. Currency conversion

## Architecture

The agent uses LangGraph with the Gemini model and connects to MCP (Model Context Protocol) servers to access the tools needed for math operations and currency conversion.

## Setup

1. Ensure you have set up the `GOOGLE_API_KEY` environment variable
2. Start the required A2A servers and MCP servers

### Starting the Required Servers

For the MCP servers to function properly, they need access to the underlying A2A servers. We've provided a helper script to start these servers:

```bash
# Start the A2A servers (keep this running in a separate terminal)
python -m finala2e.start_servers
```

This will start:
- Currency Agent server on port 10000
- Math Agent server on port 10001

Once these servers are running, the MCP servers will be able to connect to them when the A2E agent is initialized.

## Running the Agent

### Direct Testing via Client

You can test the agent directly using the client_stdio.py script:

```bash
# Run a single query
python -m finala2e.client_stdio --query "What is 5 + 7?"

# Start an interactive chat session
python -m finala2e.client_stdio --chat
```

### Running as an A2A Server

You can run the agent as an A2A-compatible server:

```bash
# Make sure start_servers.py is running in another terminal first
python -m finala2e
```

By default, the server runs on localhost:10001. You can specify a different host and port:

```bash
python -m finala2e --host 0.0.0.0 --port 8000
```

## Features

- Uses LangGraph for agent orchestration
- Connects to MCP servers for tools
- Supports streaming responses
- Handles push notifications
- A2A-compatible server

## Troubleshooting

If you encounter issues with the MCP tool connections:

1. Make sure the start_servers.py script is running and has successfully started both the Currency and Math A2A servers
2. Check that the ports 10000 and 10001 are not in use by other applications
3. Verify that your GOOGLE_API_KEY is valid and set correctly 