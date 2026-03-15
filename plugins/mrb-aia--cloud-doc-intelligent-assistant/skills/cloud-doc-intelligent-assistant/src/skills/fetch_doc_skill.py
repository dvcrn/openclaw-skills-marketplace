"""fetch_doc skill - 抓取指定云厂商的产品文档"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..contracts.response import ErrorCode, SkillResponse
from ..models import Document
from ..utils import compute_content_hash
from .runtime import SkillRuntime

SUPPORTED_CLOUDS = {"aliyun", "tencent", "baidu", "volcano"}


class FetchDocSkill:
    def __init__(self, runtime: SkillRuntime):
        self._rt = runtime

    def run(
        self,
        cloud: str,
        product: Optional[str] = None,
        doc_ref: Optional[str] = None,
        with_summary: bool = False,
        max_pages: int = 200,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        # 参数校验
        if not cloud:
            return SkillResponse.fail(ErrorCode.MISSING_PARAM, "cloud 参数必填").to_dict()
        if cloud not in SUPPORTED_CLOUDS:
            return SkillResponse.fail(
                ErrorCode.INVALID_PARAM, f"不支持的云厂商: {cloud}，支持: {', '.join(SUPPORTED_CLOUDS)}"
            ).to_dict()
        if not product and not doc_ref:
            return SkillResponse.fail(
                ErrorCode.MISSING_PARAM, "product 和 doc_ref 至少填一个"
            ).to_dict()

        try:
            crawler = self._rt.get_crawler(cloud)
        except ValueError as e:
            return SkillResponse.fail(ErrorCode.INVALID_PARAM, str(e)).to_dict()

        # doc_ref 模式：直接抓取单篇
        if doc_ref:
            return self._fetch_single(cloud, crawler, doc_ref, with_summary)

        # product 模式：发现文档列表
        return self._fetch_product(cloud, crawler, product, keyword, max_pages, with_summary)

    def _fetch_single(self, cloud: str, crawler, doc_ref: str, with_summary: bool) -> Dict[str, Any]:
        try:
            if cloud == "aliyun":
                doc = crawler.crawl_page(doc_ref)
                items = [self._doc_to_item(doc, with_summary)]
            elif cloud == "tencent":
                # doc_ref 格式: "product_id/doc_id" 或纯 doc_id
                parts = doc_ref.split("/")
                if len(parts) == 2:
                    raw = crawler.fetch_doc(parts[1], parts[0])
                else:
                    raw = crawler.fetch_doc(doc_ref)
                if not raw:
                    return SkillResponse.fail(ErrorCode.CRAWL_FAILED, f"无法获取文档: {doc_ref}").to_dict()
                items = [self._raw_to_item(cloud, raw, with_summary)]
            elif cloud == "baidu":
                # doc_ref 格式: "product/slug"
                parts = doc_ref.split("/", 1)
                if len(parts) != 2:
                    return SkillResponse.fail(ErrorCode.INVALID_PARAM, "百度云 doc_ref 格式: product/slug").to_dict()
                raw = crawler.fetch_doc(parts[0], parts[1])
                if not raw:
                    return SkillResponse.fail(ErrorCode.CRAWL_FAILED, f"无法获取文档: {doc_ref}").to_dict()
                items = [self._raw_to_item(cloud, raw, with_summary)]
            elif cloud == "volcano":
                # doc_ref 格式: "lib_id/doc_id"
                parts = doc_ref.split("/")
                if len(parts) != 2:
                    return SkillResponse.fail(ErrorCode.INVALID_PARAM, "火山云 doc_ref 格式: lib_id/doc_id").to_dict()
                raw = crawler.fetch_doc(parts[0], parts[1])
                if not raw:
                    return SkillResponse.fail(ErrorCode.CRAWL_FAILED, f"无法获取文档: {doc_ref}").to_dict()
                items = [self._raw_to_item(cloud, raw, with_summary)]
            else:
                return SkillResponse.fail(ErrorCode.INVALID_PARAM, f"不支持的云厂商: {cloud}").to_dict()
        except Exception as e:
            logging.error(f"fetch_doc 单篇抓取失败: {e}")
            return SkillResponse.fail(ErrorCode.CRAWL_FAILED, f"抓取失败: {e}").to_dict()

        return SkillResponse.ok(
            machine={"cloud": cloud, "mode": "doc_ref", "items": items, "total": len(items)},
            human={"summary_text": f"成功抓取 1 篇文档。"},
        ).to_dict()

    def _fetch_product(self, cloud: str, crawler, product: str, keyword: Optional[str],
                       max_pages: int, with_summary: bool) -> Dict[str, Any]:
        try:
            if cloud == "aliyun":
                aliases = crawler.discover_product_docs(product)
                items = []
                
                # 并发抓取文档
                def fetch_single_doc(alias):
                    try:
                        doc = crawler.crawl_page(alias)
                        # 如果指定了关键词，进行过滤
                        if keyword and keyword.strip():
                            if keyword.lower() not in doc.title.lower() and keyword.lower() not in doc.content.lower():
                                return None
                        return self._doc_to_item(doc, with_summary)
                    except Exception as e:
                        logging.warning(f"跳过文档 {alias}: {e}")
                        return None
                
                # 限制并发数量，避免过载
                max_workers = min(10, len(aliases))
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # 只提交 max_pages 数量的任务
                    aliases_to_fetch = aliases[:max_pages]
                    future_to_alias = {executor.submit(fetch_single_doc, alias): alias for alias in aliases_to_fetch}
                    
                    for future in as_completed(future_to_alias):
                        result = future.result()
                        if result:
                            items.append(result)
                            # 达到最大数量后停止
                            if len(items) >= max_pages:
                                break
            elif cloud == "tencent":
                raw_list = crawler.discover_product_docs(product, keyword=keyword or "", limit=max_pages)
                items = []
                for entry in raw_list:
                    try:
                        raw = crawler.fetch_doc(entry["doc_id"], entry.get("product_id", ""))
                        if raw:
                            items.append(self._raw_to_item(cloud, raw, with_summary))
                    except Exception as e:
                        logging.warning(f"跳过腾讯云文档 {entry.get('doc_id')}: {e}")
            elif cloud == "baidu":
                raw_list = crawler.discover_product_docs(product, limit=max_pages)
                items = []
                for entry in raw_list:
                    try:
                        raw = crawler.fetch_doc(entry["product"], entry["slug"])
                        if raw:
                            items.append(self._raw_to_item(cloud, raw, with_summary))
                    except Exception as e:
                        logging.warning(f"跳过百度云文档 {entry.get('slug')}: {e}")
            elif cloud == "volcano":
                raw_list = crawler.discover_product_docs(product, limit=max_pages)
                items = []
                for entry in raw_list:
                    try:
                        raw = crawler.fetch_doc(entry["lib_id"], entry["doc_id"])
                        if raw:
                            items.append(self._raw_to_item(cloud, raw, with_summary))
                    except Exception as e:
                        logging.warning(f"跳过火山云文档 {entry.get('doc_id')}: {e}")
            else:
                items = []
        except Exception as e:
            logging.error(f"fetch_doc product 模式失败: {e}")
            return SkillResponse.fail(ErrorCode.CRAWL_FAILED, f"抓取失败: {e}").to_dict()

        return SkillResponse.ok(
            machine={"cloud": cloud, "product": product, "mode": "product", "items": items, "total": len(items)},
            human={"summary_text": f"共找到 {len(items)} 篇与 {product} 相关的文档。"},
        ).to_dict()

    def _doc_to_item(self, doc: Document, with_summary: bool) -> Dict[str, Any]:
        item: Dict[str, Any] = {
            "title": doc.title,
            "url": doc.url,
            "doc_ref": doc.url,
            "content": doc.content,
            "last_modified": doc.last_modified.isoformat() if doc.last_modified else None,
        }
        if with_summary:
            try:
                item["summary"] = self._rt.summarizer.summarize_content(doc.title, doc.content)
            except Exception as e:
                item["summary"] = f"摘要生成失败: {e}"
        return item

    def _raw_to_item(self, cloud: str, raw: Dict[str, Any], with_summary: bool) -> Dict[str, Any]:
        title = raw.get("title", "")
        url = raw.get("url", "")
        last_modified = raw.get("last_modified") or raw.get("date") or raw.get("recent_release_time")
        content = raw.get("text", "")
        item: Dict[str, Any] = {
            "title": title,
            "url": url,
            "doc_ref": url,
            "last_modified": last_modified,
        }
        if with_summary and content:
            try:
                item["summary"] = self._rt.summarizer.summarize_content(title, content)
            except Exception as e:
                item["summary"] = f"摘要生成失败: {e}"
        return item
