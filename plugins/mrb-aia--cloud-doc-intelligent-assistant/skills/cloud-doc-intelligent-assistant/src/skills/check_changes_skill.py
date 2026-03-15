"""check_changes skill - 检测文档变更"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..contracts.response import ErrorCode, SkillResponse
from ..detector import ChangeDetector
from ..models import Document
from ..utils import compute_content_hash
from .runtime import SkillRuntime

SUPPORTED_CLOUDS = {"aliyun", "tencent", "baidu", "volcano"}


class CheckChangesSkill:
    def __init__(self, runtime: SkillRuntime):
        self._rt = runtime
        self._detector = ChangeDetector()

    def run(
        self,
        cloud: str,
        product: str,
        keyword: Optional[str] = None,
        days: int = 7,
        max_pages: int = 200,
        with_summary: bool = True,
    ) -> Dict[str, Any]:
        if not cloud:
            return SkillResponse.fail(ErrorCode.MISSING_PARAM, "cloud 参数必填").to_dict()
        if cloud not in SUPPORTED_CLOUDS:
            return SkillResponse.fail(ErrorCode.INVALID_PARAM, f"不支持的云厂商: {cloud}").to_dict()
        if not product:
            return SkillResponse.fail(ErrorCode.MISSING_PARAM, "product 参数必填").to_dict()

        try:
            crawler = self._rt.get_crawler(cloud)
        except ValueError as e:
            return SkillResponse.fail(ErrorCode.INVALID_PARAM, str(e)).to_dict()

        # 抓取当前文档列表
        try:
            current_docs = self._crawl_product_docs(cloud, crawler, product, keyword, max_pages)
        except Exception as e:
            logging.error(f"check_changes 抓取失败: {e}")
            return SkillResponse.fail(ErrorCode.CRAWL_FAILED, f"抓取失败: {e}").to_dict()

        if not current_docs:
            return SkillResponse.ok(
                machine={"cloud": cloud, "product": product, "changes": [], "total_checked": 0},
                human={"summary_markdown": f"未找到 {cloud} {product} 相关文档。"},
            ).to_dict()

        # 与历史版本对比
        changes = []
        baseline_created = []
        cutoff = datetime.now() - timedelta(days=days)

        for doc in current_docs:
            stored = self._rt.storage.get_latest(doc.url)
            if stored is None:
                # 首次抓取，建立基线
                self._rt.storage.save(doc)
                baseline_created.append(doc.url)
                continue

            change = self._detector.detect(stored, doc)
            if change is None:
                # 无变更，更新存储
                self._rt.storage.save(doc)
                continue

            # 有变更，保存新版本
            self._rt.storage.save(doc)

            # days 过滤
            if doc.crawled_at and doc.crawled_at < cutoff:
                continue

            change_item: Dict[str, Any] = {
                "change_type": change.change_type.value,
                "title": doc.title,
                "url": doc.url,
                "doc_ref": doc.url,
                "old_hash": stored.content_hash,
                "new_hash": doc.content_hash,
            }
            if with_summary:
                try:
                    change_item["summary"] = self._rt.summarizer.summarize_change(change)
                except Exception as e:
                    change_item["summary"] = f"摘要生成失败: {e}"
            changes.append(change_item)

        # 构建 human 摘要
        if baseline_created:
            human_text = (
                f"首次抓取，已为 {len(baseline_created)} 篇文档建立基线。"
                f"下次运行时将开始检测变更。"
            )
        elif not changes:
            human_text = f"检查了 {len(current_docs)} 篇文档，最近 {days} 天内无变更。"
        else:
            lines = [f"# 最近 {days} 天变更摘要\n"]
            for c in changes:
                summary = c.get("summary", "")
                lines.append(f"- [{c['change_type']}] {c['title']}: {summary}")
            human_text = "\n".join(lines)

        return SkillResponse.ok(
            machine={
                "cloud": cloud,
                "product": product,
                "days": days,
                "total_checked": len(current_docs),
                "changes": changes,
                "baseline_created": len(baseline_created),
            },
            human={"summary_markdown": human_text},
        ).to_dict()

    def _crawl_product_docs(self, cloud: str, crawler, product: str,
                             keyword: Optional[str], max_pages: int) -> List[Document]:
        docs = []
        if cloud == "aliyun":
            aliases = crawler.discover_product_docs(product)
            for alias in aliases:
                try:
                    doc = crawler.crawl_page(alias)
                    # 如果指定了关键词，进行过滤
                    if keyword and keyword.strip():
                        if keyword.lower() not in doc.title.lower() and keyword.lower() not in doc.content.lower():
                            continue
                    docs.append(doc)
                    # 达到最大数量后停止
                    if len(docs) >= max_pages:
                        break
                except Exception as e:
                    logging.warning(f"跳过 {alias}: {e}")
        elif cloud == "tencent":
            raw_list = crawler.discover_product_docs(product, keyword=keyword or "", limit=max_pages)
            for entry in raw_list:
                try:
                    raw = crawler.fetch_doc(entry["doc_id"], entry.get("product_id", ""))
                    if raw:
                        docs.append(self._raw_to_doc(raw))
                except Exception as e:
                    logging.warning(f"跳过腾讯云文档 {entry.get('doc_id')}: {e}")
        elif cloud == "baidu":
            raw_list = crawler.discover_product_docs(product, limit=max_pages)
            for entry in raw_list:
                try:
                    raw = crawler.fetch_doc(entry["product"], entry["slug"])
                    if raw:
                        docs.append(self._raw_to_doc(raw))
                except Exception as e:
                    logging.warning(f"跳过百度云文档 {entry.get('slug')}: {e}")
        elif cloud == "volcano":
            raw_list = crawler.discover_product_docs(product, limit=max_pages)
            for entry in raw_list:
                try:
                    raw = crawler.fetch_doc(entry["lib_id"], entry["doc_id"])
                    if raw:
                        docs.append(self._raw_to_doc(raw))
                except Exception as e:
                    logging.warning(f"跳过火山云文档 {entry.get('doc_id')}: {e}")
        return docs

    @staticmethod
    def _raw_to_doc(raw: Dict[str, Any]) -> Document:
        content = raw.get("text", "")
        return Document(
            url=raw.get("url", ""),
            title=raw.get("title", ""),
            content=content,
            content_hash=compute_content_hash(content),
            last_modified=None,
            crawled_at=datetime.now(),
            metadata={"image_urls": raw.get("image_urls", [])},
        )
