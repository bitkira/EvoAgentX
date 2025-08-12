"""
Web Search Demo for ALITA reproduction.

This script demonstrates the web search capabilities of the ALITA Manager Agent
using the integrated WebSearchAction with Wikipedia and Google search.
"""

import sys
import os
import logging

# Add the parent directory to sys.path to import from alita_reproduction
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.manager_agent import ManagerAgent
from evoagentx.models import OpenAILLMConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_basic_web_search():
    """Demonstrate basic web search capabilities."""
    print("\n" + "="*60)
    print("ALITA Web Search Demo - Basic Operations")
    print("="*60)
    
    # Initialize Manager Agent
    logger.info("Initializing ALITA Manager Agent...")
    
    # You can configure with actual API key for full LLM functionality
    # For demo, we'll focus on the web search capabilities
    llm_config = OpenAILLMConfig(
        model="gpt-3.5-turbo",
        api_key="demo-key",  # Replace with actual key for full functionality
        temperature=0.7
    )
    
    manager = ManagerAgent(llm_config=llm_config)
    
    # Display capabilities
    print("\nManager Agent Capabilities:")
    capabilities = manager.get_capabilities()
    for name, desc in capabilities.items():
        print(f"  • {name}: {desc}")
    
    # Display web search status
    print("\nWeb Search Status:")
    status = manager.get_web_search_status()
    for key, value in status.items():
        print(f"  • {key}: {value}")
    
    return manager


def demo_wikipedia_search():
    """Demonstrate Wikipedia search functionality."""
    print("\n" + "="*60)
    print("Wikipedia Search Demo")
    print("="*60)
    
    manager = demo_basic_web_search()
    
    # Test Wikipedia search
    queries = [
        "artificial intelligence",
        "machine learning algorithms",
        "quantum computing"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Searching Wikipedia for: '{query}'")
        result = manager.search_wikipedia(query)
        
        if result["success"]:
            print(f"   ✅ Found {len(result['results'])} results")
            for j, item in enumerate(result["results"][:2], 1):  # Show first 2 results
                print(f"      Result {j}: {item['title']}")
                print(f"      Summary: {item['summary'][:200]}...")
                print(f"      URL: {item['url']}")
        else:
            print(f"   ❌ Search failed: {result['error']}")


def demo_google_search():
    """Demonstrate Google free search functionality."""
    print("\n" + "="*60)
    print("Google Free Search Demo")
    print("="*60)
    
    manager = demo_basic_web_search()
    
    # Test Google search
    queries = [
        "python programming tutorial 2024",
        "latest AI research papers",
        "EvoAgentX framework documentation"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Searching Google for: '{query}'")
        result = manager.search_google(query)
        
        if result["success"]:
            print(f"   ✅ Found {len(result['results'])} results")
            for j, item in enumerate(result["results"][:2], 1):  # Show first 2 results
                print(f"      Result {j}: {item['title']}")
                print(f"      Content: {item['content'][:150]}...")
                print(f"      URL: {item['url']}")
        else:
            print(f"   ❌ Search failed: {result['error']}")


def demo_auto_search():
    """Demonstrate automatic search source selection."""
    print("\n" + "="*60)
    print("Auto Search Selection Demo")
    print("="*60)
    
    manager = demo_basic_web_search()
    
    # Test queries that should trigger different search strategies
    test_cases = [
        ("What is artificial intelligence?", "Should prefer Wikipedia"),
        ("latest AI news 2024", "Should prefer Google"),
        ("definition of machine learning", "Should prefer Wikipedia"),
        ("python tutorial github", "Should prefer Google")
    ]
    
    for i, (query, expectation) in enumerate(test_cases, 1):
        print(f"\n{i}. Auto-searching for: '{query}'")
        print(f"   Expected: {expectation}")
        
        result = manager.search_web(query, source="auto")
        
        if result["success"]:
            if "source" in result:
                print(f"   ✅ Selected source: {result['source']}")
                print(f"   Found {len(result.get('results', []))} results")
            elif "sources_searched" in result:
                print(f"   ✅ Searched sources: {result['sources_searched']}")
                print(f"   Total results: {result.get('total_results', 0)}")
        else:
            print(f"   ❌ Search failed: {result.get('error', 'Unknown error')}")


def demo_comprehensive_search():
    """Demonstrate comprehensive search across all sources."""
    print("\n" + "="*60)
    print("Comprehensive Search Demo")
    print("="*60)
    
    manager = demo_basic_web_search()
    
    # Search query across all sources
    query = "neural networks deep learning"
    
    print(f"\nSearching all sources for: '{query}'")
    result = manager.search_web(query, source="all")
    
    if result["success"]:
        print(f"✅ Comprehensive search successful!")
        print(f"Sources searched: {result.get('sources_searched', [])}")
        print(f"Total results: {result.get('total_results', 0)}")
        
        # Display results by source
        for source, source_results in result.get("results_by_source", {}).items():
            print(f"\n--- {source.upper()} Results ---")
            if source_results["success"]:
                print(f"Found {len(source_results['results'])} results")
                for i, item in enumerate(source_results["results"][:1], 1):  # Show 1 result per source
                    print(f"  {i}. {item['title']}")
                    if 'summary' in item:
                        print(f"     Summary: {item['summary'][:100]}...")
                    elif 'content' in item:
                        print(f"     Content: {item['content'][:100]}...")
            else:
                print(f"Failed: {source_results['error']}")
    else:
        print(f"❌ Comprehensive search failed")
        if result.get("errors"):
            for error in result["errors"]:
                print(f"   Error: {error}")


def demo_search_with_task_assessment():
    """Demonstrate task assessment with search needs detection."""
    print("\n" + "="*60)
    print("Task Assessment Demo")
    print("="*60)
    
    manager = demo_basic_web_search()
    
    # Test different types of tasks
    tasks = [
        "Search for information about quantum computing",
        "Calculate the factorial of 10",
        "Find the latest news about AI developments",
        "What is the definition of machine learning?",
        "Write a Python function to sort a list"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. Assessing task: '{task}'")
        assessment = manager.assess_tool_needs(task)
        
        print(f"   Needs additional tools: {assessment['needs_additional_tools']}")
        if assessment['suggested_tools']:
            print(f"   Suggested tools: {', '.join(assessment['suggested_tools'])}")
        
        # If web search is suggested, demonstrate it
        if "web_search" in assessment['suggested_tools']:
            print(f"   🔍 Executing web search...")
            search_result = manager.search_web(task.replace("Search for information about ", ""))
            if search_result["success"]:
                total_results = search_result.get("total_results", len(search_result.get("results", [])))
                print(f"   ✅ Search completed: {total_results} results found")
            else:
                print(f"   ❌ Search failed: {search_result.get('error', 'Unknown error')}")


def main():
    """Run all web search demo functions."""
    print("🌐 Starting ALITA Web Search Demo")
    print("This demo showcases the web search capabilities of the ALITA Manager Agent.")
    
    try:
        # Run demos
        demo_wikipedia_search()
        demo_google_search()
        demo_auto_search()
        demo_comprehensive_search()
        demo_search_with_task_assessment()
        
        print("\n" + "="*60)
        print("✅ All web search demos completed successfully!")
        print("The ALITA Manager Agent now has comprehensive web search capabilities.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        logger.error(f"Demo failed: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()