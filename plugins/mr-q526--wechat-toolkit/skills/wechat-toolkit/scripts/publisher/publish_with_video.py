#!/usr/bin/env python3
"""
publish_with_video.py - 发布含视频的 Markdown 文章到微信公众号草稿箱

流程：
1. 扫描 Markdown 中的 mp4 引用
2. 上传每个 mp4 到微信永久素材库，获取 media_id
3. 把 mp4 引用替换为 VIDEO_PLACEHOLDER_<n> 占位符
4. 用 wenyan 发布（获取草稿 media_id）
5. 用微信 API 拉取草稿内容
6. 将占位符替换为 <mp-video> 标签
7. 更新草稿

用法：
    python3 publish_with_video.py <markdown-file> [theme] [highlight]

环境变量（或从 TOOLS.md 自动读取）：
    WECHAT_APP_ID
    WECHAT_APP_SECRET
"""

import sys
import os
import re
import json
import time
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# ──────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────
TOOLS_MD_PATHS = [
    Path.home() / ".openclaw/workspace-xina-gongzhonghao/TOOLS.md",
    Path.home() / ".openclaw/workspace/TOOLS.md",
]
WENYAN_TOKEN_CACHE = Path.home() / ".config/wenyan-md/token.json"
DEFAULT_THEME = "lapis"
DEFAULT_HIGHLIGHT = "solarized-light"


def load_credentials():
    app_id = os.environ.get("WECHAT_APP_ID", "")
    secret = os.environ.get("WECHAT_APP_SECRET", "")
    if app_id and secret:
        return app_id, secret

    for tools_path in TOOLS_MD_PATHS:
        if not tools_path.exists():
            continue
        content = tools_path.read_text()
        for line in content.splitlines():
            if "export WECHAT_APP_ID=" in line:
                app_id = line.split("=", 1)[1].strip()
            if "export WECHAT_APP_SECRET=" in line:
                secret = line.split("=", 1)[1].strip()
        if app_id and secret:
            print(f"📖 凭证从 {tools_path} 读取")
            return app_id, secret

    raise RuntimeError("❌ 未找到 WECHAT_APP_ID / WECHAT_APP_SECRET，请设置环境变量或在 TOOLS.md 中配置")


def get_fresh_token(app_id, secret):
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={secret}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    if "access_token" not in data:
        raise RuntimeError(f"获取 token 失败: {data}")
    token = data["access_token"]
    expire_at = int(time.time()) + data.get("expires_in", 7200)
    # 写入 wenyan 缓存，保持 wenyan 与我们同步
    WENYAN_TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    WENYAN_TOKEN_CACHE.write_text(json.dumps({"appid": app_id, "accessToken": token, "expireAt": expire_at}))
    return token


