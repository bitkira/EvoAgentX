"""
Simplified Code Quality Checker for ALITA reproduction.

This module provides simplified code quality analysis focused on security
and basic validation for LLM-generated scripts.
"""

import ast
import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeQualityChecker:
    """
    Simplified code quality analysis tool focused on security and basic validation.
    
    This class provides essential code quality checks:
    - Syntax validation
    - Security risk detection
    - Basic structure validation
    - Essential best practices
    """
    
    def __init__(self):
        """Initialize the simplified CodeQualityChecker."""
        
        # Critical security patterns
        self.security_risks = {
            'eval_exec': ['eval', 'exec', '__import__', 'compile'],
            'dangerous_imports': ['os.system', 'subprocess', 'pickle.loads'],
            'file_operations': ['open', 'file'],
            'network_operations': ['socket', 'urllib', 'requests']
        }
        
        # Basic code smells to detect
        self.code_smells = {
            'bare_except': r'\bexcept\s*:',
            'print_debug': r'\bprint\s*\(',
            'global_vars': r'\bglobal\s+\w+'
        }
        
        logger.info("Simplified CodeQualityChecker initialized")
    
    def analyze_code(self, code: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze Python code for critical quality and security issues.
        
        Args:
            code: Python code string to analyze
            file_path: Optional file path for context
            
        Returns:
            Dictionary containing analysis results
        """
        logger.debug(f"Analyzing code {'from ' + file_path if file_path else ''}")
        
        try:
            # Initialize results
            issues = []
            security_risks = []
            warnings = []
            
            # 1. Syntax validation
            syntax_result = self._check_syntax(code)
            if not syntax_result['is_valid']:
                return {
                    "success": False,
                    "is_valid": False,
                    "error": syntax_result['error'],
                    "file_path": file_path
                }
            
            # 2. Security analysis
            security_issues = self._analyze_security(code)
            security_risks.extend(security_issues)
            
            # 3. Basic structure checks
            structure_issues = self._check_structure(code)
            issues.extend(structure_issues)
            
            # 4. Code smell detection
            smell_warnings = self._detect_code_smells(code)
            warnings.extend(smell_warnings)
            
            # Determine overall status
            has_critical_issues = bool(security_risks) or any(
                issue.get('severity') == 'critical' for issue in issues
            )
            
            return {
                "success": True,
                "is_valid": not has_critical_issues,
                "security_risks": security_risks,
                "issues": issues,
                "warnings": warnings,
                "summary": {
                    "total_issues": len(issues),
                    "security_risks": len(security_risks),
                    "warnings": len(warnings),
                    "has_critical_issues": has_critical_issues
                },
                "file_path": file_path
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return {
                "success": False,
                "error": f"Analysis error: {str(e)}",
                "file_path": file_path
            }
    
    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """Check Python syntax validity."""
        try:
            ast.parse(code)
            return {"is_valid": True, "error": None}
        except SyntaxError as e:
            return {
                "is_valid": False,
                "error": f"Syntax error at line {e.lineno}: {e.msg}",
                "line_number": e.lineno
            }
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Parse error: {str(e)}"
            }
    
    def _analyze_security(self, code: str) -> List[Dict[str, Any]]:
        """Analyze code for security risks."""
        risks = []
        
        try:
            tree = ast.parse(code)
            
            # Check AST nodes for security issues
            for node in ast.walk(tree):
                # Check dangerous function calls
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in self.security_risks['eval_exec']:
                        risks.append({
                            "type": "dangerous_function",
                            "description": f"Use of dangerous function: {func_name}",
                            "severity": "critical",
                            "line": getattr(node, 'lineno', 'unknown')
                        })
                
                # Check dangerous imports
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_names = []
                    if isinstance(node, ast.Import):
                        module_names = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        module_names = [node.module]
                    
                    for module in module_names:
                        for dangerous_pattern in self.security_risks['dangerous_imports']:
                            if dangerous_pattern in module:
                                risks.append({
                                    "type": "dangerous_import",
                                    "description": f"Potentially dangerous import: {module}",
                                    "severity": "high",
                                    "line": getattr(node, 'lineno', 'unknown')
                                })
        
        except Exception as e:
            logger.warning(f"Security analysis failed: {str(e)}")
            risks.append({
                "type": "analysis_error",
                "description": "Could not complete security analysis",
                "severity": "medium"
            })
        
        return risks
    
    def _check_structure(self, code: str) -> List[Dict[str, Any]]:
        """Check basic code structure requirements."""
        issues = []
        
        # Check for main function
        if "def main(" not in code:
            issues.append({
                "type": "missing_main",
                "description": "Missing main() function",
                "severity": "medium",
                "suggestion": "Add a main() function for better code organization"
            })
        
        # Check for proper execution guard
        if "if __name__ == '__main__':" not in code:
            issues.append({
                "type": "missing_guard",
                "description": "Missing execution guard",
                "severity": "low",
                "suggestion": "Add 'if __name__ == '__main__':' guard"
            })
        
        # Check for docstrings
        try:
            tree = ast.parse(code)
            if not ast.get_docstring(tree):
                issues.append({
                    "type": "missing_docstring",
                    "description": "Missing module docstring",
                    "severity": "low",
                    "suggestion": "Add a module-level docstring"
                })
        except:
            pass
        
        return issues
    
    def _detect_code_smells(self, code: str) -> List[Dict[str, Any]]:
        """Detect basic code smells."""
        warnings = []
        
        # Check for bare except clauses
        if re.search(self.code_smells['bare_except'], code):
            warnings.append({
                "type": "bare_except",
                "description": "Bare except clause found",
                "suggestion": "Specify exception types in except clauses"
            })
        
        # Check for print statements (debugging)
        print_matches = len(re.findall(self.code_smells['print_debug'], code))
        if print_matches > 3:  # Allow some print statements
            warnings.append({
                "type": "excessive_prints",
                "description": f"Found {print_matches} print statements",
                "suggestion": "Consider using logging instead of print for debugging"
            })
        
        # Check for global variables
        if re.search(self.code_smells['global_vars'], code):
            warnings.append({
                "type": "global_variables",
                "description": "Global variables found",
                "suggestion": "Minimize use of global variables"
            })
        
        return warnings
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file for code quality issues.
        
        Args:
            file_path: Path to Python file to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Analyzing file: {file_path}")
        
        try:
            if not Path(file_path).exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "file_path": file_path
                }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.analyze_code(content, file_path)
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}",
                "file_path": file_path
            }
    
    def quick_validate(self, code: str) -> bool:
        """
        Quick validation for basic syntax and critical security issues.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if code passes basic validation
        """
        try:
            # Syntax check
            ast.parse(code)
            
            # Quick security check for most dangerous patterns
            dangerous_patterns = ['eval(', 'exec(', '__import__(', 'os.system(']
            for pattern in dangerous_patterns:
                if pattern in code:
                    return False
            
            return True
            
        except (SyntaxError, Exception):
            return False
    
    def get_validation_summary(self, analysis_result: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of validation results.
        
        Args:
            analysis_result: Result from analyze_code()
            
        Returns:
            Formatted summary string
        """
        if not analysis_result.get("success"):
            return f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}"
        
        summary = analysis_result.get("summary", {})
        is_valid = analysis_result.get("is_valid", False)
        
        status = "✅ VALID" if is_valid else "❌ INVALID"
        
        parts = [
            f"{status}",
            f"Security risks: {summary.get('security_risks', 0)}",
            f"Issues: {summary.get('total_issues', 0)}",
            f"Warnings: {summary.get('warnings', 0)}"
        ]
        
        result = " | ".join(parts)
        
        # Add critical issues details
        if summary.get('has_critical_issues'):
            critical_details = []
            for risk in analysis_result.get("security_risks", []):
                if risk.get("severity") == "critical":
                    critical_details.append(risk.get("description", "Unknown issue"))
            
            if critical_details:
                result += f"\n⚠️  Critical: {'; '.join(critical_details)}"
        
        return result