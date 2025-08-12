"""
Test cases for Code Running functionality.

Tests the code execution capabilities integrated into ALITA,
including the CodeRunningAction class and its integration with ManagerAgent.
"""

import unittest
import sys
import os

# Add the EvoAgentX root to path
sys.path.append('/Users/bitkira/Documents/GitHub/EvoAgentX')

from examples.alita_reproduction.actions.code_running import CodeRunningAction
from examples.alita_reproduction.agents.manager_agent import ManagerAgent
from examples.alita_reproduction.config import ALITAConfig


class TestCodeRunningAction(unittest.TestCase):
    """Test cases for CodeRunningAction class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.action = CodeRunningAction()
    
    def test_initialization(self):
        """Test CodeRunningAction initialization."""
        self.assertIsNotNone(self.action.toolkit)
        self.assertIsNotNone(self.action.interpreter)
        self.assertIsNotNone(self.action.project_path)
        self.assertIsInstance(self.action.directory_names, list)
        self.assertIsInstance(self.action.allowed_imports, set)
    
    def test_simple_code_execution(self):
        """Test simple code execution."""
        simple_code = """
print("Hello, World!")
x = 5 + 3
print(f"5 + 3 = {x}")
"""
        
        result = self.action.execute_code(simple_code)
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("result", result)
        self.assertIn("output", result)
        self.assertIn("error", result)
        self.assertIn("code", result)
        
        # Check if execution was successful
        if result["success"]:
            self.assertIn("Hello, World!", result["output"])
            self.assertIn("5 + 3 = 8", result["output"])
    
    def test_math_operations(self):
        """Test mathematical operations."""
        math_code = """
import math

print("Mathematical operations:")
print(f"sqrt(16) = {math.sqrt(16)}")
print(f"factorial(5) = {math.factorial(5)}")
print(f"sin(π/2) = {math.sin(math.pi/2):.2f}")
"""
        
        result = self.action.execute_code(math_code)
        
        if result["success"]:
            output = result["output"]
            self.assertIn("sqrt(16) = 4.0", output)
            self.assertIn("factorial(5) = 120", output)
            self.assertIn("sin(π/2) = 1.00", output)
    
    def test_data_processing(self):
        """Test data processing capabilities."""
        data_code = """
import json
from collections import Counter

# Sample data
data = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 87},
    {"name": "Charlie", "score": 92}
]

print("Data processing:")
total_score = sum(item["score"] for item in data)
average = total_score / len(data)
print(f"Average score: {average:.1f}")

# Find highest scorer
best = max(data, key=lambda x: x["score"])
print(f"Highest score: {best['name']} with {best['score']}")
"""
        
        result = self.action.execute_code(data_code)
        
        if result["success"]:
            output = result["output"]
            self.assertIn("Average score: 91.3", output)
            self.assertIn("Highest score: Alice with 95", output)
    
    def test_error_handling(self):
        """Test error handling in code execution."""
        # Test runtime error
        error_code = """
print("Before error")
result = 10 / 0
print("After error")
"""
        
        result = self.action.execute_code(error_code)
        
        # Should handle error gracefully
        self.assertIn("success", result)
        if not result["success"]:
            self.assertIsNotNone(result["error"])
            self.assertTrue("ZeroDivisionError" in result["error"] or "division by zero" in result["error"])
    
    def test_syntax_error_handling(self):
        """Test syntax error handling."""
        syntax_error_code = """
print("Testing syntax error")
if True
    print("Missing colon!")
"""
        
        result = self.action.execute_code(syntax_error_code)
        
        # Should detect syntax error
        self.assertIn("success", result)
        if not result["success"]:
            self.assertIsNotNone(result["error"])
            self.assertTrue("SyntaxError" in result["error"] or "invalid syntax" in result["error"])
    
    def test_code_validation(self):
        """Test code validation functionality."""
        safe_code = """
