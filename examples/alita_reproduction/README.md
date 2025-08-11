# ALITA Reproduction Project

This project reproduces the ALITA (Autonomous LLM-based Intelligent Tool Agent) framework using EvoAgentX components.

## Project Structure

```
alita_reproduction/
├── README.md              # This file
├── config.py             # Configuration management
├── agents/               # ALITA agent implementations
│   ├── __init__.py
│   ├── manager_agent.py  # Manager Agent - central coordinator
│   ├── web_agent.py      # Web Agent - information retrieval
│   └── mcp_creation_agent.py  # MCP Creation Agent
├── actions/              # Custom Actions for ALITA
│   ├── __init__.py
│   ├── mcp_brainstorming.py     # MCP Brainstorming Action
│   ├── script_generating.py    # Script Generation Action
│   └── code_running.py         # Code Running Action
├── workflows/            # Workflow implementations
│   ├── __init__.py
│   ├── codereact_workflow.py   # Main CodeReAct loop
│   └── mcp_creation_workflow.py # MCP creation workflow
├── storage/             # MCP Box and tool storage
│   ├── __init__.py
│   ├── mcp_box.py       # MCP storage and management
│   └── tool_registry.py # Dynamic tool registry
├── examples/            # Usage examples
│   ├── __init__.py
│   ├── basic_example.py # Basic ALITA usage
│   └── advanced_example.py # Advanced features demo
├── tests/               # Test cases
│   ├── __init__.py
│   ├── test_manager_agent.py
│   └── test_actions.py
└── docs/               # Documentation
    ├── architecture.md  # System architecture
    ├── api_reference.md # API documentation
    └── tutorial.md     # Usage tutorial
```

## Development Progress

### Phase 1: Basic Framework (Commits 1-4)
- [x] Commit 1: Project initialization and basic ManagerAgent ✅ In Progress
- [ ] Commit 2: Basic tool calling mechanism
- [ ] Commit 3: Task decomposition logic
- [ ] Commit 4: Web search integration

### Phase 2: Tool Creation (Commits 5-7)
- [ ] Commit 5: Basic script generation
- [ ] Commit 6: Script validation and execution
- [ ] Commit 7: Simplified MCP storage

### Phase 3: Loop Mechanism (Commits 8-10)
- [ ] Commit 8: CodeReAct basic loop
- [ ] Commit 9: Agent collaboration
- [ ] Commit 10: Result aggregation

## Current Status: Commit 1
Creating the basic project structure and implementing a simple ManagerAgent that can:
- Accept tasks as input
- Provide basic responses
- Establish foundation for future enhancements

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

## Contributing

This project follows the EvoAgentX contribution guidelines. Each commit represents a complete, testable increment of functionality.