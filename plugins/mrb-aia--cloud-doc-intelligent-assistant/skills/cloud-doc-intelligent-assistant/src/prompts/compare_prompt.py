"""compare_docs skill 使用的 LLM prompt 模板"""

from typing import Optional


COMPARE_SYSTEM_PROMPT = "你是一个云产品技术文档分析专家，擅长对比不同云厂商的产品文档，找出差异点和各自的侧重点。"

COMPARE_USER_TEMPLATE = """请对比以下两份云产品文档，重点关注：{focus}

## 左侧文档
厂商：{left_cloud}
产品：{left_product}
标题：{left_title}

{left_content}

---

## 右侧文档
厂商：{right_cloud}
产品：{right_product}
标题：{right_title}

{right_content}

---

请按以下 JSON 格式输出对比结果（只输出 JSON，不要有其他文字）：

```json
{{
  "comparison": [
    {{
      "dimension": "维度名称",
      "left_status": "支持/不支持/部分支持/未提及",
      "right_status": "支持/不支持/部分支持/未提及",
      "difference": "差异说明"
    }}
  ],
  "summary": "总体对比摘要（200字以内）"
}}
```

对比维度应覆盖：核心功能、参数规格、计费模式、API 接口、使用限制、文档完整性等。"""


def build_compare_prompt(
    left_cloud: str,
    left_product: str,
    left_title: str,
    left_content: str,
    right_cloud: str,
    right_product: str,
    right_title: str,
    right_content: str,
    focus: Optional[str] = None,
    max_content_chars: int = 3000,
) -> tuple[str, str]:
    """构建 compare_docs 的 LLM prompt。

    Returns:
        (system_prompt, user_prompt) 元组
    """
    focus_text = focus or "功能差异、参数规格、使用限制"

    def _truncate(text: str) -> str:
        if len(text) <= max_content_chars:
            return text
        return text[:max_content_chars] + "\n\n... (内容已截断)"

    user_prompt = COMPARE_USER_TEMPLATE.format(
        focus=focus_text,
        left_cloud=left_cloud,
        left_product=left_product,
        left_title=left_title,
        left_content=_truncate(left_content),
        right_cloud=right_cloud,
        right_product=right_product,
        right_title=right_title,
        right_content=_truncate(right_content),
    )
    return COMPARE_SYSTEM_PROMPT, user_prompt
