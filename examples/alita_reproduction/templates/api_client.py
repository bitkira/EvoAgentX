"""
API Client Script Template

This template provides a basic structure for API client scripts.
Use this template to create scripts that interact with REST APIs.

Template Variables:
- api_base_url: Base URL of the API
- api_name: Name of the API service
- auth_method: Authentication method (none, token, basic, key)
- output_format: Output format for API responses (json, csv, txt)
"""

#!/usr/bin/env python3

import requests
import json
import logging
import time
import os
import sys
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class APIClient:
    """
    API client for {{api_name}}
    """
    
    def __init__(
        self,
        base_url: str,
        auth_method: str = "none",
        auth_token: Optional[str] = None,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        rate_limit: float = 1.0
    ):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API
            auth_method: Authentication method (none, token, basic, key)
            auth_token: Bearer token for token authentication
            api_key: API key for key-based authentication
            username: Username for basic authentication
            password: Password for basic authentication
            timeout: Request timeout in seconds
            rate_limit: Minimum seconds between requests
        """
        self.base_url = base_url.rstrip('/')
        self.auth_method = auth_method
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        # Set up session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ALITA API Client 1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Configure authentication
        self._configure_authentication(auth_token, api_key, username, password)
        
        logger.info(f"APIClient initialized: {self.base_url}")
        logger.info(f"Authentication method: {self.auth_method}")
    
    def _configure_authentication(
        self,
        auth_token: Optional[str],
        api_key: Optional[str],
        username: Optional[str],
        password: Optional[str]
    ) -> None:
        """Configure authentication based on method."""
        if self.auth_method == "token" and auth_token:
            self.session.headers['Authorization'] = f'Bearer {auth_token}'
        elif self.auth_method == "key" and api_key:
            self.session.headers['X-API-Key'] = api_key
        elif self.auth_method == "basic" and username and password:
            self.session.auth = (username, password)
        elif self.auth_method != "none":
            logger.warning(f"Authentication method '{self.auth_method}' configured but credentials missing")
    
    def _rate_limit_check(self) -> None:
        """Ensure rate limiting between requests."""
        if self.rate_limit > 0:
            time_since_last = time.time() - self.last_request_time
            if time_since_last < self.rate_limit:
                sleep_time = self.rate_limit - time_since_last
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            json_data: JSON data for request body
            
        Returns:
            Response data dictionary or None if failed
        """
        try:
            self._rate_limit_check()
            
            url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
            logger.debug(f"Making {method} request to: {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                timeout=self.timeout
            )
            
            logger.info(f"{method} {url} - Status: {response.status_code}")
            
            # Handle different response status codes
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"raw_response": response.text}
            elif response.status_code == 201:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"created": True, "raw_response": response.text}
            elif response.status_code == 204:
                return {"success": True, "message": "No content"}
            elif response.status_code == 401:
                logger.error("Authentication failed")
                return {"error": "Authentication failed", "status_code": 401}
            elif response.status_code == 403:
                logger.error("Access forbidden")
                return {"error": "Access forbidden", "status_code": 403}
            elif response.status_code == 404:
                logger.error(f"Endpoint not found: {url}")
                return {"error": "Endpoint not found", "status_code": 404}
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded")
                return {"error": "Rate limit exceeded", "status_code": 429}
            else:
                logger.error(f"API request failed with status {response.status_code}")
                return {
                    "error": f"Request failed with status {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout} seconds")
            return {"error": "Request timeout"}
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return {"error": "Connection error"}
        except Exception as e:
            logger.error(f"Unexpected error making request: {str(e)}")
            return {"error": str(e)}
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make GET request."""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make POST request."""
        return self._make_request('POST', endpoint, data=data, json_data=json_data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make PUT request."""
        return self._make_request('PUT', endpoint, data=data, json_data=json_data)
    
    def delete(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make DELETE request."""
        return self._make_request('DELETE', endpoint)
    
    def get_paginated_data(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        page_param: str = "page",
        limit_param: str = "limit",
        max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch paginated data from API.
        
        Args:
            endpoint: API endpoint
            params: Base query parameters
            page_param: Parameter name for page number
            limit_param: Parameter name for page size
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of all data items across pages
        """
        all_data = []
        params = params or {}
        
        for page in range(1, max_pages + 1):
            current_params = params.copy()
            current_params[page_param] = page
            
            logger.info(f"Fetching page {page}...")
            response = self.get(endpoint, params=current_params)
            
            if not response or "error" in response:
                logger.warning(f"Error or no data on page {page}")
                break
            
            # Extract data - customize based on API response structure
            page_data = response.get('data', [])
            if not page_data:
                logger.info(f"No more data on page {page}")
                break
            
            all_data.extend(page_data)
            logger.info(f"Collected {len(page_data)} items from page {page}")
            
            # Check if this is the last page
            if len(page_data) < params.get(limit_param, 20):
                logger.info("Reached last page")
                break
        
        logger.info(f"Total collected items: {len(all_data)}")
        return all_data


def save_api_data(data: Union[Dict, List], output_file: str, format_type: str = "json") -> bool:
    """
    Save API response data to file.
    
    Args:
        data: Data to save
        output_file: Output file path
        format_type: Output format (json, csv, txt)
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        if format_type == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format_type == "csv":
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                df.to_csv(output_file, index=False, encoding='utf-8')
            else:
                logger.warning("CSV format requires list of dictionaries")
                return False
        
        elif format_type == "txt":
            with open(output_file, 'w', encoding='utf-8') as f:
                if isinstance(data, (dict, list)):
                    f.write(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    f.write(str(data))
        
        logger.info(f"Data saved to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        return False


def main():
    """
    Main function to execute API client workflow.
    """
    # Configuration
    api_base_url = "{{api_base_url}}"
    output_file = "api_data.{{output_format}}"
    
    # Validate configuration
    if not api_base_url or api_base_url.startswith("{{"):
        logger.error("API base URL not specified or still contains placeholder")
        sys.exit(1)
    
    # Initialize API client
    client = APIClient(
        base_url=api_base_url,
        auth_method="{{auth_method}}",
        # Add authentication parameters as needed:
        # auth_token="your_token_here",
        # api_key="your_api_key_here",
        # username="your_username",
        # password="your_password"
    )
    
    try:
        logger.info("Starting API client workflow...")
        
        # Example: Fetch data from a specific endpoint
        # Customize this section based on your API requirements
        
        endpoint = "/api/data"  # Replace with actual endpoint
        response = client.get(endpoint)
        
        if response and "error" not in response:
            logger.info("Successfully fetched data from API")
            
            # Save the response data
            if save_api_data(response, output_file, "{{output_format}}"):
                logger.info(f"Data saved to {output_file}")
            else:
                logger.error("Failed to save data")
                sys.exit(1)
        else:
            logger.error("Failed to fetch data from API")
            if response:
                logger.error(f"Error: {response.get('error', 'Unknown error')}")
            sys.exit(1)
        
        print("✅ API client workflow completed successfully!")
        logger.info("API client workflow completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in main workflow: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()