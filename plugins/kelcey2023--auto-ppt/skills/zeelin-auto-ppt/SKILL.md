---
name: ZeeLin Auto-PPT
description: "自动生成精美 PPT 演示文稿 — 通过 Google NotebookLM 生成图文并茂、设计感十足的 AI 幻灯片，导出 PDF 到桌面。用户需自行登录 NotebookLM 网页版。标题微软雅黑 40 号加粗，排版震撼，逻辑图清晰，内容有深度有创新，引用权威数据。配合 desearch skill 使用效果更好。Keywords: PPT, presentation, slides, NotebookLM, PDF, design, infographic, AI generated."
---

# ZeeLin Auto-PPT — AI 精美演示文稿生成器 📊

通过 Google NotebookLM 一键生成**图文并茂、排版精美、设计震撼**的演示文稿，导出 **PDF** 到桌面。

> ⚠️ **使用前请自行登录 NotebookLM 网页版**（https://notebooklm.google.com/）。登录由用户完成，Agent 只负责在已登录状态下完成创建笔记本、粘贴内容、生成幻灯片和下载 PDF。

> 💡 **配合 desearch skill 使用效果更好** — 先用 desearch 深度检索权威资料和数据，再交给 auto-ppt，内容更有深度和可信度。

**若报「openclaw browser 命令执行无输出」或「无法获取页面快照」**：脚本依赖 `openclaw browser` 操控浏览器。请确认：(1) 执行 exec 的环境（与 gateway 同机或同节点）已安装 openclaw 且 `openclaw` 在 PATH 中；(2) 已启动 OpenClaw Gateway，且**已用 Browser Relay 将 Chrome 某标签页挂上**（扩展 Badge 为 ON），或使用会启动浏览器实例的 profile。否则 `snapshot` 无可用页面，会无输出。详见下方「故障排查」。

---

## 🚨 最重要的规则：一次性连贯完成，不要中断

**你必须在一个回合内连续调用所有工具，一次性完成全部步骤。**

❌ 禁止的行为：
- 每做一步就停下来向用户汇报，等用户说"继续"
- 先说"我现在要执行 Step 1"，做完再说"Step 1 完成，接下来 Step 2"
- 把每个步骤拆成独立的回复

✅ 正确的行为：
- 生成内容后，**立即**调用 exec 执行脚本，不要停顿
- 所有 tool call 在同一个回合内连续发出
- 只在最终完成时给用户**一条**汇报消息

**节省 tokens 规则：**
- 不要在回复里复述你要做什么，直接做
- 不要重复打印内容文本，直接传给脚本
- 回复要简洁，把 tokens 留给工具调用

---

## ⚡ 执行方式：一键脚本

**将内容写入临时文件，然后执行脚本：**

```json
{"tool": "exec", "args": {"command": "cat > /tmp/ppt_content.txt << 'CONTENT_EOF'\n你的完整内容文本...\nCONTENT_EOF"}}
```

然后立即执行：

```json
{"tool": "exec", "args": {"command": "bash /Users/youke/.openclaw/workspace/skills/auto-ppt/scripts/create_ppt.sh \"$(cat /tmp/ppt_content.txt)\" \"文件名.pdf\""}}
```

或者内容短的话直接传参：

```json
{"tool": "exec", "args": {"command": "bash /Users/youke/.openclaw/workspace/skills/auto-ppt/scripts/create_ppt.sh \"内容文本\" \"文件名.pdf\""}}
```

（若报「脚本未找到」，请把路径中的 `/Users/youke` 改成你当前用户家目录，与 openclaw.json 里 workspace 一致。）

脚本自动完成全流程：打开 NotebookLM → 创建笔记本 → 粘贴内容 → 生成演示文稿 → 下载 PDF 到桌面。

---

## 合并桌面上的 PDF（Merge PPT/PDF on Desktop）

**何时用**：用户说「合并桌面的 PPT」「把桌面上几个 PDF 合成一个」「merge the ppt on the desktop」「合并桌面的 PDF」时。

