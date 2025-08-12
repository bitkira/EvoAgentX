# ALITA Reproduction Project

This project reproduces the ALITA (Autonomous LLM-based Intelligent Tool Agent) framework using EvoAgentX components.

## Project Structure

```
alita_reproduction/
├── README.md              # This file
├── DEVELOPMENT_PLAN.md    # Development roadmap and progress
├── COMMIT_LOG.md          # Detailed commit history
├── config.py             # Configuration management
├── agents/               # ALITA agent implementations
│   ├── __init__.py
│   └── manager_agent.py  # Manager Agent - central coordinator with tool capabilities
├── actions/              # Tool Actions for ALITA
│   ├── __init__.py
│   └── code_running.py   # Code Running Action (Python execution)
├── examples/            # Usage examples and demos
│   ├── __init__.py
│   ├── basic_example.py # Basic ALITA usage
│   ├── code_execution_demo.py # Code execution demonstration
│   └── hello_world.py   # Test script for script execution
├── tests/               # Test cases
│   ├── __init__.py
│   ├── test_manager_agent.py # Manager Agent tests
│   └── test_code_running.py  # Code execution tests
├── utils/               # Utility modules
│   ├── __init__.py
│   └── interfaces.py    # Common interfaces and types
└── docs/               # Documentation
    ├── commit4_redesign.md
    └── decision_log/    # Architecture decision records
        ├── ADR-001-architecture-simplification.md
        └── ADR-002-framework-integration-strategy.md
```

## Development Progress (专家咨询优化版)

### Phase 1: Basic Framework (Commits 1-4)
- [x] Commit 1: Project initialization and basic ManagerAgent ✅ 完成
- [x] Commit 2: Basic tool calling mechanism ✅ 完成
- [ ] Commit 3: Web search tool integration (架构简化版)
- [ ] Commit 4: File operations tool integration

### Phase 2: Tool Creation (Commits 5-7)
- [ ] Commit 5: Basic script generation
- [ ] Commit 6: Docker secure execution (专家建议提前集成)
- [ ] Commit 7: Framework-based MCP storage (基于StorageHandler)

### Phase 3: Loop Mechanism (Commits 8-10)
- [ ] Commit 8: CodeReAct basic loop
- [ ] Commit 9: Multi-agent collaboration (现在引入WebAgent)
- [ ] Commit 10: Result aggregation

## Current Status: 基础工具调用完成
**Commit 1 已完成**: 基础项目结构和ManagerAgent实现  
**Commit 2 已完成**: 基础工具调用机制 - Python代码执行能力  
**专家咨询完成**: 已采纳Gemini Pro和OpenAI o3建议进行架构优化  
**下一步**: 实施Commit 3和4 - 网络搜索和文件操作工具集成

### 架构优化要点:
- **简化初期架构**: WebSearch作为ManagerAgent工具而非独立Agent
- **提前Docker集成**: Commit 6直接使用DockerInterpreterToolkit  
- **框架深度集成**: 基于EvoAgentX StorageHandler实现MCPBox
- **风险控制增强**: 成本监控、质量保证、安全加固

## Installation and Setup

```bash
# Make sure you're in the EvoAgentX root directory
cd /Users/bitkira/Documents/GitHub/EvoAgentX

# Install in development mode if not already done
pip install -e .

# Set up API keys
export OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

```python
from examples.alita_reproduction.agents import ManagerAgent
from evoagentx.models import OpenAILLMConfig

# Configure LLM
config = OpenAILLMConfig(
    model="gpt-4o-mini",
    openai_key=os.getenv("OPENAI_API_KEY"),
    stream=True
)

# Create and use ManagerAgent
manager = ManagerAgent(llm_config=config)
result = manager.process_task("Create a simple calculator in Python")
print(result)
```

## 最新功能展示 (Commit 2)

### Python代码执行能力

ALITA现在具备了安全的Python代码执行能力：

```python
from examples.alita_reproduction.agents import ManagerAgent
from examples.alita_reproduction.config import ALITAConfig

# 初始化Manager Agent
config = ALITAConfig(openai_api_key="your-api-key")
manager = ManagerAgent(llm_config=config.create_llm_config())

# 执行Python代码
result = manager.execute_code("""
import math

# 计算斐波那契数列
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("斐波那契数列前10项:")
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
""")

if result["success"]:
    print("代码执行成功!")
    print(result["output"])
else:
    print("执行失败:", result["error"])
```

### 支持的功能

1. **代码片段执行**: 执行Python代码字符串
2. **脚本文件执行**: 运行.py脚本文件 
3. **安全验证**: 代码执行前的安全检查
4. **错误处理**: 全面的错误捕获和报告
5. **导入限制**: 可配置的模块导入安全控制

### 运行演示

```bash
cd /Users/bitkira/Documents/GitHub/EvoAgentX
python examples/alita_reproduction/examples/code_execution_demo.py
```

## Contributing

This project follows the EvoAgentX contribution guidelines. Each commit represents a complete, testable increment of functionality.