def upload_video(token, video_path, title="视频"):
    """上传视频到微信永久素材库，返回 (media_id, vid)"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=video"
    description = json.dumps({"title": title, "introduction": title}, ensure_ascii=False)
    
    result = subprocess.run(
        [
            "curl", "-s", "-m", "180",
            "-X", "POST", url,
            "-F", f"media=@{video_path};type=video/mp4",
            "-F", f"description={description}",
        ],
        capture_output=True, text=True, timeout=200,
    )
    data = json.loads(result.stdout)
    if "media_id" not in data:
        raise RuntimeError(f"视频上传失败 ({video_path}): {data}")
    media_id = data["media_id"]
    
    # Fetch the vid identifier needed for iframe embed
    list_url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}"
    list_body = json.dumps({"type": "video", "offset": 0, "count": 5}).encode()
    req = urllib.request.Request(list_url, data=list_body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        list_data = json.loads(r.read())
    
    vid = ""
    cover_url = ""
    for item in list_data.get("item", []):
        if item.get("media_id") == media_id:
            vid = item.get("vid", "")
            cover_url = item.get("cover_url", "")
            break
    
    return media_id, vid, cover_url


def find_mp4_refs(content, article_dir):
    """扫描 Markdown 中所有 mp4 引用，返回 [(alt, rel_path, abs_path), ...]"""
    pattern = re.compile(r'!?\[([^\]]*)\]\(([^)]+\.mp4)\)', re.IGNORECASE)
    refs = []
    for m in pattern.finditer(content):
        alt = m.group(1)
        rel = m.group(2)
        abs_path = (article_dir / rel).resolve()
        refs.append((alt, rel, abs_path))
    return refs


def process_videos(content, article_dir, token):
    """
    将所有 mp4 引用：
    1. 验证是真实视频（非 HTML）
    2. 上传到微信永久素材库
    3. 替换为占位符 VIDEO_PLACEHOLDER_<media_id>
    返回 (patched_content, {placeholder: media_id})
    """
    refs = find_mp4_refs(content, article_dir)
    if not refs:
        print("✅ 文章中没有视频引用")
        return content, {}

    placeholder_map = {}  # placeholder -> media_id
    
    for alt, rel, abs_path in refs:
        if not abs_path.exists():
            print(f"⚠️  视频文件不存在: {abs_path}，跳过")
            # 替换为说明文字
            content = content.replace(f"![{alt}]({rel})", f"[视频: {alt}（文件不存在）]")
            content = content.replace(f"[{alt}]({rel})", f"[视频: {alt}（文件不存在）]")
            continue

        # 检查是否为真实视频（不是 HTML）
        file_result = subprocess.run(["file", str(abs_path)], capture_output=True, text=True)
        if "HTML" in file_result.stdout or "text" in file_result.stdout.lower():
            print(f"⚠️  {rel} 不是真实视频文件（可能是 HTML 预览页），替换为文字")
            content = content.replace(f"![{alt}]({rel})", f"[视频预览: {alt}]")
            content = content.replace(f"[{alt}]({rel})", f"[视频预览: {alt}]")
            continue

        file_size_mb = abs_path.stat().st_size / 1024 / 1024
        print(f"🎬 上传视频: {rel} ({file_size_mb:.1f} MB)...")
        
        try:
            media_id, vid, cover_url = upload_video(token, str(abs_path), title=alt or abs_path.stem)
            placeholder = f"VIDEO_PLACEHOLDER_{media_id}"
            placeholder_map[placeholder] = (media_id, vid, cover_url)
            
            # 替换 md 引用为唯一占位符（pure text，不会被 wenyan 处理）
            content = content.replace(f"![{alt}]({rel})", placeholder)
            content = content.replace(f"[{alt}]({rel})", placeholder)
            print(f"   ✅ 上传成功: media_id={media_id[:30]}... vid={vid}")
        except Exception as e:
            print(f"   ❌ 上传失败: {e}，替换为截图名称")
            png_ref = rel.replace(".mp4", ".png")
            content = content.replace(f"![{alt}]({rel})", f"![{alt}]({png_ref})")
            content = content.replace(f"[{alt}]({rel})", f"[{alt}]({png_ref})")

    return content, placeholder_map


def publish_with_wenyan(md_path, theme, highlight, app_id, secret):
    """运行 wenyan 发布，返回草稿 media_id（从 stdout 解析）"""
    env = os.environ.copy()
    env["WECHAT_APP_ID"] = app_id
    env["WECHAT_APP_SECRET"] = secret

    result = subprocess.run(
        ["wenyan", "publish", "-f", str(md_path), "-t", theme, "-h", highlight],
        env=env, capture_output=True, text=True, timeout=120,
    )
    print("wenyan stdout:", result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"wenyan 发布失败: {result.stderr or result.stdout}")

    # 解析 Media ID
    m = re.search(r"Media ID[:\s]+(\S+)", result.stdout)
    if m:
        return m.group(1)
    return None


def build_video_iframe(vid, cover_url=""):
    """构建微信公众号文章视频 iframe 标签（用 vid/mpvid，非 media_id）"""
    src = f"https://mp.weixin.qq.com/mp/readtemplate?t=pages/video_player_tmpl&action=mpvideo&scene=0&vid={vid}"
    return (
        f'<iframe class="video_iframe rich_pages wxw-img" '
        f'data-src="{src}" '
        f'data-vidtype="2" '
        f'data-mpvid="{vid}" '
        f'{("data-cover=" + chr(34) + cover_url + chr(34) + " ") if cover_url else ""}'
        f'allowfullscreen="" frameborder="0" scrolling="no" '
        f'style="width: 677px; height: 508px;" '
        f'src="{src}"></iframe>'
    )


def patch_draft_with_videos(token, draft_media_id, placeholder_map):
    """拉取草稿，替换视频占位符为 iframe <mp-video> embed，更新草稿"""
    if not placeholder_map:
        return

    print(f"\n🎬 开始修复草稿中的视频占位符...")

    # 拉取草稿
    url = f"https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}"
    body = json.dumps({"media_id": draft_media_id}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        draft_data = json.loads(resp.read())

    if "news_item" not in draft_data:
        print(f"⚠️  拉取草稿失败: {draft_data}")
        return

    articles = draft_data["news_item"]
    for article in articles:
        content_html = article.get("content", "")
        for placeholder, (media_id, vid, cover_url) in placeholder_map.items():
            if placeholder in content_html:
                if vid:
                    # Use proper WeChat iframe embed with vid (mpvid)
                    iframe = build_video_iframe(vid, cover_url)
                    video_tag = f'<p>{iframe}</p>'
                    print(f"   ✅ {placeholder[:35]}... → iframe(vid={vid[:30]}...)")
                else:
                    # Fallback: use media_id in mp-video tag
                    video_tag = f'<mp-video data-pluginname="mpvideo" data-url="{media_id}"></mp-video>'
                    print(f"   ⚠️  vid not found, fallback → mp-video(media_id)")
                content_html = content_html.replace(placeholder, video_tag)
        article["content"] = content_html

    # 更新草稿
    update_url = f"https://api.weixin.qq.com/cgi-bin/draft/update?access_token={token}"
    update_body = json.dumps({
        "media_id": draft_media_id,
        "index": 0,
        "articles": articles[0],
    }, ensure_ascii=False).encode("utf-8")
    req2 = urllib.request.Request(update_url, data=update_body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req2, timeout=15) as resp:
        result = json.loads(resp.read())

    if result.get("errcode") in (0, None):
        print("✅ 草稿视频更新成功！")
    else:
        print(f"⚠️  草稿更新失败: {result}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    article_path = Path(sys.argv[1]).resolve()
    theme = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_THEME
    highlight = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_HIGHLIGHT

    if not article_path.exists():
        print(f"❌ 文件不存在: {article_path}")
        sys.exit(1)

    article_dir = article_path.parent
    print(f"📄 文章: {article_path}")
    print(f"🎨 主题: {theme} / {highlight}\n")

    # 1. 读取凭证
    app_id, secret = load_credentials()

    # 2. 获取 token（并写入 wenyan 缓存）
    print("🔑 获取 access_token...")
    token = get_fresh_token(app_id, secret)
    print(f"   Token: {token[:20]}...\n")

    # 3. 处理视频（上传 + 替换为占位符）
    original_content = article_path.read_text(encoding="utf-8")
    patched_content, placeholder_map = process_videos(original_content, article_dir, token)

    # 4. 写入临时文件
    tmp_md = article_path.parent / f"_publish_tmp_{article_path.stem}.md"
    tmp_md.write_text(patched_content, encoding="utf-8")
    print(f"\n📝 临时文件: {tmp_md}")

    try:
        # 5. 刷新 token cache（保证 wenyan 用最新 token）
        # 注意：如果视频上传耗时较长，需要重新刷新
        token = get_fresh_token(app_id, secret)

        # 6. wenyan 发布
        print("\n🚀 发布草稿中...")
        draft_media_id = publish_with_wenyan(tmp_md, theme, highlight, app_id, secret)
        if draft_media_id:
            print(f"✅ 草稿发布成功！Media ID: {draft_media_id}")
        else:
            print("⚠️  发布成功但未解析到 Media ID，跳过视频注入")

        # 7. 如果有视频，patch 草稿
        if placeholder_map and draft_media_id:
            # 再刷新一次 token（wenyan 发布后 token 可能已新建）
            token = get_fresh_token(app_id, secret)
            patch_draft_with_videos(token, draft_media_id, placeholder_map)

    finally:
        # 清理临时文件
        if tmp_md.exists():
            tmp_md.unlink()
            print(f"\n🗑️  临时文件已清理")

    print("\n🎉 完成！请前往公众号后台草稿箱审核并发布：")
    print("   https://mp.weixin.qq.com/")


if __name__ == "__main__":
    main()
