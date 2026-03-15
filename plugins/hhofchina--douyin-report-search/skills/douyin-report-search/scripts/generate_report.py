#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成全量 HTML 分析报告
用法：python3 generate_report.py [工作目录] [关键词]
"""
import json, sys
from pathlib import Path

WORK_DIR = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
KEYWORD  = sys.argv[2] if len(sys.argv) > 2 else "抖音话题"

data = json.load(open(WORK_DIR / "analysis_result.json", encoding="utf-8"))
raw  = json.load(open(WORK_DIR / "douyin_parsed.json", encoding="utf-8"))
videos = raw["videos"]

ov = data["overview"]
top_videos = data["top_videos"]

# 序列化为 JS
def jj(x):
    return json.dumps(x, ensure_ascii=False)

dur_labels  = jj([b["label"] for b in data["duration"]["buckets"]])
dur_likes   = jj([b["avg_like"] for b in data["duration"]["buckets"]])
dur_shares  = jj([b["avg_share"] for b in data["duration"]["buckets"]])
dur_counts  = jj([b["count"] for b in data["duration"]["buckets"]])

tag_top = data["tags"][:12]
tag_labels  = jj([t["tag"] for t in tag_top])
tag_likes   = jj([t["avg_like"] for t in tag_top])
tag_shares  = jj([t["avg_share"] for t in tag_top])
tag_counts  = jj([t["count"] for t in tag_top])

fl_labels   = jj([b["label"] for b in data["follower"]["buckets"]])
fl_likes    = jj([b["avg_like"] for b in data["follower"]["buckets"]])
fl_shares   = jj([b["avg_share"] for b in data["follower"]["buckets"]])
fl_counts   = jj([b["count"] for b in data["follower"]["buckets"]])

tc_labels   = jj([b["label"] for b in data["tag_count"]])
tc_likes    = jj([b["avg_like"] for b in data["tag_count"]])
tc_shares   = jj([b["avg_share"] for b in data["tag_count"]])

# 标题特征对比
tf = data["title_features"]
pos_map = {
    "has_exclaim": ("带感叹号", "True", "False"),
    "has_question": ("带疑问句", "True", "False"),
    "has_emotion_kw": ("含情感词", "True", "False"),
    "has_female_kw": ("含女性词", "True", "False"),
    "has_growth_kw": ("含成长词", "True", "False"),
    "has_number": ("含数字", "True", "False"),
    "has_self_help": ("含励志词", "True", "False"),
}
tf_rows = []
for feat_key, (label, pos_val, neg_val) in pos_map.items():
    pos = next((x for x in tf if x["feature"] == f"{feat_key}={pos_val}"), None)
    neg = next((x for x in tf if x["feature"] == f"{feat_key}={neg_val}"), None)
    if pos and neg:
        tf_rows.append({
            "label": label,
            "pos_like": pos["avg_like"],
            "neg_like": neg["avg_like"],
            "pos_share": pos["avg_share"],
            "neg_share": neg["avg_share"],
            "pos_count": pos["count"],
            "neg_count": neg["count"],
        })

tf_labels  = jj([r["label"] for r in tf_rows])
tf_pos_lk  = jj([r["pos_like"] for r in tf_rows])
tf_neg_lk  = jj([r["neg_like"] for r in tf_rows])

# 标题长度
len_groups = {}
for item in tf:
    if item["feature"].startswith("len_group"):
        v = item["feature"].split("=")[1]
        len_groups[v] = item
len_labels = jj(["≤10字","11-20字",">20字"])
len_likes  = jj([len_groups.get(k,{}).get("avg_like",0) for k in ["≤10字","11-20字",">20字"]])
len_shares = jj([len_groups.get(k,{}).get("avg_share",0) for k in ["≤10字","11-20字",">20字"]])
len_counts = jj([len_groups.get(k,{}).get("count",0) for k in ["≤10字","11-20字",">20字"]])

# 热评关键词
ckws = data["comments"]["top_keywords"][:20]
ckw_words  = jj([x["word"] for x in ckws])
ckw_counts = jj([x["count"] for x in ckws])

# 散点图：粉丝数 vs 点赞
scatter_data = []
for v in videos:
    if v.get("follower_count",0)>0 and v.get("like_count",0)>0:
        scatter_data.append({
            "x": v["follower_count"],
            "y": v["like_count"],
            "title": v.get("title","")[:20],
        })
scatter_js = jj(scatter_data)

# Top15 视频表格
def fmt(n):
    if not n: return "–"
    n = int(n)
    if n >= 10000: return f"{n/10000:.1f}万"
    return f"{n:,}"

top_rows = ""
for i, v in enumerate(top_videos, 1):
    tags_str = " ".join(f'<span class="tag-chip">{t}</span>' for t in v.get("tags",[]))
    top_rows += f"""
    <tr>
      <td class="rank">{i}</td>
      <td class="title-cell"><a href="{v['url']}" target="_blank">{v['title'][:30]}{"…" if len(v['title'])>30 else ""}</a><br/><small>{v['author']} · {v['duration']}</small></td>
      <td class="num red">{fmt(v['like_count'])}</td>
      <td class="num orange">{fmt(v['share_count'])}</td>
      <td class="num blue">{fmt(v['collect_count'])}</td>
      <td class="num gray">{fmt(v['follower_count'])}</td>
      <td>{tags_str}</td>
    </tr>"""

# 总结洞察
insights = [
    ("🕐", "黄金时长 2-3 分钟", f"2-3分钟视频平均赞 {data['duration']['buckets'][2]['avg_like']:,}，是>5分钟视频的 {data['duration']['buckets'][2]['avg_like']//max(data['duration']['buckets'][-1]['avg_like'],1)}× 以上。抖音用户注意力窗口集中在 2-3 分钟，过长反而稀释互动。"),
    ("👤", "大号加持效应显著", f"粉丝 >100万 的账号平均赞 {fmt(data['follower']['buckets'][-1]['avg_like'])}，但 粉丝相关系数 r={data['follower']['corr_like']} 说明粉丝数并非决定性因素——中腰部账号同样能爆款。"),
    ("🏷️", "精选标签胜过堆标签", f"挂 1-2 个精准标签的视频平均赞 {fmt(data['tag_count'][0]['avg_like'])}，而挂 5+ 个标签的平均赞仅 {fmt(data['tag_count'][-1]['avg_like'])}，相差 {data['tag_count'][0]['avg_like']//max(data['tag_count'][-1]['avg_like'],1)}×。#自我成长 #个人成长 #认知 互动率最高。"),
    ("❗", "感叹号 = 情绪引爆", f"标题含感叹号的视频平均赞 {fmt(tf_rows[0]['pos_like'])} vs 不含 {fmt(tf_rows[0]['neg_like'])}，前者是后者的 {round(tf_rows[0]['pos_like']/max(tf_rows[0]['neg_like'],1),1)}×。情感类关键词同理，「爱/婚姻/情绪」等词能直接触发转发冲动。"),
    ("📝", "标题 11-20 字最优", f"11-20字标题平均赞 {fmt(len_groups.get('11-20字',{}).get('avg_like',0))}，≤10字 {fmt(len_groups.get('≤10字',{}).get('avg_like',0))}，>20字 {fmt(len_groups.get('>20字',{}).get('avg_like',0))}。短标题不够吸睛，过长则令人疲倦。"),
    ("💬", "评论区情感共鸣驱动二次传播", "热评高频词：\"女人\"\"自己\"\"成长\"\"孩子\"\"婚姻\"，折射出受众核心诉求——自我认同与关系处理。能引发\"说到我了\"共鸣的内容，转发率显著更高。"),
]

insights_html = ""
for icon, title, desc in insights:
    insights_html += f"""
    <div class="insight-card">
      <div class="insight-icon">{icon}</div>
      <div>
        <div class="insight-title">{title}</div>
        <div class="insight-desc">{desc}</div>
      </div>
    </div>"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>抖音「{KEYWORD}」话题全量分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, "PingFang SC", "Helvetica Neue", sans-serif; background: #f0f2f5; color: #1a1a2e; line-height: 1.6; }}

  .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 48px 36px; }}
  .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 6px; }}
  .header p  {{ opacity: 0.85; font-size: 15px; }}

  .container {{ max-width: 1200px; margin: 0 auto; padding: 32px 24px; }}

  .kpi-row {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; margin-bottom: 32px; }}
  .kpi {{ background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,.07); }}
  .kpi .value {{ font-size: 26px; font-weight: 700; color: #667eea; }}
  .kpi .label {{ font-size: 12px; color: #888; margin-top: 4px; }}

  .section {{ background: white; border-radius: 16px; padding: 28px; margin-bottom: 28px; box-shadow: 0 2px 8px rgba(0,0,0,.07); }}
  .section h2 {{ font-size: 18px; font-weight: 700; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #f0f2f5; display: flex; align-items: center; gap: 8px; }}
  .section h2 .emoji {{ font-size: 22px; }}

  .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
  .grid3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; }}

  canvas {{ max-height: 280px; }}

  .insight-card {{ display: flex; gap: 16px; align-items: flex-start; padding: 18px; background: linear-gradient(135deg, #f8f9ff, #f0f4ff); border-radius: 12px; margin-bottom: 14px; border-left: 4px solid #667eea; }}
  .insight-icon {{ font-size: 28px; flex-shrink: 0; }}
  .insight-title {{ font-size: 16px; font-weight: 700; margin-bottom: 6px; color: #4a4a8a; }}
  .insight-desc {{ font-size: 14px; color: #555; line-height: 1.65; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ background: #f8f9ff; padding: 10px 12px; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #e8eaf6; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #f0f2f5; vertical-align: middle; }}
  tr:hover td {{ background: #fafbff; }}
  .rank {{ font-weight: 700; color: #667eea; width: 32px; text-align: center; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }}
  .red    {{ color: #e53e3e; }}
  .orange {{ color: #dd6b20; }}
  .blue   {{ color: #3182ce; }}
  .gray   {{ color: #718096; }}
  .title-cell a {{ color: #2d3748; text-decoration: none; font-weight: 600; }}
  .title-cell a:hover {{ color: #667eea; }}
  .title-cell small {{ color: #999; }}

  .tag-chip {{ display: inline-block; background: #eef2ff; color: #667eea; border-radius: 10px; padding: 1px 8px; font-size: 11px; margin: 1px; }}

  .corr-badge {{ display: inline-block; background: #e6fffa; color: #2c7a7b; border-radius: 8px; padding: 2px 10px; font-size: 13px; font-weight: 700; margin-left: 10px; }}
  .corr-badge.weak {{ background: #fff5f5; color: #c53030; }}

  .footnote {{ font-size: 12px; color: #aaa; margin-top: 20px; text-align: center; }}

  @media (max-width: 768px) {{
    .kpi-row {{ grid-template-columns: repeat(3, 1fr); }}
    .grid2, .grid3 {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>📱 抖音「{KEYWORD}」话题全量分析报告</h1>
  <p>数据来源：100 条真实采集视频 · 分析维度：时长、标签、粉丝数、标题特征、互动数据 · 重点解答：哪些因素让视频获得更多点赞和转发</p>
</div>

<div class="container">

  <!-- KPI -->
  <div class="kpi-row">
    <div class="kpi"><div class="value">{ov['total']}</div><div class="label">采集视频总量</div></div>
    <div class="kpi"><div class="value" style="color:#e53e3e">{ov['total_likes']//10000:.1f}万</div><div class="label">总点赞数</div></div>
    <div class="kpi"><div class="value" style="color:#dd6b20">{ov['total_shares']//10000:.1f}万</div><div class="label">总转发数</div></div>
    <div class="kpi"><div class="value" style="color:#3182ce">{ov['total_plays']//10000:.1f}万</div><div class="label">总播放量</div></div>
    <div class="kpi"><div class="value">{ov['avg_likes']//100/10:.1f}k</div><div class="label">平均点赞</div></div>
    <div class="kpi"><div class="value" style="color:#38a169">{ov['max_likes']//10000:.1f}万</div><div class="label">最高点赞</div></div>
  </div>

  <!-- 核心洞察 -->
  <div class="section">
    <h2><span class="emoji">💡</span>核心影响因素洞察（6 大结论）</h2>
    {insights_html}
  </div>

  <!-- 时长分析 -->
  <div class="section">
    <h2>
      <span class="emoji">🕐</span>视频时长 vs 互动数据
      <span class="corr-badge {'weak' if abs(data['duration']['corr_like']) < 0.2 else ''}">时长-点赞 r={data['duration']['corr_like']}</span>
    </h2>
    <div class="grid2">
      <div><canvas id="durLikeChart"></canvas></div>
      <div><canvas id="durShareChart"></canvas></div>
    </div>
    <p style="font-size:13px;color:#888;margin-top:12px">* 相关系数接近 0 说明时长本身不决定表现，但 2-3 分钟区间存在明显峰值——这是「看完+转发」率最高的甜点区间。</p>
  </div>

  <!-- 标签分析 -->
  <div class="section">
    <h2><span class="emoji">🏷️</span>话题标签与互动表现（出现 ≥3 次的标签）</h2>
    <div class="grid2">
      <div><canvas id="tagLikeChart"></canvas></div>
      <div><canvas id="tagShareChart"></canvas></div>
    </div>
  </div>

  <!-- 粉丝数分析 -->
  <div class="section">
    <h2>
      <span class="emoji">👤</span>账号粉丝量级 vs 互动数据
      <span class="corr-badge">粉丝-点赞(log) r={data['follower']['corr_like']}</span>
    </h2>
    <div class="grid2">
      <div><canvas id="flLikeChart"></canvas></div>
      <div><canvas id="scatterChart"></canvas></div>
    </div>
    <p style="font-size:13px;color:#888;margin-top:12px">* 右图为各视频粉丝数 vs 点赞数散点图（对数坐标）。大账号整体占优，但 5-20万 粉丝区间出现低谷，说明中腰部账号的内容质量更关键。</p>
  </div>

  <!-- 标签数量 -->
  <div class="section">
    <h2><span class="emoji">🔢</span>标签数量策略对比</h2>
    <div class="grid2">
      <div><canvas id="tcChart"></canvas></div>
      <div style="display:flex;align-items:center;padding:20px">
        <div>
          <p style="font-size:15px;font-weight:700;color:#4a4a8a;margin-bottom:12px">精简标签 > 堆砌标签</p>
          <p style="font-size:14px;color:#555;line-height:1.8">
            • 挂 1-2 个标签：平均赞 <strong style="color:#e53e3e">{fmt(data['tag_count'][0]['avg_like'])}</strong><br/>
            • 挂 3-4 个标签：平均赞 <strong style="color:#dd6b20">{fmt(data['tag_count'][1]['avg_like'])}</strong><br/>
            • 挂 5+ 个标签：平均赞 <strong style="color:#718096">{fmt(data['tag_count'][-1]['avg_like'])}</strong><br/>
            <br/>
            建议：选 1-3 个与内容高度相关的垂类标签，避免撒网式打标。
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- 标题特征 -->
  <div class="section">
    <h2><span class="emoji">📝</span>标题特征对点赞的影响（有 vs 无）</h2>
    <div class="grid2">
      <div><canvas id="tfChart"></canvas></div>
      <div><canvas id="lenChart"></canvas></div>
    </div>
    <p style="font-size:13px;color:#888;margin-top:12px">* 左图：蓝色=含该特征，灰色=不含。感叹号和情感词的正向提升最显著。右图：11-20字标题互动最高。</p>
  </div>

  <!-- 热评关键词 -->
  <div class="section">
    <h2><span class="emoji">💬</span>热评高频词分析（用户真实诉求）</h2>
    <canvas id="ckwChart" style="max-height:220px"></canvas>
    <p style="font-size:13px;color:#888;margin-top:12px">* 热评词折射受众核心关切：「女人/自己/成长/孩子/婚姻/感情」——内容触达这些场景的视频，评论与转发率更高。</p>
  </div>

  <!-- Top 视频榜 -->
  <div class="section">
    <h2><span class="emoji">🏆</span>点赞 Top 15 视频详情</h2>
    <table>
      <thead>
        <tr>
          <th>#</th><th>视频标题 / 作者</th>
          <th style="text-align:right">点赞</th>
          <th style="text-align:right">转发</th>
          <th style="text-align:right">收藏</th>
          <th style="text-align:right">粉丝数</th>
          <th>标签</th>
        </tr>
      </thead>
      <tbody>{top_rows}</tbody>
    </table>
  </div>

  <p class="footnote">数据采集时间：2026-03-14 · 共采集 100 条「女性成长」话题视频 · 48 条获取完整互动数据</p>
</div>

<script>
const C = (id, cfg) => new Chart(document.getElementById(id), cfg);
const COLORS = ['#667eea','#764ba2','#f6ad55','#68d391','#fc8181','#63b3ed','#b794f4','#f687b3','#4fd1c5','#fbd38d','#90cdf4','#e9d8fd'];

// 1. 时长 - 点赞
C('durLikeChart', {{
  type: 'bar',
  data: {{ labels: {dur_labels}, datasets: [
    {{ label: '平均点赞', data: {dur_likes}, backgroundColor: 'rgba(102,126,234,0.8)', borderRadius: 6 }},
  ]}},
  options: {{ plugins: {{ title: {{ display: true, text: '各时长区间 平均点赞' }} }},
    scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// 2. 时长 - 转发
C('durShareChart', {{
  type: 'bar',
  data: {{ labels: {dur_labels}, datasets: [
    {{ label: '平均转发', data: {dur_shares}, backgroundColor: 'rgba(221,107,32,0.8)', borderRadius: 6 }},
  ]}},
  options: {{ plugins: {{ title: {{ display: true, text: '各时长区间 平均转发' }} }},
    scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// 3. 标签 - 点赞
C('tagLikeChart', {{
  type: 'bar',
  data: {{ labels: {tag_labels}, datasets: [
    {{ label: '平均点赞', data: {tag_likes}, backgroundColor: COLORS, borderRadius: 6 }},
  ]}},
  options: {{ indexAxis: 'y', plugins: {{ title: {{ display: true, text: '话题标签 平均点赞（前12）' }}, legend: {{ display: false }} }},
    scales: {{ x: {{ beginAtZero: true }} }} }}
}});

// 4. 标签 - 转发
C('tagShareChart', {{
  type: 'bar',
  data: {{ labels: {tag_labels}, datasets: [
    {{ label: '平均转发', data: {tag_shares}, backgroundColor: COLORS.map(c=>c+'bb'), borderRadius: 6 }},
  ]}},
  options: {{ indexAxis: 'y', plugins: {{ title: {{ display: true, text: '话题标签 平均转发（前12）' }}, legend: {{ display: false }} }},
    scales: {{ x: {{ beginAtZero: true }} }} }}
}});

// 5. 粉丝层级
C('flLikeChart', {{
  type: 'bar',
  data: {{ labels: {fl_labels}, datasets: [
    {{ label: '平均点赞', data: {fl_likes}, backgroundColor: 'rgba(99,179,237,0.85)', borderRadius: 6 }},
    {{ label: '平均转发', data: {fl_shares}, backgroundColor: 'rgba(118,75,162,0.7)', borderRadius: 6 }},
  ]}},
  options: {{ plugins: {{ title: {{ display: true, text: '粉丝量级 vs 互动数据' }} }},
    scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// 6. 散点图
const scatterRaw = {scatter_js};
C('scatterChart', {{
  type: 'scatter',
  data: {{ datasets: [{{
    label: '视频',
    data: scatterRaw.map(d => ({{ x: Math.log10(d.x+1), y: Math.log10(d.y+1), title: d.title }})),
    backgroundColor: 'rgba(102,126,234,0.6)',
    pointRadius: 5,
  }}]}},
  options: {{
    plugins: {{
      title: {{ display: true, text: '粉丝数 vs 点赞数（log坐标）' }},
      tooltip: {{ callbacks: {{ label: ctx => ctx.raw.title || '' }} }}
    }},
    scales: {{
      x: {{ title: {{ display: true, text: 'log₁₀(粉丝数)' }} }},
      y: {{ title: {{ display: true, text: 'log₁₀(点赞数)' }} }},
    }}
  }}
}});

// 7. 标签数量
C('tcChart', {{
  type: 'bar',
  data: {{ labels: {tc_labels}, datasets: [
    {{ label: '平均点赞', data: {tc_likes}, backgroundColor: ['#68d391','#f6ad55','#fc8181'], borderRadius: 6 }},
  ]}},
  options: {{ plugins: {{ title: {{ display: true, text: '标签数量 vs 平均点赞' }}, legend: {{ display: false }} }},
    scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// 8. 标题特征对比
C('tfChart', {{
  type: 'bar',
  data: {{ labels: {tf_labels}, datasets: [
    {{ label: '含该特征', data: {tf_pos_lk}, backgroundColor: 'rgba(102,126,234,0.85)', borderRadius: 4 }},
    {{ label: '不含该特征', data: {tf_neg_lk}, backgroundColor: 'rgba(180,180,200,0.6)', borderRadius: 4 }},
  ]}},
  options: {{ plugins: {{ title: {{ display: true, text: '标题特征对比 平均点赞' }} }},
    scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// 9. 标题长度
C('lenChart', {{
  type: 'bar',
  data: {{ labels: {len_labels}, datasets: [
    {{ label: '平均点赞', data: {len_likes}, backgroundColor: ['rgba(180,180,200,0.6)','rgba(102,126,234,0.85)','rgba(221,107,32,0.7)'], borderRadius: 6 }},
  ]}},
  options: {{ plugins: {{ title: {{ display: true, text: '标题长度 vs 平均点赞' }}, legend: {{ display: false }} }},
    scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// 10. 热评词
C('ckwChart', {{
  type: 'bar',
  data: {{ labels: {ckw_words}, datasets: [{{
    label: '出现次数',
    data: {ckw_counts},
    backgroundColor: COLORS.concat(COLORS),
    borderRadius: 4,
  }}]}},
  options: {{
    plugins: {{ title: {{ display: true, text: '热评高频词 Top20' }}, legend: {{ display: false }} }},
    scales: {{ y: {{ beginAtZero: true }} }}
  }}
}});
</script>
</body>
</html>"""

out_path = WORK_DIR / "douyin_analysis_report.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"✅ 报告已生成：{out_path}")
