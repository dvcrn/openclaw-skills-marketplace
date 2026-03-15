"""compare_docs skill - 对比两个云厂商的产品文档"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from ..contracts.response import ErrorCode, SkillResponse
from ..models import Document
from ..prompts.compare_prompt import build_compare_prompt
from ..utils import compute_content_hash
from .runtime import SkillRuntime

SUPPORTED_CLOUDS = {"aliyun", "tencent", "baidu", "volcano"}


class CompareDocsSkill:
    def __init__(self, runtime: SkillRuntime):
        self._rt = runtime

    def run(
        self,
        left: Dict[str, Any],
        right: Dict[str, Any],
        focus: Optional[str] = None,
    ) -> Dict[str, Any]:
        # 参数校验
        left_cloud = (left.get("cloud") or "").lower()
        right_cloud = (right.get("cloud") or "").lower()
        left_product = left.get("product") or left.get("doc_ref") or ""
        right_product = right.get("product") or right.get("doc_ref") or ""

        if not left_cloud or not right_cloud:
            return SkillResponse.fail(ErrorCode.MISSING_PARAM, "left.cloud 和 right.cloud 必填").to_dict()
        if left_cloud not in SUPPORTED_CLOUDS or right_cloud not in SUPPORTED_CLOUDS:
            return SkillResponse.fail(ErrorCode.INVALID_PARAM, f"不支持的云厂商").to_dict()
        if not left_product or not right_product:
            return SkillResponse.fail(ErrorCode.MISSING_PARAM, "left.product 和 right.product 必填").to_dict()

        # 抓取两侧文档
        try:
            left_content, left_title = self._fetch_content(left_cloud, left)
            right_content, right_title = self._fetch_content(right_cloud, right)
        except Exception as e:
            return SkillResponse.fail(ErrorCode.CRAWL_FAILED, f"文档抓取失败: {e}").to_dict()

        if not left_content:
            return SkillResponse.fail(ErrorCode.CRAWL_FAILED, f"无法获取 {left_cloud} {left_product} 文档").to_dict()
        if not right_content:
            return SkillResponse.fail(ErrorCode.CRAWL_FAILED, f"无法获取 {right_cloud} {right_product} 文档").to_dict()

        # 调 LLM 生成对比
        try:
            system_prompt, user_prompt = build_compare_prompt(
                left_cloud=left_cloud,
                left_product=left_product,
                left_title=left_title,
                left_content=left_content,
                right_cloud=right_cloud,
                right_product=right_product,
                right_title=right_title,
                right_content=right_content,
                focus=focus,
            )
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            raw_output = self._rt.summarizer.llm.generate(full_prompt, max_tokens=2000)
            comparison_data = self._parse_llm_output(raw_output)
        except Exception as e:
            logging.error(f"compare_docs LLM 调用失败: {e}")
            return SkillResponse.fail(ErrorCode.LLM_FAILED, f"LLM 对比失败: {e}").to_dict()

        comparison = comparison_data.get("comparison", [])
        summary = comparison_data.get("summary", "")

        # 构建 human markdown
        lines = [f"# {left_cloud} vs {right_cloud} {left_product} 差异\n"]
        if focus:
            lines.append(f"关注点：{focus}\n")
        for item in comparison:
            dim = item.get("dimension", "")
            l_status = item.get("left_status", "")
            r_status = item.get("right_status", "")
            diff = item.get("difference", "")
            lines.append(f"- **{dim}**: {left_cloud}={l_status}, {right_cloud}={r_status} — {diff}")
        if summary:
            lines.append(f"\n**总结**: {summary}")

        return SkillResponse.ok(
            machine={
                "left": {"cloud": left_cloud, "product": left_product, "title": left_title},
                "right": {"cloud": right_cloud, "product": right_product, "title": right_title},
                "focus": focus or "功能差异",
                "comparison": comparison,
            },
            human={"summary_markdown": "\n".join(lines)},
        ).to_dict()

    def _fetch_content(self, cloud: str, side: Dict[str, Any]) -> tuple:
        """抓取一侧文档内容，优先从缓存读取"""
        product = side.get("product", "")
        doc_ref = side.get("doc_ref", "")
        keyword = side.get("keyword", "")
        crawler = self._rt.get_crawler(cloud)

        # 优先用 doc_ref 直接抓取
        if doc_ref:
            return self._fetch_by_ref(cloud, crawler, doc_ref)

        # 用 product 搜索，支持 keyword 过滤
        return self._fetch_by_product(cloud, crawler, product, keyword)

    def _fetch_by_ref(self, cloud: str, crawler, doc_ref: str) -> tuple:
        if cloud == "aliyun":
            doc = crawler.crawl_page(doc_ref)
            return doc.content, doc.title
        elif cloud == "tencent":
            parts = doc_ref.split("/")
            raw = crawler.fetch_doc(parts[-1], parts[0] if len(parts) > 1 else "")
            return (raw or {}).get("text", ""), (raw or {}).get("title", "")
        elif cloud == "baidu":
            parts = doc_ref.split("/", 1)
            raw = crawler.fetch_doc(parts[0], parts[1]) if len(parts) == 2 else None
            return (raw or {}).get("text", ""), (raw or {}).get("title", "")
        elif cloud == "volcano":
            parts = doc_ref.split("/")
            raw = crawler.fetch_doc(parts[0], parts[1]) if len(parts) == 2 else None
            return (raw or {}).get("text", ""), (raw or {}).get("title", "")
        return "", ""

    def _fetch_by_product(self, cloud: str, crawler, product: str, keyword: str = "") -> tuple:
        """按产品名搜索文档，支持关键词过滤
        
        Args:
            cloud: 云厂商
            crawler: 爬虫实例
            product: 产品名称
            keyword: 搜索关键词（可选，用于精确过滤）
        """
        if cloud == "aliyun":
            aliases = crawler.discover_product_docs(product)
            if not aliases:
                return "", ""
            # 如果有关键词，优先选择标题包含关键词的文档
            if keyword:
                for alias in aliases:
                    try:
                        doc = crawler.crawl_page(alias)
                        if keyword.lower() in doc.title.lower():
                            return doc.content, doc.title
                    except Exception:
                        continue
            # 没有关键词或没找到匹配的，返回第一篇
            doc = crawler.crawl_page(aliases[0])
            return doc.content, doc.title
        elif cloud == "tencent":
            # 腾讯云支持 keyword 参数
            raw_list = crawler.discover_product_docs(product, keyword=keyword, limit=10)
            if not raw_list:
                return "", ""
            # 如果有关键词，优先选择标题包含关键词的文档
            if keyword:
                for item in raw_list:
                    if keyword.lower() in item.get("title", "").lower():
                        raw = crawler.fetch_doc(item["doc_id"], item.get("product_id", ""))
                        if raw:
                            return raw.get("text", ""), raw.get("title", "")
            # 没有关键词或没找到匹配的，返回第一篇
            raw = crawler.fetch_doc(raw_list[0]["doc_id"], raw_list[0].get("product_id", ""))
            return (raw or {}).get("text", ""), (raw or {}).get("title", "")
        elif cloud == "baidu":
            raw_list = crawler.discover_product_docs(product, limit=10)
            if not raw_list:
                return "", ""
            # 如果有关键词，优先选择标题包含关键词的文档
            if keyword:
                for item in raw_list:
                    if keyword.lower() in item.get("name", "").lower():
                        raw = crawler.fetch_doc(item["product"], item["slug"])
                        if raw:
                            return raw.get("text", ""), raw.get("title", "")
            # 没有关键词或没找到匹配的，返回第一篇
            raw = crawler.fetch_doc(raw_list[0]["product"], raw_list[0]["slug"])
            return (raw or {}).get("text", ""), (raw or {}).get("title", "")
        elif cloud == "volcano":
            raw_list = crawler.discover_product_docs(product, limit=10)
            if not raw_list:
                return "", ""
            # 如果有关键词，优先选择标题包含关键词的文档
            if keyword:
                for item in raw_list:
                    if keyword.lower() in item.get("name", "").lower():
                        raw = crawler.fetch_doc(item["lib_id"], item["doc_id"])
                        if raw:
                            return raw.get("text", ""), raw.get("title", "")
            # 没有关键词或没找到匹配的，返回第一篇
            raw = crawler.fetch_doc(raw_list[0]["lib_id"], raw_list[0]["doc_id"])
            return (raw or {}).get("text", ""), (raw or {}).get("title", "")
        return "", ""

    @staticmethod
    def _parse_llm_output(raw: str) -> Dict[str, Any]:
        """从 LLM 输出中提取 JSON"""
        # 尝试提取 ```json ... ``` 块
        match = re.search(r"```json\s*([\s\S]+?)\s*```", raw)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # 直接尝试解析整个输出
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        # 降级：返回空结构
        logging.warning("无法解析 LLM 对比输出为 JSON，返回原始文本")
        return {"comparison": [], "summary": raw[:500]}
