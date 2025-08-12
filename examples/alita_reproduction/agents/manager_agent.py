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
from ..actions.code_running import CodeRunningAction
from ..actions.web_search import WebSearchAction
from ..actions.file_operations import FileOperationsAction

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
        
        logger.info(f"Manager Agent '{name}' initialized successfully")
        logger.info("Code execution, web search, and file operations capabilities enabled")
    
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
            result = self(task=task)
            
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
            "file_management": "List files, get file info, and handle different file formats"
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
        
        assessment = {
            "needs_additional_tools": needs_web_search or needs_code_execution or needs_file_operations,
            "suggested_tools": [],
            "confidence": 0.7  # Simple heuristic confidence
        }
        
        if needs_web_search:
            assessment["suggested_tools"].append("web_search")
        if needs_code_execution:
            assessment["suggested_tools"].append("code_execution")
        if needs_file_operations:
            assessment["suggested_tools"].append("file_operations")
            
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