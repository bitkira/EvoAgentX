"""
File Operation Tool Interface
Simple file I/O wrapper following EvoAgentX toolkit patterns
"""

from typing import Dict, Any
from evoagentx.tools import FileToolkit


class FileOperatorTool:
    """
    Simplified file operation wrapper for other agents
    
    Provides direct access to FileToolkit with consistent return format
    """
    
    def __init__(self):
        self._toolkit = FileToolkit()
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read file content with auto format detection
        
        Args:
            file_path: Path to file
            
        Returns:
            Same as FileToolkit.read_file()
        """
        read_tool = self._toolkit.get_tool("read_file")
        return read_tool(file_path=file_path)
    
    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write content to file with format detection
        
        Args:
            file_path: Path to file  
            content: Content to write
            
        Returns:
            Same as FileToolkit.write_file()
        """
        write_tool = self._toolkit.get_tool("write_file")
        return write_tool(file_path=file_path, content=content)
    
    def append_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Append content to file
        
        Args:
            file_path: Path to file
            content: Content to append
            
        Returns:
            Same as FileToolkit.append_file()
        """
        append_tool = self._toolkit.get_tool("append_file")
        return append_tool(file_path=file_path, content=content)

