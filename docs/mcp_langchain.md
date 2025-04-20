LangChain MCP Adapters
This library provides a lightweight wrapper that makes Anthropic Model Context Protocol (MCP) tools compatible with LangChain and LangGraph.

MCP

Features
🛠️ Convert MCP tools into LangChain tools that can be used with LangGraph agents
📦 A client implementation that allows you to connect to multiple MCP servers and load tools from them
Installation
pip install langchain-mcp-adapters
Quickstart
Here is a simple example of using the MCP tools with a LangGraph agent.

pip install langchain-mcp-adapters langgraph langchain-openai

export OPENAI_API_KEY=<your_api_key>
Server
First, let's create an MCP server that can add and multiply numbers.

# math_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
Client
# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o")

server_params = StdioServerParameters(
    command="python",
    # Make sure to update to the full absolute path to your math_server.py file
    args=["/path/to/math_server.py"],
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize the connection
        await session.initialize()

        # Get tools
        tools = await load_mcp_tools(session)

        # Create and run the agent
        agent = create_react_agent(model, tools)
        agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
Multiple MCP Servers
The library also allows you to connect to multiple MCP servers and load tools from them:

Server
# math_server.py
...

# weather_server.py
from typing import List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"

if __name__ == "__main__":
    mcp.run(transport="sse")
python weather_server.py
Client
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o")

async with MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": ["/path/to/math_server.py"],
            "transport": "stdio",
        },
        "weather": {
            # make sure you start your weather server on port 8000
            "url": "http://localhost:8000/sse",
            "transport": "sse",
        }
    }
) as client:
    agent = create_react_agent(model, client.get_tools())
    math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
    weather_response = await agent.ainvoke({"messages": "what is the weather in nyc?"})
Using with LangGraph API Server
Tip

Check out this guide on getting started with LangGraph API server.

If you want to run a LangGraph agent that uses MCP tools in a LangGraph API server, you can use the following setup:

# graph.py
from contextlib import asynccontextmanager
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-3-5-sonnet-latest")

@asynccontextmanager
async def make_graph():
    async with MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": ["/path/to/math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                # make sure you start your weather server on port 8000
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        yield agent
In your langgraph.json make sure to specify make_graph as your graph entrypoint:

{
  "dependencies": ["."],
  "graphs": {
    "agent": "./graph.py:make_graph"
  }
}