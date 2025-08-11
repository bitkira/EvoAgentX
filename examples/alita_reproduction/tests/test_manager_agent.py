"""
Test cases for Manager Agent.

Tests the basic functionality of the ALITA Manager Agent
at the current development stage.
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch

# Add the EvoAgentX root to path
sys.path.append('/Users/bitkira/Documents/GitHub/EvoAgentX')

from evoagentx.models import OpenAILLMConfig
from examples.alita_reproduction.agents import ManagerAgent
from examples.alita_reproduction.config import ALITAConfig


class TestManagerAgent(unittest.TestCase):
    """Test cases for Manager Agent functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the API key for testing
        self.mock_api_key = "test_api_key"
        
        # Create test configuration
        self.config = ALITAConfig(openai_api_key=self.mock_api_key)
        self.llm_config = self.config.create_llm_config()
    
    def test_manager_agent_initialization(self):
        """Test that Manager Agent initializes correctly."""
        manager = ManagerAgent(llm_config=self.llm_config)
        
        self.assertEqual(manager.name, "ALITAManager")
        self.assertIsNotNone(manager.description)
        self.assertEqual(manager.iteration_count, 0)
        self.assertEqual(len(manager.task_history), 0)
    
    def test_get_capabilities(self):
        """Test that capabilities are properly defined."""
        manager = ManagerAgent(llm_config=self.llm_config)
        capabilities = manager.get_capabilities()
        
        self.assertIsInstance(capabilities, dict)
        self.assertIn("task_analysis", capabilities)
        self.assertIn("basic_reasoning", capabilities)
        self.assertIn("response_generation", capabilities)
        self.assertIn("task_history", capabilities)
        self.assertIn("capability_assessment", capabilities)
    
    def test_assess_tool_needs(self):
        """Test tool needs assessment functionality."""
        manager = ManagerAgent(llm_config=self.llm_config)
        
        # Test task that needs web search
        assessment = manager.assess_tool_needs("Search for latest AI research")
        self.assertTrue(assessment["needs_additional_tools"])
        self.assertIn("web_search", assessment["suggested_tools"])
        
        # Test task that needs code execution
        assessment = manager.assess_tool_needs("Calculate the sum of 1 to 100")
        self.assertTrue(assessment["needs_additional_tools"])
        self.assertIn("code_execution", assessment["suggested_tools"])
        
        # Test task that needs file operations
        assessment = manager.assess_tool_needs("Read the contents of a file")
        self.assertTrue(assessment["needs_additional_tools"])
        self.assertIn("file_operations", assessment["suggested_tools"])
        
        # Test simple task that doesn't need additional tools
        assessment = manager.assess_tool_needs("What is the capital of France?")
        # This might be False depending on heuristics
        self.assertIsInstance(assessment["needs_additional_tools"], bool)
    
    def test_task_history_management(self):
        """Test task history tracking."""
        manager = ManagerAgent(llm_config=self.llm_config)
        
        # Initially empty
        self.assertEqual(len(manager.get_task_history()), 0)
        
        # Add some mock tasks (without actually calling LLM)
        manager.task_history.append({
            "iteration": 1,
            "task": "Test task",
            "response": "Test response",
            "context": {}
        })
        
        history = manager.get_task_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["task"], "Test task")
        
        # Clear history
        manager.clear_history()
        self.assertEqual(len(manager.get_task_history()), 0)
        self.assertEqual(manager.iteration_count, 0)
    
    def test_process_task_mock(self):
        """Test task processing with mocked LLM response."""
        manager = ManagerAgent(llm_config=self.llm_config)
        
        # Mock the parent's __call__ method
        with patch.object(manager, '__call__') as mock_call:
            # Mock the LLM response
            mock_response = Mock()
            mock_response.content.content = "This is a test response"
            mock_call.return_value = mock_response
            
            task = "Test task"
            response = manager.process_task(task)
            
            self.assertEqual(response, "This is a test response")
            self.assertEqual(manager.iteration_count, 1)
            self.assertEqual(len(manager.task_history), 1)
            self.assertEqual(manager.current_task, task)


class TestALITAConfig(unittest.TestCase):
    """Test cases for ALITA configuration."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        config = ALITAConfig(openai_api_key="test_key")
        
        self.assertEqual(config.model_name, "gpt-4o-mini")
        self.assertEqual(config.openai_api_key, "test_key")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_iterations, 10)
    
    def test_create_llm_config(self):
        """Test LLM configuration creation."""
        config = ALITAConfig(openai_api_key="test_key")
        llm_config = config.create_llm_config()
        
        self.assertIsInstance(llm_config, OpenAILLMConfig)
        self.assertEqual(llm_config.model, "gpt-4o-mini")
        self.assertEqual(llm_config.openai_key, "test_key")
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Should raise error if no API key provided and none in environment
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                ALITAConfig()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)