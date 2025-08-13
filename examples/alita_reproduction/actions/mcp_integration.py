"""
MCP Integration Action for ALITA Manager Agent.

This module provides MCP integration capabilities for the Manager Agent,
including MCP tool discovery, registration, and execution coordination.
"""

import logging
import uuid
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

# Import ALITA MCP components
from examples.alita_reproduction.mcp import ALITAMCPServer, ScriptToMCPWrapper, MCPToolPersistence
from examples.alita_reproduction.utils.mcp_config_manager import MCPConfigManager

# Import EvoAgentX MCP toolkit
from evoagentx.tools import MCPToolkit

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPIntegrationAction:
    """
    MCP Integration Action for ALITA Manager Agent.
    
    This action provides MCP-related capabilities to the Manager Agent,
    including tool registration, discovery, and execution coordination.
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        persistence_dir: Optional[str] = None
    ):
        """
        Initialize the MCP Integration Action.
        
        Args:
            config_path: Path to MCP configuration file
            persistence_dir: Directory for MCP tool persistence
        """
        # Set up paths
        self.base_dir = Path(__file__).parent.parent
        
        # Initialize components
        self.config_manager = MCPConfigManager(config_path)
        self.persistence_manager = MCPToolPersistence(persistence_dir)
        self.script_wrapper = ScriptToMCPWrapper(str(self.base_dir))
        
        # Initialize ALITA MCP server
        tools_dir = self.config_manager.get_directory("generated_scripts")
        registry_file = self.config_manager.get_directory("tools_registry")
        
        self.alita_server = ALITAMCPServer(
            server_name="alita-tools",
            tools_dir=str(tools_dir) if tools_dir else None,
            persistence_file=str(registry_file) if registry_file else None
        )
        
        # EvoAgentX MCP toolkit for external MCP servers
        self._external_mcp_toolkit: Optional[MCPToolkit] = None
        self._available_external_tools: List[Any] = []
        
        logger.info("MCP Integration Action initialized")
        logger.info(f"ALITA MCP server: {self.alita_server.server_name}")
        logger.info(f"Persistence directory: {self.persistence_manager.persistence_dir}")
    
    def initialize_external_mcp_connection(self) -> Dict[str, Any]:
        """
        Initialize connection to external MCP servers using EvoAgentX MCPToolkit.
        
        Returns:
            Dict with initialization result
        """
        logger.info("Initializing external MCP connections")
        
        try:
            # Get MCP servers configuration
            config = self.config_manager.create_evoagentx_compatible_config()
            
            # Initialize MCPToolkit if there are external servers
            external_servers = {k: v for k, v in config.get("mcpServers", {}).items() 
                              if k != "alita-tools"}
            
            if external_servers:
                external_config = {"mcpServers": external_servers}
                self._external_mcp_toolkit = MCPToolkit(config=external_config)
                self._available_external_tools = self._external_mcp_toolkit.get_toolkits()
                
                logger.info(f"Connected to {len(external_servers)} external MCP servers")
                logger.info(f"Available external tools: {len(self._available_external_tools)}")
            else:
                logger.info("No external MCP servers configured")
            
            return {
                "success": True,
                "external_servers": len(external_servers),
                "external_tools": len(self._available_external_tools),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error initializing external MCP connections: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "external_servers": 0,
                "external_tools": 0
            }
    
    def register_script_as_mcp_tool(
        self,
        script_path: str,
        tool_name: Optional[str] = None,
        tool_description: Optional[str] = None,
        custom_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a Python script as an MCP tool.
        
        Args:
            script_path: Path to the Python script
            tool_name: Custom tool name
            tool_description: Custom tool description
            custom_parameters: Custom parameters schema
            
        Returns:
            Registration result dictionary
        """
        logger.info(f"Registering script as MCP tool: {script_path}")
        
        try:
            # Wrap the script
            tool_spec = self.script_wrapper.wrap_script(
                script_path, tool_name, tool_description, custom_parameters
            )
            
            # Register with ALITA MCP server
            server_result = self.alita_server.register_script_as_tool(
                script_path=tool_spec.script_path,
                tool_name=tool_spec.name,
                description=tool_spec.description,
                parameters=tool_spec.parameters,
                metadata=tool_spec.metadata
            )
            
            if not server_result["success"]:
                return server_result
            
            # Persist the tool
            auto_backup = self.config_manager.get_setting("backup_scripts_on_registration", True)
            persistence_result = self.persistence_manager.persist_tool(
                tool_id=server_result["tool_id"],
                name=tool_spec.name,
                description=tool_spec.description,
                script_path=tool_spec.script_path,
                parameters=tool_spec.parameters,
                metadata=tool_spec.metadata,
                backup_script=auto_backup
            )
            
            if persistence_result["success"]:
                logger.info(f"MCP tool registered and persisted successfully: {tool_spec.name}")
            else:
                logger.warning(f"Tool registered but persistence failed: {persistence_result['error']}")
            
            return {
                "success": True,
                "tool_id": server_result["tool_id"],
                "tool_name": tool_spec.name,
                "script_path": script_path,
                "persisted": persistence_result["success"],
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error registering script as MCP tool: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_path": script_path
            }
    
    def discover_available_tools(self) -> Dict[str, Any]:
        """
        Discover all available MCP tools (both ALITA and external).
        
        Returns:
            Dictionary containing discovered tools
        """
        logger.info("Discovering available MCP tools")
        
        try:
            # Get ALITA tools
            alita_tools = self.alita_server.list_tools()
            
            # Get external tools if available
            external_tools = []
            if self._external_mcp_toolkit:
                try:
                    external_toolkits = self._external_mcp_toolkit.get_toolkits()
                    for toolkit in external_toolkits:
                        for tool in toolkit.tools:
                            external_tools.append({
                                "name": tool.name,
                                "description": tool.description,
                                "source": "external",
                                "toolkit": toolkit.name
                            })
                except Exception as e:
                    logger.warning(f"Error getting external tools: {str(e)}")
            
            # Combine all tools
            all_tools = {
                "alita_tools": alita_tools,
                "external_tools": external_tools,
                "total_tools": alita_tools["tools_count"] + len(external_tools)
            }
            
            logger.info(f"Discovered {all_tools['total_tools']} total MCP tools")
            return all_tools
            
        except Exception as e:
            error_msg = f"Error discovering MCP tools: {str(e)}"
            logger.error(error_msg)
            return {
                "alita_tools": {"tools_count": 0, "tools": {}},
                "external_tools": [],
                "total_tools": 0,
                "error": error_msg
            }
    
    def execute_mcp_tool(
        self,
        tool_name: str,
        tool_args: Optional[Dict[str, Any]] = None,
        source: str = "auto"
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments to pass to the tool
            source: Tool source ("alita", "external", "auto")
            
        Returns:
            Tool execution result
        """
        logger.info(f"Executing MCP tool: {tool_name} (source: {source})")
        
        tool_args = tool_args or {}
        
        try:
            # Try ALITA tools first (if source is auto or alita)
            if source in ["auto", "alita"]:
                alita_tools = self.alita_server.list_tools()
                if tool_name in alita_tools["tools"]:
                    logger.info(f"Executing ALITA tool: {tool_name}")
                    
                    # Record usage
                    tool_info = alita_tools["tools"][tool_name]
                    self.persistence_manager.increment_usage(tool_info["id"])
                    
                    # Execute the tool
                    result = self.alita_server.execute_tool(tool_name, **tool_args)
                    result["source"] = "alita"
                    result["tool_id"] = tool_info["id"]
                    return result
            
            # Try external tools (if source is auto or external)
            if source in ["auto", "external"] and self._external_mcp_toolkit:
                logger.info(f"Searching for external tool: {tool_name}")
                
                for toolkit in self._available_external_tools:
                    for tool in toolkit.tools:
                        if tool.name == tool_name:
                            logger.info(f"Executing external tool: {tool_name} from {toolkit.name}")
                            
                            try:
                                result = tool(**tool_args)
                                return {
                                    "success": True,
                                    "result": result,
                                    "source": "external",
                                    "toolkit": toolkit.name,
                                    "tool_name": tool_name,
                                    "error": None
                                }
                            except Exception as e:
                                return {
                                    "success": False,
                                    "error": f"Error executing external tool: {str(e)}",
                                    "source": "external",
                                    "toolkit": toolkit.name,
                                    "tool_name": tool_name
                                }
            
            # Tool not found
            available_tools = self.discover_available_tools()
            alita_tool_names = list(available_tools["alita_tools"]["tools"].keys())
            external_tool_names = [tool["name"] for tool in available_tools["external_tools"]]
            
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "available_alita_tools": alita_tool_names,
                "available_external_tools": external_tool_names,
                "tool_name": tool_name
            }
            
        except Exception as e:
            error_msg = f"Error executing MCP tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "tool_name": tool_name
            }
    
    def find_suitable_tool(self, task_description: str) -> Dict[str, Any]:
        """
        Find suitable MCP tools for a given task description.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Dictionary containing suitable tools and recommendations
        """
        logger.info(f"Finding suitable tools for task: {task_description[:100]}...")
        
        try:
            available_tools = self.discover_available_tools()
            suitable_tools = []
            
            # Simple keyword matching for tool discovery
            task_lower = task_description.lower()
            
            # Check ALITA tools
            for tool_name, tool_info in available_tools["alita_tools"]["tools"].items():
                tool_desc_lower = tool_info["description"].lower()
                
                # Basic keyword matching
                relevance_score = 0
                for word in task_lower.split():
                    if len(word) > 3:  # Skip very short words
                        if word in tool_desc_lower:
                            relevance_score += 2
                        elif word in tool_name.lower():
                            relevance_score += 3
                
                if relevance_score > 0:
                    suitable_tools.append({
                        "name": tool_name,
                        "description": tool_info["description"],
                        "source": "alita",
                        "relevance_score": relevance_score,
                        "tool_id": tool_info["id"]
                    })
            
            # Check external tools
            for tool_info in available_tools["external_tools"]:
                tool_desc_lower = tool_info["description"].lower()
                
                relevance_score = 0
                for word in task_lower.split():
                    if len(word) > 3:
                        if word in tool_desc_lower:
                            relevance_score += 2
                        elif word in tool_info["name"].lower():
                            relevance_score += 3
                
                if relevance_score > 0:
                    suitable_tools.append({
                        "name": tool_info["name"],
                        "description": tool_info["description"],
                        "source": "external",
                        "toolkit": tool_info["toolkit"],
                        "relevance_score": relevance_score
                    })
            
            # Sort by relevance score
            suitable_tools.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Determine recommendation
            if suitable_tools:
                best_tool = suitable_tools[0]
                recommendation = f"Consider using '{best_tool['name']}' (score: {best_tool['relevance_score']})"
            else:
                recommendation = "No existing tools found. Consider generating a new script."
            
            result = {
                "suitable_tools": suitable_tools[:5],  # Top 5 matches
                "total_matches": len(suitable_tools),
                "recommendation": recommendation,
                "needs_new_tool": len(suitable_tools) == 0,
                "task_description": task_description
            }
            
            logger.info(f"Found {len(suitable_tools)} suitable tools")
            return result
            
        except Exception as e:
            error_msg = f"Error finding suitable tools: {str(e)}"
            logger.error(error_msg)
            return {
                "suitable_tools": [],
                "total_matches": 0,
                "recommendation": "Error occurred during tool search",
                "needs_new_tool": True,
                "error": error_msg
            }
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """
        Get overall MCP integration status.
        
        Returns:
            Dictionary containing MCP status information
        """
        try:
            # Get component status
            alita_tools = self.alita_server.list_tools()
            persistence_stats = self.persistence_manager.get_statistics()
            config_validation = self.config_manager.validate_config()
            
            # Get external connection status
            external_status = {
                "connected": self._external_mcp_toolkit is not None,
                "tools_count": len(self._available_external_tools)
            }
            
            return {
                "alita_server": {
                    "name": self.alita_server.server_name,
                    "tools_count": alita_tools["tools_count"],
                    "status": "active"
                },
                "persistence": {
                    "total_tools": persistence_stats["total_tools"],
                    "active_tools": persistence_stats["active_tools"],
                    "total_usage": persistence_stats["total_usage"]
                },
                "external_connections": external_status,
                "configuration": {
                    "valid": config_validation["is_valid"],
                    "errors": len(config_validation["errors"]),
                    "warnings": len(config_validation["warnings"])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting MCP status: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_old_tools(self, days: int = 30) -> Dict[str, Any]:
        """
        Clean up old, unused MCP tools.
        
        Args:
            days: Remove tools not used in this many days
            
        Returns:
            Cleanup result dictionary
        """
        logger.info(f"Cleaning up tools not used in {days} days")
        
        try:
            # Clean up old backups
            backup_cleanup = self.persistence_manager.cleanup_old_backups(days)
            
            # Could add more cleanup logic here (unused tools, etc.)
            
            return {
                "success": True,
                "backup_cleanup": backup_cleanup,
                "days_threshold": days,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error during cleanup: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "days_threshold": days
            }
    
    def disconnect_mcp_connections(self) -> None:
        """Disconnect from all MCP connections."""
        logger.info("Disconnecting MCP connections")
        
        try:
            if self._external_mcp_toolkit:
                self._external_mcp_toolkit.disconnect()
                self._external_mcp_toolkit = None
                self._available_external_tools.clear()
                logger.info("External MCP connections disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting MCP connections: {str(e)}")