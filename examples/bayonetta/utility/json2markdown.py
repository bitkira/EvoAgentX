"""json2markdown

提供一个简单函数：从给定 JSON(dict) 中选择指定 keys，生成 Markdown 字符串。

用法：
  - json_to_markdown(data, keys=['a','b.c'])
  - keys 可以是 str 或 list[str]；支持点号路径访问嵌套字段（例如 'parent.child')。

输出策略（简洁可读）：
  - 标量（str/int/float/bool/None）直接写入段落
  - list 或 dict 使用 JSON 格式的代码块展示，保证可读性

该文件包含一个简单的 __main__ 示例，便于在命令行测试。
"""

from __future__ import annotations

import json
from typing import Any, Iterable, List, Optional, Union


def _get_by_path(data: dict, path: str) -> Any:
    """通过点号路径从字典中取值；找不到时抛出 KeyError。

    例如 path='a.b.c' 会返回 data['a']['b']['c']。
    """
    parts = path.split(".") if path else []
    cur: Any = data
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            raise KeyError(path)
    return cur


def _is_primitive(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def json_to_markdown(
    data: dict,
    keys: Optional[Union[str, Iterable[str]]] = None,
    heading_level: int = 2,
    list_style: str = "-",
) -> str:
    """将 `data`（dict）中 `keys` 指定的字段转换为 Markdown 文本并返回。

    参数:
      - data: 要处理的 JSON 对象（Python dict）
      - keys: 要提取的字段，可以是单个字符串或字符串列表。支持点号路径访问嵌套字段。
              如果为 None，则输出所有顶层键（按插入顺序）。
      - heading_level: Markdown 标题级别（默认 2，对应 '##'）
      - list_style: 当键对应列表但列表项为标量时，使用的项目符号（默认 '-'）

    返回:
      - 生成的 Markdown 字符串（utf-8 可读，中文不会被转义）
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    # 规范 keys 为列表
    if keys is None:
        key_list = list(data.keys())
    elif isinstance(keys, str):
        key_list = [keys]
    else:
        key_list = list(keys)

    lines: List[str] = []
    for key in key_list:
        lines.append("{} {}".format('#' * max(1, heading_level), key))
        try:
            value = _get_by_path(data, key) if ("." in key) or key not in data else data[key]
        except KeyError:
            lines.append(f"> 键 `{key}` 未找到。")
            lines.append("")
            continue

        # 处理不同类型的值
        if _is_primitive(value):
            # 简短标量直接写成段落
            lines.append(str(value))
        elif isinstance(value, list):
            # 若列表元素都为标量，使用 Markdown 列表；否则用 JSON 代码块
            if all(_is_primitive(v) for v in value):
                for item in value:
                    lines.append(f"{list_style} {item}")
            else:
                lines.append("```json")
                lines.append(json.dumps(value, ensure_ascii=False, indent=2))
                lines.append("```")
        elif isinstance(value, dict):
            # 字典使用 JSON 代码块，保证结构性
            lines.append("```json")
            lines.append(json.dumps(value, ensure_ascii=False, indent=2))
            lines.append("```")
        else:
            # 其他可序列化对象回退为 JSON 表示
            try:
                lines.append("```json")
                lines.append(json.dumps(value, ensure_ascii=False, indent=2))
                lines.append("```")
            except TypeError:
                lines.append(str(value))

        lines.append("")  # 每个条目后空行

    return "\n".join(lines)


if __name__ == "__main__":
    # 简单示例，便于手动运行验证
    sample = {
        "title": "示例文档",
        "summary": "这是一个用于演示的简短摘要。",
        "tags": ["ai", "nlp", "模型"],
        "metrics": {"accuracy": 0.92, "f1": 0.89},
        "items": [
            {"name": "a", "value": 1},
            {"name": "b", "value": 2}
        ],
        "nested": {"a": {"b": "深层值"}}
    }
