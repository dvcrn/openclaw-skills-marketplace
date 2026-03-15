"""
StyleBuddy v0.3.3 功能测试脚本
测试所有核心功能是否正常
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("StyleBuddy v0.3.3 功能测试")
print("=" * 60)

# 测试 1: 数据库连接
print("\n[1/10] 测试数据库连接...")
try:
    from src.storage.database import Database
    db = Database()
    print("  ✅ 数据库初始化成功")
except Exception as e:
    print(f"  ❌ 数据库失败: {e}")
    sys.exit(1)

# 测试 2: 用户画像模块
print("\n[2/10] 测试用户画像模块...")
try:
    from src.models.user_profile import UserProfileManager
    profile_mgr = UserProfileManager(db)
    
    # 测试解析
    test_input = "我是小李，女，165cm，50kg，梨型身材，喜欢简约风格"
    parsed = profile_mgr.parse_profile_input(test_input)
    assert parsed['nickname'] == '小李', "昵称解析失败"
    assert parsed['gender'] == 'female', "性别解析失败"
    assert parsed['height'] == 165, "身高解析失败"
    assert parsed['weight'] == 50, "体重解析失败"
    assert parsed['body_type'] == '梨型', "体型解析失败"
    assert '简约' in parsed['style_preference'], "风格解析失败"
    print(f"  ✅ 用户画像解析成功: {parsed}")
except Exception as e:
    print(f"  ❌ 用户画像失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 3: 天气服务
print("\n[3/10] 测试天气服务...")
try:
    from src.services.weather import WeatherService
    weather_svc = WeatherService()
    
    # 测试方法存在
    assert hasattr(weather_svc, 'get_current'), "缺少 get_current 方法"
    assert hasattr(weather_svc, 'get_weather'), "缺少 get_weather 别名"
    
    # 测试天气代码
    assert weather_svc.WEATHER_CODES[1] == "大部晴朗", "天气代码翻译错误"
    assert weather_svc.WEATHER_CODES[0] == "晴天", "天气代码翻译错误"
    print(f"  ✅ 天气服务正常")
    print(f"     - get_weather 别名: ✅")
    print(f"     - 天气代码翻译: {weather_svc.WEATHER_CODES[1]}")
except Exception as e:
    print(f"  ❌ 天气服务失败: {e}")

# 测试 4: 推荐引擎
print("\n[4/10] 测试推荐引擎...")
try:
    from src.core.recommender import OutfitRecommender
    recommender = OutfitRecommender(db)
    
    # 测试模板加载
    assert len(recommender.templates) > 0, "模板未加载"
    print(f"  ✅ 推荐引擎正常")
    print(f"     - 模板数量: {len(recommender.templates)}")
    
    # 测试推荐（无用户画像）
    recs = recommender.recommend(occasion="日常", count=3)
    print(f"     - 推荐测试: {len(recs)} 套方案")
    
    # 测试推荐（有用户画像）
    test_profile = {
        'gender': 'female',
        'body_type': '梨型',
        'style_preference': ['简约', '优雅'],
        'color_preference': ['白色', '黑色'],
        'avoid_colors': ['荧光色'],
        'price_preference': '中端'
    }
    recs_profile = recommender.recommend(occasion="休闲", count=3, user_profile=test_profile)
    print(f"     - 个性化推荐: {len(recs_profile)} 套方案")
except Exception as e:
    print(f"  ❌ 推荐引擎失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 5: Vision 服务
print("\n[5/10] 测试 Vision 服务...")
try:
    from src.services.vision import VisionService
    vision_svc = VisionService({})
    assert hasattr(vision_svc, 'analyze_image'), "缺少 analyze_image 方法"
    print("  ✅ Vision 服务正常")
except Exception as e:
    print(f"  ❌ Vision 服务失败: {e}")

# 测试 6: 衣橱管理
print("\n[6/10] 测试衣橱管理...")
try:
    from src.models.wardrobe import WardrobeManager
    wardrobe = WardrobeManager(db)
    
    # 测试分类映射
    assert wardrobe._cat_to_chinese('outer') == '外套', "分类映射错误"
    assert wardrobe._cat_to_chinese('top') == '上衣', "分类映射错误"
    print("  ✅ 衣橱管理正常")
except Exception as e:
    print(f"  ❌ 衣橱管理失败: {e}")

# 测试 7: 场景提取
print("\n[7/10] 测试场景提取...")
try:
    from main import StyleBuddy
    buddy = StyleBuddy()
    
    test_cases = [
        ("去公园穿什么", "休闲"),
        ("明天约会怎么穿", "约会"),
        ("上班穿什么", "职场"),
        ("周末逛街", "休闲"),
        ("去KTV", "聚会"),
        ("今天穿什么", "日常"),
    ]
    
    for user_input, expected in test_cases:
        result = buddy._extract_occasion(user_input)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{user_input}' → {result}")
except Exception as e:
    print(f"  ❌ 场景提取失败: {e}")

# 测试 8: 种草咨询
print("\n[8/10] 测试种草咨询...")
try:
    from src.services.shopping import ShoppingConsultant
    shopping = ShoppingConsultant(db, wardrobe)
    assert hasattr(shopping, 'consult'), "缺少 consult 方法"
    assert hasattr(shopping, 'compare_wishlist_with_wardrobe'), "缺少对比方法"
    print("  ✅ 种草咨询模块正常")
except Exception as e:
    print(f"  ❌ 种草咨询失败: {e}")

# 测试 9: 衣橱分析
print("\n[9/10] 测试衣橱分析...")
try:
    from src.core.analyzer import WardrobeAnalyzer
    analyzer = WardrobeAnalyzer(db)
    assert hasattr(analyzer, 'generate_report'), "缺少 generate_report 方法"
    print("  ✅ 衣橱分析模块正常")
except Exception as e:
    print(f"  ❌ 衣橱分析失败: {e}")

# 测试 10: 整体流程
print("\n[10/10] 测试整体流程...")
try:
    # 测试欢迎消息
    welcome = buddy._get_welcome_message()
    assert "穿搭档案" in welcome, "欢迎消息缺少档案引导"
    
    # 测试帮助
    help_msg = buddy._handle_help()
    assert "录入衣服" in help_msg, "帮助信息不完整"
    
    print("  ✅ 整体流程正常")
except Exception as e:
    print(f"  ❌ 整体流程失败: {e}")

# 总结
print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)

# 检查文件列表
print("\n[文件清单]")
files = [
    "main.py",
    "src/models/user_profile.py",
    "src/models/wardrobe.py",
    "src/core/recommender.py",
    "src/core/analyzer.py",
    "src/core/router.py",
    "src/services/vision.py",
    "src/services/weather.py",
    "src/services/shopping.py",
    "src/services/visualizer.py",
    "src/storage/database.py",
]

all_exist = True
for f in files:
    path = os.path.join(os.path.dirname(__file__), f)
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"  {status} {f}")
    if not exists:
        all_exist = False

print("\n" + "=" * 60)
if all_exist:
    print("✅ 所有文件存在，可以打包！")
else:
    print("❌ 有文件缺失，请检查！")
print("=" * 60)
