# 小红书自动回复配置指南

## 📁 文件结构

```
xhs-auto-reply/
├── auto_reply.sh          # 主脚本（定时任务调用）
├── generate_reply.py      # 回复生成逻辑（关键词匹配 + AI）
├── identity.json + reply_rules.json          # 关键词规则配置
├── tracked_posts.json     # 追踪的帖子列表
├── replied_comments.json  # 已回复的评论记录
├── reply_history.json     # 回复历史（避免重复）
└── reply.log              # 运行日志
```

## 🎯 核心功能

### 1. 关键词匹配
- 支持多个关键词匹配同一类别
- 每个类别有多个回复模板，随机选择
- 自动避免短时间内重复使用相同模板

### 2. AI 个性化
- 当关键词不匹配时，使用默认回复模板
- 未来可接入 AI 对话模型，实现真正的个性化回复

### 3. 防重复机制
- 记录已回复的评论 ID
- 记录最近使用的模板，避免连续重复

## ⚙️ 配置 identity.json + reply_rules.json

### 添加新规则

在 `rules` 数组中添加：

```json
{
  "keywords": ["关键词1", "关键词2"],
  "category": "类别名称",
  "templates": [
    "模板1 {占位符}",
    "模板2 {占位符}",
    "模板3 {占位符}"
  ],
  "default_占位符": "默认值"
}
```

### 可用占位符

- `{user}` - 用户名（如果可用）
- `{emoji}` - 随机 emoji
- `{tip}` - 提示信息
- `{price_info}` - 价格信息
- `{interaction}` - 互动引导
- `{promise}` - 承诺内容
- `{question}` - 提问

### 示例：添加"求教程"规则

```json
{
  "keywords": ["求教程", "教程", "求教", "怎么弄"],
  "category": "求助",
  "templates": [
    "教程在准备中{emoji} {promise}",
    "好的我整理一下{emoji} {promise}",
    "这个后面会出详细教程的{emoji} {promise}"
  ],
  "default_emoji": "📝",
  "default_promise": "记得关注我不迷路~"
}
```

## 🔧 使用方法

### 1. 手动测试

测试单个评论的回复：

```bash
cd /root/.openclaw/workspace/xhs-auto-reply
./auto_reply.sh --test "评论内容" "帖子标题"
```

### 2. 手动检查所有帖子

```bash
./auto_reply.sh
```

### 3. 设置定时任务

添加到 crontab（每30分钟运行一次）：

```bash
crontab -e
```

添加：

```
*/30 * * * * /root/.openclaw/workspace/xhs-auto-reply/auto_reply.sh
```

### 4. 添加新帖子到监控

编辑 `tracked_posts.json`：

```json
[
  {
    "id": "帖子ID",
    "title": "帖子标题",
    "xsec_token": "安全token",
    "added_at": "2026-03-06T00:00:00+08:00"
  }
]
```

## 📊 查看日志

```bash
tail -f /root/.openclaw/workspace/xhs-auto-reply/reply.log
```

## 🎨 自定义回复风格

### 调整语气

在 `identity.json + reply_rules.json` 中修改模板：

- **正式风格**: "感谢您的评论，如有问题请随时联系。"
- **亲切风格**: "谢谢亲的评论~ 有问题随时问我哦！"
- **活泼风格**: "哇谢谢评论！有什么想聊的嘛？"

### 添加更多随机元素

在 Python 脚本中添加更多选项：

```python
emojis = ['😊', '😄', '🎉', '✨', '❤️', '👍', '💪', '🌟', '💕', '🔥', '😄', '🥰', '😋']
```

## ⚠️ 注意事项

1. **避免过度回复**: 小红书有频率限制，脚本已设置 5-10 秒延迟
2. **定期清理**: `replied_comments.json` 会越来越大，定期清理旧记录
3. **关键词优化**: 根据实际评论情况，持续优化关键词和模板
4. **测试**: 修改配置后，先用 `--test` 参数测试

## 🔮 未来计划

- [ ] 接入 AI 对话模型，实现真正的智能回复
- [ ] 支持根据用户画像（粉丝数、活跃度）调整回复策略
- [ ] 添加黑名单功能，过滤恶意评论
- [ ] 支持回复二级评论
- [ ] 添加统计数据（回复率、互动率）

## 💡 优化建议

### 提高回复质量

1. **多看真实评论**: 了解用户的真实提问方式
2. **模拟真人语气**: 避免机器感，多用口语化表达
3. **适度互动**: 回复中引导用户关注、点赞、评论

### 增加变化

1. **定期更新模板**: 每周添加新的回复模板
2. **节日特殊回复**: 节假日使用特殊模板
3. **热点话题**: 结合热点调整回复内容

## 🆘 故障排查

### 问题：脚本不运行

```bash
# 检查权限
ls -l /root/.openclaw/workspace/xhs-auto-reply/auto_reply.sh

# 检查 MCP 服务
curl http://localhost:18060/mcp

# 查看日志
tail -20 /root/.openclaw/workspace/xhs-auto-reply/reply.log
```

### 问题：回复失败

1. 检查 Cookie 是否过期（重新登录）
2. 检查 xsec_token 是否正确
3. 查看是否有频率限制

### 问题：关键词不匹配

1. 在 `identity.json + reply_rules.json` 中添加新的关键词
2. 检查关键词是否拼写正确
3. 查看默认回复是否正常工作
