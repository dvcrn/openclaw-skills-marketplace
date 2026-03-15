"""
视觉识别服务
支持三级策略：
1. 基座模型多模态（优先，免费）
2. Vision API（高精度，需配置）
3. 本地识别（降级，免费）
"""

import os
import base64
import requests
from typing import Dict, Optional, Tuple
from PIL import Image
import numpy as np


class VisionService:
    """视觉识别服务 - 基座模型优先，API其次，本地降级"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.vision_config = config.get('api', {}).get('vision', {})
        self.enabled = self.vision_config.get('enabled', False)
        self.provider = self.vision_config.get('provider', 'siliconflow')
        self.api_key = self.vision_config.get('api_key', '')
        self.model = self.vision_config.get('model', 'Qwen/Qwen-VL-Chat')
        self.local_config = self.vision_config.get('local_fallback', {})
        
        # 检测基座模型能力
        self.base_model_vision = self._detect_base_model_vision()
        
    def _detect_base_model_vision(self) -> bool:
        """检测基座模型是否支持多模态（Vision）"""
        try:
            from ..core.router import CapabilityRouter
            router = CapabilityRouter()
            caps = router.detect()
            model_tier = caps.get('model_tier', 'low')
            # high = 支持 vision + function calling
            return model_tier == 'high'
        except:
            # 检测失败，默认假设支持（因为 Kimi K2.5 支持）
            return True
        
    def analyze_image(self, image_path: str) -> Dict:
        """
        分析图片 - 三级策略：
        1. 基座模型多模态（如果支持）
        2. Vision API（如果配置了）
        3. 本地识别（降级）
        """
        # 策略1：基座模型多模态（优先，免费）
        if self.base_model_vision:
            try:
                result = self._analyze_with_base_model(image_path)
                if result and result.get('confidence', 0) > 0.6:
                    result['source'] = 'base_model'
                    return result
            except Exception as e:
                print(f"基座模型识别失败: {e}")
        
        # 策略2：Vision API（高精度，需配置）
        if self.enabled and self.api_key:
            try:
                result = self._analyze_with_api(image_path)
                if result and result.get('confidence', 0) > 0.6:
                    result['source'] = 'api'
                    return result
            except Exception as e:
                print(f"API识别失败: {e}")
        
        # 策略3：本地识别（降级，免费）
        result = self._analyze_locally(image_path)
        result['source'] = 'local'
        return result
    
    def _analyze_with_base_model(self, image_path: str) -> Optional[Dict]:
        """使用基座模型的多模态能力分析图片"""
        # 读取图片转 base64
        with open(image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # 构建 prompt
        prompt = """请分析这张衣服图片，识别以下信息：

【衣服外观】
1. 衣服名称（如：粉色针织开衫、蓝色牛仔裤）
2. 类别（上衣/裤装/裙装/外套/鞋包/配饰）
3. 主要颜色
4. 材质/面料（如：棉、羊毛、涤纶等）
5. 版型特点（宽松/修身/长款/短款等）

【吊牌信息】(如图片中有吊牌/标签，请识别)
6. 品牌名称
7. 价格
8. 尺码
9. 面料成分

【搭配属性】
10. 适合季节（春/夏/秋/冬/四季）
11. 风格标签（简约/优雅/休闲/职业等）
12. 适用场合（上班/约会/运动/日常等）

