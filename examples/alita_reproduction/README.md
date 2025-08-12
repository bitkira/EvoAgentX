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
│   ├── code_running.py   # Code Running Action (Python execution)
│   ├── web_search.py     # Web Search Action (Wikipedia + Google)
│   └── file_operations.py # File Operations Action (read/write/append)
├── examples/            # Usage examples and demos
│   ├── __init__.py
│   ├── basic_example.py # Basic ALITA usage
│   ├── code_execution_demo.py # Code execution demonstration
│   ├── web_search_demo.py # Web search demonstration
│   ├── file_operations_demo.py # File operations demonstration
│   └── hello_world.py   # Test script for script execution
├── tests/               # Test cases
│   ├── __init__.py
│   ├── test_manager_agent.py # Manager Agent tests
│   ├── test_code_running.py  # Code execution tests
│   ├── test_web_search.py    # Web search tests
│   └── test_file_operations.py # File operations tests
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

### Phase 1: Basic Framework (Commits 1-4) ✅ 完成
- [x] Commit 1: Project initialization and basic ManagerAgent ✅ 完成
- [x] Commit 2: Basic tool calling mechanism ✅ 完成 
- [x] Commit 3: Web search tool integration ✅ 完成
- [x] Commit 4: File operations tool integration ✅ 完成

### Phase 2: Tool Creation (Commits 5-7)
- [ ] Commit 5: Basic script generation
- [ ] Commit 6: Docker secure execution (专家建议提前集成)
- [ ] Commit 7: Framework-based MCP storage (基于StorageHandler)

### Phase 3: Loop Mechanism (Commits 8-10)
- [ ] Commit 8: CodeReAct basic loop
- [ ] Commit 9: Multi-agent collaboration (现在引入WebAgent)
- [ ] Commit 10: Result aggregation

## Current Status: 里程碑1完成 ✅
**Commit 1 已完成**: 基础项目结构和ManagerAgent实现  
**Commit 2 已完成**: 基础工具调用机制 - Python代码执行能力  
**Commit 3 已完成**: 网络搜索工具集成 - Wikipedia和Google搜索能力  
**Commit 4 已完成**: 文件操作工具集成 - 完整的文件读写能力  
**里程碑1完成**: 基础框架搭建完毕，三大核心工具集成成功  
**下一步**: 开始里程碑2 - Commit 5基础脚本生成功能

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

## 最新功能展示 (里程碑1 - Commits 1-4)

### 综合工具能力演示

ALITA现在具备了三大核心工具能力：代码执行、网络搜索、文件操作：

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

#### 1. 代码执行能力 (Commit 2)
- **代码片段执行**: 执行Python代码字符串
- **脚本文件执行**: 运行.py脚本文件 
- **安全验证**: 代码执行前的安全检查
- **错误处理**: 全面的错误捕获和报告
- **导入限制**: 可配置的模块导入安全控制

#### 2. 网络搜索能力 (Commit 3)
- **Wikipedia搜索**: 获取权威知识信息
- **Google免费搜索**: 获取最新网络信息
- **多源聚合**: 统一格式化搜索结果
- **智能过滤**: 内容摘要和质量评估

#### 3. 文件操作能力 (Commit 4)
- **文件读写**: 支持多种文件格式
- **文件追加**: 增量内容更新
- **目录操作**: 文件列表和信息获取
- **类型检测**: 自动文件类型识别
- **安全检查**: 路径验证和权限控制

### 运行演示

```bash
cd /Users/bitkira/Documents/GitHub/EvoAgentX

# 代码执行演示
python examples/alita_reproduction/examples/code_execution_demo.py

# 网络搜索演示
python examples/alita_reproduction/examples/web_search_demo.py

# 文件操作演示
python examples/alita_reproduction/examples/file_operations_demo.py
```

## Contributing

This project follows the EvoAgentX contribution guidelines. Each commit represents a complete, testable increment of functionality.