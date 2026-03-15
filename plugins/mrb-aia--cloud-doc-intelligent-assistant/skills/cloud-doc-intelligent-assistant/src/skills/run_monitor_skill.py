"""run_monitor skill - 批量巡检多云多产品文档"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..contracts.response import ErrorCode, SkillResponse
from ..detector import ChangeDetector
from ..models import Document, Notification
from ..utils import compute_content_hash
from .runtime import SkillRuntime

SUPPORTED_CLOUDS = {"aliyun", "tencent", "baidu", "volcano"}


class RunMonitorSkill:
    def __init__(self, runtime: SkillRuntime):
        self._rt = runtime
        self._detector = ChangeDetector()

    def run(
        self,
        clouds: List[str] = None,
        products: List[str] = None,
        mode: str = "check_now",
        max_pages: int = 50,
        days: int = 1,
        with_summary: bool = True,
        send_notification: bool = False,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        clouds = [c.lower() for c in (clouds or [])]
        products = products or []

        if not clouds:
            return SkillResponse.fail(ErrorCode.MISSING_PARAM, "clouds 参数必填").to_dict()
        if not products:
            return SkillResponse.fail(ErrorCode.MISSING_PARAM, "products 参数必填").to_dict()

        invalid = [c for c in clouds if c not in SUPPORTED_CLOUDS]
        if invalid:
            return SkillResponse.fail(ErrorCode.INVALID_PARAM, f"不支持的云厂商: {invalid}").to_dict()

        all_changes = []
        total_checked = 0
        errors = []

        for cloud in clouds:
            for product in products:
                try:
                    result = self._check_one(cloud, product, days, max_pages, with_summary)
                    total_checked += result["checked"]
                    all_changes.extend(result["changes"])
                except Exception as e:
                    logging.error(f"巡检 {cloud}/{product} 失败: {e}")
                    errors.append({"cloud": cloud, "product": product, "error": str(e)})

        # 生成日报摘要
        report_summary = self._build_report_summary(all_changes, total_checked, clouds, products)

        # 发送通知
        notification_result = {"attempted": False, "sent": False, "channel": None}
        if send_notification and (mode == "scheduled" or all_changes):
            try:
                notification = Notification(
                    title=f"云文档巡检日报 - 发现 {len(all_changes)} 处变化",
                    summary=report_summary,
                    changes=[],
                    timestamp=datetime.now(),
                    metadata={
                        "total_checked": total_checked,
                        "changes_count": len(all_changes),
                        "clouds": clouds,
                        "products": products,
                    },
                )
                results = self._rt.notifier.send_all(notification)
                notification_result["attempted"] = True
                notification_result["sent"] = any(results.values())
                notification_result["channel"] = list(results.keys())[0] if results else None
            except Exception as e:
                logging.error(f"发送通知失败: {e}")
                notification_result["attempted"] = True

        # 构建 human markdown
        lines = [
            "# 云文档巡检日报",
            f"\n## 今日概览",
            f"- 检查 {total_checked} 篇文档",
            f"- 发现 {len(all_changes)} 处变化",
        ]
        if notification_result["sent"]:
            lines.append(f"- 已发送通知")
        if errors:
            lines.append(f"- {len(errors)} 个任务失败")
        if all_changes:
            lines.append("\n## 变更详情")
            for c in all_changes[:20]:
                lines.append(f"- [{c['cloud']}] {c['product']} - {c['title']}: {c.get('summary', '')[:100]}")
            if len(all_changes) > 20:
                lines.append(f"... 还有 {len(all_changes) - 20} 条变更")

        return SkillResponse.ok(
            machine={
                "mode": mode,
                "clouds": clouds,
                "products": products,
                "total_checked": total_checked,
                "changes": all_changes,
                "errors": errors,
                "notification": notification_result,
            },
            human={"summary_markdown": "\n".join(lines)},
        ).to_dict()

    def _check_one(self, cloud: str, product: str, days: int, max_pages: int,
                   with_summary: bool) -> Dict[str, Any]:
        """检查单个云厂商+产品组合，单文档失败不中断"""
        crawler = self._rt.get_crawler(cloud)
        cutoff = datetime.now() - timedelta(days=days)
        changes = []
        checked = 0

        raw_list = self._discover_docs(cloud, crawler, product, max_pages)
        for entry in raw_list:
            try:
                doc = self._fetch_doc(cloud, crawler, entry)
                if doc is None:
                    continue
                checked += 1
                stored = self._rt.storage.get_latest(doc.url)
                if stored is None:
                    self._rt.storage.save(doc)
                    continue
                change = self._detector.detect(stored, doc)
                if change is None:
                    self._rt.storage.save(doc)
                    continue
                self._rt.storage.save(doc)
                change_item: Dict[str, Any] = {
                    "cloud": cloud,
                    "product": product,
                    "change_type": change.change_type.value,
                    "title": doc.title,
                    "url": doc.url,
                }
                if with_summary:
                    try:
                        change_item["summary"] = self._rt.summarizer.summarize_change(change)
                    except Exception as e:
                        change_item["summary"] = f"摘要失败: {e}"
                changes.append(change_item)
            except Exception as e:
                logging.warning(f"处理文档失败 ({cloud}/{product}): {e}")

        return {"checked": checked, "changes": changes}

    def _discover_docs(self, cloud: str, crawler, product: str, max_pages: int) -> List[Dict]:
        if cloud == "aliyun":
            aliases = crawler.discover_product_docs(product)[:max_pages]
            return [{"alias": a} for a in aliases]
        elif cloud == "tencent":
            return crawler.discover_product_docs(product, limit=max_pages)
        elif cloud == "baidu":
            return crawler.discover_product_docs(product, limit=max_pages)
        elif cloud == "volcano":
            return crawler.discover_product_docs(product, limit=max_pages)
        return []

    def _fetch_doc(self, cloud: str, crawler, entry: Dict) -> Optional[Document]:
        if cloud == "aliyun":
            doc = crawler.crawl_page(entry["alias"])
            return doc
        elif cloud == "tencent":
            raw = crawler.fetch_doc(entry["doc_id"], entry.get("product_id", ""))
            return self._raw_to_doc(raw) if raw else None
        elif cloud == "baidu":
            raw = crawler.fetch_doc(entry["product"], entry["slug"])
            return self._raw_to_doc(raw) if raw else None
        elif cloud == "volcano":
            raw = crawler.fetch_doc(entry["lib_id"], entry["doc_id"])
            return self._raw_to_doc(raw) if raw else None
        return None

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

    @staticmethod
    def _build_report_summary(changes: List[Dict], total_checked: int,
                               clouds: List[str], products: List[str]) -> str:
        return (
            f"本次巡检覆盖 {', '.join(clouds)} 的 {', '.join(products)} 产品，"
            f"共检查 {total_checked} 篇文档，发现 {len(changes)} 处变更。"
        )
