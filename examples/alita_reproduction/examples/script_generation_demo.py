#!/usr/bin/env python3
"""
Example usage of the simplified ALITA script generation system.

This script demonstrates how to use the new LLM-based script generation
approach for various real-world scenarios.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.alita_reproduction.actions.script_generating import ScriptGeneratingAction
from examples.alita_reproduction.utils.code_quality import CodeQualityChecker

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_data_processing():
    """Demo: Generate a data processing script."""
    print("\n" + "="*70)
    print("📊 DEMO: Data Processing Script Generation")
    print("="*70)
    
    generator = ScriptGeneratingAction(
        output_dir="demo_scripts",
        llm_model="gpt-4"  # Use GPT-4 for better code quality
    )
    
    task = """
    Create a comprehensive data analysis script that:
    1. Reads a CSV file containing sales data (columns: date, product, quantity, price)
    2. Performs data cleaning (remove duplicates, handle missing values)
    3. Calculates monthly sales totals and product performance metrics
    4. Generates a summary report with visualizations (bar charts, line plots)
    5. Exports results to both CSV and JSON formats
    """
    
    requirements = {
        "input_format": "CSV file with sales data",
        "output_format": "Multiple files (CSV, JSON, PNG charts)",
        "libraries": ["pandas", "numpy", "matplotlib", "seaborn"],
        "constraints": "Handle edge cases like empty data or invalid dates",
        "author": "ALITA Demo"
    }
    
    print("📝 Generating data processing script...")
    result = generator.generate_script(
        task_description=task,
        script_name="sales_data_analyzer",
        requirements=requirements
    )
    
    print_demo_result(result, "Sales Data Analyzer")
    return result


def demo_web_scraping():
    """Demo: Generate a web scraping script."""
    print("\n" + "="*70)
    print("🌐 DEMO: Web Scraping Script Generation")
    print("="*70)
    
    generator = ScriptGeneratingAction(output_dir="demo_scripts")
    
    task = """
    Create a respectful web scraping script that:
    1. Scrapes product information from an e-commerce website
    2. Respects robots.txt and implements rate limiting
    3. Extracts product names, prices, ratings, and descriptions
    4. Stores data in a structured format (JSON/CSV)
    5. Includes error handling for network issues and blocked requests
    6. Implements user-agent rotation and session management
    """
    
    requirements = {
        "libraries": ["requests", "beautifulsoup4", "time", "random"],
        "constraints": "Must be ethical and respectful to website resources",
        "output_format": "JSON and CSV files"
    }
    
    print("📝 Generating web scraping script...")
    result = generator.generate_script(
        task_description=task,
        script_name="ethical_web_scraper",
        requirements=requirements
    )
    
    print_demo_result(result, "Ethical Web Scraper")
    return result


def demo_automation_script():
    """Demo: Generate a system automation script."""
    print("\n" + "="*70)
    print("🤖 DEMO: System Automation Script Generation")
    print("="*70)
    
    generator = ScriptGeneratingAction(output_dir="demo_scripts")
    
    task = """
    Create a system maintenance automation script that:
    1. Monitors disk space usage and sends alerts when usage exceeds 80%
    2. Cleans up temporary files and old log files
    3. Backs up important directories to a specified location
    4. Generates a system health report (CPU, memory, disk usage)
    5. Sends email notifications with the report
    6. Logs all activities with timestamps
    """
    
    requirements = {
        "libraries": ["psutil", "shutil", "smtplib", "email"],
        "constraints": "Must be safe and not delete critical system files",
        "output_format": "Log files and email reports"
    }
    
    print("📝 Generating automation script...")
    result = generator.generate_script(
        task_description=task,
        script_name="system_maintenance",
        requirements=requirements
    )
    
    print_demo_result(result, "System Maintenance")
    return result


def demo_api_integration():
    """Demo: Generate an API integration script."""
    print("\n" + "="*70)
    print("🔌 DEMO: API Integration Script Generation")
    print("="*70)
    
    generator = ScriptGeneratingAction(output_dir="demo_scripts")
    
    task = """
    Create a REST API integration script that:
    1. Connects to a weather API to fetch current weather data
    2. Processes multiple city weather information
    3. Implements retry logic for failed requests
    4. Caches responses to minimize API calls
    5. Formats data into readable reports
    6. Supports both JSON and XML response formats
    7. Includes comprehensive error handling for API limits and failures
    """
    
    requirements = {
        "libraries": ["requests", "json", "xml.etree.ElementTree", "time"],
        "input_format": "List of city names",
        "output_format": "Formatted weather reports",
        "constraints": "Respect API rate limits and handle authentication"
    }
    
    print("📝 Generating API integration script...")
    result = generator.generate_script(
        task_description=task,
        script_name="weather_api_client",
        requirements=requirements
    )
    
    print_demo_result(result, "Weather API Client")
    return result


def demo_quality_analysis():
    """Demo: Analyze generated script quality."""
    print("\n" + "="*70)
    print("🔍 DEMO: Code Quality Analysis")
    print("="*70)
    
    checker = CodeQualityChecker()
    
    # Get list of generated scripts
    generator = ScriptGeneratingAction(output_dir="demo_scripts")
    scripts_info = generator.list_generated_scripts()
    
    if not scripts_info.get("scripts"):
        print("❌ No scripts found to analyze")
        return
    
    print(f"📊 Analyzing {len(scripts_info['scripts'])} generated scripts:")
    
    for script in scripts_info["scripts"]:
        script_path = script["path"]
        script_name = script["name"]
        
        print(f"\n🔍 Analyzing: {script_name}.py")
        
        # Analyze the script
        analysis = checker.analyze_file(script_path)
        summary = checker.get_validation_summary(analysis)
        
        print(f"   {summary}")
        
        # Show detailed issues if any
        if analysis.get("security_risks"):
            print("   ⚠️  Security risks:")
            for risk in analysis["security_risks"]:
                print(f"      - {risk['description']} (Line {risk.get('line', '?')})")
        
        if analysis.get("issues"):
            print("   📝 Issues:")
            for issue in analysis["issues"]:
                if issue.get("severity") in ["high", "critical"]:
                    print(f"      - {issue['description']}")


def demo_script_execution():
    """Demo: Execute generated scripts safely."""
    print("\n" + "="*70)
    print("🚀 DEMO: Script Execution Testing")
    print("="*70)
    
    generator = ScriptGeneratingAction(output_dir="demo_scripts")
    
    # Generate a simple test script
    print("📝 Generating test script...")
    result = generator.generate_script(
        task_description="Create a simple script that demonstrates Python best practices: imports, logging, main function, error handling, and clean output",
        script_name="demo_test_runner",
        requirements={
            "constraints": "Must be safe to execute and demonstrate good practices"
        }
    )
    
    if result.get("success"):
        script_path = result["script_path"]
        print(f"✅ Generated: {script_path}")
        
        # Test the script
        print("\n🚀 Testing script execution...")
        exec_result = generator.test_script(script_path)
        
        if exec_result.get("success"):
            print("✅ Script executed successfully!")
            print("📋 Output:")
            print("-" * 40)
            print(exec_result.get("stdout", "No output"))
            print("-" * 40)
        else:
            print("❌ Script execution failed!")
            print(f"Error: {exec_result.get('error')}")
            if exec_result.get("stderr"):
                print(f"Stderr: {exec_result.get('stderr')}")
    else:
        print(f"❌ Script generation failed: {result.get('error')}")


def print_demo_result(result, demo_name):
    """Print formatted demo result."""
    if result.get("success"):
        print(f"✅ {demo_name}: Generated successfully!")
        print(f"   📁 Script: {result.get('script_name')}.py")
        print(f"   📍 Location: {result.get('script_path')}")
        print(f"   📏 Size: {len(result.get('content', ''))} characters")
        
        # Show first few lines of the generated script
        content = result.get('content', '')
        lines = content.split('\n')[:10]  # First 10 lines
        print(f"   📖 Preview:")
        for i, line in enumerate(lines, 1):
            print(f"      {i:2d}: {line}")
        if len(content.split('\n')) > 10:
            print(f"      ... (and {len(content.split('\n')) - 10} more lines)")
    else:
        print(f"❌ {demo_name}: Generation failed!")
        print(f"   Error: {result.get('error')}")


def main():
    """Run all demonstrations."""
    print("🎭 ALITA Script Generation Demonstrations")
    print("=" * 70)
    print("This demo showcases the new LLM-based script generation approach")
    print("for various real-world automation and development scenarios.")
    
    try:
        # Run demonstrations
        demos = [
            ("Data Processing", demo_data_processing),
            ("Web Scraping", demo_web_scraping),
            ("System Automation", demo_automation_script),
            ("API Integration", demo_api_integration),
            ("Script Execution", demo_script_execution),
            ("Quality Analysis", demo_quality_analysis),
        ]
        
        for demo_name, demo_func in demos:
            try:
                demo_func()
            except Exception as e:
                print(f"❌ Demo '{demo_name}' failed: {str(e)}")
                logger.exception(f"Error in demo {demo_name}")
        
        # Final summary
        print("\n" + "="*70)
        print("📊 DEMONSTRATION SUMMARY")
        print("="*70)
        
        generator = ScriptGeneratingAction(output_dir="demo_scripts")
        scripts_info = generator.list_generated_scripts()
        
        print(f"📁 Generated scripts directory: {scripts_info.get('output_directory')}")
        print(f"📊 Total scripts generated: {scripts_info.get('total_scripts', 0)}")
        
        if scripts_info.get("scripts"):
            print("\n📋 Generated Scripts:")
            for script in scripts_info["scripts"]:
                print(f"  • {script['name']}.py")
                print(f"    Size: {script['size']} bytes")
                print(f"    Created: {script['created']}")
                print(f"    Has main(): {script['has_main']}")
                print()
        
        print("🎉 Demonstration completed!")
        print("💡 Check the 'demo_scripts' directory to see all generated scripts.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        logger.exception("Unexpected error in main")


if __name__ == "__main__":
    main()