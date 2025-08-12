"""
Simple Hello World script for testing script execution capabilities.
"""

print("Hello, World from ALITA script execution!")

# Basic calculations
a = 10
b = 5

print(f"Addition: {a} + {b} = {a + b}")
print(f"Multiplication: {a} * {b} = {a * b}")

# Using math operations
import math

numbers = [1, 4, 9, 16, 25]
print(f"Original numbers: {numbers}")

sqrt_numbers = [math.sqrt(x) for x in numbers]
print(f"Square roots: {sqrt_numbers}")

print("Script execution completed successfully!")