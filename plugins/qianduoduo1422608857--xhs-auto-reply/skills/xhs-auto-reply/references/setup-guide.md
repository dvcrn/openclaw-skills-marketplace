# 小红书自动回复 - 安装指南

## 1. 环境要求

- Linux 服务器（推荐 Ubuntu 20.04+）
- Python 3.8+
- 显示服务器（Xvfb）用于 MCP 浏览器

## 2. 安装 xiaohongshu-mcp

```bash
# 安装 Xvfb
apt-get install xvfb -y

# 启动虚拟显示
Xvfb :99 -screen 0 1920x1080x24 &

# 下载 xiaohongshu-mcp
cd /root
git clone https://github.com/xxx/xiaohongshu-mcp.git
cd xiaohongshu-mcp

# 运行
export DISPLAY=:99
nohup ./xiaohongshu-mcp-linux-amd64 > mcp.log 2>&1 &

# 检查状态
curl http://localhost:18060/health
```

## 3. 创建项目目录

```bash
mkdir -p /root/.openclaw/workspace/xhs-auto-reply
cd /root/.openclaw/workspace/xhs-auto-reply

# 创建必要文件
touch tracked_posts.json replied_comments.json reply.log
```

## 4. 获取 xsec_token

```bash
# 方法1：通过 MCP 搜索
curl -X POST http://localhost:18060/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "init",
    "method": "initialize",
    "params": {"protocolVersion": "2024-11-05", "capabilities": {}}
  }'

# 记下返回的 Mcp-Session-Id，然后搜索
curl -X POST http://localhost:18060/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {"name": "search_feeds", "arguments": {"keyword": "你的帖子标题"}}
  }'
```

## 5. 配置监控帖子

编辑 `tracked_posts.json`：

```json
{
  "posts": [
    {
      "post_id": "69a977200000000001d027395",
      "title": "测试自动回复功能",
      "xsec_token": "ABL8zUMJsFB7MayG4B0ZNxWZZMy9Q1nErDSsWvcss6kgw=",
      "added_at": "2026-03-11T00:00:00+08:00"
    }
  ]
}
```

## 6. 设置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每 30 分钟执行）
*/30 * * * * /root/.openclaw/workspace/xhs-auto-reply/cron_reply.sh >> /root/.openclaw/workspace/logs/xhs-reply.log 2>&1
```

## 7. 验证安装

```bash
# 手动测试
bash /root/.openclaw/workspace/xhs-auto-reply/cron_reply.sh

# 查看日志
tail -f /root/.openclaw/workspace/xhs-auto-reply/reply.log
```

## 故障排除

### MCP 无法启动

```bash
# 检查显示服务器
ps aux | grep Xvfb

# 重启显示服务器
pkill Xvfb
Xvfb :99 -screen 0 1920x1080x24 &
```

### 获取评论失败

```bash
# 检查 MCP 日志
tail -f /root/xiaohongshu-mcp/mcp.log

# 重启 MCP
pkill xiaohongshu-mcp
cd /root/xiaohongshu-mcp
export DISPLAY=:99
nohup ./xiaohongshu-mcp-linux-amd64 > mcp.log 2>&1 &
```

### xsec_token 过期

需要重新搜索帖子获取新的 token。
