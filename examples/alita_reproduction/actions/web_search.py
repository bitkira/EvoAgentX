"""
Web Search Action for ALITA reproduction.

This module provides web search capabilities using EvoAgentX's search toolkits,
including Wikipedia search and Google free search functionality.
"""

import logging
from typing import Dict, Any, Optional, List
from evoagentx.tools import WikipediaSearchToolkit, GoogleFreeSearchToolkit

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSearchAction:
    """
    Web Search Action for searching information from various web sources.
    
    This class provides unified access to multiple search engines including
    Wikipedia and Google, with comprehensive error handling and result processing.
    """
    
    def __init__(
        self,
        max_summary_sentences: int = 3,
        num_search_pages: int = 3,
        max_content_words: int = 500
    ):
        """
        Initialize the WebSearchAction.
        
        Args:
            max_summary_sentences: Maximum sentences in Wikipedia summaries
            num_search_pages: Number of search result pages to fetch
            max_content_words: Maximum words of content per search result
        """
        # Initialize Wikipedia search toolkit
        try:
            self.wikipedia_toolkit = WikipediaSearchToolkit(
                max_summary_sentences=max_summary_sentences
            )
            self.wikipedia_search = self.wikipedia_toolkit.get_tool("wikipedia_search")
            logger.info("Wikipedia search toolkit initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Wikipedia toolkit: {str(e)}")
            self.wikipedia_toolkit = None
            self.wikipedia_search = None
        
        # Initialize Google free search toolkit
        try:
            self.google_toolkit = GoogleFreeSearchToolkit(
                num_search_pages=num_search_pages,
                max_content_words=max_content_words
            )
            self.google_search = self.google_toolkit.get_tool("google_free_search")
            logger.info("Google free search toolkit initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google toolkit: {str(e)}")
            self.google_toolkit = None
            self.google_search = None
        
        logger.info("WebSearchAction initialized successfully")
    
    def search_wikipedia(self, query: str) -> Dict[str, Any]:
        """
        Search Wikipedia for information.
        
        Args:
            query: Search query string
            
        Returns:
            Dict containing search results and metadata
        """
        logger.info(f"Searching Wikipedia for: {query}")
        
        if not self.wikipedia_search:
            return {
                "success": False,
                "source": "wikipedia",
                "query": query,
                "results": [],
                "error": "Wikipedia search not available - toolkit initialization failed"
            }
        
        try:
            # Execute Wikipedia search
            raw_results = self.wikipedia_search(query=query)
            
            # Process and structure results
            results = []
            if isinstance(raw_results, dict) and "results" in raw_results:
                for result in raw_results["results"]:
                    processed_result = {
                        "title": result.get("title", ""),
                        "summary": result.get("summary", ""),
                        "url": result.get("url", ""),
                        "source": "wikipedia"
                    }
                    results.append(processed_result)
            
            return {
                "success": True,
                "source": "wikipedia",
                "query": query,
                "results": results,
                "total_results": len(results),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error searching Wikipedia: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "source": "wikipedia",
                "query": query,
                "results": [],
                "error": error_msg
            }
    
    def search_google(self, query: str) -> Dict[str, Any]:
        """
        Search Google for information using the free search toolkit.
        
        Args:
            query: Search query string
            
        Returns:
            Dict containing search results and metadata
        """
        logger.info(f"Searching Google for: {query}")
        
        if not self.google_search:
            return {
                "success": False,
                "source": "google",
                "query": query,
                "results": [],
                "error": "Google search not available - toolkit initialization failed"
            }
        
        try:
            # Execute Google search
            raw_results = self.google_search(query=query)
            
            # Process and structure results
            results = []
            if isinstance(raw_results, dict) and "results" in raw_results:
                for result in raw_results["results"]:
                    processed_result = {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", "")[:1000],  # Limit content length
                        "source": "google"
                    }
                    results.append(processed_result)
            
            return {
                "success": True,
                "source": "google", 
                "query": query,
                "results": results,
                "total_results": len(results),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error searching Google: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "source": "google",
                "query": query,
                "results": [],
                "error": error_msg
            }
    
    def search_all(self, query: str, include_sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search across all available sources.
        
        Args:
            query: Search query string
            include_sources: List of sources to include ('wikipedia', 'google') 
                           If None, includes all available sources
            
        Returns:
            Dict containing aggregated search results from all sources
        """
        logger.info(f"Searching all sources for: {query}")
        
        if include_sources is None:
            include_sources = ["wikipedia", "google"]
        
        aggregated_results = {
            "success": False,
            "query": query,
            "sources_searched": [],
            "results_by_source": {},
            "total_results": 0,
            "errors": []
        }
        
        # Search Wikipedia if requested and available
        if "wikipedia" in include_sources and self.wikipedia_search:
            wiki_results = self.search_wikipedia(query)
            aggregated_results["sources_searched"].append("wikipedia")
            aggregated_results["results_by_source"]["wikipedia"] = wiki_results
            
            if wiki_results["success"]:
                aggregated_results["total_results"] += len(wiki_results["results"])
            else:
                aggregated_results["errors"].append(f"Wikipedia: {wiki_results['error']}")
        
        # Search Google if requested and available  
        if "google" in include_sources and self.google_search:
            google_results = self.search_google(query)
            aggregated_results["sources_searched"].append("google")
            aggregated_results["results_by_source"]["google"] = google_results
            
            if google_results["success"]:
                aggregated_results["total_results"] += len(google_results["results"])
            else:
                aggregated_results["errors"].append(f"Google: {google_results['error']}")
        
        # Determine overall success
        aggregated_results["success"] = aggregated_results["total_results"] > 0
        
        return aggregated_results
    
    def search(self, query: str, source: str = "auto") -> Dict[str, Any]:
        """
        Unified search method that automatically selects the best source or uses a specific one.
        
        Args:
            query: Search query string
            source: Search source ('auto', 'wikipedia', 'google', 'all')
            
        Returns:
            Dict containing search results
        """
        logger.info(f"Executing search with source='{source}' for query: '{query}'")
        
        if source == "wikipedia":
            return self.search_wikipedia(query)
        elif source == "google":
            return self.search_google(query)
        elif source == "all":
            return self.search_all(query)
        elif source == "auto":
            # Auto-select best source based on query characteristics
            query_lower = query.lower()
            
            # Use Wikipedia for factual/encyclopedia queries
            wiki_keywords = ["what is", "who is", "definition", "explain", "history of", "biography"]
            if any(keyword in query_lower for keyword in wiki_keywords):
                result = self.search_wikipedia(query)
                if result["success"] and result["results"]:
                    return result
            
            # Fall back to Google search
            return self.search_google(query)
        else:
            return {
                "success": False,
                "query": query,
                "results": [],
                "error": f"Unknown source: {source}. Use 'auto', 'wikipedia', 'google', or 'all'"
            }
    
    def get_available_sources(self) -> List[str]:
        """
        Get list of available search sources.
        
        Returns:
            List of available source names
        """
        sources = []
        if self.wikipedia_search:
            sources.append("wikipedia")
        if self.google_search:
            sources.append("google")
        return sources
    
    def get_search_status(self) -> Dict[str, Any]:
        """
        Get status of search toolkits.
        
        Returns:
            Dict containing status information
        """
        return {
            "wikipedia_available": self.wikipedia_search is not None,
            "google_available": self.google_search is not None,
            "available_sources": self.get_available_sources(),
            "toolkits_initialized": {
                "wikipedia": self.wikipedia_toolkit is not None,
                "google": self.google_toolkit is not None
            }
        }