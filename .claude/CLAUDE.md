# EvoAgentX 项目说明

## 项目概述
EvoAgentX是一个开源框架，专为自动化智能体工作流的完整生命周期而设计，包括生成、执行、评估和优化。框架能够将自然语言目标转换为可执行的多智能体工作流，并使用各种进化算法迭代优化性能。

## 核心架构组件

### 1. 智能体系统 (Agents)
- **CustomizeAgent**: 最简单的智能体创建方式，支持自然语言提示词
- **Agent**: 支持多个Action的复杂智能体，可执行不同类型的任务
- **AgentManager**: 管理智能体的生命周期、配置和部署

### 2. 工作流系统 (Workflow)
- **WorkFlowGenerator**: 基于目标自动生成工作流
- **WorkFlowGraph**: 工作流的有向图表示，存储任务节点和关系
- **SequentialWorkFlowGraph**: 顺序执行的工作流图
- **WorkFlow**: 工作流执行器，协调多智能体协作

### 3. 动作系统 (Actions)
- **Action基类**: 定义智能体可执行的具体操作
- **ActionInput/ActionOutput**: 结构化的输入输出格式
- 支持自定义动作，包括代码生成、代码审查等

### 4. LLM集成 (Models)
支持多种大语言模型提供商:
- **OpenAI**: GPT系列模型(推荐)
- **LiteLLM**: 统一多提供商接口
- **OpenRouter**: 第三方模型提供商
- **阿里云**: 通义千问系列

### 5. 工具生态系统 (Tools)
丰富的外部工具集成:
- **代码执行器**:
  - PythonInterpreterToolkit: 安全Python代码执行
  - DockerInterpreterToolkit: Docker容器隔离执行
- **搜索工具**:
  - WikipediaSearchToolkit: 维基百科搜索
  - GoogleSearchToolkit: Google搜索API
  - GoogleFreeSearchToolkit: 免API密钥Google搜索
- **文件操作**:
  - FileToolkit: 文件读写，支持PDF等格式
- **浏览器自动化**:
  - BrowserToolkit: Selenium精确控制
  - BrowserUseToolkit: AI驱动的自然语言浏览器控制
- **MCP集成**: Model Context Protocol支持外部服务

### 6. 优化算法 (Optimizers)
进化算法优化工作流性能:
- **TextGrad**: 基于文本梯度的提示词优化
- **MIPRO**: 多目标提示词和参数优化
- **AFlow**: 自动化工作流结构和提示词优化

### 7. 评估系统 (Benchmark & Evaluators)
内置基准测试和评估指标:
- **基准数据集**: HotPotQA, MATH, MBPP, HumanEval, GAIA
- **评估器**: 标准化性能评估和改进建议
- **指标系统**: 多维度性能测量

### 8. 存储和记忆 (Storage & Memory)
- **StorageHandler**: 持久化存储管理
- **Memory**: 短期和长期记忆管理
- 支持多种存储后端: MongoDB, SQLite, PostgreSQL

### 9. RAG系统
完整的检索增强生成支持:
- **文档处理**: 多格式文档解析
- **向量化**: 多种嵌入模型支持
- **索引和检索**: 高效的信息检索

### 10. Human-in-the-Loop (HITL)
人机协作功能:
- **交互式工具**: 工作流执行中的人工干预
- **审批管理器**: 关键决策点的人工审批

## FastAPI后端服务

### API模块结构
- **认证系统**: JWT token身份验证和用户管理
- **智能体管理**: CRUD操作和状态管理
- **工作流管理**: 工作流定义、版本控制和编排
- **执行管理**: 异步工作流执行和监控
- **系统监控**: 健康检查和性能指标

### 数据模型
- 使用MongoDB作为主数据库
- Pydantic数据验证
- 支持复杂嵌套配置

## 开发和使用指南

### 安装配置
```bash
# 基础安装
pip install git+https://github.com/EvoAgentX/EvoAgentX.git

# 开发模式安装
git clone https://github.com/EvoAgentX/EvoAgentX.git
cd EvoAgentX
pip install -e .
```

### API密钥配置
```bash
# 环境变量
export OPENAI_API_KEY=your_openai_api_key

# .env文件
OPENAI_API_KEY=your_openai_api_key
```

### 基本使用流程
1. **配置LLM**: 设置API密钥和模型参数
2. **创建智能体**: 使用CustomizeAgent或Agent类
3. **生成工作流**: 使用WorkFlowGenerator从自然语言目标生成
4. **执行工作流**: 通过WorkFlow协调多智能体执行
5. **优化性能**: 使用内置优化算法改进工作流

### 解析模式
智能体输出支持多种解析模式:
- `str`: 默认字符串解析
- `json`: JSON格式解析
- `xml`: XML格式解析
- `title`: 标题提取
- `custom`: 自定义解析函数

### 工具集成
智能体可以自动集成各种工具:
```python
from evoagentx.tools import ArxivToolkit, CMDToolkit, BrowserToolkit

# 工具工具包
toolkit = ArxivToolkit()
agent = CustomizeAgent(name="Researcher", tools=[toolkit])
```

## 测试和构建
- **运行测试**: `pytest`
- **代码格式化**: `ruff format` 
- **代码检查**: `ruff check`
- **启动API服务**: `python -m evoagentx.app.main`

## 重要文件和示例
- `pyproject.toml`: 项目配置和依赖声明
- `examples/workflow_demo.py`: 基础工作流示例
- `examples/customize_agent.py`: 智能体创建示例
- `docs/`: 完整文档和教程

## 特色功能
- **自动工作流生成**: 从自然语言描述自动创建工作流
- **工具自动分配**: 智能体根据任务自动获得合适的工具
- **进化优化**: 使用多种算法持续优化工作流性能
- **模块化设计**: 所有组件可独立使用和扩展
- **企业级API**: 完整的后端服务支持多用户和权限管理

## 最佳实践
1. 使用明确的任务描述和输入输出定义
2. 合理选择解析模式和工具集成
3. 利用序列化功能保存和复用工作流
4. 使用评估器持续监控性能
5. 在生产环境中启用HITL人工监督