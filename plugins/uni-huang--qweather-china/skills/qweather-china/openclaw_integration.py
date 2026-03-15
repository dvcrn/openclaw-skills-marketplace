#!/usr/bin/env python3
"""
OpenClaw集成模块
将QWeather天气服务集成到OpenClaw中
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from qweather import QWeatherClient, WeatherNow, DailyForecast, LifeIndex

class OpenClawWeatherHandler:
    """OpenClaw天气处理器"""
    
    def __init__(self):
        self.client = QWeatherClient()
        self.command_patterns = self._init_command_patterns()
        
    def _init_command_patterns(self) -> Dict:
        """初始化命令模式"""
        return {
            r"(.*?)天气(怎么样)?[？?]?$": self.handle_weather_now,
            r"(.*?)的?温度(是多少)?[？?]?$": self.handle_temperature,
            r"(.*?)(今天|明天|后天)天气[？?]?$": self.handle_specific_day,
            r"(.*?)未来(\d+)天?预报[？?]?$": self.handle_forecast_days,
            r"(.*?)预报[？?]?$": self.handle_forecast,
            r"(.*?)生活指数[？?]?$": self.handle_life_indices,
            r"(.*?)空气质量[？?]?$": self.handle_air_quality,
            r"(.*?)需要带伞吗[？?]?$": self.handle_umbrella,
            r"(.*?)穿什么[？?]?$": self.handle_clothing,
            r"天气帮助[？?]?$": self.handle_help,
        }
    
    def extract_city(self, text: str) -> Tuple[str, str]:
        """从文本中提取城市"""
        # 常见城市映射
        city_map = {
            "北京": "beijing", "上海": "shanghai", "广州": "guangzhou",
            "深圳": "shenzhen", "杭州": "hangzhou", "成都": "chengdu",
            "武汉": "wuhan", "南京": "nanjing", "西安": "xian", "重庆": "chongqing",
            "bj": "beijing", "sh": "shanghai", "gz": "guangzhou", "sz": "shenzhen",
        }
        
        # 尝试匹配已知城市
        for chinese, english in city_map.items():
            if chinese in text:
                return english, chinese
        
        # 默认返回北京
        return "beijing", "北京"
    
    def handle_query(self, query: str) -> str:
        """处理用户查询"""
        query = query.strip()
        
        # 遍历所有模式
        for pattern, handler in self.command_patterns.items():
            match = re.match(pattern, query, re.IGNORECASE)
            if match:
                return handler(query, match)
        
        # 默认处理
        return self.handle_default(query)
    
    def handle_weather_now(self, query: str, match) -> str:
        """处理实时天气查询"""
        city_en, city_cn = self.extract_city(query)
        
        try:
            weather = self.client.get_weather_now(city_en)
            dressing = self.client.get_dressing_advice(weather.temp)
            umbrella = self.client.get_umbrella_advice(weather.precip, weather.text)
            
            return f"""
🌤️ {city_cn}当前天气 ({weather.obs_time})
🌡️ 温度: {weather.temp}°C (体感: {weather.feels_like}°C)
🌬️ 风力: {weather.wind_scale}级 ({weather.wind_speed}km/h) {weather.wind_dir}
💧 湿度: {weather.humidity}%
🌧️ 降水: {weather.precip}mm
📊 气压: {weather.pressure}hPa
👁️ 能见度: {weather.vis}公里
☁️ 云量: {weather.cloud}%

🎯 建议:
{dressing}
{umbrella}

