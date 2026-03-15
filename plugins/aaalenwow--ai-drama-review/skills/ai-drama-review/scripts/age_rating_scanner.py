"""
年龄分级合规检测器

两层架构：
Layer 1: 本地关键词快速扫描
Layer 2: AI 上下文深度分析（需要 API 密钥）
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class KeywordHit:
    """关键词命中记录。"""
    keyword: str
    category: str       # "violence" / "sexual" / "horror" / "profanity" / "substance"
    severity: str       # "mild" / "moderate" / "severe"
    paragraph_index: int
    position_in_paragraph: int
    context: str        # 命中前后上下文
    timestamp: Optional[str] = None


@dataclass
class RatingResult:
    """分级检测结果。"""
    suggested_rating: str   # "all_ages" / "12+" / "18+" / "non_compliant"
    target_rating: str      # 用户期望的分级
    is_compliant: bool
    total_hits: int
    hits_by_category: dict = field(default_factory=dict)
    hits_by_severity: dict = field(default_factory=dict)
    keyword_hits: List[KeywordHit] = field(default_factory=list)
    ai_analysis: Optional[dict] = None
    risk_level: str = "low"


# === 关键词库管理 ===

def _get_keywords_dir() -> Path:
    """获取关键词库目录。"""
    return Path(__file__).parent.parent / "assets" / "keyword_databases"


def _get_rules_dir() -> Path:
    """获取分级规则目录。"""
    return Path(__file__).parent.parent / "assets" / "rating_rules"


def load_keyword_database(category: str) -> dict:
    """加载指定类别的关键词库。"""
    filepath = _get_keywords_dir() / f"{category}_keywords.json"
    if not filepath.exists():
        return {"category": category, "keywords": {}}

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_keywords() -> dict:
    """加载全部类别的关键词库。"""
    categories = ["violence", "sexual", "horror", "profanity", "substance"]
    all_kw = {}
    for cat in categories:
        db = load_keyword_database(cat)
        all_kw[cat] = db.get("keywords", {})
    return all_kw


def load_rating_rules(ruleset: str = "china") -> dict:
    """加载分级规则配置。"""
    filepath = _get_rules_dir() / f"{ruleset}_rating.json"
    if not filepath.exists():
        raise FileNotFoundError(f"分级规则文件不存在: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# === Layer 1: 本地关键词扫描 ===

def _extract_context(text: str, pos: int, window: int = 30) -> str:
    """提取命中位置前后的上下文。"""
    start = max(0, pos - window)
    end = min(len(text), pos + window)
    return text[start:end]


def scan_keywords(text: str, keywords_db: dict) -> List[KeywordHit]:
    """逐段扫描关键词命中。"""
    paragraphs = re.split(r'\n\s*\n|\n', text)
    hits = []

    for para_idx, paragraph in enumerate(paragraphs):
        paragraph_lower = paragraph.lower()

        for category, keywords in keywords_db.items():
            for keyword, info in keywords.items():
                # 检查主关键词
                all_forms = [keyword] + info.get("aliases", [])
                for form in all_forms:
                    form_lower = form.lower()
                    start = 0
                    while True:
                        pos = paragraph_lower.find(form_lower, start)
                        if pos == -1:
                            break
                        hits.append(KeywordHit(
                            keyword=form,
                            category=category,
                            severity=info["severity"],
                            paragraph_index=para_idx,
                            position_in_paragraph=pos,
                            context=_extract_context(paragraph, pos),
                        ))
                        start = pos + len(form_lower)

    return hits


def _count_by_field(hits: List[KeywordHit], field_name: str) -> dict:
    """按指定字段统计命中数。"""
    counts = {}
    for hit in hits:
        value = getattr(hit, field_name)
        counts[value] = counts.get(value, 0) + 1
    return counts


def calculate_initial_rating(hits: List[KeywordHit],
                             rules: dict) -> str:
    """根据关键词命中情况计算初步分级。"""
    if not hits:
        return "all_ages"

    by_severity = _count_by_field(hits, "severity")
    by_category = _count_by_field(hits, "category")

    # 检查是否触发不合规
    for trigger in rules.get("non_compliant_triggers", []):
        if "category" in trigger and "severity" in trigger:
            cat_sev_count = sum(
                1 for h in hits
                if h.category == trigger["category"]
                and h.severity == trigger["severity"]
            )
            if cat_sev_count >= trigger.get("min_count", 1):
                return "non_compliant"
        elif "severity" in trigger:
            sev_count = by_severity.get(trigger["severity"], 0)
            if sev_count >= trigger.get("min_count", 1):
                return "non_compliant"

    # 逐级检查分级
    ratings_order = ["all_ages", "12+", "18+"]
    ratings_config = rules.get("ratings", {})

    for rating in ratings_order:
        config = ratings_config.get(rating, {})

        # 检查禁止类别
        forbidden = config.get("forbidden_categories", [])
        if any(by_category.get(cat, 0) > 0 for cat in forbidden):
            continue

        # 检查严重度上限
        max_sev = config.get("max_severity", "severe")
        severity_order = {"mild": 0, "moderate": 1, "severe": 2}
        max_sev_level = severity_order.get(max_sev, 2)

        # 检查是否有超过允许严重度的命中
        exceeded = False
        for sev, level in severity_order.items():
            if level > max_sev_level and by_severity.get(sev, 0) > 0:
                exceeded = True
                break

        if exceeded:
            continue

        # 检查各严重度的数量限制
        mild_limit = config.get("max_hits_mild", -1)
        moderate_limit = config.get("max_hits_moderate", -1)
        severe_limit = config.get("max_hits_severe", -1)

        mild_ok = mild_limit == -1 or by_severity.get("mild", 0) <= mild_limit
        moderate_ok = moderate_limit == -1 or by_severity.get("moderate", 0) <= moderate_limit
        severe_ok = severe_limit == -1 or by_severity.get("severe", 0) <= severe_limit

        if mild_ok and moderate_ok and severe_ok:
            return rating

    return "18+"


def _rating_order(rating: str) -> int:
    """分级排序值。"""
    order = {"all_ages": 0, "12+": 1, "18+": 2, "non_compliant": 3}
    return order.get(rating, 3)


def _determine_risk_level(suggested: str, target: str) -> str:
    """确定风险等级。"""
    if suggested == "non_compliant":
        return "critical"
    if _rating_order(suggested) > _rating_order(target):
        diff = _rating_order(suggested) - _rating_order(target)
        if diff >= 2:
            return "high"
        return "medium"
    return "low"


# === 辅助分析 ===

def analyze_frame_descriptions(descriptions: List[dict],
                               keywords_db: dict) -> List[KeywordHit]:
    """分析视频关键帧描述文本。"""
    hits = []
    for desc_item in descriptions:
        text = desc_item.get("description", "")
        timestamp = desc_item.get("timestamp", "")
        frame_hits = scan_keywords(text, keywords_db)
        for hit in frame_hits:
            hit.timestamp = timestamp
        hits.extend(frame_hits)
    return hits


def analyze_audio_transcript(transcript: str,
                             keywords_db: dict) -> List[KeywordHit]:
    """分析音频转录文本。"""
    return scan_keywords(transcript, keywords_db)


# === 主入口 ===

def run_age_rating_scan(text: str, target_rating: str = "all_ages",
                        ruleset: str = "china",
                        frame_descriptions: list = None,
                        audio_transcript: str = None) -> RatingResult:
    """
    完整的年龄分级扫描流程。

    Args:
        text: 剧本/台词文本
        target_rating: 用户期望的目标分级
        ruleset: 分级规则集（"china" 或 "general"）
        frame_descriptions: 视频关键帧描述列表
        audio_transcript: 音频转录文本

    Returns:
        RatingResult
    """
    keywords_db = load_all_keywords()
    rules = load_rating_rules(ruleset)

    # Layer 1: 本地扫描
    all_hits = scan_keywords(text, keywords_db)

    # 辅助内容分析
    if frame_descriptions:
        all_hits.extend(analyze_frame_descriptions(frame_descriptions, keywords_db))
    if audio_transcript:
        all_hits.extend(analyze_audio_transcript(audio_transcript, keywords_db))

    # 计算分级
    suggested = calculate_initial_rating(all_hits, rules)
    is_compliant = _rating_order(suggested) <= _rating_order(target_rating)
    risk_level = _determine_risk_level(suggested, target_rating)

    return RatingResult(
        suggested_rating=suggested,
        target_rating=target_rating,
        is_compliant=is_compliant,
        total_hits=len(all_hits),
        hits_by_category=_count_by_field(all_hits, "category"),
        hits_by_severity=_count_by_field(all_hits, "severity"),
        keyword_hits=all_hits,
        risk_level=risk_level,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="年龄分级合规检测")
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--target-rating", default="all_ages",
                        choices=["all_ages", "12+", "18+"])
    parser.add_argument("--ruleset", default="china",
                        choices=["china", "general"])
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8")
    result = run_age_rating_scan(text, args.target_rating, args.ruleset)

    print(f"=== 年龄分级检测报告 ===")
    print(f"建议分级: {result.suggested_rating}")
    print(f"目标分级: {result.target_rating}")
    print(f"是否合规: {'是' if result.is_compliant else '否'}")
    print(f"风险等级: {result.risk_level}")
    print(f"总命中数: {result.total_hits}")
    print(f"按类别: {json.dumps(result.hits_by_category, ensure_ascii=False)}")
    print(f"按严重度: {json.dumps(result.hits_by_severity, ensure_ascii=False)}")
