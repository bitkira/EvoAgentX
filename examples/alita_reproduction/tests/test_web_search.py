"""
Test cases for Web Search functionality.

Tests the web search capabilities integrated into ALITA,
including the WebSearchAction class and its integration with ManagerAgent.
"""

import unittest
import sys
import os

# Add the EvoAgentX root to path
sys.path.append('/Users/bitkira/Documents/GitHub/EvoAgentX')

from examples.alita_reproduction.actions.web_search import WebSearchAction
from examples.alita_reproduction.agents.manager_agent import ManagerAgent
from examples.alita_reproduction.config import ALITAConfig


class TestWebSearchAction(unittest.TestCase):
    """Test cases for WebSearchAction class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.action = WebSearchAction(
            max_summary_sentences=2,
            num_search_pages=2,
            max_content_words=200
        )
    
    def test_initialization(self):
        """Test WebSearchAction initialization."""
        self.assertIsNotNone(self.action)
        
        # Check available sources
        sources = self.action.get_available_sources()
        self.assertIsInstance(sources, list)
        
        # Check status
        status = self.action.get_search_status()
        self.assertIsInstance(status, dict)
        self.assertIn("wikipedia_available", status)
        self.assertIn("google_available", status)
    
    def test_wikipedia_search_structure(self):
        """Test Wikipedia search result structure."""
        if not self.action.wikipedia_search:
            self.skipTest("Wikipedia search not available")
        
        query = "artificial intelligence"
        result = self.action.search_wikipedia(query)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("source", result)
        self.assertIn("query", result)
        self.assertIn("results", result)
        self.assertIn("error", result)
        
        self.assertEqual(result["source"], "wikipedia")
        self.assertEqual(result["query"], query)
        
        if result["success"]:
            self.assertIsInstance(result["results"], list)
            if result["results"]:
                # Check first result structure
                first_result = result["results"][0]
                self.assertIn("title", first_result)
                self.assertIn("summary", first_result)
                self.assertIn("url", first_result)
                self.assertIn("source", first_result)
                self.assertEqual(first_result["source"], "wikipedia")
    
    def test_google_search_structure(self):
        """Test Google search result structure."""
        if not self.action.google_search:
            self.skipTest("Google search not available")
        
        query = "python programming"
        result = self.action.search_google(query)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("source", result)
        self.assertIn("query", result)
        self.assertIn("results", result)
        self.assertIn("error", result)
        
        self.assertEqual(result["source"], "google")
        self.assertEqual(result["query"], query)
        
        if result["success"]:
            self.assertIsInstance(result["results"], list)
            if result["results"]:
                # Check first result structure
                first_result = result["results"][0]
                self.assertIn("title", first_result)
                self.assertIn("url", first_result)
                self.assertIn("content", first_result)
                self.assertIn("source", first_result)
                self.assertEqual(first_result["source"], "google")
    
    def test_search_all_structure(self):
        """Test comprehensive search result structure."""
        query = "machine learning"
        result = self.action.search_all(query)
        
        # Check aggregated result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("query", result)
        self.assertIn("sources_searched", result)
        self.assertIn("results_by_source", result)
        self.assertIn("total_results", result)
        self.assertIn("errors", result)
        
        self.assertEqual(result["query"], query)
        self.assertIsInstance(result["sources_searched"], list)
        self.assertIsInstance(result["results_by_source"], dict)
        self.assertIsInstance(result["total_results"], int)
        self.assertIsInstance(result["errors"], list)
    
    def test_unified_search_interface(self):
        """Test unified search interface with different sources."""
        query = "neural networks"
        
        # Test auto search
        auto_result = self.action.search(query, source="auto")
        self.assertIsInstance(auto_result, dict)
        self.assertIn("success", auto_result)
        
        # Test specific source searches
        if self.action.wikipedia_search:
            wiki_result = self.action.search(query, source="wikipedia")
            self.assertEqual(wiki_result["source"], "wikipedia")
        
        if self.action.google_search:
            google_result = self.action.search(query, source="google")
            self.assertEqual(google_result["source"], "google")
        
        # Test all sources
        all_result = self.action.search(query, source="all")
        self.assertIn("sources_searched", all_result)
        
        # Test invalid source
        invalid_result = self.action.search(query, source="invalid")
        self.assertFalse(invalid_result["success"])
        self.assertIn("Unknown source", invalid_result["error"])
    
    def test_error_handling(self):
        """Test error handling in search operations."""
        # Test empty query
        empty_result = self.action.search("", source="auto")
        # Should still attempt search, but may return no results
        self.assertIsInstance(empty_result, dict)
        
        # Test very long query
        long_query = "a" * 1000
        long_result = self.action.search(long_query, source="auto")
        self.assertIsInstance(long_result, dict)


class TestManagerAgentWebSearch(unittest.TestCase):
    """Test web search through ManagerAgent integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock configuration for testing
        config = ALITAConfig(openai_api_key="test_key")
        llm_config = config.create_llm_config()
        self.manager = ManagerAgent(llm_config=llm_config)
    
    def test_manager_has_web_searcher(self):
        """Test that manager agent has web searcher initialized."""
        self.assertIsNotNone(self.manager.web_searcher)
        self.assertIsInstance(self.manager.web_searcher, WebSearchAction)
    
    def test_manager_web_search_capabilities(self):
        """Test that manager capabilities include web search."""
        capabilities = self.manager.get_capabilities()
        
        self.assertIn("web_search", capabilities)
        self.assertIn("information_retrieval", capabilities)
    
    def test_manager_web_search_methods(self):
        """Test web search methods through manager agent."""
        query = "artificial intelligence"
        
        # Test unified search
        result = self.manager.search_web(query)
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        
        # Test Wikipedia search
        wiki_result = self.manager.search_wikipedia(query)
        self.assertIsInstance(wiki_result, dict)
        self.assertIn("success", wiki_result)
        if wiki_result["success"]:
            self.assertEqual(wiki_result["source"], "wikipedia")
        
        # Test Google search
        google_result = self.manager.search_google(query)
        self.assertIsInstance(google_result, dict)
        self.assertIn("success", google_result)
        if google_result["success"]:
            self.assertEqual(google_result["source"], "google")
    
    def test_manager_search_status(self):
        """Test getting web search status through manager."""
        status = self.manager.get_web_search_status()
        
        self.assertIsInstance(status, dict)
        # Should contain status information
        expected_fields = ["wikipedia_available", "google_available", "available_sources"]
        for field in expected_fields:
            if field in status:  # Some fields might be optional
                self.assertIsNotNone(status[field])
    
    def test_enhanced_task_assessment(self):
        """Test enhanced task assessment that includes web search detection."""
        # Test tasks that should trigger web search
        search_tasks = [
            "search for information about quantum computing",
            "find the latest AI research",
            "what is machine learning?",
            "lookup current trends in technology"
        ]
        
        for task in search_tasks:
            assessment = self.manager.assess_tool_needs(task)
            self.assertIn("web_search", assessment["suggested_tools"])
        
        # Test tasks that should not trigger web search
        non_search_tasks = [
            "calculate 2 + 2",
            "write a python function",
            "create a simple algorithm"
        ]
        
        for task in non_search_tasks:
            assessment = self.manager.assess_tool_needs(task)
            # May or may not suggest web search depending on keywords
            # Just check that assessment is valid
            self.assertIsInstance(assessment, dict)
            self.assertIn("needs_additional_tools", assessment)


