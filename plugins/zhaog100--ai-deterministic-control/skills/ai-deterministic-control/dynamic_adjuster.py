#!/usr/bin/env python3
"""动态温度调整模块"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from statistics import mean


class DynamicAdjuster:
    """动态温度调整器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "adjustment_rules.json"
        self.rules = self._load_rules()
        self.history_file = Path(__file__).parent / "quality_history.json"
        self.quality_history = self._load_history()
    
    def _load_rules(self) -> Dict:
        """加载调整规则"""
        if not self.config_path.exists():
            # 默认规则
            default_rules = {
                "task_types": {
                    "code": {
                        "keywords": ["函数", "代码", "实现", "function", "code", "implement"],
                        "recommended_temp": 0.0,
                        "description": "代码生成（高确定性）"
                    },
                    "config": {
                        "keywords": ["配置", "设置", "config", "setting"],
                        "recommended_temp": 0.1,
                        "description": "配置文件生成"
                    },
                    "qa": {
                        "keywords": ["问题", "回答", "question", "answer", "为什么"],
                        "recommended_temp": 0.5,
                        "description": "问答对话"
                    },
                    "creative": {
                        "keywords": ["创作", "写", "故事", "creative", "write", "story"],
                        "recommended_temp": 0.8,
                        "description": "创意写作"
                    },
                    "brainstorm": {
                        "keywords": ["头脑风暴", "想法", "建议", "brainstorm", "idea", "suggest"],
                        "recommended_temp": 1.2,
                        "description": "头脑风暴（高创造性）"
                    }
                },
                "quality_thresholds": {
                    "excellent": {
                        "min_similarity": 95.0,
                        "action": "maintain",
                        "description": "质量优秀，保持当前温度"
                    },
                    "good": {
                        "min_similarity": 85.0,
                        "action": "maintain",
                        "description": "质量良好，保持当前温度"
                    },
                    "acceptable": {
                        "min_similarity": 70.0,
                        "action": "decrease",
                        "adjustment": -0.1,
                        "description": "质量一般，建议降低温度"
                    },
                    "poor": {
                        "min_similarity": 0,
                        "action": "decrease",
                        "adjustment": -0.2,
                        "description": "质量较差，强烈建议降低温度"
                    }
                },
                "adjustment_limits": {
                    "min_temp": 0.0,
                    "max_temp": 2.0,
                    "max_adjustment": 0.3
                }
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_rules, f, indent=2, ensure_ascii=False)
            
            return default_rules
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_history(self) -> List[Dict]:
        """加载质量历史"""
        if not self.history_file.exists():
            return []
        
        with open(self.history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("records", [])
    
    def _save_history(self):
        """保存质量历史"""
        data = {"records": self.quality_history[-100:]}  # 保留最近100条
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def detect_task_type(self, prompt: str) -> Dict:
        """检测任务类型
        
        Args:
            prompt: 输入提示词
        
        Returns:
            任务类型信息
        """
        prompt_lower = prompt.lower()
        
        for task_type, config in self.rules["task_types"].items():
            for keyword in config["keywords"]:
                if keyword in prompt_lower:
                    return {
                        "type": task_type,
                        "recommended_temp": config["recommended_temp"],
                        "description": config["description"],
                        "matched_keyword": keyword
                    }
        
        # 默认类型
        return {
            "type": "general",
            "recommended_temp": 0.5,
            "description": "通用任务",
            "matched_keyword": None
        }
    
    def analyze_quality_trend(self, recent_count: int = 10) -> Dict:
        """分析质量趋势
        
        Args:
            recent_count: 分析最近N条记录
        
        Returns:
            质量趋势分析
        """
        if not self.quality_history:
            return {
                "status": "no_data",
                "message": "暂无历史数据",
                "recommendation": "继续收集数据"
            }
        
        recent_records = self.quality_history[-recent_count:]
        
        if not recent_records:
            return {
                "status": "no_data",
                "message": "暂无历史数据",
                "recommendation": "继续收集数据"
            }
        
        similarities = [r["similarity"] for r in recent_records if "similarity" in r]
        
        if not similarities:
            return {
                "status": "no_data",
                "message": "历史数据缺少相似度信息",
                "recommendation": "继续收集数据"
            }
        
        avg_similarity = mean(similarities)
        min_similarity = min(similarities)
        max_similarity = max(similarities)
        
        # 确定质量等级
        quality_level = None
        for level, config in self.rules["quality_thresholds"].items():
            if avg_similarity >= config["min_similarity"]:
                quality_level = level
                break
        
        return {
            "status": "success",
            "average_similarity": round(avg_similarity, 2),
            "min_similarity": round(min_similarity, 2),
            "max_similarity": round(max_similarity, 2),
            "quality_level": quality_level,
            "record_count": len(similarities),
            "recommendation": self._get_quality_recommendation(avg_similarity)
        }
    
    def _get_quality_recommendation(self, avg_similarity: float) -> str:
        """获取质量建议"""
        for level, config in self.rules["quality_thresholds"].items():
            if avg_similarity >= config["min_similarity"]:
                return config["description"]
        
        return "需要提升质量"
    
    def calculate_dynamic_temperature(
        self,
        prompt: str,
        current_temp: float = None,
        consider_history: bool = True
    ) -> Dict:
        """计算动态温度
        
        Args:
            prompt: 输入提示词
            current_temp: 当前温度（None则使用推荐值）
            consider_history: 是否考虑历史质量
        
        Returns:
            动态温度调整结果
        """
        # 检测任务类型
        task_info = self.detect_task_type(prompt)
        base_temp = task_info["recommended_temp"]
        
        # 如果提供了当前温度，以当前温度为基础
        if current_temp is not None:
            base_temp = current_temp
        
        final_temp = base_temp
        adjustments = []
        
        # 考虑历史质量
        if consider_history and self.quality_history:
            quality_trend = self.analyze_quality_trend()
            
            if quality_trend["status"] == "success":
                quality_level = quality_trend.get("quality_level")
                
                if quality_level and quality_level in self.rules["quality_thresholds"]:
                    config = self.rules["quality_thresholds"][quality_level]
                    
                    if config["action"] == "decrease" and "adjustment" in config:
                        adjustment = config["adjustment"]
                        final_temp = max(
                            self.rules["adjustment_limits"]["min_temp"],
                            base_temp + adjustment
                        )
                        adjustments.append({
                            "reason": f"历史质量: {quality_level}",
                            "adjustment": adjustment,
                            "from": base_temp,
                            "to": final_temp
                        })
        
        # 确保温度在范围内
        final_temp = max(
            self.rules["adjustment_limits"]["min_temp"],
            min(self.rules["adjustment_limits"]["max_temp"], final_temp)
        )
        
        return {
            "recommended_temperature": round(final_temp, 2),
            "task_type": task_info["type"],
            "task_description": task_info["description"],
            "base_temperature": base_temp,
            "adjustments": adjustments,
            "reason": self._generate_reason(task_info, adjustments)
        }
    
    def _generate_reason(self, task_info: Dict, adjustments: List[Dict]) -> str:
        """生成调整原因说明"""
        reasons = [f"任务类型: {task_info['description']}"]
        
        if adjustments:
            for adj in adjustments:
                reasons.append(f"{adj['reason']} (调整: {adj['adjustment']:+.2f})")
        
        return " | ".join(reasons)
    
    def record_quality(self, prompt: str, similarity: float, temperature: float):
        """记录质量数据
        
        Args:
            prompt: 提示词
            similarity: 相似度
            temperature: 使用的温度
        """
        record = {
            "prompt": prompt[:100],
            "similarity": similarity,
            "temperature": temperature,
            "timestamp": datetime.now().isoformat()
        }
        
        self.quality_history.append(record)
        self._save_history()
    
    def get_adjustment_stats(self) -> Dict:
        """获取调整统计"""
        if not self.quality_history:
            return {
                "total_records": 0,
                "message": "暂无历史数据"
            }
        
        temps = [r["temperature"] for r in self.quality_history if "temperature" in r]
        similarities = [r["similarity"] for r in self.quality_history if "similarity" in r]
        
        return {
            "total_records": len(self.quality_history),
            "average_temperature": round(mean(temps), 2) if temps else 0,
            "average_similarity": round(mean(similarities), 2) if similarities else 0,
            "temperature_range": [round(min(temps), 2), round(max(temps), 2)] if temps else [0, 0],
            "similarity_range": [round(min(similarities), 2), round(max(similarities), 2)] if similarities else [0, 0]
        }


# ========== CLI命令 ==========

def adjust_command(prompt: str, current_temp: float = None):
    """动态温度调整命令"""
    adjuster = DynamicAdjuster()
    
    result = adjuster.calculate_dynamic_temperature(prompt, current_temp)
    
    print(f"\n🎯 动态温度推荐\n")
    print(f"推荐温度: {result['recommended_temperature']}")
    print(f"任务类型: {result['task_description']}")
    print(f"基础温度: {result['base_temperature']}")
    
    if result['adjustments']:
        print(f"\n调整历史:")
        for adj in result['adjustments']:
            print(f"  - {adj['reason']}: {adj['from']:.2f} → {adj['to']:.2f}")
    
    print(f"\n原因: {result['reason']}\n")
    
    return result
