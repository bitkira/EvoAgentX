"""
Web Search Tool for Agent Use

Simple and clean web search function that takes a query and returns Markdown formatted results.
Designed to be easily called by AI agents with minimal complexity.

Requirements:
- SERPER_API_KEY environment variable must be set
- Get your API key from: https://serper.dev/

Usage:
    result_md = search_web("your search query")
    print(result_md)
"""

import os
from typing import Optional
from evoagentx.tools.search_serperapi import SearchSerperAPI
from examples.bayonetta.utility import json_to_markdown


def search_web(
    query: str,
    num_results: int = 5,
    max_content_words: int = 200,
    api_key: Optional[str] = None
) -> str:
    """
    Search the web and return results in Markdown format.
    
    This function performs a web search using SerperAPI and returns formatted results
    that are ready to display or process. Designed for simplicity and agent integration.
    
    Args:
        query (str): The search query string
        num_results (int, optional): Number of search results to return. Defaults to 5.
        max_content_words (int, optional): Maximum words per result content. Defaults to 200.
        api_key (str, optional): SerperAPI key. If None, uses SERPER_API_KEY env variable.
    
    Returns:
        str: Formatted Markdown string containing search results, or error message
        
    Example:
        >>> result = search_web("Python machine learning")
        >>> print(result)
        ## Search Result 1
        ### title
        Python Machine Learning Tutorial
        ### url
        https://example.com
        ### content
        Learn Python machine learning basics...
    """
    # Get API key from parameter or environment
    api_key = api_key or os.getenv("SERPER_API_KEY")
    
    if not api_key:
        return "❌ Error: SERPER_API_KEY not found. Please set environment variable or provide api_key parameter.\nGet your key from: https://serper.dev/"
    
    if not query or not query.strip():
        return "❌ Error: Search query cannot be empty."
    
    try:
        # Initialize search tool
        search_tool = SearchSerperAPI(
            name="WebSearchTool",
            enable_content_scraping=True,
            num_search_pages=num_results,
            max_content_words=max_content_words,
            api_key=api_key
        )
        
        # Perform search
        results_dict = search_tool.search(query.strip())
        
        # Check for errors in results
        if results_dict.get("error"):
            return f"❌ Search Error: {results_dict['error']}"
        
        # Get results list
        results = results_dict.get("results", [])
        
        if not results:
            return f"🔍 No results found for query: '{query}'"
        
        # Format results to Markdown
        formatted_results = []
        for i, info in enumerate(results, 1):
            markdown_content = json_to_markdown(info, keys=["title", "url", "content"])
            formatted_results.append(f"## Search Result {i}\n{markdown_content}")
        
        # Combine all results
        final_md = "\n\n---\n\n".join(formatted_results)
        
        # Add header with search info
        header = f"# Web Search Results\n**Query:** {query}  \n**Results:** {len(results)}\n\n---\n\n"
        
        return header + final_md
        
    except Exception as e:
        return f"❌ Search failed: {str(e)}"


def quick_search(query: str) -> str:
    """
    Quick search with default parameters - most convenient for agent use.
    
    Args:
        query (str): The search query string
        
    Returns:
        str: Formatted Markdown string with search results
        
    Example:
        >>> result = quick_search("latest AI news")
        >>> print(result)
    """
    return search_web(query, num_results=3, max_content_words=None)

