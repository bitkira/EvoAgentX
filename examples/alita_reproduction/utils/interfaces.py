"""
ALITA项目核心抽象接口定义
基于专家建议，为框架集成和未来扩展提供统一接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from enum import Enum


# ============================================================================
# 基础数据模型
# ============================================================================

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolInput(BaseModel):
    """工具输入标准格式"""
    action_type: str
    parameters: Dict[str, Any]
    session_id: Optional[str] = None
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = {}


class ToolOutput(BaseModel):
    """工具输出标准格式"""
    success: bool
    result: Any = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = {}


class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str
    description: str
    status: TaskStatus
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = {}


# ============================================================================
# 工具适配器接口
# ============================================================================

class ToolAdapter(ABC):
    """
    工具适配器抽象接口
    为统一工具调用和未来多智能体拆分提供标准接口
    """
    
    @abstractmethod
    async def execute_action(self, tool_input: ToolInput) -> ToolOutput:
        """
        执行工具动作
        
        Args:
            tool_input: 工具输入参数
            
        Returns:
            ToolOutput: 工具执行结果
        """
        pass
    
    @abstractmethod
    def get_supported_actions(self) -> List[str]:
        """
        获取支持的动作类型列表
        
        Returns:
            List[str]: 支持的动作类型
        """
        pass
    
    @abstractmethod
    def get_tool_info(self) -> Dict[str, Any]:
        """
        获取工具信息
        
        Returns:
            Dict: 工具元信息
        """
        pass
    
    def validate_input(self, tool_input: ToolInput) -> bool:
        """
        验证输入参数
        
        Args:
            tool_input: 待验证的输入
            
        Returns:
            bool: 验证结果
        """
        return tool_input.action_type in self.get_supported_actions()


# ============================================================================
# 存储抽象接口
# ============================================================================

class StorageHandler(ABC):
    """
    存储处理器抽象接口
    为MCPBox和工具注册提供统一存储接口
    """
    
    @abstractmethod
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """
        存储数据
        
        Args:
            key: 存储键
            value: 存储值
            metadata: 元数据
            
        Returns:
            bool: 存储是否成功
        """
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """
        检索数据
        
        Args:
            key: 存储键
            
        Returns:
            Any: 检索到的数据，未找到返回None
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        删除数据
        
        Args:
            key: 存储键
            
        Returns:
            bool: 删除是否成功
        """
        pass
    
    @abstractmethod
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        列出所有键
        
        Args:
            pattern: 可选的模式匹配
            
        Returns:
            List[str]: 键列表
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 存储键
            
        Returns:
            bool: 是否存在
        """
        pass


# ============================================================================
# 执行引擎接口
# ============================================================================

class ExecutionResult(BaseModel):
    """代码执行结果"""
    success: bool
    output: str = ""
    error: str = ""
    execution_time: float = 0.0
    resource_usage: Dict[str, Any] = {}


