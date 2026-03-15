---
name: linkfoxai
description: "调用 LinkFox AI 开放平台全部 API：AI 作图（36 种能力：换模特、抠图、扩图、场景裂变、智能修图、套图、姿势裂变等）和 AI 会话（流式/非流式）。适用场景：(1) AI 作图任务创建与结果轮询，(2) AI 对话/内容生成，(3) 通过 api-call 调用任意开放平台接口，(4) 作图素材连通性测试。"
---

# LinkFoxAI - LinkFox AI 开放平台 Skill

LinkFoxAI 让 OpenClaw 调用 LinkFox AI 开放平台的全部能力：36 种 AI 作图接口（换模特、自动抠图、场景裂变、智能扩图、高清放大、消除笔、智能修图、商品套图、服装套图、姿势裂变等）和 AI 会话接口（流式/非流式对话）。

## 配置

1. **获取凭证**：注册 [紫鸟开放平台](https://open.ziniao.com)，认证开发者并创建 LinkFox 卖家应用，然后在 [linkfox.com/team/api-guide](https://www.linkfox.com/team/api-guide) 将应用绑定到团队，获取 API Key。
2. **环境变量**：`LINKFOXAI_API_KEY`（单一 API Key，配置一个 Key 即可调用全部接口）
3. **自定义 Base URL**（可选）：默认 `https://sbappstoreapi.ziniao.com/openapi-router`。若无固定 IP，设置 `LINKFOXAI_BASE_URL=https://sbappstoreapi-proxy.linkfox.com` 并配置白名单。

## 必须使用 sessions_spawn 调度作图任务

AI 作图任务需要排队和生成时间（通常 10 秒 ~ 5 分钟，**极端情况下可能因服务端超时或队列积压导致单个任务耗时超过 30 分钟**）。**务必通过 `sessions_spawn` 将作图任务派发到子会话**，让主会话保持响应。脚本的 `--wait` 参数会自动轮询直到出结果。

### 超时处理策略（AI 自行判断）

当作图任务超时（`--timeout` 耗尽仍未返回结果）时，AI 应根据具体情况自主选择以下策略，无需等待用户指令：

1. **延长轮询时间**：将 `--timeout` 增大到 1800（30 分钟），`--interval` 建议 10~30 秒，适用于重要任务或用户明确愿意等待的场景。
2. **告知用户并继续后台等待**：向用户说明任务仍在生成中，预估剩余时间，并在后台子会话中继续轮询；完成后主动汇报结果。
3. **任务分拆重试**：若任务参数含多图（如 `--output-num 4`），可拆分为多个单图任务并行提交，降低单个任务超时概率。
4. **放弃并报错**：仅当用户明确要求快速返回、或超时时间已大幅超出合理范围（> 40 分钟）时，才终止轮询并告知用户稍后手动查询任务 ID。

> 默认建议：将 `sessions_spawn` 的 `runTimeoutSeconds` 设为 **1800**，`--timeout` 设为 **1700**，以覆盖绝大多数超时场景。仅在明确知道该类型任务通常很快时才缩小超时值。

### 标准调度模板

```
sessions_spawn:
  task: |
    Run: <skill>/scripts/linkfoxai.py change-model --wait --timeout 1700 \
         --image-url "<模特原图>" --head-url "<头部图>" --output-num 4
    解析输出 JSON，提取 resultList 中的图片 URL 汇报给用户。
    如果 status=4（失败），报告 errorMsg。
    如果超时仍未完成，告知用户任务 ID 以便后续手动查询。
  label: "LinkFoxAI: AI 换模特"
  mode: "run"
  runTimeoutSeconds: 1800
  cleanup: "keep"
```

### 并行调度多个独立任务

```
# 子任务 1
sessions_spawn:
  task: "Run: <skill>/scripts/linkfoxai.py cutout --wait --timeout 1700 --image-url '<url>' --sub-type 1 ..."
  label: "LinkFoxAI: 自动抠图"
  mode: "run"
  runTimeoutSeconds: 1800

# 子任务 2
sessions_spawn:
  task: "Run: <skill>/scripts/linkfoxai.py scene-fission --wait --timeout 1700 --image-url '<url>' ..."
  label: "LinkFoxAI: 场景裂变"
  mode: "run"
  runTimeoutSeconds: 1800
```

### 通用接口调用（api-call）

对于脚本没有专属命令的接口（如 AI 穿衣、商品替换、饰品文字等），使用 `api-call` 传入路径和 JSON body：

```
sessions_spawn:
  task: |
    Run: <skill>/scripts/linkfoxai.py api-call \
         --path /linkfox-ai/image/v2/make/fittingRoom \
         --body '{"upperOriginUrl":"<上衣图>","modelImageUrl":"<模特图>","outputNum":2}'
    获取返回的 data.id，然后运行：
    <skill>/scripts/linkfoxai.py poll --id <task_id> --timeout 1700
    解析结果汇报给用户。如果超时仍未完成，告知用户任务 ID 以便后续手动查询。
  label: "LinkFoxAI: AI 穿衣"
  mode: "run"
  runTimeoutSeconds: 1800
```

## 脚本命令一览

### 基础命令

| 命令 | 说明 |
|------|------|
| `material-list --type <1-10>` | 作图素材列表（可用于连通性测试） |
| `upload-base64 --file <路径>` | base64 上传图片，返回 viewUrl |
| `make-info --id <任务ID>` | 查询作图结果（单次） |
| `poll --id <任务ID> [--interval 3] [--timeout 300]` | 轮询作图结果直到成功/失败 |
| `refresh --id <图片ID> [--format jpg]` | 刷新结果图片地址（注意是图片 ID，非任务 ID） |
| `chat --content "内容" [--model 1]` | AI 对话。model: 1=gpt-3.5-turbo, 9=gpt-4o |
| `api-call --path <路径> --body '<JSON>'` | 通用 API 调用，可调任意开放平台接口 |

### 作图快捷命令（均支持 `--wait`）

| 命令 | 说明 |
|------|------|
| `change-model --image-url <url> --head-url <url> [--scene-url <url>] [--output-num 1-4]` | AI 换模特 |
| `cutout --image-url <url> --sub-type <1/2/3/9/12/13> [--cloth-class tops,coat,...]` | 自动抠图 |
| `scene-fission --image-url <url> [--strength 0.5] [--prompt "描述"] [--provider SCENE_FISSION_REALISTIC]` | 场景裂变 |
| `expand-image --image-url <url> --width 1024 --height 1024 [--prompt "描述"]` | 智能扩图 |
| `super-resolution --image-url <url> --magnification 2 [--enhance]` | 图片高清放大 |
| `image-edit --image-url <url> --prompt "描述" [--pro] [--template 白底图]` | 智能修图 |
| `erase --image-url <url> --mask-url <url>` | 消除笔 |

所有作图快捷命令均支持 `--wait [--timeout 300] [--interval 3]`，提交任务后自动轮询直到完成。

### 其他能力（通过 api-call 调用）

以下能力通过 `api-call --path <路径> --body '<JSON>'` 调用，接口详情见 `references/image-make.md`：

| 能力 | 路径 |
|------|------|
| AI 换模特 2.0 | `/linkfox-ai/image/v2/make/changeModelFixed` |
| 模特换场景 | `/linkfox-ai/image/v2/make/modelChangeScene` |
| AI 穿衣-上下装 | `/linkfox-ai/image/v2/make/fittingRoom` |
| AI 穿衣-连体衣 | `/linkfox-ai/image/v2/make/fittingRoomSuit` |
| AI 穿戴 | `/linkfox-ai/image/v2/make/intelligentWear` |
| 商品替换 | `/linkfox-ai/image/v2/make/shopReplace` |
| 场景图生成 | `/linkfox-ai/image/v2/make/aiDraw` |
| 相似图裂变 | `/linkfox-ai/image/v2/make/imageToImage` |
| 精细抠图-创建 | `/linkfox-ai/v2/process/result/interactCutout/create` |
| 精细抠图-结果 | `/linkfox-ai/v2/process/result/interactCutout/info` |
| 图片翻译 | `/linkfox-ai/image/v3/make/imageTransl` |
| 手部修复 | `/linkfox-ai/image/v2/make/handRepair` |
| 局部重绘 | `/linkfox-ai/image/v2/make/areaRepair` |
| 印花提取 | `/linkfox-ai/image/v2/make/printExtract` |
| 手持商品 | `/linkfox-ai/image/v2/make/handHeld` |
| 饰品文字 | `/linkfox-ai/image/v2/make/linkedWord` |
| 商品精修 | `/linkfox-ai/image/v2/make/productRepair` |
| 图片获取描述词-创建 | `/linkfox-ai/v2/process/result/imageToPrompt/create` |
| 图片获取描述词-结果 | `/linkfox-ai/v2/process/result/imageToPrompt/info` |
| 智能修图-多图 | `/linkfox-ai/image/v2/make/multiImageFusion` |
| 商品套图 | `/linkfox-ai/image/v2/make/productMarketMaterialV2` |
| 服装套图 | `/linkfox-ai/image/v2/make/wearCollection` |
| 姿势裂变 | `/linkfox-ai/image/v2/make/modelPoseFission` |

## 连通性测试

使用作图素材接口验证凭证和网络是否正常（无需上传图片）：

```bash
<skill>/scripts/linkfoxai.py material-list --type 1
```

或对 OpenClaw 说：「用 LinkFoxAI 拉取作图素材列表」。

## 错误处理

- 错误码（如 ERR_FORBIDDEN、ERR_NOT_HAVE_TEAM_PRIVILEGE、TEAM_PERMISSION_EXPIRE）见 `references/open-platform.md`。
- 需先将应用绑定团队且团队已开通套餐。
- 作图任务失败时 `status=4`，检查 `errorCode` 和 `errorMsg`。
- 常见问题：参数校验失败（ERR_FILED_VALIDATE）、图片审核不通过（ERR_IMAGE_MAKE_AUDIT）、点数不足（ERR_IMAGE_MAKE_WILL_OUT）。

## 参考文档

- `references/open-platform.md` — 接入流程、API 基础地址、错误码
- `references/image-make.md` — 全部 36 个作图接口完整参数与注意事项
- `references/ai-chat.md` — AI 会话接口完整参数、流式/非流式响应、模板用法

## 示例

1. **连通性**：「用 LinkFoxAI 拉取作图素材列表」→ 脚本执行 `material-list --type 1`
2. **AI 换模特**：「用 LinkFoxAI 做一次 AI 换模特，原图 xxx，头部图 xxx，出 4 张」→ `change-model --wait --output-num 4`
3. **自动抠图**：「用 LinkFoxAI 把这张图抠图」→ `cutout --wait --sub-type 1`
4. **智能修图**：「用 LinkFoxAI 把这张图改成白底图」→ `image-edit --wait --prompt "白底图" --template 白底图`
5. **通用调用**：「用 LinkFoxAI 做 AI 穿衣」→ `api-call --path /linkfox-ai/image/v2/make/fittingRoom --body '{...}'` + `poll --id <id>`
6. **AI 对话**：「用 LinkFoxAI 发起一次 AI 对话：你好」→ `chat --content "你好"`
