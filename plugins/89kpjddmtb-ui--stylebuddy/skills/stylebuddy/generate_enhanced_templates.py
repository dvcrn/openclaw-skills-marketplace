"""
生成增强版搭配模板
包含更详细的字段：材质、版型、适用体型、价格档次等
"""

import json
import random

# 基础数据
CATEGORIES = {
    "outer": ["风衣", "大衣", "羽绒服", "棉服", "西装外套", "牛仔外套", "皮衣", "针织开衫"],
    "top": ["衬衫", "T恤", "针织衫", "卫衣", "毛衣", "背心", "吊带", "打底衫"],
    "bottom": ["牛仔裤", "休闲裤", "西裤", "半裙", "长裙", "短裤", "阔腿裤", "运动裤"],
    "dress": ["连衣裙", "长裙", "短裙", "包臀裙", "A字裙"],
    "shoes": ["帆布鞋", "运动鞋", "高跟鞋", "平底鞋", "靴子", "凉鞋", "乐福鞋"],
    "accessory": ["包包", "围巾", "帽子", "腰带", "首饰", "眼镜"]
}

MATERIALS = {
    "outer": ["棉混纺", "羊毛", "羊绒", "涤纶", "尼龙", "皮革"],
    "top": ["纯棉", "真丝", "雪纺", "针织", "棉麻", "莫代尔"],
    "bottom": ["牛仔布", "棉", "西装料", "针织", "亚麻", "聚酯纤维"],
    "dress": ["雪纺", "棉", "真丝", "针织", "蕾丝", "丝绒"],
    "shoes": ["帆布", "皮革", "麂皮", "PU", "网面"],
    "accessory": ["皮革", "帆布", "金属", "塑料", "织物"]
}

COLORS = {
    "基础色": ["白色", "黑色", "灰色", "米色", "卡其"],
    "大地色": ["棕色", "驼色", "焦糖色", "咖啡", "燕麦"],
    "彩色": ["粉色", "蓝色", "绿色", "黄色", "紫色", "红色", "橙色"],
    "莫兰迪": ["雾霾蓝", "豆沙粉", "灰绿", "烟灰", "浅紫"]
}

STYLES = ["简约", "优雅", "休闲", "职业", "街头", "甜美", "复古", "文艺", "运动", "奢华"]

OCCASIONS = ["日常", "上班", "约会", "聚会", "逛街", "旅行", "运动", "面试", "派对", "正式场合"]

BODY_TYPES = {
    "suitable": ["H型", "苹果型", "梨型", "沙漏型", "矩形"],
    "avoid": ["苹果型", "梨型", "H型", "沙漏型", "矩形"]
}

PRICE_LEVELS = ["平价", "中端", "高端", "奢侈"]

SEASONS = ["春", "夏", "秋", "冬", "春秋", "四季"]


