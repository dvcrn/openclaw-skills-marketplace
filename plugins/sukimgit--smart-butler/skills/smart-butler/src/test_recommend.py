"""测试智能推荐功能"""
from smart_recommend import generate_recommendation, format_recommendation_for_message

# 测试场景：明天有个火灾监控会议
topic = "火灾监控系统讨论会"
print(f"会议主题：{topic}\n")

result = generate_recommendation(topic)
msg = format_recommendation_for_message(result)
print(msg)
