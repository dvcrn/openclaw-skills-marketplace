#!/usr/bin/env python3
"""
Feishu Smart Doc Writer
飞书智能文档写入器 - 自动分段、分批写入
支持首次使用自动引导配置

核心功能：
1. 智能分块写入 - 解决飞书API字数限制导致的空白文档
2. 自动转移所有权 - 创建文档后自动转移给用户
3. 首次使用引导 - 自动询问OpenID并配置
"""

import json
import os
from typing import Dict, Optional
from dataclasses import dataclass, asdict

# 配置文件路径
CONFIG_PATH = os.path.expanduser("~/.openclaw/workspace/skills/feishu-smart-doc-writer/user_config.json")

@dataclass
class UserConfig:
    """用户配置"""
    owner_openid: str = ""
    permission_noted: bool = False  # 用户是否已确认权限
    first_time: bool = True  # 是否首次使用
    
    def save(self):
        """保存配置"""
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    @classmethod
    def load(cls) -> 'UserConfig':
        """加载配置"""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return cls(**data)
        except Exception as e:
            print(f"加载配置失败: {e}")
        return cls()


# 引导消息模板
FIRST_TIME_GUIDE = """👋 **欢迎使用 Feishu Smart Doc Writer！**

本 Skill 可以帮助你：
✅ **智能分块写入** - 解决长文档写入时因API限制导致的空白问题
✅ **自动转移所有权** - 创建文档后自动转移给你，拥有完全控制权

---

## 🔧 首次使用配置

### 第1步：获取你的 OpenID

**详细步骤（精确路径）：**

1. **登录飞书开放平台**
   - 网址：https://open.feishu.cn

2. **进入权限管理并前往调试台**
   - 进入你的**相关应用**
   - 点击 **"权限管理"**
   - 搜索权限：`im:message`
   - 鼠标移动到 **"相关API事件"**
   - 选择：**【API】发送消息**
   - 点击右下角：**"前往API调试台"**

3. **找到 "快速复制 open_id"**
   - 在页面中找到 **蓝色文字** "快速复制 open_id"
   - 点击这个链接

4. **选择用户并复制**
   - 在弹出的选择框中，**选择你的账号**
   - 点击 **"复制"** 按钮
   - 得到格式如：`ou_5b921cba0fd6e7c885276a02d730ec19`

💡 **提示**：OpenID 是以 `ou_` 开头的一串字符，不是数字ID

---

### 第2步：开通并发布权限

⚠️ **重要：需要开通权限并发布应用新版本**

**开通权限步骤：**

1. **进入权限管理**
   - 登录 https://open.feishu.cn
   - 进入你的应用
   - 点击左侧菜单 **"权限管理"**

2. **搜索并开通权限**
   - 在搜索框输入：`docs:permission.member:transfer`
   - 找到权限 **"转移云文档的所有权"**
   - 点击 **"开通"** 按钮

3. **发布新版本（关键！）**
   - 开通后，点击页面右上角的 **"发布"** 按钮
   - 等待发布完成（显示"已发布"状态）
   - ⚠️ **不发布的话，权限不会生效！**

---

## 💬 请回复配置信息

请按以下格式回复：

```
配置OpenID：ou_你的OpenID
权限已开通并发布：是
```

例如：
```
配置OpenID：ou_5b921cba0fd6e7c885276a02d730ec19
权限已开通并发布：是
```

配置完成后，本 Skill 将自动保存配置，之后创建文档会自动转移所有权给你！
"""


