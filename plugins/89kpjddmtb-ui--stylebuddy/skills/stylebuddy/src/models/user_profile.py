"""
用户画像管理模块
处理用户信息收集和个性化偏好
"""

import json
from typing import Dict, List, Optional
from ..storage.database import Database


class UserProfileManager:
    """用户画像管理器"""
    
    # 预设选项
    BODY_TYPES = ["H型", "苹果型", "梨型", "沙漏型", "矩形"]
    
    STYLE_OPTIONS = [
        "简约", "优雅", "休闲", "职业", "街头",
        "甜美", "复古", "文艺", "运动", "奢华"
    ]
    
    COLOR_OPTIONS = [
        "白色", "黑色", "灰色", "米色", "卡其",
        "粉色", "蓝色", "绿色", "黄色", "紫色",
        "红色", "棕色", "驼色", "焦糖色"
    ]
    
    PRICE_OPTIONS = ["平价", "中端", "高端", "奢侈"]
    
    def __init__(self, database: Database):
        self.db = database
    
    def get_profile(self) -> Optional[Dict]:
        """获取用户画像"""
        return self.db.get_user_profile()
    
    def has_profile(self) -> bool:
        """检查是否已设置画像"""
        return self.db.has_user_profile()
    
    def create_profile_wizard(self) -> str:
        """创建用户画像引导流程"""
        guide = """🌸 首次使用，让我们了解一下你～

这样我能给你更精准的穿搭建议！

请告诉我：
1. **昵称**（怎么称呼你？）
2. **性别**（female/male）
3. **身高**（cm，如：165）
4. **体重**（kg，如：55）
5. **体型**（H型/苹果型/梨型/沙漏型/矩形）
6. **风格偏好**（多选：简约/优雅/休闲/职业/街头/甜美/复古/文艺/运动/奢华）
7. **喜欢的颜色**（多选）
8. **避开的颜色**（多选）
9. **价格偏好**（平价/中端/高端/奢侈）

💡 可以一次说完，也可以分批告诉我～
例如：我是小李，女，165cm，50kg，梨型身材，喜欢简约风格"""
        return guide
    
    def parse_profile_input(self, user_input: str) -> Dict:
        """
        解析用户输入的画像信息
        支持自然语言描述
        """
        profile = {
            'nickname': '',
            'gender': 'female',
            'height': None,
            'weight': None,
            'body_type': '',
            'style_preference': [],
            'color_preference': [],
            'avoid_colors': [],
            'price_preference': '中端'
        }
        
        import re
        text = user_input.lower()
        
        # 解析昵称（我是/叫/昵称）
        nickname_patterns = [
            r'(?:我是|叫|昵称)[是为]?\s*["\']?(\w{1,10})["\']?',
            r'(\w{2,6})[，,。]\s*(?:女|男)',
        ]
        for pattern in nickname_patterns:
            match = re.search(pattern, user_input)
            if match:
                profile['nickname'] = match.group(1).strip()
                break
        
        # 解析性别
        if any(kw in text for kw in ['男', '男生', 'male', 'boy']):
            profile['gender'] = 'male'
        elif any(kw in text for kw in ['女', '女生', 'female', 'girl']):
            profile['gender'] = 'female'
        
        # 解析身高（165cm / 1米65 / 身高165）
        height_patterns = [
            r'身高?\s*(\d{2,3})\s*(?:cm|厘米)?',
            r'(\d{2,3})\s*(?:cm|厘米)',
            r'(\d)米(\d{1,2})',
        ]
        for pattern in height_patterns:
            match = re.search(pattern, user_input)
            if match:
                if len(match.groups()) == 2:  # 1米65
                    profile['height'] = int(match.group(1)) * 100 + int(match.group(2))
                else:
                    h = int(match.group(1))
                    if 140 <= h <= 200:  # 合理范围
                        profile['height'] = h
                break
        
        # 解析体重（55kg / 体重55 / 110斤）
        weight_patterns = [
            r'体重?\s*(\d{2,3})\s*(?:kg|公斤)?',
            r'(\d{2,3})\s*(?:kg|公斤)',
            r'(\d{2,3})\s*(?:斤)',
        ]
        for pattern in weight_patterns:
            match = re.search(pattern, user_input)
            if match:
                w = int(match.group(1))
                if '斤' in user_input[match.start():match.end()+2]:
                    w = w // 2  # 斤转kg
                if 30 <= w <= 150:  # 合理范围
                    profile['weight'] = w
                break
        
        # 解析体型
        for body_type in self.BODY_TYPES:
            if body_type in user_input or body_type.lower() in text:
                profile['body_type'] = body_type
                break
        
        # 解析风格偏好
        for style in self.STYLE_OPTIONS:
            if style in user_input:
                if style not in profile['style_preference']:
                    profile['style_preference'].append(style)
        
        # 解析颜色偏好（喜欢/偏爱/偏好）
        color_section = re.search(r'(?:喜欢|偏爱|偏好|爱).*?(?:颜色|色)', user_input)
        if color_section:
            section = user_input[color_section.start():color_section.end()+20]
            for color in self.COLOR_OPTIONS:
                if color in section and color not in profile['color_preference']:
                    profile['color_preference'].append(color)
        
        # 解析避开的颜色（避开/不喜欢/讨厌）
        avoid_section = re.search(r'(?:避开|不喜欢|讨厌| avoid).*?(?:颜色|色)', user_input)
        if avoid_section:
            section = user_input[avoid_section.start():avoid_section.end()+20]
            for color in self.COLOR_OPTIONS:
                if color in section and color not in profile['avoid_colors']:
                    profile['avoid_colors'].append(color)
        
        # 解析价格偏好
        for price in self.PRICE_OPTIONS:
            if price in user_input:
                profile['price_preference'] = price
                break
        
        return profile
    
    def save_profile(self, profile: Dict) -> bool:
        """保存用户画像"""
        return self.db.save_user_profile(profile)
    
    def get_profile_summary(self) -> str:
        """获取用户画像摘要（用于显示）"""
        profile = self.get_profile()
        if not profile:
            return "暂无用户画像，请先设置～"
        
        result = f"👤 {profile.get('nickname', '我')} 的穿搭档案\n"
        result += "━" * 20 + "\n"
        
        # 基础信息
        gender = "女生" if profile.get('gender') == 'female' else "男生"
        result += f"📋 {gender}"
        
        if profile.get('height'):
            result += f" | {profile['height']}cm"
        if profile.get('weight'):
            result += f" | {profile['weight']}kg"
        if profile.get('body_type'):
            result += f"\n   体型：{profile['body_type']}"
        result += "\n"
        
        # 偏好
        if profile.get('style_preference'):
            result += f"🎨 风格：{'、'.join(profile['style_preference'][:3])}\n"
        
        if profile.get('color_preference'):
            result += f"❤️ 喜欢：{'、'.join(profile['color_preference'][:5])}\n"
        
        if profile.get('avoid_colors'):
            result += f"🚫 避开：{'、'.join(profile['avoid_colors'][:3])}\n"
        
        result += f"💰 价位：{profile.get('price_preference', '中端')}\n"
        
        return result
    
    def update_partial(self, updates: Dict) -> bool:
        """部分更新用户画像"""
        profile = self.get_profile() or {}
        profile.update(updates)
        return self.save_profile(profile)


# 便捷函数
def create_profile_manager(database: Database) -> UserProfileManager:
    """工厂函数"""
    return UserProfileManager(database)