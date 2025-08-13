"""
MCP Integration Demo for ALITA reproduction.

This demo showcases the complete MCP (Model Context Protocol) integration
functionality in the ALITA system, including:
- Dynamic tool discovery and management
- Script-to-MCP-tool conversion
- Tool persistence and reuse
- Enhanced workflow with existing tool prioritization
"""

import os
import sys
from pathlib import Path
import tempfile
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.alita_reproduction.config import ALITAConfig
from examples.alita_reproduction.agents.manager_agent import ManagerAgent
from examples.alita_reproduction.mcp import ALITAMCPServer, ScriptToMCPWrapper, MCPToolPersistence
from examples.alita_reproduction.utils.mcp_config_manager import MCPConfigManager


def create_sample_scripts():
    """Create sample scripts for MCP demonstration."""
    # Create a temporary directory for demo scripts
    demo_dir = Path(tempfile.gettempdir()) / "alita_mcp_demo"
    demo_dir.mkdir(exist_ok=True)
    
    # Sample script 1: Simple calculator
    calculator_script = demo_dir / "calculator.py"
    with open(calculator_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Simple calculator script demonstrating MCP tool conversion.
"""
import sys
import json

def calculate(operation, a, b):
    """Perform calculation based on operation."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b != 0:
            return a / b
        else:
            return "Error: Division by zero"
    else:
        return f"Error: Unknown operation {operation}"

def main():
    """Main function for calculator."""
    try:
        # Try to read JSON input from stdin (MCP tool mode)
        input_data = sys.stdin.read().strip()
        if input_data:
            data = json.loads(input_data)
            operation = data.get('operation', 'add')
            a = float(data.get('a', 0))
            b = float(data.get('b', 0))
            
            result = calculate(operation, a, b)
            print(f"Calculator result: {a} {operation} {b} = {result}")
        else:
            # Default demonstration
            print("Calculator: 10 + 5 = 15")
            print("Calculator: 20 * 3 = 60")
    except Exception as e:
        print(f"Calculator error: {str(e)}")

if __name__ == "__main__":
    main()
''')
    
    # Sample script 2: Text processor
    text_processor_script = demo_dir / "text_processor.py"
    with open(text_processor_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Text processing script demonstrating MCP tool capabilities.
"""
import sys
import json
import re

def process_text(text, operation="clean"):
    """Process text based on operation."""
    if operation == "clean":
        # Remove extra whitespace and normalize
        return re.sub(r'\\s+', ' ', text.strip())
    elif operation == "uppercase":
        return text.upper()
    elif operation == "lowercase":
        return text.lower()
    elif operation == "word_count":
        words = text.split()
        return f"Word count: {len(words)}"
    elif operation == "char_count":
        return f"Character count: {len(text)}"
    else:
        return f"Unknown operation: {operation}"

def main():
    """Main function for text processor."""
    try:
        # Try to read JSON input from stdin
        input_data = sys.stdin.read().strip()
        if input_data:
            data = json.loads(input_data)
            text = data.get('text', 'Hello, World!')
            operation = data.get('operation', 'clean')
            
            result = process_text(text, operation)
            print(f"Text processing result: {result}")
        else:
            # Default demonstration
            demo_text = "  This   is    a    sample   text   "
            print(f"Original: '{demo_text}'")
            print(f"Cleaned: '{process_text(demo_text, 'clean')}'")
            print(f"Uppercase: '{process_text(demo_text, 'uppercase')}'")
            print(f"{process_text(demo_text, 'word_count')}")
    except Exception as e:
        print(f"Text processor error: {str(e)}")

if __name__ == "__main__":
    main()
''')
    
    # Sample script 3: Data analyzer
    data_analyzer_script = demo_dir / "data_analyzer.py"
    with open(data_analyzer_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Data analysis script for MCP tool demonstration.
"""
import sys
import json
import statistics

def analyze_data(data, analysis_type="basic"):
    """Analyze numeric data."""
    if not data or not isinstance(data, list):
        return "Error: Invalid data - expected list of numbers"
    
    try:
        numeric_data = [float(x) for x in data]
        
        if analysis_type == "basic":
            return {
                "count": len(numeric_data),
                "sum": sum(numeric_data),
                "average": statistics.mean(numeric_data),
                "min": min(numeric_data),
                "max": max(numeric_data)
            }
        elif analysis_type == "statistics":
            result = {
                "mean": statistics.mean(numeric_data),
                "median": statistics.median(numeric_data),
                "mode": statistics.mode(numeric_data) if len(set(numeric_data)) < len(numeric_data) else "No mode",
                "stdev": statistics.stdev(numeric_data) if len(numeric_data) > 1 else 0,
                "variance": statistics.variance(numeric_data) if len(numeric_data) > 1 else 0
            }
            return result
        else:
            return f"Unknown analysis type: {analysis_type}"
    except Exception as e:
        return f"Analysis error: {str(e)}"

def main():
    """Main function for data analyzer."""
    try:
        input_data = sys.stdin.read().strip()
        if input_data:
            data = json.loads(input_data)
            numbers = data.get('data', [1, 2, 3, 4, 5])
            analysis_type = data.get('analysis_type', 'basic')
            
            result = analyze_data(numbers, analysis_type)
            print(f"Data analysis result: {json.dumps(result, indent=2)}")
        else:
            # Default demonstration
            sample_data = [10, 20, 30, 40, 50, 25, 35, 45]
            print(f"Sample data: {sample_data}")
            result = analyze_data(sample_data, "basic")
            print(f"Basic analysis: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Data analyzer error: {str(e)}")

if __name__ == "__main__":
    main()
''')
    
    return demo_dir, [calculator_script, text_processor_script, data_analyzer_script]


def demo_mcp_server():
    """Demonstrate ALITA MCP server functionality."""
    print("=== ALITA MCP Server Demo ===")
    
    # Create sample scripts
    demo_dir, script_paths = create_sample_scripts()
    print(f"Created sample scripts in: {demo_dir}")
    
    # Initialize MCP server
    server = ALITAMCPServer(
        server_name="alita-demo",
        tools_dir=str(demo_dir)
    )
    
    print(f"\\n1. Initialized ALITA MCP Server: {server.server_name}")
    
    # Register scripts as MCP tools
    for script_path in script_paths:
        script_name = script_path.stem
        tool_name = f"{script_name}_tool"
        
        # Register script
        result = server.register_script_as_tool(
            script_path=str(script_path),
            tool_name=tool_name,
            description=f"MCP tool for {script_name} operations"
        )
        
        if result["success"]:
            print(f"✓ Registered: {tool_name}")
        else:
            print(f"✗ Failed to register {tool_name}: {result['error']}")
    
    # List registered tools
    tools = server.list_tools()
    print(f"\\n2. Registered Tools ({tools['tools_count']} total):")
    for tool_name, tool_info in tools["tools"].items():
        print(f"   - {tool_name}: {tool_info['description']}")
    
    # Execute tools
    print("\\n3. Tool Execution Examples:")
    
    # Test calculator
    calc_result = server.execute_tool("calculator_tool", operation="multiply", a=7, b=8)
    if calc_result["success"]:
        print(f"   Calculator: {calc_result['output']}")
    
    # Test text processor
    text_result = server.execute_tool("text_processor_tool", 
                                    text="   Hello,    World!   ", 
                                    operation="clean")
    if text_result["success"]:
        print(f"   Text Processor: {text_result['output']}")
    
    # Test data analyzer
    data_result = server.execute_tool("data_analyzer_tool", 
                                    data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
                                    analysis_type="basic")
    if data_result["success"]:
        print(f"   Data Analyzer: {data_result['output']}")
    
    print("\\n✓ MCP Server demo completed")
    return server


def demo_script_wrapper():
    """Demonstrate script-to-MCP-tool wrapping."""
    print("\\n=== Script Wrapper Demo ===")
    
    # Create sample scripts
    demo_dir, script_paths = create_sample_scripts()
    
    # Initialize script wrapper
    wrapper = ScriptToMCPWrapper(str(demo_dir))
    
    print("1. Script Analysis:")
    for script_path in script_paths:
        analysis = wrapper.analyze_script(str(script_path))
        if analysis["success"]:
            print(f"   ✓ {script_path.name}:")
            print(f"     Description: {analysis['description']}")
            print(f"     Functions: {len(analysis['functions'])}")
            print(f"     Entry point: {analysis['entry_point']}")
            print(f"     Imports: {len(analysis['imports'])}")
        else:
            print(f"   ✗ {script_path.name}: {analysis['error']}")
    
    print("\\n2. Script Wrapping:")
    for script_path in script_paths[:2]:  # Wrap first two scripts
        try:
            tool_spec = wrapper.wrap_script(
                str(script_path),
                tool_name=f"{script_path.stem}_wrapped",
                tool_description=f"Wrapped version of {script_path.name}"
            )
            print(f"   ✓ Wrapped: {tool_spec.name}")
            print(f"     Parameters: {len(tool_spec.parameters.get('properties', {}))}")
        except Exception as e:
            print(f"   ✗ Failed to wrap {script_path.name}: {str(e)}")
    
    print("\\n3. Script Execution Test:")
    test_result = wrapper.test_script_execution(
        str(script_paths[0]),  # Test calculator
        {"operation": "add", "a": 15, "b": 25}
    )
    
    if test_result["success"]:
        print(f"   ✓ Test execution successful")
        print(f"   Output: {test_result['stdout']}")
    else:
        print(f"   ✗ Test execution failed: {test_result['error']}")
    
    print("\\n✓ Script Wrapper demo completed")


def demo_tool_persistence():
    """Demonstrate MCP tool persistence."""
    print("\\n=== Tool Persistence Demo ===")
    
    # Create temporary persistence directory
    persistence_dir = Path(tempfile.gettempdir()) / "alita_persistence_demo"
    persistence_dir.mkdir(exist_ok=True)
    
    # Initialize persistence manager
    persistence = MCPToolPersistence(str(persistence_dir))
    
    print(f"1. Initialized persistence manager: {persistence_dir}")
    
    # Create sample scripts
    demo_dir, script_paths = create_sample_scripts()
    
    # Persist tools
    print("\\n2. Persisting Tools:")
    tool_ids = []
    for i, script_path in enumerate(script_paths):
        tool_id = f"demo_tool_{i+1}"
        result = persistence.persist_tool(
            tool_id=tool_id,
            name=f"{script_path.stem}_persistent",
            description=f"Persistent version of {script_path.name}",
            script_path=str(script_path),
            parameters={"type": "object", "properties": {"input": {"type": "string"}}},
            metadata={"demo": True, "script_type": script_path.stem}
        )
        
        if result["success"]:
            print(f"   ✓ Persisted: {tool_id}")
            tool_ids.append(tool_id)
        else:
            print(f"   ✗ Failed to persist {tool_id}: {result['error']}")
    
    # List persisted tools
    tools_list = persistence.list_tools()
    print(f"\\n3. Persisted Tools ({tools_list['total_tools']} total):")
    for tool in tools_list["tools"]:
        print(f"   - {tool['name']} (ID: {tool['id']}, Usage: {tool['usage_count']})")
    
    # Simulate usage
    print("\\n4. Simulating Tool Usage:")
    for tool_id in tool_ids[:2]:  # Use first two tools
        persistence.increment_usage(tool_id)
        print(f"   ✓ Incremented usage for {tool_id}")
    
    # Show statistics
    stats = persistence.get_statistics()
    print("\\n5. Persistence Statistics:")
    print(f"   Total tools: {stats['total_tools']}")
    print(f"   Active tools: {stats['active_tools']}")
    print(f"   Total usage: {stats['total_usage']}")
    if stats['most_used_tool']:
        print(f"   Most used: {stats['most_used_tool']['name']} ({stats['most_used_tool']['usage_count']} uses)")
    
    print("\\n✓ Tool Persistence demo completed")


def demo_full_workflow():
    """Demonstrate the complete MCP workflow with Manager Agent."""
    print("\\n=== Full MCP Workflow Demo ===")
    
    try:
        # Set up ALITA configuration (use environment variables if available)
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("⚠️  OpenAI API key not found. Creating minimal demo config.")
            print("   Set OPENAI_API_KEY environment variable for full demo.")
            return
        
        # Initialize ALITA configuration
        config = ALITAConfig(openai_api_key=openai_key)
        llm_config = config.create_llm_config()
        
        # Initialize Manager Agent
        manager = ManagerAgent(llm_config=llm_config)
        
        print("1. ✓ Initialized Manager Agent with MCP capabilities")
        
        # Get MCP status
        mcp_status = manager.get_mcp_status()
        print(f"2. MCP Status: {mcp_status}")
        
        # Discover existing tools
        discovered_tools = manager.discover_mcp_tools()
        print(f"3. Discovered {discovered_tools.get('total_tools', 0)} existing MCP tools")
        
        # Demo task processing with MCP workflow
        demo_tasks = [
            "Calculate the result of 25 multiplied by 4",
            "Process this text: '  Hello,   WORLD!   ' and make it clean",
            "Analyze these numbers: [5, 10, 15, 20, 25] and give me basic statistics"
        ]
        
        print("\\n4. Processing Tasks with MCP Workflow:")
        for i, task in enumerate(demo_tasks, 1):
            print(f"\\n   Task {i}: {task}")
            print("   " + "-" * 50)
            
            # Find suitable tools for the task
            suitable_tools = manager.find_suitable_mcp_tool(task)
            if suitable_tools.get("suitable_tools"):
                best_tool = suitable_tools["suitable_tools"][0]
                print(f"   → Found suitable tool: {best_tool['name']}")
                
                # Try to execute the tool
                if "calculate" in task.lower():
                    tool_result = manager.execute_mcp_tool(best_tool["name"], {
                        "operation": "multiply", "a": 25, "b": 4
                    })
                elif "process" in task.lower():
                    tool_result = manager.execute_mcp_tool(best_tool["name"], {
                        "text": "  Hello,   WORLD!   ", "operation": "clean"
                    })
                elif "analyze" in task.lower():
                    tool_result = manager.execute_mcp_tool(best_tool["name"], {
                        "data": [5, 10, 15, 20, 25], "analysis_type": "basic"
                    })
                else:
                    tool_result = {"success": False, "error": "Task not supported"}
                
                if tool_result["success"]:
                    print(f"   ✓ Result: {tool_result.get('output', tool_result.get('result'))}")
                else:
                    print(f"   ✗ Tool execution failed: {tool_result.get('error')}")
            else:
                print(f"   → No suitable existing tools found")
                print(f"   → Recommendation: {suitable_tools.get('recommendation')}")
        
        print("\\n✓ Full MCP Workflow demo completed")
        
    except Exception as e:
        print(f"\\n✗ Full workflow demo failed: {str(e)}")
        print("   This may be due to missing dependencies or configuration issues.")


def main():
    """Run complete MCP integration demonstration."""
    print("🚀 ALITA MCP Integration Comprehensive Demo")
    print("=" * 60)
    print("This demo showcases the complete MCP (Model Context Protocol)")
    print("integration in the ALITA reproduction project.")
    print("=" * 60)
    
    try:
        # 1. MCP Server Demo
        server = demo_mcp_server()
        
        # 2. Script Wrapper Demo
        demo_script_wrapper()
        
        # 3. Tool Persistence Demo
        demo_tool_persistence()
        
        # 4. Full Workflow Demo (requires OpenAI API key)
        demo_full_workflow()
        
        print("\\n" + "=" * 60)
        print("🎉 All MCP Integration Demos Completed Successfully!")
        print("=" * 60)
        print("\\nKey Features Demonstrated:")
        print("✓ ALITA MCP Server - Dynamic tool hosting")
        print("✓ Script-to-MCP Tool Conversion - Automatic wrapping")  
        print("✓ Tool Persistence - File-based tool management")
        print("✓ Manager Agent Integration - Enhanced workflow")
        print("✓ Tool Discovery & Execution - Intelligent tool selection")
        print("\\nThe ALITA system can now:")
        print("• Automatically convert scripts to reusable MCP tools")
        print("• Persist tools across sessions for future reuse") 
        print("• Discover and prioritize existing tools before generating new ones")
        print("• Integrate seamlessly with the EvoAgentX MCP ecosystem")
        
    except KeyboardInterrupt:
        print("\\n\\nDemo interrupted by user.")
    except Exception as e:
        print(f"\\n\\nDemo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\\nDemo completed. Thank you for exploring ALITA MCP integration!")


if __name__ == "__main__":
    main()