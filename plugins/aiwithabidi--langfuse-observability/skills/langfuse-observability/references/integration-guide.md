# Langfuse Hub Integration Guide

How to integrate `langfuse_hub.py` into any OpenClaw skill.

## Setup (add to top of your script)

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/skills/langfuse-observability/scripts"))
from langfuse_hub import traced, trace_llm, trace_api, trace_tool, trace_event, score, flush
```

## Examples

### 1. Trace an LLM Call

```python
import time

start = time.time()
# ... make your LLM call ...
response = call_llm(model="claude-sonnet-4", prompt=user_query)
latency = round((time.time() - start) * 1000)

trace_llm(
    model="claude-sonnet-4",
    prompt=user_query,
    completion=response.text,
    input_tokens=response.usage.input,
    output_tokens=response.usage.output,
    latency_ms=latency,
    tags=["my-skill", "chat"],
)
```

Cost is auto-calculated from the model pricing table.

### 2. Trace an API Call

```python
trace_api(
    service="perplexity",
    endpoint="/chat/completions",
    status=200,
    latency_ms=350,
    request_data={"query": "test"},
    response_data={"answer": "result"},
    tags=["search"],
)
```

### 3. Trace a Tool Execution

```python
trace_tool(
    name="memory_engine",
    input_data={"action": "search", "query": "test"},
    output_data={"results": 5},
    duration_ms=120,
)

# With error:
trace_tool(
    name="memory_engine",
    input_data={"action": "add"},
    error="Connection refused",
    duration_ms=50,
)
```

### 4. Custom Events

```python
trace_event("user-login", data={"user": "abidi", "source": "telegram"})
trace_event("rate-limit-hit", data={"service": "openai"}, level="WARNING")
```

### 5. Decorator (auto-traces function calls)

```python
@traced("my-operation")
def process_query(query):
    # ... do work ...
    return result

# Function calls are automatically traced with input/output
process_query("hello world")
```

### 6. Context Manager (block tracing with full control)

```python
with traced("complex-pipeline") as t:
    # Step 1
    data = fetch_data()
    t.event("data-fetched", {"rows": len(data)})
    
    # Step 2: nested LLM call
    t.generation(
        name="summarize",
        model="gpt-5-nano",
        input=str(data),
        output=summary,
        usage={"input": 500, "output": 100, "unit": "TOKENS"},
    )
    
    t.set_output({"summary": summary, "rows": len(data)})
```

### 7. Session Grouping

All traces auto-group by hour (`session-YYYYMMDD-HH`). Override:

```python
trace_llm(model="claude-sonnet-4", prompt="hi", completion="hello",
          session_id="my-custom-session-123")
```

### 8. Scoring Traces

```python
t = trace_llm(model="claude-sonnet-4", prompt="q", completion="a",
              input_tokens=10, output_tokens=20)
score(trace_id=t.id, name="relevance", value=0.95, comment="Highly relevant")
score(trace_id=t.id, name="accuracy", value=0.8)
```

### 9. Always Flush

```python
# At the end of your script (auto-flush on exit, but explicit is safer):
flush()
```

## Best Practices

1. **Always import flush** and call it at script end for short-lived scripts
2. **Use `traced` decorator** for simple functions, context manager for complex flows
3. **Tag consistently** — use skill name as a tag for filtering in dashboard
4. **Don't trace sensitive data** — redact PII from prompts/completions if needed
5. **Never crash** — all functions silently fail if Langfuse is down

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need observability for your AI agents?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
