#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure UTF-8 output
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
api_endpoint = "http://10.30.22.33:29222/searchGoogle"

# Function
def get_news(textSearch, isParseDetailContent, limit=1):
    params = {
        "searchKind": 12,
        "isParseDetailContent": isParseDetailContent,
        "textSearch": textSearch
    }
    response = requests.get(api_endpoint, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    related_news = ""
    for item in data["data"]["objResult"]["lsItems"][:limit]:
        formated_json = {
            "full_news": item["fullText"] if isParseDetailContent==True else "",
            "news_description": item["desc"] if isParseDetailContent==False else "",
            "published_date": item.get("strTs", ""),
            "url": item.get("url", "")
        }
        related_news += str(formated_json) + "\n"
    return related_news
    


if __name__ == "__main__":
    #-- Parser
    parser = argparse.ArgumentParser(description='Fetch latest news from BBC')
    parser.add_argument('--need_detail', type=bool, default=True, help='True if need full text of the news')
    parser.add_argument('--keyword_search', type=str, required=True, help='Keyword that need to search')
    args = parser.parse_args()

    print(get_news(
        textSearch=args.keyword_search,
        isParseDetailContent=args.need_detail
    ))




