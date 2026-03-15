---
name: fangcloud_ai
description: "亿方云 (Fangcloud) AI 能力集成 Skill。支持文件管理（列表、上传、下载、分享）、协作邀请、知识库对话 (DeepSeek) 以及智能体交互。当用户需要操作亿方云文件、查询最近文档或创建分享链接时，使用此 Skill。"
---

# Fangcloud AI Skill

此 Skill 允许通过亿方云开放平台 API 执行各类操作。

## 配置说明

Skill 自动从环境变量获取 Token：
- `FANGCLOUD_ADMIN_TOKEN`: 用于 URL 中包含 `admin` 的企业级接口。
- `FANGCLOUD_USER_TOKEN`: 用于普通用户级接口。

## 核心功能与接口参考

详细接口定义请参考 [references/openapi.md](references/openapi.md)。

### 1. 最近使用的文件
- **Endpoint**: `GET /v2/file/recent_items`
- **用法**: 获取当前用户最近操作过的文件列表。**重要：必须携带 `limit` 参数，否则接口可能返回 500 错误。** 例如：`/v2/file/recent_items?limit=20`。

### 2. 搜索文件
- **Endpoint**: `GET /v2/item/search`
- **用法**: 根据关键词搜索文件。参数：`query_words`, `sort_by=modified_at`, `sort_direction=desc`。

### 3. 获取用户信息
- **Endpoint**: `GET /v2/user/info`
- **用法**: 获取当前登录用户的基本信息，用于确认身份。

### 4. 创建分享链接
- **Endpoint**: `POST /v2/share_link/create`
- **用法**: 为指定的文件或文件夹创建分享链接。

### 5. 预览与在线编辑 (URL 构造)
- **预览 URL**: `https://v2.fangcloud.com/desktop/files/recent?preview={file_id}`
- **在线编辑 URL**: `https://v2.fangcloud.com/desktop/files/recent?preview={file_id}&fv=1&online=1`

### 6. 知识库与智能体 (DeepSeek)
- **知识库对话**: `POST /v2/kbase/chatStream` (支持 `gptType: "deepseek"`)
- **智能体对话**: `POST /v2/knowledge/chatStream`
- **智能体列表**: `GET /v2/knowledge/list`

## 常用工作流

### 查找并处理文件
1. 调用 `GET https://open.fangcloud.com/api/v2/item/search` 搜索文件。
2. 根据返回的 `id` 构造预览或编辑 URL。

## 实用场景 (Practical Scenarios)

### 1. 文件搜索下载
**目标**: 根据用户关键词查找文件，并将其下载到本地。
**执行流程**:
1. 调用 `GET /v2/item/search`（参数 `query_words=<关键词>`）查询目标文件的 `file_id`。
2. 调用 `GET /v2/file/{file_id}/download_v2` 或相应下载接口获取文件的真实下载链接。
3. （可选）使用本地工具将获取到的链接内容下载并保存为本地文件。

### 2. 文件夹创建及文件上传到个人空间
**目标**: 在个人空间创建专属文件夹，并将本地文件上传至该目录。
**执行流程**:
1. 调用 `GET /v2/folder/personal_items` 获取个人空间的目录信息，确认目标父文件夹 ID（通常根目录为 `0` 或根据接口返回判断）。
2. 调用 `POST /v2/folder/create`（参数 `name=<文件夹名>`, `parent_id=<个人空间ID>`）创建目标文件夹，并记录返回的 `id`。
3. 调用上传接口（如 `POST /v2/file/upload_v2` 或 `POST /v2/file/upload_by_path`），将本地文件上传到刚创建的文件夹下。

### 3. 文件搜索，创建分享
**目标**: 查找指定文件，并为该文件生成对外分享链接。
**执行流程**:
1. 调用 `GET /v2/item/search` 搜索并获取目标文件的 `file_id`。
2. 调用 `POST /v2/share_link/create`，传入对应的 `file_id`。可根据需求设置必要的权限参数（如提取码、有效期限等）。
3. 提取接口返回的分享 `url` 和密码，并呈现给用户。

### 4. 文件夹搜索创建收集场景 (没有就补全)
**目标**: 查找是否存在指定名称的“收集文件夹”，如果存在则使用该文件夹创建收集任务，如果不存在则自动创建文件夹后再创建收集任务。
**执行流程**:
1. 调用 `GET /v2/item/search`（设置 `type=folder`，传入名称）搜索目标文件夹。
2. 若找到目标文件夹，提取其 `folder_id`；若未找到，调用 `POST /v2/folder/create`（在个人空间或指定目录）创建该文件夹并获取 `folder_id`。
3. 调用 `POST /v2/collection/create`（传入 `target_folder_id`、`name` 等参数）为该文件夹创建公网收集任务。
4. 提取接口返回的收集任务链接（如提取接口返回的收集 URL 或其他标识），提供给用户用于文件收集。后续可通过 `GET /v2/collection/get_files_info` 查询收集状态。

