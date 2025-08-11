"""
Configuration management for ALITA reproduction project.
"""
import os
from typing import Optional
from dataclasses import dataclass
from evoagentx.models import OpenAILLMConfig


@dataclass
class ALITAConfig:
    """Configuration class for ALITA system."""
    
    # LLM Configuration
    model_name: str = "gpt-4o-mini"
    openai_api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = True
    output_response: bool = True
    
    # System Configuration
    max_iterations: int = 10
    debug: bool = True
    log_level: str = "INFO"
    
    # Storage Configuration
    mcp_box_path: str = "./mcp_box"
    tool_registry_path: str = "./tool_registry.json"
    
    def __post_init__(self):
        """Initialize configuration after creation."""
        if self.openai_api_key is None:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass openai_api_key parameter."
            )
    
    def create_llm_config(self) -> OpenAILLMConfig:
        """Create EvoAgentX LLM configuration from ALITA config."""
        return OpenAILLMConfig(
            model=self.model_name,
            openai_key=self.openai_api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=self.stream,
            output_response=self.output_response
        )


# Default configuration instance
default_config = ALITAConfig()