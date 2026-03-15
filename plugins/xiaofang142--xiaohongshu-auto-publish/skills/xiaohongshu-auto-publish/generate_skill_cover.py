#!/usr/bin/env python3
"""
生成技能封面图
"""

from PIL import Image, ImageDraw, ImageFont

width, height = 400, 400
img = Image.new('RGB', (width, height), (245, 235, 220))
draw = ImageDraw.Draw(img)

# 红色边框
draw.rectangle([(10, 10), (width-10, height-10)], outline=(139, 26, 26), width=3)

# 标题文字（简单用默认字体）
draw.text((width//2, 150), "📱", fill=(139, 26, 26), anchor="mm")
draw.text((width//2, 220), "小红书自动发布", fill=(0, 0, 0), anchor="mm")
draw.text((width//2, 260), "¥0.01/次", fill=(139, 26, 26), anchor="mm")

img.save("/Users/xiaofang/.openclaw/workspace-taizi/skills/xiaohongshu-auto-publish/assets/cover.png")
print("✅ 技能封面已生成")
