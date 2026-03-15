---
name: dynatrace-oncall
description: "Dynatrace 生产故障排查与根因分析。当用户提供 Dynatrace 故障链接（Problem URL 或 Trace URL/ID）并要求排查、分析、定位根因时触发。输出结构化故障报告，包含一句话摘要和详细根因分析。"
---

# dynatrace-oncall

收到故障链接后，**先读取 `references/SOP-ROUTER.md`** 判断入口类型，再按对应 SOP 执行排查：

- Problem URL（含 `/problem/`）→ `references/SOP-PROBLEM.md`
- Trace URL 或 Trace ID → `references/SOP-TRACE.md`
- 公共资源（铁律/DQL 模板/报告格式）→ `references/SOP-COMMON.md`

## 环境配置

**首次使用时脚本会交互式询问并保存配置**，无需手动设置环境变量：

- `DT_ENV_URL`：Dynatrace 环境地址（如 `https://qlf23711.apps.dynatrace.com`）
- `DT_TOKEN`：Platform Token（`dt0s16.xxx`，从 Dynatrace 控制台生成）

配置保存在 `scripts/config.json`（权限 600，已加入 `.gitignore`）。

如需覆盖已保存的配置，直接设置同名环境变量即可（环境变量优先级高于 config.json）。

## 执行方式

使用 `scripts/dql.sh`，通过 stdin 传入 DQL：

```bash
# 单行
echo "fetch events, from: now()-7d | filter event.kind == 'DAVIS_PROBLEM' | limit 3" | ./scripts/dql.sh

# 多行（heredoc）
./scripts/dql.sh << 'EOF'
fetch events, from: now()-7d
| filter event.kind == "DAVIS_PROBLEM"
| filter event.id == "{EVENT_ID}"  # 新版：event.id == "-187049689802719993_1773133500000V2"
| # 旧版：display_id == "P-xxx"
| limit 3
EOF
```

**依赖**：`curl`、`jq`（均为系统级工具，无需额外安装）

## 输出规则

排查完成后：

1. 用 `lark-wiki` skill 的 `create-node` 命令在 wiki 创建文档，父节点固定为「Dynatrace 故障排查报告」：
   ```bash
   # space: BIT-Payment统一文档中心 (7541224992629915679)
   # parent: 研发文档 > 后端 > 稳定性治理 > Dynatrace 故障排查报告 (NpI1w6d1yiDcUhkLjCclec71gHc)
   /opt/anaconda3/bin/python3 ~/.openclaw/workspace/skills/lark-wiki/scripts/lark_wiki.py \
     create-node 7541224992629915679 "<故障标题>" --parent NpI1w6d1yiDcUhkLjCclec71gHc
   ```
   拿到 `obj_token` 后，用 Python 直接调用 Lark API 写入 blocks（**禁止用 `write-doc` 命令行或 `feishu_doc` 工具**，两者均有 bug）：
   ```python
   import sys, os, json
   sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/skills/lark-wiki/scripts'))
   import importlib.util
   spec = importlib.util.spec_from_file_location("lark_wiki", os.path.expanduser('~/.openclaw/workspace/skills/lark-wiki/scripts/lark_wiki.py'))
   mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

   def h2(t): return {"block_type": 4, "heading2": {"elements": [{"type": 0, "text_run": {"content": t}}]}}
   def h3(t): return {"block_type": 5, "heading3": {"elements": [{"type": 0, "text_run": {"content": t}}]}}
   def p(t):  return {"block_type": 2, "text":     {"elements": [{"type": 0, "text_run": {"content": t}}]}}

   doc_token = "<obj_token>"
   token = mod.get_token()
   blocks = [h2("一句话摘要"), p("..."), h2("二、故障现象"), p("..."), ...]  # 按报告格式填充
   r = mod.api("POST", f"/docx/v1/documents/{doc_token}/blocks/{doc_token}/children",
               {"children": blocks, "index": -1}, token=token)
   print(r.get("code"))  # 0 = 成功
   ```
   > ⚠️ block_type=2 必须用 `"text"` 字段，**不是** `"paragraph"`（后者导致 1770001 错误）。
   > ⚠️ `feishu_doc` 工具用飞书国内 bot token，写 Lark international 文档会 403，禁止使用。
2. 回复一条消息，内容为：一句话摘要 + wiki 文档链接（`https://bytedance.larkoffice.com/wiki/<node_token>`）。

**报告正文不含一级标题（`#`），从二级标题（`##`）开始。**

报告格式严格遵循 `references/SOP.md` Phase 5 结构。