async def write_smart(ctx, args: dict) -> dict:
    """
    智能创建飞书文档（自动分块 + 自动转移所有权）
    
    首次使用时会自动引导配置。
    
    Args:
        ctx: OpenClaw 上下文
        args: 包含 title, content, folder_token, chunk_size, show_progress
    
    Returns:
        {"doc_url": "...", "doc_token": "...", "chunks_count": N, "owner_transferred": True/False}
    """
    # 加载用户配置
    config = UserConfig.load()
    
    # 首次使用或未完成配置，显示引导
    if config.first_time or not config.owner_openid:
        return {
            "doc_url": None,
            "doc_token": None,
            "chunks_count": 0,
            "owner_transferred": False,
            "need_config": True,
            "message": FIRST_TIME_GUIDE
        }
    
    # 已配置，正常执行
    title = args.get("title")
    content = args.get("content", "")
    folder_token = args.get("folder_token")
    chunk_size = args.get("chunk_size", 2000)
    show_progress = args.get("show_progress", True)
    
    if not title:
        raise ValueError("必须提供 title 参数")
    
    from .feishu_smart_doc_writer import FeishuDocWriter, ChunkConfig
    
    chunk_config = ChunkConfig(
        chunk_size=chunk_size,
        show_progress=show_progress
    )
    writer = FeishuDocWriter(ctx, chunk_config)
    
    try:
        # 使用配置的 owner_openid 自动转移
        result = await writer.write_document_with_transfer(
            title=title,
            content=content,
            folder_token=folder_token,
            owner_openid=config.owner_openid
        )
        
        transfer_msg = "，所有权已转移" if result.get("owner_transferred") else ""
        
        return {
            "doc_url": result["doc_url"],
            "doc_token": result["doc_token"],
            "chunks_count": result["chunks_count"],
            "owner_transferred": result["owner_transferred"],
            "need_config": False,
            "message": f"✅ 文档创建成功，共分 {result['chunks_count']} 块写入{transfer_msg}"
        }
    except Exception as e:
        return {
            "doc_url": None,
            "doc_token": None,
            "chunks_count": 0,
            "owner_transferred": False,
            "need_config": False,
            "message": f"❌ 创建失败: {e}"
        }


async def configure(ctx, args: dict) -> dict:
    """
    配置 Skill
    
    用户首次使用时，通过此工具配置 OpenID。
    
    Args:
        ctx: OpenClaw 上下文
        args: 包含 openid, permission_checked
    
    Returns:
        {"success": True/False, "message": "..."}
    """
    openid = args.get("openid", "").strip()
    permission_checked = args.get("permission_checked", False)
    
    # 验证 OpenID 格式
    if not openid:
        return {
            "success": False,
            "message": "❌ 请提供 OpenID"
        }
    
    if not openid.startswith("ou_"):
        return {
            "success": False,
            "message": "❌ OpenID 格式错误，应以 'ou_' 开头，请检查"
        }
    
    # 保存配置
    config = UserConfig()
    config.owner_openid = openid
    config.permission_noted = permission_checked
    config.first_time = False
    
    if config.save():
        return {
            "success": True,
            "openid": openid,
            "message": f"✅ 配置成功！\n\n你的 OpenID：{openid}\n\n配置已保存，现在可以使用 write_smart 创建文档，所有权会自动转移给你。"
        }
    else:
        return {
            "success": False,
            "message": "❌ 配置保存失败"
        }


async def append_smart(ctx, args: dict) -> dict:
    """
    智能追加内容到飞书文档（自动分块）
    
    Args:
        ctx: OpenClaw 上下文
        args: 包含 doc_url, content, chunk_size, show_progress
    
    Returns:
        {"success": True/False, "chunks_count": N}
    """
    doc_url = args.get("doc_url")
    content = args.get("content", "")
    chunk_size = args.get("chunk_size", 2000)
    show_progress = args.get("show_progress", True)
    
    if not doc_url:
        raise ValueError("必须提供 doc_url 参数")
    
    from .feishu_smart_doc_writer import FeishuDocWriter, ChunkConfig, ContentChunker
    
    config = ChunkConfig(
        chunk_size=chunk_size,
        show_progress=show_progress
    )
    writer = FeishuDocWriter(ctx, config)
    
    try:
        success = await writer.append_to_document(doc_url, content)
        
        # 计算分块数
        chunks = ContentChunker(config).chunk_content(content)
        
        return {
            "success": success,
            "chunks_count": len(chunks),
            "message": f"{'✅' if success else '❌'} 追加 {'成功' if success else '失败'}，共分 {len(chunks)} 块"
        }
    except Exception as e:
        return {
            "success": False,
            "chunks_count": 0,
            "message": f"❌ 追加失败: {e}"
        }


async def transfer_ownership(ctx, args: dict) -> dict:
    """
    转移文档所有权
    
    Args:
        ctx: OpenClaw 上下文
        args: 包含 doc_url, owner_openid
    
    Returns:
        {"success": True/False, "message": "..."}
    """
    doc_url = args.get("doc_url")
    owner_openid = args.get("owner_openid")
    
    if not doc_url or not owner_openid:
        raise ValueError("必须提供 doc_url 和 owner_openid 参数")
    
    from .feishu_smart_doc_writer import FeishuDocWriter, ChunkConfig
    
    config = ChunkConfig(show_progress=False)
    writer = FeishuDocWriter(ctx, config)
    
    try:
        success = await writer.transfer_ownership(doc_url, owner_openid)
        
        return {
            "success": success,
            "message": f"{'✅' if success else '❌'} 所有权转移{'成功' if success else '失败'}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ 转移失败: {e}"
        }


async def get_config_status(ctx, args: dict) -> dict:
    """
    获取当前配置状态
    
    Returns:
        {"configured": True/False, "openid": "...", "message": "..."}
    """
    config = UserConfig.load()
    
    if config.owner_openid:
        return {
            "configured": True,
            "openid": config.owner_openid,
            "first_time": config.first_time,
            "message": f"✅ 已配置\nOpenID: {config.owner_openid}"
        }
    else:
        return {
            "configured": False,
            "openid": None,
            "first_time": config.first_time,
            "message": "⚠️ 未配置\n请使用 configure 工具进行配置"
        }


async def search_docs(ctx, args: dict) -> dict:
    """
    搜索本地索引中的文档
    
    Args:
        ctx: OpenClaw 上下文
        args: 包含 keyword, search_in(可选)
    
    Returns:
        {"results": [...], "count": N, "message": "..."}
    """
    keyword = args.get("keyword", "").strip()
    search_in = args.get("search_in", ["name", "summary", "tags"])
    
    if not keyword:
        return {
            "results": [],
            "count": 0,
            "message": "❌ 请提供搜索关键词"
        }
    
    try:
        from .index_manager import IndexManager
        
        manager = IndexManager()
        results = manager.search_docs(keyword, search_in)
        
        # 格式化结果
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "name": doc.get("name", ""),
                "type": doc.get("type", ""),
                "link": doc.get("link", ""),
                "summary": doc.get("summary", ""),
                "status": doc.get("status", ""),
                "tags": doc.get("tags", ""),
                "updated": doc.get("updated", "")
            })
        
        return {
            "results": formatted_results,
            "count": len(formatted_results),
            "message": f"✅ 找到 {len(formatted_results)} 个结果" if formatted_results else f"⚠️ 未找到包含 '{keyword}' 的文档"
        }
        
    except Exception as e:
        return {
            "results": [],
            "count": 0,
            "message": f"❌ 搜索失败: {e}"
        }


async def list_docs(ctx, args: dict) -> dict:
    """
    列出所有文档（支持筛选）
    
    Args:
        ctx: OpenClaw 上下文
        args: 包含 tag(可选), status(可选), limit(可选)
    
    Returns:
        {"results": [...], "count": N, "message": "..."}
    """
    tag = args.get("tag")
    status = args.get("status")
    limit = args.get("limit", 50)
    
    try:
        from .index_manager import IndexManager
        
        manager = IndexManager()
        results = manager.list_docs(tag=tag, status=status, limit=limit)
        
        # 格式化结果
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "name": doc.get("name", ""),
                "type": doc.get("type", ""),
                "link": doc.get("link", ""),
                "summary": doc.get("summary", ""),
                "status": doc.get("status", ""),
                "tags": doc.get("tags", ""),
                "updated": doc.get("updated", "")
            })
        
        # 构建消息
        filter_desc = []
        if tag:
            filter_desc.append(f"标签 '{tag}'")
        if status:
            filter_desc.append(f"状态 '{status}'")
        
        filter_text = "，".join(filter_desc) if filter_desc else "全部"
        
        return {
            "results": formatted_results,
            "count": len(formatted_results),
            "message": f"✅ {filter_text}文档共 {len(formatted_results)} 个"
        }
        
    except Exception as e:
        return {
            "results": [],
            "count": 0,
            "message": f"❌ 列出文档失败: {e}"
        }


# 版本信息
__version__ = "1.3.0"
__all__ = [
    "write_smart",
    "append_smart",
    "transfer_ownership",
    "configure",
    "get_config_status",
    "search_docs",
    "list_docs",
    "UserConfig",
    "FIRST_TIME_GUIDE"
]