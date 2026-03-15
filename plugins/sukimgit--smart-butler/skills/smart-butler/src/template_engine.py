"""
模板引擎
根据场景选择模板并生成文档
"""

import os
from pathlib import Path
from datetime import datetime


# 模板配置
TEMPLATES = {
    "技术": {
        "file": "技术方案模板.md",
        "keywords": ["技术", "方案", "开发", "实施", "系统"],
        "default_fields": {
            "background": "待补充",
            "requirements": "1. 待补充\n2. 待补充",
            "solution": "待补充",
            "plan": "第一阶段：待补充\n第二阶段：待补充",
            "expected_results": "1. 待补充\n2. 待补充",
            "risks": "1. 待补充\n2. 待补充",
            "budget": "待补充"
        }
    },
    "销售": {
        "file": "销售方案模板.md",
        "keywords": ["销售", "客户", "报价", "商务", "产品"],
        "default_fields": {
            "pain_points": "1. 待补充\n2. 待补充",
            "solution": "待补充",
            "advantages": "1. 待补充\n2. 待补充",
            "comparison": "待补充",
            "pricing": "待补充",
            "cases": "待补充",
            "service": "待补充"
        }
    },
    "周会": {
        "file": "周会报告模板.md",
        "keywords": ["周会", "周报", "例会", "进展"],
        "default_fields": {
            "week": "第 X 周",
            "progress": "待补充",
            "issues": "待补充",
            "coordination": "待补充",
            "next_week_plan": "待补充",
            "goals_table": "| - | - | - | - |"
        }
    },
    "投标": {
        "file": "投标方案模板.md",
        "keywords": ["投标", "标书", "招标"],
        "default_fields": {
            "bid_letter": "待补充",
            "qualifications": "待补充",
            "technical_solution": "待补充",
            "implementation_plan": "待补充",
            "pricing_details": "待补充",
            "after_sales": "待补充",
            "case_studies": "待补充",
            "company": "待补充"
        }
    }
}


def detect_template_type(meeting_topic: str) -> str:
    """
    根据会议主题检测模板类型
    
    :param meeting_topic: 会议主题
    :return: 模板类型
    """
    for template_type, config in TEMPLATES.items():
        for keyword in config["keywords"]:
            if keyword in meeting_topic:
                return template_type
    
    # 默认返回技术模板
    return "技术"


def load_template(template_type: str) -> tuple[str, dict]:
    """
    加载模板
    
    :param template_type: 模板类型
    :return: (模板内容，默认字段)
    """
    if template_type not in TEMPLATES:
        template_type = "技术"
    
    config = TEMPLATES[template_type]
    template_file = os.path.join("D:\\OpenClawDocs\\templates", config["file"])
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content, config["default_fields"]


def generate_from_template(
    template_type: str,
    title: str,
    custom_fields: dict = None,
    author: str = "老高"
) -> tuple[str, str]:
    """
    从模板生成文档
    
    :param template_type: 模板类型
    :param title: 文档标题
    :param custom_fields: 自定义字段
    :param author: 作者
    :return: (文档内容，文件名)
    """
    # 加载模板
    template_content, default_fields = load_template(template_type)
    
    # 合并字段
    fields = default_fields.copy()
    if custom_fields:
        fields.update(custom_fields)
    
    # 添加通用字段
    fields["title"] = title
    fields["version"] = "1.0"
    fields["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    fields["author"] = author
    
    # 渲染模板
    content = template_content
    for key, value in fields.items():
        content = content.replace(f"{{{key}}}", str(value))
    
    # 生成文件名
    safe_title = "".join(c for c in title if c.isalnum() or c in "_-")
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}_{safe_title}_v1.md"
    
    return content, filename


def save_document(content: str, filename: str, category: str = "temp") -> str:
    """
    保存文档
    
    :param content: 文档内容
    :param filename: 文件名
    :param category: 类别 (temp/projects/meetings)
    :return: 完整路径
    """
    base_path = Path(f"D:\\OpenClawDocs\\{category}")
    base_path.mkdir(parents=True, exist_ok=True)
    
    file_path = base_path / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(file_path)


def list_templates() -> list:
    """
    列出所有模板
    
    :return: 模板列表
    """
    return [
        {
            "type": template_type,
            "file": config["file"],
            "keywords": config["keywords"]
        }
        for template_type, config in TEMPLATES.items()
    ]


# 测试
if __name__ == "__main__":
    # 测试模板检测
    test_topics = [
        "技术方案讨论会",
        "销售方案汇报",
        "项目周会",
        "投标方案评审"
    ]
    
    print("=== 模板类型检测 ===")
    for topic in test_topics:
        template_type = detect_template_type(topic)
        print(f"{topic} → {template_type}模板")
    
    # 测试生成
    print("\n=== 生成销售方案 ===")
    content, filename = generate_from_template(
        template_type="销售",
        title="AI 视觉监控系统销售方案",
        custom_fields={
            "pain_points": "1. 人工巡检效率低\n2. 安全隐患发现不及时",
            "solution": "基于 AI 视觉的智能监控方案",
            "pricing": "3.98W/套"
        }
    )
    
    print(f"生成文件：{filename}")
    print(f"内容预览：{content[:200]}...")
