"""测试归档功能"""
from doc_archive import archive_document, list_projects

# 查看当前项目
print('=== 当前项目 ===')
projects = list_projects()
for p in projects:
    print(f"  {p['name']}")

# 归档今天的方案（v2 版本）
print('\n=== 归档文档 ===')
result = archive_document(
    source_path='D:/OpenClawDocs/temp/20260304_人员密集度检测方案_v2.md',
    project_name='人员密集度检测',
    mark_as_final=True
)

if result['success']:
    print(f"✅ {result['action']}成功")
    print(f"   源文件：{result['source']}")
    print(f"   目标：{result['target']}")
    print(f"   项目：{result['project']}")
else:
    print(f"❌ 失败：{result.get('error')}")