### 5. 云盘文件自动分类与整理 (NEW)
**目标**: 自动识别指定目录中的文件类型，创建分类目录并将文件移动或复制到对应目录中。
**执行流程**:
1. **获取 ID**: 从用户提供的 URL（如 `preview={id}`）或直接提供的 ID 中提取目标文件夹 ID。
2. **读取列表**: 调用 `GET /v2/folder/{id}/children` 获取目录下所有文件列表。
3. **智能分类**: 分析文件后缀或名称（如 `.pdf`、`.docx`、`.xlsx`、`.jpg`），制定分类方案（如“文档”、“图片”、“表格”）。
4. **用户确认**: 向用户展示分类建议，并询问是执行“移动 (Move)”还是“复制 (Copy)”。
5. **执行整理**:
   - 调用 `POST /v2/folder/create` 创建分类子文件夹。
   - 遍历文件，根据用户选择调用 `POST /v2/file/{id}/move` 或 `POST /v2/file/{id}/copy` 将其分配到对应目录。
6. **结果反馈**: 整理完成后通知用户结果。

### 6. 云盘使用周报自动生成 (NEW)
**目标**: 通过分析最近操作的文件，生成用户的使用周报，并提供优化建议。
**执行流程**:
1. **获取数据**: 调用 `GET /v2/file/recent_items?limit=50` 获取最近操作的文件列表（尽可能多抓取）。
2. **时间筛选**: 根据当前时间戳，统计本周（通常为过去 7 天）操作过的文件。
3. **内容分析**: 
   - 提取文件名、类型、修改时间。
   - 使用 AI 总结本周的工作重心（如：“本周主要在处理产研相关的 Excel 文档”）。
   - 统计文件分布（如：修改了 5 个表格，创建了 2 个 PDF）。
4. **生成周报**:
   - **本周回顾**: 总结操作的文件类型、项目相关性。
   - **工作重心**: 自动识别最常操作的文件所属项目。
   - **使用建议**: 根据使用习惯提供建议（如：“建议将本周频繁修改的文档归档到特定项目文件夹”）。
5. **呈现报告**: 将汇总结果以 Markdown 格式呈现。

## 执行工具

可以使用内置的 Python 客户端执行请求：
- **通用客户端**: `python3 scripts/fangcloud_client.py <METHOD> <URL> [DATA_JSON]`
- **智能体对话**: `python3 scripts/chat_agent.py "你的问题" [--agent-id ID] [--type TYPE] [--libs LIBS]`
  - 示例: `python3 scripts/chat_agent.py "你好" --agent-id 3776`
  - 示例: `python3 scripts/chat_agent.py "帮我总结文档" --type AI_LIBRARY --libs 123,456`

- **目录自动整理工具**: `python3 scripts/organize_folder.py [--folder-id ID | --folder-url URL] [--mode move|copy] [--dry-run]`
  - 说明: 按文件后缀自动分类（文档/表格/图片/代码/演示/压缩包/其他），自动创建分类目录并批量移动或复制文件。
  - 示例(先预演): `python3 scripts/organize_folder.py --folder-url "https://v2.fangcloud.com/atlas-web/desktop/files?desktop=%2Fdesktop%2Ffiles%2Ffolder%2F501007507161" --dry-run`
  - 示例(执行移动): `python3 scripts/organize_folder.py --folder-id 501007507161 --mode move`
  - 示例(执行复制): `python3 scripts/organize_folder.py --folder-id 501007507161 --mode copy`

- **目录上传工具**: `python3 scripts/upload_directory.py <local_dir> [--remote-root PATH | --remote-parent-id ID] [--conflict-strategy overwrite|rename] [--include-hidden] [--dry-run]`
  - 说明: 将本地目录递归上传到个人空间，默认会在云端创建同名目录并保持子目录结构；支持二次上传，默认同名走覆盖上传（`overwrite`）；默认不上传隐藏文件/目录（可通过 `--include-hidden` 开启）；支持按云端父目录ID上传（`--remote-parent-id`）。
  - 示例(先预演): `python3 scripts/upload_directory.py ~/dev/workspace/file-check-workspace --dry-run`
  - 示例(上传到个人空间根目录): `python3 scripts/upload_directory.py ~/dev/workspace/file-check-workspace`
  - 示例(上传到指定父路径): `python3 scripts/upload_directory.py ~/dev/workspace/file-check-workspace --remote-root "自动上传测试"`
  - 示例(上传到指定父目录ID): `python3 scripts/upload_directory.py ~/dev/workspace/file-check-workspace --remote-parent-id 501007507161`
  - 示例(改为重命名策略): `python3 scripts/upload_directory.py ~/dev/workspace/file-check-workspace --conflict-strategy rename`
  - 示例(包含隐藏文件): `python3 scripts/upload_directory.py ~/dev/workspace/file-check-workspace --include-hidden`
