"""
Basic example demonstrating ALITA Manager Agent usage.

This example shows the current capabilities of the ALITA system
at the initial development stage (Commit 1).
"""

import os
import sys
sys.path.append('/Users/bitkira/Documents/GitHub/EvoAgentX')

from evoagentx.models import OpenAILLMConfig
from examples.alita_reproduction.agents import ManagerAgent
from examples.alita_reproduction.config import ALITAConfig


def main():
    """Demonstrate basic ALITA Manager Agent functionality."""
    
    print("=== ALITA Reproduction - Basic Example ===")
    print("Current stage: Commit 1 - Basic Manager Agent")
    print()
    
    try:
        # Initialize configuration
        config = ALITAConfig()
        llm_config = config.create_llm_config()
        
        # Create Manager Agent
        print("Initializing ALITA Manager Agent...")
        manager = ManagerAgent(llm_config=llm_config)
        
        # Display current capabilities
        print(f"Manager Agent initialized: {manager.name}")
        print("Current capabilities:")
        for capability, description in manager.get_capabilities().items():
            print(f"  - {capability}: {description}")
        print()
        
        # Test with various tasks
        test_tasks = [
            "Hello, can you introduce yourself?",
            "Create a simple calculator in Python",
            "Search for the latest AI research papers",
            "Write a function to sort a list of numbers",
            "What's the weather like today?",
        ]
        
        for i, task in enumerate(test_tasks, 1):
            print(f"--- Test {i} ---")
            print(f"Task: {task}")
            
            # Process the task
            response = manager.process_task(task)
            print(f"Response: {response}")
            
            # Show tool assessment
            assessment = manager.assess_tool_needs(task)
            print(f"Tool Assessment:")
            print(f"  - Needs additional tools: {assessment['needs_additional_tools']}")
            if assessment['suggested_tools']:
                print(f"  - Suggested tools: {', '.join(assessment['suggested_tools'])}")
            print(f"  - Confidence: {assessment['confidence']}")
            print()
        
        # Show task history
        print("--- Task History ---")
        history = manager.get_task_history()
        print(f"Total tasks processed: {len(history)}")
        for record in history:
            print(f"  Task {record['iteration']}: {record['task'][:50]}...")
        
    except Exception as e:
        print(f"Error running example: {e}")
        print("Make sure you have set your OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    main()