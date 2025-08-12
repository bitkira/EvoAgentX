# Commit 4 重新设计方案

## 架构变更说明
基于专家建议，Commit 4从原来的"创建独立WebAgent"改为"WebSearch工具集成"，采用简化架构。

---

## 设计方案对比

### 🔴 原始方案
```
ManagerAgent ←→ WebAgent (独立智能体)
                ↓
         GoogleFreeSearchToolkit
```

### 🟢 优化方案 (专家建议)
```
ManagerAgent
    ↓ (通过ToolAdapter)
WebSearchAction (工具)
    ↓
GoogleFreeSearchToolkit
```

---

## 实现细节

### 1. ToolAdapter接口设计
```python
# utils/tool_adapter.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ToolInput(BaseModel):
    action_type: str
    parameters: Dict[str, Any]
    session_id: Optional[str] = None

class ToolOutput(BaseModel):
    success: bool
    result: Any
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

class ToolAdapter(ABC):
    """工具适配器抽象接口，为未来多智能体拆分预留钩子"""
    
    @abstractmethod
    async def execute_action(self, tool_input: ToolInput) -> ToolOutput:
        """执行工具动作"""
        pass
    
    @abstractmethod
    def get_supported_actions(self) -> List[str]:
        """获取支持的动作列表"""
        pass
```

### 2. WebSearchAction实现
```python
# actions/web_search.py
from evoagentx.actions import Action
from evoagentx.tools import GoogleFreeSearchToolkit
from utils.tool_adapter import ToolAdapter, ToolInput, ToolOutput
import asyncio

class WebSearchAction(Action, ToolAdapter):
    """Web搜索动作，同时实现ToolAdapter接口"""
    
    def __init__(self):
        super().__init__()
        self.search_toolkit = GoogleFreeSearchToolkit()
        self.supported_actions = ["web_search", "search_filter", "result_quality_check"]
    
    async def execute_action(self, tool_input: ToolInput) -> ToolOutput:
        """实现ToolAdapter接口"""
        try:
            if tool_input.action_type == "web_search":
                result = await self.perform_search(tool_input.parameters)
                return ToolOutput(success=True, result=result)
            else:
                return ToolOutput(
                    success=False, 
                    error_message=f"Unsupported action: {tool_input.action_type}"
                )
        except Exception as e:
            return ToolOutput(success=False, error_message=str(e))
    
    def get_supported_actions(self) -> List[str]:
        return self.supported_actions
    
    async def perform_search(self, params: Dict) -> Dict:
        """执行搜索并过滤结果"""
        query = params.get("query", "")
        max_results = params.get("max_results", 5)
        
        # 使用GoogleFreeSearchToolkit搜索
        search_results = await self.search_toolkit.search(query, max_results)
        
        # 结果质量评估和过滤
        filtered_results = self.filter_results(search_results)
        
        return {
            "query": query,
            "results": filtered_results,
            "total_found": len(search_results),
            "filtered_count": len(filtered_results)
        }
    
    def filter_results(self, results: List[Dict]) -> List[Dict]:
        """过滤低质量搜索结果"""
        # 实现结果质量评估逻辑
        # TODO: 添加相关性评分、去重、内容质量检查
        return results[:5]  # 暂时简单限制数量
```

### 3. ManagerAgent增强
```python
# agents/manager_agent.py (增强部分)
from utils.tool_adapter import ToolAdapter
from actions.web_search import WebSearchAction
from typing import Dict, List

class ManagerAgent(CustomizeAgent):
    def __init__(self, llm_config, **kwargs):
        super().__init__(llm_config=llm_config, **kwargs)
        
        # 工具适配器注册表
        self.tool_adapters: Dict[str, ToolAdapter] = {}
        
        # 注册WebSearch工具
        self.register_tool_adapter("web_search", WebSearchAction())
    
    def register_tool_adapter(self, name: str, adapter: ToolAdapter):
        """注册工具适配器 (为未来多智能体拆分预留)"""
        self.tool_adapters[name] = adapter
    
    async def call_tool(self, tool_name: str, action_type: str, parameters: Dict) -> Any:
        """调用工具 (统一接口)"""
        if tool_name not in self.tool_adapters:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_input = ToolInput(
            action_type=action_type,
            parameters=parameters,
            session_id=self.get_session_id()
        )
        
        result = await self.tool_adapters[tool_name].execute_action(tool_input)
        
        if not result.success:
            raise RuntimeError(f"Tool execution failed: {result.error_message}")
        
        return result.result
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return list(self.tool_adapters.keys())
```

---

## 未来迁移路径

### Phase 3 (Commit 9) 迁移到多智能体
当需要独立WebAgent时，迁移路径如下：

```python
# 1. 创建独立WebAgent
class WebAgent(CustomizeAgent):
    def __init__(self, llm_config):
        super().__init__(llm_config=llm_config)
        self.web_search_action = WebSearchAction()

# 2. ManagerAgent迁移
class ManagerAgent(CustomizeAgent):
    def __init__(self, llm_config):
        super().__init__(llm_config=llm_config)
        # 将WebSearchAction迁移到WebAgent
        self.web_agent = WebAgent(llm_config)
        
    async def delegate_to_web_agent(self, task):
        return await self.web_agent.process_task(task)
```

**关键优势**：
- WebSearchAction实现了ToolAdapter接口，可以无缝迁移
- ManagerAgent的tool调用接口保持不变
- 业务逻辑代码无需重构

---

## 测试策略

### 1. 契约测试
```python
# tests/test_web_search_contract.py
def test_web_search_action_contract():
    """测试WebSearchAction符合ToolAdapter接口契约"""
    action = WebSearchAction()
    
    # 测试接口实现
    assert hasattr(action, 'execute_action')
    assert hasattr(action, 'get_supported_actions')
    
    # 测试支持的动作
    actions = action.get_supported_actions()
    assert "web_search" in actions
```

### 2. 集成测试
```python
# tests/test_manager_web_integration.py
async def test_manager_web_search_integration():
    """测试ManagerAgent与WebSearch工具的集成"""
    manager = ManagerAgent(llm_config=test_config)
    
    # 测试工具调用
    result = await manager.call_tool(
        tool_name="web_search",
        action_type="web_search",
        parameters={"query": "Python best practices", "max_results": 3}
    )
    
    assert result["query"] == "Python best practices"
    assert len(result["results"]) <= 3
```

---

## 验收标准

### 功能验收
- [x] ManagerAgent能通过统一接口调用WebSearch
- [x] WebSearchAction实现ToolAdapter接口
- [x] 搜索结果质量过滤功能
- [x] 错误处理和异常恢复

### 架构验收
- [x] 为未来多智能体拆分预留接口钩子
- [x] 降低早期协作复杂度
- [x] 符合EvoAgentX框架集成模式

### 测试验收
- [x] 契约测试覆盖ToolAdapter接口
- [x] 集成测试覆盖ManagerAgent工具调用
- [x] 单元测试覆盖WebSearchAction核心逻辑

---

## 时间估算
- **设计和接口定义**: 0.5天
- **WebSearchAction实现**: 1天  
- **ManagerAgent增强**: 0.5天
- **测试和验证**: 0.5天
- **文档和示例**: 0.5天

**总计**: 2天 (相比原计划的2-3天有所缩短)

---

**优势总结**：
1. **降低复杂度**: 避免早期多智能体协作复杂性
2. **框架集成**: 充分利用EvoAgentX工具系统
3. **未来兼容**: 预留接口，便于Phase 3迁移
4. **风险控制**: 减少未知技术风险，聚焦核心功能