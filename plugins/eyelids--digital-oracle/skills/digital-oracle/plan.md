# Oracle Service - 实现方案

## 概述
把 Digital Oracle 做成 Web 服务，让没有 Agent 的朋友也能用。
用 OpenRouter (Sonnet 4.6) 驱动一个 Agent，自动选择数据源、拉取数据、生成分析报告。

## 技术栈
- **后端**: Python + FastAPI
- **LLM**: OpenRouter (`anthropic/claude-sonnet-4-6`)
- **Agent**: 自定义 tool-use 循环（不依赖外部 agent 框架）
- **前端**: 纯 HTML/CSS/JS（无构建步骤）
- **数据层**: 直接复用 digital_oracle 包（vendor 方式拷贝进来）

## 架构
```
用户浏览器 → FastAPI (SSE) → Agent Loop → OpenRouter (Sonnet 4.6)
                                  ↕
                          digital_oracle (12个数据源)
```

## Repo 结构
```
oracle-service/              (GitHub private repo)
├── .gitignore
├── .env                     (不提交，含 OPENROUTER_API_KEY)
├── .env.example
├── README.md
├── pyproject.toml           (依赖: fastapi, uvicorn, httpx)
├── digital_oracle/          (从原 repo 拷贝)
│   ├── __init__.py
│   ├── concurrent.py
│   ├── http.py
│   ├── providers/
│   └── ...
├── app/
│   ├── __init__.py
│   ├── main.py              (FastAPI 入口，路由，静态文件)
│   ├── agent.py             (Agent 循环: prompt → tool calls → execute → respond)
│   ├── tools.py             (把 digital_oracle providers 包装成 tool 定义)
│   └── config.py            (配置: OpenRouter URL, API key, model)
└── static/
    ├── index.html           (聊天界面)
    ├── style.css
    └── app.js               (SSE 处理，Markdown 渲染)
```

## 核心实现

### 1. Tool 定义 (app/tools.py)
把 digital_oracle 的 14 个核心方法包装成 OpenAI function calling 格式：
- `polymarket_search` - 预测市场事件搜索
- `polymarket_orderbook` - 订单簿深度
- `kalshi_markets` - 二元合约
- `stooq_price_history` - 价格历史（股票/商品/汇率）
- `deribit_futures_curve` - 加密货币期货曲线
- `deribit_option_chain` - 加密货币期权链
- `treasury_yield_curve` - 美国国债收益率曲线
- `yfinance_options` - 美股期权链 + Greeks
- `web_search` - DuckDuckGo 搜索
- `cftc_positioning` - CFTC 持仓报告
- `coingecko_prices` - 加密货币价格
- `edgar_insider_trades` - SEC 内部人交易
- `bis_policy_rates` - 央行利率
- `worldbank_indicator` - 宏观经济指标

每个 tool 有 JSON Schema 参数定义 + 执行函数。

### 2. Agent 循环 (app/agent.py)
```python
async def run_agent(question: str) -> AsyncGenerator[str, None]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},  # 含 SKILL.md 方法论
        {"role": "user", "content": question}
    ]

    while True:
        response = await call_openrouter(messages, tools=TOOL_DEFINITIONS)

        if response has tool_calls:
            # 并行执行所有 tool calls
            results = await execute_tools(response.tool_calls)
            messages.append(assistant_message)
            messages.append(tool_results)
            continue
        else:
            # 最终回答，流式输出
            async for chunk in stream_response(messages):
                yield chunk
            break
```

### 3. System Prompt
包含 SKILL.md 的核心方法论（5步分析法），指导 Agent：
1. 理解问题 → 分解变量
2. 选择 3+ 独立信号源
3. 并行拉取数据（使用提供的 tools）
4. 矛盾分析（不同信号的冲突）
5. 输出结构化报告（概率估计 + 信号一致性评估）

### 4. FastAPI 服务 (app/main.py)
- `GET /` → 静态聊天页面
- `POST /api/chat` → SSE 流式响应
  - 接收: `{"question": "..."}`
  - 返回: `text/event-stream`，每个 event 包含一段文本 chunk

### 5. 前端 (static/)
- 简洁的聊天界面，类似 ChatGPT 风格
- 输入框 + 发送按钮
- 流式显示回复（Markdown 渲染）
- 显示 Agent 正在调用哪些工具（进度指示）

## 实施步骤
1. 创建 GitHub private repo `oracle-service`
2. 初始化项目结构 + pyproject.toml
3. 拷贝 digital_oracle 包
4. 实现 app/config.py（配置管理）
5. 实现 app/tools.py（tool 定义 + 执行）
6. 实现 app/agent.py（agent 循环）
7. 实现 app/main.py（FastAPI 路由）
8. 实现前端 static/（聊天界面）
9. 本地测试
