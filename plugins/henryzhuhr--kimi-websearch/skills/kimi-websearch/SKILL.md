---
name: kimi-websearch
description: "联网搜索工具。Use When (1)用户需要通过联网获取信息; (2)如果你无法直接回答用户的问题，或者需要更多信息来回答用户的问题。"
---

# Kimi Web Search / Kimi 联网搜索工具

## 依赖与前置条件

- 检查环境变量中是否设置了有效的 API Key，支持 `KIMI_API_KEY` 和 `MOONSHOT_API_KEY` 两个变量。如果没有设置，请登录 `https://platform.moonshot.cn/console/api-keys` 获取 API Key，并将其设置为环境变量。

## 可用脚本

- **`scripts/kimi-web_search.py`** — 联网搜索

## 使用说明

```bash
python3 scripts/kimi-web_search.py --message "<the question you want to ask>"
```

## 执行流程

1. 先把用户请求整理成适合搜索的单条问题，尽量具体，避免模糊描述。
2. 使用命令行传入问题，例如：`python3 scripts/kimi-web_search.py --message "最近有什么AI领域的重大新闻吗？"`。
3. 如需特殊角色设定，再追加 `--system-prompt "..."`。
4. 运行脚本并读取标准输出，最终打印出来的 `choice.message.content` 就是搜索后的回答。
5. 把结果整理后回复给用户，并明确这是基于 Kimi 联网搜索得到的内容。

## 输出要求

- 优先输出整理后的结论，不要把整段原始脚本输出原封不动贴给用户。
- 如果搜索结果明显不完整、存在时效风险，直接说明不足。
- 如果用户要求继续追问同一主题，直接换一个 `--message` 参数重新运行。