请直接返回 JSON 格式：
{"name": "...", "category": "...", "color": "...", "material": "...", "brand": "...", "price": "...", "size": "...", "fabric": "...", "season": "...", "style": "...", "occasions": ["..."]}"""

        # 调用基座模型（通过 OpenClaw 框架）
        try:
            import json
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]
            
            # 尝试调用模型（这里简化处理，实际由 OpenClaw 框架处理）
            # 返回模拟结果，实际应该调用 agent 的模型能力
            result = self._call_base_model(messages)
            
            if result:
                return {
                    "name": result.get('name', '未命名单品'),
                    "category": self._normalize_category(result.get('category', 'top')),
                    "color": result.get('color', '未知'),
                    "material": result.get('material', ''),
                    "fit": result.get('fit', ''),
                    "brand": result.get('brand', ''),
                    "price": result.get('price', ''),
                    "size": result.get('size', ''),
                    "fabric": result.get('fabric', ''),
                    "style": result.get('style', ''),
                    "season": result.get('season', '四季'),
                    "occasions": result.get('occasions', []),
                    "confidence": 0.9,
                    "raw_analysis": result
                }
        except Exception as e:
            print(f"基座模型调用失败: {e}")
            return None
    
    def _call_base_model(self, messages: list) -> Optional[Dict]:
        """调用基座模型（简化版，实际由 OpenClaw 处理）"""
        # 注意：这里实际应该通过 OpenClaw 的 agent 调用模型
        # 但目前框架限制，这里返回 None，让逻辑降级到 API 或本地
        # 未来可以扩展为真正的基座模型调用
        return None
    
    def _analyze_with_api(self, image_path: str) -> Optional[Dict]:
        """使用 Vision API 分析图片"""
        if self.provider == 'siliconflow':
            return self._analyze_with_siliconflow(image_path)
        elif self.provider == 'openai':
            return self._analyze_with_openai(image_path)
        return None
    
    def _analyze_with_siliconflow(self, image_path: str) -> Optional[Dict]:
        """使用 SiliconFlow Vision API"""
        with open(image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        prompt = """请分析这张衣服图片，识别以下信息：

【衣服外观】
1. 名称（如：粉色针织开衫、蓝色牛仔裤）
2. 类别（上衣/裤装/裙装/外套/鞋包/配饰）
3. 主要颜色
4. 材质/面料（如：棉、羊毛、涤纶、真丝等）
5. 版型特点（宽松/修身/长款/短款/oversize等）

【吊牌信息】(如图片中有吊牌/标签，请识别)
6. 品牌名称（如：ZARA、优衣库、Nike等）
7. 价格（如：299元、$49.99等）
8. 尺码（如：S、M、L、160/84A等）
9. 面料成分（如：棉95%、氨纶5%等）

【搭配属性】
10. 适合季节（春/夏/秋/冬/四季）
11. 风格标签（简约/优雅/休闲/职业/街头/甜美等）
12. 适用场合（上班/约会/运动/日常/派对等）

