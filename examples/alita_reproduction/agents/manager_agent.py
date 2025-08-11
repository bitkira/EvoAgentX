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
        
        logger.info(f"Manager Agent '{name}' initialized successfully")
    
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
            "capability_assessment": "Assess whether additional tools are needed"
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
        # Simple heuristic-based assessment (will be enhanced with LLM reasoning later)
        needs_web_search = any(keyword in task.lower() for keyword in 
                              ["search", "find", "lookup", "research", "latest", "current"])
        
        needs_code_execution = any(keyword in task.lower() for keyword in
                                  ["code", "program", "script", "calculate", "compute", "run"])
        
        needs_file_operations = any(keyword in task.lower() for keyword in
                                   ["file", "read", "write", "save", "load", "document"])
        
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