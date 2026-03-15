#!/usr/bin/env python3
"""
APIClaw NLU Router
Parses natural language queries and extracts intent and parameters.
Supports both English and Chinese queries.
"""

import re
from typing import Dict, Any, Tuple, Optional

# Intent patterns with keywords in multiple languages
INTENT_PATTERNS = {
    "categories": {
        "keywords": [
            "category", "categories", "类目", "分类", "category list",
            "有哪些类目", "所有类目", "类目列表"
        ],
        "endpoint": "/openapi/v2/categories"
    },
    "markets_search": {
        "keywords": [
            "market", "markets", "analyze market", "market analysis",
            "市场", "市场分析", "analyze category", "类目分析"
        ],
        "endpoint": "/openapi/v2/markets/search"
    },
    "products_search": {
        "keywords": [
            "find", "search", "look for", "查询", "搜索", "查找",
            "find products", "search for", "找", "有没有"
        ],
        "endpoint": "/openapi/v2/products/search"
    },
    "competitor_lookup": {
        "keywords": [
            "competitor", "competitors", "competition", "brand",
            "竞品", "竞争对手", "竞争", "品牌分析", "by brand"
        ],
        "endpoint": "/openapi/v2/products/competitor-lookup"
    },
    "realtime_product": {
        "keywords": [
            "details", "detail", "product detail", "get info", "show me",
            "详情", "产品详情", "查看", "详细信息", "realtime", "实时"
        ],
        "endpoint": "/openapi/v2/realtime/product"
    }
}

# Category aliases mapping
CATEGORY_ALIASES = {
    # English
    "electronics": "Electronics",
    "electronic": "Electronics",
    "home": "Home & Kitchen",
    "kitchen": "Home & Kitchen",
    "sports": "Sports & Outdoors",
    "outdoor": "Sports & Outdoors",
    "beauty": "Beauty & Personal Care",
    "personal care": "Beauty & Personal Care",
    "toys": "Toys & Games",
    "games": "Toys & Games",
    "books": "Books",
    "clothing": "Clothing, Shoes & Jewelry",
    "shoes": "Clothing, Shoes & Jewelry",
    "jewelry": "Clothing, Shoes & Jewelry",
    "health": "Health & Household",
    "household": "Health & Household",
    "pet": "Pet Supplies",
    "pets": "Pet Supplies",
    "baby": "Baby Products",
    "grocery": "Grocery & Gourmet Food",
    "food": "Grocery & Gourmet Food",
    "automotive": "Automotive",
    "car": "Automotive",
    "tools": "Tools & Home Improvement",
    "home improvement": "Tools & Home Improvement",
    "office": "Office Products",
    "musical": "Musical Instruments",
    "instruments": "Musical Instruments",
    "cell phones": "Cell Phones & Accessories",
    "accessories": "Cell Phones & Accessories",
    "computers": "Computers",
    "camera": "Camera & Photo",
    "photo": "Camera & Photo",
    
    # Chinese
    "电子": "Electronics",
    "电子产品": "Electronics",
    "家居": "Home & Kitchen",
    "厨房": "Home & Kitchen",
    "运动": "Sports & Outdoors",
    "户外": "Sports & Outdoors",
    "美容": "Beauty & Personal Care",
    "个护": "Beauty & Personal Care",
    "玩具": "Toys & Games",
    "游戏": "Toys & Games",
    "图书": "Books",
    "服装": "Clothing, Shoes & Jewelry",
    "鞋": "Clothing, Shoes & Jewelry",
    "首饰": "Clothing, Shoes & Jewelry",
    "健康": "Health & Household",
    "家居用品": "Health & Household",
    "宠物": "Pet Supplies",
    "婴儿": "Baby Products",
    "食品": "Grocery & Gourmet Food",
    "杂货": "Grocery & Gourmet Food",
    "汽车": "Automotive",
    "工具": "Tools & Home Improvement",
    "办公": "Office Products",
    "乐器": "Musical Instruments",
    "手机": "Cell Phones & Accessories",
    "配件": "Cell Phones & Accessories",
    "电脑": "Computers",
    "相机": "Camera & Photo",
    "摄影": "Camera & Photo",
    "耳机": "Electronics",
    "headphones": "Electronics",
    "蓝牙": "Electronics",
    "bluetooth": "Electronics",
    "音箱": "Electronics",
    "speaker": "Electronics",
}

