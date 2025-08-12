"""
Code Execution Demo for ALITA reproduction.

This script demonstrates the code execution capabilities of the ALITA Manager Agent
using the integrated CodeRunningAction and PythonInterpreterToolkit.
"""

import sys
import os
import logging

# Add the parent directory to sys.path to import from alita_reproduction
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.manager_agent import ManagerAgent
from evoagentx.models import OpenAILLMConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_basic_code_execution():
    """Demonstrate basic code execution capabilities."""
    print("\n" + "="*60)
    print("ALITA Code Execution Demo - Basic Operations")
    print("="*60)
    
    # Initialize Manager Agent
    logger.info("Initializing ALITA Manager Agent...")
    
    # You can configure with actual API key for full LLM functionality
    # For demo, we'll focus on the code execution capabilities
    llm_config = OpenAILLMConfig(
        model="gpt-3.5-turbo",
        api_key="demo-key",  # Replace with actual key for full functionality
        temperature=0.7
    )
    
    manager = ManagerAgent(llm_config=llm_config)
    
    # Display capabilities
    print("\nManager Agent Capabilities:")
    capabilities = manager.get_capabilities()
    for name, desc in capabilities.items():
        print(f"  • {name}: {desc}")
    
    # Display code runner status
    print("\nCode Runner Status:")
    status = manager.get_code_runner_status()
    for key, value in status.items():
        if key == "allowed_imports":
            print(f"  • {key}: {len(value)} allowed imports")
        else:
            print(f"  • {key}: {value}")
    
    return manager


def demo_code_validation():
    """Demonstrate code validation functionality."""
    print("\n" + "="*60)
    print("Code Validation Demo")
    print("="*60)
    
    manager = demo_basic_code_execution()
    
    # Test safe code
    safe_code = """
import math
print("Testing safe code execution")
result = math.sqrt(16)
print(f"Square root of 16 is: {result}")
"""
    
    print("\n1. Validating safe code:")
    validation_result = manager.validate_code(safe_code)
    print(f"   Is safe: {validation_result['is_safe']}")
    if validation_result['violations']:
        print(f"   Violations: {validation_result['violations']}")
    
    # Test potentially unsafe code
    unsafe_code = """
import subprocess
subprocess.run(['ls', '-la'])
"""
    
    print("\n2. Validating potentially unsafe code:")
    validation_result = manager.validate_code(unsafe_code)
    print(f"   Is safe: {validation_result['is_safe']}")
    if validation_result['violations']:
        print(f"   Violations: {validation_result['violations']}")
    
    return manager


def demo_simple_calculations():
    """Demonstrate simple mathematical calculations."""
    print("\n" + "="*60)
    print("Simple Calculations Demo")
    print("="*60)
    
    manager = demo_basic_code_execution()
    
    # Simple math operations
    math_code = """
import math

print("=== Mathematical Calculations ===")

# Basic arithmetic
a, b = 15, 4
print(f"Addition: {a} + {b} = {a + b}")
print(f"Multiplication: {a} * {b} = {a * b}")
print(f"Division: {a} / {b} = {a / b:.2f}")

# Using math library
print(f"\\nSquare root of {a}: {math.sqrt(a):.2f}")
print(f"Sine of π/2: {math.sin(math.pi/2):.2f}")
print(f"Factorial of 5: {math.factorial(5)}")

# List operations
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f"\\nSum of {numbers}: {sum(numbers)}")
print(f"Average: {sum(numbers)/len(numbers):.2f}")
"""
    
    print("\nExecuting mathematical calculations...")
    result = manager.execute_code(math_code)
    
    if result['success']:
        print("✅ Execution successful!")
        print("Output:")
        print(result['output'])
    else:
        print("❌ Execution failed!")
        print("Error:", result['error'])
    
    return result


def demo_data_processing():
    """Demonstrate data processing capabilities."""
    print("\n" + "="*60)
    print("Data Processing Demo")
    print("="*60)
    
    manager = demo_basic_code_execution()
    
    # Data processing example
    data_code = """
import json
from collections import Counter

print("=== Data Processing Example ===")

# Sample data
data = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "San Francisco"},
    {"name": "Charlie", "age": 35, "city": "New York"},
    {"name": "Diana", "age": 28, "city": "Chicago"},
    {"name": "Eve", "age": 32, "city": "San Francisco"}
]

print("Original data:")
for person in data:
    print(f"  {person}")

# Count cities
cities = [person['city'] for person in data]
city_counts = Counter(cities)
print(f"\\nCity distribution: {dict(city_counts)}")

# Calculate average age
average_age = sum(person['age'] for person in data) / len(data)
print(f"Average age: {average_age:.1f}")

# Filter by age
adults_over_30 = [person for person in data if person['age'] > 30]
print(f"\\nPeople over 30:")
for person in adults_over_30:
    print(f"  {person['name']}: {person['age']}")
"""
    
    print("\nExecuting data processing code...")
    result = manager.execute_code(data_code)
    
    if result['success']:
        print("✅ Execution successful!")
        print("Output:")
        print(result['output'])
    else:
        print("❌ Execution failed!")
        print("Error:", result['error'])
    
    return result


def demo_error_handling():
    """Demonstrate error handling in code execution."""
    print("\n" + "="*60)
    print("Error Handling Demo")
    print("="*60)
    
    manager = demo_basic_code_execution()
    
    # Code with intentional error
    error_code = """
print("Starting execution...")

# This will cause a division by zero error
result = 10 / 0
print(f"Result: {result}")
"""
    
    print("\nExecuting code with intentional error...")
    result = manager.execute_code(error_code)
    
    if result['success']:
        print("✅ Unexpected success!")
        print("Output:", result['output'])
    else:
        print("❌ Expected error caught!")
        print("Error details:")
        print(result['error'])
    
    # Code with syntax error
    syntax_error_code = """
print("Testing syntax error")
if True
    print("Missing colon!")
"""
    
    print("\nExecuting code with syntax error...")
    result = manager.execute_code(syntax_error_code)
    
    if result['success']:
        print("✅ Unexpected success!")
        print("Output:", result['output'])
    else:
        print("❌ Syntax error caught!")
        print("Error details:")
        print(result['error'][:200] + "..." if len(result['error']) > 200 else result['error'])
    
    return result


def main():
    """Run all demo functions."""
    print("🚀 Starting ALITA Code Execution Demo")
    print("This demo showcases the code execution capabilities of the ALITA Manager Agent.")
    
    try:
        # Run demos
        demo_code_validation()
        demo_simple_calculations()
        demo_data_processing()
        demo_error_handling()
        
        print("\n" + "="*60)
        print("✅ All demos completed successfully!")
        print("The ALITA Manager Agent is now equipped with code execution capabilities.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        logger.error(f"Demo failed: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()