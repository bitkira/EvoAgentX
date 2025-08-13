"""
MCP Configuration Manager.

This module provides functionality to manage MCP server configurations
and integration settings for the ALITA system.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPConfigManager:
    """
    MCP Configuration Manager for ALITA.
    
    This class manages MCP server configurations, settings, and integration
    parameters for the ALITA system.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MCP configuration manager.
        
        Args:
            config_path: Path to the MCP configuration file
        """
        # Set up paths
        self.base_dir = Path(__file__).parent.parent
        self.config_path = Path(config_path) if config_path else self.base_dir / "config" / "mcp_config.json"
        
        # Configuration data
        self.config_data: Dict[str, Any] = {}
        
        # Load configuration
        self._load_config()
        
        logger.info(f"MCPConfigManager initialized")
        logger.info(f"Configuration file: {self.config_path}")
    
    def _load_config(self) -> None:
        """Load MCP configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                logger.info(f"MCP configuration loaded successfully")
            else:
                # Create default configuration
                self._create_default_config()
                logger.info("Created default MCP configuration")
                
        except Exception as e:
            logger.error(f"Error loading MCP configuration: {str(e)}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default MCP configuration."""
        self.config_data = {
            "mcpServers": {
                "alita-tools": {
                    "command": "python",
                    "args": [
                        "-m",
                        "examples.alita_reproduction.mcp.alita_mcp_server"
                    ],
                    "env": {
                        "PYTHONPATH": str(Path(__file__).parent.parent.parent)
                    },
                    "timeout": 120.0,
                    "description": "ALITA dynamic tools MCP server"
                }
            },
            "settings": {
                "auto_register_generated_scripts": True,
                "backup_scripts_on_registration": True,
                "cleanup_old_backups_days": 30,
                "max_concurrent_tools": 50,
                "tool_execution_timeout": 60
            },
            "directories": {
                "generated_scripts": "generated_scripts",
                "mcp_persistence": "mcp_persistence",
                "tools_registry": "mcp/tools_registry.json"
            }
        }
        
        # Save default configuration
        self._save_config()
    
    def _save_config(self) -> None:
        """Save MCP configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            logger.debug("MCP configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving MCP configuration: {str(e)}")
    
    def get_mcp_servers_config(self) -> Dict[str, Any]:
        """
        Get MCP servers configuration for use with EvoAgentX MCPToolkit.
        
        Returns:
            MCP servers configuration dictionary
        """
        return self.config_data.get("mcpServers", {})
    
    def get_full_config(self) -> Dict[str, Any]:
        """
        Get complete MCP configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config_data.copy()
    
    def get_setting(self, setting_name: str, default_value: Any = None) -> Any:
        """
        Get a specific setting value.
        
        Args:
            setting_name: Name of the setting
            default_value: Default value if setting not found
            
        Returns:
            Setting value
        """
        return self.config_data.get("settings", {}).get(setting_name, default_value)
    
    def set_setting(self, setting_name: str, value: Any) -> None:
        """
        Set a specific setting value.
        
        Args:
            setting_name: Name of the setting
            value: Value to set
        """
        if "settings" not in self.config_data:
            self.config_data["settings"] = {}
        
        self.config_data["settings"][setting_name] = value
        self._save_config()
        
        logger.info(f"Setting updated: {setting_name} = {value}")
    
    def get_directory(self, dir_name: str) -> Optional[Path]:
        """
        Get a directory path from configuration.
        
        Args:
            dir_name: Directory name key
            
        Returns:
            Path object or None if not found
        """
        directories = self.config_data.get("directories", {})
        if dir_name in directories:
            dir_path = directories[dir_name]
            if not Path(dir_path).is_absolute():
                return self.base_dir / dir_path
            else:
                return Path(dir_path)
        return None
    
    def set_directory(self, dir_name: str, path: Union[str, Path]) -> None:
        """
        Set a directory path in configuration.
        
        Args:
            dir_name: Directory name key
            path: Directory path
        """
        if "directories" not in self.config_data:
            self.config_data["directories"] = {}
        
        self.config_data["directories"][dir_name] = str(path)
        self._save_config()
        
        logger.info(f"Directory updated: {dir_name} = {path}")
    
    def add_mcp_server(
        self,
        server_name: str,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: float = 120.0,
        description: Optional[str] = None
    ) -> None:
        """
        Add a new MCP server configuration.
        
        Args:
            server_name: Name of the MCP server
            command: Command to start the server
            args: Command arguments
            env: Environment variables
            timeout: Connection timeout
            description: Server description
        """
        if "mcpServers" not in self.config_data:
            self.config_data["mcpServers"] = {}
        
        server_config = {
            "command": command,
            "timeout": timeout
        }
        
        if args:
            server_config["args"] = args
        
        if env:
            server_config["env"] = env
        
        if description:
            server_config["description"] = description
        
        self.config_data["mcpServers"][server_name] = server_config
        self._save_config()
        
        logger.info(f"MCP server added: {server_name}")
    
    def remove_mcp_server(self, server_name: str) -> bool:
        """
        Remove an MCP server configuration.
        
        Args:
            server_name: Name of the MCP server to remove
            
        Returns:
            True if server was removed, False if not found
        """
        mcp_servers = self.config_data.get("mcpServers", {})
        if server_name in mcp_servers:
            del self.config_data["mcpServers"][server_name]
            self._save_config()
            logger.info(f"MCP server removed: {server_name}")
            return True
        else:
            logger.warning(f"MCP server not found: {server_name}")
            return False
    
    def update_mcp_server(self, server_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update an MCP server configuration.
        
        Args:
            server_name: Name of the MCP server
            updates: Dictionary of updates to apply
            
        Returns:
            True if server was updated, False if not found
        """
        mcp_servers = self.config_data.get("mcpServers", {})
        if server_name in mcp_servers:
            self.config_data["mcpServers"][server_name].update(updates)
            self._save_config()
            logger.info(f"MCP server updated: {server_name}")
            return True
        else:
            logger.warning(f"MCP server not found: {server_name}")
            return False
    
    def list_mcp_servers(self) -> List[Dict[str, Any]]:
        """
        List all configured MCP servers.
        
        Returns:
            List of server information dictionaries
        """
        servers = []
        mcp_servers = self.config_data.get("mcpServers", {})
        
        for server_name, server_config in mcp_servers.items():
            server_info = {
                "name": server_name,
                "command": server_config.get("command", ""),
                "args": server_config.get("args", []),
                "env": server_config.get("env", {}),
                "timeout": server_config.get("timeout", 120.0),
                "description": server_config.get("description", "")
            }
            servers.append(server_info)
        
        return servers
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the current MCP configuration.
        
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required sections
        required_sections = ["mcpServers", "settings", "directories"]
        for section in required_sections:
            if section not in self.config_data:
                validation_result["errors"].append(f"Missing required section: {section}")
                validation_result["is_valid"] = False
        
        # Validate MCP servers
        mcp_servers = self.config_data.get("mcpServers", {})
        if not mcp_servers:
            validation_result["warnings"].append("No MCP servers configured")
        
        for server_name, server_config in mcp_servers.items():
            if "command" not in server_config:
                validation_result["errors"].append(f"MCP server '{server_name}' missing command")
                validation_result["is_valid"] = False
        
        # Validate directories
        directories = self.config_data.get("directories", {})
        for dir_name, dir_path in directories.items():
            full_path = self.get_directory(dir_name)
            if full_path and not full_path.parent.exists():
                validation_result["warnings"].append(f"Parent directory for '{dir_name}' does not exist: {full_path.parent}")
        
        # Validate settings
        settings = self.config_data.get("settings", {})
        if "tool_execution_timeout" in settings:
            timeout = settings["tool_execution_timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                validation_result["errors"].append("tool_execution_timeout must be a positive number")
                validation_result["is_valid"] = False
        
        logger.info(f"Configuration validation completed: {'VALID' if validation_result['is_valid'] else 'INVALID'}")
        return validation_result
    
    def create_evoagentx_compatible_config(self) -> Dict[str, Any]:
        """
        Create EvoAgentX MCPToolkit compatible configuration.
        
        Returns:
            Configuration dictionary for EvoAgentX MCPToolkit
        """
        mcp_servers = self.config_data.get("mcpServers", {})
        
        # Format for EvoAgentX MCPToolkit
        config = {
            "mcpServers": mcp_servers
        }
        
        return config
    
    def export_config(self, export_path: str) -> Dict[str, Any]:
        """
        Export configuration to a file.
        
        Args:
            export_path: Path to export the configuration
            
        Returns:
            Export result
        """
        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration exported to: {export_path}")
            
            return {
                "success": True,
                "export_path": str(export_path),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error exporting configuration: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def import_config(self, import_path: str, merge: bool = False) -> Dict[str, Any]:
        """
        Import configuration from a file.
        
        Args:
            import_path: Path to import the configuration from
            merge: Whether to merge with existing config or replace
            
        Returns:
            Import result
        """
        try:
            import_path = Path(import_path)
            if not import_path.exists():
                return {
                    "success": False,
                    "error": f"Configuration file not found: {import_path}"
                }
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            if merge:
                # Merge configurations
                for key, value in imported_config.items():
                    if isinstance(value, dict) and key in self.config_data:
                        self.config_data[key].update(value)
                    else:
                        self.config_data[key] = value
            else:
                # Replace configuration
                self.config_data = imported_config
            
            # Save the updated configuration
            self._save_config()
            
            logger.info(f"Configuration imported from: {import_path}")
            
            return {
                "success": True,
                "import_path": str(import_path),
                "merge_mode": merge,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error importing configuration: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }