#!/usr/bin/env python3
"""
Simple Script Generation Example for ALITA reproduction.

This example shows basic script generation functionality without requiring API keys.
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from actions.script_generating import ScriptGeneratingAction
from utils.code_quality import CodeQualityChecker, quick_check

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Main function demonstrating script generation.
    """
    print("🔧 ALITA Script Generation - Simple Example")
    print("=" * 50)
    
    try:
        # Initialize script generator
        print("\n1. Initializing Script Generator...")
        script_generator = ScriptGeneratingAction()
        
        # Show available templates
        print("\n2. Available Templates:")
        templates = script_generator.get_available_templates()
        print(f"Total templates: {templates['total_templates']}")
        
        for name, info in templates['templates'].items():
            print(f"  📄 {name}: {info['description'][:60]}...")
            if info['variables']:
                print(f"     Variables: {', '.join(info['variables'])}")
        
        # Generate a data processing script from requirements
        print("\n3. Creating Data Processing Script...")
        result = script_generator.create_script_from_requirements(
            script_name='example_data_processor',
            task_description='Process customer data and generate summary reports',
            script_type='data_processing',
            additional_requirements={
                'author': 'ALITA Example',
                'tags': ['data-processing', 'customer-analysis']
            }
        )
        
        if result['success']:
            print(f"✅ Script created: {result['script_path']}")
            
            # Validate the generated script
            print("\n4. Validating Generated Script...")
            validation = script_generator.validate_script_syntax(result['script_path'])
            
            if validation['is_valid']:
                print("✅ Script syntax is valid")
                
                # Perform quality analysis
                print("\n5. Quality Analysis...")
                with open(result['script_path'], 'r', encoding='utf-8') as f:
                    script_content = f.read()
                
                quality_result = quick_check(script_content)
                print(f"Quality Score: {quality_result['score']}/100")
                print(f"Total Issues: {quality_result['total_issues']}")
                print(f"Critical Issues: {quality_result['critical_issues']}")
                print(f"Security Risks: {quality_result['has_security_risks']}")
                
                # Show part of the generated script
                print("\n6. Generated Script Preview:")
                print("-" * 40)
                lines = script_content.split('\n')
                for i, line in enumerate(lines[:25], 1):
                    print(f"{i:2}: {line}")
                if len(lines) > 25:
                    print("... (script continues)")
                print("-" * 40)
                
            else:
                print(f"❌ Script validation failed: {validation['error']}")
        else:
            print(f"❌ Script creation failed: {result['error']}")
        
        # Generate a web scraping script using template (if available)
        if 'web_scraping' in templates['templates']:
            print("\n7. Generating Web Scraping Script from Template...")
            template_result = script_generator.generate_script(
                template_name='web_scraping',
                script_name='example_web_scraper',
                requirements={
                    'target_url': 'https://example-ecommerce.com/products',
                    'output_file': 'scraped_products.json',
                    'scraping_description': 'product information and prices',
                    'user_agent': 'ALITA Web Scraper 1.0',
                    'description': 'E-commerce product price scraper',
                    'author': 'ALITA Template System'
                }
            )
            
            if template_result['success']:
                print(f"✅ Template-based script created: {template_result['script_path']}")
                
                # Quick validation
                template_validation = script_generator.validate_script_syntax(template_result['script_path'])
                print(f"Template script validity: {'✅ Valid' if template_validation['is_valid'] else '❌ Invalid'}")
            else:
                print(f"❌ Template-based generation failed: {template_result['error']}")
        
        # Demonstrate code quality analysis
        print("\n8. Code Quality Analysis Demo...")
        
        # Analyze good code
        good_code = '''
def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def main():
    """Main function."""
    data = [1, 2, 3, 4, 5]
    avg = calculate_average(data)
    print(f"Average: {avg}")

if __name__ == "__main__":
    main()
'''
        
        good_quality = quick_check(good_code)
        print(f"Good code quality: {good_quality['score']}/100")
        
        # Analyze problematic code
        bad_code = '''
import os
def bad_func():
    x = input("Enter: ")
    os.system(x)  # Security risk
    return eval(x)  # Another risk
'''
        
        bad_quality = quick_check(bad_code)
        print(f"Problematic code quality: {bad_quality['score']}/100")
        print(f"Security risks detected: {bad_quality['has_security_risks']}")
        
        print("\n" + "=" * 50)
        print("✅ Simple script generation example completed!")
        print("=" * 50)
        
        # Show generated files
        output_dir = script_generator.output_dir
        if output_dir.exists():
            generated_files = list(output_dir.glob("*.py"))
            if generated_files:
                print(f"\n📁 Generated files in {output_dir}:")
                for file in generated_files:
                    size = file.stat().st_size
                    print(f"  - {file.name} ({size} bytes)")
        
    except Exception as e:
        logger.error(f"Example failed: {str(e)}")
        print(f"❌ Example failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()