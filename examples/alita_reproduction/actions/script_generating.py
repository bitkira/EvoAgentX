"""
Script Generating Action for ALITA reproduction - Simplified LLM-based approach.

This module provides a simplified ScriptGeneratingAction that uses LLM to directly
generate Python scripts based on task descriptions, eliminating the need for complex
template systems.
"""

import ast
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from evoagentx.agents import CustomizeAgent
from evoagentx.models import OpenAILLMConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScriptMetadata:
    """Metadata for generated scripts."""
    name: str
    description: str
    author: str = "ALITA"
    created_at: str = None
    version: str = "1.0.0"
    dependencies: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


class ScriptGeneratingAction:
    """
    Simplified Script Generating Action using LLM for direct code generation.
    
    This class provides functionality to:
    - Generate Python scripts directly from task descriptions using LLM
    - Validate script syntax and security
    - Perform automated fixes when possible
    - Manage script metadata and registration
    """
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        default_author: str = "ALITA",
        llm_model: str = "gpt-4",
        max_retries: int = 3
    ):
        """
        Initialize the ScriptGeneratingAction.
        
        Args:
            output_dir: Directory for generated scripts output
            default_author: Default author name for script metadata
            llm_model: LLM model to use for code generation
            max_retries: Maximum number of generation retries
        """
        # Set up directories
        self.base_dir = Path(__file__).parent.parent
        self.output_dir = Path(output_dir) if output_dir else self.base_dir / "generated_scripts"
        self.default_author = default_author
        self.max_retries = max_retries
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize LLM agent for code generation
        # Create LLM config for the script generator
        llm_config = OpenAILLMConfig(
            model=llm_model,
            temperature=0.1,  # Low temperature for more consistent code generation
            max_tokens=4000
        )
        
        self.code_agent = CustomizeAgent(
            name="ScriptGenerator",
            description="Expert Python Developer for generating high-quality scripts",
            role="Expert Python Developer",
            goal="Generate high-quality, secure Python scripts based on task descriptions",
            backstory="""You are an expert Python developer specializing in creating clean, 
            efficient, and secure Python scripts. You follow best practices including proper 
            error handling, logging, documentation, and security considerations.""",
            prompt="You are an expert Python developer. Generate clean, secure Python scripts based on the given task description.",
            llm_config=llm_config,
            verbose=True
        )
        
        logger.info(f"ScriptGeneratingAction initialized with LLM-based generation")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Using LLM model: {llm_model}")
    
    def generate_script(
        self,
        task_description: str,
        script_name: str,
        requirements: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a Python script using LLM based on task description.
        
        Args:
            task_description: Detailed description of what the script should do
            script_name: Name for the generated script
            requirements: Additional requirements and constraints
            output_path: Custom output path (optional)
            
        Returns:
            Dictionary containing generation result and metadata
        """
        logger.info(f"Generating script '{script_name}' using LLM")
        
        try:
            # Prepare requirements
            requirements = requirements or {}
            
            # Generate script content using LLM
            for attempt in range(self.max_retries):
                logger.info(f"Generation attempt {attempt + 1}/{self.max_retries}")
                
                script_content = self._generate_with_llm(task_description, requirements, attempt)
                
                if script_content:
                    # Validate the generated script
                    validation_result = self._validate_script_content(script_content)
                    
                    if validation_result["is_valid"]:
                        # Script is valid, proceed to save
                        return self._save_script(
                            script_content, script_name, task_description, 
                            requirements, output_path
                        )
                    else:
                        # Try to fix the script
                        fixed_content = self._attempt_fix(script_content, validation_result)
                        if fixed_content:
                            final_validation = self._validate_script_content(fixed_content)
                            if final_validation["is_valid"]:
                                return self._save_script(
                                    fixed_content, script_name, task_description,
                                    requirements, output_path
                                )
                        
                        logger.warning(f"Attempt {attempt + 1} failed validation: {validation_result['error']}")
                else:
                    logger.warning(f"Attempt {attempt + 1} failed to generate content")
            
            # All attempts failed
            return {
                "success": False,
                "error": f"Failed to generate valid script after {self.max_retries} attempts",
                "script_name": script_name
            }
            
        except Exception as e:
            error_msg = f"Error generating script: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_name": script_name
            }
    
    def _generate_with_llm(
        self, 
        task_description: str, 
        requirements: Dict[str, Any], 
        attempt: int
    ) -> Optional[str]:
        """
        Generate script content using LLM.
        
        Args:
            task_description: Task description
            requirements: Additional requirements
            attempt: Current attempt number
            
        Returns:
            Generated script content or None if failed
        """
        try:
            # Build the prompt for LLM
            prompt = self._build_generation_prompt(task_description, requirements, attempt)
            
            # Get response from LLM
            response = self.code_agent(inputs={"task": prompt})
            
            # Extract Python code from response
            script_content = self._extract_code_from_response(response)
            
            return script_content
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return None
    
    def _build_generation_prompt(
        self, 
        task_description: str, 
        requirements: Dict[str, Any], 
        attempt: int
    ) -> str:
        """Build the prompt for LLM code generation."""
        
        prompt_parts = [
            "Generate a complete, production-ready Python script that accomplishes the following task:",
            f"TASK: {task_description}",
            "",
            "REQUIREMENTS:",
        ]
        
        # Add specific requirements
        if requirements.get('input_format'):
            prompt_parts.append(f"- Input format: {requirements['input_format']}")
        if requirements.get('output_format'):
            prompt_parts.append(f"- Output format: {requirements['output_format']}")
        if requirements.get('libraries'):
            prompt_parts.append(f"- Use these libraries: {', '.join(requirements['libraries'])}")
        if requirements.get('constraints'):
            prompt_parts.append(f"- Constraints: {requirements['constraints']}")
        
        # Add general requirements
        prompt_parts.extend([
            "- Include proper error handling and logging",
            "- Add comprehensive docstrings and comments",
            "- Follow Python best practices and PEP 8",
            "- Make the script robust and production-ready",
            "- Include a main() function and if __name__ == '__main__' guard",
            "- Handle edge cases and provide helpful error messages",
            ""
        ])
        
        # Add attempt-specific guidance
        if attempt > 0:
            prompt_parts.extend([
                f"NOTE: This is attempt {attempt + 1}. Previous attempts had issues.",
                "Please ensure the code is syntactically correct and follows best practices.",
                ""
            ])
        
        prompt_parts.extend([
            "OUTPUT FORMAT:",
            "Provide ONLY the Python code, no explanations or markdown formatting.",
            "Start directly with the Python code (#!/usr/bin/env python3 or imports).",
            ""
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_code_from_response(self, response) -> Optional[str]:
        """
        Extract Python code from LLM response.
        
        Args:
            response: LLM response (Message object or string)
            
        Returns:
            Extracted Python code or None
        """
        try:
            # Extract text content from response object
            if hasattr(response, 'content'):
                code = response.content
            elif hasattr(response, 'text'):
                code = response.text
            elif hasattr(response, 'output'):
                code = response.output
            elif hasattr(response, 'result'):
                code = response.result  
            elif hasattr(response, '__dict__'):
                # Try to find text content in the response object
                attrs = ['scriptgenerator_action', 'response', 'message', 'answer']
                for attr in attrs:
                    if hasattr(response, attr):
                        code = getattr(response, attr)
                        break
                else:
                    # If no known attribute found, convert to string
                    code = str(response)
            elif isinstance(response, str):
                code = response
            else:
                code = str(response)
            
            # Remove common markdown code block markers
            code = code.strip()
            
            # Remove markdown code blocks
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            
            if code.endswith("```"):
                code = code[:-3]
            
            # Clean up the code
            code = code.strip()
            
            # Basic validation - should start with typical Python patterns
            if (code.startswith(("#!/usr/bin/env python", "import ", "from ", '"""', "def ", "class ")) or
                "def main(" in code):
                return code
            else:
                logger.warning("Generated code doesn't match expected Python patterns")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting code from response: {str(e)}")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response attributes: {dir(response) if hasattr(response, '__dict__') else 'No __dict__'}")
            if hasattr(response, '__dict__'):
                logger.debug(f"Response dict: {response.__dict__}")
            return None
    
    def _validate_script_content(self, content: str) -> Dict[str, Any]:
        """
        Validate script content for syntax and basic security.
        
        Args:
            content: Script content to validate
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Syntax validation
            try:
                ast.parse(content)
            except SyntaxError as e:
                return {
                    "is_valid": False,
                    "error": f"Syntax error: {str(e)}",
                    "error_type": "syntax",
                    "line_number": getattr(e, 'lineno', None)
                }
            
            # Basic security checks
            security_issues = self._check_security(content)
            if security_issues:
                return {
                    "is_valid": False,
                    "error": f"Security issues found: {', '.join(security_issues)}",
                    "error_type": "security",
                    "security_issues": security_issues
                }
            
            # Check for required patterns
            if "def main(" not in content:
                return {
                    "is_valid": False,
                    "error": "Script must contain a main() function",
                    "error_type": "structure"
                }
            
            return {
                "is_valid": True,
                "error": None
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Validation error: {str(e)}",
                "error_type": "unknown"
            }
    
    def _check_security(self, content: str) -> List[str]:
        """
        Check for basic security issues in the script.
        
        Args:
            content: Script content
            
        Returns:
            List of security issues found
        """
        issues = []
        
        # Check for dangerous imports
        dangerous_imports = [
            "subprocess", "os.system", "eval", "exec", "compile",
            "__import__", "open"  # open can be risky but might be necessary
        ]
        
        # Parse AST to check imports and function calls
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Check dangerous imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_names = []
                    if isinstance(node, ast.Import):
                        module_names = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        module_names = [node.module]
                    
                    for module in module_names:
                        if any(dangerous in module for dangerous in dangerous_imports[:5]):  # Exclude 'open'
                            issues.append(f"Potentially dangerous import: {module}")
                
                # Check for eval/exec calls
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec", "__import__"]:
                        issues.append(f"Dangerous function call: {node.func.id}")
        
        except Exception as e:
            logger.warning(f"Security check failed: {str(e)}")
            issues.append("Could not perform complete security analysis")
        
        return issues
    
    def _attempt_fix(self, content: str, validation_result: Dict[str, Any]) -> Optional[str]:
        """
        Attempt to automatically fix common issues in generated script.
        
        Args:
            content: Script content with issues
            validation_result: Validation result with error details
            
        Returns:
            Fixed content or None if unable to fix
        """
        try:
            error_type = validation_result.get("error_type")
            
            if error_type == "structure":
                # Try to add missing main function
                if "def main(" not in content:
                    content += "\n\ndef main():\n    \"\"\"Main function.\"\"\"\n    pass\n\nif __name__ == '__main__':\n    main()\n"
                    return content
            
            elif error_type == "syntax":
                # For syntax errors, we'll ask LLM to fix it
                fix_prompt = f"""
                Fix the following Python script that has a syntax error:
                
                ERROR: {validation_result['error']}
                
                SCRIPT:
                {content}
                
                Please provide the corrected Python script with the syntax error fixed.
                Return ONLY the corrected Python code, no explanations.
                """
                
                try:
                    fixed_response = self.code_agent(inputs={"task": fix_prompt})
                    fixed_content = self._extract_code_from_response(fixed_response)
                    return fixed_content
                except Exception as e:
                    logger.error(f"Failed to fix syntax error with LLM: {str(e)}")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error attempting to fix script: {str(e)}")
            return None
    
    def _save_script(
        self,
        content: str,
        script_name: str,
        task_description: str,
        requirements: Dict[str, Any],
        output_path: Optional[str]
    ) -> Dict[str, Any]:
        """
        Save the generated script to file.
        
        Args:
            content: Script content
            script_name: Script name
            task_description: Task description
            requirements: Requirements dict
            output_path: Custom output path
            
        Returns:
            Save result dictionary
        """
        try:
            # Create metadata
            metadata = ScriptMetadata(
                name=script_name,
                description=task_description,
                author=requirements.get('author', self.default_author),
                tags=['llm-generated', 'alita']
            )
            
            # Determine output path
            if output_path:
                script_path = Path(output_path)
            else:
                script_path = self.output_dir / f"{script_name}.py"
            
            # Ensure output directory exists
            script_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata header
            header = self._generate_header(metadata)
            full_content = header + "\n\n" + content
            
            # Write the script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Script saved successfully: {script_path}")
            
            return {
                "success": True,
                "script_path": str(script_path),
                "script_name": script_name,
                "metadata": metadata.__dict__,
                "content": full_content,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error saving script: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_name": script_name
            }
    
    def _generate_header(self, metadata: ScriptMetadata) -> str:
        """Generate script header with metadata."""
        header_lines = [
            '"""',
            f'{metadata.description}',
            '',
            f'Generated by: {metadata.author}',
            f'Created at: {metadata.created_at}',
            f'Version: {metadata.version}',
        ]
        
        if metadata.dependencies:
            header_lines.extend(['', 'Dependencies:'])
            for dep in metadata.dependencies:
                header_lines.append(f'  - {dep}')
        
        if metadata.tags:
            header_lines.extend(['', f'Tags: {", ".join(metadata.tags)}'])
        
        header_lines.append('"""')
        return '\n'.join(header_lines)
    
    def test_script(self, script_path: str) -> Dict[str, Any]:
        """
        Test the generated script by running it in a controlled environment.
        
        Args:
            script_path: Path to the script to test
            
        Returns:
            Test result dictionary
        """
        logger.info(f"Testing script: {script_path}")
        
        try:
            if not os.path.exists(script_path):
                return {
                    "success": False,
                    "error": f"Script file not found: {script_path}"
                }
            
            # Run the script with a timeout
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": None if result.returncode == 0 else "Script execution failed"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Script execution timeout (30 seconds)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error testing script: {str(e)}"
            }
    
    def list_generated_scripts(self) -> Dict[str, Any]:
        """
        List all generated scripts in the output directory.
        
        Returns:
            Dictionary containing scripts information
        """
        try:
            scripts = []
            for script_file in self.output_dir.glob("*.py"):
                try:
                    # Get basic file info
                    stat = script_file.stat()
                    
                    # Try to extract metadata from header
                    with open(script_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    scripts.append({
                        "name": script_file.stem,
                        "path": str(script_file),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "has_main": "def main(" in content
                    })
                    
                except Exception as e:
                    logger.warning(f"Error reading script {script_file}: {str(e)}")
            
            return {
                "total_scripts": len(scripts),
                "scripts": scripts,
                "output_directory": str(self.output_dir)
            }
            
        except Exception as e:
            return {
                "total_scripts": 0,
                "scripts": [],
                "error": f"Error listing scripts: {str(e)}"
            }