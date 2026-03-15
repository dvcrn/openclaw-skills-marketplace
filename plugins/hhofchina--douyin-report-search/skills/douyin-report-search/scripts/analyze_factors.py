#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量分析：哪些因素影响视频点赞和转发
用法：python3 analyze_factors.py [工作目录]
输出 analysis_result.json 供报告使用
"""
import json, re, math, sys
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

WORK_DIR = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()

data = json.load(open(WORK_DIR / "douyin_parsed.json"))
vs = data["videos"]

# ── 工具函数 ──────────────────────────────────────────────
def dur_to_sec(s):
    if not s or ":" not in s:
        return None
    parts = s.split(":")
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return None

def corr(x, y):
    """Pearson 相关系数"""
    x, y = np.array(x, float), np.array(y, float)
    if len(x) < 3:
        return 0
    if x.std() == 0 or y.std() == 0:
        return 0
    return float(np.corrcoef(x, y)[0, 1])

def fmt_num(n):
    if n >= 10000:
        return f"{n/10000:.1f}万"
    return str(n)

# ── 基础数据 ──────────────────────────────────────────────
valid = [v for v in vs if v.get("like_count", 0) > 0]
print(f"有点赞数: {len(valid)} 条")

likes   = [v["like_count"] for v in valid]
shares  = [v.get("share_count", 0) for v in valid]
plays   = [v.get("play_count", 0) for v in valid]
collects= [v.get("collect_count", 0) for v in valid]
comments= [v.get("comment_count", 0) for v in valid]
followers=[v.get("follower_count", 0) for v in valid]

# 互动综合指数
engagement = [l + s * 3 + c * 2 for l, s, c in zip(likes, shares, collects)]

result = {}

# ── 1. 基础统计 ──────────────────────────────────────────
result["overview"] = {
    "total": len(vs),
    "with_data": len(valid),
    "total_likes": int(sum(likes)),
    "total_shares": int(sum(shares)),
    "total_plays": int(sum(plays)),
    "avg_likes": int(np.mean(likes)),
    "median_likes": int(np.median(likes)),
    "max_likes": int(max(likes)),
    "avg_shares": int(np.mean(shares)),
    "median_shares": int(np.median(shares) if shares else 0),
    "max_shares": int(max(shares) if shares else 0),
    "avg_play": int(np.mean(plays)) if plays else 0,
}
print("✓ 基础统计完成")

# ── 2. 时长分析 ──────────────────────────────────────────
dur_data = []
for v in valid:
    sec = dur_to_sec(v.get("duration", ""))
    if sec:
        dur_data.append({
            "sec": sec, "like": v["like_count"],
            "share": v.get("share_count", 0),
            "engage": v["like_count"] + v.get("share_count",0)*3
        })

def bucket_label(sec):
    if sec <= 60:   return "≤1分钟"
    if sec <= 120:  return "1-2分钟"
    if sec <= 180:  return "2-3分钟"
    if sec <= 300:  return "3-5分钟"
    return ">5分钟"

bucket_stats = defaultdict(list)
for d in dur_data:
    bucket_stats[bucket_label(d["sec"])].append(d)

dur_result = []
for label in ["≤1分钟","1-2分钟","2-3分钟","3-5分钟",">5分钟"]:
    items = bucket_stats.get(label, [])
    if items:
        dur_result.append({
            "label": label,
            "count": len(items),
            "avg_like": int(np.mean([i["like"] for i in items])),
            "avg_share": int(np.mean([i["share"] for i in items])),
            "avg_engage": int(np.mean([i["engage"] for i in items])),
        })

# 相关系数
secs = [d["sec"] for d in dur_data]
dur_likes = [d["like"] for d in dur_data]
dur_shares = [d["share"] for d in dur_data]
result["duration"] = {
    "buckets": dur_result,
    "corr_like": round(corr(secs, dur_likes), 3),
    "corr_share": round(corr(secs, dur_shares), 3),
}
print("✓ 时长分析完成")

# ── 3. 标签分析 ──────────────────────────────────────────
tag_stats = defaultdict(list)
for v in valid:
    tags = v.get("tags", [])
    for t in tags:
        tag_stats[t].append({
            "like": v["like_count"],
            "share": v.get("share_count", 0),
            "engage": v["like_count"] + v.get("share_count",0)*3
        })

tag_result = []
for tag, items in tag_stats.items():
    if len(items) >= 3:
        tag_result.append({
            "tag": tag,
            "count": len(items),
            "avg_like": int(np.mean([i["like"] for i in items])),
            "avg_share": int(np.mean([i["share"] for i in items])),
            "avg_engage": int(np.mean([i["engage"] for i in items])),
        })
tag_result.sort(key=lambda x: x["avg_engage"], reverse=True)
result["tags"] = tag_result[:20]
print(f"✓ 标签分析完成 ({len(tag_result)} 个有效标签)")

# ── 4. 粉丝数 vs 点赞 ──────────────────────────────────
fv_data = [(v.get("follower_count",0), v["like_count"], v.get("share_count",0))
           for v in valid if v.get("follower_count",0) > 0]

def follower_bucket(n):
    if n < 10000:     return "<1万"
    if n < 50000:     return "1-5万"
    if n < 200000:    return "5-20万"
    if n < 1000000:   return "20-100万"
    return ">100万"

fb_stats = defaultdict(list)
for fn, lk, sh in fv_data:
    fb_stats[follower_bucket(fn)].append({"like": lk, "share": sh})

fb_result = []
for label in ["<1万","1-5万","5-20万","20-100万",">100万"]:
    items = fb_stats.get(label, [])
    if items:
        fb_result.append({
            "label": label,
            "count": len(items),
            "avg_like": int(np.mean([i["like"] for i in items])),
            "avg_share": int(np.mean([i["share"] for i in items])),
        })

fn_list = [x[0] for x in fv_data]
lk_list = [x[1] for x in fv_data]
sh_list = [x[2] for x in fv_data]

# log变换的相关系数（更稳定）
log_fn = [math.log10(x+1) for x in fn_list]
log_lk = [math.log10(x+1) for x in lk_list]
log_sh = [math.log10(x+1) for x in sh_list]

result["follower"] = {
    "buckets": fb_result,
    "corr_like": round(corr(log_fn, log_lk), 3),
    "corr_share": round(corr(log_fn, log_sh), 3),
}
print("✓ 粉丝数分析完成")

# ── 5. 标题特征分析 ──────────────────────────────────────
def title_features(title):
    feats = {}
    feats["has_question"]   = "？" in title or "?" in title
    feats["has_exclaim"]    = "！" in title or "!" in title
    feats["has_number"]     = bool(re.search(r"\d", title))
    feats["has_female_kw"]  = any(w in title for w in ["女","姐","妈","她","女人","女性","女生","姑娘","妻","母"])
    feats["has_growth_kw"]  = any(w in title for w in ["成长","成熟","提升","改变","升华","觉醒","蜕变","逆袭","跃迁"])
    feats["has_emotion_kw"] = any(w in title for w in ["爱","感情","婚姻","恋爱","心动","情绪","幸福","痛苦","快乐","伤","难过"])
    feats["has_self_help"]  = any(w in title for w in ["自律","坚持","努力","奋斗","拼搏","赚钱","自信","独立","自我"])
    title_len = len(title)
    feats["len_group"] = "≤10字" if title_len <= 10 else ("11-20字" if title_len <= 20 else ">20字")
    return feats

feat_stats = defaultdict(lambda: {"like": [], "share": []})
for v in valid:
    title = v.get("title", "")
    feats = title_features(title)
    for feat, val in feats.items():
        key = f"{feat}={val}"
        feat_stats[key]["like"].append(v["like_count"])
        feat_stats[key]["share"].append(v.get("share_count", 0))

title_result = []
for key, data in feat_stats.items():
    lks = data["like"]
    shs = data["share"]
    title_result.append({
        "feature": key,
        "count": len(lks),
        "avg_like": int(np.mean(lks)),
        "avg_share": int(np.mean(shs)),
        "avg_engage": int(np.mean([l + s*3 for l, s in zip(lks, shs)])),
    })
result["title_features"] = sorted(title_result, key=lambda x: x["avg_engage"], reverse=True)
print("✓ 标题特征分析完成")

# ── 6. 标签数量 ──────────────────────────────────────────
tag_count_stats = defaultdict(lambda: {"like":[], "share":[]})
for v in valid:
    n = len(v.get("tags", []))
    bucket = "0个" if n==0 else ("1-2个" if n<=2 else ("3-4个" if n<=4 else "5+个"))
    tag_count_stats[bucket]["like"].append(v["like_count"])
    tag_count_stats[bucket]["share"].append(v.get("share_count", 0))

tc_result = []
for label in ["0个","1-2个","3-4个","5+个"]:
    d = tag_count_stats.get(label)
    if d and d["like"]:
        tc_result.append({
            "label": label,
            "count": len(d["like"]),
            "avg_like": int(np.mean(d["like"])),
            "avg_share": int(np.mean(d["share"])),
        })
result["tag_count"] = tc_result
print("✓ 标签数量分析完成")

# ── 7. 热评特征 ──────────────────────────────────────────
comment_kws = Counter()
has_comment_likes = []
no_comment_likes  = []
for v in valid:
    comments_data = v.get("top_comments", [])
    if comments_data:
        has_comment_likes.append(v["like_count"])
        for c in comments_data:
            text = c.get("text", "")
            for w in re.findall(r"[\u4e00-\u9fff]{2,4}", text):
                comment_kws[w] += 1
    else:
        no_comment_likes.append(v["like_count"])

result["comments"] = {
    "top_keywords": [{"word": w, "count": c} for w, c in comment_kws.most_common(30)],
    "avg_like_with_comments": int(np.mean(has_comment_likes)) if has_comment_likes else 0,
    "avg_like_without": int(np.mean(no_comment_likes)) if no_comment_likes else 0,
}
print("✓ 热评分析完成")

# ── 8. Top 视频样本 ──────────────────────────────────────
top_videos = sorted(valid, key=lambda v: v["like_count"], reverse=True)[:15]
result["top_videos"] = [{
    "title": v["title"],
    "like_count": v["like_count"],
    "share_count": v.get("share_count", 0),
    "collect_count": v.get("collect_count", 0),
    "comment_count": v.get("comment_count", 0),
    "follower_count": v.get("follower_count", 0),
    "play_count": v.get("play_count", 0),
    "duration": v.get("duration", ""),
    "tags": v.get("tags", []),
    "author": v.get("author_nickname", ""),
    "url": v.get("video_url", ""),
} for v in top_videos]

# ── 综合影响力排序 ─────────────────────────────────────
# 量化各因素对 like 的影响（效应量：有 vs 无的均值比）
factors = []

# 时长
for item in result["duration"]["buckets"]:
    factors.append({"factor": f"时长{item['label']}", "avg_like": item["avg_like"], "avg_share": item["avg_share"], "count": item["count"]})

# 标签
for item in result["tags"][:10]:
    factors.append({"factor": f"#{item['tag']}", "avg_like": item["avg_like"], "avg_share": item["avg_share"], "count": item["count"]})

result["factor_summary"] = sorted(factors, key=lambda x: x["avg_like"], reverse=True)

out_path = WORK_DIR / "analysis_result.json"
json.dump(result, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n✅ 分析完成，已保存到 {out_path}")
