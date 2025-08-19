"""Utilities for Bayonetta examples.

本模块对外导出 examples 中常用的小工具函数，便于通过

	from examples.bayonetta.utility import json_to_markdown

直接使用。
"""

from .json2markdown import json_to_markdown

__all__ = ["json_to_markdown"]

