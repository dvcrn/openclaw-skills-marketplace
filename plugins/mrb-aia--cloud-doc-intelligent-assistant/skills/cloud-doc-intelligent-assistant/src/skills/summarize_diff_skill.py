"""summarize_diff skill - 对新旧文档内容进行 diff 和摘要"""

import logging
from typing import Any, Dict, Optional

from ..contracts.response import ErrorCode, SkillResponse
from ..detector import ChangeDetector
from ..models import Document, DocumentChange
from ..utils import compute_content_hash
from .runtime import SkillRuntime


class SummarizeDiffSkill:
    def __init__(self, runtime: SkillRuntime):
        self._rt = runtime
        self._detector = ChangeDetector()

    def run(
        self,
        title: str,
        old_content: str,
        new_content: str,
        focus: Optional[str] = None,
        url: str = "",
    ) -> Dict[str, Any]:
        if not title:
            return SkillResponse.fail(ErrorCode.MISSING_PARAM, "title 参数必填").to_dict()
        if old_content is None or new_content is None:
            return SkillResponse.fail(ErrorCode.MISSING_PARAM, "old_content 和 new_content 必填").to_dict()

        old_hash = compute_content_hash(old_content)
        new_hash = compute_content_hash(new_content)

        if old_hash == new_hash:
            return SkillResponse.ok(
                machine={
                    "title": title,
                    "change_type": "unchanged",
                    "focus": focus,
                    "summary": "内容无变化。",
                    "old_hash": old_hash,
                    "new_hash": new_hash,
                },
                human={"summary_text": "文档内容无变化。"},
            ).to_dict()

        # 构建临时 Document 对象用于 detector
        from datetime import datetime
        old_doc = Document(
            url=url or "temp://old",
            title=title,
            content=old_content,
            content_hash=old_hash,
            last_modified=None,
            crawled_at=datetime.now(),
            metadata={},
        )
        new_doc = Document(
            url=url or "temp://new",
            title=title,
            content=new_content,
            content_hash=new_hash,
            last_modified=None,
            crawled_at=datetime.now(),
            metadata={},
        )

        change = self._detector.detect(old_doc, new_doc)
        if change is None:
            change_type = "modified"
            diff_text = f"旧内容长度: {len(old_content)}, 新内容长度: {len(new_content)}"
        else:
            change_type = change.change_type.value
            diff_text = change.diff

        # 调 LLM 生成摘要
        try:
            focus_hint = f"，重点关注：{focus}" if focus else ""
            prompt = (
                f"请分析以下文档《{title}》的变更内容{focus_hint}，生成简洁的中文摘要：\n\n"
                f"{diff_text[:3000]}\n\n"
                f"请输出：\n1. 变更类型\n2. 主要变更点（3-5条）\n3. 影响范围"
            )
            summary = self._rt.summarizer.llm.generate(prompt, max_tokens=800)
        except Exception as e:
            logging.error(f"summarize_diff LLM 失败: {e}")
            summary = f"摘要生成失败: {e}"

        return SkillResponse.ok(
            machine={
                "title": title,
                "change_type": change_type,
                "focus": focus,
                "summary": summary,
                "old_hash": old_hash,
                "new_hash": new_hash,
            },
            human={"summary_text": summary},
        ).to_dict()
