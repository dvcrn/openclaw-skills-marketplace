from typing import List
import requests
import json

# 请求头信息
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Content-Type": "application/json",
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    "Referer": "https://www.eqxiu.com/",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

eqxiustore_host_url = "https://msearch-api.eqxiu.com"
eqxiustore_search_url = "https://msearch-api.eqxiu.com/m/search/searchProducts"
basepreview_url = "https://www.eqxiu.com/mall/detail-{className}/"


class EqxiuStoreWebSearch:
    name: str = "eqxiu_template_search"
    description: str = """进行易企秀模版搜素，返回模版内容"""
    def getClassName(self, attrGroupId: int) -> str:      
        return 'h5' if attrGroupId == 2 else 'h5l' if attrGroupId == 10 else 'h5e' if attrGroupId == 11 else 'h2' if attrGroupId == 7 else 'gc' if attrGroupId == 14 else 'video' if attrGroupId == 15 else 'ebook' if attrGroupId == 18 else ''

    def execute(self, query: str, page_no :int =0, num_results: int = 10) -> List[str]:
        session = requests.Session()
        session.headers = HEADERS
        jsonquery = {"keywords": f"{query}",  "sortBy": "common_total|desc", "pageNo": page_no,"pageSize": num_results}
        res = session.post(url=eqxiustore_search_url, json=jsonquery)
        res.encoding = "utf-8"
        result = json.loads(res.text)
        if result["obj"]["total"] == 0:
            return []
        result_list = []
        for k in result["obj"]["dataList"]:
            className = self.getClassName(k["attrGroupId"])
            preview_url = basepreview_url.format(className=className)
            result_list.append({"title": k["title"], "link":preview_url+ str(k["id"]), "description": k["description"], "pv":k["views"]})
        return result_list

if __name__ == "__main__":
    import argparse
    import json
    
    from typing import List

    parser = argparse.ArgumentParser(description="Eqxiu Store Search")
    parser.add_argument( "--keywords", type=str, required=True, help="关键词")
    parser.add_argument("--pageNo", type=int, required=False, default=1, help="分页页码")
    parser.add_argument("--pageSize", type=int, required=False, default=10, help="每页条数")
    args = parser.parse_args()
    search = EqxiuStoreWebSearch()
    print(json.dumps(search.execute(args.keywords, args.pageNo, args.pageSize), ensure_ascii=False, indent=2)) 