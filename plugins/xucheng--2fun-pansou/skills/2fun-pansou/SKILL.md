---
name: 2fun-pansou
description: "Search cloud-drive and pan-share resources through 2fun.live PanSou aggregation. Use when the user asks to find movie, TV, anime, software, or other downloadable resources on Aliyun Drive, Quark, Baidu, 115, PikPak, magnet, or similar sources. Triggers: 网盘搜索, 找资源, pan search, cloud drive links, 下载链接, 有没有XX资源."
---

# 2fun-pansou Skill

Search PanSou resources via 2fun.live.

## 使用方法

```bash
python3 ~/.openclaw/workspace/skills/2fun-pansou/scripts/search.py "关键词"
```

默认走 `s.2fun.live` 的搜索接口；也可以通过环境变量覆盖：

```bash
API_URL=https://www.2fun.live python3 ~/.openclaw/workspace/skills/2fun-pansou/scripts/search.py "关键词"
```

也可以直接指定完整搜索 endpoint：

```bash
PAN_SEARCH_API_URL=https://s.2fun.live/api/search python3 ~/.openclaw/workspace/skills/2fun-pansou/scripts/search.py "关键词"
```

## 支持的云盘类型

☁️ 阿里云盘 / ⚡ 夸克网盘 / 🔵 百度网盘 / 🔷 115网盘  
🟣 PikPak / UC网盘 / 迅雷云盘 / 123网盘 / 天翼云盘 / 移动云盘  
🧲 磁力链接 / 🔗 ED2K

## 常用示例

```bash
# 基本搜索
python3 search.py "流浪地球2"

# 限定云盘类型
python3 search.py "权游 第四季" --types aliyun quark

# 服务端分页（主站 POST API）
API_URL=https://www.2fun.live python3 search.py "流浪地球2" --types aliyun --page 2 --page-size 10

# 直接走 s.2fun.live 的 GET 搜索接口
PAN_SEARCH_API_URL=https://s.2fun.live/api/search python3 search.py "流浪地球2" --types aliyun --page 2 --page-size 10

# 指定每种类型显示更多结果
python3 search.py "复仇者联盟" --max 5

# 强制刷新缓存（跳过5分钟缓存）
python3 search.py "沙丘2" --refresh

# 原始 JSON 输出
python3 search.py "流浪地球2" --json
```

## API 说明

- 默认接口：`GET https://s.2fun.live/api/search`
- 完整 endpoint 覆盖：`PAN_SEARCH_API_URL=...`
- 请求方式：
  - 主站接口：`POST /api/pan/search`
  - `s.2fun.live` 接口：`GET /api/search?q=关键词&page=1&pageSize=10&cloud=aliyun`
- 限速：60次/分钟（按 IP，公开访问无需登录）
- 缓存：服务端 Redis 缓存 5 分钟
- `API_URL` 主要用于生成站点链接；`PAN_SEARCH_API_URL` 用于指定真实搜索 endpoint
- 脚本会自动识别主站 POST 接口和 `s.2fun.live` GET 接口，并归一化结果格式

## 结果格式

```text
🔍 流浪地球2 — 共 42 条结果 (823ms)

☁️ 阿里云盘 (8 个)
  `https://www.aliyundrive.com/s/xxx`  密码: `abc1`

⚡ 夸克网盘 (5 个)
  `https://pan.quark.cn/s/xxx`

🌐 完整搜索：https://www.2fun.live/pan?kw=流浪地球2
```
