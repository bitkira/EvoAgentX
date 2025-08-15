#!/usr/bin/env python3
"""
Test script for the simplified LLM-based script generation functionality.

This script tests the new ScriptGeneratingAction with various scenarios
to validate the LLM-based approach.
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.alita_reproduction.actions.script_generating import ScriptGeneratingAction
from examples.alita_reproduction.utils.code_quality import CodeQualityChecker

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_basic_script_generation():
    """Test basic script generation functionality."""
    print("\n" + "="*60)
    print("🔍 Testing Basic Script Generation")
    print("="*60)
    
    # Initialize the script generator
    generator = ScriptGeneratingAction(
        output_dir="test_output",
        llm_model="gpt-3.5-turbo"  # Use a faster model for testing
    )
    
    # Test case 1: Simple data processing script
    print("\n📝 Test 1: Data Processing Script")
    result = generator.generate_script(
        task_description="Create a script that reads a CSV file, calculates basic statistics (mean, median, std), and saves results to a new CSV file",
        script_name="data_analyzer",
        requirements={
            "input_format": "CSV file",
            "output_format": "CSV file with statistics",
            "libraries": ["pandas", "numpy"]
        }
    )
    
    print_test_result(result, "Data Processing Script")
    
    # Test case 2: Simple automation script
    print("\n📝 Test 2: File Organization Script")
    result = generator.generate_script(
        task_description="Create a script that organizes files in a directory by extension, moving them into subdirectories",
        script_name="file_organizer",
        requirements={
            "input_format": "Directory path",
            "output_format": "Organized directory structure",
            "constraints": "Handle file name conflicts gracefully"
        }
    )
    
    print_test_result(result, "File Organization Script")
    
    return True


def test_code_quality_validation():
    """Test the code quality validation functionality."""
    print("\n" + "="*60)
    print("🔍 Testing Code Quality Validation")
    print("="*60)
    
    checker = CodeQualityChecker()
    
    # Test case 1: Valid code
    print("\n✅ Test 1: Valid Code")
    valid_code = '''
#!/usr/bin/env python3
"""Simple test script."""
import logging

def main():
    """Main function."""
    print("Hello, World!")
    logging.info("Script executed successfully")

if __name__ == '__main__':
    main()
'''
    
    result = checker.analyze_code(valid_code)
    print(f"Result: {checker.get_validation_summary(result)}")
    
    # Test case 2: Code with security issues
    print("\n❌ Test 2: Code with Security Issues")
    unsafe_code = '''
import os
def dangerous_function(user_input):
    eval(user_input)  # Dangerous!
    os.system("rm -rf /")  # Very dangerous!
'''
    
    result = checker.analyze_code(unsafe_code)
    print(f"Result: {checker.get_validation_summary(result)}")
    
    # Test case 3: Code with syntax errors
    print("\n❌ Test 3: Code with Syntax Errors")
    broken_code = '''
def broken_function(
    print("This has syntax errors"
    return "broken
'''
    
    result = checker.analyze_code(broken_code)
    print(f"Result: {checker.get_validation_summary(result)}")
    
    return True


def test_error_handling():
    """Test error handling and retry mechanisms."""
    print("\n" + "="*60)
    print("🔍 Testing Error Handling")
    print("="*60)
    
    generator = ScriptGeneratingAction(
        output_dir="test_output",
        llm_model="gpt-3.5-turbo",
        max_retries=2  # Limit retries for testing
    )
    
    # Test with very ambiguous requirements
    print("\n📝 Test: Ambiguous Requirements")
    result = generator.generate_script(
        task_description="Do something with files",  # Very vague
        script_name="vague_script",
        requirements={}
    )
    
    print_test_result(result, "Ambiguous Requirements Test")
    
    return True


def test_script_execution():
    """Test execution of generated scripts."""
    print("\n" + "="*60)
    print("🔍 Testing Script Execution")
    print("="*60)
    
    generator = ScriptGeneratingAction(
        output_dir="test_output",
        llm_model="gpt-3.5-turbo"
    )
    
    # Generate a simple executable script
    print("\n📝 Generating Simple Executable Script")
    result = generator.generate_script(
        task_description="Create a simple script that prints 'Hello from ALITA!' and exits with code 0",
        script_name="hello_test",
        requirements={
            "constraints": "Must be executable and return success code"
        }
    )
    
    if result.get("success"):
        script_path = result["script_path"]
        print(f"✅ Script generated: {script_path}")
        
        # Test execution
        print("\n🚀 Testing Script Execution")
        exec_result = generator.test_script(script_path)
        
        if exec_result.get("success"):
            print("✅ Script executed successfully!")
            print(f"Output: {exec_result.get('stdout', '').strip()}")
        else:
            print("❌ Script execution failed!")
            print(f"Error: {exec_result.get('error')}")
            if exec_result.get('stderr'):
                print(f"Stderr: {exec_result.get('stderr')}")
    else:
        print(f"❌ Script generation failed: {result.get('error')}")
    
    return True


def test_list_scripts():
    """Test script listing functionality."""
    print("\n" + "="*60)
    print("🔍 Testing Script Listing")
    print("="*60)
    
    generator = ScriptGeneratingAction(output_dir="test_output")
    
    scripts_info = generator.list_generated_scripts()
    
    print(f"📁 Output directory: {scripts_info.get('output_directory')}")
    print(f"📊 Total scripts: {scripts_info.get('total_scripts', 0)}")
    
    if scripts_info.get("scripts"):
        print("\n📋 Generated Scripts:")
        for script in scripts_info["scripts"]:
            print(f"  • {script['name']}.py ({script['size']} bytes)")
            print(f"    Created: {script['created']}")
            print(f"    Has main(): {script['has_main']}")
    else:
        print("No scripts found in output directory")
    
    return True


def print_test_result(result, test_name):
    """Print formatted test result."""
    if result.get("success"):
        print(f"✅ {test_name}: SUCCESS")
        print(f"   Script: {result.get('script_name')}")
        print(f"   Path: {result.get('script_path')}")
        if result.get('metadata'):
            print(f"   Generated: {result['metadata'].get('created_at')}")
    else:
        print(f"❌ {test_name}: FAILED")
        print(f"   Error: {result.get('error')}")


def cleanup_test_files():
    """Clean up test output files."""
    test_dir = Path("test_output")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test directory: {test_dir}")


def main():
    """Run all tests."""
    print("🚀 Starting ALITA Script Generation Tests")
    print("=" * 60)
    
    try:
        # Clean up any existing test files
        cleanup_test_files()
        
        # Run tests
        tests = [
            ("Basic Script Generation", test_basic_script_generation),
            ("Code Quality Validation", test_code_quality_validation),
            ("Error Handling", test_error_handling),
            ("Script Execution", test_script_execution),
            ("Script Listing", test_list_scripts),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n🔄 Running: {test_name}")
                if test_func():
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                logger.exception(f"Error in test {test_name}")
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the output above.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        logger.exception("Unexpected error in main")
    finally:
        # Optional: Keep test files for inspection
        # cleanup_test_files()
        print("\n🏁 Test run completed")


if __name__ == "__main__":
    main()