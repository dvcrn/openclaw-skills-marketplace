#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书评论回复工具 - 交互式版本
支持：获取评论 → 选择评论 → AI生成回复 → 审核后发送
"""

import sys
import json
import requests
import random
from pathlib import Path
from datetime import datetime

# 配置
BASE_DIR = Path(__file__).parent
MCP_URL = "http://localhost:18060/mcp"
IDENTITY_FILE = BASE_DIR / "identity.json"
RULES_FILE = BASE_DIR / "reply_rules.json"

def load_config():
    """加载配置文件"""
    identity = {}
    rules = {}
    
    if IDENTITY_FILE.exists():
        with open(IDENTITY_FILE, 'r', encoding='utf-8') as f:
            identity = json.load(f)
    
    if RULES_FILE.exists():
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            rules = json.load(f)
    
    return identity, rules

def get_mcp_session():
    """获取 MCP Session"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json"},
            json={"jsonrpc": "2.0", "method": "initialize",
                  "params": {"protocolVersion": "2024-11-05", "capabilities": {}}},
            timeout=10)
        session_id = resp.headers.get("Mcp-Session-Id")
        if session_id:
            # 确认初始化
            requests.post(MCP_URL,
                headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                timeout=5)
        return session_id
    except Exception as e:
        print(f"❌ MCP 连接失败: {e}")
        return None

def check_login(session_id):
    """检查登录状态"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "check_login_status", "arguments": {}}},
            timeout=15)
        data = resp.json()
        if "result" in data:
            text = data["result"].get("content", [{}])[0].get("text", "")
            return "已登录" in text
        return False
    except:
        return False

def get_login_qrcode(session_id):
    """获取登录二维码"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "get_login_qrcode", "arguments": {}}},
            timeout=30)
        data = resp.json()
        if "result" in data and "content" in data["result"]:
            for item in data["result"]["content"]:
                if item.get("type") == "image":
                    import base64
                    qr_path = BASE_DIR / "login_qrcode.png"
                    with open(qr_path, "wb") as f:
                        f.write(base64.b64decode(item["data"]))
                    return str(qr_path)
    except Exception as e:
        print(f"❌ 获取二维码失败: {e}")
    return None

def parse_note_url(url):
    """解析笔记链接，提取 feed_id 和 xsec_token"""
    import re
    # https://www.xiaohongshu.com/explore/xxxxxx?xsec_token=yyy
    match = re.search(r'explore/([a-f0-9]+)', url)
    if match:
        feed_id = match.group(1)
    else:
        return None, None
    
    # 提取 xsec_token
    token_match = re.search(r'xsec_token=([A-Za-z0-9+=\-]+)', url)
    xsec_token = token_match.group(1) if token_match else ""
    
    return feed_id, xsec_token

