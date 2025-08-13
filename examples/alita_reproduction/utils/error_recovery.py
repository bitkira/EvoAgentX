#!/usr/bin/env python3
"""
Error Recovery System for ALITA reproduction.

This module provides error recovery and retry mechanisms for Docker execution,
including failure analysis, recovery strategies, and automated retry logic.

Author: ALITA Development Team
Created: 2025-08-13
Version: 1.0.0
"""

import time
import logging
import traceback
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import random

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of execution errors."""
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"
    IMPORT_ERROR = "import_error"
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    CONTAINER_ERROR = "container_error"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""
    RETRY = "retry"                     # Simple retry
    RETRY_WITH_BACKOFF = "retry_with_backoff"  # Retry with exponential backoff
    INCREASE_RESOURCES = "increase_resources"   # Increase memory/timeout limits
    CHANGE_ENVIRONMENT = "change_environment"  # Use different container image
    FIX_CODE = "fix_code"              # Attempt code fixes
    SKIP = "skip"                      # Skip this execution
    FAIL = "fail"                      # Give up


@dataclass
class ErrorContext:
    """Context information for an error."""
    error_type: ErrorType
    original_error: str
    code_snippet: Optional[str] = None
    execution_attempt: int = 1
    total_attempts: int = 1
    timestamp: float = field(default_factory=time.time)
    environment_info: Dict[str, Any] = field(default_factory=dict)
    suggested_fixes: List[str] = field(default_factory=list)


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""
    success: bool
    strategy_used: RecoveryStrategy
    attempts_made: int
    total_time: float
    final_error: Optional[str] = None
    recovery_log: List[str] = field(default_factory=list)
    modified_code: Optional[str] = None
    modified_config: Optional[Dict[str, Any]] = None


class ErrorRecoverySystem:
    """
    Comprehensive error recovery system for Docker execution.
    
    Provides automated error analysis, recovery strategy selection,
    and retry mechanisms with various recovery techniques.
    """
    
    def __init__(self, max_total_attempts: int = 3, max_backoff_time: int = 30):
        """
        Initialize error recovery system.
        
        Args:
            max_total_attempts: Maximum total recovery attempts
            max_backoff_time: Maximum backoff time for retries
        """
        self.max_total_attempts = max_total_attempts
        self.max_backoff_time = max_backoff_time
        
        # Error pattern matching
        self._error_patterns = {
            ErrorType.TIMEOUT: [
                r'timeout',
                r'timed out',
                r'TimeoutError',
                r'execution time exceeded'
            ],
            ErrorType.MEMORY_LIMIT: [
                r'out of memory',
                r'MemoryError',
                r'memory limit exceeded',
                r'killed.*memory',
                r'OOM'
            ],
            ErrorType.NETWORK_ERROR: [
                r'ConnectionError',
                r'network.*unreachable',
                r'no route to host',
                r'connection refused',
                r'dns resolution failed'
            ],
            ErrorType.PERMISSION_ERROR: [
                r'PermissionError',
                r'permission denied',
                r'access denied',
                r'forbidden'
            ],
            ErrorType.IMPORT_ERROR: [
                r'ImportError',
                r'ModuleNotFoundError',
                r'No module named',
                r'cannot import name'
            ],
            ErrorType.SYNTAX_ERROR: [
                r'SyntaxError',
                r'IndentationError',
                r'invalid syntax'
            ],
            ErrorType.CONTAINER_ERROR: [
                r'container.*failed',
                r'docker.*error',
                r'container not found',
                r'image not found'
            ]
        }
        
        # Recovery strategies for each error type
        self._recovery_strategies = {
            ErrorType.TIMEOUT: [
                RecoveryStrategy.INCREASE_RESOURCES,
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                RecoveryStrategy.RETRY
            ],
            ErrorType.MEMORY_LIMIT: [
                RecoveryStrategy.INCREASE_RESOURCES,
                RecoveryStrategy.CHANGE_ENVIRONMENT,
                RecoveryStrategy.RETRY
            ],
            ErrorType.NETWORK_ERROR: [
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                RecoveryStrategy.CHANGE_ENVIRONMENT,
                RecoveryStrategy.RETRY
            ],
            ErrorType.PERMISSION_ERROR: [
                RecoveryStrategy.CHANGE_ENVIRONMENT,
                RecoveryStrategy.RETRY,
                RecoveryStrategy.SKIP
            ],
            ErrorType.IMPORT_ERROR: [
                RecoveryStrategy.CHANGE_ENVIRONMENT,
                RecoveryStrategy.FIX_CODE,
                RecoveryStrategy.SKIP
            ],
            ErrorType.SYNTAX_ERROR: [
                RecoveryStrategy.FIX_CODE,
                RecoveryStrategy.SKIP,
                RecoveryStrategy.FAIL
            ],
            ErrorType.CONTAINER_ERROR: [
                RecoveryStrategy.CHANGE_ENVIRONMENT,
                RecoveryStrategy.RETRY,
                RecoveryStrategy.FAIL
            ],
            ErrorType.RUNTIME_ERROR: [
                RecoveryStrategy.RETRY,
                RecoveryStrategy.FIX_CODE,
                RecoveryStrategy.INCREASE_RESOURCES
            ],
            ErrorType.UNKNOWN_ERROR: [
                RecoveryStrategy.RETRY,
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                RecoveryStrategy.SKIP
            ]
        }
        
        # Code fix patterns
        self._code_fixes = {
            ErrorType.IMPORT_ERROR: [
                self._fix_missing_imports,
                self._add_fallback_imports
            ],
            ErrorType.SYNTAX_ERROR: [
                self._fix_common_syntax_errors
            ]
        }
        
        logger.info(f"ErrorRecoverySystem initialized (max_attempts: {max_total_attempts})")
    
    def recover_from_error(
        self,
        error_message: str,
        execution_function: Callable,
        execution_args: Tuple = (),
        execution_kwargs: Dict[str, Any] = None,
        code: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> RecoveryResult:
        """
        Attempt to recover from an execution error.
        
        Args:
            error_message: The error message from failed execution
            execution_function: Function to retry execution
            execution_args: Arguments for execution function
            execution_kwargs: Keyword arguments for execution function
            code: Original code that failed
            config: Original configuration
            
        Returns:
            RecoveryResult with outcome of recovery attempts
        """
        start_time = time.time()
        execution_kwargs = execution_kwargs or {}
        recovery_log = []
        
        logger.info(f"Starting error recovery for: {error_message[:100]}...")
        recovery_log.append(f"Initial error: {error_message}")
        
        # Analyze the error
        error_context = self._analyze_error(error_message, code)
        recovery_log.append(f"Error type identified: {error_context.error_type.value}")
        
        # Get recovery strategies for this error type
        strategies = self._recovery_strategies.get(
            error_context.error_type, 
            [RecoveryStrategy.RETRY, RecoveryStrategy.SKIP]
        )
        
        current_code = code
        current_config = config or {}
        
        for attempt in range(1, self.max_total_attempts + 1):
            logger.info(f"Recovery attempt {attempt}/{self.max_total_attempts}")
            recovery_log.append(f"--- Attempt {attempt} ---")
            
            # Try each recovery strategy
            for strategy in strategies:
                try:
                    recovery_log.append(f"Trying strategy: {strategy.value}")
                    
                    # Apply recovery strategy
                    success, modified_code, modified_config = self._apply_recovery_strategy(
                        strategy, error_context, current_code, current_config, attempt
                    )
                    
                    if not success:
                        recovery_log.append(f"Strategy {strategy.value} not applicable")
                        continue
                    
                    # Update current code/config if modified
                    if modified_code is not None:
                        current_code = modified_code
                        recovery_log.append("Code modified for recovery")
                    
                    if modified_config:
                        current_config.update(modified_config)
                        recovery_log.append("Configuration modified for recovery")
                    
                    # Update execution arguments if needed
                    updated_kwargs = execution_kwargs.copy()
                    if modified_code is not None and 'code' in updated_kwargs:
                        updated_kwargs['code'] = modified_code
                    
                    # Attempt execution
                    try:
                        result = execution_function(*execution_args, **updated_kwargs)
                        
                        # Check if execution was successful
                        if self._is_execution_successful(result):
                            total_time = time.time() - start_time
                            recovery_log.append(f"Recovery successful using {strategy.value}")
                            
                            return RecoveryResult(
                                success=True,
                                strategy_used=strategy,
                                attempts_made=attempt,
                                total_time=total_time,
                                recovery_log=recovery_log,
                                modified_code=current_code if current_code != code else None,
                                modified_config=modified_config if modified_config != config else None
                            )
                        else:
                            recovery_log.append("Execution completed but result indicates failure")
                    
                    except Exception as e:
                        new_error = str(e)
                        recovery_log.append(f"Execution failed with: {new_error[:100]}...")
                        
                        # Update error context for next iteration
                        error_context = self._analyze_error(new_error, current_code)
                        error_context.execution_attempt = attempt
                        
                        # If it's the same error type, try next strategy
                        continue
                
                except Exception as strategy_error:
                    recovery_log.append(f"Recovery strategy failed: {str(strategy_error)}")
                    continue
        
        # All recovery attempts failed
        total_time = time.time() - start_time
        recovery_log.append("All recovery attempts failed")
        
        return RecoveryResult(
            success=False,
            strategy_used=RecoveryStrategy.FAIL,
            attempts_made=self.max_total_attempts,
            total_time=total_time,
            final_error=error_context.original_error,
            recovery_log=recovery_log
        )
    
    def _analyze_error(self, error_message: str, code: Optional[str] = None) -> ErrorContext:
        """Analyze error message to determine error type and context."""
        error_type = ErrorType.UNKNOWN_ERROR
        
        # Match error patterns
        for err_type, patterns in self._error_patterns.items():
            for pattern in patterns:
                import re
                if re.search(pattern, error_message, re.IGNORECASE):
                    error_type = err_type
                    break
            if error_type != ErrorType.UNKNOWN_ERROR:
                break
        
        # Generate suggested fixes
        suggested_fixes = self._generate_suggested_fixes(error_type, error_message, code)
        
        return ErrorContext(
            error_type=error_type,
            original_error=error_message,
            code_snippet=code[:500] if code else None,  # First 500 chars
            suggested_fixes=suggested_fixes
        )
    
    def _apply_recovery_strategy(
        self,
        strategy: RecoveryStrategy,
        error_context: ErrorContext,
        code: Optional[str],
        config: Dict[str, Any],
        attempt: int
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Apply a specific recovery strategy.
        
        Returns:
            Tuple of (success, modified_code, modified_config)
        """
        if strategy == RecoveryStrategy.RETRY:
            return True, None, None
        
        elif strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
            backoff_time = min(2 ** attempt, self.max_backoff_time)
            jitter = random.uniform(0, backoff_time * 0.1)
            time.sleep(backoff_time + jitter)
            return True, None, None
        
        elif strategy == RecoveryStrategy.INCREASE_RESOURCES:
            modified_config = {}
            
            if error_context.error_type == ErrorType.TIMEOUT:
                current_timeout = config.get('timeout', 30)
                modified_config['timeout'] = min(current_timeout * 2, 300)  # Max 5 minutes
            
            elif error_context.error_type == ErrorType.MEMORY_LIMIT:
                current_memory = config.get('memory_limit', '512m')
                if current_memory.endswith('m'):
                    memory_mb = int(current_memory[:-1])
                    new_memory = min(memory_mb * 2, 2048)  # Max 2GB
                    modified_config['memory_limit'] = f'{new_memory}m'
            
            return len(modified_config) > 0, None, modified_config
        
        elif strategy == RecoveryStrategy.CHANGE_ENVIRONMENT:
            modified_config = {}
            
            # Try different Docker images
            current_image = config.get('image_tag', 'python:3.9-slim')
            
            if 'alpine' not in current_image:
                modified_config['image_tag'] = 'python:3.9-alpine'
            elif 'slim' not in current_image:
                modified_config['image_tag'] = 'python:3.9-slim'
            else:
                modified_config['image_tag'] = 'python:3.9'
            
            # Adjust network settings for network errors
            if error_context.error_type == ErrorType.NETWORK_ERROR:
                modified_config['network_mode'] = 'bridge'
            
            return True, None, modified_config
        
        elif strategy == RecoveryStrategy.FIX_CODE:
            if not code:
                return False, None, None
            
            modified_code = self._attempt_code_fix(error_context, code)
            return modified_code != code, modified_code, None
        
        elif strategy == RecoveryStrategy.SKIP:
            # Skip strategy doesn't modify anything but indicates we should skip
            return False, None, None
        
        elif strategy == RecoveryStrategy.FAIL:
            # Fail strategy indicates we should give up
            return False, None, None
        
        return False, None, None
    
    def _attempt_code_fix(self, error_context: ErrorContext, code: str) -> str:
        """Attempt to fix code based on error context."""
        if error_context.error_type in self._code_fixes:
            for fix_function in self._code_fixes[error_context.error_type]:
                try:
                    fixed_code = fix_function(code, error_context.original_error)
                    if fixed_code != code:
                        return fixed_code
                except Exception as e:
                    logger.debug(f"Code fix function failed: {str(e)}")
        
        return code
    
    def _fix_missing_imports(self, code: str, error_message: str) -> str:
        """Fix missing import errors."""
        import re
        
        # Extract module name from error
        module_match = re.search(r"No module named '([^']+)'", error_message)
        if module_match:
            module_name = module_match.group(1)
            
            # Add common module mappings
            common_imports = {
                'pandas': 'import pandas as pd',
                'numpy': 'import numpy as np',
                'requests': 'import requests',
                'json': 'import json',
                'os': 'import os',
                'sys': 'import sys',
                'time': 'import time',
                'datetime': 'from datetime import datetime',
                'pathlib': 'from pathlib import Path'
            }
            
            if module_name in common_imports:
                import_line = common_imports[module_name]
                # Add import at the beginning after any existing imports
                lines = code.split('\n')
                import_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_index = i + 1
                
                lines.insert(import_index, import_line)
                return '\n'.join(lines)
        
        return code
    
    def _add_fallback_imports(self, code: str, error_message: str) -> str:
        """Add fallback imports with try-except blocks."""
        import re
        
        module_match = re.search(r"No module named '([^']+)'", error_message)
        if module_match:
            module_name = module_match.group(1)
            
            fallback_code = f"""
try:
    import {module_name}
except ImportError:
    print(f"Warning: {module_name} not available, using fallback")
    class Mock{module_name.title()}:
        def __getattr__(self, name):
            def mock_method(*args, **kwargs):
                print(f"Mock {{name}} called with args={{args}}, kwargs={{kwargs}}")
                return None
            return mock_method
    {module_name} = Mock{module_name.title()}()
"""
            
            return fallback_code + '\n' + code
        
        return code
    
    def _fix_common_syntax_errors(self, code: str, error_message: str) -> str:
        """Fix common syntax errors."""
        import re
        
        # Fix missing colons
        if 'invalid syntax' in error_message and 'if' in code:
            # Simple fix for missing colons after if statements
            fixed_code = re.sub(r'\bif\s+([^:]+)(?<![:])\s*$', r'if \1:', code, flags=re.MULTILINE)
            if fixed_code != code:
                return fixed_code
        
        # Fix indentation issues (basic)
        lines = code.split('\n')
        fixed_lines = []
        for line in lines:
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if line.strip().startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except')):
                    fixed_lines.append(line)
                else:
                    # Add basic indentation
                    fixed_lines.append('    ' + line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _generate_suggested_fixes(
        self, 
        error_type: ErrorType, 
        error_message: str, 
        code: Optional[str]
    ) -> List[str]:
        """Generate suggested fixes for an error type."""
        suggestions = []
        
        if error_type == ErrorType.TIMEOUT:
            suggestions.extend([
                "Increase execution timeout",
                "Optimize code for better performance",
                "Reduce data processing size"
            ])
        
        elif error_type == ErrorType.MEMORY_LIMIT:
            suggestions.extend([
                "Increase memory limit",
                "Process data in smaller chunks",
                "Use more memory-efficient algorithms"
            ])
        
        elif error_type == ErrorType.NETWORK_ERROR:
            suggestions.extend([
                "Check network connectivity",
                "Add retry logic for network requests",
                "Use different network configuration"
            ])
        
        elif error_type == ErrorType.IMPORT_ERROR:
            suggestions.extend([
                "Install missing Python packages",
                "Check module name spelling",
                "Use alternative libraries"
            ])
        
        elif error_type == ErrorType.SYNTAX_ERROR:
            suggestions.extend([
                "Fix Python syntax errors",
                "Check indentation",
                "Validate parentheses and brackets"
            ])
        
        return suggestions
    
    def _is_execution_successful(self, result: Any) -> bool:
        """Check if execution result indicates success."""
        # This is a basic check - can be made more sophisticated
        if hasattr(result, 'status'):
            return str(result.status).lower() == 'success'
        
        if hasattr(result, 'success'):
            return bool(result.success)
        
        if isinstance(result, dict):
            if 'success' in result:
                return bool(result['success'])
            if 'status' in result:
                return str(result['status']).lower() == 'success'
            if 'error' in result:
                return not result['error']
        
        # If no clear success indicator, assume success if no exception was raised
        return True


# Convenience functions
def recover_execution(
    error_message: str,
    execution_function: Callable,
    max_attempts: int = 3,
    **execution_kwargs
) -> RecoveryResult:
    """
    Convenience function for error recovery.
    
    Args:
        error_message: Error from failed execution
        execution_function: Function to retry
        max_attempts: Maximum recovery attempts
        **execution_kwargs: Arguments for execution function
        
    Returns:
        RecoveryResult
    """
    recovery_system = ErrorRecoverySystem(max_total_attempts=max_attempts)
    
    return recovery_system.recover_from_error(
        error_message=error_message,
        execution_function=execution_function,
        execution_kwargs=execution_kwargs
    )


def analyze_error_type(error_message: str) -> Dict[str, Any]:
    """
    Analyze error message and return error type information.
    
    Args:
        error_message: Error message to analyze
        
    Returns:
        Dictionary with error analysis
    """
    recovery_system = ErrorRecoverySystem()
    error_context = recovery_system._analyze_error(error_message)
    
    return {
        "error_type": error_context.error_type.value,
        "suggested_fixes": error_context.suggested_fixes,
        "recovery_strategies": [s.value for s in recovery_system._recovery_strategies.get(
            error_context.error_type, []
        )]
    }