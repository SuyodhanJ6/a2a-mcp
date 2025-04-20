# MCP Integration with A2A Agents

This directory contains an example of integrating A2A protocol agents with the Model Context Protocol (MCP) framework.

## Overview

The implementation demonstrates how to:

1. Create MCP servers that wrap existing A2A protocol agents
2. Connect to these MCP servers using both STDIO and SSE transports
3. Use the MCP tools with LangGraph agents

## Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

You will also need to ensure that your A2A agents are running on their respective ports:
- Currency Agent: http://localhost:10000
- Math Agent: http://localhost:10001

## Directory Structure

```
test_mcp/
├── client/
│   ├── client_stdio.py   # Client using STDIO transport
│   └── client_sse.py     # Client using SSE transport
├── server/
│   ├── currency_server.py   # MCP Server wrapping the Currency A2A Agent
│   └── math_server.py       # MCP Server wrapping the Math A2A Agent
├── start_sse_servers.py  # Helper script to start SSE servers
├── requirements.txt      # Required dependencies
└── README.md             # This file
```

## Usage

### Using STDIO Transport

The STDIO transport starts the MCP servers as child processes and communicates with them via standard input/output.

```bash
# Run with a specific query
python client/client_stdio.py --query "What is 5 + 7?"

# Run in interactive chat mode
python client/client_stdio.py --chat
```

### Using SSE Transport

The SSE (Server-Sent Events) transport requires the MCP servers to be running as HTTP servers.

1. First, start the SSE servers:

```bash
python start_sse_servers.py
```

2. Then, in another terminal, run the client:

```bash
# Run with a specific query
python client/client_sse.py --query "What is 5 + 7?"

# Run in interactive chat mode
python client/client_sse.py --chat
```

## Example Queries

Here are some example queries you can try:

- "What is 7 + 12?"
- "Multiply 8 and 15"
- "What is the exchange rate between USD and EUR?"
- "Convert 100 USD to JPY"
- "Add 23 and 45, then convert the result from USD to GBP"

## Troubleshooting

If you encounter errors:

1. Ensure that the A2A agents are running on their respective ports
2. Check that you have installed all required dependencies
3. Make sure the MCP servers are running (for SSE transport)
4. Set the GOOGLE_API_KEY environment variable if using the Google Gemini model 