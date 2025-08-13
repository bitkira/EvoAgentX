#!/usr/bin/env python3
"""
Script Generation Demo for ALITA reproduction.

This demo showcases the script generation capabilities of the ALITA system,
including template-based generation, requirements-based creation, and code quality validation.
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.manager_agent import ManagerAgent
from actions.script_generating import ScriptGeneratingAction
from utils.code_quality import CodeQualityChecker, quick_check

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_direct_script_generation():
    """
    Demonstrate direct script generation using ScriptGeneratingAction.
    """
    print("=" * 60)
    print("DEMO 1: Direct Script Generation")
    print("=" * 60)
    
    # Initialize the script generator
    script_generator = ScriptGeneratingAction()
    
    # Check available templates
    print("\n1. Checking Available Templates:")
    templates_info = script_generator.get_available_templates()
    print(f"Total templates available: {templates_info['total_templates']}")
    
    for template_name, template_info in templates_info['templates'].items():
        print(f"  - {template_name}: {template_info['description']}")
        if template_info['variables']:
            print(f"    Variables: {', '.join(template_info['variables'])}")
    
    # Generate script from template
    if templates_info['total_templates'] > 0:
        print("\n2. Generating Script from Template:")
        template_name = list(templates_info['templates'].keys())[0]
        print(f"Using template: {template_name}")
        
        requirements = {
            'input_file': 'sample_data.csv',
            'output_file': 'processed_data.csv',
            'processing_description': 'clean and analyze sales data',
            'additional_imports': '# Additional analysis libraries\nfrom datetime import datetime',
            'description': 'Sales data processing and analysis script',
            'author': 'ALITA Demo'
        }
        
        result = script_generator.generate_script(
            template_name=template_name,
            script_name='demo_sales_processor',
            requirements=requirements
        )
        
        if result['success']:
            print(f"✅ Script generated successfully: {result['script_path']}")
            print(f"Template used: {result['template_used']}")
            
            # Show first few lines of generated script
            with open(result['script_path'], 'r', encoding='utf-8') as f:
                lines = f.readlines()[:20]
                print("\nFirst 20 lines of generated script:")
                print("-" * 40)
                for i, line in enumerate(lines, 1):
                    print(f"{i:2}: {line.rstrip()}")
                print("-" * 40)
        else:
            print(f"❌ Script generation failed: {result['error']}")
    
    # Create script from requirements
    print("\n3. Creating Script from Requirements:")
    requirements_result = script_generator.create_script_from_requirements(
        script_name='demo_web_scraper',
        task_description='Scrape product prices from e-commerce websites',
        script_type='web_scraping',
        additional_requirements={
            'author': 'ALITA Demo System',
            'tags': ['web-scraping', 'price-monitoring', 'automation']
        }
    )
    
    if requirements_result['success']:
        print(f"✅ Requirements-based script created: {requirements_result['script_path']}")
        
        # Validate the generated script
        print("\n4. Validating Generated Script:")
        validation = script_generator.validate_script_syntax(requirements_result['script_path'])
        
        if validation['is_valid']:
            print("✅ Script syntax is valid")
        else:
            print(f"❌ Script syntax error: {validation['error']}")
            if validation['suggestions']:
                print("Suggestions:")
                for suggestion in validation['suggestions']:
                    print(f"  - {suggestion}")
    else:
        print(f"❌ Requirements-based script creation failed: {requirements_result['error']}")


def demo_manager_agent_integration():
    """
    Demonstrate script generation through ManagerAgent integration.
    """
    print("\n" + "=" * 60)
    print("DEMO 2: ManagerAgent Integration")
    print("=" * 60)
    
    try:
        # Initialize ManagerAgent (this might require API keys)
        manager = ManagerAgent()
        
        print("\n1. Manager Capabilities:")
        capabilities = manager.get_capabilities()
        script_capabilities = {k: v for k, v in capabilities.items() 
                             if 'script' in k.lower() or 'template' in k.lower()}
        for cap, desc in script_capabilities.items():
            print(f"  - {cap}: {desc}")
        
        print("\n2. Assessing Tool Needs:")
        test_tasks = [
            "Create a script to process CSV files and generate reports",
            "Build an automation script for web scraping",
            "Generate a data analysis script for sales data"
        ]
        
        for task in test_tasks:
            assessment = manager.assess_tool_needs(task)
            print(f"Task: '{task}'")
            print(f"  Needs additional tools: {assessment['needs_additional_tools']}")
            print(f"  Suggested tools: {assessment['suggested_tools']}")
        
        print("\n3. Creating Script via Manager:")
        manager_result = manager.create_script_from_requirements(
            script_name='manager_demo_script',
            task_description='Automate daily backup of important files',
            script_type='automation',
            additional_requirements={
                'author': 'ManagerAgent Demo',
                'tags': ['backup', 'automation', 'daily-task']
            }
        )
        
        if manager_result['success']:
            print(f"✅ Manager created script: {manager_result['script_path']}")
            
            # Get script generation status
            print("\n4. Script Generation Status:")
            status = manager.get_script_generation_status()
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            # Validate the script
            validation = manager.validate_generated_script(manager_result['script_path'])
            print(f"\n5. Script Validation: {'✅ Valid' if validation['is_valid'] else '❌ Invalid'}")
            
        else:
            print(f"❌ Manager script creation failed: {manager_result['error']}")
    
    except Exception as e:
        print(f"⚠️  Manager demo skipped due to initialization error: {str(e)}")
        print("(This is normal if OpenAI API keys are not configured)")


def demo_code_quality_analysis():
    """
    Demonstrate code quality analysis for generated scripts.
    """
    print("\n" + "=" * 60)
    print("DEMO 3: Code Quality Analysis")
    print("=" * 60)
    
    # Initialize code quality checker
    quality_checker = CodeQualityChecker()
    
    # Create sample scripts with different quality levels
    print("\n1. Analyzing High-Quality Code:")
    good_code = '''#!/usr/bin/env python3
"""
High-quality example script.

