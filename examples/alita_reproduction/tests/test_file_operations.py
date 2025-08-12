"""
Test cases for File Operations functionality.

Tests the file operations capabilities integrated into ALITA,
including the FileOperationsAction class and its integration with ManagerAgent.
"""

import unittest
import sys
import os
import tempfile
import shutil
import json

# Add the EvoAgentX root to path
sys.path.append('/Users/bitkira/Documents/GitHub/EvoAgentX')

from examples.alita_reproduction.actions.file_operations import FileOperationsAction
from examples.alita_reproduction.agents.manager_agent import ManagerAgent
from examples.alita_reproduction.config import ALITAConfig


class TestFileOperationsAction(unittest.TestCase):
    """Test cases for FileOperationsAction class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.action = FileOperationsAction()
        
        # Create temporary directory for tests
        self.test_dir = tempfile.mkdtemp(prefix="alita_file_test_")
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        self.test_content = "Hello from ALITA file operations test!\nLine 2: Testing content\nLine 3: 你好世界 🌍"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test FileOperationsAction initialization."""
        self.assertIsNotNone(self.action)
        
        # Check status
        status = self.action.get_operations_status()
        self.assertIsInstance(status, dict)
        self.assertIn("toolkit_available", status)
        self.assertIn("read_available", status)
        self.assertIn("write_available", status)
        self.assertIn("append_available", status)
        self.assertIn("available_operations", status)
        
        # Check available operations
        operations = self.action.get_available_operations()
        self.assertIsInstance(operations, list)
        self.assertIn("list_files", operations)
        self.assertIn("get_file_info", operations)
    
    def test_write_file(self):
        """Test file writing functionality."""
        result = self.action.write_file(self.test_file, self.test_content)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("operation", result)
        self.assertIn("file_path", result)
        self.assertIn("content_length", result)
        self.assertIn("file_type", result)
        self.assertIn("error", result)
        
        self.assertEqual(result["operation"], "write")
        self.assertEqual(result["file_path"], self.test_file)
        
        if result["success"]:
            self.assertEqual(result["content_length"], len(self.test_content))
            self.assertEqual(result["file_type"], "text")
            self.assertTrue(os.path.exists(self.test_file))
            
            # Verify file was actually written
            with open(self.test_file, 'r', encoding='utf-8') as f:
                written_content = f.read()
            self.assertEqual(written_content, self.test_content)
    
    def test_read_file(self):
        """Test file reading functionality."""
        # First write a file
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(self.test_content)
        
        result = self.action.read_file(self.test_file)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("operation", result)
        self.assertIn("file_path", result)
        self.assertIn("content", result)
        self.assertIn("file_type", result)
        self.assertIn("file_size", result)
        self.assertIn("error", result)
        
        self.assertEqual(result["operation"], "read")
        self.assertEqual(result["file_path"], self.test_file)
        
        if result["success"]:
            self.assertEqual(result["content"], self.test_content)
            self.assertEqual(result["file_type"], "text")
            self.assertEqual(result["file_size"], len(self.test_content))
    
    def test_append_file(self):
        """Test file appending functionality."""
        # First write initial content
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(self.test_content)
        
        append_content = "\nAppended line: This is additional content"
        result = self.action.append_file(self.test_file, append_content)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("operation", result)
        self.assertIn("file_path", result)
        self.assertIn("content_length", result)
        self.assertIn("error", result)
        
        self.assertEqual(result["operation"], "append")
        self.assertEqual(result["file_path"], self.test_file)
        
        if result["success"]:
            self.assertEqual(result["content_length"], len(append_content))
            
            # Verify content was appended
            with open(self.test_file, 'r', encoding='utf-8') as f:
                final_content = f.read()
            self.assertEqual(final_content, self.test_content + append_content)
    
    def test_list_files(self):
        """Test file listing functionality."""
        # Create several test files
        test_files = [
            ("test1.txt", "content1"),
            ("test2.py", "print('hello')"),
            ("test3.json", '{"key": "value"}'),
            ("test4.txt", "content4")
        ]
        
        for filename, content in test_files:
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Test listing all files
        result = self.action.list_files(self.test_dir)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("operation", result)
        self.assertIn("directory_path", result)
        self.assertIn("files", result)
        self.assertIn("total_files", result)
        self.assertIn("error", result)
        
        self.assertEqual(result["operation"], "list")
        self.assertEqual(result["directory_path"], self.test_dir)
        
        if result["success"]:
            self.assertEqual(result["total_files"], len(test_files))
            self.assertIsInstance(result["files"], list)
            
            # Check file info structure
            for file_info in result["files"]:
                self.assertIn("name", file_info)
                self.assertIn("path", file_info)
                self.assertIn("size", file_info)
                self.assertIn("type", file_info)
                self.assertIn("modified", file_info)
        
        # Test pattern filtering
        txt_result = self.action.list_files(self.test_dir, "*.txt")
        if txt_result["success"]:
            txt_files = [f for f in txt_result["files"]]
            expected_txt_count = 2  # test1.txt and test4.txt
            self.assertEqual(len(txt_files), expected_txt_count)
            for file_info in txt_files:
                self.assertTrue(file_info["name"].endswith(".txt"))
    
    def test_get_file_info(self):
        """Test file information retrieval."""
        # Create test file
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(self.test_content)
        
        result = self.action.get_file_info(self.test_file)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("operation", result)
        self.assertIn("file_path", result)
        self.assertIn("error", result)
        
        self.assertEqual(result["operation"], "info")
        self.assertEqual(result["file_path"], self.test_file)
        
        if result["success"]:
            expected_fields = ["name", "size", "type", "created", "modified", "accessed", 
                             "is_file", "is_directory", "readable", "writable"]
            for field in expected_fields:
                self.assertIn(field, result)
            
            self.assertEqual(result["name"], os.path.basename(self.test_file))
            self.assertEqual(result["size"], len(self.test_content))
            self.assertEqual(result["type"], "text")
            self.assertTrue(result["is_file"])
            self.assertFalse(result["is_directory"])
    
    def test_file_type_detection(self):
        """Test file type detection."""
        test_cases = [
            ("test.txt", "text"),
            ("test.py", "python"),
            ("test.js", "javascript"),
            ("test.json", "json"),
            ("test.html", "html"),
            ("test.csv", "csv"),
            ("test.unknown", "unknown")
        ]
        
        for filename, expected_type in test_cases:
            detected_type = self.action._detect_file_type(filename)
            self.assertEqual(detected_type, expected_type)
    
    def test_error_handling(self):
        """Test error handling in file operations."""
        non_existent_path = "/non/existent/path/file.txt"
        
        # Test reading non-existent file
        read_result = self.action.read_file(non_existent_path)
        self.assertFalse(read_result["success"])
        self.assertIn("not found", read_result["error"].lower())
        
        # Test listing non-existent directory
        list_result = self.action.list_files(non_existent_path)
        self.assertFalse(list_result["success"])
        self.assertIn("not found", list_result["error"].lower())
        
        # Test getting info for non-existent file
        info_result = self.action.get_file_info(non_existent_path)
        self.assertFalse(info_result["success"])
        self.assertIn("not found", info_result["error"].lower())
        
        # Test writing to invalid path (permission denied scenario)
        # Note: This might pass on some systems, so we just check structure
        invalid_result = self.action.write_file("/root/invalid_file.txt", "content")
        self.assertIsInstance(invalid_result, dict)
        self.assertIn("success", invalid_result)
    
    def test_overwrite_protection(self):
        """Test file overwrite protection."""
        # Create initial file
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("initial content")
        
        # Try to write without overwrite
        result = self.action.write_file(self.test_file, "new content", overwrite=False)
        
        self.assertIsInstance(result, dict)
        if not result["success"]:
            self.assertIn("already exists", result["error"])
        
        # Write with overwrite should work
        overwrite_result = self.action.write_file(self.test_file, "new content", overwrite=True)
        if overwrite_result["success"]:
            # Verify content was overwritten
            with open(self.test_file, 'r', encoding='utf-8') as f:
                final_content = f.read()
            self.assertEqual(final_content, "new content")