请返回 JSON 格式：
{
  "name": "衣服名称",
  "category": "类别",
  "color": "颜色",
  "material": "材质",
  "fit": "版型",
  "brand": "品牌",
  "price": "价格",
  "size": "尺码",
  "fabric": "面料成分",
  "season": "季节",
  "style": "风格",
  "occasions": ["场合1", "场合2"]
}"""
        
        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            "max_tokens": 500
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        import json
        try:
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            data = json.loads(content.strip())
            return {
                "name": data.get('name', '未命名单品'),
                "category": self._normalize_category(data.get('category', 'top')),
                "color": data.get('color', '未知'),
                "material": data.get('material', ''),
                "fit": data.get('fit', ''),  # 版型
                "brand": data.get('brand', ''),  # 品牌
                "price": data.get('price', ''),  # 价格
                "size": data.get('size', ''),  # 尺码
                "fabric": data.get('fabric', ''),  # 面料成分
                "style": data.get('style', ''),
                "season": data.get('season', '四季'),
                "occasions": data.get('occasions', []),  # 适用场合
                "confidence": 0.85,
                "raw_analysis": data
            }
        except:
            return {
                "name": "识别商品",
                "category": "top",
                "color": "未知",
                "material": "",
                "fit": "",
                "brand": "",
                "price": "",
                "size": "",
                "fabric": "",
                "style": "",
                "season": "四季",
                "occasions": [],
                "confidence": 0.5,
                "raw_analysis": {"text": content}
            }
    
    def _analyze_with_openai(self, image_path: str) -> Optional[Dict]:
        """使用 OpenAI Vision API（待实现）"""
        return None
    
    def _analyze_locally(self, image_path: str) -> Dict:
        """本地识别 - 使用 PIL + 基础图像处理"""
        result = {
            "name": "",
            "category": "top",
            "color": "",
            "material": "",
            "style": "",
            "season": "四季",
            "confidence": 0.0,
            "raw_analysis": {}
        }
        
        try:
            img = Image.open(image_path)
            
            # 提取主色调
            if self.local_config.get('extract_color', True):
                dominant_color = self._extract_dominant_color(img)
                color_name = self._rgb_to_color_name(dominant_color)
                result['color'] = color_name
                result['raw_analysis']['dominant_rgb'] = dominant_color
            
            # 检测类别
            if self.local_config.get('detect_category', True):
                category = self._detect_category_by_shape(img)
                result['category'] = category
            
            # 生成名称
            result['name'] = f"{result['color']}{self._category_to_name(result['category'])}"
            result['confidence'] = 0.5
            
        except Exception as e:
            result['name'] = "未识别单品"
            result['raw_analysis']['error'] = str(e)
        
        return result
    
    def _extract_dominant_color(self, img: Image.Image) -> Tuple[int, int, int]:
        """提取图片主色调"""
        img = img.copy()
        img.thumbnail((150, 150))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = np.array(img)
        pixels = pixels.reshape(-1, 3)
        
        # 过滤白色背景
        non_white = pixels[
            (pixels[:, 0] < 240) | 
            (pixels[:, 1] < 240) | 
            (pixels[:, 2] < 240)
        ]
        
        if len(non_white) > 0:
            avg_color = tuple(non_white.mean(axis=0).astype(int))
        else:
            avg_color = tuple(pixels.mean(axis=0).astype(int))
        
        return avg_color
    
    def _rgb_to_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """RGB 转颜色名称"""
        r, g, b = rgb
        
        if max(r, g, b) - min(r, g, b) < 30:
            if r > 200: return "白色"
            elif r > 150: return "浅灰"
            elif r > 80: return "灰色"
            else: return "黑色"
        
        max_val = max(r, g, b)
        if r == max_val and r > g + 20 and r > b + 20:
            return "红色" if r > 150 else "深红"
        elif g == max_val and g > r + 20 and g > b + 20:
            return "绿色"
        elif b == max_val and b > r + 20 and b > g + 20:
            return "蓝色"
        elif r > 150 and g > 100 and b < 100:
            return "橙色"
        elif r > 150 and g > 150 and b < 100:
            return "黄色"
        elif r > 100 and b > 100 and g < 100:
            return "紫色"
        elif r > 150 and g > 100 and b > 100:
            return "粉色"
        elif r > 100 and g > 100 and b > 100:
            return "米色" if r > 180 else "卡其"
        else:
            return "多色"
    
    def _detect_category_by_shape(self, img: Image.Image) -> str:
        """基于图像比例检测类别"""
        width, height = img.size
        ratio = height / width
        
        if ratio > 1.8: return "dress"
        elif ratio > 1.4: return "bottom"
        elif ratio < 0.6: return "accessory"
        else: return "top"
    
    def _normalize_category(self, category: str) -> str:
        """标准化类别名称"""
        category_map = {
            '上衣': 'top', 'top': 'top',
            '外套': 'outer', 'outer': 'outer',
            '裤装': 'bottom', '裤子': 'bottom', 'bottom': 'bottom',
            '裙子': 'dress', '裙装': 'dress', 'dress': 'dress',
            '鞋包': 'accessory', '配饰': 'accessory', 'accessory': 'accessory'
        }
        return category_map.get(category.lower(), 'top')
    
    def _category_to_name(self, category: str) -> str:
        """类别代码转中文名"""
        name_map = {
            'top': '上衣', 'outer': '外套', 'bottom': '裤装',
            'dress': '裙装', 'accessory': '配饰'
        }
        return name_map.get(category, '单品')


def create_vision_service(config: Dict) -> VisionService:
    """工厂函数创建 VisionService"""
    return VisionService(config)