"""
文本相似度检测引擎

用于版权侵权检测，支持三种互补的相似度算法：
- n-gram Jaccard 系数（局部词汇重复）
- 归一化编辑距离（整体文本差异）
- TF-IDF 余弦相似度（语义主题相似）

纯 Python 实现，不依赖外部 NLP 库。
"""

import math
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SimilarityResult:
    """单段相似度检测结果。"""
    source_paragraph_index: int
    source_text: str
    reference_id: str
    reference_paragraph_index: int
    reference_text: str
    ngram_jaccard: float
    edit_distance_normalized: float
    cosine_similarity: float
    combined_score: float
    is_suspicious: bool


@dataclass
class CopyrightReport:
    """版权检测报告。"""
    total_paragraphs: int
    suspicious_paragraphs: int
    max_similarity_score: float
    risk_level: str  # "low" / "medium" / "high" / "critical"
    results: List[SimilarityResult] = field(default_factory=list)


# === 文本预处理 ===

def preprocess_text(text: str) -> str:
    """统一编码、去标点、去多余空白。"""
    # Unicode 归一化
    text = unicodedata.normalize("NFKC", text)
    # 去除标点
    text = re.sub(r'[^\w\s]', '', text)
    # 合并多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()


def split_paragraphs(text: str, min_length: int = 20) -> List[str]:
    """按段落分割文本，过滤过短段落。"""
    paragraphs = re.split(r'\n\s*\n|\n', text)
    return [p.strip() for p in paragraphs if len(p.strip()) >= min_length]


def tokenize_chinese(text: str) -> List[str]:
    """中文分词（优先 jieba，降级到字符级）。"""
    try:
        import jieba
        return list(jieba.cut(text))
    except ImportError:
        # 降级：按字符分词，保留连续英文/数字为整词
        tokens = []
        current_ascii = []
        for char in text:
            if char.isascii() and char.isalnum():
                current_ascii.append(char)
            else:
                if current_ascii:
                    tokens.append(''.join(current_ascii))
                    current_ascii = []
                if char.strip():
                    tokens.append(char)
        if current_ascii:
            tokens.append(''.join(current_ascii))
        return tokens


# === n-gram 相似度 ===

def char_ngrams(text: str, n: int = 3) -> set:
    """生成字符级 n-gram 集合。"""
    text = preprocess_text(text)
    if len(text) < n:
        return {text} if text else set()
    return {text[i:i + n] for i in range(len(text) - n + 1)}


