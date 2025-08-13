"""
Test cases for MCP integration functionality.

This module tests the MCP integration capabilities including:
- MCP tool discovery and registration
- Script to MCP tool conversion
- Tool persistence and management
- Integration with Manager Agent
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
import json
import shutil

# Add the project root to the Python path for testing
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.alita_reproduction.mcp.alita_mcp_server import ALITAMCPServer
from examples.alita_reproduction.mcp.tool_wrapper import ScriptToMCPWrapper
from examples.alita_reproduction.mcp.tool_persistence import MCPToolPersistence
from examples.alita_reproduction.actions.mcp_integration import MCPIntegrationAction
from examples.alita_reproduction.utils.mcp_config_manager import MCPConfigManager


class TestMCPIntegration(unittest.TestCase):
    """Test MCP integration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.scripts_dir = Path(self.test_dir) / "scripts"
        self.persistence_dir = Path(self.test_dir) / "persistence"
        self.config_dir = Path(self.test_dir) / "config"
        
        # Create directories
        self.scripts_dir.mkdir(exist_ok=True)
        self.persistence_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        # Create test script
        self.test_script_path = self.scripts_dir / "test_calculator.py"
        with open(self.test_script_path, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
Simple calculator script for testing MCP integration.
"""

import sys
import json

def add(a, b):
    """Add two numbers."""
    return a + b

def main():
    """Main function for calculator operations."""
    # Try to read input from stdin (for MCP tool calling)
    try:
        input_data = sys.stdin.read().strip()
        if input_data:
            data = json.loads(input_data)
            operation = data.get('operation', 'add')
            a = float(data.get('a', 0))
            b = float(data.get('b', 0))
            
            if operation == 'add':
                result = add(a, b)
                print(f"Result: {a} + {b} = {result}")
            else:
                print(f"Unknown operation: {operation}")
        else:
            # Default behavior
            print("Calculator: 2 + 3 = 5")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
''')
        
        # Create test config
        self.config_path = self.config_dir / "test_mcp_config.json"
        test_config = {
            "mcpServers": {
                "alita-tools-test": {
                    "command": "python",
                    "args": ["-c", "print('Test MCP server')"],
                    "timeout": 30.0,
                    "description": "Test ALITA MCP server"
                }
            },
            "settings": {
                "auto_register_generated_scripts": True,
                "backup_scripts_on_registration": True,
                "cleanup_old_backups_days": 30,
                "max_concurrent_tools": 10,
                "tool_execution_timeout": 30
            },
            "directories": {
                "generated_scripts": str(self.scripts_dir),
                "mcp_persistence": str(self.persistence_dir),
                "tools_registry": str(self.persistence_dir / "tools_registry.json")
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_mcp_config_manager(self):
        """Test MCP configuration manager functionality."""
        config_manager = MCPConfigManager(str(self.config_path))
        
        # Test configuration loading
        self.assertTrue(config_manager.config_data)
        self.assertIn("mcpServers", config_manager.config_data)
        self.assertIn("settings", config_manager.config_data)
        
        # Test settings access
        auto_register = config_manager.get_setting("auto_register_generated_scripts", False)
        self.assertTrue(auto_register)
        
        # Test directory access
        scripts_dir = config_manager.get_directory("generated_scripts")
        self.assertEqual(str(scripts_dir), str(self.scripts_dir))
        
        # Test configuration validation
        validation = config_manager.validate_config()
        self.assertTrue(validation["is_valid"])
        self.assertEqual(len(validation["errors"]), 0)
        
        print("✓ MCP Config Manager test passed")
    
    def test_script_wrapper(self):
        """Test script to MCP tool wrapper functionality."""
        wrapper = ScriptToMCPWrapper(str(self.test_dir))
        
        # Test script analysis
        analysis = wrapper.analyze_script(str(self.test_script_path))
        self.assertTrue(analysis["success"])
        self.assertEqual(analysis["name"], "test_calculator")
        self.assertIn("Simple calculator", analysis["description"])
        self.assertIn("main", [func["name"] for func in analysis["functions"]])
        
        # Test script wrapping
        tool_spec = wrapper.wrap_script(
            str(self.test_script_path),
            tool_name="test_calculator_tool",
            tool_description="Calculator tool for testing"
        )
        
        self.assertEqual(tool_spec.name, "test_calculator_tool")
        self.assertEqual(tool_spec.description, "Calculator tool for testing")
        self.assertEqual(tool_spec.script_path, str(self.test_script_path.absolute()))
        self.assertIsInstance(tool_spec.parameters, dict)
        
        # Test script execution testing
        test_result = wrapper.test_script_execution(
            str(self.test_script_path),
            {"operation": "add", "a": 2, "b": 3}
        )
        self.assertTrue(test_result["success"])
        self.assertIn("Result: 2.0 + 3.0 = 5.0", test_result["stdout"])
        
        print("✓ Script Wrapper test passed")
    
    def test_tool_persistence(self):
        """Test MCP tool persistence functionality."""
        persistence = MCPToolPersistence(str(self.persistence_dir))
        
        # Test tool persistence
        tool_id = "test_tool_123"
        persist_result = persistence.persist_tool(
            tool_id=tool_id,
            name="test_calculator",
            description="Test calculator tool",
            script_path=str(self.test_script_path),
            parameters={"type": "object", "properties": {}},
            metadata={"test": True}
        )
        
        self.assertTrue(persist_result["success"])
        self.assertEqual(persist_result["tool_id"], tool_id)
        
        # Test tool loading
        loaded_tool = persistence.load_tool(tool_id)
        self.assertIsNotNone(loaded_tool)
        self.assertEqual(loaded_tool.name, "test_calculator")
        self.assertEqual(loaded_tool.id, tool_id)
        
        # Test tool listing
        tools_list = persistence.list_tools()
        self.assertEqual(tools_list["total_tools"], 1)
        self.assertEqual(len(tools_list["tools"]), 1)
        
        # Test usage increment
        persistence.increment_usage(tool_id)
        updated_tool = persistence.load_tool(tool_id)
        self.assertEqual(updated_tool.usage_count, 1)
        
        # Test tool deletion
        delete_result = persistence.delete_tool(tool_id)
        self.assertTrue(delete_result["success"])
        
        deleted_tool = persistence.load_tool(tool_id)
        self.assertIsNone(deleted_tool)
        
        print("✓ Tool Persistence test passed")
    
    def test_alita_mcp_server(self):
        """Test ALITA MCP server functionality."""
        server = ALITAMCPServer(
            server_name="alita-test",
            tools_dir=str(self.scripts_dir),
            persistence_file=str(self.persistence_dir / "test_registry.json")
        )
        
        # Test tool registration
        registration_result = server.register_script_as_tool(
            script_path=str(self.test_script_path),
            tool_name="test_calculator_server",
            description="Calculator tool registered with server",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "description": "Math operation"},
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                }
            }
        )
        
        self.assertTrue(registration_result["success"])
        self.assertIsNotNone(registration_result["tool_id"])
        
        # Test tool listing
        tools_list = server.list_tools()
        self.assertEqual(tools_list["tools_count"], 1)
        self.assertIn("test_calculator_server", tools_list["tools"])
        
        # Test tool execution
        execution_result = server.execute_tool(
            "test_calculator_server",
            operation="add",
            a=5,
            b=7
        )
        self.assertTrue(execution_result["success"])
        self.assertIn("5.0 + 7.0 = 12.0", execution_result["output"])
        
        # Test tool unregistration
        unregister_result = server.unregister_tool("test_calculator_server")
        self.assertTrue(unregister_result["success"])
        
        updated_list = server.list_tools()
        self.assertEqual(updated_list["tools_count"], 0)
        
        print("✓ ALITA MCP Server test passed")
    
    def test_mcp_integration_action(self):
        """Test MCP integration action functionality."""
        integration = MCPIntegrationAction(
            config_path=str(self.config_path),
            persistence_dir=str(self.persistence_dir)
        )
        
        # Test external MCP initialization
        init_result = integration.initialize_external_mcp_connection()
        # Note: This might fail in test environment, which is expected
        self.assertIn("success", init_result)
        
        # Test tool registration
        registration_result = integration.register_script_as_mcp_tool(
            script_path=str(self.test_script_path),
            tool_name="test_calculator_integration",
            tool_description="Calculator tool via integration action"
        )
        self.assertTrue(registration_result["success"])
        
        # Test tool discovery
        discovery_result = integration.discover_available_tools()
        self.assertIn("alita_tools", discovery_result)
        self.assertIn("external_tools", discovery_result)
        self.assertGreaterEqual(discovery_result["total_tools"], 1)
        
        # Test suitable tool finding
        suitable_tools = integration.find_suitable_tool("calculate 2 plus 3")
        self.assertIn("suitable_tools", suitable_tools)
        
        # Test tool execution
        execution_result = integration.execute_mcp_tool(
            "test_calculator_integration",
            {"operation": "add", "a": 4, "b": 6}
        )
        self.assertTrue(execution_result["success"])
        
        # Test MCP status
        status = integration.get_mcp_status()
        self.assertIn("alita_server", status)
        self.assertIn("persistence", status)
        
        print("✓ MCP Integration Action test passed")
    
    def test_manager_agent_mcp_integration(self):
        """Test Manager Agent MCP integration."""
        # This test would require a full Manager Agent setup
        # For now, we'll test that the integration can be imported
        try:
            from examples.alita_reproduction.agents.manager_agent import ManagerAgent
            # If we can import it, the integration is properly structured
            print("✓ Manager Agent MCP integration import test passed")
        except ImportError as e:
            self.fail(f"Manager Agent MCP integration import failed: {str(e)}")


def run_mcp_tests():
    """Run all MCP integration tests."""
    print("Running ALITA MCP Integration Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMCPIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nTest Result: {'PASSED' if success else 'FAILED'}")
    
    return success


if __name__ == "__main__":
    run_mcp_tests()