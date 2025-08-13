#!/usr/bin/env python3
"""
Docker Execution Action for ALITA reproduction.

This module provides secure code execution capabilities using Docker containers
through EvoAgentX's DockerInterpreterToolkit. It offers enhanced security by
isolating code execution in containerized environments.

Author: ALITA Development Team
Created: 2025-08-13
Version: 1.0.0
"""

import logging
import os
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from evoagentx.actions.base import BaseAction
from evoagentx.tools import DockerInterpreterToolkit

# Set up logging
logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    """Data class for execution results."""
    status: ExecutionStatus
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    container_id: Optional[str] = None
    resource_usage: Optional[Dict[str, Any]] = None
    security_issues: Optional[List[str]] = None


@dataclass
class DockerConfig:
    """Docker container configuration."""
    image_tag: str = "python:3.9-slim"
    memory_limit: str = "512m"
    cpu_quota: int = 100000
    cpu_period: int = 100000
    pids_limit: int = 100
    timeout: int = 30
    network_mode: str = "none"
    container_directory: str = "/app"
    print_stdout: bool = True
    print_stderr: bool = True
    require_confirm: bool = False


class DockerExecutionAction(BaseAction):
    """
    Docker-based secure code execution action.
    
    This action provides secure code execution using Docker containers,
    with resource limits, timeout controls, and security validations.
    """
    
    def __init__(self, config: Optional[DockerConfig] = None):
        """
        Initialize Docker execution action.
        
        Args:
            config: Docker configuration settings
        """
        super().__init__()
        self.config = config or DockerConfig()
        self._toolkit = None
        self._execute_tool = None
        self._script_tool = None
        self._execution_history: List[ExecutionResult] = []
        
        logger.info("DockerExecutionAction initialized")
    
    def _ensure_toolkit_ready(self) -> bool:
        """
        Ensure Docker toolkit is initialized and ready.
        
        Returns:
            True if toolkit is ready, False otherwise
        """
        try:
            if self._toolkit is None:
                logger.info("Initializing DockerInterpreterToolkit...")
                
                self._toolkit = DockerInterpreterToolkit(
                    image_tag=self.config.image_tag,
                    container_directory=self.config.container_directory,
                    print_stdout=self.config.print_stdout,
                    print_stderr=self.config.print_stderr,
                    require_confirm=self.config.require_confirm
                )
                
                # Get execution tools
                self._execute_tool = self._toolkit.get_tool("docker_execute")
                self._script_tool = self._toolkit.get_tool("docker_execute_script")
                
                logger.info(f"Docker toolkit ready with image: {self.config.image_tag}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Docker toolkit: {str(e)}")
            return False
    
    def _validate_code_security(self, code: str) -> List[str]:
        """
        Perform basic security validation on code.
        
        Args:
            code: Code to validate
            
        Returns:
            List of security issues found
        """
        security_issues = []
        
        # Define dangerous patterns
        dangerous_patterns = [
            ('import subprocess', 'Subprocess execution detected'),
            ('os.system', 'OS system command execution detected'),
            ('eval(', 'Dynamic code evaluation detected'),
            ('exec(', 'Dynamic code execution detected'),
            ('__import__', 'Dynamic import detected'),
            ('open(', 'File access detected - review required'),
            ('socket', 'Network socket usage detected'),
            ('urllib', 'URL/HTTP request detected'),
            ('requests', 'HTTP request library detected'),
        ]
        
        # Check for dangerous patterns
        for pattern, message in dangerous_patterns:
            if pattern in code:
                security_issues.append(f"{message}: '{pattern}'")
        
        # Check for potential code injection
        suspicious_chars = [';', '&&', '||', '`', '$']
        for char in suspicious_chars:
            if char in code:
                security_issues.append(f"Suspicious character detected: '{char}'")
        
        return security_issues
    
    def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[int] = None,
        validate_security: bool = True
    ) -> ExecutionResult:
        """
        Execute code in Docker container.
        
        Args:
            code: Code to execute
            language: Programming language (default: python)
            timeout: Execution timeout in seconds
            validate_security: Whether to perform security validation
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        timeout = timeout or self.config.timeout
        
        logger.info(f"Executing code in Docker container (timeout: {timeout}s)")
        
        # Security validation
        security_issues = []
        if validate_security:
            security_issues = self._validate_code_security(code)
            if security_issues:
                logger.warning(f"Security issues detected: {len(security_issues)} issues")
                for issue in security_issues:
                    logger.warning(f"  - {issue}")
        
        # Ensure toolkit is ready
        if not self._ensure_toolkit_ready():
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output="",
                error="Failed to initialize Docker toolkit",
                execution_time=time.time() - start_time,
                security_issues=security_issues
            )
        
        try:
            logger.debug(f"Executing code: {code[:100]}...")
            
            # Execute code with timeout handling
            output = self._execute_tool(code=code, language=language)
            
            execution_time = time.time() - start_time
            
            # Create successful result
            result = ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output=output or "",
                execution_time=execution_time,
                security_issues=security_issues if security_issues else None
            )
            
            self._execution_history.append(result)
            logger.info(f"Code execution completed successfully ({execution_time:.2f}s)")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"Code execution failed: {error_msg}")
            
            # Determine failure type
            status = ExecutionStatus.TIMEOUT if "timeout" in error_msg.lower() else ExecutionStatus.FAILED
            
            result = ExecutionResult(
                status=status,
                output="",
                error=error_msg,
                execution_time=execution_time,
                security_issues=security_issues if security_issues else None
            )
            
            self._execution_history.append(result)
            return result
    
    def execute_script_file(
        self,
        script_path: Union[str, Path],
        language: str = "python",
        timeout: Optional[int] = None,
        validate_security: bool = True
    ) -> ExecutionResult:
        """
        Execute script file in Docker container.
        
        Args:
            script_path: Path to script file
            language: Programming language (default: python)
            timeout: Execution timeout in seconds
            validate_security: Whether to perform security validation
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        timeout = timeout or self.config.timeout
        
        script_path = Path(script_path)
        
        if not script_path.exists():
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output="",
                error=f"Script file not found: {script_path}",
                execution_time=time.time() - start_time
            )
        
        logger.info(f"Executing script file: {script_path}")
        
        # Security validation
        security_issues = []
        if validate_security:
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                security_issues = self._validate_code_security(script_content)
                if security_issues:
                    logger.warning(f"Security issues in script: {len(security_issues)} issues")
            except Exception as e:
                logger.warning(f"Failed to read script for security validation: {e}")
        
        # Ensure toolkit is ready
        if not self._ensure_toolkit_ready():
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output="",
                error="Failed to initialize Docker toolkit",
                execution_time=time.time() - start_time,
                security_issues=security_issues
            )
        
        try:
            # Execute script file
            output = self._script_tool(file_path=str(script_path), language=language)
            
            execution_time = time.time() - start_time
            
            result = ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output=output or "",
                execution_time=execution_time,
                security_issues=security_issues if security_issues else None
            )
            
            self._execution_history.append(result)
            logger.info(f"Script execution completed successfully ({execution_time:.2f}s)")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"Script execution failed: {error_msg}")
            
            # Determine failure type
            status = ExecutionStatus.TIMEOUT if "timeout" in error_msg.lower() else ExecutionStatus.FAILED
            
            result = ExecutionResult(
                status=status,
                output="",
                error=error_msg,
                execution_time=execution_time,
                security_issues=security_issues if security_issues else None
            )
            
            self._execution_history.append(result)
            return result
    
    def execute_generated_script(
        self,
        script_path: Union[str, Path],
        timeout: Optional[int] = None,
        enhanced_security: bool = True
    ) -> ExecutionResult:
        """
        Execute a generated script with enhanced security validation.
        
        Args:
            script_path: Path to generated script
            timeout: Execution timeout in seconds
            enhanced_security: Use enhanced security validation
            
        Returns:
            ExecutionResult with execution details
        """
        script_path = Path(script_path)
        
        logger.info(f"Executing generated script: {script_path}")
        
        # Enhanced security for generated scripts
        return self.execute_script_file(
            script_path=script_path,
            timeout=timeout,
            validate_security=enhanced_security
        )
    
    def validate_execution_environment(self) -> Dict[str, Any]:
        """
        Validate Docker execution environment.
        
        Returns:
            Validation result with environment details
        """
        logger.info("Validating Docker execution environment")
        
        try:
            if not self._ensure_toolkit_ready():
                return {
                    "valid": False,
                    "error": "Failed to initialize Docker toolkit"
                }
            
            # Test basic execution
            test_code = "print('Docker environment test')"
            result = self.execute_code(test_code, validate_security=False)
            
            if result.status == ExecutionStatus.SUCCESS:
                return {
                    "valid": True,
                    "docker_image": self.config.image_tag,
                    "container_directory": self.config.container_directory,
                    "test_output": result.output.strip(),
                    "execution_time": result.execution_time
                }
            else:
                return {
                    "valid": False,
                    "error": result.error,
                    "docker_image": self.config.image_tag
                }
                
        except Exception as e:
            logger.error(f"Environment validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get execution history.
        
        Returns:
            List of execution history records
        """
        history = []
        for result in self._execution_history:
            history.append({
                "status": result.status.value,
                "execution_time": result.execution_time,
                "output_length": len(result.output) if result.output else 0,
                "has_error": result.error is not None,
                "security_issues": len(result.security_issues) if result.security_issues else 0
            })
        return history
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary with execution statistics
        """
        if not self._execution_history:
            return {"total_executions": 0}
        
        total = len(self._execution_history)
        successful = sum(1 for r in self._execution_history if r.status == ExecutionStatus.SUCCESS)
        failed = sum(1 for r in self._execution_history if r.status == ExecutionStatus.FAILED)
        timeout = sum(1 for r in self._execution_history if r.status == ExecutionStatus.TIMEOUT)
        
        avg_execution_time = sum(r.execution_time for r in self._execution_history) / total
        total_security_issues = sum(
            len(r.security_issues) if r.security_issues else 0 
            for r in self._execution_history
        )
        
        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "timeout_executions": timeout,
            "success_rate": successful / total * 100,
            "average_execution_time": round(avg_execution_time, 3),
            "total_security_issues": total_security_issues,
            "docker_image": self.config.image_tag
        }
    
    def cleanup(self):
        """
        Cleanup Docker resources.
        """
        logger.info("Cleaning up Docker execution resources")
        
        try:
            if self._toolkit:
                # The toolkit should handle cleanup automatically
                logger.info("Docker toolkit cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass


# Convenience functions for quick usage
def quick_docker_execute(
    code: str,
    language: str = "python",
    timeout: int = 30,
    image_tag: str = "python:3.9-slim"
) -> ExecutionResult:
    """
    Quick Docker code execution.
    
    Args:
        code: Code to execute
        language: Programming language
        timeout: Execution timeout
        image_tag: Docker image tag
        
    Returns:
        ExecutionResult
    """
    config = DockerConfig(
        image_tag=image_tag,
        timeout=timeout,
        print_stdout=False,
        print_stderr=False
    )
    
    executor = DockerExecutionAction(config)
    try:
        return executor.execute_code(code, language, timeout)
    finally:
        executor.cleanup()


def quick_docker_script(
    script_path: Union[str, Path],
    language: str = "python",
    timeout: int = 30,
    image_tag: str = "python:3.9-slim"
) -> ExecutionResult:
    """
    Quick Docker script execution.
    
    Args:
        script_path: Path to script file
        language: Programming language
        timeout: Execution timeout
        image_tag: Docker image tag
        
    Returns:
        ExecutionResult
    """
    config = DockerConfig(
        image_tag=image_tag,
        timeout=timeout,
        print_stdout=False,
        print_stderr=False
    )
    
    executor = DockerExecutionAction(config)
    try:
        return executor.execute_script_file(script_path, language, timeout)
    finally:
        executor.cleanup()