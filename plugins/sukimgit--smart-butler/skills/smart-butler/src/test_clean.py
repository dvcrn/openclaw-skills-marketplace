from doc_archive import clean_temp

print("=== Temp 清理预览（7 天以上文件）===\n")
result = clean_temp(days_old=7, dry_run=True)

if result['deleted_files']:
    print(f"可清理 {len(result['deleted_files'])} 个文件：")
    for f in result['deleted_files']:
        print(f"  - {f['path']}")
        print(f"    {f['days_old']} 天前，{f['size']} bytes")
else:
    print("✅ 没有需要清理的文件（所有文件都在 7 天内）")

print(f"\nDry run: {result['dry_run']}")
print(f"Threshold: {result['days_old_threshold']} days")