def fetch_comments(session_id, feed_id, xsec_token):
    """获取评论（包括一级评论、子评论、楼中楼）"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "get_feed_detail", "arguments": {
                      "feed_id": feed_id,
                      "xsec_token": xsec_token,
                      "load_all_comments": True,
                      "click_more_replies": True
                  }}},
            timeout=60)
        
        data = resp.json()
        if "result" in data and "content" in data["result"]:
            text = data["result"]["content"][0].get("text", "")
            try:
                result = json.loads(text)
                comments = result.get("data", {}).get("comments", {}).get("list", [])
                return comments
            except:
                pass
    except Exception as e:
        print(f"❌ 获取评论失败: {e}")
    return []

def extract_all_comments(comments, author_user_id=None):
    """提取所有评论（一级、子评论、楼中楼），排除博主自己的评论"""
    all_comments = []
    
    for comment in comments:
        user_id = comment.get("userInfo", {}).get("userId", "")
        is_author = "is_author" in comment.get("showTags", [])
        
        # 跳过博主自己的评论
        if is_author:
            continue
        
        # 检查是否已有博主回复
        has_author_reply = False
        for sub in comment.get("subComments", []):
            if "is_author" in sub.get("showTags", []):
                has_author_reply = True
                break
        
        # 如果没有博主回复，添加到列表
        if not has_author_reply:
            all_comments.append({
                "comment_id": comment["id"],
                "user_name": comment.get("userInfo", {}).get("nickname", "用户"),
                "user_id": user_id,
                "content": comment["content"],
                "is_sub": False,
                "parent_id": None
            })
        
        # 处理子评论
        for sub in comment.get("subComments", []):
            sub_is_author = "is_author" in sub.get("showTags", [])
            if sub_is_author:
                continue
            
            # 检查子评论是否有博主回复（楼中楼）
            sub_has_reply = False
            for third in sub.get("subComments", []):
                if "is_author" in third.get("showTags", []):
                    sub_has_reply = True
                    break
            
            if not sub_has_reply:
                all_comments.append({
                    "comment_id": sub["id"],
                    "user_name": sub.get("userInfo", {}).get("nickname", "用户"),
                    "user_id": sub.get("userInfo", {}).get("userId", ""),
                    "content": sub["content"],
                    "is_sub": True,
                    "parent_id": comment["id"]
                })
    
    return all_comments

def generate_reply(comment, user_name, identity, rules):
    """AI 生成回复"""
    # 读取配置
    role = identity.get("identity", {}).get("role", "小红书博主")
    personality = "、".join(identity.get("identity", {}).get("personality", ["幽默", "接地气"]))
    
    safety_rules = rules.get("safety_rules", {})
    safety_text = "\n".join([f"{i+1}. {v}" for i, (k, v) in enumerate(safety_rules.items()) if k.startswith("铁律")])
    
    reply_rules_list = rules.get("reply_rules", [])
    rules_text = "\n".join([f"- {r}" for r in reply_rules_list])
    
    # 获取 AI 配置
    ai_config = rules.get("ai_config", {})
    model = ai_config.get("model", "glm-4-flash")
    
    # 获取 API Key（从环境变量或配置）
    import os
    api_key = os.environ.get("GLM_API_KEY", "")
    if not api_key:
        # 尝试从其他地方读取
        try:
            with open(BASE_DIR / ".glm_api_key", "r") as f:
                api_key = f.read().strip()
        except:
            pass
    
    if not api_key:
        return "哈哈🐾"  # fallback
    
    today = datetime.now()
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    date_str = today.strftime("%Y年%m月%d日")
    weekday = weekday_cn[today.weekday()]
    
    prompt = f"""你是小多，一个{role}，性格{personality}。今天是{date_str} {weekday}。

【安全铁律 - 必须遵守】
{safety_text}

【回复规则】
{rules_text}

用户 {user_name} 说：{comment}

请根据以上规则回复："""
    
    try:
        resp = requests.post("https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            json={"model": model, "max_tokens": 200, "enable_thinking": False,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=15)
        
        if resp.status_code == 200:
            text = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "哈哈🐾")
            return text[:80] if "🐾" in text else text.strip() + "🐾"
    except Exception as e:
        print(f"⚠️ AI 生成失败: {e}")
    
    # fallback
    return random.choice(["哈哈🐾", "确实🐾", "怎么说呢🐾"])

def send_reply(session_id, feed_id, comment_id, user_id, content):
    """发送回复到小红书"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "reply_comment_in_feed", "arguments": {
                      "feed_id": feed_id,
                      "comment_id": comment_id,
                      "user_id": user_id,
                      "content": content
                  }}},
            timeout=60)
        
        data = resp.json()
        if "result" in data:
            return True, None
        elif "error" in data:
            return False, data["error"].get("message", "未知错误")
    except Exception as e:
        return False, str(e)
    
    return False, "未知错误"

