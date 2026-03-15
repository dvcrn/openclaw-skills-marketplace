#!/usr/bin/env python3
"""
CCFI Data Query Tool
"""

import requests
import re

API_BASE = "http://106.54.203.43:8001"

def get_latest():
    """Get latest CCFI data"""
    r = requests.get(f"{API_BASE}/ccfi/latest", timeout=10)
    data = r.json()
    return f"""📊 **CCFI Latest Data**

• Date: {data['date']}
• Index: {data['ccfi_index']}
• MoM Change: {data['mom_change']}%
"""

def get_stats():
    """Get CCFI statistics"""
    r = requests.get(f"{API_BASE}/ccfi/stats", timeout=10)
    data = r.json()
    return f"""📈 **CCFI Statistics**

• Total Records: {data['total_count']}
• Latest Date: {data['latest_date']}
• Earliest Date: {data['earliest_date']}
• Max Index: {data['max_index']}
• Min Index: {data['min_index']}
• Avg Index: {data['avg_index']:.2f}
"""

def get_history(start_date=None, end_date=None, limit=30):
    """Get historical data"""
    params = {"limit": limit}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    
    r = requests.get(f"{API_BASE}/ccfi", params=params, timeout=10)
    data = r.json()
    
    if not data["data"]:
        return "No data found"
    
    result = "📊 **CCFI Historical Data**\n\n"
    result += "| Date | Index | MoM Change |\n"
    result += "|------|-------|------------|\n"
    
    for item in data["data"][:20]:
        change = f"{item['mom_change']}%" if item['mom_change'] else "-"
        result += f"| {item['date']} | {item['ccfi_index']} | {change} |\n"
    
    if data["total"] > 20:
        result += f"\n... Total {data['total']} records"
    
    return result

def parse_query(query: str) -> str:
    """Parse user query"""
    query = query.lower().strip()
    
    # Latest data
    if "latest" in query or query == "ccfi":
        return get_latest()
    
    # Statistics
    if "stat" in query:
        return get_stats()
    
    # Date range: YYYY-MM-DD to YYYY-MM-DD
    range_match = re.search(r'(\d{4})-?(\d{2})?-?(\d{2})?\s+to\s+(\d{4})-?(\d{2})?-?(\d{2})?', query)
    if range_match:
        start = range_match.group(1)
        end = range_match.group(4)
        if range_match.group(2):
            start += "-" + range_match.group(2)
            if range_match.group(3):
                start += "-" + range_match.group(3)
        if range_match.group(5):
            end += "-" + range_match.group(5)
            if range_match.group(6):
                end += "-" + range_match.group(6)
        return get_history(start, end)
    
    # Year query
    year_match = re.search(r'20\d{2}', query)
    if year_match:
        year = year_match.group()
        return get_history(f"{year}-01-01", f"{year}-12-31")
    
    # Default: latest
    return get_latest()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(parse_query(" ".join(sys.argv[1:])))
    else:
        print(parse_query("latest"))
