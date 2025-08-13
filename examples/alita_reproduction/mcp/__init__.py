"""
MCP (Model Context Protocol) integration for ALITA reproduction.

This module provides MCP functionality for the ALITA system, including:
- ALITA-specific MCP server implementation
- Tool wrapper for converting scripts to MCP tools
- Tool persistence management
- Configuration management
"""

from .alita_mcp_server import ALITAMCPServer
from .tool_wrapper import ScriptToMCPWrapper
from .tool_persistence import MCPToolPersistence

__all__ = [
    'ALITAMCPServer',
    'ScriptToMCPWrapper', 
    'MCPToolPersistence'
]