This script demonstrates good Python practices.
"""

import logging
from typing import List, Optional
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Class for processing data files."""
    
    def __init__(self, input_dir: Path):
        """Initialize processor with input directory."""
        self.input_dir = input_dir
        logger.info(f"DataProcessor initialized with {input_dir}")
    
    def process_files(self, file_extensions: List[str]) -> Optional[int]:
        """Process files with given extensions."""
        try:
            processed_count = 0
            for ext in file_extensions:
                files = list(self.input_dir.glob(f"*.{ext}"))
                processed_count += len(files)
                logger.info(f"Processed {len(files)} .{ext} files")
            
            return processed_count
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            return None

def main() -> None:
    """Main function."""
    processor = DataProcessor(Path("./data"))
    result = processor.process_files(["csv", "json", "txt"])
    
    if result is not None:
        print(f"Successfully processed {result} files")
    else:
        print("File processing failed")

if __name__ == "__main__":
    main()
'''
    
    good_result = quality_checker.analyze_code(good_code)
    print(f"Quality Score: {good_result['overall_score']}/100")
    print(f"Issues Found: {len(good_result['issues'])}")
    
    print("\n2. Analyzing Problematic Code:")
    problematic_code = '''#!/usr/bin/env python3
import os
import sys

def bad_function(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o):  # Too many parameters
    x = 123456  # Magic number
    if a:
        if b:
            if c:
                if d:  # Deep nesting
                    print("Too deep!")
    
    user_cmd = input("Enter command: ")
    os.system(user_cmd)  # Security risk
    
    try:
        result = eval(user_cmd)  # Another security risk
    except:  # Bare except
        pass
    
    return x*42  # Another magic number

bad_function(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
'''
    
    bad_result = quality_checker.analyze_code(problematic_code)
    print(f"Quality Score: {bad_result['overall_score']}/100")
    print(f"Issues Found: {len(bad_result['issues'])}")
    
    # Show issue details
    if bad_result['issues']:
        print("\nDetected Issues:")
        for issue in bad_result['issues'][:5]:  # Show first 5 issues
            print(f"  - {issue.get('type', 'unknown')} ({issue.get('severity', 'unknown')}): "
                  f"{issue.get('description', 'No description')}")
    
    # Generate quality report
    print("\n3. Quality Report:")
    report = quality_checker.get_quality_report(bad_result)
    print(report)
    
    # Quick check demo
    print("\n4. Quick Quality Check:")
    quick_result = quick_check(good_code)
    print(f"Quick check result: {quick_result}")


def demo_template_system():
    """
    Demonstrate the template system capabilities.
    """
    print("\n" + "=" * 60)
    print("DEMO 4: Template System")
    print("=" * 60)
    
    script_generator = ScriptGeneratingAction()
    
    print("\n1. Template Discovery:")
    templates = script_generator.get_available_templates()
    
    for name, info in templates['templates'].items():
        print(f"\nTemplate: {name}")
        print(f"  Description: {info['description']}")
        print(f"  Variables: {info['variables']}")
        print(f"  Dependencies: {info['dependencies']}")
        print(f"  Category: {info['category']}")
    
    print("\n2. Template Variable Analysis:")
    # Show how template variables are detected
    sample_template = '''#!/usr/bin/env python3
"""
{{description}}

Author: {{author}}
Created: {{date}}
"""

import {{main_library}}
from {{package}} import {{module}}

def {{function_name}}({{parameters}}):
    """{{function_description}}"""
    {{variable_name}} = "{{default_value}}"
    print(f"Processing: {{{variable_name}}}")
    
    return {{return_value}}

if __name__ == "__main__":
    {{function_name}}({{arguments}})
'''
    
    variables = script_generator._extract_template_metadata(sample_template)
    print(f"Detected variables in sample template: {variables['variables']}")


def run_comprehensive_demo():
    """
    Run all demonstration scenarios.
    """
    print("🚀 ALITA Script Generation System - Comprehensive Demo")
    print("=" * 70)
    
    try:
        demo_direct_script_generation()
        demo_manager_agent_integration()
        demo_code_quality_analysis()
        demo_template_system()
        
        print("\n" + "=" * 70)
        print("✅ All demonstrations completed successfully!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"Error during demo: {str(e)}")
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if we're in the right directory
    expected_files = ['agents', 'actions', 'examples', 'tests', 'templates']
    current_files = [f for f in os.listdir('.') if os.path.isdir(f)]
    
    missing_files = [f for f in expected_files if f not in current_files]
    
    if missing_files:
        print("⚠️  Warning: Some expected directories are missing:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nMake sure you're running this from the alita_reproduction directory")
        print("Current directory:", os.getcwd())
    
    # Run the demo
    run_comprehensive_demo()