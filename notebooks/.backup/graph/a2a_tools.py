"""
A2A Tools to call the Currency and Math Agents

This module provides tools that call A2A protocol-compatible agents.
"""

import json
import uuid
import httpx
from typing import Dict, Any, Optional, List, ClassVar, Type
from langchain_core.tools import BaseTool
from pydantic import Field

class A2ABaseTool(BaseTool):
    """Base tool for calling A2A protocol-compatible agents."""
    
    host: str = Field(default="localhost")
    port: int = Field(default=8000)
    session_id: Optional[str] = Field(default=None)
    
    def _init_session(self) -> str:
        """Initialize a session ID if it doesn't exist."""
        if not self.session_id:
            self.session_id = uuid.uuid4().hex
        return self.session_id
    
    def _call_agent(self, prompt: str) -> str:
        """Call the A2A agent with the provided prompt.
        
        Args:
            prompt: The text prompt to send to the agent.
            
        Returns:
            The agent's response text.
        """
        session_id = self._init_session()
        task_id = uuid.uuid4().hex
        
        url = f"http://{self.host}:{self.port}"
        
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
                            "text": prompt
                        }
                    ]
                }
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            
            # Extract the content from the response
            if "result" in result:
                if "artifacts" in result["result"] and result["result"]["artifacts"]:
                    return result["result"]["artifacts"][0]["parts"][0]["text"]
                elif "status" in result["result"] and result["result"]["status"].get("message"):
                    return result["result"]["status"]["message"]["parts"][0]["text"]
            
            # If we couldn't find the expected content, return the raw result
            return f"Unexpected response format: {json.dumps(result)}"
            
        except httpx.HTTPError as e:
            return f"Error calling A2A agent: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

class CurrencyTool(A2ABaseTool):
    """Tool for currency conversions using the Currency A2A Agent."""
    
    name: ClassVar[str] = "currency_tool"
    description: ClassVar[str] = """
    Use this tool when you need to get currency exchange rates or convert amounts between different currencies.
    The input should be a natural language query about currency conversion.
    Examples:
    - "What is the exchange rate between USD and EUR?"
    - "How much is 100 USD in Japanese Yen?"
    - "Convert 50 Euros to Indian Rupees"
    """
    
    host: str = Field(default="localhost")
    port: int = Field(default=10000)
    
    def _run(self, query: str) -> str:
        """Execute the currency tool with the given query."""
        return self._call_agent(query)


class MathTool(A2ABaseTool):
    """Tool for mathematical operations using the Math A2A Agent."""
    
    name: ClassVar[str] = "math_tool"
    description: ClassVar[str] = """
    Use this tool for mathematical calculations, specifically addition and multiplication.
    The input should be a natural language query about math operations.
    Examples:
    - "What is 24 + 56?"
    - "Calculate 18 * 7"
    - "Add 123 and 456, then multiply by 2"
    """
    
    host: str = Field(default="localhost")
    port: int = Field(default=10001)
    
    def _run(self, query: str) -> str:
        """Execute the math tool with the given query."""
        return self._call_agent(query) 