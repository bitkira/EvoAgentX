"""
MCP Tool Persistence Management.

This module provides functionality for persisting MCP tools and their metadata
using a simplified file-based approach with JSON storage.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PersistedTool:
    """Represents a persisted MCP tool."""
    id: str
    name: str
    description: str
    script_path: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str
    last_modified: str
    version: str = "1.0.0"
    status: str = "active"
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersistedTool":
        """Create instance from dictionary."""
        return cls(**data)


class MCPToolPersistence:
    """
    MCP Tool Persistence Manager.
    
    This class manages the persistence of MCP tools and their metadata
    using a file-based approach with JSON storage for simplicity and reliability.
    """
    
    def __init__(
        self,
        persistence_dir: Optional[str] = None,
        registry_file: str = "tools_registry.json",
        scripts_backup_dir: str = "scripts_backup"
    ):
        """
        Initialize the persistence manager.
        
        Args:
            persistence_dir: Directory for persistence files
            registry_file: Name of the registry file
            scripts_backup_dir: Directory for script backups
        """
        # Set up directories
        self.base_dir = Path(__file__).parent.parent
        self.persistence_dir = Path(persistence_dir) if persistence_dir else self.base_dir / "mcp_persistence"
        self.registry_file = self.persistence_dir / registry_file
        self.scripts_backup_dir = self.persistence_dir / scripts_backup_dir
        self.metadata_dir = self.persistence_dir / "metadata"
        
        # Ensure directories exist
        self.persistence_dir.mkdir(exist_ok=True)
        self.scripts_backup_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
        
        # In-memory registry
        self.tools_registry: Dict[str, PersistedTool] = {}
        
        # Load existing tools
        self._load_registry()
        
        logger.info(f"MCPToolPersistence initialized")
        logger.info(f"Persistence directory: {self.persistence_dir}")
        logger.info(f"Registry file: {self.registry_file}")
        logger.info(f"Loaded {len(self.tools_registry)} persisted tools")
    
    def _load_registry(self) -> None:
        """Load tools registry from persistence file."""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)
                
                # Convert dictionary entries to PersistedTool objects
                tools_data = registry_data.get('tools', {})
                for tool_id, tool_data in tools_data.items():
                    try:
                        tool = PersistedTool.from_dict(tool_data)
                        self.tools_registry[tool_id] = tool
                    except Exception as e:
                        logger.warning(f"Error loading tool {tool_id}: {str(e)}")
                
                logger.info(f"Loaded {len(self.tools_registry)} tools from registry")
            else:
                logger.info("No existing registry found, starting with empty registry")
                
        except Exception as e:
            logger.error(f"Error loading tools registry: {str(e)}")
            self.tools_registry = {}
    
    def _save_registry(self) -> None:
        """Save tools registry to persistence file."""
        try:
            # Convert PersistedTool objects to dictionaries
            tools_data = {}
            for tool_id, tool in self.tools_registry.items():
                tools_data[tool_id] = tool.to_dict()
            
            registry_data = {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "tools_count": len(self.tools_registry),
                "tools": tools_data
            }
            
            # Write to temporary file first, then rename for atomic operation
            temp_file = self.registry_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_file.replace(self.registry_file)
            
            logger.debug(f"Registry saved: {len(self.tools_registry)} tools")
            
        except Exception as e:
            logger.error(f"Error saving tools registry: {str(e)}")
    
    def persist_tool(
        self,
        tool_id: str,
        name: str,
        description: str,
        script_path: str,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        backup_script: bool = True
    ) -> Dict[str, Any]:
        """
        Persist an MCP tool.
        
        Args:
            tool_id: Unique tool identifier
            name: Tool name
            description: Tool description
            script_path: Path to the script file
            parameters: Tool parameters schema
            metadata: Additional metadata
            backup_script: Whether to create a backup of the script
            
        Returns:
            Result dictionary
        """
        logger.info(f"Persisting MCP tool: {name} (ID: {tool_id})")
        
        try:
            script_path = Path(script_path)
            if not script_path.exists():
                return {
                    "success": False,
                    "error": f"Script file not found: {script_path}",
                    "tool_id": tool_id
                }
            
            # Create backup of script if requested
            backup_path = None
            if backup_script:
                backup_path = self._backup_script(script_path, tool_id)
            
            # Create persisted tool object
            now = datetime.now().isoformat()
            persisted_tool = PersistedTool(
                id=tool_id,
                name=name,
                description=description,
                script_path=str(script_path.absolute()),
                parameters=parameters,
                metadata=metadata or {},
                created_at=now,
                last_modified=now
            )
            
            # Add backup path to metadata if created
            if backup_path:
                persisted_tool.metadata["backup_path"] = str(backup_path)
            
            # Store in registry
            self.tools_registry[tool_id] = persisted_tool
            
            # Save individual tool metadata
            self._save_tool_metadata(tool_id, persisted_tool)
            
            # Save registry
            self._save_registry()
            
            logger.info(f"Tool persisted successfully: {name}")
            
            return {
                "success": True,
                "tool_id": tool_id,
                "name": name,
                "backup_path": backup_path,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error persisting tool: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "tool_id": tool_id
            }
    
    def _backup_script(self, script_path: Path, tool_id: str) -> Path:
        """
        Create a backup of the script file.
        
        Args:
            script_path: Path to the original script
            tool_id: Tool identifier for backup naming
            
        Returns:
            Path to the backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{tool_id}_{timestamp}_{script_path.name}"
        backup_path = self.scripts_backup_dir / backup_name
        
        shutil.copy2(script_path, backup_path)
        logger.debug(f"Script backed up: {backup_path}")
        
        return backup_path
    
    def _save_tool_metadata(self, tool_id: str, tool: PersistedTool) -> None:
        """Save individual tool metadata to separate file."""
        metadata_file = self.metadata_dir / f"{tool_id}.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(tool.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_tool(self, tool_id: str) -> Optional[PersistedTool]:
        """
        Load a persisted tool by ID.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            PersistedTool object or None if not found
        """
        return self.tools_registry.get(tool_id)
    
    def update_tool(
        self,
        tool_id: str,
        updates: Dict[str, Any],
        backup_script: bool = False
    ) -> Dict[str, Any]:
        """
        Update a persisted tool.
        
        Args:
            tool_id: Tool identifier
            updates: Dictionary of updates to apply
            backup_script: Whether to create a new backup
            
        Returns:
            Result dictionary
        """
        logger.info(f"Updating persisted tool: {tool_id}")
        
        try:
            if tool_id not in self.tools_registry:
                return {
                    "success": False,
                    "error": f"Tool not found: {tool_id}",
                    "tool_id": tool_id
                }
            
            tool = self.tools_registry[tool_id]
            
            # Create backup if script path is being updated and backup is requested
            if "script_path" in updates and backup_script:
                new_script_path = Path(updates["script_path"])
                if new_script_path.exists():
                    backup_path = self._backup_script(new_script_path, tool_id)
                    if "metadata" not in updates:
                        updates["metadata"] = tool.metadata.copy()
                    updates["metadata"]["backup_path"] = str(backup_path)
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(tool, key):
                    setattr(tool, key, value)
            
            # Update last modified timestamp
            tool.last_modified = datetime.now().isoformat()
            
            # Save individual metadata
            self._save_tool_metadata(tool_id, tool)
            
            # Save registry
            self._save_registry()
            
            logger.info(f"Tool updated successfully: {tool_id}")
            
            return {
                "success": True,
                "tool_id": tool_id,
                "updates_applied": list(updates.keys()),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error updating tool: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "tool_id": tool_id
            }
    
    def delete_tool(self, tool_id: str, delete_backup: bool = False) -> Dict[str, Any]:
        """
        Delete a persisted tool.
        
        Args:
            tool_id: Tool identifier
            delete_backup: Whether to also delete the backup file
            
        Returns:
            Result dictionary
        """
        logger.info(f"Deleting persisted tool: {tool_id}")
        
        try:
            if tool_id not in self.tools_registry:
                return {
                    "success": False,
                    "error": f"Tool not found: {tool_id}",
                    "tool_id": tool_id
                }
            
            tool = self.tools_registry[tool_id]
            
            # Delete backup if requested and exists
            if delete_backup and "backup_path" in tool.metadata:
                backup_path = Path(tool.metadata["backup_path"])
                if backup_path.exists():
                    backup_path.unlink()
                    logger.debug(f"Backup deleted: {backup_path}")
            
            # Delete individual metadata file
            metadata_file = self.metadata_dir / f"{tool_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            # Remove from registry
            del self.tools_registry[tool_id]
            
            # Save registry
            self._save_registry()
            
            logger.info(f"Tool deleted successfully: {tool_id}")
            
            return {
                "success": True,
                "tool_id": tool_id,
                "backup_deleted": delete_backup,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error deleting tool: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "tool_id": tool_id
            }
    
    def list_tools(
        self,
        status_filter: Optional[str] = None,
        name_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all persisted tools.
        
        Args:
            status_filter: Filter by tool status
            name_pattern: Filter by name pattern
            
        Returns:
            Dictionary containing tools information
        """
        logger.debug("Listing persisted tools")
        
        tools_list = []
        
        for tool_id, tool in self.tools_registry.items():
            # Apply filters
            if status_filter and tool.status != status_filter:
                continue
            
            if name_pattern and name_pattern.lower() not in tool.name.lower():
                continue
            
            tool_info = {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "status": tool.status,
                "created_at": tool.created_at,
                "last_modified": tool.last_modified,
                "usage_count": tool.usage_count,
                "version": tool.version
            }
            tools_list.append(tool_info)
        
        return {
            "total_tools": len(tools_list),
            "tools": tools_list,
            "filters_applied": {
                "status": status_filter,
                "name_pattern": name_pattern
            }
        }
    
    def increment_usage(self, tool_id: str) -> None:
        """
        Increment usage count for a tool.
        
        Args:
            tool_id: Tool identifier
        """
        if tool_id in self.tools_registry:
            self.tools_registry[tool_id].usage_count += 1
            self.tools_registry[tool_id].last_modified = datetime.now().isoformat()
            
            # Save updated metadata
            self._save_tool_metadata(tool_id, self.tools_registry[tool_id])
            self._save_registry()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get persistence statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.tools_registry:
            return {
                "total_tools": 0,
                "active_tools": 0,
                "inactive_tools": 0,
                "total_usage": 0,
                "most_used_tool": None,
                "oldest_tool": None,
                "newest_tool": None
            }
        
        tools = list(self.tools_registry.values())
        active_tools = [t for t in tools if t.status == "active"]
        inactive_tools = [t for t in tools if t.status != "active"]
        total_usage = sum(t.usage_count for t in tools)
        
        # Find most used tool
        most_used = max(tools, key=lambda t: t.usage_count)
        
        # Find oldest and newest tools
        oldest = min(tools, key=lambda t: t.created_at)
        newest = max(tools, key=lambda t: t.created_at)
        
        return {
            "total_tools": len(tools),
            "active_tools": len(active_tools),
            "inactive_tools": len(inactive_tools),
            "total_usage": total_usage,
            "most_used_tool": {
                "name": most_used.name,
                "usage_count": most_used.usage_count
            },
            "oldest_tool": {
                "name": oldest.name,
                "created_at": oldest.created_at
            },
            "newest_tool": {
                "name": newest.name,
                "created_at": newest.created_at
            }
        }
    
    def export_tools(self, export_path: str) -> Dict[str, Any]:
        """
        Export all tools to a single file.
        
        Args:
            export_path: Path for the export file
            
        Returns:
            Export result
        """
        logger.info(f"Exporting tools to: {export_path}")
        
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "tools_count": len(self.tools_registry),
                "tools": {tool_id: tool.to_dict() for tool_id, tool in self.tools_registry.items()}
            }
            
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Tools exported successfully: {len(self.tools_registry)} tools")
            
            return {
                "success": True,
                "export_path": str(export_path),
                "tools_count": len(self.tools_registry),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error exporting tools: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def cleanup_old_backups(self, days: int = 30) -> Dict[str, Any]:
        """
        Clean up old backup files.
        
        Args:
            days: Delete backups older than this many days
            
        Returns:
            Cleanup result
        """
        logger.info(f"Cleaning up backups older than {days} days")
        
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            deleted_files = []
            
            for backup_file in self.scripts_backup_dir.glob("*"):
                if backup_file.is_file() and backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    deleted_files.append(str(backup_file))
            
            logger.info(f"Cleaned up {len(deleted_files)} old backup files")
            
            return {
                "success": True,
                "deleted_count": len(deleted_files),
                "deleted_files": deleted_files,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error cleaning up backups: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }