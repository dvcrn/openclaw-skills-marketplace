# Novel Scraper 📖

轻量级小说抓取工具，支持自动翻页、会话复用、内存监控。使用 OpenClaw browser 工具抓取笔趣阁等小说网站，输出格式化 TXT 文件。

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **自动翻页** | 检测并抓取分页章节，最多 5 页 |
| **会话复用** | 多章复用浏览器，每 3 章释放内存 |
| **内存监控** | 超 2.5GB 自动释放浏览器 |
| **智能过滤** | 自动过滤导航、广告等无关内容 |
| **缓存系统** | 避免重复抓取，支持断点续抓 |
| **进度追踪** | 中断后可续抓，不重复劳动 |

## 🚀 快速开始

### 安装依赖

```bash
cd ~/.openclaw/workspace/skills/novel-scraper
pip3 install -r requirements.txt --user
```

### 抓取单章

```bash
cd ~/.openclaw/workspace/skills/novel-scraper
python3 scripts/scraper.py --url "https://www.bqquge.com/4/1962"
```

### 批量抓取多章

```bash
python3 scripts/scraper.py \
  --urls "https://www.bqquge.com/4/1962,https://www.bqquge.com/4/1963,https://www.bqquge.com/4/1964" \
  --book "没钱修什么仙"
```

### 合并缓存

如果之前抓取过但未合并，可以使用：

```bash
python3 scripts/merge_cache.py --book "书名"
```

## 📁 输出位置

抓取的小说保存在：`~/.openclaw/workspace/novels/`

**文件名格式：**
- 单章：`书名_第 X 章.txt`
- 多章：`书名_第 X-Y 章.txt`

**输出示例：**
```
============================================================
第 1 章 面试
============================================================

"到了吗？"

"不要紧张，你成绩这么好，一定能过的。"

看着屏幕上母亲发来的消息，张羽默默收起手机...
```

## ⚙️ 命令行参数

```bash
python3 scripts/scraper.py [选项]

# URL 选项
--url URL           单章 URL
--urls URLS         多章 URL（逗号分隔）

# 输出选项
--output, -o PATH   输出文件路径
--book, -b NAME     书名（可选，自动提取）
--no-auto-save      禁用自动保存

# 性能选项
--memory-limit MB   内存限制（默认 2500）
--auto-close N      每 N 章释放内存（默认 3）
--retry N           重试次数（默认 3）
--wait N            等待时间秒（默认 2）
```

## 🌐 支持网站

| 网站 | 状态 | 配置 |
|------|------|------|
| 笔趣阁 (bqquge.com) | ✅ 已测试 | `configs/sites.json` |
| 其他网站 | 🔄 需配置 | 添加选择器配置 |

### 配置新网站

编辑 `configs/sites.json`：

```json
{
  "www.example.com": {
    "name": "示例网站",
    "title_selector": "h1",
    "content_selector": "#content p",
    "next_selector": ".next a",
    "wait_element": "#content",
    "memory_limit_mb": 500
  }
}
```

## 🔧 故障排除

### 抓取内容为空

1. 检查 URL 是否正确
2. 清除缓存：`rm -rf /tmp/novel_scraper_cache/*`
3. 增加等待时间：`--wait 3`

### 内存过高

1. 降低内存限制：`--memory-limit 1500`
2. 缩短释放间隔：`--auto-close 2`

### 文件名乱码

确保系统支持 UTF-8，或手动指定 `--book` 参数。

## 📦 打包发布

```bash
python3 scripts/package_skill.py ~/.openclaw/workspace/skills/novel-scraper
```

生成 `novel-scraper.skill` 文件。

## 📝 相关脚本

| 脚本 | 用途 |
|------|------|
| `scripts/scraper.py` | 主程序（859 行） |
| `scripts/merge_cache.py` | 合并缓存文件 |
| `scripts/package_skill.py` | 打包为 .skill 文件 |

## 📄 许可证

MIT License

---

**Created for OpenClaw** 🦞
