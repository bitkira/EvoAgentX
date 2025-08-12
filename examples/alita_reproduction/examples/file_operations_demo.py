"""
File Operations Demo for ALITA reproduction.

This script demonstrates the file operations capabilities of the ALITA system,
including reading, writing, appending, and listing files using the integrated FileToolkit.
"""

import sys
import os

# Add the EvoAgentX root to path
sys.path.append('/Users/bitkira/Documents/GitHub/EvoAgentX')

from examples.alita_reproduction.agents.manager_agent import ManagerAgent
from examples.alita_reproduction.config import ALITAConfig

def main():
    """Main demonstration function."""
    
    print("🔧 ALITA File Operations Demo")
    print("=" * 60)
    
    # Initialize the Manager Agent
    try:
        config = ALITAConfig()
        llm_config = config.create_llm_config()
        manager = ManagerAgent(llm_config=llm_config)
        print("✅ Manager Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Manager Agent: {e}")
        return
    
    print("\n📊 File Operations Status:")
    print("-" * 30)
    status = manager.get_file_operations_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Demo data directory
    demo_dir = "examples/alita_reproduction/temp_file_demo"
    os.makedirs(demo_dir, exist_ok=True)
    
    print(f"\n📁 Demo Directory: {demo_dir}")
    print("-" * 40)
    
    # Demo 1: Write a file
    print("\n1️⃣ Writing a file...")
    file_path = os.path.join(demo_dir, "demo_file.txt")
    content = """Hello from ALITA File Operations!

This is a demonstration of file writing capabilities.
- Line 1: Basic text writing
- Line 2: Unicode support: 你好世界! 🌍
- Line 3: Numbers and symbols: 123 @#$%

Created by ALITA ManagerAgent.
"""
    
    write_result = manager.write_file(file_path, content)
    if write_result["success"]:
        print(f"   ✅ File written: {write_result['content_length']} characters")
        print(f"   📄 File type: {write_result['file_type']}")
    else:
        print(f"   ❌ Write failed: {write_result['error']}")
    
    # Demo 2: Read the file
    print("\n2️⃣ Reading the file...")
    read_result = manager.read_file(file_path)
    if read_result["success"]:
        print(f"   ✅ File read: {read_result['file_size']} bytes")
        print(f"   📄 File type: {read_result['file_type']}")
        print("   📝 Content preview (first 100 chars):")
        print(f"   '{read_result['content'][:100]}...'")
    else:
        print(f"   ❌ Read failed: {read_result['error']}")
    
    # Demo 3: Append to the file
    print("\n3️⃣ Appending to the file...")
    append_content = "\n\n[APPENDED CONTENT]\nThis content was appended using ALITA file operations.\nTimestamp: " + str(os.time.time() if hasattr(os, 'time') else "N/A")
    
    append_result = manager.append_file(file_path, append_content)
    if append_result["success"]:
        print(f"   ✅ Content appended: {append_result['content_length']} characters")
    else:
        print(f"   ❌ Append failed: {append_result['error']}")
    
    # Demo 4: Get file information
    print("\n4️⃣ Getting file information...")
    info_result = manager.get_file_info(file_path)
    if info_result["success"]:
        print(f"   ✅ File info retrieved:")
        print(f"      📁 Name: {info_result['name']}")
        print(f"      📏 Size: {info_result['size']} bytes")
        print(f"      📄 Type: {info_result['type']}")
        print(f"      🔍 Readable: {info_result['readable']}")
        print(f"      ✏️  Writable: {info_result['writable']}")
    else:
        print(f"   ❌ Info retrieval failed: {info_result['error']}")
    
    # Demo 5: Create additional files for listing
    print("\n5️⃣ Creating additional demo files...")
    additional_files = [
        ("demo_data.json", '{"name": "ALITA", "version": "1.0", "capabilities": ["code", "search", "files"]}'),
        ("demo_script.py", "print('Hello from ALITA Python script!')\\nresult = 2 + 2\\nprint(f'2 + 2 = {result}')"),
        ("demo_config.txt", "[ALITA Config]\\nmode=demo\\nversion=commit4\\nfeatures=file_operations")
    ]
    
    for filename, file_content in additional_files:
        path = os.path.join(demo_dir, filename)
        result = manager.write_file(path, file_content)
        if result["success"]:
            print(f"   ✅ Created: {filename}")
        else:
            print(f"   ❌ Failed to create {filename}: {result['error']}")
    
    # Demo 6: List files in directory
    print("\n6️⃣ Listing files in demo directory...")
    list_result = manager.list_files(demo_dir)
    if list_result["success"]:
        print(f"   ✅ Found {list_result['total_files']} files:")
        for file_info in list_result["files"]:
            print(f"      📄 {file_info['name']} ({file_info['size']} bytes, {file_info['type']})")
    else:
        print(f"   ❌ Listing failed: {list_result['error']}")
    
    # Demo 7: List Python files specifically
    print("\n7️⃣ Listing Python files only...")
    python_list_result = manager.list_files(demo_dir, "*.py")
    if python_list_result["success"]:
        print(f"   ✅ Found {python_list_result['total_files']} Python files:")
        for file_info in python_list_result["files"]:
            print(f"      🐍 {file_info['name']} ({file_info['size']} bytes)")
    else:
        print(f"   ❌ Python file listing failed: {python_list_result['error']}")
    
    # Demo 8: Error handling - try to read non-existent file
    print("\n8️⃣ Error handling demo - reading non-existent file...")
    nonexistent_path = os.path.join(demo_dir, "nonexistent_file.txt")
    error_result = manager.read_file(nonexistent_path)
    if not error_result["success"]:
        print(f"   ✅ Error handled gracefully: {error_result['error']}")
    else:
        print(f"   ⚠️  Unexpected success reading non-existent file")
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 File Operations Demo Summary")
    print(f"{'='*60}")
    print("✅ Demonstrated capabilities:")
    print("   • File writing with content validation")
    print("   • File reading with format detection")
    print("   • File appending with size tracking")
    print("   • File information retrieval")
    print("   • Directory file listing")
    print("   • Pattern-based file filtering")
    print("   • Comprehensive error handling")
    print("   • Multiple file format support")
    
    print(f"\n🧹 Demo files created in: {demo_dir}")
    print("   (You can safely delete this directory after the demo)")
    
    print("\n🎉 File operations demo completed successfully!")

if __name__ == "__main__":
    main()