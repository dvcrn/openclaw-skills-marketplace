#!/usr/bin/env python3
"""
QWeather China - 基于中国气象局数据的完整天气服务
和风天气API封装，提供实时天气、预报、生活指数等功能
"""

import os
import json
import time
import jwt
import requests
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# 配置常量 - 从环境变量或配置文件读取
def load_config():
    """从环境变量加载配置（ClawHub会注入配置）"""
    import os
    from pathlib import Path
    
    # 从环境变量获取配置（ClawHub会自动注入）
    config = {
        "kid": os.environ.get("QWEATHER_KID", ""),
        "sub": os.environ.get("QWEATHER_SUB", ""),
        "api_host": os.environ.get("QWEATHER_API_HOST", ""),
        "private_key_path": os.environ.get("QWEATHER_PRIVATE_KEY_PATH", ""),
        "cache_dir": os.environ.get("QWEATHER_CACHE_DIR", str(Path.home() / ".openclaw" / "cache" / "qweather")),
        "cache_ttl": {
            "now": 600,      # 10分钟
            "forecast": 3600, # 1小时
            "indices": 10800, # 3小时
            "air": 1800,     # 30分钟
        }
    }
    
    return config

CONFIG = load_config()

# 常用城市代码（示例）
CITY_CODES = {
    # 中国城市
    "beijing": "101010100",
    "shanghai": "101020100",
    "guangzhou": "101280101",
    "shenzhen": "101280601",
    "hangzhou": "101210101",
    "chengdu": "101270101",
    "wuhan": "101200101",
    "nanjing": "101190101",
    "xian": "101110101",
    "chongqing": "101040100",
    # 国际城市
    "newyork": "USNY0996",
    "london": "GBLO0483",
    "tokyo": "JAXX0085",
    "paris": "FRXX0076",
    "sydney": "ASXX0112",
}

@dataclass
class WeatherNow:
    """实时天气数据"""
    obs_time: str
    temp: int
    feels_like: int
    text: str
    icon: str
    wind_speed: int
    wind_scale: str
    wind_dir: str
    humidity: int
    precip: float
    pressure: int
    vis: int
    cloud: int
    dew: int
    
    def format(self) -> str:
        """格式化显示"""
        return f"""
🌤️ 实时天气 ({self.obs_time})
🌡️ 温度: {self.temp}°C (体感: {self.feels_like}°C)
🌬️ 风力: {self.wind_scale}级 ({self.wind_speed}km/h) {self.wind_dir}
💧 湿度: {self.humidity}%
🌧️ 降水: {self.precip}mm
📊 气压: {self.pressure}hPa
👁️ 能见度: {self.vis}公里
☁️ 云量: {self.cloud}%
🌡️ 露点: {self.dew}°C
"""

@dataclass
class DailyForecast:
    """每日预报"""
    fx_date: str
    sunrise: str
    sunset: str
    temp_max: int
    temp_min: int
    text_day: str
    text_night: str
    icon_day: str
    icon_night: str
    wind_scale_day: str
    wind_dir_day: str
    precip: float
    humidity: int
    uv_index: str
    cloud: int
    
    def format(self) -> str:
        """格式化显示"""
        weekday = self._get_weekday()
        return f"""
{weekday} ({self.fx_date})
🌅 日出: {self.sunrise} | 🌇 日落: {self.sunset}
🌡️ 温度: {self.temp_min}°C ~ {self.temp_max}°C
☀️ 白天: {self.text_day}
🌙 夜间: {self.text_night}
🌬️ 风力: {self.wind_scale_day}级 {self.wind_dir_day}
💧 湿度: {self.humidity}%
🌧️ 降水: {self.precip}mm
☀️ 紫外线: {self.uv_index}级
☁️ 云量: {self.cloud}%
"""
    
    def _get_weekday(self) -> str:
        """获取星期几"""
        date_obj = datetime.strptime(self.fx_date, "%Y-%m-%d")
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return weekdays[date_obj.weekday()]

