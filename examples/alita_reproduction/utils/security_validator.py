#!/usr/bin/env python3
"""
Security Validator for ALITA reproduction.

This module provides comprehensive security validation for generated scripts
and code execution, including static analysis, pattern detection, and risk assessment.

Author: ALITA Development Team
Created: 2025-08-13
Version: 1.0.0
"""

import ast
import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security risk levels."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationType(Enum):
    """Security violation types."""
    DANGEROUS_IMPORT = "dangerous_import"
    SYSTEM_COMMAND = "system_command"
    FILE_ACCESS = "file_access"
    NETWORK_ACCESS = "network_access"
    DYNAMIC_EXECUTION = "dynamic_execution"
    SUBPROCESS_USAGE = "subprocess_usage"
    SECURITY_BYPASS = "security_bypass"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PRIVILEGE_ESCALATION = "privilege_escalation"


@dataclass
class SecurityIssue:
    """Security issue data class."""
    violation_type: ViolationType
    severity: SecurityLevel
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None


@dataclass
class SecurityReport:
    """Comprehensive security analysis report."""
    overall_risk: SecurityLevel
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    issues: List[SecurityIssue]
    analysis_time: float
    is_safe_to_execute: bool
    recommendations: List[str]


class SecurityValidator:
    """
    Comprehensive security validator for code analysis.
    
    Provides static analysis, pattern detection, and risk assessment
    for Python code and scripts before execution.
    """
    
    def __init__(self):
        """Initialize security validator."""
        self._dangerous_imports = {
            'subprocess': (SecurityLevel.HIGH, "Can execute system commands"),
            'os': (SecurityLevel.MEDIUM, "Provides system access functions"),
            'sys': (SecurityLevel.MEDIUM, "Can modify system settings"),
            'socket': (SecurityLevel.HIGH, "Network communication capability"),
            'urllib': (SecurityLevel.MEDIUM, "HTTP/URL access capability"),
            'requests': (SecurityLevel.MEDIUM, "HTTP request library"),
            'paramiko': (SecurityLevel.HIGH, "SSH/SFTP library"),
            'ftplib': (SecurityLevel.MEDIUM, "FTP access library"),
            'telnetlib': (SecurityLevel.HIGH, "Telnet access library"),
            'smtplib': (SecurityLevel.MEDIUM, "Email sending capability"),
            'poplib': (SecurityLevel.MEDIUM, "Email receiving capability"),
            'imaplib': (SecurityLevel.MEDIUM, "Email access library"),
            'pickle': (SecurityLevel.HIGH, "Can execute arbitrary code during deserialization"),
            'marshal': (SecurityLevel.HIGH, "Can execute code during unmarshaling"),
            'ctypes': (SecurityLevel.CRITICAL, "Direct memory access and system calls"),
            'multiprocessing': (SecurityLevel.MEDIUM, "Process creation and management"),
            'threading': (SecurityLevel.LOW, "Thread creation and management"),
            'importlib': (SecurityLevel.MEDIUM, "Dynamic import capability"),
            'types': (SecurityLevel.MEDIUM, "Dynamic type creation"),
            'code': (SecurityLevel.HIGH, "Code compilation and execution"),
            'platform': (SecurityLevel.LOW, "System information access")
        }
        
        self._dangerous_functions = {
            'eval': (SecurityLevel.CRITICAL, "Dynamic code evaluation"),
            'exec': (SecurityLevel.CRITICAL, "Dynamic code execution"),
            'compile': (SecurityLevel.HIGH, "Code compilation"),
            '__import__': (SecurityLevel.HIGH, "Dynamic import"),
            'getattr': (SecurityLevel.MEDIUM, "Dynamic attribute access"),
            'setattr': (SecurityLevel.MEDIUM, "Dynamic attribute modification"),
            'hasattr': (SecurityLevel.LOW, "Attribute existence check"),
            'delattr': (SecurityLevel.MEDIUM, "Dynamic attribute deletion"),
            'globals': (SecurityLevel.MEDIUM, "Global namespace access"),
            'locals': (SecurityLevel.MEDIUM, "Local namespace access"),
            'vars': (SecurityLevel.MEDIUM, "Variable namespace access"),
            'dir': (SecurityLevel.LOW, "Object introspection"),
            'id': (SecurityLevel.LOW, "Object identity"),
            'type': (SecurityLevel.LOW, "Type introspection"),
            'isinstance': (SecurityLevel.LOW, "Type checking"),
            'issubclass': (SecurityLevel.LOW, "Inheritance checking")
        }
        
        self._dangerous_patterns = [
            (r'os\.system\s*\(', SecurityLevel.CRITICAL, "System command execution"),
            (r'os\.popen\s*\(', SecurityLevel.HIGH, "Process creation with shell"),
            (r'os\.spawn[^(]*\s*\(', SecurityLevel.HIGH, "Process spawning"),
            (r'subprocess\.[^(]+\s*\(', SecurityLevel.HIGH, "Subprocess execution"),
            (r'eval\s*\(', SecurityLevel.CRITICAL, "Dynamic code evaluation"),
            (r'exec\s*\(', SecurityLevel.CRITICAL, "Dynamic code execution"),
            (r'compile\s*\(', SecurityLevel.HIGH, "Code compilation"),
            (r'__import__\s*\(', SecurityLevel.HIGH, "Dynamic import"),
            (r'open\s*\([^)]*["\'][rwa]', SecurityLevel.MEDIUM, "File access operation"),
            (r'urllib\.request\.urlopen', SecurityLevel.MEDIUM, "URL/HTTP request"),
            (r'requests\.[a-zA-Z]+\s*\(', SecurityLevel.MEDIUM, "HTTP request"),
            (r'socket\.socket\s*\(', SecurityLevel.HIGH, "Socket creation"),
            (r'input\s*\([^)]*\)', SecurityLevel.LOW, "User input required"),
            (r'getpass\.getpass\s*\(', SecurityLevel.LOW, "Password input"),
            (r'os\.environ\[["\'][^"\']*["\']\]', SecurityLevel.MEDIUM, "Environment variable access"),
            (r'sys\.exit\s*\(', SecurityLevel.LOW, "Program termination"),
            (r'quit\s*\(', SecurityLevel.LOW, "Program termination"),
            (r'exit\s*\(', SecurityLevel.LOW, "Program termination"),
            (r'while\s+True\s*:', SecurityLevel.MEDIUM, "Infinite loop detected"),
            (r'for\s+[^:]+\s+in\s+range\s*\(\s*\d{6,}', SecurityLevel.MEDIUM, "Large range iteration")
        ]
        
        logger.info("SecurityValidator initialized with comprehensive rule sets")
    
    def analyze_code(self, code: str) -> SecurityReport:
        """
        Perform comprehensive security analysis on code.
        
        Args:
            code: Python code to analyze
            
        Returns:
            SecurityReport with detailed analysis
        """
        import time
        start_time = time.time()
        
        logger.info("Starting comprehensive security analysis")
        
        issues: List[SecurityIssue] = []
        
        try:
            # Parse AST for structural analysis
            tree = ast.parse(code)
            issues.extend(self._analyze_ast(tree))
            
        except SyntaxError as e:
            issues.append(SecurityIssue(
                violation_type=ViolationType.SECURITY_BYPASS,
                severity=SecurityLevel.HIGH,
                description=f"Syntax error could hide malicious code: {str(e)}",
                line_number=e.lineno,
                recommendation="Fix syntax errors before security analysis"
            ))
        except Exception as e:
            logger.error(f"AST analysis failed: {str(e)}")
        
        # Pattern-based analysis
        issues.extend(self._analyze_patterns(code))
        
        # Import analysis
        issues.extend(self._analyze_imports(code))
        
        # Function analysis
        issues.extend(self._analyze_functions(code))
        
        # Generate report
        analysis_time = time.time() - start_time
        report = self._generate_report(issues, analysis_time)
        
        logger.info(f"Security analysis completed: {report.total_issues} issues found")
        return report
    
    def _analyze_ast(self, tree: ast.AST) -> List[SecurityIssue]:
        """
        Analyze AST for security issues.
        
        Args:
            tree: AST tree to analyze
            
        Returns:
            List of security issues
        """
        issues: List[SecurityIssue] = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self, issues_list):
                self.issues = issues_list
                self.depth = 0
                self.in_function = False
            
            def visit_Import(self, node):
                for alias in node.names:
                    if alias.name in self._dangerous_imports:
                        level, desc = self._dangerous_imports[alias.name]
                        self.issues.append(SecurityIssue(
                            violation_type=ViolationType.DANGEROUS_IMPORT,
                            severity=level,
                            description=f"Import of potentially dangerous module '{alias.name}': {desc}",
                            line_number=node.lineno,
                            recommendation=f"Consider alternatives to '{alias.name}' or ensure secure usage"
                        ))
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module and node.module in self._dangerous_imports:
                    level, desc = self._dangerous_imports[node.module]
                    self.issues.append(SecurityIssue(
                        violation_type=ViolationType.DANGEROUS_IMPORT,
                        severity=level,
                        description=f"Import from potentially dangerous module '{node.module}': {desc}",
                        line_number=node.lineno,
                        recommendation=f"Review usage of functions from '{node.module}'"
                    ))
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in self._dangerous_functions:
                        level, desc = self._dangerous_functions[func_name]
                        self.issues.append(SecurityIssue(
                            violation_type=ViolationType.DYNAMIC_EXECUTION,
                            severity=level,
                            description=f"Call to dangerous function '{func_name}': {desc}",
                            line_number=node.lineno,
                            recommendation=f"Avoid using '{func_name}' or ensure input validation"
                        ))
                
                # Check for attribute calls (e.g., os.system)
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        module_name = node.func.value.id
                        attr_name = node.func.attr
                        full_name = f"{module_name}.{attr_name}"
                        
                        if full_name in ['os.system', 'os.popen', 'os.spawn*']:
                            self.issues.append(SecurityIssue(
                                violation_type=ViolationType.SYSTEM_COMMAND,
                                severity=SecurityLevel.CRITICAL,
                                description=f"System command execution via '{full_name}'",
                                line_number=node.lineno,
                                recommendation="Use subprocess with shell=False or avoid system commands"
                            ))
                
                self.generic_visit(node)
            
            def visit_While(self, node):
                # Check for infinite loops
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    self.issues.append(SecurityIssue(
                        violation_type=ViolationType.RESOURCE_EXHAUSTION,
                        severity=SecurityLevel.MEDIUM,
                        description="Infinite while loop detected",
                        line_number=node.lineno,
                        recommendation="Ensure loop has proper termination conditions"
                    ))
                self.generic_visit(node)
            
            def visit_For(self, node):
                # Check for large range iterations
                if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
                    if node.iter.func.id == 'range' and node.iter.args:
                        if isinstance(node.iter.args[-1], ast.Constant):
                            if isinstance(node.iter.args[-1].value, int) and node.iter.args[-1].value > 100000:
                                self.issues.append(SecurityIssue(
                                    violation_type=ViolationType.RESOURCE_EXHAUSTION,
                                    severity=SecurityLevel.MEDIUM,
                                    description=f"Large range iteration: {node.iter.args[-1].value}",
                                    line_number=node.lineno,
                                    recommendation="Consider if large iterations are necessary"
                                ))
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                old_in_function = self.in_function
                self.in_function = True
                
                # Check for suspicious function names
                suspicious_names = ['exploit', 'hack', 'bypass', 'crack', 'inject']
                if any(name in node.name.lower() for name in suspicious_names):
                    self.issues.append(SecurityIssue(
                        violation_type=ViolationType.SECURITY_BYPASS,
                        severity=SecurityLevel.MEDIUM,
                        description=f"Suspicious function name: '{node.name}'",
                        line_number=node.lineno,
                        recommendation="Review function purpose and rename if legitimate"
                    ))
                
                self.generic_visit(node)
                self.in_function = old_in_function
        
        visitor = SecurityVisitor(issues)
        visitor.visit(tree)
        
        return issues
    
    def _analyze_patterns(self, code: str) -> List[SecurityIssue]:
        """
        Analyze code using regex patterns.
        
        Args:
            code: Code to analyze
            
        Returns:
            List of security issues
        """
        issues: List[SecurityIssue] = []
        lines = code.split('\n')
        
        for pattern, severity, description in self._dangerous_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        violation_type=ViolationType.SYSTEM_COMMAND,
                        severity=severity,
                        description=f"{description} at line {line_num}",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation="Review and validate this operation"
                    ))
        
        return issues
    
    def _analyze_imports(self, code: str) -> List[SecurityIssue]:
        """
        Analyze import statements.
        
        Args:
            code: Code to analyze
            
        Returns:
            List of security issues
        """
        issues: List[SecurityIssue] = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Simple import analysis
            if line.startswith('import ') or line.startswith('from '):
                # Extract module names
                if 'import ' in line:
                    parts = line.split('import ')
                    if len(parts) > 1:
                        modules = [m.strip() for m in parts[1].split(',')]
                        for module in modules:
                            module = module.split(' as ')[0].strip()  # Remove alias
                            if module in self._dangerous_imports:
                                level, desc = self._dangerous_imports[module]
                                issues.append(SecurityIssue(
                                    violation_type=ViolationType.DANGEROUS_IMPORT,
                                    severity=level,
                                    description=f"Import of dangerous module '{module}': {desc}",
                                    line_number=line_num,
                                    code_snippet=line,
                                    recommendation=f"Ensure secure usage of '{module}'"
                                ))
        
        return issues
    
    def _analyze_functions(self, code: str) -> List[SecurityIssue]:
        """
        Analyze function calls.
        
        Args:
            code: Code to analyze
            
        Returns:
            List of security issues
        """
        issues: List[SecurityIssue] = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for func_name, (severity, description) in self._dangerous_functions.items():
                if f'{func_name}(' in line:
                    issues.append(SecurityIssue(
                        violation_type=ViolationType.DYNAMIC_EXECUTION,
                        severity=severity,
                        description=f"Use of dangerous function '{func_name}': {description}",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation=f"Avoid '{func_name}' or validate inputs carefully"
                    ))
        
        return issues
    
    def _generate_report(self, issues: List[SecurityIssue], analysis_time: float) -> SecurityReport:
        """
        Generate comprehensive security report.
        
        Args:
            issues: List of security issues
            analysis_time: Time taken for analysis
            
        Returns:
            SecurityReport
        """
        # Count issues by severity
        critical = sum(1 for issue in issues if issue.severity == SecurityLevel.CRITICAL)
        high = sum(1 for issue in issues if issue.severity == SecurityLevel.HIGH)
        medium = sum(1 for issue in issues if issue.severity == SecurityLevel.MEDIUM)
        low = sum(1 for issue in issues if issue.severity == SecurityLevel.LOW)
        
        # Determine overall risk
        if critical > 0:
            overall_risk = SecurityLevel.CRITICAL
        elif high > 0:
            overall_risk = SecurityLevel.HIGH
        elif medium > 0:
            overall_risk = SecurityLevel.MEDIUM
        elif low > 0:
            overall_risk = SecurityLevel.LOW
        else:
            overall_risk = SecurityLevel.SAFE
        
        # Determine if safe to execute
        is_safe = critical == 0 and high == 0
        
        # Generate recommendations
        recommendations = []
        if critical > 0:
            recommendations.append("CRITICAL: Do not execute this code without thorough review")
        if high > 0:
            recommendations.append("HIGH: Review and mitigate high-risk operations")
        if medium > 0:
            recommendations.append("MEDIUM: Validate inputs and review medium-risk operations")
        if len(issues) == 0:
            recommendations.append("Code appears safe for execution")
        
        return SecurityReport(
            overall_risk=overall_risk,
            total_issues=len(issues),
            critical_issues=critical,
            high_issues=high,
            medium_issues=medium,
            low_issues=low,
            issues=issues,
            analysis_time=analysis_time,
            is_safe_to_execute=is_safe,
            recommendations=recommendations
        )
    
    def validate_script_file(self, script_path: Path) -> SecurityReport:
        """
        Validate a script file.
        
        Args:
            script_path: Path to script file
            
        Returns:
            SecurityReport
        """
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            logger.info(f"Validating script file: {script_path}")
            return self.analyze_code(code)
            
        except Exception as e:
            logger.error(f"Failed to validate script file: {str(e)}")
            return SecurityReport(
                overall_risk=SecurityLevel.CRITICAL,
                total_issues=1,
                critical_issues=1,
                high_issues=0,
                medium_issues=0,
                low_issues=0,
                issues=[SecurityIssue(
                    violation_type=ViolationType.SECURITY_BYPASS,
                    severity=SecurityLevel.CRITICAL,
                    description=f"Failed to read/analyze file: {str(e)}",
                    recommendation="Ensure file is readable and contains valid Python code"
                )],
                analysis_time=0.0,
                is_safe_to_execute=False,
                recommendations=["Cannot validate - do not execute"]
            )
    
    def get_security_summary(self, report: SecurityReport) -> str:
        """
        Generate a human-readable security summary.
        
        Args:
            report: SecurityReport to summarize
            
        Returns:
            Summary string
        """
        summary = f"""Security Analysis Summary:
Overall Risk Level: {report.overall_risk.value.upper()}
Safe to Execute: {'Yes' if report.is_safe_to_execute else 'No'}

Issue Breakdown:
- Critical: {report.critical_issues}
- High: {report.high_issues}
- Medium: {report.medium_issues}
- Low: {report.low_issues}
- Total: {report.total_issues}

Analysis Time: {report.analysis_time:.3f} seconds

Recommendations:"""
        
        for rec in report.recommendations:
            summary += f"\n- {rec}"
        
        if report.issues and len(report.issues) <= 10:
            summary += "\n\nDetailed Issues:"
            for issue in report.issues:
                summary += f"\n- {issue.severity.value.upper()}: {issue.description}"
                if issue.line_number:
                    summary += f" (Line {issue.line_number})"
        elif len(report.issues) > 10:
            summary += f"\n\nShowing first 10 of {len(report.issues)} issues:"
            for issue in report.issues[:10]:
                summary += f"\n- {issue.severity.value.upper()}: {issue.description}"
                if issue.line_number:
                    summary += f" (Line {issue.line_number})"
        
        return summary


# Convenience functions
def quick_security_check(code: str) -> Dict[str, Any]:
    """
    Quick security check for code.
    
    Args:
        code: Code to check
        
    Returns:
        Dictionary with security check results
    """
    validator = SecurityValidator()
    report = validator.analyze_code(code)
    
    return {
        "is_safe": report.is_safe_to_execute,
        "risk_level": report.overall_risk.value,
        "total_issues": report.total_issues,
        "critical_issues": report.critical_issues,
        "high_issues": report.high_issues,
        "summary": validator.get_security_summary(report)
    }


def validate_file_security(file_path: str) -> Dict[str, Any]:
    """
    Validate security of a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with validation results
    """
    validator = SecurityValidator()
    report = validator.validate_script_file(Path(file_path))
    
    return {
        "is_safe": report.is_safe_to_execute,
        "risk_level": report.overall_risk.value,
        "total_issues": report.total_issues,
        "critical_issues": report.critical_issues,
        "high_issues": report.high_issues,
        "summary": validator.get_security_summary(report)
    }