# Browser Search 技能

使用本地浏览器进行自动化搜索和内容提取。

## 安装

```bash
# 复制技能到仓库
cp -r /home/linshui/.openclaw/workspace/skills/browser-search ~/.openclaw/skills/
```

## 快速使用

### 基本搜索

```bash
# 使用 Bing 搜索（默认）
python ~/.openclaw/skills/browser-search/browser-search.py "人工智能 2026"

# 使用 Google 搜索
python ~/.openclaw/skills/browser-search/browser-search.py "AI 趋势" --engine google
```

### 保存结果

```bash
python ~/.openclaw/skills/browser-search/browser-search.py "Python 教程" --output ai_tutorials.md
```

### 指定结果数量

```bash
python ~/.openclaw/skills/browser-search/browser-search.py "深度学习" --max 5
```

## 支持的搜索引擎

- **Bing** (默认)
- **Google**
- **Baidu**
- **DuckDuckGo**

## 输出示例

```
============================================================
搜索结果 (10 条)
============================================================

1. 2026 AI 趋势预测，全球科技巨头与顶尖机构研判
   https://cloud.tencent.com.cn/developer/article/2631820
   2026 年 AI 将迈向规模化落地，AI Agent 成为核心趋势...

2. 2026 年中国 AI 发展趋势前瞻
   https://www.tsinghua.edu.cn/info/1182/124190.htm
   2026 年是"十五五"开局之年...

============================================================
```

## 注意事项

1. **浏览器服务**：确保浏览器正常运行
2. **网络环境**：部分搜索引擎可能受地区限制
3. **超时设置**：默认 30 秒，可根据需要调整

## 故障排除

### 浏览器超时

```bash
# 重启网关
openclaw gateway restart
```

### 没有结果

尝试其他搜索引擎：
```bash
--engine baidu  # 国内搜索
--engine google  # 国际搜索
```

## 相关技能

- `agent-browser` - 浏览器自动化
- `web-search` - API 搜索
- `web-fetch` - 网页提取