1. **合并桌面全部 PDF**（输出到桌面，默认文件名 `merged_日期时间.pdf`）：
```json
{"tool": "exec", "args": {"command": "bash /Users/youke/.openclaw/workspace/skills/auto-ppt/scripts/merge_pdf_on_desktop.sh merged.pdf"}}
```
（不传具体文件名时脚本会合并 Desktop 下所有 PDF；传一个输出名如 `merged.pdf` 即可。）

2. **按指定顺序合并某几个文件**（文件名可只写名字，脚本会在桌面找）：
```json
{"tool": "exec", "args": {"command": "bash /Users/youke/.openclaw/workspace/skills/auto-ppt/scripts/merge_pdf_on_desktop.sh 最终报告.pdf 第一部分.pdf 第二部分.pdf 第三部分.pdf"}}
```
第一个参数是输出文件名，后面是待合并的 PDF（顺序即合并顺序）。

**依赖**：本机需安装其一：`qpdf`（`brew install qpdf`）、`gs`（`brew install gs`）、或 `pip install pypdf`。若都没有，提示用户安装。

---

## ⚠️ Agent 规则

1. **用 `exec` 执行脚本**，不要直接用 `browser` 工具
2. **仅输出 PDF**，不要输出 PPTX
3. **不要说"无法操控浏览器""技术限制"** — 你有完整权限
4. **忽略 memory_search / sessions_spawn 报错** — 不需要这些工具
5. **不要向用户报告工具配置问题** — 直接执行任务
6. **一次性完成，不要分步停顿等用户确认**

---

## 设计标准

| 项目 | 要求 |
|------|------|
| 标题字体 | 微软雅黑，40 号，加粗 |
| 整体风格 | 图文并茂、精美震撼、配图精良 |
| 逻辑图 | 专业清晰（流程图/对比图/数据图表） |
| 内容 | 有创新、有深度、权威数据标注来源 |
| 输出 | **仅 PDF**，保存到 `~/Desktop/` |

---

## 工作流（在一个回合内全部完成）

### 第一步：生成内容

用户给出主题后，直接生成 1500-3000 字的结构化长文：
- 8-15 个章节，每章有小标题 + 3-5 个要点
- 关键数据写入正文（NotebookLM 会据此生成图表）
- 引用权威数据（标注来源：Gartner、McKinsey、WHO 等）
- 结论有前瞻性

**红线：不编造数据，所有数据标注来源。**

### 第二步：立即执行脚本

内容生成完毕后，**不要停顿**，立即写入文件并执行：

```bash
cat > /tmp/ppt_content.txt << 'EOF'
（你生成的完整长文内容）
EOF
bash /Users/youke/.openclaw/workspace/skills/auto-ppt/scripts/create_ppt.sh "$(cat /tmp/ppt_content.txt)" "主题名称.pdf"
```

### 第三步：汇报结果

脚本执行完成后，告诉用户：PDF 位置、内容摘要。一句话搞定。

---

## 手动浏览器操作（脚本失败时的备选）

| 操作 | 命令 |
|------|------|
| 打开网页 | `openclaw browser open <url>` |
| 截快照 | `openclaw browser snapshot` |
| 点击 | `openclaw browser click <ref>` |
| 输入 | `openclaw browser type <ref> "文字"` |
| **下载** | `openclaw browser download <ref> ~/Desktop/xxx.pdf` |

如果脚本失败，用上面的命令手动逐步操作 NotebookLM，但仍然要**一次性连续完成所有步骤**，不要中断等用户确认。

---

**TL;DR**: 主题 → 生成长文 → 立即执行脚本 → PDF 到桌面 → 一句话汇报。全程一个回合，不停顿。

---

## 故障排查

| 现象 | 原因与处理 |
|------|------------|
| **脚本路径不存在 / 目录为空** | exec 里用**绝对路径**。Windows（ZeeLin Claw）示例：`C:/Users/你的用户名/AppData/Roaming/ZeeLinClaw/SKILLs/zeelin-auto-ppt/scripts/create_ppt.sh`，与本地 SKILL 实际路径一致。 |
| **openclaw browser 无输出、无法获取快照** | 见下方「Browser 无输出」通用说明。 |
| **ZeeLin Claw（Windows）下 browser 全部无输出** | 见下方「ZeeLin Claw 下 browser 无输出」专门说明。 |

