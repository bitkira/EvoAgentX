"""
File Operations Action for ALITA reproduction.

This module provides file operations capabilities using EvoAgentX's FileToolkit,
including reading, writing, and appending files with special support for different formats.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from evoagentx.tools import FileToolkit

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileOperationsAction:
    """
    File Operations Action for handling file read, write, and append operations.
    
    This class provides unified access to file operations with comprehensive
    error handling, format detection, and safety checks.
    """
    
    def __init__(self):
        """
        Initialize the FileOperationsAction.
        """
        # Initialize File toolkit
        try:
            self.file_toolkit = FileToolkit()
            
            # Get individual tools from the toolkit
            self.read_tool = self.file_toolkit.get_tool("read_file")
            self.write_tool = self.file_toolkit.get_tool("write_file")
            self.append_tool = self.file_toolkit.get_tool("append_file")
            
            logger.info("File operations toolkit initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize file toolkit: {str(e)}")
            self.file_toolkit = None
            self.read_tool = None
            self.write_tool = None
            self.append_tool = None
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read content from a file with automatic format detection.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Dict containing file content and metadata
        """
        logger.info(f"Reading file: {file_path}")
        
        if not self.read_tool:
            return {
                "success": False,
                "operation": "read",
                "file_path": file_path,
                "content": None,
                "error": "File operations not available - toolkit initialization failed"
            }
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "operation": "read",
                    "file_path": file_path,
                    "content": None,
                    "error": f"File not found: {file_path}"
                }
            
            # Execute file read
            raw_result = self.read_tool(file_path=file_path)
            
            # Process result
            if isinstance(raw_result, dict):
                return {
                    "success": raw_result.get("success", False),
                    "operation": "read",
                    "file_path": file_path,
                    "content": raw_result.get("content", ""),
                    "file_type": raw_result.get("file_type", "unknown"),
                    "file_size": len(str(raw_result.get("content", ""))) if raw_result.get("content") else 0,
                    "error": raw_result.get("error")
                }
            else:
                # If raw_result is just content
                content = str(raw_result) if raw_result else ""
                return {
                    "success": True,
                    "operation": "read",
                    "file_path": file_path,
                    "content": content,
                    "file_type": self._detect_file_type(file_path),
                    "file_size": len(content),
                    "error": None
                }
                
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "read",
                "file_path": file_path,
                "content": None,
                "error": error_msg
            }
    
    def write_file(self, file_path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dict containing operation result and metadata
        """
        logger.info(f"Writing file: {file_path}")
        
        if not self.write_tool:
            return {
                "success": False,
                "operation": "write",
                "file_path": file_path,
                "error": "File operations not available - toolkit initialization failed"
            }
        
        try:
            # Check if file exists and overwrite is False
            if os.path.exists(file_path) and not overwrite:
                return {
                    "success": False,
                    "operation": "write",
                    "file_path": file_path,
                    "error": f"File already exists and overwrite is disabled: {file_path}"
                }
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            # Execute file write
            raw_result = self.write_tool(file_path=file_path, content=content)
            
            # Process result
            if isinstance(raw_result, dict):
                success = raw_result.get("success", False)
            else:
                # Assume success if no error occurred
                success = True
            
            return {
                "success": success,
                "operation": "write",
                "file_path": file_path,
                "content_length": len(content),
                "file_type": self._detect_file_type(file_path),
                "message": f"Successfully wrote {len(content)} characters to {file_path}",
                "error": raw_result.get("error") if isinstance(raw_result, dict) else None
            }
                
        except Exception as e:
            error_msg = f"Error writing file {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "write",
                "file_path": file_path,
                "error": error_msg
            }
    
    def append_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Append content to a file.
        
        Args:
            file_path: Path to the file to append to
            content: Content to append to the file
            
        Returns:
            Dict containing operation result and metadata
        """
        logger.info(f"Appending to file: {file_path}")
        
        if not self.append_tool:
            return {
                "success": False,
                "operation": "append",
                "file_path": file_path,
                "error": "File operations not available - toolkit initialization failed"
            }
        
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            # Execute file append
            raw_result = self.append_tool(file_path=file_path, content=content)
            
            # Process result
            if isinstance(raw_result, dict):
                success = raw_result.get("success", False)
            else:
                # Assume success if no error occurred
                success = True
            
            return {
                "success": success,
                "operation": "append",
                "file_path": file_path,
                "content_length": len(content),
                "file_type": self._detect_file_type(file_path),
                "message": f"Successfully appended {len(content)} characters to {file_path}",
                "error": raw_result.get("error") if isinstance(raw_result, dict) else None
            }
                
        except Exception as e:
            error_msg = f"Error appending to file {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "append",
                "file_path": file_path,
                "error": error_msg
            }
    
    def list_files(self, directory_path: str, pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        List files in a directory with optional pattern matching.
        
        Args:
            directory_path: Path to the directory to list
            pattern: Optional pattern to match (e.g., "*.py", "*.txt")
            
        Returns:
            Dict containing list of files and metadata
        """
        logger.info(f"Listing files in directory: {directory_path}")
        
        try:
            if not os.path.exists(directory_path):
                return {
                    "success": False,
                    "operation": "list",
                    "directory_path": directory_path,
                    "files": [],
                    "error": f"Directory not found: {directory_path}"
                }
            
            if not os.path.isdir(directory_path):
                return {
                    "success": False,
                    "operation": "list",
                    "directory_path": directory_path,
                    "files": [],
                    "error": f"Path is not a directory: {directory_path}"
                }
            
            # List files
            all_items = os.listdir(directory_path)
            
            # Filter files (exclude directories unless specifically requested)
            files = []
            for item in all_items:
                full_path = os.path.join(directory_path, item)
                if os.path.isfile(full_path):
                    # Apply pattern filter if specified
                    if pattern is None or self._match_pattern(item, pattern):
                        file_info = {
                            "name": item,
                            "path": full_path,
                            "size": os.path.getsize(full_path),
                            "type": self._detect_file_type(full_path),
                            "modified": os.path.getmtime(full_path)
                        }
                        files.append(file_info)
            
            return {
                "success": True,
                "operation": "list",
                "directory_path": directory_path,
                "files": files,
                "total_files": len(files),
                "pattern": pattern,
                "error": None
            }
                
        except Exception as e:
            error_msg = f"Error listing files in {directory_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "list",
                "directory_path": directory_path,
                "files": [],
                "error": error_msg
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing file information
        """
        logger.info(f"Getting file info: {file_path}")
        
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "operation": "info",
                    "file_path": file_path,
                    "error": f"File not found: {file_path}"
                }
            
            # Get file stats
            stat = os.stat(file_path)
            
            return {
                "success": True,
                "operation": "info",
                "file_path": file_path,
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "type": self._detect_file_type(file_path),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime,
                "is_file": os.path.isfile(file_path),
                "is_directory": os.path.isdir(file_path),
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK),
                "error": None
            }
                
        except Exception as e:
            error_msg = f"Error getting file info for {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "info",
                "file_path": file_path,
                "error": error_msg
            }
    
    def _detect_file_type(self, file_path: str) -> str:
        """
        Detect file type based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File type string
        """
        _, ext = os.path.splitext(file_path.lower())
        
        type_mapping = {
            '.txt': 'text',
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.csv': 'csv',
            '.md': 'markdown',
            '.pdf': 'pdf',
            '.doc': 'document',
            '.docx': 'document',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image'
        }
        
        return type_mapping.get(ext, 'unknown')
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        Simple pattern matching for file names.
        
        Args:
            filename: Name of the file
            pattern: Pattern to match (supports * wildcard)
            
        Returns:
            True if filename matches pattern
        """
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def get_available_operations(self) -> List[str]:
        """
        Get list of available file operations.
        
        Returns:
            List of available operation names
        """
        operations = ["list_files", "get_file_info"]
        
        if self.read_tool:
            operations.append("read_file")
        if self.write_tool:
            operations.append("write_file")
        if self.append_tool:
            operations.append("append_file")
        
        return operations
    
    def get_operations_status(self) -> Dict[str, Any]:
        """
        Get status of file operations capabilities.
        
        Returns:
            Dict containing status information
        """
        return {
            "toolkit_available": self.file_toolkit is not None,
            "read_available": self.read_tool is not None,
            "write_available": self.write_tool is not None,
            "append_available": self.append_tool is not None,
            "available_operations": self.get_available_operations()
        }