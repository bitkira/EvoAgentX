"""
Code Running Action for ALITA reproduction.

This module provides the CodeRunningAction class that enables the ALITA system
to execute Python code safely using the EvoAgentX PythonInterpreterToolkit.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from evoagentx.tools.interpreter_python import PythonInterpreterToolkit, PythonInterpreter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeRunningAction:
    """
    Code Running Action for executing Python code in a controlled environment.
    
    This class provides a safe interface for executing Python code snippets and scripts
    using the EvoAgentX Python interpreter with security restrictions and error handling.
    """
    
    def __init__(
        self,
        project_path: Optional[str] = None,
        directory_names: Optional[List[str]] = None,
        allowed_imports: Optional[set] = None
    ):
        """
        Initialize the CodeRunningAction.
        
        Args:
            project_path: Path to the project directory for module resolution
            directory_names: List of directory names to check for imports
            allowed_imports: Set of allowed module imports for security
        """
        # Set default project path to current working directory if not provided
        self.project_path = project_path or os.getcwd()
        
        # Set default directory names for local imports
        self.directory_names = directory_names or ["examples", "evoagentx", "tests", "actions", "agents", "utils"]
        
        # Set default allowed imports for security
        self.allowed_imports = allowed_imports or {
            "os", "sys", "time", "datetime", "math", "random", 
            "json", "csv", "re", "collections", "itertools",
            "pathlib", "typing", "dataclasses", "functools",
            "logging", "warnings", "traceback"
        }
        
        # Initialize the Python interpreter toolkit
        self.toolkit = PythonInterpreterToolkit(
            name="ALITAPythonToolkit",
            project_path=self.project_path,
            directory_names=self.directory_names,
            allowed_imports=self.allowed_imports
        )
        
        # Get direct reference to interpreter for convenience
        self.interpreter = self.toolkit.python_interpreter
        
        logger.info(f"CodeRunningAction initialized with project path: {self.project_path}")
    
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Execute Python code and return structured result.
        
        Args:
            code: The Python code to execute
            language: Programming language (default: "python")
            
        Returns:
            Dict containing execution result, success status, and any errors
        """
        logger.info("Executing Python code snippet")
        logger.debug(f"Code to execute: {code[:100]}...")
        
        try:
            # Execute the code using the interpreter
            result = self.interpreter.execute(code, language)
            
            # Check if result contains error information
            if "Error:" in result or "Traceback" in result:
                return {
                    "success": False,
                    "result": None,
                    "output": result,
                    "error": result,
                    "code": code
                }
            
            return {
                "success": True,
                "result": result,
                "output": result,
                "error": None,
                "code": code
            }
            
        except Exception as e:
            error_msg = f"Error executing code: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "result": None,
                "output": None,
                "error": error_msg,
                "code": code
            }
    
    def execute_script(self, file_path: str, language: str = "python") -> Dict[str, Any]:
        """
        Execute Python script file and return structured result.
        
        Args:
            file_path: Path to the Python script file
            language: Programming language (default: "python")
            
        Returns:
            Dict containing execution result, success status, and any errors
        """
        logger.info(f"Executing Python script: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            error_msg = f"Script file not found: {file_path}"
            logger.error(error_msg)
            return {
                "success": False,
                "result": None,
                "output": None,
                "error": error_msg,
                "file_path": file_path
            }
        
        try:
            # Execute the script using the interpreter
            result = self.interpreter.execute_script(file_path, language)
            
            # Check if result contains error information
            if "Error:" in result or "Traceback" in result:
                return {
                    "success": False,
                    "result": None,
                    "output": result,
                    "error": result,
                    "file_path": file_path
                }
            
            return {
                "success": True,
                "result": result,
                "output": result,
                "error": None,
                "file_path": file_path
            }
            
        except Exception as e:
            error_msg = f"Error executing script {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "result": None,
                "output": None,
                "error": error_msg,
                "file_path": file_path
            }
    
    def get_tools(self) -> List[Any]:
        """
        Get the list of available tools from the toolkit.
        
        Returns:
            List of available tools
        """
        return self.toolkit.tools
    
    def get_interpreter_status(self) -> Dict[str, Any]:
        """
        Get current status and configuration of the interpreter.
        
        Returns:
            Dict containing interpreter configuration and status
        """
        return {
            "project_path": self.project_path,
            "directory_names": self.directory_names,
            "allowed_imports": list(self.allowed_imports),
            "toolkit_name": self.toolkit.name,
            "available_tools": [tool.name for tool in self.toolkit.tools]
        }
    
    def validate_code_safety(self, code: str) -> Dict[str, Any]:
        """
        Validate code for safety violations before execution.
        
        Args:
            code: Python code to validate
            
        Returns:
            Dict containing validation results
        """
        logger.debug("Validating code safety")
        
        try:
            # Use the interpreter's internal analysis method
            violations = self.interpreter._analyze_code(code)
            
            is_safe = len(violations) == 0
            
            return {
                "is_safe": is_safe,
                "violations": violations,
                "code": code
            }
            
        except Exception as e:
            logger.error(f"Error during code safety validation: {str(e)}")
            return {
                "is_safe": False,
                "violations": [f"Validation error: {str(e)}"],
                "code": code
            }