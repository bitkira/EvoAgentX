#!/usr/bin/env python3
"""
Result Validator for ALITA reproduction.

This module provides comprehensive validation and evaluation of script execution results,
including output analysis, error detection, and performance assessment.

Author: ALITA Development Team
Created: 2025-08-13
Version: 1.0.0
"""

import re
import ast
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ResultStatus(Enum):
    """Result validation status."""
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    INCOMPLETE = "incomplete"
    ERROR = "error"


class OutputType(Enum):
    """Types of output content."""
    TEXT = "text"
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    XML = "xml"
    BINARY = "binary"
    ERROR = "error"
    EMPTY = "empty"
    MIXED = "mixed"


@dataclass
class ValidationIssue:
    """Validation issue data class."""
    severity: str  # "error", "warning", "info"
    category: str  # "security", "performance", "correctness", "format"
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ExecutionMetrics:
    """Execution performance metrics."""
    execution_time: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    output_size: int = 0
    error_count: int = 0
    warning_count: int = 0
    lines_of_output: int = 0
    characters_output: int = 0


@dataclass
class ValidationResult:
    """Comprehensive validation result."""
    status: ResultStatus
    is_valid: bool
    confidence: float  # 0.0 to 1.0
    output_type: OutputType
    metrics: ExecutionMetrics
    issues: List[ValidationIssue]
    summary: str
    parsed_data: Optional[Any] = None
    recommendations: List[str] = None


