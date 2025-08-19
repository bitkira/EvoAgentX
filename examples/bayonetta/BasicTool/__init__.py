"""
BasicTool Package
Simplified tool interfaces for common operations
"""

from .fileoperate import FileOperatorTool
from .websearch import search_web, quick_search

__all__ = [
    "FileOperatorTool",
    "search_web", 
    "quick_search"
]