def main():
    print("=" * 50)
    print("   小红书评论回复工具 - 交互式版本")
    print("=" * 50)
    
    # 加载配置
    identity, rules = load_config()
    
    # 1. 获取 MCP Session
    print("\n📡 连接 MCP 服务...")
    session_id = get_mcp_session()
    if not session_id:
        print("❌ 无法连接 MCP 服务，请确保服务已启动")
        sys.exit(1)
    
    # 2. 检查登录状态
    print("🔍 检查登录状态...")
    if not check_login(session_id):
        print("⚠️ 未登录小红书")
        qr_path = get_login_qrcode(session_id)
        if qr_path:
            print(f"📱 请扫码登录，二维码已保存到: {qr_path}")
        sys.exit(1)
    
    print("✅ 已登录")
    
    # 3. 获取笔记链接
    print("\n📝 请输入小红书笔记链接：")
    url = input("> ").strip()
    
    feed_id, xsec_token = parse_note_url(url)
    if not feed_id:
        print("❌ 无法解析笔记链接")
        sys.exit(1)
    
    # 4. 获取评论
    print(f"\n📥 正在获取评论...")
    comments = fetch_comments(session_id, feed_id, xsec_token)
    if not comments:
        print("❌ 获取评论失败或没有评论")
        sys.exit(1)
    
    # 5. 提取待回复评论
    all_comments = extract_all_comments(comments)
    if not all_comments:
        print("✅ 所有评论都已回复，没有待回复的评论")
        sys.exit(0)
    
    print(f"\n📋 待回复评论（共 {len(all_comments)} 条）：\n")
    for i, c in enumerate(all_comments, 1):
        prefix = "  └─ " if c["is_sub"] else ""
        print(f"{prefix}{i}. @{c['user_name']}：{c['content'][:30]}...")
    
    # 6. 选择要回复的评论
    print("\n请选择要回复的评论：")
    print("- 输入序号（如 1,2,3）")
    print("- 或输入 '全部'")
    selection = input("> ").strip()
    
    if selection == "全部":
        selected = all_comments
    else:
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(",")]
            selected = [all_comments[i] for i in indices if 0 <= i < len(all_comments)]
        except:
            print("❌ 输入无效")
            sys.exit(1)
    
    # 7. 生成回复
    print(f"\n🤖 正在生成 {len(selected)} 条回复...\n")
    replies = []
    for c in selected:
        reply = generate_reply(c["content"], c["user_name"], identity, rules)
        replies.append({
            **c,
            "reply": reply
        })
        print(f"  @{c['user_name']}：{c['content'][:20]}...")
        print(f"    → {reply}")
        print()
    
    # 8. 审核
    print("=" * 50)
    print("📋 回复预览：\n")
    for i, r in enumerate(replies, 1):
        print(f"{i}. @{r['user_name']}：{r['content'][:25]}...")
        print(f"   回复：{r['reply']}")
        print()
    
    print("请审核：")
    print("1. 确认发送")
    print("2. 修改某条回复")
    print("3. 仅复制（不发送）")
    print("4. 取消")
    choice = input("> ").strip()
    
    if choice == "1":
        # 发送回复
        print("\n📤 正在发送...")
        success = 0
        failed = 0
        for r in replies:
            ok, err = send_reply(session_id, feed_id, 
                                 r["parent_id"] if r["is_sub"] else r["comment_id"],
                                 r["user_id"], r["reply"])
            if ok:
                success += 1
                print(f"  ✅ @{r['user_name']}")
            else:
                failed += 1
                print(f"  ❌ @{r['user_name']}: {err}")
        
        print(f"\n✅ 发送完成：成功 {success} 条，失败 {failed} 条")
    
    elif choice == "2":
        print("请输入序号和新回复（如：1 这是新的回复内容🐾）")
        mod = input("> ").strip()
        parts = mod.split(None, 1)
        if len(parts) == 2:
            idx = int(parts[0]) - 1
            if 0 <= idx < len(replies):
                replies[idx]["reply"] = parts[1]
                print(f"✅ 已修改第 {idx+1} 条回复")
        # 重新展示审核
        print("\n修改后的回复：")
        for r in replies:
            print(f"  @{r['user_name']} → {r['reply']}")
    
    elif choice == "3":
        print("\n📋 回复内容：")
        for r in replies:
            print(r["reply"])
    
    else:
        print("❌ 已取消")

if __name__ == "__main__":
    main()