@dataclass
class LifeIndex:
    """生活指数"""
    date: str
    type: str
    name: str
    level: str
    category: str
    text: str
    
    def format(self) -> str:
        """格式化显示"""
        emoji = self._get_emoji()
        return f"{emoji} {self.name}: {self.level} - {self.text}"
    
    def _get_emoji(self) -> str:
        """获取对应的emoji"""
        emoji_map = {
            "穿衣": "👕", "洗车": "🚗", "运动": "🏃", "紫外线": "☀️",
            "感冒": "🤧", "空气污染": "😷", "钓鱼": "🎣", "旅游": "🧳",
            "舒适度": "😊", "晾晒": "👕", "交通": "🚦", "防晒": "🧴"
        }
        return emoji_map.get(self.name, "📊")

class QWeatherClient:
    """和风天气API客户端"""
    
    def __init__(self):
        # 验证配置
        if not CONFIG["kid"]:
            raise ValueError("QWEATHER_KID 未配置。请设置环境变量或检查配置")
        if not CONFIG["sub"]:
            raise ValueError("QWEATHER_SUB 未配置。请设置环境变量或检查配置")
        if not CONFIG["api_host"]:
            raise ValueError("QWEATHER_API_HOST 未配置。请设置环境变量或检查配置")
        
        self.kid = CONFIG["kid"]
        self.sub = CONFIG["sub"]
        self.api_host = CONFIG["api_host"]
        self.private_key = self._load_private_key()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "OpenClaw-QWeather/1.0"
        })
        
        # 创建缓存目录
        os.makedirs(CONFIG["cache_dir"], exist_ok=True)
    
    def _load_private_key(self):
        """加载私钥"""
        private_key_path = CONFIG["private_key_path"]
        
        if not private_key_path:
            raise ValueError("私钥路径未配置。请设置 QWEATHER_PRIVATE_KEY_PATH 环境变量")
        
        if not os.path.exists(private_key_path):
            raise FileNotFoundError(f"私钥文件不存在: {private_key_path}")
        
        with open(private_key_path, 'r') as f:
            private_key_pem = f.read()
        
        return serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
    
    def _generate_jwt(self) -> str:
        """生成JWT token"""
        current_time = int(time.time())
        payload = {
            "sub": self.sub,
            "iat": current_time,
            "exp": current_time + 3600
        }
        
        headers = {
            "alg": "EdDSA",
            "typ": "JWT",
            "kid": self.kid
        }
        
        return jwt.encode(
            payload,
            self.private_key,
            algorithm="EdDSA",
            headers=headers
        )
    
    def _get_cached_data(self, cache_key: str, ttl: int) -> Optional[Dict]:
        """获取缓存数据"""
        cache_file = os.path.join(CONFIG["cache_dir"], f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            mtime = os.path.getmtime(cache_file)
            if time.time() - mtime < ttl:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """保存到缓存"""
        cache_file = os.path.join(CONFIG["cache_dir"], f"{cache_key}.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送API请求"""
        # 生成JWT token
        token = self._generate_jwt()
        
        # 构建URL
        url = f"https://{self.api_host}{endpoint}"
        
        # 设置headers
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # 发送请求
        response = self.session.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def get_city_code(self, city_name: str) -> str:
        """获取城市代码"""
        city_name_lower = city_name.lower()
        
        # 首先检查已知城市
        if city_name_lower in CITY_CODES:
            return CITY_CODES[city_name_lower]
        
        # 如果是数字，直接返回
        if city_name.isdigit():
            return city_name
        
        # 默认返回北京
        return CITY_CODES["beijing"]
    
    def get_weather_now(self, city: str) -> WeatherNow:
        """获取实时天气"""
        cache_key = f"now_{city}"
        
        # 检查缓存
        cached = self._get_cached_data(cache_key, CONFIG["cache_ttl"]["now"])
        if cached:
            data = cached
        else:
            city_code = self.get_city_code(city)
            data = self._make_request("/v7/weather/now", {"location": city_code})
            self._save_to_cache(cache_key, data)
        
        now_data = data["now"]
        return WeatherNow(
            obs_time=now_data["obsTime"],
            temp=int(now_data["temp"]),
            feels_like=int(now_data["feelsLike"]),
            text=now_data["text"],
            icon=now_data["icon"],
            wind_speed=int(now_data["windSpeed"]),
            wind_scale=now_data["windScale"],
            wind_dir=now_data["windDir"],
            humidity=int(now_data["humidity"]),
            precip=float(now_data["precip"]),
            pressure=int(now_data["pressure"]),
            vis=int(now_data["vis"]),
            cloud=int(now_data["cloud"]),
            dew=int(now_data["dew"])
        )
    
    def get_weather_forecast(self, city: str, days: int = 3) -> List[DailyForecast]:
        """获取天气预报"""
        cache_key = f"forecast_{city}_{days}"
        
        # 检查缓存
        cached = self._get_cached_data(cache_key, CONFIG["cache_ttl"]["forecast"])
        if cached:
            data = cached
        else:
            city_code = self.get_city_code(city)
            endpoint = "/v7/weather/7d" if days > 3 else "/v7/weather/3d"
            data = self._make_request(endpoint, {"location": city_code})
            self._save_to_cache(cache_key, data)
        
        forecasts = []
        for daily_data in data["daily"][:days]:
            forecast = DailyForecast(
                fx_date=daily_data["fxDate"],
                sunrise=daily_data["sunrise"],
                sunset=daily_data["sunset"],
                temp_max=int(daily_data["tempMax"]),
                temp_min=int(daily_data["tempMin"]),
                text_day=daily_data["textDay"],
                text_night=daily_data["textNight"],
                icon_day=daily_data["iconDay"],
                icon_night=daily_data["iconNight"],
                wind_scale_day=daily_data["windScaleDay"],
                wind_dir_day=daily_data["windDirDay"],
                precip=float(daily_data["precip"]),
                humidity=int(daily_data["humidity"]),
                uv_index=daily_data["uvIndex"],
                cloud=int(daily_data["cloud"])
            )
            forecasts.append(forecast)
        
        return forecasts
    
    def get_life_indices(self, city: str, date: str = None) -> List[LifeIndex]:
        """获取生活指数"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        cache_key = f"indices_{city}_{date}"
        
        # 检查缓存
        cached = self._get_cached_data(cache_key, CONFIG["cache_ttl"]["indices"])
        if cached:
            data = cached
        else:
            city_code = self.get_city_code(city)
            data = self._make_request("/v7/indices/1d", {
                "location": city_code,
                "type": "0"  # 获取所有类型
            })
            self._save_to_cache(cache_key, data)
        
        indices = []
        for index_data in data["daily"]:
            index = LifeIndex(
                date=index_data["date"],
                type=index_data["type"],
                name=index_data["name"],
                level=index_data["level"],
                category=index_data["category"],
                text=index_data["text"]
            )
            indices.append(index)
        
        return indices
    
    def get_air_quality(self, city: str) -> Dict:
        """获取空气质量"""
        cache_key = f"air_{city}"
        
        # 检查缓存
        cached = self._get_cached_data(cache_key, CONFIG["cache_ttl"]["air"])
        if cached:
            return cached
        
        city_code = self.get_city_code(city)
        data = self._make_request("/v7/air/now", {"location": city_code})
        self._save_to_cache(cache_key, data)
        
        return data
    
    def get_dressing_advice(self, temp: int) -> str:
        """根据温度提供穿衣建议"""
        if temp >= 28:
            return "👕 短袖、短裤、裙子，注意防晒"
        elif temp >= 23:
            return "👕 短袖、薄外套，早晚可加衣"
        elif temp >= 18:
            return "👕 长袖、薄外套，舒适温度"
        elif temp >= 10:
            return "🧥 外套、长裤，注意保暖"
        elif temp >= 0:
            return "🧥 厚外套、毛衣，建议穿秋裤"
        else:
            return "🧥 羽绒服、厚毛衣，注意防寒保暖"
    
    def get_umbrella_advice(self, precip: float, text: str) -> str:
        """根据降水提供雨伞建议"""
        if precip > 5 or "雨" in text:
            return "🌂 需要带雨伞，可能有中到大雨"
        elif precip > 0.1 or "小雨" in text:
            return "🌂 建议带雨伞，可能有小雨"
        else:
            return "☀️ 不需要带雨伞"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="QWeather China - 中国气象局天气服务")
    parser.add_argument("command", choices=["now", "forecast", "indices", "air", "full"],
                       help="命令: now(实时天气), forecast(预报), indices(生活指数), air(空气质量), full(完整报告)")
    parser.add_argument("--city", default="beijing", help="城市名称或代码，默认: beijing")
    parser.add_argument("--days", type=int, default=3, help="预报天数，默认: 3")
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    
    args = parser.parse_args()
    
    # 创建客户端
    client = QWeatherClient()
    
    try:
        if args.command == "now":
            # 实时天气
            weather = client.get_weather_now(args.city)
            print(weather.format())
            
            # 穿衣建议
            dressing = client.get_dressing_advice(weather.temp)
            print(f"👕 穿衣建议: {dressing}")
            
            # 雨伞建议
            umbrella = client.get_umbrella_advice(weather.precip, weather.text)
            print(f"🌂 雨伞建议: {umbrella}")
            
        elif args.command == "forecast":
            # 天气预报
            forecasts = client.get_weather_forecast(args.city, args.days)
            print(f"📅 {args.city.capitalize()} {args.days}天天气预报")
            print("=" * 50)
            
            for forecast in forecasts:
                print(forecast.format())
                print("-" * 50)
            
        elif args.command == "indices":
            # 生活指数
            indices = client.get_life_indices(args.city)
            print(f"📊 {args.city.capitalize()} 今日生活指数")
            print("=" * 50)
            
            for index in indices[:10]:  # 显示前10个
                print(index.format())
            
        elif args.command == "air":
            # 空气质量
            air_data = client.get_air_quality(args.city)
            now = air_data["now"]
            print(f"🌫️ {args.city.capitalize()} 空气质量")
            print("=" * 50)
            print(f"更新时间: {air_data['updateTime']}")
            print(f"AQI: {now['aqi']} ({now['category']})")
            print(f"主要污染物: {now['primary']}")
            print(f"PM2.5: {now['pm2p5']} μg/m³")
            print(f"PM10: {now['pm10']} μg/m³")
            print(f"二氧化硫: {now['so2']} μg/m³")
            print(f"二氧化氮: {now['no2']} μg/m³")
            print(f"臭氧: {now['o3']} μg/m³")
            print(f"一氧化碳: {now['co']} mg/m³")
            
        elif args.command == "full":
            # 完整报告
            print(f"📋 {args.city.capitalize()} 天气完整报告")
            print("=" * 60)
            
            # 实时天气
            weather = client.get_weather_now(args.city)
            print("🌤️ 实时天气")
            print(weather.format())
            
            # 穿衣和雨伞建议
            dressing = client.get_dressing_advice(weather.temp)
            umbrella = client.get_umbrella_advice(weather.precip, weather.text)
            print(f"👕 穿衣建议: {dressing}")
            print(f"🌂 雨伞建议: {umbrella}")
            print()
            
            # 3天预报
            print("📅 3天天气预报")
            print("-" * 50)
            forecasts = client.get_weather_forecast(args.city, 3)
            for forecast in forecasts:
                print(forecast.format())
            
            # 生活指数
            print("📊 今日生活指数")
            print("-" * 50)
            indices = client.get_life_indices(args.city)
            for index in indices[:8]:  # 显示前8个重要指数
                print(index.format())
            
            # 空气质量
            print("🌫️ 空气质量")
            print("-" * 50)
            try:
                air_data = client.get_air_quality(args.city)
                now = air_data["now"]
                print(f"AQI: {now['aqi']} ({now['category']})")
                print(f"主要污染物: {now['primary']}")
                print(f"PM2.5: {now['pm2p5']} μg/m³")
            except Exception as e:
                print(f"空气质量数据暂时不可用: {e}")
            
            print()
            print("=" * 60)
            print("数据来源: 中国气象局 · 和风天气")
            print(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("请检查网络连接或API配置")

if __name__ == "__main__":
    main()