"""
会前准备清单生成器
根据会议主题自动生成需要准备的材料清单
"""

# 会议主题关键词映射
PREP_TEMPLATES = {
    # 技术/产品类
    "人员密集度": [
        "人员密集度检测方案文档",
        "历史检测数据报告",
        "算法准确率统计",
        "摄像头接入情况",
        "项目进展 PPT"
    ],
    "火灾监控": [
        "火灾监控方案文档",
        "历史告警记录",
        "设备运行状态报告",
        "误报率分析"
    ],
    "AI 视觉": [
        "AI 视觉方案文档",
        "模型性能报告",
        "测试数据集结果",
        "部署方案"
    ],
    "产品": [
        "产品介绍文档",
        "功能清单",
        "技术架构图",
        "竞品分析"
    ],
    
    # 销售/商务类
    "销售": [
        "产品介绍 PPT",
        "价格表",
        "客户案例",
        "合同模板"
    ],
    "客户": [
        "客户需求分析",
        "解决方案文档",
        "报价单",
        "合作协议"
    ],
    "投标": [
        "投标文件",
        "技术方案",
        "商务报价",
        "资质证明"
    ],
    
    # 内部管理类
    "周会": [
        "本周工作进展",
        "下周计划",
        "问题与风险",
        "需要协调事项"
    ],
    "项目": [
        "项目进度报告",
        "里程碑完成情况",
        "风险与问题",
        "资源需求"
    ],
    "评审": [
        "评审材料",
        "技术方案文档",
        "测试报告",
        "用户反馈"
    ],
    
    # 默认清单
    "default": [
        "会议议程",
        "相关文档资料",
        "笔记本/记录工具"
    ]
}


def generate_prep_list(meeting_content: str) -> list:
    """
    根据会议内容生成准备清单
    
    :param meeting_content: 会议主题/内容
    :return: 准备清单列表
    """
    prep_items = []
    matched = False
    
    # 关键词匹配
    for keyword, items in PREP_TEMPLATES.items():
        if keyword in meeting_content:
            prep_items.extend(items)
            matched = True
    
    # 如果没有匹配到关键词，使用默认清单
    if not matched:
        prep_items = PREP_TEMPLATES["default"].copy()
    
    # 去重
    return list(dict.fromkeys(prep_items))


def generate_prep_questions(meeting_content: str) -> list:
    """
    生成询问用户的问题列表
    
    :param meeting_content: 会议主题/内容
    :return: 问题列表
    """
    questions = []
    
    # 总是问的通用问题
    questions.append("需要我生成方案文档吗？")
    
    # 根据关键词问特定问题
    if any(k in meeting_content for k in ["人员密集度", "火灾监控", "AI 视觉"]):
        questions.append("需要调取历史检测数据吗？")
        questions.append("需要准备算法性能报告吗？")
    
    if any(k in meeting_content for k in ["销售", "客户", "投标"]):
        questions.append("需要准备报价单吗？")
        questions.append("需要客户案例资料吗？")
    
    if any(k in meeting_content for k in ["周会", "项目", "评审"]):
        questions.append("需要准备进展报告吗？")
    
    return questions[:3]  # 最多 3 个问题，避免太多


# 测试
if __name__ == "__main__":
    test_cases = [
        "人员密集度检测讨论会",
        "销售会议",
        "项目周会",
        "随便一个会"
    ]
    
    for case in test_cases:
        print(f"\n会议：{case}")
        prep = generate_prep_list(case)
        print(f"准备清单：{prep}")
        questions = generate_prep_questions(case)
        print(f"询问问题：{questions}")