def word_ngrams(tokens: list, n: int = 2) -> set:
    """生成词级 n-gram 集合。"""
    if len(tokens) < n:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard 系数 = |A ∩ B| / |A ∪ B|。"""
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


# === 编辑距离 ===

def edit_distance(s1: str, s2: str) -> int:
    """Levenshtein 编辑距离（空间优化为 O(min(m,n))）。"""
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (0 if c1 == c2 else 1)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def normalized_edit_distance(s1: str, s2: str) -> float:
    """归一化编辑距离 = edit_distance / max(len(s1), len(s2))。"""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 0.0
    return edit_distance(s1, s2) / max_len


# === TF-IDF 余弦相似度 ===

def compute_idf(corpus: List[List[str]]) -> dict:
    """计算逆文档频率（平滑版，避免 log(1)=0 的问题）。"""
    doc_count = len(corpus)
    if doc_count == 0:
        return {}

    df = {}
    for tokens in corpus:
        seen = set(tokens)
        for token in seen:
            df[token] = df.get(token, 0) + 1

    return {
        token: math.log((doc_count + 1) / (count + 1)) + 1.0
        for token, count in df.items()
    }


def build_tfidf_vector(tokens: list, idf_dict: dict) -> dict:
    """构建 TF-IDF 向量。"""
    tf = {}
    for token in tokens:
        tf[token] = tf.get(token, 0) + 1

    total = len(tokens) if tokens else 1
    return {
        token: (count / total) * idf_dict.get(token, 1.0)
        for token, count in tf.items()
    }


def cosine_similarity_vec(vec_a: dict, vec_b: dict) -> float:
    """余弦相似度。"""
    common_keys = set(vec_a.keys()) & set(vec_b.keys())
    dot_product = sum(vec_a[k] * vec_b[k] for k in common_keys)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


# === 综合比对 ===

def combine_scores(ngram_sim: float, edit_dist_norm: float,
                   cosine_sim: float) -> float:
    """综合评分（加权平均）。"""
    edit_sim = 1.0 - edit_dist_norm
    return 0.3 * ngram_sim + 0.3 * edit_sim + 0.4 * cosine_sim


def compare_paragraphs(para_a: str, para_b: str,
                       idf_dict: dict = None) -> dict:
    """计算两段文本的全部相似度指标。"""
    # n-gram Jaccard
    ngrams_a = char_ngrams(para_a, n=3)
    ngrams_b = char_ngrams(para_b, n=3)
    ngram_sim = jaccard_similarity(ngrams_a, ngrams_b)

    # 编辑距离
    preprocessed_a = preprocess_text(para_a)
    preprocessed_b = preprocess_text(para_b)
    edit_dist = normalized_edit_distance(preprocessed_a, preprocessed_b)

    # TF-IDF 余弦
    tokens_a = tokenize_chinese(preprocessed_a)
    tokens_b = tokenize_chinese(preprocessed_b)

    if idf_dict is None:
        idf_dict = compute_idf([tokens_a, tokens_b])

    vec_a = build_tfidf_vector(tokens_a, idf_dict)
    vec_b = build_tfidf_vector(tokens_b, idf_dict)
    cosine_sim = cosine_similarity_vec(vec_a, vec_b)

    combined = combine_scores(ngram_sim, edit_dist, cosine_sim)

    return {
        "ngram_jaccard": round(ngram_sim, 4),
        "edit_distance_normalized": round(edit_dist, 4),
        "cosine_similarity": round(cosine_sim, 4),
        "combined_score": round(combined, 4),
    }


def _determine_risk_level(max_score: float, suspicious_count: int,
                          total: int) -> str:
    """根据检测结果确定风险等级。"""
    if suspicious_count == 0:
        return "low"
    ratio = suspicious_count / total if total > 0 else 0
    if max_score >= 0.95 or ratio >= 0.5:
        return "critical"
    if max_score >= 0.85 or ratio >= 0.3:
        return "high"
    if max_score >= 0.7 or ratio >= 0.1:
        return "medium"
    return "low"


def scan_for_plagiarism(input_text: str, reference_texts: dict,
                        threshold: float = 0.7) -> CopyrightReport:
    """
    主入口：扫描输入文本与参考文本库的相似度。

    Args:
        input_text: 待检剧本全文
        reference_texts: {"source_id": "全文内容", ...}
        threshold: 判定阈值 (默认 0.7)

    Returns:
        CopyrightReport
    """
    input_paragraphs = split_paragraphs(input_text)

    if not input_paragraphs:
        return CopyrightReport(
            total_paragraphs=0,
            suspicious_paragraphs=0,
            max_similarity_score=0.0,
            risk_level="low",
        )

    # 构建参考文本段落
    ref_paragraphs = {}
    for ref_id, ref_text in reference_texts.items():
        ref_paragraphs[ref_id] = split_paragraphs(ref_text)

    # 构建全局 IDF
    all_token_lists = []
    for para in input_paragraphs:
        all_token_lists.append(tokenize_chinese(preprocess_text(para)))
    for ref_id, paras in ref_paragraphs.items():
        for para in paras:
            all_token_lists.append(tokenize_chinese(preprocess_text(para)))
    global_idf = compute_idf(all_token_lists)

    # 逐段比对
    results = []
    for i, input_para in enumerate(input_paragraphs):
        best_match = None
        best_score = 0.0

        for ref_id, ref_paras in ref_paragraphs.items():
            for j, ref_para in enumerate(ref_paras):
                scores = compare_paragraphs(input_para, ref_para, global_idf)
                if scores["combined_score"] > best_score:
                    best_score = scores["combined_score"]
                    best_match = SimilarityResult(
                        source_paragraph_index=i,
                        source_text=input_para[:100],
                        reference_id=ref_id,
                        reference_paragraph_index=j,
                        reference_text=ref_para[:100],
                        ngram_jaccard=scores["ngram_jaccard"],
                        edit_distance_normalized=scores["edit_distance_normalized"],
                        cosine_similarity=scores["cosine_similarity"],
                        combined_score=scores["combined_score"],
                        is_suspicious=scores["combined_score"] >= threshold,
                    )

        if best_match and best_match.is_suspicious:
            results.append(best_match)

    suspicious_count = len(results)
    max_score = max((r.combined_score for r in results), default=0.0)

    return CopyrightReport(
        total_paragraphs=len(input_paragraphs),
        suspicious_paragraphs=suspicious_count,
        max_similarity_score=round(max_score, 4),
        risk_level=_determine_risk_level(
            max_score, suspicious_count, len(input_paragraphs)
        ),
        results=results,
    )


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="文本相似度检测")
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--reference-dir", required=True, help="参考文本目录")
    parser.add_argument("--threshold", type=float, default=0.7, help="判定阈值")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)

    input_text = input_path.read_text(encoding="utf-8")

    ref_dir = Path(args.reference_dir)
    reference_texts = {}
    if ref_dir.exists():
        for f in ref_dir.glob("*.txt"):
            reference_texts[f.stem] = f.read_text(encoding="utf-8")

    report = scan_for_plagiarism(input_text, reference_texts, args.threshold)

    print(f"=== 版权侵权检测报告 ===")
    print(f"总段落数: {report.total_paragraphs}")
    print(f"可疑段落: {report.suspicious_paragraphs}")
    print(f"最高相似度: {report.max_similarity_score}")
    print(f"风险等级: {report.risk_level}")

    if report.results:
        print(f"\n可疑段落详情:")
        for r in report.results:
            print(f"\n  段落 {r.source_paragraph_index}: "
                  f"综合得分 {r.combined_score:.4f}")
            print(f"  来源: {r.reference_id} 段落 {r.reference_paragraph_index}")
            print(f"  原文: {r.source_text[:60]}...")
            print(f"  参考: {r.reference_text[:60]}...")
