"""
Manager Agent implementation for ALITA reproduction.

The Manager Agent serves as the central coordinator in the ALITA system,
responsible for:
- Task analysis and decomposition
- Decision making on tool usage
- Coordination of other agents
- Result aggregation and output generation
"""

import logging
from typing import Dict, Any, Optional, List
from evoagentx.agents import CustomizeAgent
from evoagentx.models import OpenAILLMConfig
from evoagentx.core.message import Message
from examples.alita_reproduction.actions.code_running import CodeRunningAction
from examples.alita_reproduction.actions.web_search import WebSearchAction
from examples.alita_reproduction.actions.file_operations import FileOperationsAction
from examples.alita_reproduction.actions.script_generating import ScriptGeneratingAction
from examples.alita_reproduction.actions.docker_execution import DockerExecutionAction, DockerConfig
from examples.alita_reproduction.actions.mcp_integration import MCPIntegrationAction
from examples.alita_reproduction.utils.security_validator import SecurityValidator, quick_security_check
from examples.alita_reproduction.utils.docker_config import DockerConfigManager, get_config_for_script_type
from examples.alita_reproduction.utils.result_validator import ResultValidator, quick_validate_result
from examples.alita_reproduction.utils.error_recovery import ErrorRecoverySystem
from examples.alita_reproduction.utils.execution_monitor import ExecutionMonitor, MonitoringConfig, MonitoringLevel, ExecutionPhase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManagerAgent(CustomizeAgent):
    """
    Manager Agent - Central coordinator for ALITA system.
    
    This agent serves as the "brain" of ALITA, making high-level decisions
    about task processing, tool usage, and agent coordination.
    """
    
    def __init__(
        self,
        name: str = "ALITAManager",
        description: str = "ALITA Manager Agent - Central task coordinator and decision maker",
        llm_config: Optional[OpenAILLMConfig] = None,
        **kwargs
    ):
        # Define the manager's core prompt
        manager_prompt = """You are the Manager Agent of the ALITA (Autonomous LLM-based Intelligent Tool Agent) system.

Your core responsibilities:
1. TASK ANALYSIS: Analyze incoming tasks and determine the best approach to solve them
2. DECISION MAKING: Decide whether existing capabilities are sufficient or new tools need to be created
3. COORDINATION: Direct and coordinate with other specialized agents when needed
4. RESULT SYNTHESIS: Aggregate and synthesize results from various sources into a coherent final answer

Current capabilities (will expand over time):
- Basic task analysis and response generation
- Simple problem-solving reasoning
- Clear communication and explanation

When you receive a task:
1. First, analyze what the task is asking for
2. Think about what capabilities or knowledge are needed
3. Determine if you can handle it with current capabilities
4. If not, explain what additional tools or information would be helpful
5. Provide the best possible response given current limitations

Be clear, helpful, and honest about your current capabilities and limitations.

Task to process: {task}

Please analyze this task and provide your response:"""

        super().__init__(
            name=name,
            description=description,
            prompt=manager_prompt,
            llm_config=llm_config,
            inputs=[
            {"name": "task", "type": "string", "description": "The task to process"}
        ],
            **kwargs
        )
        
        # Initialize manager state
        self.task_history: List[Dict[str, Any]] = []
        self.current_task: Optional[str] = None
        self.iteration_count: int = 0
        
        # Initialize action capabilities
        self.code_runner = CodeRunningAction()
        self.web_searcher = WebSearchAction()
        self.file_handler = FileOperationsAction()
        self.script_generator = ScriptGeneratingAction()
        
        # Initialize MCP integration (Commit 7)
        self.mcp_integration = MCPIntegrationAction()
        self.mcp_initialized = False
        
        # Initialize Docker execution capabilities (Commit 6)
        self.docker_config_manager = DockerConfigManager()
        self.security_validator = SecurityValidator()
        self.result_validator = ResultValidator()
        self.error_recovery = ErrorRecoverySystem()
        
        # Docker execution will be initialized on-demand to avoid Docker dependency issues
        self._docker_executor = None
        self._execution_monitor = None
        
        logger.info(f"Manager Agent '{name}' initialized successfully")
        logger.info("Code execution, web search, file operations, script generation, Docker security execution, and MCP integration capabilities enabled")
    
    def process_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a task using the Manager Agent.
        
        Args:
            task: The task description to process
            context: Optional context information
            
        Returns:
            str: The manager's response to the task
        """
        logger.info(f"Processing task: {task[:100]}...")
        
        self.current_task = task
        self.iteration_count += 1
        
        try:
            # Use the parent CustomizeAgent's __call__ method to process the task
            result = self(inputs={"task": task})

            # Extract the content from the Message object
            if isinstance(result, Message):
                response = result.content.content
            else:
                response = str(result)
            
            # Store task history
            task_record = {
                "iteration": self.iteration_count,
                "task": task,
                "response": response,
                "context": context or {}
            }
            self.task_history.append(task_record)
            
            logger.info("Task processed successfully")
            return response
            
        except Exception as e:
            error_msg = f"Error processing task: {str(e)}"
            logger.error(error_msg)
            return f"I encountered an error while processing your task: {error_msg}"
    
    def get_capabilities(self) -> Dict[str, str]:
        """
        Get current capabilities of the Manager Agent.
        
        Returns:
            Dict mapping capability names to descriptions
        """
        return {
            "task_analysis": "Analyze and understand task requirements",
            "basic_reasoning": "Apply logical reasoning to problems", 
            "response_generation": "Generate clear and helpful responses",
            "task_history": "Track and learn from previous tasks",
            "capability_assessment": "Assess whether additional tools are needed",
            "code_execution": "Execute Python code safely in controlled environment",
            "script_execution": "Run Python script files with security restrictions",
            "web_search": "Search web sources (Wikipedia, Google) for information",
            "information_retrieval": "Retrieve and process information from multiple sources",
            "file_operations": "Read, write, append, and manage files and directories",
            "file_management": "List files, get file info, and handle different file formats",
            "script_generation": "Generate Python scripts from templates and requirements",
            "template_management": "Manage and utilize code templates for script generation",
            "docker_execution": "Execute code safely in isolated Docker containers",
            "security_validation": "Validate code security before execution",
            "result_validation": "Validate and analyze script execution results",
            "error_recovery": "Automatically recover from execution errors",
            "execution_monitoring": "Monitor resource usage and performance during execution",
            "mcp_tool_discovery": "Discover and manage MCP tools dynamically",
            "mcp_tool_execution": "Execute MCP tools from various sources",
            "script_to_tool_conversion": "Convert generated scripts to reusable MCP tools",
            "mcp_persistence": "Persist and manage MCP tool lifecycle"
        }
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get the history of processed tasks."""
        return self.task_history.copy()
    
    def clear_history(self) -> None:
        """Clear the task history."""
        self.task_history.clear()
        self.iteration_count = 0
        logger.info("Task history cleared")
    
    def assess_tool_needs(self, task: str) -> Dict[str, Any]:
        """
        Assess whether additional tools are needed for a task.
        
        This is a simplified version - will be enhanced in later commits.
        
        Args:
            task: Task to assess
            
        Returns:
            Assessment results including whether new tools are needed
        """
        # Enhanced heuristic-based assessment for web search and other tools
        needs_web_search = any(keyword in task.lower() for keyword in 
                              ["search", "find", "lookup", "research", "latest", "current", 
                               "information about", "what is", "who is", "news", "trends"])
        
        needs_code_execution = any(keyword in task.lower() for keyword in
                                  ["code", "program", "script", "calculate", "compute", "run",
                                   "algorithm", "function", "class", "python"])
        
        needs_file_operations = any(keyword in task.lower() for keyword in
                                   ["file", "read", "write", "save", "load", "document", "csv", "json"])
        
        needs_script_generation = any(keyword in task.lower() for keyword in
                                     ["generate", "create script", "build script", "write script", 
                                      "template", "automation", "script for", "generate code"])
        
        assessment = {
            "needs_additional_tools": needs_web_search or needs_code_execution or needs_file_operations or needs_script_generation,
            "suggested_tools": [],
            "confidence": 0.7  # Simple heuristic confidence
        }
        
        if needs_web_search:
            assessment["suggested_tools"].append("web_search")
        if needs_code_execution:
            assessment["suggested_tools"].append("code_execution")
        if needs_file_operations:
            assessment["suggested_tools"].append("file_operations")
        if needs_script_generation:
            assessment["suggested_tools"].append("script_generation")
            
        return assessment
    
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Execute Python code using the integrated code runner.
        
        Args:
            code: Python code to execute
            language: Programming language (default: "python")
            
        Returns:
            Dict containing execution result and metadata
        """
        logger.info("Executing code via Manager Agent")
        
        try:
            result = self.code_runner.execute_code(code, language)
            
            # Log the execution result
            if result["success"]:
                logger.info("Code executed successfully")
            else:
                logger.warning(f"Code execution failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in code execution: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "result": None,
                "output": None,
                "error": error_msg,
                "code": code
            }
    
    def execute_script(self, file_path: str, language: str = "python") -> Dict[str, Any]:
        """
        Execute Python script file using the integrated code runner.
        
        Args:
            file_path: Path to Python script file
            language: Programming language (default: "python")
            
        Returns:
            Dict containing execution result and metadata
        """
        logger.info(f"Executing script via Manager Agent: {file_path}")
        
        try:
            result = self.code_runner.execute_script(file_path, language)
            
            # Log the execution result
            if result["success"]:
                logger.info(f"Script {file_path} executed successfully")
            else:
                logger.warning(f"Script execution failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in script execution: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "result": None,
                "output": None,
                "error": error_msg,
                "file_path": file_path
            }
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate Python code for safety before execution.
        
        Args:
            code: Python code to validate
            
        Returns:
            Dict containing validation results
        """
        logger.debug("Validating code via Manager Agent")
        
        try:
            result = self.code_runner.validate_code_safety(code)
            return result
            
        except Exception as e:
            error_msg = f"Error in code validation: {str(e)}"
            logger.error(error_msg)
            return {
                "is_safe": False,
                "violations": [error_msg],
                "code": code
            }
    
    def get_code_runner_status(self) -> Dict[str, Any]:
        """
        Get status and configuration of the code runner.
        
        Returns:
            Dict containing code runner status
        """
        try:
            return self.code_runner.get_interpreter_status()
        except Exception as e:
            logger.error(f"Error getting code runner status: {str(e)}")
            return {"error": str(e)}
    
    def search_web(self, query: str, source: str = "auto") -> Dict[str, Any]:
        """
        Search the web for information using the integrated web search action.
        
        Args:
            query: Search query string
            source: Search source ('auto', 'wikipedia', 'google', 'all')
            
        Returns:
            Dict containing search results and metadata
        """
        logger.info(f"Searching web via Manager Agent: {query}")
        
        try:
            result = self.web_searcher.search(query, source)
            
            # Log the search result
            if result["success"]:
                total_results = result.get("total_results", len(result.get("results", [])))
                logger.info(f"Web search successful: {total_results} results found")
            else:
                logger.warning(f"Web search failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in web search: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "query": query,
                "results": [],
                "error": error_msg
            }
    
    def search_wikipedia(self, query: str) -> Dict[str, Any]:
        """
        Search Wikipedia specifically.
        
        Args:
            query: Search query string
            
        Returns:
            Dict containing Wikipedia search results
        """
        logger.info(f"Searching Wikipedia via Manager Agent: {query}")
        
        try:
            result = self.web_searcher.search_wikipedia(query)
            
            if result["success"]:
                logger.info(f"Wikipedia search successful: {len(result['results'])} results found")
            else:
                logger.warning(f"Wikipedia search failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in Wikipedia search: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "source": "wikipedia",
                "query": query,
                "results": [],
                "error": error_msg
            }
    
    def search_google(self, query: str) -> Dict[str, Any]:
        """
        Search Google specifically using free search.
        
        Args:
            query: Search query string
            
        Returns:
            Dict containing Google search results
        """
        logger.info(f"Searching Google via Manager Agent: {query}")
        
        try:
            result = self.web_searcher.search_google(query)
            
            if result["success"]:
                logger.info(f"Google search successful: {len(result['results'])} results found")
            else:
                logger.warning(f"Google search failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in Google search: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "source": "google",
                "query": query,
                "results": [],
                "error": error_msg
            }
    
    def get_web_search_status(self) -> Dict[str, Any]:
        """
        Get status of web search capabilities.
        
        Returns:
            Dict containing web search status information
        """
        try:
            return self.web_searcher.get_search_status()
        except Exception as e:
            logger.error(f"Error getting web search status: {str(e)}")
            return {"error": str(e)}
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read content from a file using the integrated file operations action.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Dict containing file content and metadata
        """
        logger.info(f"Reading file via Manager Agent: {file_path}")
        
        try:
            result = self.file_handler.read_file(file_path)
            
            # Log the operation result
            if result["success"]:
                logger.info(f"File read successful: {result.get('file_size', 0)} bytes")
            else:
                logger.warning(f"File read failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in file read: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "read",
                "file_path": file_path,
                "content": None,
                "error": error_msg
            }
    
    def write_file(self, file_path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
        """
        Write content to a file using the integrated file operations action.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dict containing operation result and metadata
        """
        logger.info(f"Writing file via Manager Agent: {file_path}")
        
        try:
            result = self.file_handler.write_file(file_path, content, overwrite)
            
            # Log the operation result
            if result["success"]:
                logger.info(f"File write successful: {result.get('content_length', 0)} bytes written")
            else:
                logger.warning(f"File write failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in file write: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "write",
                "file_path": file_path,
                "error": error_msg
            }
    
    def append_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Append content to a file using the integrated file operations action.
        
        Args:
            file_path: Path to the file to append to
            content: Content to append to the file
            
        Returns:
            Dict containing operation result and metadata
        """
        logger.info(f"Appending to file via Manager Agent: {file_path}")
        
        try:
            result = self.file_handler.append_file(file_path, content)
            
            # Log the operation result
            if result["success"]:
                logger.info(f"File append successful: {result.get('content_length', 0)} bytes appended")
            else:
                logger.warning(f"File append failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in file append: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "append",
                "file_path": file_path,
                "error": error_msg
            }
    
    def list_files(self, directory_path: str, pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        List files in a directory using the integrated file operations action.
        
        Args:
            directory_path: Path to the directory to list
            pattern: Optional pattern to match files (e.g., "*.py", "*.txt")
            
        Returns:
            Dict containing list of files and metadata
        """
        logger.info(f"Listing files via Manager Agent: {directory_path}")
        
        try:
            result = self.file_handler.list_files(directory_path, pattern)
            
            # Log the operation result
            if result["success"]:
                logger.info(f"File listing successful: {result.get('total_files', 0)} files found")
            else:
                logger.warning(f"File listing failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in file listing: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "list",
                "directory_path": directory_path,
                "files": [],
                "error": error_msg
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information using the integrated file operations action.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing file information
        """
        logger.info(f"Getting file info via Manager Agent: {file_path}")
        
        try:
            result = self.file_handler.get_file_info(file_path)
            
            # Log the operation result
            if result["success"]:
                logger.info(f"File info retrieval successful: {result.get('size', 0)} bytes")
            else:
                logger.warning(f"File info retrieval failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error getting file info: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "operation": "info",
                "file_path": file_path,
                "error": error_msg
            }
    
    def get_file_operations_status(self) -> Dict[str, Any]:
        """
        Get status of file operations capabilities.
        
        Returns:
            Dict containing file operations status information
        """
        try:
            return self.file_handler.get_operations_status()
        except Exception as e:
            logger.error(f"Error getting file operations status: {str(e)}")
            return {"error": str(e)}
    
    def generate_script_from_template(
        self,
        template_name: str,
        script_name: str,
        requirements: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a script from a template using the integrated script generation action.
        
        Args:
            template_name: Name of the template to use
            script_name: Name for the generated script
            requirements: Dictionary containing template variable values
            output_path: Custom output path (optional)
            
        Returns:
            Dict containing generation result and metadata
        """
        logger.info(f"Generating script via Manager Agent: {script_name} from {template_name}")
        
        try:
            result = self.script_generator.generate_script(
                template_name, script_name, requirements, output_path
            )
            
            # Log the operation result
            if result["success"]:
                logger.info(f"Script generation successful: {result['script_path']}")
            else:
                logger.warning(f"Script generation failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in script generation: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_name": script_name,
                "template_used": template_name
            }
    
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
            Dict containing generation result
        """
        logger.info(f"Creating script from requirements via Manager Agent: {script_name}")
        
        try:
            result = self.script_generator.create_script_from_requirements(
                script_name, task_description, script_type, additional_requirements
            )
            
            # Log the operation result
            if result["success"]:
                logger.info(f"Script creation successful: {result['script_path']}")
            else:
                logger.warning(f"Script creation failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in script creation: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_name": script_name
            }
    
    def get_available_templates(self) -> Dict[str, Any]:
        """
        Get information about all available script templates.
        
        Returns:
            Dictionary containing template information
        """
        logger.info("Getting available templates via Manager Agent")
        
        try:
            result = self.script_generator.get_available_templates()
            logger.info(f"Retrieved {result['total_templates']} available templates")
            return result
            
        except Exception as e:
            error_msg = f"Error getting available templates: {str(e)}"
            logger.error(error_msg)
            return {
                "total_templates": 0,
                "templates": {},
                "error": error_msg
            }
    
    def validate_generated_script(self, script_path: str) -> Dict[str, Any]:
        """
        Validate the syntax and quality of a generated script.
        
        Args:
            script_path: Path to the script file to validate
            
        Returns:
            Dictionary containing validation results
        """
        logger.info(f"Validating generated script via Manager Agent: {script_path}")
        
        try:
            result = self.script_generator.validate_script_syntax(script_path)
            
            # Log the validation result
            if result["is_valid"]:
                logger.info("Script validation successful")
            else:
                logger.warning(f"Script validation failed: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in script validation: {str(e)}"
            logger.error(error_msg)
            return {
                "is_valid": False,
                "error": error_msg,
                "script_path": script_path
            }
    
    def get_script_generation_status(self) -> Dict[str, Any]:
        """
        Get status of script generation capabilities.
        
        Returns:
            Dict containing script generation status information
        """
        try:
            templates_info = self.script_generator.get_available_templates()
            return {
                "available_templates": templates_info['total_templates'],
                "templates_directory": templates_info['templates_directory'],
                "output_directory": str(self.script_generator.output_dir),
                "default_author": self.script_generator.default_author
            }
        except Exception as e:
            logger.error(f"Error getting script generation status: {str(e)}")
            return {"error": str(e)}
    
    # Docker Execution Methods (Commit 6)
    
    def _ensure_docker_executor(self, script_type: str = "standard") -> bool:
        """Ensure Docker executor is initialized with appropriate configuration."""
        try:
            if self._docker_executor is None:
                config = get_config_for_script_type(script_type)
                self._docker_executor = DockerExecutionAction(config)
                logger.info(f"Docker executor initialized for script type: {script_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Docker executor: {str(e)}")
            return False
    
    def _ensure_execution_monitor(self) -> bool:
        """Ensure execution monitor is initialized."""
        try:
            if self._execution_monitor is None:
                monitor_config = MonitoringConfig(level=MonitoringLevel.STANDARD)
                self._execution_monitor = ExecutionMonitor(monitor_config)
                logger.info("Execution monitor initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize execution monitor: {str(e)}")
            return False
    
    def execute_code_in_docker(
        self,
        code: str,
        script_type: str = "standard",
        timeout: Optional[int] = None,
        validate_security: bool = True,
        monitor_execution: bool = True
    ) -> Dict[str, Any]:
        """
        Execute code in Docker container with security validation and monitoring.
        
        Args:
            code: Code to execute
            script_type: Type of script for configuration selection
            timeout: Execution timeout
            validate_security: Whether to perform security validation
            monitor_execution: Whether to monitor execution
            
        Returns:
            Dict with execution results and metadata
        """
        logger.info(f"Executing code in Docker container (type: {script_type})")
        
        execution_id = None
        
        try:
            # Ensure Docker executor is available
            if not self._ensure_docker_executor(script_type):
                return {
                    "success": False,
                    "error": "Failed to initialize Docker execution environment",
                    "execution_method": "docker"
                }
            
            # Start monitoring if enabled
            if monitor_execution:
                if self._ensure_execution_monitor():
                    execution_id = self._execution_monitor.start_execution_monitoring(
                        docker_image=self._docker_executor.config.image_tag,
                        timeout=timeout or self._docker_executor.config.timeout
                    )
                    self._execution_monitor.update_execution_phase(
                        execution_id, ExecutionPhase.VALIDATION
                    )
            
            # Security validation
            security_result = None
            if validate_security:
                logger.info("Performing security validation...")
                security_result = quick_security_check(code)
                
                if execution_id:
                    self._execution_monitor.record_security_issues(
                        execution_id, security_result.get('total_issues', 0)
                    )
                
                if not security_result['is_safe'] and security_result['critical_issues'] > 0:
                    logger.warning(f"Code failed security validation: {security_result['total_issues']} issues")
                    if execution_id:
                        self._execution_monitor.stop_execution_monitoring(execution_id)
                    return {
                        "success": False,
                        "error": "Code failed security validation",
                        "security_report": security_result,
                        "execution_method": "docker"
                    }
            
            # Execute in Docker
            if execution_id:
                self._execution_monitor.update_execution_phase(
                    execution_id, ExecutionPhase.CODE_EXECUTION
                )
            
            execution_result = self._docker_executor.execute_code(
                code, timeout=timeout, validate_security=False  # Already validated above
            )
            
            # Validate results
            if execution_id:
                self._execution_monitor.update_execution_phase(
                    execution_id, ExecutionPhase.RESULT_PROCESSING
                )
            
            validation_result = quick_validate_result(
                execution_result.output,
                execution_result.error,
                execution_result.execution_time,
                script_type
            )
            
            # Record results
            if execution_id:
                self._execution_monitor.record_execution_result(
                    execution_id,
                    execution_result.status.value == "success",
                    len(execution_result.output) if execution_result.output else 0,
                    execution_result.error
                )
                
                final_metrics = self._execution_monitor.stop_execution_monitoring(execution_id)
            else:
                final_metrics = None
            
            # Prepare response
            response = {
                "success": execution_result.status.value == "success",
                "output": execution_result.output,
                "error": execution_result.error,
                "execution_time": execution_result.execution_time,
                "execution_method": "docker",
                "security_issues": len(execution_result.security_issues) if execution_result.security_issues else 0,
                "validation_result": validation_result
            }
            
            if security_result:
                response["security_report"] = security_result
            
            if final_metrics:
                response["metrics"] = {
                    "total_duration": final_metrics.get_total_duration(),
                    "phase_timings": final_metrics.phase_timings,
                    "resource_usage": {
                        "avg_cpu": sum(final_metrics.cpu_usage_percent) / len(final_metrics.cpu_usage_percent) if final_metrics.cpu_usage_percent else 0,
                        "max_memory_mb": max(final_metrics.memory_usage_mb) if final_metrics.memory_usage_mb else 0
                    }
                }
            
            logger.info(f"Docker code execution completed: success={response['success']}")
            return response
            
        except Exception as e:
            error_msg = f"Error in Docker code execution: {str(e)}"
            logger.error(error_msg)
            
            if execution_id:
                self._execution_monitor.record_execution_result(execution_id, False, 0, error_msg)
                self._execution_monitor.stop_execution_monitoring(execution_id)
            
            return {
                "success": False,
                "error": error_msg,
                "execution_method": "docker"
            }
    
    def execute_script_in_docker(
        self,
        script_path: str,
        script_type: str = "standard",
        timeout: Optional[int] = None,
        validate_security: bool = True,
        monitor_execution: bool = True
    ) -> Dict[str, Any]:
        """
        Execute script file in Docker container.
        
        Args:
            script_path: Path to script file
            script_type: Type of script
            timeout: Execution timeout
            validate_security: Whether to validate security
            monitor_execution: Whether to monitor execution
            
        Returns:
            Dict with execution results
        """
        logger.info(f"Executing script file in Docker: {script_path}")
        
        try:
            if not self._ensure_docker_executor(script_type):
                return {
                    "success": False,
                    "error": "Failed to initialize Docker execution environment",
                    "script_path": script_path
                }
            
            execution_result = self._docker_executor.execute_script_file(
                script_path, timeout=timeout, validate_security=validate_security
            )
            
            # Validate results
            validation_result = quick_validate_result(
                execution_result.output,
                execution_result.error,
                execution_result.execution_time,
                script_type
            )
            
            response = {
                "success": execution_result.status.value == "success",
                "output": execution_result.output,
                "error": execution_result.error,
                "execution_time": execution_result.execution_time,
                "script_path": script_path,
                "execution_method": "docker",
                "security_issues": len(execution_result.security_issues) if execution_result.security_issues else 0,
                "validation_result": validation_result
            }
            
            logger.info(f"Docker script execution completed: success={response['success']}")
            return response
            
        except Exception as e:
            error_msg = f"Error in Docker script execution: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_path": script_path,
                "execution_method": "docker"
            }
    
    def execute_generated_script_securely(
        self,
        script_path: str,
        script_type: str = "standard",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a generated script with maximum security validation.
        
        Args:
            script_path: Path to generated script
            script_type: Type of script
            timeout: Execution timeout
            
        Returns:
            Dict with execution results
        """
        logger.info(f"Executing generated script securely: {script_path}")
        
        try:
            if not self._ensure_docker_executor(script_type):
                return {
                    "success": False,
                    "error": "Failed to initialize Docker execution environment",
                    "script_path": script_path
                }
            
            execution_result = self._docker_executor.execute_generated_script(
                script_path, timeout=timeout, enhanced_security=True
            )
            
            # Enhanced result validation for generated scripts
            validation_result = quick_validate_result(
                execution_result.output,
                execution_result.error,
                execution_result.execution_time,
                script_type
            )
            
            response = {
                "success": execution_result.status.value == "success",
                "output": execution_result.output,
                "error": execution_result.error,
                "execution_time": execution_result.execution_time,
                "script_path": script_path,
                "execution_method": "docker_secure",
                "security_issues": len(execution_result.security_issues) if execution_result.security_issues else 0,
                "validation_result": validation_result,
                "enhanced_security": True
            }
            
            logger.info(f"Secure script execution completed: success={response['success']}")
            return response
            
        except Exception as e:
            error_msg = f"Error in secure script execution: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_path": script_path,
                "execution_method": "docker_secure"
            }
    
    def validate_code_security(self, code: str) -> Dict[str, Any]:
        """
        Validate code security using the security validator.
        
        Args:
            code: Code to validate
            
        Returns:
            Dict with security validation results
        """
        logger.info("Validating code security via Manager Agent")
        
        try:
            return quick_security_check(code)
        except Exception as e:
            error_msg = f"Error in security validation: {str(e)}"
            logger.error(error_msg)
            return {
                "is_safe": False,
                "risk_level": "critical",
                "total_issues": 1,
                "critical_issues": 1,
                "summary": f"Validation failed: {error_msg}"
            }
    
    def validate_docker_environment(self) -> Dict[str, Any]:
        """
        Validate Docker execution environment.
        
        Returns:
            Dict with environment validation results
        """
        logger.info("Validating Docker environment via Manager Agent")
        
        try:
            if not self._ensure_docker_executor():
                return {
                    "valid": False,
                    "error": "Failed to initialize Docker executor"
                }
            
            return self._docker_executor.validate_execution_environment()
            
        except Exception as e:
            error_msg = f"Error validating Docker environment: {str(e)}"
            logger.error(error_msg)
            return {
                "valid": False,
                "error": error_msg
            }
    
    def get_docker_execution_statistics(self) -> Dict[str, Any]:
        """
        Get Docker execution statistics.
        
        Returns:
            Dict with execution statistics
        """
        try:
            if self._docker_executor:
                return self._docker_executor.get_execution_statistics()
            else:
                return {"total_executions": 0, "message": "Docker executor not initialized"}
        except Exception as e:
            logger.error(f"Error getting Docker statistics: {str(e)}")
            return {"error": str(e)}
    
    # MCP Integration Methods (Commit 7)
    
    def _ensure_mcp_initialized(self) -> bool:
        """Ensure MCP connections are initialized."""
        try:
            if not self.mcp_initialized:
                result = self.mcp_integration.initialize_external_mcp_connection()
                self.mcp_initialized = result["success"]
                if self.mcp_initialized:
                    logger.info("MCP integration initialized successfully")
                else:
                    logger.warning(f"MCP initialization failed: {result.get('error', 'Unknown error')}")
            return self.mcp_initialized
        except Exception as e:
            logger.error(f"Error initializing MCP: {str(e)}")
            return False
    
    def discover_mcp_tools(self) -> Dict[str, Any]:
        """
        Discover all available MCP tools.
        
        Returns:
            Dictionary containing discovered MCP tools
        """
        logger.info("Discovering MCP tools via Manager Agent")
        
        try:
            self._ensure_mcp_initialized()
            result = self.mcp_integration.discover_available_tools()
            
            total_tools = result.get("total_tools", 0)
            logger.info(f"Discovered {total_tools} MCP tools")
            
            return result
            
        except Exception as e:
            error_msg = f"Error discovering MCP tools: {str(e)}"
            logger.error(error_msg)
            return {
                "alita_tools": {"tools_count": 0, "tools": {}},
                "external_tools": [],
                "total_tools": 0,
                "error": error_msg
            }
    
    def find_suitable_mcp_tool(self, task_description: str) -> Dict[str, Any]:
        """
        Find suitable MCP tools for a task.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Dictionary containing suitable tools and recommendations
        """
        logger.info(f"Finding suitable MCP tools for task: {task_description[:100]}...")
        
        try:
            self._ensure_mcp_initialized()
            result = self.mcp_integration.find_suitable_tool(task_description)
            
            suitable_count = len(result.get("suitable_tools", []))
            logger.info(f"Found {suitable_count} suitable MCP tools")
            
            return result
            
        except Exception as e:
            error_msg = f"Error finding suitable MCP tools: {str(e)}"
            logger.error(error_msg)
            return {
                "suitable_tools": [],
                "total_matches": 0,
                "recommendation": "Error occurred during tool search",
                "needs_new_tool": True,
                "error": error_msg
            }
    
    def execute_mcp_tool(
        self,
        tool_name: str,
        tool_args: Optional[Dict[str, Any]] = None,
        source: str = "auto"
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments to pass to the tool
            source: Tool source ("alita", "external", "auto")
            
        Returns:
            Tool execution result
        """
        logger.info(f"Executing MCP tool via Manager Agent: {tool_name}")
        
        try:
            self._ensure_mcp_initialized()
            result = self.mcp_integration.execute_mcp_tool(tool_name, tool_args, source)
            
            if result["success"]:
                logger.info(f"MCP tool execution successful: {tool_name}")
            else:
                logger.warning(f"MCP tool execution failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error executing MCP tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "tool_name": tool_name
            }
    
    def register_script_as_mcp_tool(
        self,
        script_path: str,
        tool_name: Optional[str] = None,
        tool_description: Optional[str] = None,
        auto_register: bool = None
    ) -> Dict[str, Any]:
        """
        Register a generated script as an MCP tool.
        
        Args:
            script_path: Path to the script to register
            tool_name: Custom tool name
            tool_description: Custom tool description
            auto_register: Whether to auto-register (uses config if None)
            
        Returns:
            Registration result dictionary
        """
        logger.info(f"Registering script as MCP tool via Manager Agent: {script_path}")
        
        try:
            # Check auto-registration setting
            if auto_register is None:
                auto_register = self.mcp_integration.config_manager.get_setting(
                    "auto_register_generated_scripts", True
                )
            
            if not auto_register:
                return {
                    "success": False,
                    "error": "Auto-registration is disabled",
                    "script_path": script_path
                }
            
            self._ensure_mcp_initialized()
            result = self.mcp_integration.register_script_as_mcp_tool(
                script_path, tool_name, tool_description
            )
            
            if result["success"]:
                logger.info(f"Script registered as MCP tool: {result['tool_name']}")
            else:
                logger.warning(f"Script registration failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error registering script as MCP tool: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script_path": script_path
            }
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """
        Get MCP integration status.
        
        Returns:
            Dictionary containing MCP status information
        """
        logger.info("Getting MCP status via Manager Agent")
        
        try:
            return self.mcp_integration.get_mcp_status()
        except Exception as e:
            error_msg = f"Error getting MCP status: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def process_task_with_mcp_workflow(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a task using the enhanced MCP workflow.
        
        This method implements the new workflow:
        Task -> Query MCP Tools -> Use Existing OR Generate New -> Register -> Execute
        
        Args:
            task: Task description
            context: Optional context information
            
        Returns:
            Enhanced task processing result
        """
        logger.info(f"Processing task with MCP workflow: {task[:100]}...")
        
        try:
            # Step 1: Find suitable existing MCP tools
            tool_search = self.find_suitable_mcp_tool(task)
            
            # Step 2: Try to use existing tools first
            if not tool_search.get("needs_new_tool", True) and tool_search.get("suitable_tools"):
                best_tool = tool_search["suitable_tools"][0]
                logger.info(f"Found suitable existing tool: {best_tool['name']}")
                
                # Attempt to use the existing tool
                tool_result = self.execute_mcp_tool(best_tool["name"], {"input": task})
                
                if tool_result["success"]:
                    return f"Task completed using existing MCP tool '{best_tool['name']}':\n{tool_result.get('result', tool_result.get('output', 'Success'))}"
                else:
                    logger.warning(f"Existing tool failed, falling back to generation: {tool_result.get('error')}")
            
            # Step 3: No suitable tool found, generate new script
            logger.info("No suitable existing tools found, generating new script")
            
            # Determine script type based on task
            script_type = self._infer_script_type(task)
            script_name = self._generate_script_name(task)
            
            # Generate script
            generation_result = self.create_script_from_requirements(
                script_name=script_name,
                task_description=task,
                script_type=script_type
            )
            
            if not generation_result["success"]:
                return f"Failed to generate script for task: {generation_result.get('error')}"
            
            script_path = generation_result["script_path"]
            logger.info(f"Generated script: {script_path}")
            
            # Step 4: Register script as MCP tool for future use
            registration_result = self.register_script_as_mcp_tool(
                script_path=script_path,
                tool_name=script_name,
                tool_description=f"Generated tool for: {task[:100]}"
            )
            
            if registration_result["success"]:
                logger.info(f"Script registered as MCP tool: {registration_result['tool_name']}")
            else:
                logger.warning(f"Script registration failed: {registration_result.get('error')}")
            
            # Step 5: Execute the generated script
            execution_result = self.execute_generated_script_securely(
                script_path=script_path,
                script_type=script_type
            )
            
            # Format response
            response_parts = [
                f"Task processed using generated script '{script_name}':",
                f"Script Location: {script_path}"
            ]
            
            if registration_result["success"]:
                response_parts.append(f"✓ Registered as MCP tool for future use")
            
            if execution_result["success"]:
                response_parts.append(f"✓ Execution successful")
                if execution_result.get("output"):
                    response_parts.append(f"Output:\n{execution_result['output']}")
            else:
                response_parts.append(f"✗ Execution failed: {execution_result.get('error')}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            error_msg = f"Error in MCP workflow processing: {str(e)}"
            logger.error(error_msg)
            return f"Task processing failed: {error_msg}"
    
    def _infer_script_type(self, task: str) -> str:
        """Infer script type from task description."""
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ["data", "csv", "json", "process", "analyze"]):
            return "data_processing"
        elif any(keyword in task_lower for keyword in ["web", "scrape", "crawl", "download", "fetch"]):
            return "web_scraping"
        elif any(keyword in task_lower for keyword in ["api", "request", "client", "service"]):
            return "api_client"
        else:
            return "general"
    
    def _generate_script_name(self, task: str) -> str:
        """Generate a script name from task description."""
        import re
        
        # Extract key words from task
        words = re.findall(r'\b[a-zA-Z]+\b', task.lower())
        key_words = [word for word in words if len(word) > 3 and word not in {
            'this', 'that', 'with', 'from', 'they', 'were', 'been', 'have', 'will', 'would', 'could', 'should'
        }][:3]  # Take first 3 meaningful words
        
        if key_words:
            script_name = "_".join(key_words)
        else:
            script_name = f"generated_script_{self.iteration_count}"
        
        return script_name
    
    def cleanup_mcp_tools(self, days: int = 30) -> Dict[str, Any]:
        """
        Clean up old, unused MCP tools.
        
        Args:
            days: Remove tools not used in this many days
            
        Returns:
            Cleanup result dictionary
        """
        logger.info(f"Cleaning up MCP tools via Manager Agent (older than {days} days)")
        
        try:
            return self.mcp_integration.cleanup_old_tools(days)
        except Exception as e:
            error_msg = f"Error cleaning up MCP tools: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "days_threshold": days
            }
    
    def disconnect_mcp(self) -> None:
        """Disconnect from MCP connections."""
        try:
            self.mcp_integration.disconnect_mcp_connections()
            self.mcp_initialized = False
            logger.info("MCP connections disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting MCP: {str(e)}")