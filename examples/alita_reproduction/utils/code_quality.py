"""
Code Quality Checker for ALITA reproduction.

This module provides code quality analysis and validation utilities
for generated scripts and code snippets.
"""

import ast
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import sys
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeQualityChecker:
    """
    Code quality analysis and validation tool.
    
    This class provides various code quality checks including:
    - Syntax validation
    - Code complexity analysis
    - Security risk detection
    - Best practices validation
    - Style consistency checks
    """
    
    def __init__(self, max_complexity: int = 10, max_line_length: int = 88):
        """
        Initialize the CodeQualityChecker.
        
        Args:
            max_complexity: Maximum allowed cyclomatic complexity
            max_line_length: Maximum line length for style checks
        """
        self.max_complexity = max_complexity
        self.max_line_length = max_line_length
        
        # Security risk patterns
        self.security_patterns = {
            'eval_usage': r'\beval\s*\(',
            'exec_usage': r'\bexec\s*\(',
            'os_system': r'\bos\.system\s*\(',
            'subprocess_shell': r'\bsubprocess\.[a-zA-Z_]+\([^)]*shell\s*=\s*True',
            'pickle_loads': r'\bpickle\.loads?\s*\(',
            'input_function': r'\binput\s*\(',
            'open_write': r'\bopen\s*\([^)]*[\'"]w[\'"]',
        }
        
        # Code smell patterns
        self.code_smell_patterns = {
            'long_parameter_list': r'def\s+\w+\s*\([^)]{80,}\)',
            'magic_numbers': r'\b(?<![a-zA-Z_])\d{2,}(?![a-zA-Z_])',
            'print_statements': r'\bprint\s*\(',
            'global_variables': r'\bglobal\s+\w+',
            'bare_except': r'\bexcept\s*:',
        }
        
        logger.info("CodeQualityChecker initialized")
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file for code quality issues.
        
        Args:
            file_path: Path to Python file to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Analyzing file: {file_path}")
        
        if not Path(file_path).exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "file_path": file_path
            }
        
        try:
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
    
    def analyze_code(self, code: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze Python code for quality issues.
        
        Args:
            code: Python code string to analyze
            file_path: Optional file path for context
            
        Returns:
            Dictionary containing analysis results
        """
        results = {
            "success": True,
            "file_path": file_path,
            "syntax_valid": False,
            "overall_score": 0,
            "issues": [],
            "metrics": {},
            "suggestions": []
        }
        
        try:
            # 1. Syntax validation
            syntax_result = self._check_syntax(code)
            results["syntax_valid"] = syntax_result["is_valid"]
            
            if not syntax_result["is_valid"]:
                results["issues"].extend(syntax_result["errors"])
                results["suggestions"].extend(syntax_result["suggestions"])
            else:
                # Only proceed with other checks if syntax is valid
                
                # 2. Complexity analysis
                complexity_result = self._analyze_complexity(code)
                results["metrics"]["complexity"] = complexity_result
                results["issues"].extend(complexity_result.get("violations", []))
                
                # 3. Security risk detection
                security_result = self._check_security_risks(code)
                results["issues"].extend(security_result.get("risks", []))
                
                # 4. Code smell detection
                smell_result = self._check_code_smells(code)
                results["issues"].extend(smell_result.get("smells", []))
                
                # 5. Style and best practices
                style_result = self._check_style(code)
                results["issues"].extend(style_result.get("style_issues", []))
                results["suggestions"].extend(style_result.get("suggestions", []))
                
                # 6. Calculate overall score
                results["overall_score"] = self._calculate_score(results)
            
            logger.info(f"Code analysis completed. Score: {results['overall_score']}/100")
            return results
            
        except Exception as e:
            logger.error(f"Error during code analysis: {str(e)}")
            results["success"] = False
            results["error"] = str(e)
            return results
    
    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """Check Python syntax validity."""
        try:
            ast.parse(code)
            return {
                "is_valid": True,
                "errors": [],
                "suggestions": []
            }
        except SyntaxError as e:
            return {
                "is_valid": False,
                "errors": [{
                    "type": "syntax_error",
                    "severity": "critical",
                    "line": e.lineno,
                    "message": str(e),
                    "description": f"Syntax error at line {e.lineno}: {e.msg}"
                }],
                "suggestions": [
                    "Check for missing colons, brackets, or quotes",
                    "Verify proper indentation",
                    "Check for invalid Python syntax"
                ]
            }
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [{
                    "type": "parse_error",
                    "severity": "critical",
                    "message": str(e),
                    "description": f"Failed to parse code: {str(e)}"
                }],
                "suggestions": ["Check file encoding and content structure"]
            }
    
    def _analyze_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze cyclomatic complexity of code."""
        try:
            tree = ast.parse(code)
            complexity_analyzer = ComplexityAnalyzer()
            complexity_analyzer.visit(tree)
            
            violations = []
            total_complexity = 0
            
            for func_name, complexity in complexity_analyzer.complexities.items():
                total_complexity += complexity
                if complexity > self.max_complexity:
                    violations.append({
                        "type": "high_complexity",
                        "severity": "medium",
                        "function": func_name,
                        "complexity": complexity,
                        "max_allowed": self.max_complexity,
                        "description": f"Function '{func_name}' has complexity {complexity} (max allowed: {self.max_complexity})"
                    })
            
            return {
                "total_complexity": total_complexity,
                "function_complexities": dict(complexity_analyzer.complexities),
                "average_complexity": total_complexity / max(1, len(complexity_analyzer.complexities)),
                "violations": violations
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing complexity: {str(e)}")
            return {"error": str(e), "violations": []}
    
    def _check_security_risks(self, code: str) -> Dict[str, Any]:
        """Check for potential security risks in code."""
        risks = []
        
        for risk_type, pattern in self.security_patterns.items():
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                risks.append({
                    "type": "security_risk",
                    "subtype": risk_type,
                    "severity": "high" if risk_type in ['eval_usage', 'exec_usage'] else "medium",
                    "line": line_num,
                    "match": match.group(),
                    "description": self._get_security_description(risk_type)
                })
        
        return {"risks": risks}
    
    def _get_security_description(self, risk_type: str) -> str:
        """Get description for security risk type."""
        descriptions = {
            'eval_usage': "Use of eval() can execute arbitrary code and is a security risk",
            'exec_usage': "Use of exec() can execute arbitrary code and is a security risk",
            'os_system': "Using os.system() with user input can lead to command injection",
            'subprocess_shell': "Using shell=True in subprocess can lead to command injection",
            'pickle_loads': "Pickle deserialization can execute arbitrary code",
            'input_function': "Using input() function can be exploited in some contexts",
            'open_write': "Writing files without validation can be a security risk"
        }
        return descriptions.get(risk_type, f"Potential security risk: {risk_type}")
    
    def _check_code_smells(self, code: str) -> Dict[str, Any]:
        """Check for code smells and anti-patterns."""
        smells = []
        
        for smell_type, pattern in self.code_smell_patterns.items():
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                smells.append({
                    "type": "code_smell",
                    "subtype": smell_type,
                    "severity": "low",
                    "line": line_num,
                    "match": match.group(),
                    "description": self._get_smell_description(smell_type)
                })
        
        return {"smells": smells}
    
    def _get_smell_description(self, smell_type: str) -> str:
        """Get description for code smell type."""
        descriptions = {
            'long_parameter_list': "Function has too many parameters, consider refactoring",
            'magic_numbers': "Magic numbers should be replaced with named constants",
            'print_statements': "Print statements should be replaced with logging",
            'global_variables': "Global variables can make code harder to test and maintain",
            'bare_except': "Bare except clauses can hide important errors"
        }
        return descriptions.get(smell_type, f"Code smell detected: {smell_type}")
    
    def _check_style(self, code: str) -> Dict[str, Any]:
        """Check style and formatting issues."""
        style_issues = []
        suggestions = []
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > self.max_line_length:
                style_issues.append({
                    "type": "style_issue",
                    "subtype": "long_line",
                    "severity": "low",
                    "line": i,
                    "length": len(line),
                    "max_allowed": self.max_line_length,
                    "description": f"Line {i} is {len(line)} characters long (max: {self.max_line_length})"
                })
            
            # Check trailing whitespace
            if line.rstrip() != line:
                style_issues.append({
                    "type": "style_issue",
                    "subtype": "trailing_whitespace",
                    "severity": "low",
                    "line": i,
                    "description": f"Line {i} has trailing whitespace"
                })
        
        # General suggestions based on detected issues
        if any(issue["subtype"] == "long_line" for issue in style_issues):
            suggestions.append("Consider breaking long lines for better readability")
        
        if any(issue["subtype"] == "trailing_whitespace" for issue in style_issues):
            suggestions.append("Remove trailing whitespace from lines")
        
        return {
            "style_issues": style_issues,
            "suggestions": suggestions
        }
    
    def _calculate_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall quality score (0-100)."""
        score = 100
        
        # Deduct points for issues based on severity
        for issue in results["issues"]:
            severity = issue.get("severity", "low")
            if severity == "critical":
                score -= 20
            elif severity == "high":
                score -= 10
            elif severity == "medium":
                score -= 5
            elif severity == "low":
                score -= 2
        
        return max(0, score)
    
    def get_quality_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable quality report."""
        if not results.get("success", False):
            return f"Analysis failed: {results.get('error', 'Unknown error')}"
        
        report_lines = [
            f"Code Quality Report",
            f"==================",
            f"File: {results.get('file_path', 'N/A')}",
            f"Overall Score: {results['overall_score']}/100",
            f"Syntax Valid: {'Yes' if results['syntax_valid'] else 'No'}",
            f""
        ]
        
        # Group issues by type and severity
        issue_groups = defaultdict(list)
        for issue in results["issues"]:
            key = f"{issue.get('severity', 'unknown').title()} {issue.get('type', 'issue').replace('_', ' ').title()}s"
            issue_groups[key].append(issue)
        
        if issue_groups:
            report_lines.append("Issues Found:")
            report_lines.append("=============")
            
            for group_name, issues in sorted(issue_groups.items()):
                report_lines.append(f"\n{group_name} ({len(issues)}):")
                for issue in issues:
                    line_info = f" (line {issue['line']})" if 'line' in issue else ""
                    report_lines.append(f"  - {issue.get('description', 'No description')}{line_info}")
        else:
            report_lines.append("No issues found! ✅")
        
        if results.get("suggestions"):
            report_lines.extend([
                "\nSuggestions:",
                "============"
            ])
            for suggestion in results["suggestions"]:
                report_lines.append(f"  - {suggestion}")
        
        # Add metrics if available
        metrics = results.get("metrics", {})
        if metrics:
            report_lines.extend([
                "\nMetrics:",
                "========"
            ])
            
            if "complexity" in metrics:
                complexity = metrics["complexity"]
                if "total_complexity" in complexity:
                    report_lines.append(f"  Total Complexity: {complexity['total_complexity']}")
                if "average_complexity" in complexity:
                    report_lines.append(f"  Average Complexity: {complexity['average_complexity']:.2f}")
        
        return '\n'.join(report_lines)


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor for calculating cyclomatic complexity."""
    
    def __init__(self):
        self.complexities = defaultdict(int)
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        old_function = self.current_function
        self.current_function = node.name
        self.complexities[node.name] = 1  # Base complexity
        
        self.generic_visit(node)
        
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition."""
        self.visit_FunctionDef(node)
    
    def visit_If(self, node):
        """Visit if statement."""
        if self.current_function:
            self.complexities[self.current_function] += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Visit while loop."""
        if self.current_function:
            self.complexities[self.current_function] += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Visit for loop."""
        if self.current_function:
            self.complexities[self.current_function] += 1
        self.generic_visit(node)
    
    def visit_AsyncFor(self, node):
        """Visit async for loop."""
        self.visit_For(node)
    
    def visit_ExceptHandler(self, node):
        """Visit except handler."""
        if self.current_function:
            self.complexities[self.current_function] += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        """Visit with statement."""
        if self.current_function:
            self.complexities[self.current_function] += 1
        self.generic_visit(node)
    
    def visit_AsyncWith(self, node):
        """Visit async with statement."""
        self.visit_With(node)


def quick_check(code: str) -> Dict[str, Any]:
    """
    Perform a quick code quality check.
    
    Args:
        code: Python code string to check
        
    Returns:
        Dictionary with basic quality information
    """
    checker = CodeQualityChecker()
    results = checker.analyze_code(code)
    
    return {
        "score": results["overall_score"],
        "syntax_valid": results["syntax_valid"],
        "critical_issues": len([i for i in results["issues"] if i.get("severity") == "critical"]),
        "total_issues": len(results["issues"]),
        "has_security_risks": any(i.get("type") == "security_risk" for i in results["issues"])
    }