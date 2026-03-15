#!/usr/bin/env python3
"""
APIClaw API Client
Handles HTTP requests to APIClaw API v2 with proper headers and error handling.
"""

import urllib.request
import urllib.error
import json
import ssl
from typing import Dict, Any, Optional


class APIClawClient:
    """Client for APIClaw API v2."""
    
    BASE_URL = "https://hermes.spider.yesy.dev"
    
    # Endpoint mappings
    ENDPOINTS = {
        "/openapi/v2/categories": "categories",
        "/openapi/v2/markets/search": "markets_search",
        "/openapi/v2/products/competitor-lookup": "competitor_lookup",
        "/openapi/v2/products/search": "products_search",
        "/openapi/v2/realtime/product": "realtime_product",
    }
    
    def __init__(self, api_key: str):
        """
        Initialize the client with an API key.
        
        Args:
            api_key: APIClaw API key
        """
        self.api_key = api_key
        self.ssl_context = ssl.create_default_context()
    
    # Quota exhausted message
    QUOTA_EXHAUSTED_MESSAGE = "You've used all your tokens. Please top up at https://www.APIClaw.io"
    
    def is_quota_exhausted_error(self, error_response: Dict[str, Any]) -> bool:
        """
        Check if the error is due to quota exhaustion.
        
        Args:
            error_response: The error response from API
            
        Returns:
            True if quota is exhausted
        """
        if not error_response:
            return False
        
        error_code = error_response.get("code", "")
        error_message = error_response.get("message", "").lower()
        
        # Check for quota-related error codes or messages
        quota_indicators = [
            "quota",
            "limit exceeded",
            "no quota",
            "out of quota",
            "token",
            "credits",
            "429"
        ]
        
        # Check error code
        if error_code in ["429", "QUOTA_EXHAUSTED", "NO_QUOTA", "LIMIT_EXCEEDED"]:
            return True
        
        # Check error message
        for indicator in quota_indicators:
            if indicator in error_message:
                return True
        
        return False
    
    def execute(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an API call based on the specification.
        
        Args:
            api_spec: API call specification with method, endpoint, and body
            
        Returns:
            API response as dict
        """
        method = api_spec.get("method", "POST")
        endpoint = api_spec.get("endpoint", "")
        body = api_spec.get("body", {})
        
        url = f"{self.BASE_URL}{endpoint}"
        
        # Build request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "APIClaw-NL-Client/1.0",
            "Accept": "application/json"
        }
        
        # Encode body
        data = json.dumps(body).encode("utf-8") if body else None
        
        # Create request
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method
        )
        
        try:
            # Execute request
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=60) as response:
                response_data = response.read().decode("utf-8")
                return json.loads(response_data)
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                error_json = json.loads(error_body)
                error_info = error_json.get("error", {
                    "code": str(e.code),
                    "message": error_json.get("detail", str(e.reason))
                })
                
                # Check for quota exhaustion
                if self.is_quota_exhausted_error(error_info):
                    return {
                        "success": False,
                        "error": {
                            "code": "QUOTA_EXHAUSTED",
                            "message": self.QUOTA_EXHAUSTED_MESSAGE
                        },
                        "data": None,
                        "meta": {}
                    }
                
                return {
                    "success": False,
                    "error": error_info,
                    "data": None,
                    "meta": {}
                }
            except json.JSONDecodeError:
                # Check for quota exhaustion in HTTP status
                if e.code == 429:
                    return {
                        "success": False,
                        "error": {
                            "code": "QUOTA_EXHAUSTED",
                            "message": self.QUOTA_EXHAUSTED_MESSAGE
                        },
                        "data": None,
                        "meta": {}
                    }
                
                return {
                    "success": False,
                    "error": {
                        "code": str(e.code),
                        "message": str(e.reason)
                    },
                    "data": None,
                    "meta": {}
                }
                
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": {
                    "code": "URL_ERROR",
                    "message": str(e.reason)
                },
                "data": None,
                "meta": {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "UNKNOWN_ERROR",
                    "message": str(e)
                },
                "data": None,
                "meta": {}
            }
    
    def get_categories(self, **params) -> Dict[str, Any]:
        """
        Get categories.
        
        Args:
            **params: Optional parameters (marketplace, categoryKeyword, etc.)
            
        Returns:
            API response
        """
        api_spec = {
            "method": "POST",
            "endpoint": "/openapi/v2/categories",
            "body": params
        }
        return self.execute(api_spec)
    
    def search_markets(self, **params) -> Dict[str, Any]:
        """
        Search markets.
        
        Args:
            **params: Search parameters (categoryKeyword, priceMin, priceMax, etc.)
            
        Returns:
            API response
        """
        # Set defaults
        defaults = {
            "dateRange": "30d",
            "sampleType": "by_sale_100",
            "newProductPeriod": "3",
            "topN": "10",
            "page": 1,
            "pageSize": 20,
            "sortOrder": "desc"
        }
        defaults.update(params)
        
        api_spec = {
            "method": "POST",
            "endpoint": "/openapi/v2/markets/search",
            "body": defaults
        }
        return self.execute(api_spec)
    
    def search_products(self, **params) -> Dict[str, Any]:
        """
        Search products.
        
        Args:
            **params: Search parameters (keyword, priceMin, priceMax, etc.)
            
        Returns:
            API response
        """
        # Set defaults
        defaults = {
            "dateRange": "30d",
            "page": 1,
            "pageSize": 20,
            "sortBy": "monthlySales",
            "sortOrder": "desc"
        }
        defaults.update(params)
        
        api_spec = {
            "method": "POST",
            "endpoint": "/openapi/v2/products/search",
            "body": defaults
        }
        return self.execute(api_spec)
    
    def competitor_lookup(self, **params) -> Dict[str, Any]:
        """
        Lookup competitors.
        
        Args:
            **params: Search parameters (keyword, brand, asin, etc.)
            
        Returns:
            API response
        """
        # Set defaults
        defaults = {
            "dateRange": "30d",
            "page": 1,
            "pageSize": 20,
            "sortBy": "monthlySales",
            "sortOrder": "desc"
        }
        defaults.update(params)
        
        api_spec = {
            "method": "POST",
            "endpoint": "/openapi/v2/products/competitor-lookup",
            "body": defaults
        }
        return self.execute(api_spec)
    
    def get_realtime_product(self, asin: str, marketplace: str = "US") -> Dict[str, Any]:
        """
        Get realtime product details.
        
        Args:
            asin: Product ASIN
            marketplace: Marketplace code (default: US)
            
        Returns:
            API response
        """
        api_spec = {
            "method": "POST",
            "endpoint": "/openapi/v2/realtime/product",
            "body": {
                "asin": asin,
                "marketplace": marketplace
            }
        }
        return self.execute(api_spec)