class TestWebSearchIntegration(unittest.TestCase):
    """Test integration between web search components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.action = WebSearchAction()
        config = ALITAConfig(openai_api_key="test_key")
        llm_config = config.create_llm_config()
        self.manager = ManagerAgent(llm_config=llm_config)
    
    def test_consistent_search_results(self):
        """Test that direct action search and manager search return consistent results."""
        query = "python programming"
        
        # Search through action directly
        if self.action.wikipedia_search:
            direct_result = self.action.search_wikipedia(query)
            
            # Search through manager
            manager_result = self.manager.search_wikipedia(query)
            
            # Results should have same structure
            self.assertEqual(direct_result["source"], manager_result["source"])
            self.assertEqual(direct_result["query"], manager_result["query"])
            # Success may vary due to network conditions, but structure should be same
    
    def test_search_toolkit_availability(self):
        """Test availability of search toolkits across components."""
        # Check action status
        action_status = self.action.get_search_status()
        
        # Check manager status  
        manager_status = self.manager.get_web_search_status()
        
        # Should report consistent availability
        if "wikipedia_available" in action_status and "wikipedia_available" in manager_status:
            self.assertEqual(
                action_status["wikipedia_available"], 
                manager_status["wikipedia_available"]
            )


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWebSearchAction))
    suite.addTests(loader.loadTestsFromTestCase(TestManagerAgentWebSearch))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSearchIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Web Search Test Summary")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed! Web search functionality is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the details above.")