# Sort field mappings
SORT_MAPPINGS = {
    "sales": "monthlySales",
    "monthly sales": "monthlySales",
    "销量": "monthlySales",
    "revenue": "monthlyRevenue",
    "收入": "monthlyRevenue",
    "销售额": "monthlyRevenue",
    "price": "price",
    "价格": "price",
    "rating": "rating",
    "评分": "rating",
    "review": "reviewCount",
    "reviews": "reviewCount",
    "评论": "reviewCount",
    "bsr": "bsr",
    "rank": "bsr",
    "排名": "bsr",
    "date": "listingDate",
    "listing date": "listingDate",
    "上架时间": "listingDate",
}


def parse_query(query: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parse a natural language query and extract intent and parameters.
    
    Args:
        query: Natural language query string
        
    Returns:
        Tuple of (intent, parameters)
    """
    query_lower = query.lower().strip()
    
    # Determine intent
    intent = determine_intent(query_lower)
    
    # Extract parameters
    params = extract_params(query)
    
    return intent, params


def determine_intent(query: str) -> str:
    """Determine the intent from the query."""
    
    # Check for ASIN pattern (10-character, starts with B followed by digit)
    asin_pattern = r'\b[Bb][0-9][A-Za-z0-9]{8}\b'
    has_asin = re.search(asin_pattern, query)
    
    # Check for product detail queries (has ASIN + detail keywords)
    if has_asin and any(kw in query for kw in ["realtime", "实时", "detail", "详情", "查看", "show me", "get info"]):
        return "realtime_product"
    
    # Check for market analysis queries (higher priority than categories)
    if any(kw in query for kw in ["market analysis", "analyze market", "市场分析", "analyze category", "类目分析"]):
        return "markets_search"
    
    # Check for category list queries
    if any(kw in query for kw in ["list categories", "all categories", "有哪些类目", "类目列表", "所有类目"]):
        return "categories"
    
    # Check for competitor/brand queries
    if any(kw in query for kw in ["competitor", "competitors", "竞品", "竞争对手", "by brand", "品牌分析"]):
        return "competitor_lookup"
    
    # Check for market search (general market keyword without analysis context)
    if any(kw in query for kw in ["market", "markets", "市场"]):
        return "markets_search"
    
    # Check for single category query
    if any(kw in query for kw in ["category", "categories", "类目", "分类"]):
        return "categories"
    
    # Check for product detail queries
    if any(kw in query for kw in ["detail", "details", "详情", "查看", "show me", "get info"]):
        return "realtime_product"
    
    # Default to product search
    return "products_search"


def extract_params(query: str) -> Dict[str, Any]:
    """Extract parameters from the query."""
    params = {}
    query_lower = query.lower()
    
    # Extract ASIN (Amazon Standard Identification Number)
    # ASINs are typically 10 characters, starting with B for products
    asin_match = re.search(r'\b([Bb][0-9][A-Za-z0-9]{8})\b', query)
    if asin_match:
        params["asin"] = asin_match.group(1).upper()
    
    # Extract keyword (remove common stop words and ASIN)
    keyword = extract_keyword(query)
    if keyword:
        params["keyword"] = keyword
    
    # Extract brand
    brand_match = re.search(r'(?:brand|品牌)\s*[:：]?\s*([A-Za-z0-9\s]+?)(?:\s+(?:in|category|类目|under|below)|\s*$)', query, re.IGNORECASE)
    if brand_match:
        params["brand"] = brand_match.group(1).strip()
    
    # Extract price range
    price_params = extract_price_params(query_lower)
    params.update(price_params)
    
    # Extract rating (patterns: 4 stars, 4+ stars, 4.5星, etc.)
    rating_match = re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*(?:stars?|星|星级|评分)', query_lower)
    if rating_match:
        params["ratingMin"] = float(rating_match.group(1))
    
    # Extract BSR range
    bsr_match = re.search(r'bsr\s*(\d+)(?:\s*-\s*(\d+))?', query_lower)
    if bsr_match:
        params["bsrMin"] = int(bsr_match.group(1))
        if bsr_match.group(2):
            params["bsrMax"] = int(bsr_match.group(2))
    
    # Extract category
    category = extract_category(query)
    if category:
        params["categoryKeyword"] = category
        # Also set categoryPath for some endpoints
        params["categoryPath"] = [category]
    
    # Extract sort parameters
    sort_match = re.search(r'(?:sort(?:ed)?\s+by|按|排序)\s*[:：]?\s*(\w+)', query_lower)
    if sort_match:
        sort_field = sort_match.group(1).lower()
        if sort_field in SORT_MAPPINGS:
            params["sortBy"] = SORT_MAPPINGS[sort_field]
    
    # Extract sort order
    if any(kw in query_lower for kw in ["ascending", "asc", "升序", "从低到高"]):
        params["sortOrder"] = "asc"
    elif any(kw in query_lower for kw in ["descending", "desc", "降序", "从高到低"]):
        params["sortOrder"] = "desc"
    
    # Extract limit/page size
    limit_match = re.search(r'(?:top|前|limit)\s*(\d+)', query_lower)
    if limit_match:
        params["pageSize"] = int(limit_match.group(1))
    
    # Extract marketplace
    if "uk" in query_lower or "英国" in query:
        params["marketplace"] = "UK"
    else:
        params["marketplace"] = "US"  # Default
    
    return params


def extract_keyword(query: str) -> Optional[str]:
    """Extract the main keyword from the query."""
    # Remove common prefixes
    prefixes = [
        r'^find\s+',
        r'^search\s+(?:for\s+)?',
        r'^look\s+for\s+',
        r'^查询',
        r'^搜索',
        r'^查找',
        r'^找',
        r'^有没有',
    ]
    
    cleaned = query
    for prefix in prefixes:
        cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)
    
    # Remove ASIN (valid ASINs start with B followed by digit)
    cleaned = re.sub(r'\b[Bb][0-9][A-Za-z0-9]{8}\b', '', cleaned)
    
    # Remove price-related phrases - must include dollar sign or number context
    # Pattern: under/below/over/above $X or X dollars (with optional space between $ and number)
    cleaned = re.sub(r'(?:under|below|over|above|less than|more than)\s+(?:\$\s*\d+(?:\.\d+)?(?:\s*dollars?)?|\d+(?:\.\d+)?\s*dollars?)', ' ', cleaned, flags=re.IGNORECASE)
    # Pattern: $X (dollar sign followed by number)
    cleaned = re.sub(r'\$\s*\d+(?:\.\d+)?(?:\s*dollars?)?', ' ', cleaned, flags=re.IGNORECASE)
    # Pattern: between $X and $Y
    cleaned = re.sub(r'between\s+\$?\d+\s+and\s+\$?\d+', ' ', cleaned, flags=re.IGNORECASE)
    # Chinese patterns: 价格/价钱/低于/高于 followed by number (with optional currency symbol)
    # Pattern: 价格/价钱 followed by optional currency and number, or followed by 低于/高于 then number
    cleaned = re.sub(r'(?:价格|价钱)\s*(?:[\$¥￥]?\s*\d+|(?:低于|高于|不超过|多于)\s*[\$¥￥]?\s*\d+)', ' ', cleaned)
    # Pattern: 低于/高于/不超过/多于 followed by optional currency and number
    cleaned = re.sub(r'(?:低于|高于|不超过|多于)\s*[\$¥￥]?\s*\d+', ' ', cleaned)
    
    # Remove category phrases
    cleaned = re.sub(r'(?:in|category|类目)\s+\w+', '', cleaned, flags=re.IGNORECASE)
    
    # Remove rating phrases (including "with X stars" patterns)
    cleaned = re.sub(r'(?:with|有)?\s*\d+(?:\.\d+)?\s*\+?\s*(?:stars?|星|星级|评分)', '', cleaned, flags=re.IGNORECASE)
    
    # Remove sort phrases
    cleaned = re.sub(r'(?:sort\s+by|按|排序).*', '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' ,.:;')
    
    # Return if we have something meaningful
    if len(cleaned) > 2:
        return cleaned
    
    return None


def extract_price_params(query: str) -> Dict[str, Any]:
    """Extract price range parameters."""
    params = {}
    
    # Pattern: under/below/less than $X
    under_match = re.search(r'(?:under|below|less than|低于|少于|不超过)\s*\$?(\d+)', query)
    if under_match:
        params["priceMax"] = float(under_match.group(1))
    
    # Pattern: over/above/more than $X
    over_match = re.search(r'(?:over|above|more than|高于|多于|超过)\s*\$?(\d+)', query)
    if over_match:
        params["priceMin"] = float(over_match.group(1))
    
    # Pattern: between $X and $Y
    between_match = re.search(r'(?:between|从).*?\$?(\d+).*?(?:and|到|至).*?\$?(\d+)', query)
    if between_match:
        params["priceMin"] = float(between_match.group(1))
        params["priceMax"] = float(between_match.group(2))
    
    # Pattern: $X-$Y
    range_match = re.search(r'\$(\d+)\s*-\s*\$?(\d+)', query)
    if range_match:
        params["priceMin"] = float(range_match.group(1))
        params["priceMax"] = float(range_match.group(2))
    
    return params


def extract_category(query: str) -> Optional[str]:
    """Extract category from the query."""
    query_lower = query.lower()
    
    # Check for explicit category mentions
    for alias, category in CATEGORY_ALIASES.items():
        # Match whole words
        pattern = r'\b' + re.escape(alias.lower()) + r'\b'
        if re.search(pattern, query_lower):
            return category
    
    # Check for "in [category]" pattern
    in_match = re.search(r'(?:in|category|类目)\s+([A-Za-z\s&]+?)(?:\s+(?:with|under|below|price)|\s*$)', query, re.IGNORECASE)
    if in_match:
        cat = in_match.group(1).strip()
        if cat in CATEGORY_ALIASES:
            return CATEGORY_ALIASES[cat]
        return cat
    
    return None


def translate_to_api_call(intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate intent and parameters to an API call specification.
    
    Args:
        intent: The determined intent
        params: Extracted parameters
        
    Returns:
        API call specification dict
    """
    endpoint_map = {
        "categories": "/openapi/v2/categories",
        "markets_search": "/openapi/v2/markets/search",
        "products_search": "/openapi/v2/products/search",
        "competitor_lookup": "/openapi/v2/products/competitor-lookup",
        "realtime_product": "/openapi/v2/realtime/product",
    }
    
    endpoint = endpoint_map.get(intent, "/openapi/v2/products/search")
    
    # Build request body based on endpoint
    body = build_request_body(intent, params)
    
    return {
        "method": "POST",
        "endpoint": endpoint,
        "body": body
    }


def build_request_body(intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Build the request body for the given intent and parameters."""
    body = {}
    
    # Common parameters for all endpoints
    if "marketplace" in params:
        body["marketplace"] = params["marketplace"]
    
    if intent == "categories":
        # Categories endpoint
        if "categoryKeyword" in params:
            body["categoryKeyword"] = params["categoryKeyword"]
        # Default: return all root categories
        
    elif intent == "markets_search":
        # Markets search endpoint
        if "categoryKeyword" in params:
            body["categoryKeyword"] = params["categoryKeyword"]
        if "categoryPath" in params:
            body["categoryPath"] = params["categoryPath"]
        
        # Price filters
        if "priceMin" in params:
            body["sampleAvgPriceMin"] = params["priceMin"]
        if "priceMax" in params:
            body["sampleAvgPriceMax"] = params["priceMax"]
        
        # Rating filters
        if "ratingMin" in params:
            body["sampleAvgRatingMin"] = params["ratingMin"]
        
        # Sorting
        if "sortBy" in params:
            body["sortBy"] = params["sortBy"]
        if "sortOrder" in params:
            body["sortOrder"] = params["sortOrder"]
        else:
            body["sortOrder"] = "desc"
        
        # Pagination
        if "pageSize" in params:
            body["pageSize"] = params["pageSize"]
        else:
            body["pageSize"] = 20
        
        body["page"] = 1
        
        # Default values
        body["dateRange"] = "30d"
        body["sampleType"] = "by_sale_100"
        body["newProductPeriod"] = "3"
        body["topN"] = "10"
        
    elif intent in ["products_search", "competitor_lookup"]:
        # Products search and competitor lookup endpoints
        if "keyword" in params:
            body["keyword"] = params["keyword"]
        if "asin" in params:
            body["asin"] = params["asin"]
        if "brand" in params:
            body["brand"] = params["brand"]
        if "categoryPath" in params:
            body["categoryPath"] = params["categoryPath"]
        
        # Price filters
        if "priceMin" in params:
            body["priceMin"] = params["priceMin"]
        if "priceMax" in params:
            body["priceMax"] = params["priceMax"]
        
        # Rating filters
        if "ratingMin" in params:
            body["ratingMin"] = params["ratingMin"]
        if "ratingMax" in params:
            body["ratingMax"] = params["ratingMax"]
        
        # BSR filters
        if "bsrMin" in params:
            body["bsrMin"] = params["bsrMin"]
        if "bsrMax" in params:
            body["bsrMax"] = params["bsrMax"]
        
        # Sorting
        if "sortBy" in params:
            body["sortBy"] = params["sortBy"]
        else:
            body["sortBy"] = "monthlySales"
        
        if "sortOrder" in params:
            body["sortOrder"] = params["sortOrder"]
        else:
            body["sortOrder"] = "desc"
        
        # Pagination
        if "pageSize" in params:
            body["pageSize"] = params["pageSize"]
        else:
            body["pageSize"] = 20
        
        body["page"] = 1
        
        # Default values
        body["dateRange"] = "30d"
        
    elif intent == "realtime_product":
        # Realtime product endpoint
        if "asin" in params:
            body["asin"] = params["asin"]
        else:
            # Try to extract ASIN from keyword if present
            if "keyword" in params:
                asin_match = re.search(r'\b([Bb][0-9][A-Za-z0-9]{8})\b', params["keyword"])
                if asin_match:
                    body["asin"] = asin_match.group(1).upper()
    
    return body
