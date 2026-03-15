---
name: case-analyzer
description: "Analyze Pexo video creation cases from Langfuse traces. Fetches traces, identifies agent behavior issues, generates a visual QA dashboard with all media assets and prompts, and auto-uploads to the strategy-optimizer backend. Use when the user asks to analyze a case, review a conversation ID, or debug a Langfuse trace."
---

# Case Analyzer

Workflow: Langfuse traces → 分析 → **用户确认方案** → 执行改动 → QA 看板 → 上传。

## Prerequisites

Environment variables (already configured in shell profile):
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`
- `PEXO_ADMIN_TOKEN` (JWT for admin.pexo.ai — obtain from browser DevTools if expired)

Skill root: `.cursor/skills/case-analyzer` (relative to project root)

## Workflow

### Phase A: 分析（自动执行，无需确认）

#### Step 1: Fetch Traces

```bash
python3 .cursor/skills/case-analyzer/scripts/fetch-case.py \
  --conversation-id <CASE_ID> \
  --output-dir analysis/langfuse-data
```

Output: `analysis/langfuse-data/cases/<CASE_ID>/trace-*.json`

#### Step 2: Analyze Traces

Read each trace JSON. For every trace, extract:

1. **Timeline entry**: timestamp, latency, user input summary, agent action summary, version label
2. **Tool calls**: model used, parameters, success/failure, output paths
3. **Problems**: any behavior that caused user friction, wasted tokens, or produced wrong output

Organize findings into the **analysis report** (markdown):

```
analysis/<CASE_ID>_<duration>_<slug>.md
```

Naming convention: `<conversation_id>_<duration>_<hyphenated-problem-summary>.md`

**Analysis report structure** (follow existing reports in `analysis/` for style):
- Header: conversation ID, timestamps, video spec, user ID, iteration count
- Session overview table (trace × time × input × action × version)
- Problem sections: phenomenon → root cause → agent response → attribution (model vs skill)
- Recommendations: specific skill file + rule changes

#### Step 3: Extract Media Assets

```bash
python3 .cursor/skills/case-analyzer/scripts/extract-assets.py \
  --case-dir analysis/langfuse-data/cases/<CASE_ID>
```

Output:
- `analysis/langfuse-data/cases/<CASE_ID>/assets.json` — metadata (name, type, prompt, url, model)
- `analysis/langfuse-data/cases/<CASE_ID>/media/` — downloaded files (images, videos, audio)

### ⏸ Phase B: 方案确认（等用户确认后再继续）

分析完成后，向用户呈报：

1. **问题清单**：每个问题一句话总结 + 严重程度（P1/P2/P3）
2. **修改方案**：每个问题对应的具体 skill 修改方案，格式：
   - 目标文件（如 `creative-skill/SKILL.md`）
   - 修改位置（哪条规则 / 哪个 section）
   - 改动内容（加什么规则、改什么逻辑）
   - 为什么这么改（一句话根因归因）
3. **是否有新增规则 vs 修改现有规则**：明确区分

**等用户确认后再进入 Phase C。** 用户可能会：
- 全部同意 → 进入 Phase C
- 修改部分方案 → 按用户意见调整后再确认
- 否决部分方案 → 跳过该项
- 追加新问题 → 补充分析后重新确认

### Phase C: 执行改动 + 上线（用户确认后自动执行）

#### Step 4: Apply Skill Modifications

按用户确认的方案，逐文件执行修改。改完每个文件后简要说明改了什么。

#### Step 5: Generate QA Dashboard

Build a self-contained HTML dashboard at:

```
analysis/langfuse-data/cases/<CASE_ID>/qa-report.html
```

Use the CSS template at `templates/dashboard-styles.css`. The dashboard must include:

1. **Header**: case ID, video spec, date, one-line problem summary
2. **Stats bar**: problem count, skill changes, iteration count, wasted time, total time
3. **Problem cards**: each problem with phenomenon → root cause → fix flow chain
4. **Iteration timeline**: version-by-version progression with error/success/warn markers
5. **Skill modifications**: per-file cards listing what was added/changed and why
6. **Media gallery**: every generated asset (image/video/audio) embedded with its prompt, model name, and generation round label
7. **File index**: links to analysis report, skill files, trace data

**Media path rule**: all `src` attributes must use relative paths (`media/filename.ext`), not absolute or remote URLs.

#### Step 6: Package & Upload

```bash
.cursor/skills/case-analyzer/scripts/upload-package.sh \
  <CASE_ID> \
  analysis/langfuse-data/cases/<CASE_ID>
