import os 
from dotenv import load_dotenv
from evoagentx.models import OpenRouterConfig
from evoagentx.agents import CustomizeAgent
from evoagentx.agents import agent
from evoagentx.tools import DockerInterpreterToolkit


load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

openrouter_config = OpenRouterConfig(model="openai/gpt-4o-mini", openrouter_key=OPENROUTER_API_KEY)

simple_agent = CustomizeAgent(
    name="SimpleAgent",
    description="A basic agent that responds to queries",
    prompt="Answer the following question: {question}",
    llm_config=openrouter_config,
    inputs=[
        {"name": "question", "type": "string", "description": "The question to answer"}
    ]
)

response = simple_agent(inputs={"question": "What is a language model?"})
print(response.content.content)

# 使用特定的 Docker 镜像进行初始化
toolkit = DockerInterpreterToolkit(
    image_tag="fundingsocietiesdocker/python3.9-slim",
    print_stdout=True,
    print_stderr=True,
    container_directory="/app"
)

# 获取执行脚本的工具
execute_script_tool = toolkit.get_tool("docker_execute_script")

# 在 Docker 中执行一个 Python 脚本文件
script_result = execute_script_tool(file_path="examples/docker_test.py", language="python")
print(script_result)