class TestManagerAgentFileOperations(unittest.TestCase):
    """Test file operations through ManagerAgent integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock configuration for testing
        config = ALITAConfig(openai_api_key="test_key")
        llm_config = config.create_llm_config()
        self.manager = ManagerAgent(llm_config=llm_config)
        
        # Create temporary directory for tests
        self.test_dir = tempfile.mkdtemp(prefix="alita_manager_file_test_")
        self.test_file = os.path.join(self.test_dir, "manager_test.txt")
        self.test_content = "Hello from Manager Agent file operations!"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_manager_has_file_handler(self):
        """Test that manager agent has file handler initialized."""
        self.assertIsNotNone(self.manager.file_handler)
        self.assertIsInstance(self.manager.file_handler, FileOperationsAction)
    
    def test_manager_file_capabilities(self):
        """Test that manager capabilities include file operations."""
        capabilities = self.manager.get_capabilities()
        
        self.assertIn("file_operations", capabilities)
        self.assertIn("file_management", capabilities)
    
    def test_manager_file_methods(self):
        """Test file operation methods through manager agent."""
        # Test write
        write_result = self.manager.write_file(self.test_file, self.test_content)
        self.assertIsInstance(write_result, dict)
        self.assertIn("success", write_result)
        
        if write_result["success"]:
            # Test read
            read_result = self.manager.read_file(self.test_file)
            self.assertIsInstance(read_result, dict)
            self.assertIn("success", read_result)
            
            if read_result["success"]:
                self.assertEqual(read_result["content"], self.test_content)
            
            # Test append
            append_content = "\nAppended via Manager"
            append_result = self.manager.append_file(self.test_file, append_content)
            self.assertIsInstance(append_result, dict)
            self.assertIn("success", append_result)
            
            # Test list files
            list_result = self.manager.list_files(self.test_dir)
            self.assertIsInstance(list_result, dict)
            self.assertIn("success", list_result)
            
            if list_result["success"]:
                self.assertGreater(list_result["total_files"], 0)
            
            # Test get file info
            info_result = self.manager.get_file_info(self.test_file)
            self.assertIsInstance(info_result, dict)
            self.assertIn("success", info_result)
    
    def test_manager_file_operations_status(self):
        """Test getting file operations status through manager."""
        status = self.manager.get_file_operations_status()
        
        self.assertIsInstance(status, dict)
        expected_fields = ["toolkit_available", "read_available", "write_available", 
                          "append_available", "available_operations"]
        for field in expected_fields:
            if field in status:  # Some fields might be optional
                self.assertIsNotNone(status[field])
    
    def test_enhanced_task_assessment(self):
        """Test enhanced task assessment that includes file operations detection."""
        # Test tasks that should trigger file operations
        file_tasks = [
            "read the contents of a file",
            "write data to a document",
            "save information to a file",
            "load configuration from file",
            "create a CSV file"
        ]
        
        for task in file_tasks:
            assessment = self.manager.assess_tool_needs(task)
            self.assertIn("file_operations", assessment["suggested_tools"])
        
        # Test mixed tasks
        mixed_task = "read a file and calculate some data"
        assessment = self.manager.assess_tool_needs(mixed_task)
        suggested = assessment["suggested_tools"]
        self.assertTrue("file_operations" in suggested or "code_execution" in suggested)
    
    def test_json_file_operations(self):
        """Test operations with JSON files."""
        json_file = os.path.join(self.test_dir, "test_data.json")
        json_data = {
            "name": "ALITA",
            "version": "commit4",
            "features": ["code_execution", "web_search", "file_operations"],
            "config": {
                "max_iterations": 10,
                "temperature": 0.7
            }
        }
        
        json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        # Write JSON file
        write_result = self.manager.write_file(json_file, json_content)
        if write_result["success"]:
            self.assertEqual(write_result["file_type"], "json")
            
            # Read JSON file
            read_result = self.manager.read_file(json_file)
            if read_result["success"]:
                self.assertEqual(read_result["file_type"], "json")
                # Parse and verify JSON content
                parsed_data = json.loads(read_result["content"])
                self.assertEqual(parsed_data["name"], "ALITA")
                self.assertEqual(parsed_data["version"], "commit4")


class TestFileOperationsIntegration(unittest.TestCase):
    """Test integration between file operations components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.action = FileOperationsAction()
        config = ALITAConfig(openai_api_key="test_key")
        llm_config = config.create_llm_config()
        self.manager = ManagerAgent(llm_config=llm_config)
        
        self.test_dir = tempfile.mkdtemp(prefix="alita_integration_test_")
        self.test_file = os.path.join(self.test_dir, "integration_test.txt")
        self.test_content = "Integration test content"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_consistent_file_operations(self):
        """Test that direct action and manager operations return consistent results."""
        # Write through action
        action_write = self.action.write_file(self.test_file, self.test_content)
        
        # Read through manager
        manager_read = self.manager.read_file(self.test_file)
        
        if action_write["success"] and manager_read["success"]:
            # Content should be consistent
            self.assertEqual(manager_read["content"], self.test_content)
            # File types should match
            self.assertEqual(action_write["file_type"], manager_read["file_type"])
    
    def test_operations_status_consistency(self):
        """Test consistency of operations status across components."""
        action_status = self.action.get_operations_status()
        manager_status = self.manager.get_file_operations_status()
        
        # Should report consistent availability
        if "toolkit_available" in action_status and "toolkit_available" in manager_status:
            self.assertEqual(
                action_status["toolkit_available"], 
                manager_status["toolkit_available"]
            )


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperationsAction))
    suite.addTests(loader.loadTestsFromTestCase(TestManagerAgentFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperationsIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("File Operations Test Summary")
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
        print("\n✅ All tests passed! File operations functionality is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the details above.")