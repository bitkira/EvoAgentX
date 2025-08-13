"""
Script Generating Action for ALITA reproduction.

This module provides the ScriptGeneratingAction class that enables the ALITA system
to generate Python scripts based on templates, user requirements, and code generation patterns.
"""

import logging
import os
import re
import ast
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScriptMetadata:
    """
    Metadata for generated scripts.
    """
    name: str
    description: str
    author: str = "ALITA"
    created_at: str = None
    version: str = "1.0.0"
    dependencies: List[str] = None
    tags: List[str] = None
    template_used: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


class ScriptGeneratingAction:
    """
    Script Generating Action for creating Python scripts from templates and requirements.
    
    This class provides functionality to:
    - Generate Python scripts from templates
    - Apply code generation patterns
    - Perform basic code quality checks
    - Manage script metadata
    """
    
    def __init__(
        self,
        templates_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        default_author: str = "ALITA"
    ):
        """
        Initialize the ScriptGeneratingAction.
        
        Args:
            templates_dir: Directory containing script templates
            output_dir: Directory for generated scripts output
            default_author: Default author name for script metadata
        """
        # Set up directories
        self.base_dir = Path(__file__).parent.parent
        self.templates_dir = Path(templates_dir) if templates_dir else self.base_dir / "templates"
        self.output_dir = Path(output_dir) if output_dir else self.base_dir / "generated_scripts"
        self.default_author = default_author
        
        # Ensure directories exist
        self.templates_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize template registry
        self.template_registry = {}
        self._load_templates()
        
        logger.info(f"ScriptGeneratingAction initialized")
        logger.info(f"Templates directory: {self.templates_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def _load_templates(self) -> None:
        """Load all available templates from the templates directory."""
        try:
            for template_file in self.templates_dir.glob("*.py"):
                template_name = template_file.stem
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                self.template_registry[template_name] = {
                    'path': template_file,
                    'content': template_content,
                    'metadata': self._extract_template_metadata(template_content)
                }
                logger.debug(f"Loaded template: {template_name}")
                
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
    
    def _extract_template_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from template content.
        
        Args:
            content: Template file content
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {
            'description': 'No description available',
            'variables': [],
            'dependencies': [],
            'category': 'general'
        }
        
        try:
            # Parse the AST to extract information
            tree = ast.parse(content)
            
            # Extract docstring as description
            if (ast.get_docstring(tree)):
                metadata['description'] = ast.get_docstring(tree)
            
            # Find placeholder variables (format: {{variable_name}})
            variables = re.findall(r'\{\{(\w+)\}\}', content)
            metadata['variables'] = list(set(variables))
            
            # Extract import statements to identify dependencies
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata['dependencies'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        metadata['dependencies'].append(node.module)
            
        except Exception as e:
            logger.warning(f"Error extracting template metadata: {str(e)}")
        
        return metadata
    
    def generate_script(
        self,
        template_name: str,
        script_name: str,
        requirements: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a script from a template with given requirements.
        
        Args:
            template_name: Name of the template to use
            script_name: Name for the generated script
            requirements: Dictionary containing template variable values
            output_path: Custom output path (optional)
            
        Returns:
            Dictionary containing generation result and metadata
        """
        logger.info(f"Generating script '{script_name}' from template '{template_name}'")
        
        try:
            # Check if template exists
            if template_name not in self.template_registry:
                return {
                    "success": False,
                    "error": f"Template '{template_name}' not found",
                    "available_templates": list(self.template_registry.keys())
                }
            
            template = self.template_registry[template_name]
            template_content = template['content']
            
            # Replace template variables
            generated_content = self._process_template(template_content, requirements)
            
            # Create script metadata
            metadata = ScriptMetadata(
                name=script_name,
                description=requirements.get('description', f'Generated from {template_name} template'),
                author=requirements.get('author', self.default_author),
                dependencies=template['metadata'].get('dependencies', []),
                tags=requirements.get('tags', [template_name]),
                template_used=template_name
            )
            
            # Determine output path
            if output_path:
                script_path = Path(output_path)
            else:
                script_path = self.output_dir / f"{script_name}.py"
            
            # Ensure output directory exists
            script_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata header to generated content
            header = self._generate_header(metadata)
            full_content = header + "\n\n" + generated_content
            
            # Write the generated script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Script generated successfully: {script_path}")
            
            return {
                "success": True,
                "script_path": str(script_path),
                "script_name": script_name,
                "template_used": template_name,
                "metadata": metadata.__dict__,
                "content": full_content,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error generating script: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_path": None,
                "script_name": script_name,
                "template_used": template_name
            }
    
    def _process_template(self, template_content: str, requirements: Dict[str, Any]) -> str:
        """
        Process template by replacing variables and applying transformations.
        
        Args:
            template_content: Raw template content
            requirements: Variable values and requirements
            
        Returns:
            Processed template content
        """
        processed_content = template_content
        
        # Replace template variables (format: {{variable_name}})
        for key, value in requirements.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in processed_content:
                processed_content = processed_content.replace(placeholder, str(value))
                logger.debug(f"Replaced {placeholder} with {value}")
        
        return processed_content
    
    def _generate_header(self, metadata: ScriptMetadata) -> str:
        """
        Generate script header with metadata information.
        
        Args:
            metadata: Script metadata
            
        Returns:
            Formatted header string
        """
        header_lines = [
            '"""',
            f'{metadata.description}',
            '',
            f'Generated by: {metadata.author}',
            f'Created at: {metadata.created_at}',
            f'Version: {metadata.version}',
            f'Template: {metadata.template_used}',
        ]
        
        if metadata.dependencies:
            header_lines.extend(['', 'Dependencies:'])
            for dep in metadata.dependencies:
                header_lines.append(f'  - {dep}')
        
        if metadata.tags:
            header_lines.extend(['', f'Tags: {", ".join(metadata.tags)}'])
        
        header_lines.append('"""')
        
        return '\n'.join(header_lines)
    
    def create_script_from_requirements(
        self,
        script_name: str,
        task_description: str,
        script_type: str = "general",
        additional_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a script based on task description and requirements without using templates.
        
        Args:
            script_name: Name for the generated script
            task_description: Description of what the script should do
            script_type: Type of script (data_processing, web_scraping, automation, etc.)
            additional_requirements: Additional requirements dictionary
            
        Returns:
            Dictionary containing generation result
        """
        logger.info(f"Creating script '{script_name}' from requirements")
        
        try:
            # Build requirements dictionary
            requirements = additional_requirements or {}
            requirements.update({
                'task_description': task_description,
                'script_type': script_type,
                'script_name': script_name
            })
            
            # Generate script content based on type and requirements
            generated_content = self._generate_script_content(requirements)
            
            # Create metadata
            metadata = ScriptMetadata(
                name=script_name,
                description=task_description,
                author=requirements.get('author', self.default_author),
                tags=[script_type, 'generated'],
                template_used=None
            )
            
            # Determine output path
            script_path = self.output_dir / f"{script_name}.py"
            
            # Add metadata header to generated content
            header = self._generate_header(metadata)
            full_content = header + "\n\n" + generated_content
            
            # Write the generated script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Script created successfully: {script_path}")
            
            return {
                "success": True,
                "script_path": str(script_path),
                "script_name": script_name,
                "metadata": metadata.__dict__,
                "content": full_content,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error creating script from requirements: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_path": None,
                "script_name": script_name
            }
    
    def _generate_script_content(self, requirements: Dict[str, Any]) -> str:
        """
        Generate script content based on requirements and script type.
        
        Args:
            requirements: Requirements dictionary
            
        Returns:
            Generated script content
        """
        script_type = requirements.get('script_type', 'general')
        task_description = requirements.get('task_description', '')
        
        # Basic script structure
        content_lines = [
            '#!/usr/bin/env python3',
            '',
            'import os',
            'import sys',
            'import logging',
            '',
            '# Set up logging',
            'logging.basicConfig(level=logging.INFO)',
            'logger = logging.getLogger(__name__)',
            '',
            '',
            'def main():',
            '    """',
            f'    Main function for: {task_description}',
            '    """',
            '    logger.info("Starting script execution")',
            '    ',
            '    # TODO: Implement the main functionality based on requirements',
            f'    # Task: {task_description}',
            '    # Script Type: {}'.format(script_type),
            '    ',
            '    print("Script executed successfully!")',
            '    logger.info("Script execution completed")',
            '',
            '',
            'if __name__ == "__main__":',
            '    main()',
        ]
        
        # Add specific code patterns based on script type
        if script_type == "data_processing":
            additional_lines = [
                '    # Data processing specific imports',
                '    import pandas as pd',
                '    import numpy as np',
                '    ',
                '    # TODO: Add data loading and processing logic',
                '    # data = pd.read_csv("your_file.csv")',
                '    # processed_data = data.process()',
                '    # processed_data.to_csv("output.csv")',
            ]
            # Insert after the TODO comment
            insert_index = next(i for i, line in enumerate(content_lines) if "TODO: Implement" in line)
            content_lines[insert_index+3:insert_index+3] = additional_lines
            
        elif script_type == "web_scraping":
            additional_lines = [
                '    # Web scraping specific imports',
                '    import requests',
                '    from bs4 import BeautifulSoup',
                '    ',
                '    # TODO: Add web scraping logic',
                '    # response = requests.get("https://example.com")',
                '    # soup = BeautifulSoup(response.content, "html.parser")',
                '    # data = soup.find_all("div", class_="target-class")',
            ]
            insert_index = next(i for i, line in enumerate(content_lines) if "TODO: Implement" in line)
            content_lines[insert_index+3:insert_index+3] = additional_lines
        
        return '\n'.join(content_lines)
    
    def get_available_templates(self) -> Dict[str, Any]:
        """
        Get information about all available templates.
        
        Returns:
            Dictionary containing template information
        """
        templates_info = {}
        for name, template in self.template_registry.items():
            templates_info[name] = {
                'description': template['metadata']['description'],
                'variables': template['metadata']['variables'],
                'dependencies': template['metadata']['dependencies'],
                'category': template['metadata']['category'],
                'path': str(template['path'])
            }
        
        return {
            "total_templates": len(self.template_registry),
            "templates": templates_info,
            "templates_directory": str(self.templates_dir)
        }
    
    def validate_script_syntax(self, script_path: str) -> Dict[str, Any]:
        """
        Validate the syntax of a generated script.
        
        Args:
            script_path: Path to the script file
            
        Returns:
            Dictionary containing validation results
        """
        logger.debug(f"Validating script syntax: {script_path}")
        
        try:
            if not os.path.exists(script_path):
                return {
                    "is_valid": False,
                    "error": f"Script file not found: {script_path}",
                    "suggestions": []
                }
            
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse the Python code
            try:
                ast.parse(content)
                return {
                    "is_valid": True,
                    "error": None,
                    "suggestions": []
                }
            except SyntaxError as e:
                return {
                    "is_valid": False,
                    "error": f"Syntax error: {str(e)}",
                    "line_number": e.lineno,
                    "suggestions": [
                        "Check for missing colons, brackets, or quotes",
                        "Verify proper indentation",
                        "Check for invalid Python syntax"
                    ]
                }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Error validating script: {str(e)}",
                "suggestions": ["Check file permissions and encoding"]
            }