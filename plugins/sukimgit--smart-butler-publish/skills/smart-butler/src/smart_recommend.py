"""
智能推荐引擎
根据会议主题推荐历史文档
"""

import os
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher


# 项目关键词映射
PROJECT_KEYWORDS = {
    "人员密集度": ["人员密集度", "人数统计", "人流监控", "人流密度"],
    "火灾监控": ["火灾", "火情", "烟雾", "消防"],
    "AI 视觉": ["AI 视觉", "视觉分析", "图像识别", "视频分析"],
    "销售": ["销售", "客户", "报价", "商务"],
    "项目": ["项目", "进展", "里程碑", "验收"],
    "周会": ["周会", "周报", "例会", "周例会"],
}


def extract_keywords(meeting_topic: str) -> list:
    """
    从会议主题提取关键词
    
    :param meeting_topic: 会议主题
    :return: 关键词列表
    """
    keywords = []
    
    for project, kws in PROJECT_KEYWORDS.items():
        if project in meeting_topic:
            keywords.extend(kws)
            keywords.append(project)
    
    # 如果没有匹配到，使用原始主题
    if not keywords:
        keywords = [meeting_topic]
    
    return list(set(keywords))


def similarity_score(str1: str, str2: str) -> float:
    """
    计算两个字符串的相似度
    
    :param str1: 字符串 1
    :param str2: 字符串 2
    :return: 相似度 0-1
    """
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def find_related_documents(
    meeting_topic: str,
    base_dir: str = "D:\\OpenClawDocs",
    limit: int = 5,
    days_limit: int = None
) -> list:
    """
    查找相关文档
    
    :param meeting_topic: 会议主题
    :param base_dir: 基础目录
    :param limit: 返回数量限制
    :param days_limit: 只查找多少天内的文档（None=不限制）
    :return: 相关文档列表
    """
    keywords = extract_keywords(meeting_topic)
    results = []
    seen_paths = set()
    
    # 遍历目录
    for root, dirs, files in os.walk(base_dir):
        # 跳过 temp 的子目录
        if root.count('\\temp') > 1:
            continue
        
        for file in files:
            if not file.endswith(('.md', '.docx')):
                continue
            
            filepath = os.path.join(root, file)
            
            # 检查时间限制
            if days_limit:
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                days_old = (datetime.now() - mtime).days
                if days_old > days_limit:
                    continue
            
            # 计算匹配分数
            score = 0
            match_keywords = []
            
            # 文件名匹配
            for kw in keywords:
                if kw in file:
                    score += 30
                    match_keywords.append(kw)
            
            # 路径匹配（项目目录）
            for kw in keywords:
                if kw in root:
                    score += 20
                    match_keywords.append(kw)
            
            # 内容匹配（前 5KB）
            try:
                if file.endswith('.md'):
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(5000)
                        for kw in keywords:
                            if kw in content:
                                score += 10
                                if kw not in match_keywords:
                                    match_keywords.append(kw)
            except:
                pass
            
            # 时间衰减（越近越重要）
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            days_old = (datetime.now() - mtime).days
            time_boost = max(0, 20 - days_old)  # 20 天内有加分
            score += time_boost
            
            if score > 0 and filepath not in seen_paths:
                seen_paths.add(filepath)
                
                # 获取文件信息
                stat = os.stat(filepath)
                results.append({
                    "path": filepath,
                    "filename": file,
                    "size": stat.st_size,
                    "modified": mtime.strftime("%Y-%m-%d %H:%M"),
                    "days_old": days_old,
                    "score": score,
                    "match_keywords": list(set(match_keywords)),
                    "category": _get_category(filepath)
                })
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:limit]


def _get_category(filepath: str) -> str:
    """
    获取文档类别
    
    :param filepath: 文件路径
    :return: 类别
    """
    if "\\projects\\" in filepath:
        return "正式文档"
    elif "\\meetings\\" in filepath:
        return "会议资料"
    elif "\\temp\\" in filepath:
        return "草稿"
    else:
        return "其他"


def generate_recommendation(meeting_topic: str) -> dict:
    """
    生成推荐结果
    
    :param meeting_topic: 会议主题
    :return: 推荐结果
    """
    # 查找相关文档
    results = find_related_documents(meeting_topic, limit=5)
    
    if not results:
        return {
            "has_recommendations": False,
            "message": "未找到相关历史文档",
            "documents": []
        }
    
    # 分类整理
    formal_docs = [r for r in results if r["category"] == "正式文档"]
    drafts = [r for r in results if r["category"] == "草稿"]
    meeting_docs = [r for r in results if r["category"] == "会议资料"]
    
    # 生成建议
    best_match = results[0]
    suggestion = f"建议基于《{best_match['filename']}》修改，可节省 80% 时间"
    
    return {
        "has_recommendations": True,
        "message": f"检测到 {len(results)} 个相关文档",
        "best_match": best_match,
        "suggestion": suggestion,
        "documents": results,
        "by_category": {
            "formal": formal_docs,
            "drafts": drafts,
            "meetings": meeting_docs
        }
    }


def format_recommendation_for_message(rec_result: dict) -> str:
    """
    格式化推荐结果为消息
    
    :param rec_result: 推荐结果
    :return: 格式化的消息
    """
    if not rec_result["has_recommendations"]:
        return "📋 未找到相关历史文档，将生成全新方案"
    
    msg = f"📋 {rec_result['message']}:\n\n"
    
    # 最佳匹配
    best = rec_result["best_match"]
    msg += f"💡 **推荐复用**：{best['filename']}\n"
    msg += f"   📁 {best['path']}\n"
    msg += f"   ⏰ {best['modified']}（{best['days_old']}天前）\n"
    msg += f"   🏷️ 匹配：{', '.join(best['match_keywords'][:3])}\n\n"
    
    # 其他文档
    if len(rec_result["documents"]) > 1:
        msg += f"📂 **其他相关**：\n"
        for i, doc in enumerate(rec_result["documents"][1:4], 1):
            msg += f"   {i}. {doc['filename']}（{doc['category']}）\n"
    
    msg += f"\n{rec_result['suggestion']}"
    msg += f"\n\n要复用这个文档吗？我帮你复制一份并修改。"
    
    return msg


# 测试
if __name__ == "__main__":
    # 测试推荐
    test_topics = [
        "人员密集度检测讨论会",
        "销售方案汇报",
        "项目周会"
    ]
    
    for topic in test_topics:
        print(f"\n{'='*60}")
        print(f"会议主题：{topic}")
        print(f"{'='*60}")
        
        result = generate_recommendation(topic)
        if result["has_recommendations"]:
            print(f"推荐：{result['best_match']['filename']}")
            print(f"分数：{result['best_match']['score']}")
            print(f"匹配关键词：{result['best_match']['match_keywords']}")
        else:
            print("无推荐文档")
