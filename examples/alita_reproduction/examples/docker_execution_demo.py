#!/usr/bin/env python3
"""
Docker Execution Demo for ALITA reproduction.

This demo showcases the Docker security execution capabilities added in Commit 6,
including secure code execution, security validation, result validation, and error recovery.
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from actions.docker_execution import DockerExecutionAction, DockerConfig, quick_docker_execute
from utils.security_validator import quick_security_check, SecurityValidator
from utils.docker_config import DockerConfigManager, ContainerProfile, get_config_for_script_type
from utils.result_validator import quick_validate_result, ResultValidator
from utils.error_recovery import analyze_error_type, recover_execution
from utils.execution_monitor import ExecutionMonitor, MonitoringConfig, MonitoringLevel

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_docker_configuration():
    """Demonstrate Docker configuration management."""
    print("=== Docker Configuration Demo ===")
    
    config_manager = DockerConfigManager()
    
    # Show available profiles
    print("\nAvailable Docker Profiles:")
    profiles = config_manager.list_profiles()
    for profile_name, description in profiles.items():
        print(f"  - {profile_name}: {description}")
    
    # Show different profile configurations
    print("\nProfile Configurations:")
    
    # Standard profile
    standard_config = config_manager.get_profile(ContainerProfile.STANDARD)
    print(f"Standard: {standard_config.image_tag}, Memory: {standard_config.resource_limits.memory_limit}, Timeout: {standard_config.execution_settings.timeout}s")
    
    # Secure profile
    secure_config = config_manager.get_profile(ContainerProfile.SECURE)
    print(f"Secure: {secure_config.image_tag}, Memory: {secure_config.resource_limits.memory_limit}, Timeout: {secure_config.execution_settings.timeout}s")
    
    # Script-type specific recommendations
    print("\nScript Type Recommendations:")
    for script_type in ["data_processing", "web_scraping", "automation", "simple"]:
        config = get_config_for_script_type(script_type)
        print(f"  {script_type}: {config.profile.value} profile")


def demo_security_validation():
    """Demonstrate security validation capabilities."""
    print("\n=== Security Validation Demo ===")
    
    validator = SecurityValidator()
    
    # Test safe code
    print("\n1. Validating Safe Code:")
    safe_code = '''
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b

def main():
    result = calculate_fibonacci(10)
    print(f"10th Fibonacci number: {result}")

if __name__ == "__main__":
    main()
'''
    
    result = quick_security_check(safe_code)
    print(f"Safe: {result['is_safe']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Issues: {result['total_issues']}")
    
    # Test dangerous code
    print("\n2. Validating Dangerous Code:")
    dangerous_code = '''
import os
import subprocess

def dangerous_function():
    # Security risks
    user_input = input("Enter command: ")
    os.system(user_input)  # System command execution
    result = eval(user_input)  # Dynamic evaluation
    
    # Network access
    import requests
    requests.get("http://malicious-site.com")
    
    return result

dangerous_function()
'''
    
    result = quick_security_check(dangerous_code)
    print(f"Safe: {result['is_safe']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Issues: {result['total_issues']} (Critical: {result['critical_issues']}, High: {result['high_issues']})")
    
    # Show detailed analysis
    detailed_report = validator.analyze_code(dangerous_code)
    print(f"Detailed Analysis: {detailed_report.total_issues} issues found")
    print("Top issues:")
    for issue in detailed_report.issues[:3]:
        print(f"  - {issue.severity.value}: {issue.description}")


def demo_result_validation():
    """Demonstrate result validation capabilities."""
    print("\n=== Result Validation Demo ===")
    
    # Test successful output
    print("\n1. Validating Successful Output:")
    success_output = "Processing completed successfully!\nProcessed 1000 records\nTotal time: 2.5 seconds"
    
    result = quick_validate_result(success_output, None, 2.5)
    print(f"Valid: {result['is_valid']}")
    print(f"Status: {result['status']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Summary: {result['summary']}")
    
    # Test error output
    print("\n2. Validating Error Output:")
    error_output = ""
    error_message = "ValueError: invalid input format - expected JSON but received XML"
    
    result = quick_validate_result(error_output, error_message, 0.1)
    print(f"Valid: {result['is_valid']}")
    print(f"Status: {result['status']}")
    print(f"Error Count: {result['error_count']}")
    print(f"Summary: {result['summary']}")
    
    # Test script-specific validation
    print("\n3. Script-Type Specific Validation:")
    data_output = "Loaded dataset: 5000 rows, 15 columns\nMean age: 34.5\nStandard deviation: 12.3"
    
    result = quick_validate_result(data_output, None, 3.0, "data_processing")
    print(f"Data Processing Result - Valid: {result['is_valid']}")
    print(f"Recommendations: {result['recommendations']}")


def demo_error_analysis():
    """Demonstrate error analysis and recovery strategies."""
    print("\n=== Error Analysis Demo ===")
    
    error_examples = [
        "TimeoutError: execution time exceeded after 30 seconds",
        "ImportError: No module named 'pandas'",
        "MemoryError: out of memory during processing",
        "ConnectionError: failed to connect to remote server",
        "SyntaxError: invalid syntax on line 15"
    ]
    
    for error_msg in error_examples:
        print(f"\nAnalyzing: {error_msg}")
        analysis = analyze_error_type(error_msg)
        
        print(f"  Error Type: {analysis['error_type']}")
        print(f"  Recovery Strategies: {', '.join(analysis['recovery_strategies'])}")
        print(f"  Suggested Fixes: {analysis['suggested_fixes'][0] if analysis['suggested_fixes'] else 'None'}")


def demo_execution_monitoring():
    """Demonstrate execution monitoring capabilities."""
    print("\n=== Execution Monitoring Demo ===")
    
    # Create monitor with standard configuration
    config = MonitoringConfig(
        level=MonitoringLevel.STANDARD,
        enable_resource_monitoring=False,  # Disable for demo
        enable_network_monitoring=False,
        enable_disk_monitoring=False
    )
    
    monitor = ExecutionMonitor(config)
    
    print("Starting execution monitoring...")
    
    # Start monitoring
    execution_id = monitor.start_execution_monitoring(
        docker_image="python:3.9-slim",
        timeout=30,
        metadata={"demo": "execution_monitoring"}
    )
    
    print(f"Execution ID: {execution_id}")
    
    # Simulate execution phases
    from utils.execution_monitor import ExecutionPhase
    import time
    
    phases = [
        ExecutionPhase.VALIDATION,
        ExecutionPhase.DOCKER_SETUP,
        ExecutionPhase.CODE_EXECUTION,
        ExecutionPhase.RESULT_PROCESSING,
        ExecutionPhase.COMPLETED
    ]
    
    for phase in phases:
        time.sleep(0.2)  # Simulate work
        monitor.update_execution_phase(execution_id, phase, {"phase_info": f"Processing {phase.value}"})
        print(f"Phase: {phase.value}")
    
    # Record results
    monitor.record_execution_result(execution_id, True, 256, None, 0)
    
    # Stop monitoring and get metrics
    final_metrics = monitor.stop_execution_monitoring(execution_id)
    
    print(f"Total Duration: {final_metrics.get_total_duration():.2f}s")
    print(f"Success: {final_metrics.success}")
    print(f"Output Size: {final_metrics.output_size_bytes} bytes")
    
    # Generate report
    report = monitor.generate_execution_report(execution_id)
    if report:
        print(f"Execution Report Summary: {report['summary']['total_duration']:.2f}s execution")


def demo_docker_execution():
    """Demonstrate actual Docker code execution (requires Docker)."""
    print("\n=== Docker Execution Demo ===")
    print("Note: This demo requires Docker to be installed and running")
    
    try:
        # Quick execution example
        print("\n1. Quick Docker Execution:")
        simple_code = '''
import sys
print(f"Hello from Python {sys.version_info.major}.{sys.version_info.minor}")
print("Docker execution successful!")

# Simple calculation
numbers = [1, 2, 3, 4, 5]
result = sum(numbers)
print(f"Sum of {numbers} = {result}")
'''
        
        result = quick_docker_execute(
            simple_code,
            timeout=15,
            image_tag="python:3.9-alpine"
        )
        
        print(f"Execution Status: {result.status.value}")
        print(f"Execution Time: {result.execution_time:.2f}s")
        print("Output:")
        print(result.output)
        
        if result.error:
            print(f"Error: {result.error}")
        
        # Full Docker executor example
        print("\n2. Full Docker Executor:")
        config = DockerConfig(
            image_tag="python:3.9-alpine",
            timeout=20,
            print_stdout=False,
            print_stderr=False
        )
        
        executor = DockerExecutionAction(config)
        
        # Test environment
        env_result = executor.validate_execution_environment()
        if env_result['valid']:
            print("✓ Docker environment validated successfully")
            print(f"Docker Image: {env_result['docker_image']}")
            print(f"Test Output: {env_result['test_output']}")
        else:
            print(f"✗ Docker environment validation failed: {env_result['error']}")
        
        # Execute code with security validation
        calculation_code = '''
import math

def calculate_statistics(data):
    """Calculate basic statistics for a dataset."""
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    std_dev = math.sqrt(variance)
    
    return {
        "count": n,
        "mean": mean,
        "variance": variance,
        "std_dev": std_dev,
        "min": min(data),
        "max": max(data)
    }

# Test data
test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
stats = calculate_statistics(test_data)

print("Dataset Statistics:")
for key, value in stats.items():
    print(f"  {key}: {value:.2f}")

print("\\n✅ Statistics calculation completed successfully!")
'''
        
        execution_result = executor.execute_code(
            calculation_code,
            validate_security=True
        )
        
        print(f"Execution Status: {execution_result.status.value}")
        print(f"Execution Time: {execution_result.execution_time:.2f}s")
        print(f"Security Issues: {len(execution_result.security_issues) if execution_result.security_issues else 0}")
        
        if execution_result.status.value == "success":
            print("Output:")
            print(execution_result.output)
        else:
            print(f"Error: {execution_result.error}")
        
        # Get execution statistics
        stats = executor.get_execution_statistics()
        print(f"\nExecutor Statistics:")
        print(f"  Total Executions: {stats['total_executions']}")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        print(f"  Average Time: {stats['average_execution_time']:.3f}s")
        
    except Exception as e:
        print(f"Docker demo failed: {str(e)}")
        print("Make sure Docker is installed and running, or set DOCKER_AVAILABLE=1 environment variable")


def demo_comprehensive_workflow():
    """Demonstrate a comprehensive workflow combining all features."""
    print("\n=== Comprehensive Workflow Demo ===")
    
    # Create a sample script
    script_content = '''
"""
Sample data processing script for Docker execution demo.
"""

import json
import math
from typing import List, Dict, Any

def process_sales_data(sales: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process sales data and generate summary statistics."""
    if not sales:
        return {"error": "No sales data provided"}
    
    total_revenue = sum(item["amount"] for item in sales)
    avg_revenue = total_revenue / len(sales)
    
    # Calculate revenue by category
    category_revenue = {}
    for item in sales:
        category = item["category"]
        category_revenue[category] = category_revenue.get(category, 0) + item["amount"]
    
    return {
        "total_sales": len(sales),
        "total_revenue": total_revenue,
        "average_revenue": avg_revenue,
        "category_breakdown": category_revenue,
        "processing_successful": True
    }

