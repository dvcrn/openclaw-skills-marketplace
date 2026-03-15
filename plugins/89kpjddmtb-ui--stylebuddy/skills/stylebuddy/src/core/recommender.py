"""
推荐引擎模块
智能搭配推荐核心逻辑
"""

import json
import random
from typing import List, Dict, Optional, Any
from datetime import datetime
import re
import os

class OutfitRecommender:
    """搭配推荐引擎"""
    
    def __init__(self, database):
        self.db = database
        self.templates = self._load_templates()
        self.color_schemes = self._load_color_schemes()
    
    def _load_templates(self) -> List[Dict]:
        """加载搭配模板"""
        template_path = "./assets/data/templates.json"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_templates()
    
    def _load_color_schemes(self) -> List[Dict]:
        """加载配色方案"""
        color_path = "./assets/data/color_schemes.json"
        if os.path.exists(color_path):
            with open(color_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_colors()
    
    def _get_default_templates(self) -> List[Dict]:
        """默认模板数据"""
        return [
            {
                "id": "t_casual_001",
                "name": "基础休闲搭配",
                "category": "休闲",
                "gender": "female",
                "occasions": ["日常", "逛街"],
                "items": {"outer": ["风衣"], "top": ["T恤"], "bottom": ["牛仔裤"], "shoes": ["小白鞋"]},
                "colors": {"primary": ["米色"], "accent": ["白色", "蓝色"]},
                "tips": "敞开穿更休闲，内搭塞进去显腿长"
            },
            {
                "id": "t_work_001",
                "name": "职场通勤搭配",
                "category": "职场",
                "gender": "female",
                "occasions": ["上班", "面试"],
                "items": {"outer": ["西装"], "top": ["衬衫"], "bottom": ["西裤"], "shoes": ["高跟鞋"]},
                "colors": {"primary": ["黑色", "白色"], "accent": ["藏青"]},
                "tips": "合身剪裁更显专业，配饰选择简约款"
            },
            {
                "id": "t_date_001",
                "name": "约会温柔搭配",
                "category": "约会",
                "gender": "female",
                "occasions": ["约会", "聚会"],
                "items": {"outer": ["针织开衫"], "top": ["连衣裙"], "bottom": [], "shoes": ["低跟鞋"]},
                "colors": {"primary": ["粉色", "米色"], "accent": ["白色"]},
                "tips": "柔和色调更有亲和力，适当露肤增加女人味"
            }
        ]
    
    def _get_default_colors(self) -> List[Dict]:
        """默认配色方案"""
        return [
            {"name": "经典黑白", "colors": ["黑色", "白色"], "style": "简约", "occasions": ["职场", "日常"]},
            {"name": "大地色系", "colors": ["米色", "卡其色", "棕色", "驼色"], "style": "优雅", "occasions": ["通勤", "休闲"]},
            {"name": "莫兰迪色", "colors": ["雾霾蓝", "灰粉", "豆绿", "燕麦"], "style": "温柔", "occasions": ["约会", "日常"]},
            {"name": "海军蓝白", "colors": ["藏青", "白色", "条纹"], "style": "清爽", "occasions": ["休闲", "度假"]}
        ]
    
    def recommend(self, occasion: str = "日常", weather: Dict = None, count: int = 3, user_profile: Dict = None) -> List[Dict]:
        """
        生成搭配推荐
        
        Args:
            occasion: 场合
            weather: 天气信息
            count: 推荐数量
            user_profile: 用户画像（可选）
        
        Returns:
            推荐方案列表
        """
        # 获取用户衣橱
        items = self.db.get_all_items()
        
        if not items:
            # 没有单品，返回纯模板推荐（考虑用户画像）
            return self._get_template_recommendations(occasion, count, user_profile)
        
        # 有单品，基于模板+实际单品生成（考虑用户画像）
        return self._generate_personalized_recommendations(items, occasion, weather, count, user_profile)
    
    def _filter_templates_by_profile(self, templates: List[Dict], user_profile: Dict) -> List[Dict]:
        """根据用户画像过滤模板"""
        if not user_profile:
            return templates
        
        filtered = []
        for template in templates:
            score = 0
            
            # 1. 风格匹配
            if user_profile.get('style_preference'):
                template_style = template.get('style', '')
                if template_style in user_profile['style_preference']:
                    score += 3
            
            # 2. 颜色偏好匹配
            if user_profile.get('color_preference'):
                template_colors = template.get('colors', {})
                primary_colors = template_colors.get('primary', [])
                for color in primary_colors:
                    if color in user_profile['color_preference']:
                        score += 2
            
            # 3. 避开颜色检查
            if user_profile.get('avoid_colors'):
                template_colors = template.get('colors', {})
                all_colors = template_colors.get('primary', []) + template_colors.get('secondary', [])
                has_avoid_color = any(c in user_profile['avoid_colors'] for c in all_colors)
                if has_avoid_color:
                    score -= 5  # 大幅减分
            
            # 4. 价格档次匹配
            if user_profile.get('price_preference'):
                template_price = template.get('price_level', '中端')
                if template_price == user_profile['price_preference']:
                    score += 1
            
            # 5. 体型适配
            if user_profile.get('body_type') and template.get('body_type'):
                body_type = user_profile['body_type']
                suitable = template['body_type'].get('suitable', [])
                avoid = template['body_type'].get('avoid', [])
                
                if body_type in suitable:
                    score += 2
                if body_type in avoid:
                    score -= 3
            
            # 6. 性别匹配
            if user_profile.get('gender'):
                template_gender = template.get('gender', 'female')
                if template_gender == user_profile['gender']:
                    score += 1
            
            # 保存得分
            template['_match_score'] = score
            filtered.append(template)
        
        # 按得分排序
        filtered.sort(key=lambda x: x.get('_match_score', 0), reverse=True)
        return filtered
    
    def _get_template_recommendations(self, occasion: str, count: int, user_profile: Dict = None) -> List[Dict]:
        """纯模板推荐（无单品时）"""
        # 过滤适合该场合的模板
        matching = [t for t in self.templates if occasion in t.get('occasions', [])]
        
        if not matching:
            matching = self.templates
        
        # 根据用户画像排序
        if user_profile:
            matching = self._filter_templates_by_profile(matching, user_profile)
        
        # 选择前 count 个
        selected = matching[:count]
        
        # 如果没有足够的匹配模板，随机补充
        if len(selected) < count:
            remaining = [t for t in self.templates if t not in selected]
            additional = random.sample(remaining, min(count - len(selected), len(remaining)))
            selected.extend(additional)
        
        # 格式化输出 - 确保使用中文名称
        return [self._format_template(t) for t in selected]
    
    def _generate_personalized_recommendations(self, items: List[Dict], occasion: str, 
                                                 weather: Dict, count: int, user_profile: Dict = None) -> List[Dict]:
        """个性化推荐（考虑用户画像）"""
        recommendations = []
        
        # 按类别分组
        by_category = {"outer": [], "top": [], "bottom": [], "shoes": [], "accessory": []}
        for item in items:
            cat = item.get('category', 'top')
            if cat in by_category:
                by_category[cat].append(item)
        
        # 根据天气调整
        temp = weather.get('temp', 20) if weather else 20
        need_outer = temp < 20
        need_warm = temp < 10
        
        # 生成方案 - 获取原始模板进行匹配
        matching_templates = [t for t in self.templates if occasion in t.get('occasions', [])]
        if not matching_templates:
            matching_templates = self.templates
        
        # 根据用户画像排序和过滤
        if user_profile:
            matching_templates = self._filter_templates_by_profile(matching_templates, user_profile)
        
        # 选择前 count*2 个进行匹配
        selected_templates = matching_templates[:count * 2]
        
        for template in selected_templates[:count]:
            outfit = self._match_items_to_template(template, by_category, need_outer)
            if outfit:
                # 添加个性化提示
                if user_profile:
                    outfit = self._add_personalized_tips(outfit, user_profile, weather)
                recommendations.append(outfit)
        
        # 如果匹配不够，补充纯模板（也考虑用户画像）
        if len(recommendations) < count:
            template_recs = self._get_template_recommendations(occasion, count - len(recommendations), user_profile)
            recommendations.extend(template_recs)
        
        return recommendations[:count]
    
    def _add_personalized_tips(self, outfit: Dict, user_profile: Dict, weather: Dict) -> Dict:
        """根据用户画像添加个性化建议"""
        tips = outfit.get('tips', '')
        personalized_tips = []
        
        # 体型建议
        if user_profile.get('body_type'):
            body_type = user_profile['body_type']
            if body_type == '苹果型':
                personalized_tips.append(f"【{body_type}穿搭建议】选择宽松上衣+修身下装，突出腿部线条")
            elif body_type == '梨型':
                personalized_tips.append(f"【{body_type}穿搭建议】强调上半身，选择A字裙/阔腿裤平衡下半身")
            elif body_type == 'H型':
                personalized_tips.append(f"【{body_type}穿搭建议】创造腰线，选择收腰款式或腰带点缀")
            elif body_type == '沙漏型':
                personalized_tips.append(f"【{body_type}穿搭建议】突出腰部曲线，选择修身款式")
        
        # 颜色偏好提示
        if user_profile.get('color_preference'):
            colors = '、'.join(user_profile['color_preference'][:3])
            personalized_tips.append(f"你偏爱的{colors}单品会让这套搭配更适合你")
        
        # 天气+体型综合建议
        if weather and user_profile.get('height'):
            temp = weather.get('temp', 20)
            if temp < 15 and user_profile['height'] < 160:
                personalized_tips.append("【小个子保暖技巧】选择高腰裤+短款外套，既保暖又显高")
        
        if personalized_tips:
            outfit['personalized_tips'] = '\n'.join(personalized_tips)
        
        return outfit
    
    def _match_items_to_template(self, template: Dict, by_category: Dict, need_outer: bool) -> Optional[Dict]:
        """将模板与用户单品匹配"""
        template_items = template.get('items', {})
        matched_items = []
        
        for cat, keywords in template_items.items():
            if not keywords:
                continue
            
            # 跳过外套如果不需要
            if cat == 'outer' and not need_outer:
                continue
            
            # 在用户单品中找匹配的
            user_items = by_category.get(cat, [])
            matched = self._find_matching_item(user_items, keywords, template.get('colors', {}))
            
            if matched:
                color = matched.get('color', '') or ''
                name = matched.get('name', '')
                # 避免颜色重复
                if color and name.startswith(color):
                    matched_items.append(name)
                else:
                    matched_items.append(f"{color}{name}")
            elif cat in ['top', 'bottom']:
                # 核心单品必须匹配到
                return None
        
        if len(matched_items) >= 2:
            # 获取友好的名称
            name = template.get('name', '')
            if not name or name.startswith('t_') or re.match(r'^.+搭配\s+\d+$', name):
                category = template.get('category', '搭配')
                occasions = template.get('occasions', ['日常'])
                occasion = occasions[0]
                # 避免重复（如类别和场合都是'其他'）
                if category == occasion or category in occasion:
                    name = f"{occasion}风"
                else:
                    name = f"{occasion}{category}风"
            
            # 获取参考图片
            image_path = self._get_outfit_image(template)
            
            return {
                "name": name,
                "items": matched_items,
                "tips": template.get('tips', ''),
                "template_id": template.get('id'),
                "matched": True,
                "image_path": image_path
            }
        
        return None
    
    def _find_matching_item(self, items: List[Dict], keywords: List[str], colors: Dict) -> Optional[Dict]:
        """根据关键词和颜色找匹配单品"""
        target_colors = colors.get('primary', []) + colors.get('accent', [])
        
        # 优先颜色匹配
        for item in items:
            item_color = item.get('color', '')
            if any(c in item_color for c in target_colors):
                return item
        
        # 其次关键词匹配
        for item in items:
            name = item.get('name', '')
            for kw in keywords:
                if kw in name:
                    return item
        
        # 随机选一个同类别
        return random.choice(items) if items else None
    
    def _format_template(self, template: Dict) -> Dict:
        """格式化模板为推荐格式"""
        items = []
        template_items = template.get('items', {})
        
        for cat, keywords in template_items.items():
            if keywords:
                items.append(keywords[0])
        
        # 获取中文名称
        name = template.get('name', '')
        # 如果名称是通用格式（如'休闲搭配 32'），生成更友好的名称
        if not name or name.startswith('t_') or re.match(r'^.+搭配\s+\d+$', name):
            category = template.get('category', '搭配')
            occasions = template.get('occasions', ['日常'])
            occasion = occasions[0]
            # 避免重复
            if category == occasion or category in occasion:
                name = f"{occasion}风"
            else:
                name = f"{occasion}{category}风"
        
        return {
            "name": name,
            "items": items,
            "tips": template.get('tips', ''),
            "template_id": template.get('id'),
            "matched": False
        }
    
    def get_item_styles(self, item_name: str) -> List[Dict]:
        """
        一衣多穿 - 获取某件单品的多种搭配方式
        """
        # 找包含该单品的模板
        matching_templates = []
        
        for template in self.templates:
            items = template.get('items', {})
            for cat, keywords in items.items():
                for kw in keywords:
                    if kw in item_name or item_name in kw:
                        matching_templates.append(template)
                        break
        
        # 如果没找到，基于类别推荐
        if not matching_templates:
            # 判断单品类别
            category = self._guess_category(item_name)
            matching_templates = [t for t in self.templates 
                                 if category in str(t.get('items', {}))]
        
        return [self._format_template(t) for t in matching_templates[:5]]
    
    def _guess_category(self, item_name: str) -> str:
        """猜测单品类别"""
        keywords = {
            "outer": ["风衣", "大衣", "外套", "西装", "夹克", "羽绒服"],
            "top": ["T恤", "衬衫", "卫衣", "毛衣", "针织衫"],
            "bottom": ["裤", "裙", "牛仔裤", "休闲裤"],
            "shoes": ["鞋", "靴", "拖"],
            "accessory": ["包", "围巾", "帽子", "项链"]
        }
        
        for cat, words in keywords.items():
            for w in words:
                if w in item_name:
                    return cat
        
        return "top"
    def _get_outfit_image(self, template: Dict) -> Optional[str]:
        """根据模板获取对应的参考图片路径（返回 workspace 可访问路径）"""
        import glob
        import random
        import shutil
        
        category = template.get('category', '休闲')
        
        category_map = {
            '休闲': 'casual', '职场': 'business', '约会': 'date',
            '聚会': 'party', '运动': 'sport', '旅行': 'travel', '其他': 'casual'
        }
        
        prefix = category_map.get(category, 'casual')
        skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        image_dir = os.path.join(skill_dir, 'assets', 'images', 'outfits')
        
        images = glob.glob(os.path.join(image_dir, f'{prefix}_*.jpg'))
        if not images:
            images = glob.glob(os.path.join(image_dir, '*.jpg'))
        
        if images:
            selected = random.choice(images)
            workspace_dir = '/Users/mac/.openclaw/workspace/stylebuddy_images'
            os.makedirs(workspace_dir, exist_ok=True)
            filename = os.path.basename(selected)
            workspace_path = os.path.join(workspace_dir, filename)
            if not os.path.exists(workspace_path):
                shutil.copy2(selected, workspace_path)
            return workspace_path
        
        return None
