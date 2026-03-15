"""
文档搜索器
在 D:\OpenClawDocs\ 中搜索相关文档
"""

import os
from pathlib import Path
from datetime import datetime


def search_documents(query: str, base_dir: str = "D:\\OpenClawDocs", limit: int = 10) -> list:
    """
    搜索文档
    
    :param query: 搜索关键词
    :param base_dir: 基础目录
    :param limit: 返回数量限制
    :return: 匹配的文档列表
    """
    results = []
    query_lower = query.lower()
    
    # 遍历目录
    for root, dirs, files in os.walk(base_dir):
        # 跳过 temp 目录的子目录（避免太深）
        if root.count('\\temp') > 1:
            continue
        
        for file in files:
            if file.endswith(('.md', '.docx', '.txt')):
                filepath = os.path.join(root, file)
                
                # 检查文件名
                score = 0
                match_reasons = []
                
                if query_lower in file.lower():
                    score += 50
                    match_reasons.append("文件名匹配")
                
                # 检查路径
                if query_lower in root.lower():
                    score += 30
                    match_reasons.append("路径匹配")
                
                # 检查文件内容（只读前 10KB，避免大文件）
                try:
                    if file.endswith('.md') or file.endswith('.txt'):
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(10000)  # 只读前 10KB
                            if query_lower in content.lower():
                                score += 20
                                match_reasons.append("内容匹配")
                                # 提取包含关键词的上下文
                                idx = content.lower().find(query_lower)
                                if idx >= 0:
                                    start = max(0, idx - 50)
                                    end = min(len(content), idx + 100)
                                    context = content[start:end].replace('\n', ' ').strip()
                                    match_reasons.append(f"上下文：...{context}...")
                except Exception as e:
                    pass  # 跳过无法读取的文件
                
                if score > 0:
                    # 获取文件信息
                    stat = os.stat(filepath)
                    results.append({
                        "path": filepath,
                        "filename": file,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "score": score,
                        "reasons": match_reasons
                    })
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:limit]


def find_related_documents(meeting_topic: str, base_dir: str = "D:\\OpenClawDocs") -> list:
    """
    根据会议主题查找相关文档
    
    :param meeting_topic: 会议主题
    :param base_dir: 基础目录
    :return: 相关文档列表
    """
    # 提取关键词
    keywords = []
    
    # 常见主题关键词
    topic_keywords = {
        "人员密集度": ["人员密集度", "人数统计", "人流监控"],
        "火灾监控": ["火灾", "火情", "烟雾"],
        "AI 视觉": ["AI 视觉", "视觉分析", "图像识别"],
        "销售": ["销售", "客户", "报价"],
        "项目": ["项目", "进展", "里程碑"],
        "周会": ["周会", "周报", "本周"],
    }
    
    for topic, kws in topic_keywords.items():
        if topic in meeting_topic:
            keywords.extend(kws)
            break
    
    if not keywords:
        keywords = [meeting_topic]
    
    # 搜索
    all_results = []
    for kw in keywords:
        results = search_documents(kw, base_dir, limit=5)
        all_results.extend(results)
    
    # 去重（按路径）
    seen = set()
    unique_results = []
    for r in all_results:
        if r["path"] not in seen:
            seen.add(r["path"])
            unique_results.append(r)
    
    # 按分数排序
    unique_results.sort(key=lambda x: x["score"], reverse=True)
    
    return unique_results[:10]


# 测试
if __name__ == "__main__":
    # 测试搜索
    query = "人员密集度"
    print(f"搜索：{query}\n")
    
    results = search_documents(query, "D:\\OpenClawDocs", limit=5)
    
    if results:
        print(f"找到 {len(results)} 个相关文档：\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['filename']}")
            print(f"   路径：{r['path']}")
            print(f"   修改时间：{r['modified']}")
            print(f"   匹配原因：{', '.join(r['reasons'])}")
            print()
    else:
        print("未找到相关文档")