def generate_enhanced_templates(count=300):
    """生成增强版搭配模板"""
    templates = []
    
    # 场景定义
    scenes = [
        {"name": "知性通勤", "style": "职业", "occasion": "上班", "price": "中端"},
        {"name": "休闲周末", "style": "休闲", "occasion": "日常", "price": "平价"},
        {"name": "优雅约会", "style": "优雅", "occasion": "约会", "price": "中端"},
        {"name": "甜美少女", "style": "甜美", "occasion": "逛街", "price": "平价"},
        {"name": "街头潮流", "style": "街头", "occasion": "聚会", "price": "中端"},
        {"name": "文艺复古", "style": "文艺", "occasion": "旅行", "price": "中端"},
        {"name": "运动活力", "style": "运动", "occasion": "运动", "price": "平价"},
        {"name": "奢华晚宴", "style": "奢华", "occasion": "派对", "price": "高端"},
        {"name": "简约基础", "style": "简约", "occasion": "日常", "price": "平价"},
        {"name": "复古港风", "style": "复古", "occasion": "聚会", "price": "中端"},
    ]
    
    for i in range(count):
        scene = random.choice(scenes)
        
        # 构建单品组合
        items = {}
        items_details = {}
        
        # 必选项：上衣/裙装
        if random.choice([True, False]):
            # 上下装搭配
            top_item = random.choice(CATEGORIES["top"])
            items["top"] = [top_item]
            items_details["top"] = {
                "name": top_item,
                "color": random.choice(COLORS["基础色"] + COLORS["莫兰迪"]),
                "material": random.choice(MATERIALS["top"]),
                "fit": random.choice(["修身", "宽松", "直筒", "短款"])
            }
            
            bottom_item = random.choice(CATEGORIES["bottom"])
            items["bottom"] = [bottom_item]
            items_details["bottom"] = {
                "name": bottom_item,
                "color": random.choice(COLORS["基础色"] + COLORS["大地色"]),
                "material": random.choice(MATERIALS["bottom"]),
                "fit": random.choice(["高腰", "直筒", "阔腿", "修身"])
            }
        else:
            # 连衣裙
            dress_item = random.choice(CATEGORIES["dress"])
            items["dress"] = [dress_item]
            items_details["dress"] = {
                "name": dress_item,
                "color": random.choice(COLORS["彩色"] + COLORS["莫兰迪"]),
                "material": random.choice(MATERIALS["dress"]),
                "fit": random.choice(["修身", "宽松", "A字", "包臀"])
            }
        
        # 可选外套（50%概率）
        if random.random() > 0.5:
            outer_item = random.choice(CATEGORIES["outer"])
            items["outer"] = [outer_item]
            items_details["outer"] = {
                "name": outer_item,
                "color": random.choice(COLORS["基础色"] + COLORS["大地色"]),
                "material": random.choice(MATERIALS["outer"]),
                "fit": random.choice(["oversize", "修身", "直筒", "长款"])
            }
        
        # 鞋子
        shoes_item = random.choice(CATEGORIES["shoes"])
        items["shoes"] = [shoes_item]
        items_details["shoes"] = {
            "name": shoes_item,
            "color": random.choice(["白色", "黑色", "棕色", "米色"]),
            "material": random.choice(MATERIALS["shoes"]),
            "style": random.choice(["休闲", "优雅", "运动", "复古"])
        }
        
        # 配饰（30%概率）
        if random.random() > 0.7:
            acc_item = random.choice(CATEGORIES["accessory"])
            items["accessory"] = [acc_item]
            items_details["accessory"] = {
                "name": acc_item,
                "color": random.choice(["金色", "银色", "棕色", "黑色"]),
                "material": random.choice(MATERIALS["accessory"])
            }
        
        # 颜色搭配
        colors = {
            "primary": [items_details.get("top", items_details.get("dress", {})).get("color", "白色")],
            "secondary": [items_details.get("bottom", {}).get("color", "")] if "bottom" in items_details else [],
            "accent": [items_details.get("outer", {}).get("color", "")] if "outer" in items_details else []
        }
        colors["secondary"] = [c for c in colors["secondary"] if c]
        colors["accent"] = [c for c in colors["accent"] if c]
        
        # 适用体型
        body_suitable = random.sample(BODY_TYPES["suitable"], random.randint(2, 3))
        body_avoid = random.sample([b for b in BODY_TYPES["avoid"] if b not in body_suitable], random.randint(0, 2))
        
        # 生成详细描述
        item_names = [v["name"] for v in items_details.values()]
        description = f"{scene['name']}风格，以{items_details.get('top', items_details.get('dress', {})).get('color', '主色')}为主色调，"
        description += f"搭配{', '.join(item_names[:2])}，"
        description += f"展现{scene['style']}气质，适合{scene['occasion']}场合"
        
        # 搭配建议
        tips = f"适合{', '.join(body_suitable)}身材"
        if body_avoid:
            tips += f"；{', '.join(body_avoid)}身材建议调整版型"
        tips += f"；{scene['price']}价位，品质感不错"
        
        template = {
            "id": f"t_{scene['style']}_{i+1:03d}",
            "name": scene["name"],
            "description": description,
            "style": scene["style"],
            "occasion": [scene["occasion"]],
            "price_level": scene["price"],
            "season": random.choice(SEASONS),
            "items": items,
            "items_details": items_details,
            "colors": colors,
            "body_type": {
                "suitable": body_suitable,
                "avoid": body_avoid
            },
            "tips": tips
        }
        
        templates.append(template)
    
    return templates


if __name__ == "__main__":
    templates = generate_enhanced_templates(300)
    
    with open("templates_enhanced.json", "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)
    
    print(f"已生成 {len(templates)} 个增强版搭配模板")
    print(f"示例模板：")
    print(json.dumps(templates[0], ensure_ascii=False, indent=2))