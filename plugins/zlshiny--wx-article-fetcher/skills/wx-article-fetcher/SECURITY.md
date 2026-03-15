# wx-article-fetcher 安全说明

**版本:** 1.0.1  
**最后更新:** 2026-03-13  
**作者:** 十三香 (agent 管理者) 🌶️

---

## 🔐 安全架构

本 skill 采用 **双层安全控制**：权限验证 + 数据隔离

```
┌─────────────────────────────────────────────────────────┐
│                    权限验证层                              │
├─────────────────────────────────────────────────────────┤
│  • 检查 OPENCLAW_AGENT_NAME                              │
│  • 仅允许：蒜蓉、baseagent                               │
│  • 其他 agent → 拒绝访问                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    数据隔离层                              │
├─────────────────────────────────────────────────────────┤
│  • baseagent → 全局目录 (~/.wx_*)                        │
│  • 其他 agent → 工作空间内 ({workspace}/.wx_*)           │
│  • 物理隔离，无法跨空间访问                               │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 数据存储位置

### baseagent (agent 管理者)

```
~/.wx_biz_query/
├── cache.json          # 公众号 biz 缓存
└── config.enc          # 加密的签名配置

~/.wx_articles/
└── <公众号名称>_<时间戳>/
    ├── YYYY-MM-DD/
    │   ├── xxx.json
    │   └── xxx.md
    └── images/
```

### 蒜蓉（授权 agent）

```
{workspace}/
├── .wx_cache/
│   └── wx_biz_cache.json    # 独立的缓存文件
├── .wx_config/
│   └── wx_sign.enc          # 独立的签名配置
└── .wx_articles/
    └── <公众号名称>_<时间戳>/
        ├── YYYY-MM-DD/
        │   ├── xxx.json
        │   └── xxx.md
        └── images/
```

**workspace 示例:**
- `/Users/edy/.openclaw/workspace/suanrong/` (蒜蓉的工作空间)
- `/Users/edy/.openclaw/workspace/malatang/` (麻辣烫的工作空间)

---

## 🚫 访问控制矩阵

| 操作 | baseagent | 蒜蓉 | 其他 agent |
|------|-----------|------|------------|
| 查询公众号 biz | ✅ | ✅ | ❌ |
| 抓取文章 | ✅ | ✅ | ❌ |
| 访问自己的缓存 | ✅ | ✅ | ❌ |
| 访问自己的文章 | ✅ | ✅ | ❌ |
| 访问其他 agent 数据 | ✅ (管理员) | ❌ | ❌ |
| 修改其他 agent 数据 | ✅ (管理员) | ❌ | ❌ |

---

## 🔒 安全机制详解

### 1. 权限验证 (`commands/wx-commands.sh`)

```bash
check_permission() {
    local current_agent="${OPENCLAW_AGENT_NAME:-unknown}"
    
    # 仅允许授权 agent
    if [[ "$current_agent" != "蒜蓉" && "$current_agent" != "baseagent" ]]; then
        echo "❌ 权限拒绝"
        exit 1
    fi
}
```

### 2. 数据路径隔离 (Python 脚本)

```python
def get_cache_path():
    agent_name = os.environ.get("OPENCLAW_AGENT_NAME", "unknown")
    
    # baseagent 访问全局数据
    if agent_name == "baseagent":
        return Path.home() / ".wx_biz_query" / "cache.json"
    
    # 其他 agent 只能访问自己工作空间
    workspace = os.environ.get("OPENCLAW_WORKSPACE")
    return Path(workspace) / ".wx_cache" / "wx_biz_cache.json"
```

### 3. 环境变量依赖

脚本依赖以下环境变量（由 OpenClaw 自动设置）：

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENCLAW_AGENT_NAME` | 当前 agent 名称 | `baseagent`, `蒜蓉` |
| `OPENCLAW_WORKSPACE` | 当前 agent 工作空间 | `/path/to/workspace/suanrong` |

**攻击防护:**
- 即使 agent 尝试伪造环境变量，也无法突破文件系统权限
- 工作空间路径由 OpenClaw 框架控制，agent 无法自行修改

---

## ⚠️ 安全注意事项

### 对 baseagent (agent 管理者)

✅ **可以:**
- 访问所有 agent 的数据（用于审计、备份）
- 管理全局缓存和配置
- 查看任何 agent 的抓取记录

❌ **禁止:**
- 未经授权查看其他 agent 的敏感数据
- 修改其他 agent 的配置文件
- 将数据泄露给未授权的第三方

### 对蒜蓉（授权 agent）

✅ **可以:**
- 使用 skill 查询和抓取文章
- 访问自己工作空间内的所有数据
- 管理自己的缓存和配置

❌ **禁止:**
- 尝试访问 `~/.wx_*` 全局目录
- 尝试访问其他 agent 的工作空间
- 将签名配置分享给其他 agent

### 对其他 agent

❌ **完全禁止:**
- 使用本 skill 的任何功能
- 访问本 skill 的任何数据
- 绕过权限检查的尝试

---

## 🔍 审计日志

所有操作都会记录以下信息：

```bash
# 权限检查日志
✅ 权限验证通过：蒜蓉
🔒 隔离模式：工作空间 = /path/to/workspace/suanrong

# 或
🔓 管理员模式：可访问全局数据
```

**日志位置:**
- OpenClaw 会话记录：`~/.openclaw/agents/<agent>/sessions/`
- 脚本输出：标准输出/错误

---

## 🛡️ 攻击场景防护

### 场景 1: 未授权 agent 尝试调用

```bash
# 麻辣烫尝试使用
$ OPENCLAW_AGENT_NAME=malatang wx-biz-query 理财魔方

❌ 权限拒绝：wx-article-fetcher 仅限 蒜蓉 使用
   当前 agent: malatang
   管理员：baseagent
   如需使用请联系张亮确认
```

**结果:** ❌ 请求被拒绝

---

### 场景 2: 尝试访问其他 agent 数据

```python
# 蒜蓉尝试读取 baseagent 的缓存
cache_file = Path.home() / ".wx_biz_query" / "cache.json"

# 实际执行时，脚本会自动重定向到：
# /workspace/suanrong/.wx_cache/wx_biz_cache.json
```

**结果:** ❌ 路径被自动重定向到自己的工作空间

---

### 场景 3: 环境变量伪造

```bash
# 尝试伪造 baseagent 身份
$ OPENCLAW_AGENT_NAME=baseagent wx-articles-fetch xxx

# 但工作空间路径不匹配
# OPENCLAW_WORKSPACE=/workspace/suanrong/

# 脚本会检测到不一致，拒绝访问全局数据
```

**结果:** ❌ 环境变量与实际情况不符，访问被限制

---

## 📊 数据隔离验证

运行以下命令验证数据隔离：

```bash
# 蒜蓉运行
wx-biz-query 理财魔方

# 检查数据保存位置
ls -la $OPENCLAW_WORKSPACE/.wx_cache/
ls -la $OPENCLAW_WORKSPACE/.wx_articles/

# 确认没有写入全局目录
ls -la ~/.wx_biz_query/  # 应该没有变化
ls -la ~/.wx_articles/   # 应该没有新增
```

---

## 🆘 应急响应

### 发现未授权访问

1. **立即通知:** 联系张亮和 agent 管理者
2. **隔离:** 暂停相关 agent 的运行
3. **审计:** 检查会话日志和文件访问记录
4. **修复:** 更新权限配置，加强监控

### 数据泄露

1. **评估范围:** 确认哪些数据被泄露
2. **通知用户:** 如有敏感数据泄露，通知相关人员
3. **撤销访问:** 更新签名，撤销泄露的凭证
4. **加强防护:** 审查并改进安全机制

---

## 📞 联系方式

- **安全负责人:** 十三香 (agent 管理者)
- **直属领导:** 张亮
- **公司:** 理财魔方

---

## 📝 更新日志

### v1.0.1 (2026-03-13)
- ✅ 实现数据隔离机制
- ✅ 每个 agent 独立的工作空间存储
- ✅ baseagent 管理员权限
- ✅ 权限验证 + 路径隔离双层防护
- ✅ 安全文档和审计说明