class ExecutionEngine(ABC):
    """
    代码执行引擎抽象接口
    支持不同的执行环境 (本地、Docker、云端等)
    """
    
    @abstractmethod
    async def execute_code(
        self, 
        code: str, 
        language: str = "python",
        timeout: Optional[int] = None,
        resource_limits: Optional[Dict] = None
    ) -> ExecutionResult:
        """
        执行代码
        
        Args:
            code: 要执行的代码
            language: 编程语言
            timeout: 超时时间(秒)
            resource_limits: 资源限制配置
            
        Returns:
            ExecutionResult: 执行结果
        """
        pass
    
    @abstractmethod
    async def validate_code(self, code: str, language: str = "python") -> bool:
        """
        验证代码安全性
        
        Args:
            code: 待验证的代码
            language: 编程语言
            
        Returns:
            bool: 是否安全
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """
        获取支持的编程语言列表
        
        Returns:
            List[str]: 支持的语言
        """
        pass


# ============================================================================
# 协作协议接口
# ============================================================================

class Message(BaseModel):
    """智能体间消息"""
    sender: str
    receiver: str
    message_type: str
    content: Any
    timestamp: str
    correlation_id: Optional[str] = None


class CollaborationProtocol(ABC):
    """
    智能体协作协议接口
    为多智能体通信和协调提供标准接口
    """
    
    @abstractmethod
    async def send_message(self, message: Message) -> bool:
        """
        发送消息
        
        Args:
            message: 要发送的消息
            
        Returns:
            bool: 发送是否成功
        """
        pass
    
    @abstractmethod
    async def receive_message(self, agent_id: str, timeout: Optional[int] = None) -> Optional[Message]:
        """
        接收消息
        
        Args:
            agent_id: 智能体ID
            timeout: 超时时间
            
        Returns:
            Optional[Message]: 接收到的消息
        """
        pass
    
    @abstractmethod
    async def register_agent(self, agent_id: str, capabilities: List[str]) -> bool:
        """
        注册智能体
        
        Args:
            agent_id: 智能体ID
            capabilities: 智能体能力列表
            
        Returns:
            bool: 注册是否成功
        """
        pass


# ============================================================================
# 工具注册表接口
# ============================================================================

class ToolMetadata(BaseModel):
    """工具元数据"""
    name: str
    version: str
    description: str
    capabilities: List[str]
    author: str
    created_at: str
    usage_count: int = 0
    success_rate: float = 0.0
    performance_metrics: Dict[str, Any] = {}


class ToolRegistry(ABC):
    """
    工具注册表接口
    管理动态创建的工具和MCP组件
    """
    
    @abstractmethod
    async def register_tool(self, tool_id: str, tool_adapter: ToolAdapter, metadata: ToolMetadata) -> bool:
        """
        注册工具
        
        Args:
            tool_id: 工具唯一标识
            tool_adapter: 工具适配器实例
            metadata: 工具元数据
            
        Returns:
            bool: 注册是否成功
        """
        pass
    
    @abstractmethod
    async def get_tool(self, tool_id: str) -> Optional[ToolAdapter]:
        """
        获取工具
        
        Args:
            tool_id: 工具ID
            
        Returns:
            Optional[ToolAdapter]: 工具适配器实例
        """
        pass
    
    @abstractmethod
    async def list_tools(self, capability_filter: Optional[List[str]] = None) -> List[ToolMetadata]:
        """
        列出所有工具
        
        Args:
            capability_filter: 能力过滤条件
            
        Returns:
            List[ToolMetadata]: 工具元数据列表
        """
        pass
    
    @abstractmethod
    async def update_tool_metrics(self, tool_id: str, success: bool, execution_time: float) -> bool:
        """
        更新工具性能指标
        
        Args:
            tool_id: 工具ID
            success: 是否成功
            execution_time: 执行时间
            
        Returns:
            bool: 更新是否成功
        """
        pass


# ============================================================================
# 提示词管理接口
# ============================================================================

class PromptTemplate(BaseModel):
    """提示词模板"""
    name: str
    template: str
    variables: List[str]
    version: str
    description: str


class PromptManager(ABC):
    """
    提示词管理器接口
    中心化管理所有LLM提示词模板
    """
    
    @abstractmethod
    async def get_prompt(self, prompt_name: str, variables: Dict[str, Any]) -> str:
        """
        获取渲染后的提示词
        
        Args:
            prompt_name: 提示词名称
            variables: 模板变量
            
        Returns:
            str: 渲染后的提示词
        """
        pass
    
    @abstractmethod
    async def register_template(self, template: PromptTemplate) -> bool:
        """
        注册提示词模板
        
        Args:
            template: 提示词模板
            
        Returns:
            bool: 注册是否成功
        """
        pass
    
    @abstractmethod
    async def list_templates(self) -> List[PromptTemplate]:
        """
        列出所有模板
        
        Returns:
            List[PromptTemplate]: 模板列表
        """
        pass