📱 详细: {self.client.api_host}/weather/{city_cn}
"""
        except Exception as e:
            return f"❌ 获取{city_cn}天气失败: {str(e)}"
    
    def handle_temperature(self, query: str, match) -> str:
        """处理温度查询"""
        city_en, city_cn = self.extract_city(query)
        
        try:
            weather = self.client.get_weather_now(city_en)
            return f"🌡️ {city_cn}当前温度: {weather.temp}°C (体感: {weather.feels_like}°C)"
        except Exception as e:
            return f"❌ 获取{city_cn}温度失败: {str(e)}"
    
    def handle_specific_day(self, query: str, match) -> str:
        """处理特定日期天气"""
        city_en, city_cn = self.extract_city(query)
        day = match.group(2)  # 今天、明天、后天
        
        day_map = {"今天": 0, "明天": 1, "后天": 2}
        if day not in day_map:
            return "❌ 请指定今天、明天或后天"
        
        try:
            forecasts = self.client.get_weather_forecast(city_en, 3)
            if day_map[day] >= len(forecasts):
                return f"❌ 无法获取{city_cn}{day}的预报"
            
            forecast = forecasts[day_map[day]]
            return forecast.format()
        except Exception as e:
            return f"❌ 获取{city_cn}{day}天气失败: {str(e)}"
    
    def handle_forecast_days(self, query: str, match) -> str:
        """处理指定天数预报"""
        city_en, city_cn = self.extract_city(query)
        
        try:
            days = int(match.group(2))
            if days < 1 or days > 7:
                return "❌ 预报天数请选择1-7天"
            
            forecasts = self.client.get_weather_forecast(city_en, days)
            result = f"📅 {city_cn}未来{days}天预报\n"
            result += "=" * 50 + "\n"
            
            for forecast in forecasts:
                result += forecast.format() + "\n"
                result += "-" * 50 + "\n"
            
            return result
        except Exception as e:
            return f"❌ 获取{city_cn}预报失败: {str(e)}"
    
    def handle_forecast(self, query: str, match) -> str:
        """处理天气预报（默认3天）"""
        city_en, city_cn = self.extract_city(query)
        
        try:
            forecasts = self.client.get_weather_forecast(city_en, 3)
            result = f"📅 {city_cn}未来3天预报\n"
            result += "=" * 50 + "\n"
            
            for forecast in forecasts:
                result += forecast.format() + "\n"
                result += "-" * 50 + "\n"
            
            return result
        except Exception as e:
            return f"❌ 获取{city_cn}预报失败: {str(e)}"
    
    def handle_life_indices(self, query: str, match) -> str:
        """处理生活指数查询"""
        city_en, city_cn = self.extract_city(query)
        
        try:
            indices = self.client.get_life_indices(city_en)
            result = f"📊 {city_cn}今日生活指数\n"
            result += "=" * 50 + "\n"
            
            # 分类显示
            categories = {}
            for index in indices:
                if index.category not in categories:
                    categories[index.category] = []
                categories[index.category].append(index)
            
            for category, cat_indices in categories.items():
                result += f"\n{category}:\n"
                for index in cat_indices[:3]:  # 每个类别显示前3个
                    result += f"  {index.format()}\n"
            
            return result
        except Exception as e:
            return f"❌ 获取{city_cn}生活指数失败: {str(e)}"
    
    def handle_air_quality(self, query: str, match) -> str:
        """处理空气质量查询"""
        city_en, city_cn = self.extract_city(query)
        
        try:
            air_data = self.client.get_air_quality(city_en)
            now = air_data["now"]
            
            return f"""
🌫️ {city_cn}空气质量
更新时间: {air_data['updateTime']}
AQI指数: {now['aqi']} ({now['category']})
主要污染物: {now['primary']}
PM2.5: {now['pm2p5']} μg/m³
PM10: {now['pm10']} μg/m³
二氧化硫: {now['so2']} μg/m³
二氧化氮: {now['no2']} μg/m³
臭氧: {now['o3']} μg/m³
一氧化碳: {now['co']} mg/m³

