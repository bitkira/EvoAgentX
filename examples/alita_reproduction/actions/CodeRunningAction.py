from evoagentx.tools.tool import Tool
from evoagentx.tools.interpreter_python import PythonInterpreter
import os

interpreter = PythonInterpreter(
    project_path=os.getcwd(),
    directory_names=["examples", "evoagentx", "tests"],
    allowed_imports={
        "os", "sys", "time", "datetime", "math", "random", 
        "json", "csv", "re", "collections", "itertools"
    }
)

# # 执行 Python 脚本文件
# script_path = "examples/hello_world.py"
# script_result = interpreter.execute_script(script_path, "python")
# print(script_result)

# 执行简单的代码片段
result = interpreter.execute("""
print("Hello, World!")
import math
print(f"The value of pi is: {math.pi:.4f}")
""", "python")

print(result)