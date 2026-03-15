#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
思维模型推荐引擎 v1.0
根据用户输入的问题自动推荐最佳思维模型组合

使用方法:
    python recommend.py "我要分析一个行业是否值得进入"
    python recommend.py "如何评估这个投资机会"
    python recommend.py "分析 Tesla 的竞争优势"
"""

import json
import sys
import re
from typing import List, Dict, Tuple

# 模型知识库
MODELS_DB = {
    # 基础分析模型
    "PESTEL": {
        "name": "PESTEL 分析",
        "file": "pestel-analysis.md",
        "keywords": ["宏观", "环境", "政策", "经济", "社会", "技术", "法律"],
        "scenarios": ["宏观环境分析", "市场进入", "政策影响"],
        "description": "宏观环境扫描工具"
    },
    "SWOT": {
        "name": "SWOT 分析",
        "file": "swot-analysis.md",
        "keywords": ["优势", "劣势", "机会", "威胁", "内外部"],
        "scenarios": ["综合分析", "战略制定", "竞争分析"],
        "description": "内外部综合分析工具"
    },
    "Porter5": {
        "name": "波特五力",
        "file": "porters-five-forces.md",
        "keywords": ["行业", "竞争", "供应商", "购买者", "进入壁垒", "替代"],
        "scenarios": ["行业分析", "竞争策略", "市场进入"],
        "description": "行业竞争分析框架"
    },
    "MECE": {
        "name": "MECE 原则",
        "file": "mece-principle.md",
        "keywords": ["结构化", "分类", "不重不漏", "拆解"],
        "scenarios": ["问题分析", "结构化思考", "团队协作"],
        "description": "结构化思考原则"
    },
    "Systems": {
        "name": "系统思维",
        "file": "systems-thinking.md",
        "keywords": ["系统", "整体", "相互作用", "反馈", "循环"],
        "scenarios": ["复杂问题", "团队协作", "组织分析"],
        "description": "整体性分析框架"
    },
    "FirstPrinciples": {
        "name": "第一性原理",
        "file": "first-principles.md",
        "keywords": ["本质", "拆解", "基本原理", "回归"],
        "scenarios": ["创新", "本质分析", "产品定位"],
        "description": "本质拆解思维"
    },
    
    # 决策思维模型
    "SecondOrder": {
        "name": "二阶效应",
        "file": "second-order-effects.md",
        "keywords": ["连锁", "后果", "长期", "推演"],
        "scenarios": ["风险评估", "决策分析", "政策影响"],
        "description": "连锁反应推演"
    },
    "Occam": {
        "name": "奥卡姆剃刀",
        "file": "occams-razor.md",
        "keywords": ["简化", "简单", "假设"],
        "scenarios": ["问题简化", "决策优化"],
        "description": "简化原则"
    },
    "Hanlon": {
        "name": "汉隆剃刀",
        "file": "hans-razor.md",
        "keywords": ["归因", "恶意", "愚蠢"],
        "scenarios": ["人际分析", "组织行为"],
        "description": "归因简化原则"
    },
    "Inversion": {
        "name": "逆向思维",
        "file": "inversion.md",
        "keywords": ["反向", "失败", "避免"],
        "scenarios": ["风险评估", "竞争策略", "创新"],
        "description": "反向思考方法"
    },
    "GameTheory": {
        "name": "博弈论",
        "file": "game-theory.md",
        "keywords": ["策略", "互动", "纳什均衡", "定价", "竞争"],
        "scenarios": ["竞争策略", "定价策略", "谈判"],
        "description": "策略互动分析"
    },
    "Comparative": {
        "name": "比较优势",
        "file": "comparative-advantage.md",
        "keywords": ["优势", "专业化", "分工", "差异化"],
        "scenarios": ["职业选择", "竞争策略", "创业定位"],
        "description": "专业化分工思维"
    },
    "Opportunity": {
        "name": "机会成本",
        "file": "opportunity-cost.md",
        "keywords": ["选择", "代价", "放弃"],
        "scenarios": ["职业选择", "投资决策", "资源分配"],
        "description": "选择代价分析"
    },
    "LeanStartup": {
        "name": "精益创业",
        "file": "lean-startup.md",
        "keywords": ["MVP", "验证", "迭代", "快速"],
        "scenarios": ["创业", "产品开发", "市场验证"],
        "description": "快速验证方法"
    },
    
    # 趋势分析模型
    "Cycle": {
        "name": "周期理论",
        "file": "cycle-theory.md",
        "keywords": ["周期", "循环", "波动", "趋势"],
        "scenarios": ["宏观分析", "投资决策", "市场时机"],
        "description": "经济周期分析"
    },
    "PowerLaw": {
        "name": "幂律分布",
        "file": "power-law.md",
        "keywords": ["80/20", "分布", "头部", "长尾"],
        "scenarios": ["投资", "资源配置", "市场分析"],
        "description": "80/20 法则"
    },
    "Antifragile": {
        "name": "反脆弱",
        "file": "antifragile.md",
        "keywords": ["风险", "波动", "收益", "不确定性"],
        "scenarios": ["风险评估", "投资决策", "危机管理"],
        "description": "风险收益思维"
    },
    "CriticalMass": {
        "name": "临界质量",
        "file": "critical-mass.md",
        "keywords": ["临界点", "量变", "质变", "爆发"],
        "scenarios": ["市场进入", "产品增长", "技术采用"],
        "description": "量变到质变"
    },
    "LongTerm": {
        "name": "长期主义",
        "file": "long-term-thinking.md",
        "keywords": ["长期", "复利", "持续", "耐心"],
        "scenarios": ["投资", "职业发展", "企业战略"],
        "description": "复利思维"
    },
    
    # 概率思维模型
    "Probabilistic": {
        "name": "概率思维",
        "file": "probabilistic-thinking.md",
        "keywords": ["概率", "不确定性", "期望值", "风险"],
        "scenarios": ["投资决策", "风险评估", "决策分析"],
        "description": "不确定性决策"
    },
    "Bayes": {
        "name": "贝叶斯定理",
        "file": "bayes-theorem.md",
        "keywords": ["信念", "更新", "证据", "概率"],
        "scenarios": ["投资决策", "判断更新", "信息分析"],
        "description": "信念更新方法"
    },
    "Survivorship": {
        "name": "幸存者偏差",
        "file": "survivorship-bias.md",
        "keywords": ["沉默", "证据", "样本", "偏差"],
        "scenarios": ["投资分析", "案例学习", "风险评估"],
        "description": "沉默警惕"
    },
    
    # 商业战略模型
    "Network": {
        "name": "网络效应",
        "file": "network-effects.md",
        "keywords": ["网络", "平台", "规模", "效应"],
        "scenarios": ["平台战略", "创业", "竞争策略"],
        "description": "平台经济思维"
    },
    "BlueOcean": {
        "name": "蓝海战略",
        "file": "blue-ocean.md",
        "keywords": ["蓝海", "无竞争", "价值创新", "差异化"],
        "scenarios": ["创业", "市场进入", "产品定位"],
        "description": "无竞争市场策略"
    }
}

# 场景到模型的映射
SCENARIO_MAP = {
    "行业分析": ["Porter5", "Cycle", "PESTEL", "SWOT"],
    "投资决策": ["Probabilistic", "Bayes", "Antifragile", "PowerLaw", "LongTerm"],
    "创业方向": ["BlueOcean", "LeanStartup", "Network", "CriticalMass", "Comparative"],
    "竞争策略": ["Porter5", "GameTheory", "Comparative", "BlueOcean", "Inversion"],
    "风险评估": ["Inversion", "SecondOrder", "Survivorship", "Antifragile", "Probabilistic"],
    "职业选择": ["Comparative", "Opportunity", "LongTerm", "PowerLaw"],
    "宏观分析": ["PESTEL", "Cycle", "Systems", "LongTerm"],
    "产品定位": ["FirstPrinciples", "BlueOcean", "LeanStartup", "Network"],
    "市场进入": ["PESTEL", "Porter5", "CriticalMass", "BlueOcean"],
    "创新方向": ["FirstPrinciples", "Inversion", "BlueOcean", "Systems"],
}

# 关键词到模型的映射
KEYWORD_MAP = {
    "行业": ["Porter5", "PESTEL", "Cycle"],
    "投资": ["Probabilistic", "Bayes", "Antifragile", "PowerLaw", "Cycle"],
    "创业": ["BlueOcean", "LeanStartup", "Network", "CriticalMass"],
    "竞争": ["Porter5", "GameTheory", "Comparative", "Inversion"],
    "风险": ["Antifragile", "Probabilistic", "Inversion", "SecondOrder"],
    "职业": ["Comparative", "Opportunity", "LongTerm"],
    "宏观": ["PESTEL", "Cycle", "Systems"],
    "产品": ["FirstPrinciples", "LeanStartup", "BlueOcean"],
    "市场": ["PESTEL", "Porter5", "BlueOcean", "Network"],
    "创新": ["FirstPrinciples", "Inversion", "BlueOcean"],
    "分析": ["SWOT", "MECE", "Systems", "FirstPrinciples"],
    "决策": ["Probabilistic", "SecondOrder", "Opportunity", "GameTheory"],
    "战略": ["SWOT", "Porter5", "BlueOcean", "LongTerm"],
}


def extract_keywords(query: str) -> List[str]:
    """从查询中提取关键词"""
    keywords = []
    for keyword in KEYWORD_MAP.keys():
        if keyword in query:
            keywords.append(keyword)
    return keywords


def detect_scenario(query: str) -> str:
    """检测查询场景"""
    for scenario in SCENARIO_MAP.keys():
        if scenario in query:
            return scenario
    return None


def recommend_models(query: str, top_n: int = 4) -> List[Dict]:
    """
    根据查询推荐模型
    
    Args:
        query: 用户输入的问题
        top_n: 推荐模型数量
    
    Returns:
        推荐的模型列表
    """
    scores = {}
    
    # 1. 场景匹配（权重最高）
    scenario = detect_scenario(query)
    if scenario and scenario in SCENARIO_MAP:
        for model_id in SCENARIO_MAP[scenario]:
            scores[model_id] = scores.get(model_id, 0) + 10
    
    # 2. 关键词匹配
    keywords = extract_keywords(query)
    for keyword in keywords:
        for model_id in KEYWORD_MAP.get(keyword, []):
            scores[model_id] = scores.get(model_id, 0) + 5
    
    # 3. 模型关键词匹配
    for model_id, model_info in MODELS_DB.items():
        for keyword in model_info["keywords"]:
            if keyword in query:
                scores[model_id] = scores.get(model_id, 0) + 3
    
    # 4. 排序并返回 top_n
    sorted_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    recommendations = []
    for model_id, score in sorted_models[:top_n]:
        model_info = MODELS_DB[model_id]
        recommendations.append({
            "id": model_id,
            "name": model_info["name"],
            "file": model_info["file"],
            "description": model_info["description"],
            "score": score
        })
    
    return recommendations


def generate_output_template(models: List[Dict]) -> str:
    """生成输出模板"""
    template = []
    template.append("## 📊 推荐模型组合\n")
    
    for i, model in enumerate(models, 1):
        template.append(f"### {i}. {model['name']}")
        template.append(f"- **描述**: {model['description']}")
        template.append(f"- **文档**: `{model['file']}`")
        template.append(f"- **匹配度**: {'⭐' * min(5, model['score'] // 2)}\n")
    
    return "\n".join(template)


def generate_analysis_framework(models: List[Dict], topic: str) -> str:
    """生成分析框架模板"""
    template = []
    template.append(f"# 📋 {topic} 分析框架\n")
    template.append("## 推荐模型组合\n")
    
    for i, model in enumerate(models, 1):
        template.append(f"{i}. **{model['name']}** - {model['description']}")
    
    template.append("\n## 分析步骤\n")
    template.append("### 第一步：数据收集\n- [ ] 收集相关行业数据\n- [ ] 收集竞争对手信息\n- [ ] 收集市场环境信息\n")
    
    template.append("### 第二步：模型应用\n")
    for model in models:
        template.append(f"- [ ] 应用 **{model['name']}**: {model['description']}")
    
    template.append("\n### 第三步：综合分析\n- [ ] 整合各模型分析结果\n- [ ] 识别关键发现\n- [ ] 形成结论和建议\n")
    
    template.append("\n## 输出模板\n")
    template.append("```markdown\n")
    template.append("### 分析结论\n[在此填写主要发现]\n\n")
    template.append("### 关键洞察\n1. [洞察 1]\n2. [洞察 2]\n3. [洞察 3]\n\n")
    template.append("### 建议行动\n1. [行动 1]\n2. [行动 2]\n3. [行动 3]\n")
    template.append("```\n")
    
    return "\n".join(template)


def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python recommend.py \"你的问题\"")
        print("\n示例:")
        print("  python recommend.py \"我要分析一个行业是否值得进入\"")
        print("  python recommend.py \"如何评估这个投资机会\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"🔍 分析问题：{query}\n")
    
    # 推荐模型
    recommendations = recommend_models(query)
    
    if not recommendations:
        print("❌ 未找到匹配的模型，请尝试更具体的问题描述")
        sys.exit(1)
    
    # 输出推荐结果
    print(generate_output_template(recommendations))
    
    # 生成分析框架
    topic = query[:50] + "..." if len(query) > 50 else query
    print("\n" + "="*60 + "\n")
    print(generate_analysis_framework(recommendations, topic))
    
    # 输出 JSON 格式（可选，用于程序调用）
    if "--json" in sys.argv:
        print("\n" + "="*60 + "\n")
        print(json.dumps(recommendations, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
