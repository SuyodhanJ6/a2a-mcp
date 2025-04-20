# 🤖 A2A-to-Everything (A2E) with LangGraph 🤖

This project demonstrates an Agent-to-Everything (A2E) implementation that combines multiple capabilities through the A2A protocol. It showcases how specialized agents can be used as tools by a central orchestrating agent using [LangGraph](https://langchain-ai.github.io/langgraph/) and the [Model Context Protocol (MCP)](https://github.com/google/model-context-protocol).

## Project Structure

The repository is organized into the following components:

- `finala2e/`: The main A2E implementation combining math and currency capabilities
- `graph/`: Core LangGraph agent implementation with A2A tool integration
- `test_mcp/`: MCP server implementations and testing clients

## Prerequisites

- Python 3.10 or higher
- Google API Key for Gemini model
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (optional, for containerized deployment)

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/a2a-langgraph.git
   cd a2a-langgraph
   ```

2. Create an environment file with your API key:

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3. Install dependencies with uv:

   ```bash
   uv pip install .
   ```

## Running the A2E Agent

### Start the Required Servers

First, start the component A2A servers:

```bash
# Start the Currency and Math A2A servers (keep running in a separate terminal)
uv run -m finala2e.start_servers
```

This starts:
- Currency Agent server on port 10000
- Math Agent server on port 10001

### Run the A2E Server

In a separate terminal, run the A2E agent as an A2A-compatible server:

```bash
uv run -m finala2e
```

By default, the server runs on localhost:10003. You can specify a different host and port:

```bash
uv run -m finala2e --host 0.0.0.0 --port 8000
```

### Direct Testing with the Client

You can test the agent directly using the client:

```bash
# Run a single query
uv run -m finala2e.client_stdio --query "What is 5 + 7?"

# Start an interactive chat session
uv run -m finala2e.client_stdio --chat
```

## MCP Integration

The `test_mcp` directory provides examples of integrating A2A agents with MCP.

### Start MCP Servers

```bash
uv run test_mcp/start_sse_servers.py
```

### Using STDIO Transport Client

```bash
# Run with a specific query
uv run test_mcp/client/client_stdio.py --query "What is 5 + 7?"

# Run in interactive chat mode
uv run test_mcp/client/client_stdio.py --chat
```

### Using SSE Transport Client

```bash
# Run with a specific query
uv run test_mcp/client/client_sse.py --query "What is 5 + 7?"

# Run in interactive chat mode
uv run test_mcp/client/client_sse.py --chat
```

## Technical Implementation

- **LangGraph ReAct Agent**: Uses the ReAct pattern for reasoning and tool usage
- **MCP Integration**: Connects to A2A agents via Model Context Protocol
- **A2A Tools**: Specialized tools for math and currency operations
- **Streaming Support**: Provides incremental updates during processing
- **Checkpoint Memory**: Maintains conversation state between turns
- **Push Notification System**: Webhook-based updates with JWK authentication

## Example Queries

- "What is 7 + 12?"
- "Multiply 8 and 15"
- "What is the exchange rate between USD and EUR?"
- "Convert 100 USD to JPY"
- "Add 23 and 45, then convert the result from USD to GBP"

## Docker Deployment (Optional)

```bash
# Build Image
docker build -t a2a-langgraph .

# Run Image
docker run -p 10003:10003 -e GOOGLE_API_KEY=your_api_key_here --name a2e a2a-langgraph

# Check Logs
docker logs -f a2e
```

## Troubleshooting

If you encounter issues:

1. Make sure the start_servers.py script is running and has successfully started both the Currency and Math A2A servers
2. Check that the ports 10000, 10001, and 10003 are not in use by other applications
3. Verify that your GOOGLE_API_KEY is valid and set correctly
4. For MCP tool connections, ensure the MCP servers are running (for SSE transport)

## Learn More

- [A2A Protocol Documentation](https://google.github.io/A2A/#/documentation)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Model Context Protocol](https://github.com/google/model-context-protocol)
- [Google Gemini API](https://ai.google.dev/gemini-api)
