# OpenClaw 接入说明

OpenClaw 和 `DocAssistant` 之间的接入方式。

## 接入方式

```python
from src.skills import DocAssistant

assistant = DocAssistant(config_path="config.yaml")

# 直接调用
result = assistant.fetch_doc(cloud="aliyun", product="vpc")
result = assistant.check_changes(cloud="tencent", product="私有网络", days=7)
result = assistant.compare_docs(
    left={"cloud": "aliyun", "product": "vpc"},
    right={"cloud": "tencent", "product": "私有网络"},
    focus="能力差异"
)
result = assistant.run_monitor(
    clouds=["aliyun", "tencent"],
    products=["vpc"],
    send_notification=True
)
```

## CLI 方式

```bash
cloud-doc-monitor list-skills
cloud-doc-monitor run fetch_doc '{"cloud": "aliyun", "product": "vpc"}'
cloud-doc-monitor run check_changes '{"cloud": "aliyun", "product": "vpc", "days": 7}'
```

## 返回结构

所有 skill 返回统一的 `SkillResponse`：

```json
{
  "machine": { ... },
  "human": { "summary_text": "..." },
  "error": null
}
```

`machine` 供 OpenClaw 程序读取，`human` 供人类阅读。
