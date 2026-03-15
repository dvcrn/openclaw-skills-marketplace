"""
小说魔改检测器

比对原著与改编版本，量化改编偏离程度。
使用 Needleman-Wunsch 变体进行章节对齐。
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent))
from text_similarity import (
    preprocess_text, char_ngrams, jaccard_similarity,
    tokenize_chinese, compute_idf, build_tfidf_vector,
    cosine_similarity_vec,
)


@dataclass
class PlotPoint:
    """情节点。"""
    index: int
    summary: str
    characters: List[str] = field(default_factory=list)
    location: Optional[str] = None
    importance: str = "normal"  # "core" / "normal" / "minor"


@dataclass
class CharacterProfile:
    """角色概要。"""
    name: str
    traits: List[str] = field(default_factory=list)
    relationships: dict = field(default_factory=dict)
    fate: Optional[str] = None


@dataclass
class DeviationItem:
    """偏离项。"""
    deviation_type: str  # "plot_added"/"plot_removed"/"plot_modified"
                         # "character_changed"/"setting_changed"
    original_content: str
    adapted_content: str
    severity: str        # "minor" / "moderate" / "major"
    description: str


@dataclass
class AdaptationReport:
    """改编检测报告。"""
    deviation_score: float        # 0-100
    adaptation_type: str          # "faithful"/"reasonable"/"severe_modification"
    total_deviations: int
    deviations_by_type: dict = field(default_factory=dict)
    deviations_by_severity: dict = field(default_factory=dict)
    deviation_items: List[DeviationItem] = field(default_factory=list)
    section_alignment: list = field(default_factory=list)


# === 文本结构提取 ===

def extract_sections(text: str) -> List[dict]:
    """
    提取章节/段落结构。

    尝试按章节标题分割，如果没有明确标题则按段落分割。
    """
    # 尝试按中文章节标题分割
    chapter_pattern = r'(第[一二三四五六七八九十百千\d]+[章节回集幕][\s：:]*[^\n]*)'
    chapters = re.split(chapter_pattern, text)

    sections = []
    if len(chapters) > 1:
        # 有明确章节标题
        i = 0
        while i < len(chapters):
            if re.match(chapter_pattern, chapters[i]):
                title = chapters[i].strip()
                content = chapters[i + 1].strip() if i + 1 < len(chapters) else ""
                sections.append({"title": title, "content": content})
                i += 2
            else:
                if chapters[i].strip():
                    sections.append({"title": "", "content": chapters[i].strip()})
                i += 1
    else:
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        for i, para in enumerate(paragraphs):
            if len(para) >= 15:  # 过滤过短段落
                sections.append({"title": f"段落{i + 1}", "content": para})

    return sections


def _quick_similarity(text_a: str, text_b: str) -> float:
    """快速计算两段文本的相似度（用于对齐）。"""
    if not text_a or not text_b:
        return 0.0

    # 使用字符 n-gram Jaccard 作为快速相似度
    ngrams_a = char_ngrams(text_a, n=3)
    ngrams_b = char_ngrams(text_b, n=3)
    return jaccard_similarity(ngrams_a, ngrams_b)


# === 章节对齐 ===

def align_sections(original_sections: list, adapted_sections: list) -> list:
    """
    基于 Needleman-Wunsch 变体的章节对齐。

    Returns:
        [(orig_idx_or_None, adapted_idx_or_None, similarity, status), ...]
        status: "matched" / "added" / "removed" / "modified"
    """
    m = len(original_sections)
    n = len(adapted_sections)

    if m == 0 and n == 0:
        return []
    if m == 0:
        return [(None, j, 0.0, "added") for j in range(n)]
    if n == 0:
        return [(i, None, 0.0, "removed") for i in range(m)]

    # 构建相似度矩阵
    sim_matrix = [[0.0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            sim_matrix[i][j] = _quick_similarity(
                original_sections[i]["content"],
                adapted_sections[j]["content"],
            )

    # 动态规划
    GAP_PENALTY = -0.1
    dp = [[0.0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        dp[i][0] = dp[i - 1][0] + GAP_PENALTY
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j - 1] + GAP_PENALTY

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match_score = dp[i - 1][j - 1] + sim_matrix[i - 1][j - 1]
            skip_orig = dp[i - 1][j] + GAP_PENALTY
            skip_adapt = dp[i][j - 1] + GAP_PENALTY
            dp[i][j] = max(match_score, skip_orig, skip_adapt)

    # 回溯
    alignment = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + sim_matrix[i - 1][j - 1]:
            sim = sim_matrix[i - 1][j - 1]
            status = "matched" if sim >= 0.3 else "modified"
            alignment.append((i - 1, j - 1, sim, status))
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + GAP_PENALTY:
            alignment.append((i - 1, None, 0.0, "removed"))
            i -= 1
        else:
            alignment.append((None, j - 1, 0.0, "added"))
            j -= 1

    alignment.reverse()
    return alignment


# === 角色分析 ===

def extract_characters_local(text: str) -> List[str]:
    """本地方式提取角色名（基于高频重复的短词）。"""
    # 简单启发式：提取引号中出现的称呼和高频 2-3 字名
    names = set()

    # 提取对话前的称呼
    dialogue_pattern = r'[「『"](.*?)[」』"]'
    speaker_pattern = r'(\S{2,4})[说道叫喊问答笑哭]'
    for match in re.finditer(speaker_pattern, text):
        name = match.group(1)
        if len(name) <= 4 and not any(c.isdigit() for c in name):
            names.add(name)

    return list(names)


# === 偏离度计算 ===

def _classify_deviation_severity(sim: float, status: str) -> str:
    """判定偏离严重程度。"""
    if status == "removed":
        return "major"
    if status == "added":
        return "moderate"
    if status == "modified":
        if sim >= 0.5:
            return "minor"
        if sim >= 0.2:
            return "moderate"
        return "major"
    return "minor"


def build_deviations(alignment: list, original_sections: list,
                     adapted_sections: list) -> List[DeviationItem]:
    """从对齐结果构建偏离项列表。"""
    deviations = []

    for orig_idx, adapt_idx, sim, status in alignment:
        if status == "matched":
            continue

        orig_content = (original_sections[orig_idx]["content"][:200]
                        if orig_idx is not None else "")
        adapt_content = (adapted_sections[adapt_idx]["content"][:200]
                         if adapt_idx is not None else "")

        severity = _classify_deviation_severity(sim, status)

        if status == "removed":
            desc = f"原著段落被删除"
            dev_type = "plot_removed"
        elif status == "added":
            desc = f"新增了原著中没有的内容"
            dev_type = "plot_added"
        else:
            desc = f"内容被修改（相似度: {sim:.2f}）"
            dev_type = "plot_modified"

        deviations.append(DeviationItem(
            deviation_type=dev_type,
            original_content=orig_content,
            adapted_content=adapt_content,
            severity=severity,
            description=desc,
        ))

    return deviations


def calculate_deviation_score(deviations: List[DeviationItem],
                              total_sections: int) -> float:
    """
    计算偏离度评分 (0-100)。

    权重设计：
    - plot_removed × 3.0（删除原著核心最严重）
    - plot_modified × 2.0
    - plot_added × 1.0
    - character_changed × 2.5
    - setting_changed × 1.5
    严重度加权：minor × 0.5, moderate × 1.0, major × 2.0
    """
    if not deviations or total_sections == 0:
        return 0.0

    severity_weights = {"minor": 0.5, "moderate": 1.0, "major": 2.0}
    type_weights = {
        "plot_removed": 3.0,
        "plot_modified": 2.0,
        "plot_added": 1.0,
        "character_changed": 2.5,
        "setting_changed": 1.5,
    }

    weighted_sum = 0.0
    for d in deviations:
        sw = severity_weights.get(d.severity, 1.0)
        tw = type_weights.get(d.deviation_type, 1.0)
        weighted_sum += sw * tw

    # 归一化到 0-100
    max_possible = total_sections * 3.0 * 2.0  # 全部为 major + removed
    score = min(100.0, (weighted_sum / max(max_possible, 1)) * 100)
    return round(score, 1)


def classify_adaptation(score: float) -> str:
    """分类改编类型。"""
    if score <= 30:
        return "faithful"
    if score <= 60:
        return "reasonable"
    return "severe_modification"


# === 主入口 ===

def detect_adaptation(original_text: str, adapted_text: str) -> AdaptationReport:
    """
    完整的魔改检测流程。

    Args:
        original_text: 原著全文
        adapted_text: 改编版全文

    Returns:
        AdaptationReport
    """
    # 提取结构
    orig_sections = extract_sections(original_text)
    adapt_sections = extract_sections(adapted_text)

    if not orig_sections and not adapt_sections:
        return AdaptationReport(
            deviation_score=0.0,
            adaptation_type="faithful",
            total_deviations=0,
        )

    # 章节对齐
    alignment = align_sections(orig_sections, adapt_sections)

    # 构建偏离项
    deviations = build_deviations(alignment, orig_sections, adapt_sections)

    # 计算偏离度
    total_sections = max(len(orig_sections), len(adapt_sections))
    score = calculate_deviation_score(deviations, total_sections)
    adaptation_type = classify_adaptation(score)

    # 统计
    by_type = {}
    by_severity = {}
    for d in deviations:
        by_type[d.deviation_type] = by_type.get(d.deviation_type, 0) + 1
        by_severity[d.severity] = by_severity.get(d.severity, 0) + 1

    return AdaptationReport(
        deviation_score=score,
        adaptation_type=adaptation_type,
        total_deviations=len(deviations),
        deviations_by_type=by_type,
        deviations_by_severity=by_severity,
        deviation_items=deviations,
        section_alignment=[(o, a, s, st) for o, a, s, st in alignment],
    )


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="小说魔改检测")
    parser.add_argument("--original", required=True, help="原著文件路径")
    parser.add_argument("--adapted", required=True, help="改编版文件路径")
    args = parser.parse_args()

    orig_path = Path(args.original)
    adapt_path = Path(args.adapted)

    if not orig_path.exists():
        print(f"错误: 原著文件不存在: {orig_path}")
        sys.exit(1)
    if not adapt_path.exists():
        print(f"错误: 改编文件不存在: {adapt_path}")
        sys.exit(1)

    original = orig_path.read_text(encoding="utf-8")
    adapted = adapt_path.read_text(encoding="utf-8")

    report = detect_adaptation(original, adapted)

    print(f"=== 小说魔改检测报告 ===")
    print(f"偏离度评分: {report.deviation_score}/100")
    print(f"改编类型: {report.adaptation_type}")
    print(f"总偏离数: {report.total_deviations}")
    print(f"按类型: {json.dumps(report.deviations_by_type, ensure_ascii=False)}")
    print(f"按严重度: {json.dumps(report.deviations_by_severity, ensure_ascii=False)}")

    if report.deviation_items:
        print(f"\n偏离详情:")
        for d in report.deviation_items[:10]:
            print(f"  [{d.severity}] {d.description}")
            if d.original_content:
                print(f"    原文: {d.original_content[:80]}...")
            if d.adapted_content:
                print(f"    改编: {d.adapted_content[:80]}...")