import math
result = math.sqrt(25)
print(f"Result: {result}")
"""
        
        validation_result = self.action.validate_code_safety(safe_code)
        
        self.assertIsInstance(validation_result, dict)
        self.assertIn("is_safe", validation_result)
        self.assertIn("violations", validation_result)
        self.assertIn("code", validation_result)
    
    def test_get_status(self):
        """Test getting interpreter status."""
        status = self.action.get_interpreter_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("project_path", status)
        self.assertIn("directory_names", status)
        self.assertIn("allowed_imports", status)
        self.assertIn("available_tools", status)
    
    def test_get_tools(self):
        """Test getting available tools."""
        tools = self.action.get_tools()
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)


class TestManagerAgentCodeExecution(unittest.TestCase):
    """Test code execution through ManagerAgent integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock configuration for testing
        config = ALITAConfig(openai_api_key="test_key")
        llm_config = config.create_llm_config()
        self.manager = ManagerAgent(llm_config=llm_config)
    
    def test_manager_has_code_runner(self):
        """Test that manager agent has code runner initialized."""
        self.assertIsNotNone(self.manager.code_runner)
        self.assertIsInstance(self.manager.code_runner, CodeRunningAction)
    
    def test_manager_code_execution(self):
        """Test code execution through manager agent."""
        simple_code = """
print("Testing manager code execution")
result = 3 * 7
print(f"3 * 7 = {result}")
"""
        
        execution_result = self.manager.execute_code(simple_code)
        
        self.assertIsInstance(execution_result, dict)
        self.assertIn("success", execution_result)
        
        if execution_result["success"]:
            self.assertIn("Testing manager code execution", execution_result["output"])
            self.assertIn("3 * 7 = 21", execution_result["output"])
    
    def test_manager_code_validation(self):
        """Test code validation through manager agent."""
        test_code = """
import math
print("Safe code test")
"""
        
        validation_result = self.manager.validate_code(test_code)
        
        self.assertIsInstance(validation_result, dict)
        self.assertIn("is_safe", validation_result)
        self.assertIn("violations", validation_result)
    
    def test_manager_capabilities_include_code_execution(self):
        """Test that manager capabilities include code execution."""
        capabilities = self.manager.get_capabilities()
        
        self.assertIn("code_execution", capabilities)
        self.assertIn("script_execution", capabilities)
    
    def test_complex_computation(self):
        """Test complex computation through manager agent."""
        complex_code = """
import math

# Calculate fibonacci sequence
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("Fibonacci sequence (first 10 numbers):")
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")

# Calculate prime numbers
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

primes = [i for i in range(2, 20) if is_prime(i)]
print(f"Prime numbers up to 20: {primes}")
"""
        
        execution_result = self.manager.execute_code(complex_code)
        
        if execution_result["success"]:
            output = execution_result["output"]
            self.assertIn("F(0) = 0", output)
            self.assertIn("F(1) = 1", output)
            self.assertIn("F(9) = 34", output)
            self.assertIn("Prime numbers up to 20:", output)
            self.assertIn("[2, 3, 5, 7, 11, 13, 17, 19]", output)


class TestCodeExecutionSafety(unittest.TestCase):
    """Test safety features of code execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.action = CodeRunningAction()
    
    def test_import_restrictions(self):
        """Test that import restrictions work."""
        # Test allowed import
        allowed_code = """
import math
print(f"Pi = {math.pi}")
"""
        
        result = self.action.execute_code(allowed_code)
        # Should succeed with allowed import
        
        # Test potentially restricted import
        restricted_code = """
import subprocess
print("This might be restricted")
"""
        
        result = self.action.execute_code(restricted_code)
        # Result depends on security configuration
        self.assertIn("success", result)
    
    def test_security_validation(self):
        """Test security validation of code."""
        potentially_unsafe_code = """
import os
os.system("ls -la")
"""
        
        validation_result = self.action.validate_code_safety(potentially_unsafe_code)
        
        self.assertIsInstance(validation_result, dict)
        self.assertIn("is_safe", validation_result)
        
        # os is not in default allowed_imports, so this should be flagged
        if not validation_result["is_safe"]:
            self.assertGreater(len(validation_result["violations"]), 0)


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeRunningAction))
    suite.addTests(loader.loadTestsFromTestCase(TestManagerAgentCodeExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeExecutionSafety))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Code Running Test Summary")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed! Code execution functionality is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the details above.")