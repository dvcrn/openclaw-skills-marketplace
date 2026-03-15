---
name: trade-code-analyzer
description: "智能分析交易维度前端代码，自动逆向推导业务需求，构建可复用的交易知识图谱"
---

# 核心能力
capabilities:
  - 多技术栈代码解析（Vue/React/Angular/小程序）
  - 交易语义识别与分类
  - 业务规则自动提取与标准化
  - 知识图谱构建与智能关联
  - 需求文档自动生成

# 触发器
trigger:
  patterns:
    - "分析.*代码"
    - "逆向.*(交易|业务)"
    - "提取.*需求"
    - "沉淀.*知识"
    - "trade.*analysis"
  files: ["*.vue", "*.jsx", "*.tsx", "*.js", "*.ts"]

# 工具依赖
tools:
  - file_read
  - file_write
  - python_execute
  - memory_search
  - memory_write

# 环境配置
environment:
  KNOWLEDGE_BASE_PATH:
    description: 知识库存储根目录
    default: "~/.openclaw/knowledge/trade/"
    required: true
  CACHE_DIR:
    description: 解析缓存目录
    default: "~/.openclaw/cache/trade-analyzer/"
  LLM_API_KEY:
    description: 用于深度语义分析的LLM API（可选）
    required: false