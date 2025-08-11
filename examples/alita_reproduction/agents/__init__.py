"""
ALITA Agents package.

This package contains the core agent implementations for the ALITA reproduction:
- ManagerAgent: Central coordinator and task dispatcher
- WebAgent: Information retrieval and web search 
- MCPCreationAgent: MCP tool creation and management
"""

from .manager_agent import ManagerAgent

__all__ = [
    "ManagerAgent"
]