class ResultValidator:
    """
    Comprehensive result validator for script execution outputs.
    
    Provides validation, analysis, and evaluation of script execution results
    with support for various output formats and content types.
    """
    
    def __init__(self):
        """Initialize result validator."""
        self._error_patterns = [
            (r'Traceback \(most recent call last\):', "Python traceback"),
            (r'Error:', "General error"),
            (r'Exception:', "Exception occurred"),
            (r'ValueError:', "Value error"),
            (r'TypeError:', "Type error"),
            (r'NameError:', "Name error"),
            (r'ImportError:', "Import error"),
            (r'ModuleNotFoundError:', "Module not found"),
            (r'FileNotFoundError:', "File not found"),
            (r'PermissionError:', "Permission denied"),
            (r'ConnectionError:', "Connection error"),
            (r'TimeoutError:', "Timeout error"),
            (r'KeyError:', "Key error"),
            (r'IndexError:', "Index error"),
            (r'AttributeError:', "Attribute error"),
            (r'SyntaxError:', "Syntax error"),
            (r'IndentationError:', "Indentation error"),
            (r'RuntimeError:', "Runtime error")
        ]
        
        self._warning_patterns = [
            (r'Warning:', "General warning"),
            (r'DeprecationWarning:', "Deprecation warning"),
            (r'FutureWarning:', "Future warning"),
            (r'UserWarning:', "User warning"),
            (r'ResourceWarning:', "Resource warning"),
            (r'ImportWarning:', "Import warning")
        ]
        
        self._success_indicators = [
            r'successfully',
            r'complete',
            r'done',
            r'finished',
            r'✅',
            r'SUCCESS',
            r'OK'
        ]
        
        logger.info("ResultValidator initialized with comprehensive validation rules")
    
    def validate_execution_result(
        self,
        output: str,
        error: Optional[str] = None,
        execution_time: float = 0.0,
        expected_output: Optional[str] = None,
        script_type: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate script execution result.
        
        Args:
            output: Script output
            error: Error message if any
            execution_time: Execution time in seconds
            expected_output: Expected output for comparison
            script_type: Type of script executed
            
        Returns:
            ValidationResult with comprehensive analysis
        """
        logger.info("Validating execution result")
        
        issues: List[ValidationIssue] = []
        
        # Determine output type
        output_type = self._detect_output_type(output)
        
        # Calculate basic metrics
        metrics = ExecutionMetrics(
            execution_time=execution_time,
            output_size=len(output) if output else 0,
            lines_of_output=len(output.split('\n')) if output else 0,
            characters_output=len(output) if output else 0
        )
        
        # Analyze errors
        if error:
            error_issues = self._analyze_errors(error)
            issues.extend(error_issues)
            metrics.error_count = len(error_issues)
        
        # Analyze output content
        if output:
            output_issues = self._analyze_output_content(output, script_type)
            issues.extend(output_issues)
            
            # Count warnings
            warning_count = sum(1 for issue in issues if issue.severity == "warning")
            metrics.warning_count = warning_count
        
        # Performance analysis
        performance_issues = self._analyze_performance(metrics, script_type)
        issues.extend(performance_issues)
        
        # Compare with expected output if provided
        if expected_output:
            comparison_issues = self._compare_with_expected(output, expected_output)
            issues.extend(comparison_issues)
        
        # Try to parse structured data
        parsed_data = self._try_parse_output(output, output_type)
        
        # Determine overall status and confidence
        status, confidence = self._determine_status_confidence(
            output, error, issues, metrics, expected_output
        )
        
        # Generate summary
        summary = self._generate_summary(status, metrics, issues, output_type)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, metrics, script_type)
        
        return ValidationResult(
            status=status,
            is_valid=status in [ResultStatus.VALID, ResultStatus.INCOMPLETE],
            confidence=confidence,
            output_type=output_type,
            metrics=metrics,
            issues=issues,
            summary=summary,
            parsed_data=parsed_data,
            recommendations=recommendations
        )
    
    def _detect_output_type(self, output: str) -> OutputType:
        """Detect the type of output content."""
        if not output or output.strip() == "":
            return OutputType.EMPTY
        
        output_stripped = output.strip()
        
        # Check for JSON
        if (output_stripped.startswith('{') and output_stripped.endswith('}')) or \
           (output_stripped.startswith('[') and output_stripped.endswith(']')):
            try:
                json.loads(output_stripped)
                return OutputType.JSON
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Check for CSV (basic heuristic)
        lines = output.split('\n')
        if len(lines) > 1:
            first_line_commas = lines[0].count(',')
            if first_line_commas > 0:
                # Check if most lines have similar comma counts
                similar_comma_count = sum(
                    1 for line in lines[1:5] if abs(line.count(',') - first_line_commas) <= 1
                )
                if similar_comma_count >= min(3, len(lines) - 1):
                    return OutputType.CSV
        
        # Check for HTML
        if '<html' in output.lower() or '<body' in output.lower() or \
           re.search(r'<[a-zA-Z][^>]*>', output):
            return OutputType.HTML
        
        # Check for XML
        if output_stripped.startswith('<?xml') or \
           re.match(r'<[a-zA-Z][^>]*>', output_stripped):
            return OutputType.XML
        
        # Check for binary content
        if any(ord(char) < 32 and char not in '\n\r\t' for char in output[:100]):
            return OutputType.BINARY
        
        # Check for error content
        if any(pattern[0] in output for pattern in self._error_patterns):
            return OutputType.ERROR
        
        # Check for mixed content
        if '\n' in output and len(set(self._detect_line_types(output))) > 1:
            return OutputType.MIXED
        
        return OutputType.TEXT
    
    def _detect_line_types(self, output: str) -> List[str]:
        """Detect types of different lines in output."""
        line_types = []
        for line in output.split('\n')[:10]:  # Check first 10 lines
            line = line.strip()
            if not line:
                continue
            
            if any(pattern in line for pattern, _ in self._error_patterns):
                line_types.append('error')
            elif any(pattern in line for pattern, _ in self._warning_patterns):
                line_types.append('warning')
            elif line.startswith('{') or line.startswith('['):
                line_types.append('json')
            elif ',' in line and len(line.split(',')) > 2:
                line_types.append('csv')
            else:
                line_types.append('text')
        
        return line_types
    
    def _analyze_errors(self, error: str) -> List[ValidationIssue]:
        """Analyze error messages."""
        issues = []
        
        for pattern, description in self._error_patterns:
            if re.search(pattern, error):
                # Extract line number if present
                line_match = re.search(r'line (\d+)', error)
                line_number = int(line_match.group(1)) if line_match else None
                
                issues.append(ValidationIssue(
                    severity="error",
                    category="execution",
                    message=f"{description} detected in error output",
                    line_number=line_number,
                    suggestion=self._get_error_suggestion(pattern)
                ))
        
        return issues
    
    def _analyze_output_content(self, output: str, script_type: Optional[str]) -> List[ValidationIssue]:
        """Analyze output content for issues."""
        issues = []
        
        # Check for warnings
        for pattern, description in self._warning_patterns:
            if re.search(pattern, output):
                issues.append(ValidationIssue(
                    severity="warning",
                    category="execution",
                    message=f"{description} detected in output",
                    suggestion="Review and address warning if necessary"
                ))
        
        # Check for suspicious content
        suspicious_patterns = [
            (r'password', "Potential password exposure"),
            (r'token', "Potential token exposure"),
            (r'key.*=.*[a-zA-Z0-9]{20,}', "Potential API key exposure"),
            (r'secret', "Potential secret exposure"),
            (r'DEBUG.*', "Debug information in output")
        ]
        
        for pattern, description in suspicious_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity="warning",
                    category="security",
                    message=description,
                    suggestion="Review output for sensitive information"
                ))
        
        # Script-type specific validation
        if script_type:
            type_issues = self._validate_by_script_type(output, script_type)
            issues.extend(type_issues)
        
        return issues
    
    def _analyze_performance(self, metrics: ExecutionMetrics, script_type: Optional[str]) -> List[ValidationIssue]:
        """Analyze performance metrics."""
        issues = []
        
        # Execution time analysis
        if metrics.execution_time > 30:
            issues.append(ValidationIssue(
                severity="warning",
                category="performance",
                message=f"Long execution time: {metrics.execution_time:.2f} seconds",
                suggestion="Consider optimizing the script for better performance"
            ))
        
        # Output size analysis
        if metrics.output_size > 1024 * 1024:  # > 1MB
            issues.append(ValidationIssue(
                severity="warning",
                category="performance",
                message=f"Large output size: {metrics.output_size} bytes",
                suggestion="Consider reducing output verbosity or using file output"
            ))
        
        # Script-type specific performance checks
        if script_type == "data_processing" and metrics.execution_time > 60:
            issues.append(ValidationIssue(
                severity="info",
                category="performance",
                message="Data processing script took over 1 minute",
                suggestion="Consider using more efficient data processing libraries"
            ))
        
        return issues
    
    def _compare_with_expected(self, actual: str, expected: str) -> List[ValidationIssue]:
        """Compare actual output with expected output."""
        issues = []
        
        # Normalize whitespace for comparison
        actual_norm = ' '.join(actual.split())
        expected_norm = ' '.join(expected.split())
        
        if actual_norm != expected_norm:
            # Calculate similarity
            similarity = self._calculate_similarity(actual_norm, expected_norm)
            
            if similarity < 0.8:
                issues.append(ValidationIssue(
                    severity="error",
                    category="correctness",
                    message=f"Output differs significantly from expected (similarity: {similarity:.2f})",
                    suggestion="Review script logic and expected output"
                ))
            elif similarity < 0.95:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="correctness",
                    message=f"Minor differences from expected output (similarity: {similarity:.2f})",
                    suggestion="Review output for minor discrepancies"
                ))
        
        return issues
    
    def _validate_by_script_type(self, output: str, script_type: str) -> List[ValidationIssue]:
        """Validate output based on script type."""
        issues = []
        
        if script_type == "data_processing":
            if not re.search(r'\d+', output):
                issues.append(ValidationIssue(
                    severity="warning",
                    category="correctness",
                    message="Data processing script produced no numeric output",
                    suggestion="Verify that data processing completed successfully"
                ))
        
        elif script_type == "web_scraping":
            if len(output) < 100:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="correctness",
                    message="Web scraping produced minimal output",
                    suggestion="Check if scraping target was accessible and contained data"
                ))
        
        elif script_type == "api_client":
            if "error" in output.lower() or "failed" in output.lower():
                issues.append(ValidationIssue(
                    severity="warning",
                    category="correctness",
                    message="API client indicates error or failure",
                    suggestion="Review API response and error handling"
                ))
        
        return issues
    
    def _try_parse_output(self, output: str, output_type: OutputType) -> Optional[Any]:
        """Try to parse structured output data."""
        if not output or output_type == OutputType.EMPTY:
            return None
        
        try:
            if output_type == OutputType.JSON:
                return json.loads(output.strip())
            
            elif output_type == OutputType.CSV:
                # Simple CSV parsing
                lines = output.strip().split('\n')
                return [line.split(',') for line in lines]
            
            elif output_type == OutputType.TEXT:
                # Try to extract key-value pairs
                kv_pairs = re.findall(r'(\w+):\s*(.+)', output)
                if kv_pairs:
                    return dict(kv_pairs)
        
        except Exception as e:
            logger.debug(f"Failed to parse output: {str(e)}")
        
        return None
    
    def _determine_status_confidence(
        self,
        output: str,
        error: Optional[str],
        issues: List[ValidationIssue],
        metrics: ExecutionMetrics,
        expected_output: Optional[str]
    ) -> Tuple[ResultStatus, float]:
        """Determine overall status and confidence level."""
        confidence = 1.0
        
        # Check for errors
        if error or metrics.error_count > 0:
            return ResultStatus.ERROR, 0.1
        
        # Check for critical issues
        critical_issues = [i for i in issues if i.severity == "error"]
        if critical_issues:
            return ResultStatus.INVALID, 0.2
        
        # Check for suspicious content
        suspicious_issues = [i for i in issues if i.category == "security"]
        if suspicious_issues:
            confidence *= 0.7
            return ResultStatus.SUSPICIOUS, confidence
        
        # Check if output exists
        if not output or output.strip() == "":
            if expected_output:
                return ResultStatus.INCOMPLETE, 0.3
            else:
                return ResultStatus.VALID, 0.8  # Empty output might be valid
        
        # Check warnings
        warning_count = len([i for i in issues if i.severity == "warning"])
        if warning_count > 0:
            confidence *= max(0.5, 1.0 - (warning_count * 0.1))
        
        # Check success indicators
        if any(re.search(indicator, output, re.IGNORECASE) for indicator in self._success_indicators):
            confidence *= 1.1  # Boost confidence for success indicators
        
        # Performance impact on confidence
        if metrics.execution_time > 30:
            confidence *= 0.9
        
        return ResultStatus.VALID, min(confidence, 1.0)
    
    def _generate_summary(
        self,
        status: ResultStatus,
        metrics: ExecutionMetrics,
        issues: List[ValidationIssue],
        output_type: OutputType
    ) -> str:
        """Generate validation summary."""
        summary_parts = [
            f"Status: {status.value.upper()}",
            f"Output Type: {output_type.value}",
            f"Execution Time: {metrics.execution_time:.3f}s"
        ]
        
        if metrics.output_size > 0:
            summary_parts.append(f"Output Size: {metrics.output_size} bytes")
        
        if issues:
            error_count = len([i for i in issues if i.severity == "error"])
            warning_count = len([i for i in issues if i.severity == "warning"])
            
            if error_count > 0:
                summary_parts.append(f"Errors: {error_count}")
            if warning_count > 0:
                summary_parts.append(f"Warnings: {warning_count}")
        
        return " | ".join(summary_parts)
    
    def _generate_recommendations(
        self,
        issues: List[ValidationIssue],
        metrics: ExecutionMetrics,
        script_type: Optional[str]
    ) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Error-based recommendations
        error_issues = [i for i in issues if i.severity == "error"]
        if error_issues:
            recommendations.append("Fix execution errors before considering the script valid")
        
        # Performance recommendations
        if metrics.execution_time > 30:
            recommendations.append("Consider optimizing script for better performance")
        
        if metrics.output_size > 1024 * 1024:
            recommendations.append("Large output detected - consider using file output or reducing verbosity")
        
        # Security recommendations
        security_issues = [i for i in issues if i.category == "security"]
        if security_issues:
            recommendations.append("Review output for potentially sensitive information")
        
        # Script-type recommendations
        if script_type == "web_scraping" and metrics.output_size < 100:
            recommendations.append("Web scraping produced minimal output - verify target accessibility")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Execution appears successful with no major issues")
        
        return recommendations
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity (simple implementation)."""
        if not str1 and not str2:
            return 1.0
        
        if not str1 or not str2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _get_error_suggestion(self, pattern: str) -> str:
        """Get suggestion for specific error patterns."""
        suggestions = {
            r'ValueError:': "Check input data types and value ranges",
            r'TypeError:': "Verify data types match expected function parameters",
            r'NameError:': "Check variable names and ensure proper initialization",
            r'ImportError:': "Verify required modules are installed and accessible",
            r'ModuleNotFoundError:': "Install missing Python packages or check module paths",
            r'FileNotFoundError:': "Check file paths and ensure files exist",
            r'PermissionError:': "Verify file/directory permissions",
            r'ConnectionError:': "Check network connectivity and target availability",
            r'TimeoutError:': "Increase timeout values or check system performance",
            r'KeyError:': "Verify dictionary keys exist before accessing",
            r'IndexError:': "Check list/array bounds before accessing elements",
            r'AttributeError:': "Verify object has the expected attributes",
            r'SyntaxError:': "Fix Python syntax errors",
            r'IndentationError:': "Fix code indentation",
            r'RuntimeError:': "Review runtime conditions and error handling"
        }
        
        return suggestions.get(pattern, "Review and fix the error")


# Convenience functions
def quick_validate_result(
    output: str,
    error: Optional[str] = None,
    execution_time: float = 0.0,
    script_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick result validation.
    
    Args:
        output: Script output
        error: Error message if any
        execution_time: Execution time
        script_type: Type of script
        
    Returns:
        Dictionary with validation results
    """
    validator = ResultValidator()
    result = validator.validate_execution_result(
        output, error, execution_time, script_type=script_type
    )
    
    return {
        "is_valid": result.is_valid,
        "status": result.status.value,
        "confidence": result.confidence,
        "output_type": result.output_type.value,
        "execution_time": result.metrics.execution_time,
        "total_issues": len(result.issues),
        "error_count": result.metrics.error_count,
        "warning_count": result.metrics.warning_count,
        "summary": result.summary,
        "recommendations": result.recommendations
    }


def validate_script_output(output_file: Path, script_type: str = None) -> ValidationResult:
    """
    Validate script output from file.
    
    Args:
        output_file: Path to output file
        script_type: Type of script that generated output
        
    Returns:
        ValidationResult
    """
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            output = f.read()
        
        validator = ResultValidator()
        return validator.validate_execution_result(output, script_type=script_type)
        
    except Exception as e:
        logger.error(f"Failed to validate output file: {str(e)}")
        return ValidationResult(
            status=ResultStatus.ERROR,
            is_valid=False,
            confidence=0.0,
            output_type=OutputType.ERROR,
            metrics=ExecutionMetrics(execution_time=0.0),
            issues=[ValidationIssue(
                severity="error",
                category="validation",
                message=f"Failed to read output file: {str(e)}"
            )],
            summary=f"Validation failed: {str(e)}"
        )