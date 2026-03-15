#!/usr/bin/env python3
"""
记忆回顾与查漏补缺模块
功能：回顾当天聊天，发现遗漏，补充记忆
作者：米粒儿
版本：1.0.0
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from openai import OpenAI
except ImportError:
    print("⚠️ openai 未安装，请运行：pip install openai")
    sys.exit(1)


class MemoryReviewer:
    """记忆回顾器 - 查漏补缺"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
    
    def review_today_memory(self, today_memory: str, long_term_memory: str = None) -> dict:
        """
        回顾今天的记忆，找出遗漏
        
        Args:
            today_memory: 今天的记忆文件路径
            long_term_memory: 长期记忆文件路径（MEMORY.md）
        
        Returns:
            {
                "gaps": ["遗漏1", "遗漏2", ...],
                "important_events": ["事件1", "事件2", ...],
                "decisions": ["决策1", "决策2", ...],
                "lessons": ["教训1", "教训2", ...]
            }
        """
        
        # 读取今天的记忆
        with open(today_memory, 'r', encoding='utf-8') as f:
            today_content = f.read()
        
        # 读取长期记忆（如果存在）
        long_term_content = ""
        if long_term_memory and os.path.exists(long_term_memory):
            with open(long_term_memory, 'r', encoding='utf-8') as f:
                long_term_content = f.read()[:2000]  # 限制长度
        
        # 构建提示词
        prompt = f"""你是一个记忆审查助手。请仔细阅读今天的聊天记录，找出可能遗漏的重要内容。

今天的记忆：
{today_content}

长期记忆参考（MEMORY.md 前2000字符）：
{long_term_content}

请分析并返回 JSON 格式结果：
{{
    "gaps": ["遗漏的内容（需要补充到今天记忆的）"],
    "important_events": ["重要事件（值得记录到长期记忆的）"],
    "decisions": ["关键决策"],
    "lessons": ["学到的教训/洞察"]
}}

要求：
1. gaps：找出今天记忆中可能遗漏的内容（比如某个重要话题、用户偏好等）
2. important_events：识别今天发生的重要事件（系统更新、新功能、重要决定等）
3. decisions：记录今天的决策（比如选择了某个方案、放弃了某个想法等）
4. lessons：总结今天的教训或洞察（学到了什么、需要注意什么等）

只返回 JSON，不要其他内容。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是记忆审查助手，擅长发现遗漏和总结要点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 尝试解析 JSON
            result = json.loads(result_text)
            
            return result
            
        except Exception as e:
            print(f"❌ AI 分析失败：{e}")
            return {
                "gaps": [],
                "important_events": [],
                "decisions": [],
                "lessons": []
            }
    
    def generate_supplement(self, gaps: list) -> str:
        """
        生成补充内容（Markdown格式）
        
        Args:
            gaps: 遗漏内容列表
        
        Returns:
            Markdown 格式的补充内容
        """
        
        if not gaps:
            return ""
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        supplement = f"\n\n---\n\n## 查漏补缺（{now}）\n\n"
        
        for i, gap in enumerate(gaps, 1):
            supplement += f"**{i}.** {gap}\n\n"
        
        return supplement
    
    def update_memory_file(self, memory_file: str, supplement: str):
        """
        更新记忆文件（追加补充内容）
        
        Args:
            memory_file: 记忆文件路径
            supplement: 补充内容
        """
        
        if not supplement:
            return
        
        with open(memory_file, 'a', encoding='utf-8') as f:
            f.write(supplement)
        
        print(f"✅ 已补充 {len(supplement.split(chr(10)))} 行到 {memory_file}")
    
    def save_review_report(self, output_file: str, review_result: dict):
        """
        保存审查报告
        
        Args:
            output_file: 输出文件路径
            review_result: 审查结果
        """
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# 记忆审查报告

**审查时间**：{now}

## 📋 查漏补缺结果

### 遗漏内容（{len(review_result['gaps'])}项）
"""
        
        for i, gap in enumerate(review_result['gaps'], 1):
            report += f"{i}. {gap}\n"
        
        report += f"""
### 重要事件（{len(review_result['important_events'])}项）
"""
        
        for i, event in enumerate(review_result['important_events'], 1):
            report += f"{i}. {event}\n"
        
        report += f"""
### 关键决策（{len(review_result['decisions'])}项）
"""
        
        for i, decision in enumerate(review_result['decisions'], 1):
            report += f"{i}. {decision}\n"
        
        report += f"""
### 教训/洞察（{len(review_result['lessons'])}项）
"""
        
        for i, lesson in enumerate(review_result['lessons'], 1):
            report += f"{i}. {lesson}\n"
        
        report += "\n---\n\n*自动生成 by Session-Memory Enhanced v4.0*\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 审查报告已保存：{output_file}")


def main():
    parser = argparse.ArgumentParser(description='记忆回顾与查漏补缺')
    parser.add_argument('--today-memory', required=True, help='今天的记忆文件路径')
    parser.add_argument('--long-term-memory', help='长期记忆文件路径（MEMORY.md）')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--api-key', required=True, help='OpenAI API Key')
    
    args = parser.parse_args()
    
    # 创建审查器
    reviewer = MemoryReviewer(api_key=args.api_key)
    
    print(f"🔍 开始审查：{args.today_memory}")
    
    # 审查今天的记忆
    review_result = reviewer.review_today_memory(
        today_memory=args.today_memory,
        long_term_memory=args.long_term_memory
    )
    
    # 统计结果
    gaps_count = len(review_result['gaps'])
    events_count = len(review_result['important_events'])
    decisions_count = len(review_result['decisions'])
    lessons_count = len(review_result['lessons'])
    
    print(f"📊 审查结果：")
    print(f"   - 遗漏内容：{gaps_count} 项")
    print(f"   - 重要事件：{events_count} 项")
    print(f"   - 关键决策：{decisions_count} 项")
    print(f"   - 教训/洞察：{lessons_count} 项")
    
    # 如果有遗漏，补充到今天记忆
    if gaps_count > 0:
        supplement = reviewer.generate_supplement(review_result['gaps'])
        reviewer.update_memory_file(args.today_memory, supplement)
    
    # 保存审查报告
    if args.output:
        reviewer.save_review_report(args.output, review_result)
    
    print("✅ 记忆审查完成")


if __name__ == "__main__":
    main()