```

This zips the directory (qa-report.html + media/) and uploads via:

```
POST https://admin.pexo.ai/api/strategy-packages
Content-Type: multipart/form-data

Fields:
  sourceType = "zip"
  name       = <CASE_ID>
  entryFile  = <CASE_ID>/qa-report.html
  archive    = <zip file>
```

After upload, report the preview URL to the user:
`https://admin.pexo.ai/api/strategy-packages/<id>/preview/<CASE_ID>/qa-report.html`

#### Step 7: Update QA Changelog

Append a summary to `skills-kling/QA-CHANGELOG.md` following the existing case entry format (see Case 24 as reference).

## Key Decisions

- **方案必须用户确认**：Phase B 是强制审批门禁，不能跳过。分析可以自动做，但改动必须用户看过并同意后才执行。
- **Dashboard must be self-contained**: no external CDN, no remote fonts, no JS frameworks. Pure HTML + inline CSS.
- **Media must be local**: download all assets to `media/` and reference via relative paths. Signed OSS URLs expire — local copies are permanent.
- **Upload is automatic after approval**: Phase C 中的上传不再需要额外确认。用户已在 Phase B 确认过方案，执行即上传。
- **Analysis report is separate from dashboard**: the markdown report in `analysis/` is the detailed written analysis. The dashboard is the visual summary. Both are produced.

## Trace JSON Structure

Langfuse trace JSON has two observation formats for tool calls:

**Format 1 (most common)**: Observations with `name: "tools"`, args nested in `input.tool_call`:

```
observation.input = {
  "__type": "tool_call_with_context",
  "tool_call": {
    "name": "video_generate",       ← actual tool name
    "args": { ... parameters ... }  ← actual arguments
  }
}
```

**Format 2**: Observations with `type: "TOOL"`, tool name in `observation.name`, args directly in `input`:

```
observation.name = "video_generate"
observation.type = "TOOL"
observation.input = { ... parameters ... }
```

The extract-assets script handles both formats automatically.

**Tool name aliases** (some tools have prefixed names):
- `video-editor__execute_edit_video` → `execute_edit_video`
- `videoagent-image-studio__image_generate` → `image_generate`
- `videoagent-audio-studio__tts_generate` → `tts_generate`
- `videoagent-audio-studio__music_generate` → `music_generate`

Asset URLs appear in:
- `execute_edit_video` input → `edit_spec.clips[].url` and `edit_spec.audio_tracks[].source` (signed OSS URLs)
- `video_generate` input → `image_list[].image_url` (keyframe reference URLs)
- Workspace paths (`/workspace/assets/...`) are internal and not directly downloadable

## MCP Server（跨 agent 使用）

本 skill 提供 MCP server，任何支持 MCP 的 agent 都可以直接调用。

### 启动方式

```bash
uv run --script .cursor/skills/case-analyzer/mcp-server.py
```

### MCP 客户端配置

在 Cursor、Claude Desktop 或其他 MCP 客户端的配置中加入：

```json
{
  "case-analyzer": {
    "command": "uv",
    "args": ["run", "--script", "<项目根目录>/.cursor/skills/case-analyzer/mcp-server.py"]
  }
}
```

### 暴露的 tools

| Tool | 说明 |
|------|------|
| `fetch_traces` | 拉取 Langfuse traces（参数：`conversation_id`） |
| `extract_assets` | 从 traces 中提取素材元数据 + 下载媒体文件（参数：`case_dir`） |
| `upload_package` | 打包 dashboard + 媒体上传到 admin 后台（参数：`conversation_id`, `dashboard_dir`） |
| `list_cases` | 列出所有已分析的 case 及其状态 |

任何 agent 只需调用这 4 个 tool 即可完成「拉数据 → 提素材 → 上传」的自动化流程。分析和 dashboard 生成仍由 agent 自身完成（依赖 LLM 理解 trace 内容）。

## Token Refresh

If upload returns 401:
1. Tell user: "Admin token 过期了，请在 admin.pexo.ai 页面 DevTools → Network 中复制 Authorization header 的 Bearer token"
2. User provides token
3. Set `PEXO_ADMIN_TOKEN` and retry
