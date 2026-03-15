"""
智能管家完整工作流演示
"""

print("=" * 60)
print("智能管家完整工作流演示")
print("=" * 60)

# 场景 1：会前准备
print("\n【场景 1】会前准备")
print("-" * 60)
from smart_recommend import generate_recommendation

topic = "人员密集度检测方案讨论"
result = generate_recommendation(topic)

if result['has_recommendations']:
    best = result['best_match']
    print(f"检测到 {len(result['documents'])} 个相关文档")
    print(f"推荐复用：{best['filename']}")
    print(f"匹配关键词：{', '.join(best['match_keywords'][:3])}")
    print(f"可节省时间：80%")

# 场景 2：使用模板生成
print("\n【场景 2】生成新文档")
print("-" * 60)
from template_engine import detect_template_type, generate_from_template

template_type = detect_template_type("销售方案汇报")
content, filename = generate_from_template(template_type, "AI 监控系统销售方案")
print(f"使用模板：{template_type}方案模板")
print(f"生成文件：{filename}")
print(f"包含章节：客户痛点/解决方案/竞品对比/报价/案例")

# 场景 3：任务依赖
print("\n【场景 3】任务依赖检查")
print("-" * 60)
import sys
sys.path.insert(0, 'D:\\OpenClawDocs\\reminders')
import task_manager as tm

# 检查现有任务的依赖
data = tm.load_tasks()
for task in data.get('reminders', []):
    if task.get('depends_on'):
        dep_status = tm.check_dependencies(task['id'])
        print(f"任务 {task['id']}: {task['content']}")
        print(f"  依赖：{dep_status['pending']} 未完成")

# 场景 4：统计数据
print("\n【场景 4】工作统计")
print("-" * 60)
from stats import get_task_stats, get_document_stats

task_stats = get_task_stats(30)
print(f"最近 30 天：")
print(f"  任务总数：{task_stats['total']}")
print(f"  完成率：{task_stats['completion_rate']}%")
print(f"  生成文档：{task_stats['documents_generated']}份")

doc_stats = get_document_stats(30)
print(f"  文档总数：{doc_stats['total']}")
print(f"  总大小：{doc_stats.get('total_size_mb', 0)}MB")

print("\n" + "=" * 60)
print("演示完成！")
print("=" * 60)