💡 建议: {self._get_air_quality_advice(now['category'])}
"""
        except Exception as e:
            return f"❌ 获取{city_cn}空气质量失败: {str(e)}"
    
    def _get_air_quality_advice(self, category: str) -> str:
        """获取空气质量建议"""
        advice_map = {
            "优": "空气质量非常好，适合户外活动",
            "良": "空气质量良好，基本适合户外活动",
            "轻度污染": "敏感人群减少户外活动",
            "中度污染": "减少户外活动，外出佩戴口罩",
            "重度污染": "避免户外活动，关闭门窗",
            "严重污染": "尽量避免外出，使用空气净化器"
        }
        return advice_map.get(category, "请参考官方空气质量建议")
    
    def handle_umbrella(self, query: str, match) -> str:
        """处理雨伞查询"""
        city_en, city_cn = self.extract_city(query)
        
        try:
            weather = self.client.get_weather_now(city_en)
            umbrella = self.client.get_umbrella_advice(weather.precip, weather.text)
            return f"🌂 {city_cn}{umbrella}"
        except Exception as e:
            return f"❌ 获取{city_cn}天气失败: {str(e)}"
    
    def handle_clothing(self, query: str, match) -> str:
        """处理穿衣查询"""
        city_en, city_cn = self.extract_city(query)
        
        try:
            weather = self.client.get_weather_now(city_en)
            dressing = self.client.get_dressing_advice(weather.temp)
            return f"👕 {city_cn}{dressing}"
        except Exception as e:
            return f"❌ 获取{city_cn}温度失败: {str(e)}"
    
    def handle_help(self, query: str, match) -> str:
        """处理帮助查询"""
        return """
🌤️ 天气查询帮助
==============

常用命令:
1. [城市]天气 - 查询实时天气 (例: 北京天气)
2. [城市]温度 - 查询当前温度
3. [城市]今天/明天/后天天气 - 查询特定日期
4. [城市]预报 - 查询3天预报
5. [城市]未来N天预报 - 查询N天预报
6. [城市]生活指数 - 查询生活指数
7. [城市]空气质量 - 查询空气质量
8. [城市]需要带伞吗 - 雨伞建议
9. [城市]穿什么 - 穿衣建议

支持城市:
北京、上海、广州、深圳、杭州、成都、武汉、南京、西安、重庆

数据来源: 中国气象局 · 和风天气
"""
    
    def handle_default(self, query: str) -> str:
        """默认处理"""
        return f"🤔 我不太明白你的意思。你可以问我关于天气的问题，比如:\n- 北京天气怎么样？\n- 上海未来3天预报\n- 广州生活指数\n\n输入'天气帮助'查看完整帮助。"

# OpenClaw技能接口
class QWeatherSkill:
    """QWeather OpenClaw技能"""
    
    def __init__(self):
        self.handler = OpenClawWeatherHandler()
        self.name = "qweather-china"
        self.version = "1.0.0"
        self.description = "基于中国气象局数据的天气服务"
    
    def process(self, message: str, context: Dict = None) -> str:
        """处理消息"""
        try:
            response = self.handler.handle_query(message)
            return response
        except Exception as e:
            return f"❌ 天气服务暂时不可用: {str(e)}"
    
    def get_capabilities(self) -> List[str]:
        """获取技能能力"""
        return [
            "实时天气查询",
            "天气预报",
            "生活指数",
            "空气质量",
            "穿衣建议",
            "雨伞建议"
        ]
    
    def get_supported_cities(self) -> List[str]:
        """获取支持的城市"""
        return [
            "北京", "上海", "广州", "深圳", "杭州",
            "成都", "武汉", "南京", "西安", "重庆"
        ]

# 测试函数
def test_integration():
    """测试集成"""
    print("测试OpenClaw天气集成...")
    print("=" * 60)
    
    skill = QWeatherSkill()
    handler = OpenClawWeatherHandler()
    
    test_queries = [
        "北京天气怎么样？",
        "上海温度",
        "广州明天天气",
        "深圳未来3天预报",
        "杭州生活指数",
        "成都空气质量",
        "武汉需要带伞吗",
        "南京穿什么",
        "天气帮助",
        "随机查询"
    ]
    
    for query in test_queries:
        print(f"\n📝 查询: {query}")
        print(f"🤖 回复: {handler.handle_query(query)}")
        print("-" * 60)

if __name__ == "__main__":
    test_integration()