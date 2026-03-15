#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文章收藏助手 - 增强版
自动提取文章内容并保存到飞书多维表格
"""

import json
import requests
import re
from datetime import datetime
from urllib.parse import urlparse
import subprocess

# 飞书应用配置（从环境变量读取）
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

APP_ID = os.getenv("FEISHU_APP_ID", "")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN", "")
TABLE_ID = os.getenv("FEISHU_TABLE_ID", "")


def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        raise Exception(f"获取 token 失败: {result}")


def detect_source(url):
    """自动识别链接来源"""
    domain = urlparse(url).netloc.lower()
    
    if "zhihu.com" in domain:
        return "知乎"
    elif "mp.weixin.qq.com" in domain or "weixin.qq.com" in domain:
        return "微信公众号"
    elif "toutiao.com" in domain or "jinri" in domain:
        return "今日头条"
    elif "xiaohongshu.com" in domain or "xhs" in domain:
        return "小红书"
    elif "bilibili.com" in domain or "b23.tv" in domain:
        return "B站"
    elif "douyin.com" in domain:
        return "抖音"
    else:
        return "其他"


def extract_article_content(url):
    """
    使用 OpenClaw 的 web_fetch 功能提取文章内容
    返回: (title, content, summary)
    """
    try:
        # 调用 openclaw CLI 的 web_fetch 功能
        # 使用 markdown 模式获取内容
        cmd = [
            "openclaw", "web-fetch",
            "--url", url,
            "--mode", "markdown",
            "--max-chars", "5000"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            content = result.stdout
            
            # 提取标题（通常在第一行）
            lines = content.split('\n')
            title = lines[0].strip('#').strip() if lines else url
            
            # 生成摘要（取前300字）
            content_text = '\n'.join(lines[1:]).strip()
            summary = content_text[:300] + "..." if len(content_text) > 300 else content_text
            
            print(f"✅ 内容提取成功")
            print(f"   标题: {title}")
            print(f"   正文长度: {len(content_text)} 字符")
            
            return title, content_text, summary
        else:
            print(f"⚠️  web_fetch 失败，尝试备用方法...")
            return extract_with_requests(url)
            
    except Exception as e:
        print(f"⚠️  提取失败: {e}")
        return extract_with_requests(url)


def extract_with_requests(url):
    """备用方法：使用 requests 直接获取"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding
        
        html = response.text
        
        # 提取 title - 多种方法
        title = None
        
        # 方法1: 标准 title 标签
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        
        # 方法2: 微信公众号专用 - rich_media_title
        if not title or len(title) < 3:
            wechat_title = re.search(r'<h1[^>]*class="rich_media_title"[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
            if wechat_title:
                title = wechat_title.group(1).strip()
                title = re.sub(r'<[^>]+>', '', title).strip()
        
        # 方法3: meta 标签
        if not title or len(title) < 3:
            og_title = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', html, re.IGNORECASE)
            if og_title:
                title = og_title.group(1).strip()
        
        # 方法4: 微信 msg_title
        if not title or len(title) < 3:
            msg_title = re.search(r'var\s+msg_title\s*=\s*["\']([^"\']+)["\']', html)
            if msg_title:
                title = msg_title.group(1).strip()
        
        # 清理标题
        if title:
            title = re.sub(r'\s*[-_|]\s*(知乎|微信公众号|今日头条).*$', '', title)
            title = title.strip()
        
        # 如果还是没有标题，用 URL
        if not title or len(title) < 2:
            title = None  # 返回 None 让后续处理
        
        # 简单提取正文（移除 HTML 标签）
        content = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
        content = re.sub(r'<style.*?</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        summary = content[:300] + "..." if len(content) > 300 else content
        
        return title, content, summary
        
    except Exception as e:
        print(f"❌ 备用方法也失败: {e}")
        return None, "", "无法提取内容"


def clean_empty_rows(token):
    """清理表格中的空白行"""
    print("\n🧹 检查并清理空白行...")
    
    # 获取所有记录
    api_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(api_url, headers=headers)
        result = response.json()
        
        if result.get("code") != 0:
            print(f"   ⚠️  获取记录失败，跳过清理")
            return
        
        records = result.get("data", {}).get("items", [])
        empty_count = 0
        
        for record in records:
            record_id = record.get("record_id")
            fields = record.get("fields", {})
            
            # 检查是否为空白行（标题和链接都为空）
            title_field = fields.get("文本", "")
            link_field = fields.get("链接", {})
            
            # 提取链接内容
            if isinstance(link_field, dict):
                link_text = link_field.get("link", "")
            else:
                link_text = str(link_field)
            
            # 判断是否为空白行
            is_empty = (
                (not title_field or len(str(title_field).strip()) < 2) and
                (not link_text or len(link_text.strip()) < 5)
            )
            
            if is_empty:
                # 删除空白行
                delete_url = f"{api_url}/{record_id}"
                delete_response = requests.delete(delete_url, headers=headers)
                delete_result = delete_response.json()
                
                if delete_result.get("code") == 0:
                    empty_count += 1
                    print(f"   🗑️  删除空白行: {record_id}")
        
        if empty_count > 0:
            print(f"   ✅ 清理完成，删除了 {empty_count} 个空白行")
        else:
            print(f"   ✅ 没有空白行，表格整洁")
    
    except Exception as e:
        print(f"   ⚠️  清理过程出错: {e}")


def save_article_to_feishu(url, title=None, content=None, summary=None):
    """保存文章到飞书多维表格"""
    
    print(f"\n📖 开始处理文章...")
    print(f"   链接: {url}")
    
    # 如果没有提供内容，自动提取
    if not content:
        auto_title, auto_content, auto_summary = extract_article_content(url)
        title = title or auto_title
        content = auto_content
        summary = summary or auto_summary
    
    # 检查标题是否为空
    if not title or len(title.strip()) < 2:
        print(f"\n⚠️  警告：无法自动提取标题！")
        print(f"   建议：手动指定标题")
        print(f"   用法：python feishu_article_saver.py \"{url}\" \"文章标题\"")
        return False
    
    # 获取访问令牌
    token = get_tenant_access_token()
    
    # 先清理空白行
    clean_empty_rows(token)
    
    # 自动识别来源
    source = detect_source(url)
    
    # 准备数据
    current_time = int(datetime.now().timestamp() * 1000)
    
    fields = {
        "文本": title,
        "链接": {
            "link": url
        },
        "来源": source,
        "保存时间": current_time
    }
    
    # 保存摘要（前300字）+ 完整正文
    if summary:
        # 将摘要和正文都保存到"摘要"字段
        full_text = f"【摘要】\n{summary}\n\n【正文】\n{content[:2000]}"
        fields["摘要"] = full_text
    
    # 发送请求
    api_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "fields": fields
    }
    
    response = requests.post(api_url, headers=headers, json=data)
    result = response.json()
    
    if result.get("code") == 0:
        print(f"\n✅ 保存成功！")
        print(f"   📝 标题: {title}")
        print(f"   🏷️  来源: {source}")
        print(f"   📊 摘要长度: {len(summary)} 字符")
        print(f"   📄 正文长度: {len(content)} 字符")
        return True
    else:
        print(f"\n❌ 保存失败: {result}")
        return False


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python feishu_article_saver.py <URL> [标题]")
        print("\n示例:")
        print("  python feishu_article_saver.py 'https://mp.weixin.qq.com/s/xxxxx'")
        print("  python feishu_article_saver.py 'https://zhuanlan.zhihu.com/p/123' '自定义标题'")
        return
    
    url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    save_article_to_feishu(url, title)


if __name__ == "__main__":
    main()