def main():
    """Main processing function."""
    # Sample sales data
    sales_data = [
        {"category": "Electronics", "amount": 299.99, "date": "2025-01-01"},
        {"category": "Books", "amount": 19.99, "date": "2025-01-02"},
        {"category": "Electronics", "amount": 899.99, "date": "2025-01-03"},
        {"category": "Clothing", "amount": 49.99, "date": "2025-01-04"},
        {"category": "Books", "amount": 29.99, "date": "2025-01-05"},
    ]
    
    print("Starting sales data processing...")
    
    # Process the data
    results = process_sales_data(sales_data)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    # Display results
    print(f"\\nProcessing Results:")
    print(f"  Total Sales: {results['total_sales']}")
    print(f"  Total Revenue: ${results['total_revenue']:.2f}")
    print(f"  Average Revenue: ${results['average_revenue']:.2f}")
    
    print(f"\\nRevenue by Category:")
    for category, revenue in results['category_breakdown'].items():
        print(f"  {category}: ${revenue:.2f}")
    
    print(f"\\n✅ Data processing completed successfully!")

if __name__ == "__main__":
    main()
'''
    
    print("1. Security Validation:")
    security_result = quick_security_check(script_content)
    print(f"   Safe to execute: {security_result['is_safe']}")
    print(f"   Risk level: {security_result['risk_level']}")
    print(f"   Issues found: {security_result['total_issues']}")
    
    if os.getenv("DOCKER_AVAILABLE"):
        print("\n2. Docker Execution:")
        try:
            result = quick_docker_execute(script_content, timeout=30)
            
            print(f"   Execution status: {result.status.value}")
            print(f"   Execution time: {result.execution_time:.2f}s")
            
            if result.status.value == "success":
                print("   Output preview:")
                output_lines = result.output.split('\n')
                for line in output_lines[:10]:  # First 10 lines
                    print(f"     {line}")
                if len(output_lines) > 10:
                    print("     ... (output truncated)")
            else:
                print(f"   Error: {result.error}")
            
            # Result validation
            print("\n3. Result Validation:")
            validation = quick_validate_result(
                result.output, result.error, result.execution_time, "data_processing"
            )
            
            print(f"   Result valid: {validation['is_valid']}")
            print(f"   Status: {validation['status']}")
            print(f"   Confidence: {validation['confidence']}")
            
            if validation['recommendations']:
                print("   Recommendations:")
                for rec in validation['recommendations'][:2]:
                    print(f"     - {rec}")
        
        except Exception as e:
            print(f"   Docker execution failed: {str(e)}")
    
    else:
        print("\n2. Docker Execution: Skipped (Docker not available)")
        print("   Set DOCKER_AVAILABLE=1 environment variable to enable")
    
    print("\n4. Workflow Summary:")
    print("   ✓ Security validation completed")
    print("   ✓ Code analysis performed")
    if os.getenv("DOCKER_AVAILABLE"):
        print("   ✓ Docker execution completed")
        print("   ✓ Result validation performed")
    else:
        print("   - Docker execution skipped")
    print("   ✓ Comprehensive workflow demonstrated")


def main():
    """Run all Docker execution demos."""
    print("🐳 ALITA Docker Security Execution Environment - Demo")
    print("=" * 60)
    print("This demo showcases the Docker security execution capabilities")
    print("added in Commit 6 of the ALITA reproduction project.")
    print("=" * 60)
    
    try:
        # Run demos
        demo_docker_configuration()
        demo_security_validation()
        demo_result_validation()
        demo_error_analysis()
        demo_execution_monitoring()
        
        # Docker execution demo (requires Docker)
        if os.getenv("DOCKER_AVAILABLE"):
            demo_docker_execution()
        else:
            print("\n=== Docker Execution Demo ===")
            print("Docker execution demo skipped - Docker not available")
            print("To enable Docker demos:")
            print("  1. Install Docker")
            print("  2. Start Docker daemon")
            print("  3. Set environment variable: export DOCKER_AVAILABLE=1")
            print("  4. Re-run this demo")
        
        # Comprehensive workflow
        demo_comprehensive_workflow()
        
        print("\n" + "=" * 60)
        print("✅ All Docker execution demos completed successfully!")
        print("=" * 60)
        
        print("\nKey Features Demonstrated:")
        print("  🔧 Docker configuration management")
        print("  🔒 Advanced security validation")
        print("  ✅ Comprehensive result validation")
        print("  🔄 Intelligent error recovery")
        print("  📊 Real-time execution monitoring")
        if os.getenv("DOCKER_AVAILABLE"):
            print("  🐳 Secure Docker container execution")
        
        print("\nNext Steps:")
        print("  1. Try running generated scripts with Docker execution")
        print("  2. Experiment with different security profiles")
        print("  3. Test error recovery with problematic code")
        print("  4. Monitor resource usage during execution")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed with error: {str(e)}")
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()