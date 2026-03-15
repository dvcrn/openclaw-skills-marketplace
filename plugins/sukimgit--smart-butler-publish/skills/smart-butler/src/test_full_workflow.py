"""
完整工作流测试
测试：创建 → 修改 → 归档 → 搜索
"""

import sys
sys.path.insert(0, 'D:\\OpenClawDocs\\smart-butler\\src')

from doc_generator import generate_scheme_content, save_doc
from doc_modifier import modify_document, save_version
from doc_archive import archive_document, list_projects, clean_temp
from doc_search import search_documents

print("=" * 60)
print("智能管家完整工作流测试")
print("=" * 60)

# Step 1: 生成新文档
print("\n[Step 1] 生成新方案文档...")
content = generate_scheme_content(
    title="火灾监控系统方案",
    background="火灾安全是物业管理的重中之重...",
    requirements="1. 实时火情监测\n2. 自动告警\n3. 视频联动",
    solution="基于 AI 视觉的烟雾和火焰识别算法...",
    plan="第一阶段：1 周\n第二阶段：4 周\n第三阶段：2 周",
    expected_results="1. 识别准确率>98%\n2. 告警响应<5 秒",
    risks="1. 误报问题\n2. 光线影响",
    budget="硬件：2W\n软件：3W\n实施：1W\n总计：6W",
    version="1.0"
)

filename = f"20260304_火灾监控系统方案_v1"
paths = save_doc(content, filename, "temp")
print(f"✅ 草稿已生成：{paths['md']}")

# Step 2: 修改文档
print("\n[Step 2] 修改文档（强调技术优势）...")
with open(paths['md'], 'r', encoding='utf-8') as f:
    original_content = f.read()

modified_content, topic, success = modify_document(original_content, "强调一下技术优势")
if success:
    new_path = save_version(modified_content, paths['md'])
    print(f"✅ 修改成功，新版本：{new_path}")
else:
    print(f"❌ 修改失败")
    new_path = paths['md']

# Step 3: 归档到正式目录
print("\n[Step 3] 归档到正式目录...")
result = archive_document(
    source_path=new_path,
    project_name="火灾监控系统",
    mark_as_final=True
)

if result['success']:
    print(f"✅ {result['action']}成功")
    print(f"   源文件：{result['source']}")
    print(f"   目标：{result['target']}")
else:
    print(f"❌ 归档失败：{result.get('error')}")

# Step 4: 搜索文档
print("\n[Step 4] 搜索历史文档...")
results = search_documents("火灾监控", "D:\\OpenClawDocs", limit=5)
print(f"找到 {len(results)} 个相关文档：")
for i, r in enumerate(results, 1):
    print(f"  {i}. {r['filename']}")
    print(f"     路径：{r['path']}")

# Step 5: 查看项目列表
print("\n[Step 5] 查看项目列表...")
projects = list_projects()
for p in projects:
    print(f"  📁 {p['name']} - {p['file_count']} 个文件")

# Step 6: temp 清理预览
print("\n[Step 6] Temp 清理预览...")
clean_result = clean_temp(days_old=7, dry_run=True)
if clean_result['deleted_files']:
    print(f"可清理 {len(clean_result['deleted_files'])} 个文件：")
    for f in clean_result['deleted_files']:
        print(f"  - {f['path']} ({f['days_old']} 天前)")
else:
    print("✅ 没有需要清理的文件")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
