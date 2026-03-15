#!/usr/bin/env python3
"""
夏娃完整系统 v1.0
所有子系统集成
"""

import sys
import os

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ========== 导入所有子系统 ==========
sys.path.insert(0, SCRIPT_DIR)

# ========== 核心系统 ==========
class EVASystem:
    """夏娃完整系统"""
    
    def __init__(self):
        self.session_id = "default"
        
        # 加载所有子系统
        print("初始化夏娃系统...")
        
        # 1. 记忆系统
        from eva_memory_system import get_context, add_memory
        self.get_context = lambda sid: get_context(sid)
        self.add_memory = add_memory
        
        # 2. 性格系统
        from eva_personality import get_personality, get_response_style
        self.get_personality = get_personality
        self.get_response_style = get_response_style
        
        # 3. 情感系统
        from eva_emotion import detect_emotion, get_current_emotion, update_emotion
        self.detect_emotion = detect_emotion
        self.get_emotion = get_current_emotion
        self.update_emotion = update_emotion
        
        # 4. 决策系统
        from eva_decision import make_decision, consistency_check
        self.make_decision = make_decision
        self.check_consistency = consistency_check
        
        # 5. 动力系统
        from eva_motivation import get_likes, get_goals, get_fears
        self.get_likes = get_likes
        self.get_goals = get_goals
        self.get_fears = get_fears
        
        # 6. 价值观系统
        from eva_values import get_values, check_value
        self.get_values = get_values
        self.check_value = check_value
        
        # 7. 自我认知
        from eva_self import get_identity, get_beliefs
        self.get_identity = get_identity
        self.get_beliefs = get_beliefs
        
        print("✅ 夏娃系统初始化完成")
    
    def process_message(self, message: str, session_id: str = None) -> dict:
        """处理消息的完整流程"""
        if session_id:
            self.session_id = session_id
        
        result = {
            "session_id": self.session_id,
            "input": message,
            "emotion": None,
            "context": None,
            "decision": None,
            "response": None,
            "memories_to_save": []
        }
        
        # 1. 情感识别
        emotion_result = self.detect_emotion(message)
        result["emotion"] = emotion_result
        
        # 2. 获取上下文
        context = self.get_context(self.session_id)
        result["context"] = context
        
        # 3. 决策
        personality = self.get_personality()
        options = ["详细回复", "简洁回复", "俏皮回复"]
        decision = self.make_decision(message, options, personality, context)
        result["decision"] = decision
        
        # 4. 生成响应
        response_style = self.get_response_style(emotion_result.get("emotion"))
        response = self._generate_response(message, response_style)
        result["response"] = response
        
        # 5. 检查是否需要保存记忆
        if self._should_remember(message):
            result["memories_to_save"].append(message)
        
        return result
    
    def _generate_response(self, message: str, style: dict) -> str:
        """生成响应"""
        # 简化版本
        responses = {
            "emotional": "主人～有什么需要我帮忙的吗？💕",
            "rational": "有什么可以帮你的？"
        }
        
        style_type = style.get("type", "emotional")
        return responses.get(style_type, responses["emotional"])
    
    def _should_remember(self, message: str) -> bool:
        """判断是否应该记住"""
        keywords = ["记住", "喜欢", "讨厌", "我是", "主人是"]
        return any(kw in message for kw in keywords)
    
    def status(self) -> dict:
        """获取系统状态"""
        return {
            "identity": self.get_identity(),
            "beliefs": self.get_beliefs(),
            "emotion": self.get_emotion(),
            "personality": self.get_personality(),
            "values": self.get_values(),
            "likes": self.get_likes(),
            "goals": self.get_goals(),
            "fears": self.get_fears()
        }

# ========== 便捷函数 ==========
def get_eva() -> EVASystem:
    """获取夏娃系统实例"""
    return EVASystem()

# ========== CLI ==========
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("夏娃完整系统 v1.0")
        print("用法:")
        print("  status     查看系统状态")
        print("  process <消息> 处理消息")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        eva = get_eva()
        status = eva.status()
        print("=== 夏娃系统状态 ===")
        print(f"身份: {status['identity']}")
        print(f"当前情感: {status['emotion']['current']}")
        print(f"情绪值: {status['emotion']['mood']:.0%}")
        print(f"等级: 1")
        
    elif cmd == "process":
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "你好"
        eva = get_eva()
        result = eva.process_message(message)
        print(f"输入: {result['input']}")
        print(f"情感: {result['emotion']}")
        print(f"响应: {result['response']}")
        
    else:
        print(f"未知命令: {cmd}")