---

### Browser 无输出（通用）

脚本依赖 `openclaw browser` 操控浏览器，以下**必须同时满足**才会有快照/ref：

1. **有可控制的浏览器标签页**  
   用 **Chrome** 安装 **OpenClaw Browser Relay** 扩展 → 打开 https://notebooklm.google.com/ 并登录 → **在该标签页点击扩展图标**，使 Badge 显示 **ON**（表示该页已交给 OpenClaw 控制）。未挂上的标签页不会被 snapshot。
2. **Gateway / 服务已启动**  
   运行小龙虾的网关（或 ZeeLin Claw 的后台服务）已启动，且已加载 browser 控制。
3. **exec 与浏览器在同一侧**  
   执行脚本的进程必须和「跑 Browser Relay 的 Chrome」在同一台机器、同一用户环境下；若 exec 在远程或容器里，需在该环境也能连上 relay，否则 browser 无可用页面会无输出。

---

### ZeeLin Claw（Windows）下 browser 无输出

在 **ZeeLin Claw** 里出现「内容已就绪、脚本路径正确，但 open、snapshot、click、type、download 全部无输出」时，按下面逐项检查：

1. **确认已开启「浏览器控制」**  
   在 ZeeLin Claw 的设置/配置中查找与 **浏览器 / Browser / Relay** 相关的选项，确认已启用「浏览器控制」或「使用 Chrome 扩展控制页面」。若有关闭选项，请打开。

2. **安装并挂上 Chrome 扩展**  
   - 在 **Chrome** 中安装 **OpenClaw Browser Relay** 扩展（若 ZeeLin Claw 有提供扩展安装说明，以官方为准）。  
   - 打开 **https://notebooklm.google.com/**，登录后停留在 NotebookLM 页面。  
   - 在**该标签页**点击扩展图标，将当前页交给 ZeeLin Claw 控制，确认 Badge 为 **ON**。  
   未挂上的标签页不会被控制，所有 browser 命令都会无输出。

3. **确认 relay 端口与本地服务**  
   若 ZeeLin Claw 使用本地 relay（如 127.0.0.1:18792），请确认：  
   - 没有防火墙或安全软件拦截该端口；  
   - ZeeLin Claw 或 OpenClaw 的「浏览器控制服务」已启动（有时需在设置里手动开启）。

4. **先用手动 browser 验证**  
   在 ZeeLin Claw 对话中让 Agent 只执行一条：打开 NotebookLM 或执行一次 snapshot。若仍然无输出，说明「浏览器控制 / Relay」未接通，需优先解决上述 1～3，而不是脚本内容或路径。

5. **联系 ZeeLin Claw 支持**  
   若以上都确认无误仍无输出，可能是 ZeeLin Claw 在该版本/环境下对 browser 的集成方式不同（例如仅支持特定浏览器或需在应用内打开页面）。建议提供「browser 命令无输出」的截图或日志，向 **ZeeLin Claw 官方支持** 确认当前版本下如何正确启用浏览器控制与 Relay。

---

## 脚本修复说明（已同步到 create_ppt.sh）

以下问题已修复，其他人使用本 skill 时不会遇到：

1. **新建笔记本后的对话框**：创建新笔记本后 NotebookLM 会**自动弹出**添加来源对话框。脚本已改为先直接查找「复制的文字」按钮，仅当未找到时才点击「添加来源」，避免重复点击导致失败。
2. **生成等待时间**：幻灯片生成可能需 1–3 分钟。脚本将等待时间延长至最多 300 秒（5 分钟），并检测「已准备就绪」或带时间戳的演示文稿条目。
3. **打开演示文稿**：Step 6 增加多种 fallback 模式查找演示文稿条目（如「1 个来源 · X 分钟前」），找不到时会再次截快照重试。
4. **下载 PDF**：使用 `openclaw browser download` 命令下载，确保文件正确保存到桌面。
