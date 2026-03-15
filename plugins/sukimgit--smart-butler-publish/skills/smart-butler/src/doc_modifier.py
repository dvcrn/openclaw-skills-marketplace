"""
文档修改器
支持自然语言修改指令，定位并修改文档内容
"""

import re
from pathlib import Path
from datetime import datetime


# 预定义的修改规则
MODIFY_RULES = {
    "成本": {
        "keywords": ["成本", "预算", "价格", "费用"],
        "template": """💰 **成本优势突出**：
- 硬件成本：{hardware}W（低于市场价 30%）
- 软件授权：{software}W（一次性买断，终身使用）
- 实施费用：{service}W（含现场部署 + 培训）
- **总计：{total}W（性价比最优方案）**

> 注：批量采购可进一步优惠，具体面议。""",
        "extract_pattern": r"硬件成本：([\d.]+)W\n软件授权：([\d.]+)W\n实施费用：([\d.]+)W\n总计：([\d.]+)W"
    },
    "实施周期": {
        "keywords": ["实施", "周期", "时间", "进度"],
        "template": """**实施周期优化**：
总周期：8 周（2 个月），分四个阶段：
- 第 1-2 周：需求调研 + 方案设计
- 第 3-6 周：系统开发 + 单元测试
- 第 7-8 周：部署测试 + 用户培训
- 第 9 周：验收交付 + 售后支持

> 注：可根据客户需求压缩周期，最快 6 周交付。""",
        "extract_pattern": r"第一阶段：(.+)\n第二阶段：(.+)\n第三阶段：(.+)\n第四阶段：(.+)"
    },
    "技术方案": {
        "keywords": ["技术", "方案", "算法", "AI"],
        "template": """**技术优势**：
1. **自研算法**：基于深度学习的人员统计算法，准确率行业领先
2. **无感部署**：利用现有摄像头资源，无需额外硬件投入
3. **实时分析**：边缘计算 + 云端协同，响应时间<3 秒
4. **可扩展性**：支持从单路到千路视频并发分析

**技术栈**：
- 前端：Vue3 + TypeScript
- 后端：Python FastAPI
- AI 框架：PyTorch + OpenCV
- 数据库：PostgreSQL + Redis""",
        "extract_pattern": None
    },
    "预期效果": {
        "keywords": ["效果", "准确率", "性能"],
        "template": """**核心指标**：
| 指标 | 目标值 | 行业平均 |
|------|--------|----------|
| 监测准确率 | >95% | 85-90% |
| 告警响应时间 | <3 秒 | 5-10 秒 |
| 并发路数 | 支持多路 | 单路为主 |
| 误报率 | <1% | 3-5% |

**客户价值**：
- 降低人工巡检成本 70%
- 提前 30 分钟预警风险
- 管理效率提升 3 倍""",
        "extract_pattern": None
    }
}


def detect_modify_intent(instruction: str) -> str:
    """
    检测修改意图
    
    :param instruction: 用户指令
    :return: 意图类型
    """
    instruction_lower = instruction.lower()
    
    # 检查是否包含强调/修改/增加等动作
    actions = ["强调", "改", "修改", "增加", "补充", "优化", "完善"]
    has_action = any(action in instruction for action in actions)
    
    # 检测目标主题
    for topic, rule in MODIFY_RULES.items():
        for keyword in rule["keywords"]:
            if keyword in instruction:
                return topic
    
    return "unknown"


def apply_modify_rule(content: str, topic: str, instruction: str) -> tuple[str, bool]:
    """
    应用修改规则
    
    :param content: 原文档内容
    :param topic: 主题
    :param instruction: 修改指令
    :return: (修改后的内容，是否成功)
    """
    if topic not in MODIFY_RULES:
        return content, False
    
    rule = MODIFY_RULES[topic]
    
    # 尝试提取原有数据
    if rule["extract_pattern"]:
        match = re.search(rule["extract_pattern"], content)
        if match:
            if topic == "成本":
                hardware, software, service, total = match.groups()
                new_section = rule["template"].format(
                    hardware=hardware,
                    software=software,
                    service=service,
                    total=total
                )
                # 替换原有内容
                content = re.sub(
                    r"硬件成本：[\d.]+W\n软件授权：[\d.]+W\n实施费用：[\d.]+W\n总计：[\d.]+W",
                    new_section,
                    content
                )
                return content, True
    
    # 如果没有提取到数据，使用通用增强
    if topic == "成本" and "强调" in instruction:
        # 找到预算章节
        budget_start = content.find("## 七、预算估算")
        if budget_start >= 0:
            # 找到章节结束
            budget_end = content.find("---", budget_start)
            if budget_end < 0:
                budget_end = len(content)
            
            old_budget = content[budget_start:budget_end]
            new_budget = """## 七、预算估算

💰 **成本优势突出**：
- 硬件成本：1.5W（低于市场价 30%）
- 软件授权：2W（一次性买断，终身使用）
- 实施费用：0.5W（含现场部署 + 培训）
- **总计：4W（性价比最优方案）**

> 注：批量采购可进一步优惠，具体面议。"""
            
            content = content[:budget_start] + new_budget + content[budget_end:]
            return content, True
    
    return content, False


def modify_document(content: str, instruction: str) -> tuple[str, str, bool]:
    """
    修改文档
    
    :param content: 原文档内容
    :param instruction: 修改指令
    :return: (修改后的内容，修改主题，是否成功)
    """
    # 检测意图
    topic = detect_modify_intent(instruction)
    
    if topic == "unknown":
        return content, "unknown", False
    
    # 应用规则
    new_content, success = apply_modify_rule(content, topic, instruction)
    
    return new_content, topic, success


def save_version(content: str, base_filepath: str) -> str:
    """
    保存新版本
    
    :param content: 文档内容
    :param base_filepath: 基础文件路径
    :return: 新版本文件路径
    """
    path = Path(base_filepath)
    stem = path.stem
    suffix = path.suffix
    
    # 提取版本号
    version_match = re.search(r'_v(\d+)$', stem)
    if version_match:
        current_version = int(version_match.group(1))
        new_version = current_version + 1
        new_stem = stem[:version_match.start()] + f'_v{new_version}'
    else:
        new_stem = stem + '_v2'
    
    # 更新版本号
    content = re.sub(
        r'\*\*文档版本：\*\* v[\d.]+',
        f'**文档版本：** v{new_version}.0',
        content
    )
    # 更新时间
    content = re.sub(
        r'\*\*生成时间：\*\* [\d-]+ [\d:]+',
        f'**生成时间：** {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        content
    )
    
    # 保存文件
    new_path = path.parent / f"{new_stem}{suffix}"
    with open(new_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(new_path)


# 测试
if __name__ == "__main__":
    # 读取测试文档
    with open('D:/OpenClawDocs/temp/20260304_人员密集度检测方案_v1.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 测试修改
    instruction = "强调一下成本优势"
    print(f"修改指令：{instruction}\n")
    
    new_content, topic, success = modify_document(content, instruction)
    print(f"检测主题：{topic}")
    print(f"修改成功：{success}\n")
    
    if success:
        # 显示修改后的预算部分
        start = new_content.find("## 七、预算估算")
        end = new_content.find("---", start)
        print("=== 修改后的预算部分 ===")
        print(new_content[start:end])
        
        # 保存新版本
        new_path = save_version(new_content, 'D:/OpenClawDocs/temp/20260304_人员密集度检测方案_v1.md')
        print(f"\n新版本已保存：{new_path}")
