# 小红书智能自动回复系统 🤖

## ✨ 核心特性

### 🎯 关键词智能匹配
- 支持 6 大类别关键词：求助、价格咨询、夸奖、关注互动、收藏、分享
- 每个类别多个回复模板，自动随机选择
- 智能避免重复，连续回复不会用相同模板

### 🧠 AI 个性化回复
- 每条评论独立分析，生成独特回复
- 支持占位符填充（emoji、提示、互动引导等）
- 未来可接入 AI 对话模型

### 🔄 防重复机制
- 自动记录已回复的评论 ID
- 避免对同一条评论重复回复
- 记录最近使用的模板，增加变化

### 📊 完整日志
- 详细的运行日志
- 回复历史记录
- 便于调试和优化

## 🚀 快速开始

### 1. 测试回复生成

```bash
cd /root/.openclaw/workspace/xhs-auto-reply

# 测试不同类型的评论
./auto_reply.sh --test "这个怎么用？" "OpenClaw教程"
./auto_reply.sh --test "太厉害了！" "OpenClaw教程"
./auto_reply.sh --test "多少钱？" "OpenClaw教程"
```

### 2. 手动检查回复

```bash
./auto_reply.sh
```

### 3. 设置定时任务

```bash
crontab -e

# 每30分钟检查一次
*/30 * * * * /root/.openclaw/workspace/xhs-auto-reply/auto_reply.sh
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `auto_reply.sh` | 主脚本，定时任务调用 |
| `generate_reply.py` | 回复生成逻辑 |
| `identity.json + reply_rules.json` | **关键词规则配置（可自定义）** |
| `tracked_posts.json` | 追踪的帖子列表 |
| `replied_comments.json` | 已回复的评论记录 |
| `reply_history.json` | 回复模板使用历史 |
| `CONFIG.md` | **详细配置指南** |

## ⚙️ 自定义配置

### 修改关键词规则

编辑 `identity.json + reply_rules.json`：

```json
{
  "rules": [
    {
      "keywords": ["怎么用", "教程"],
      "category": "求助",
      "templates": [
        "很高兴你对这个感兴趣！{tip}",
        "其实很简单，{tip} 有问题随时问我~"
      ]
    }
  ]
}
```

### 添加新的回复类别

参见 [CONFIG.md](./CONFIG.md) 详细说明

## 📊 查看运行状态

```bash
# 实时日志
tail -f /root/.openclaw/workspace/xhs-auto-reply/reply.log

# 查看已回复数量
cat /root/.openclaw/workspace/xhs-auto-reply/replied_comments.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'已回复: {len(data)} 条')"

# 查看追踪的帖子
cat /root/.openclaw/workspace/xhs-auto-reply/tracked_posts.json | python3 -m json.tool
```

## 🎯 回复策略

### 关键词匹配优先
1. 分析评论内容
2. 匹配预定义关键词
3. 使用对应类别的模板
4. 随机选择模板变体

### 默认回复兜底
当没有关键词匹配时，使用默认回复模板：
- "谢谢你的评论😊 有什么想了解的吗？"
- "看到你的留言啦❤️ 需要帮助吗？"
- ...

## 💡 使用建议

### 1. 定期优化关键词
- 查看实际评论内容
- 添加新的关键词
- 删除不常用的关键词

### 2. 更新回复模板
- 每周添加新的模板
- 保持语气新鲜感
- 结合热点话题

### 3. 监控回复效果
- 查看日志确认回复成功
- 检查是否有异常
- 调整回复频率

## ⚠️ 注意事项

1. **频率限制**: 脚本已设置 5-10 秒延迟，避免触发平台限制
2. **Cookie 过期**: 定期检查登录状态
3. **监控帖子**: 发布新笔记后记得添加到追踪列表
4. **备份数据**: 定期备份 `identity.json + reply_rules.json` 和配置文件

## 📖 详细文档

- [CONFIG.md](./CONFIG.md) - 完整配置指南
- [../memory/xhs-monitor.json](../memory/xhs-monitor.json) - 统一监控列表

## 🆘 常见问题

**Q: 如何添加新帖子到监控？**
A: 发布笔记后，OpenClaw 会自动询问是否加入监控。也可以手动编辑 `tracked_posts.json`。

**Q: 如何修改回复语气？**
A: 编辑 `identity.json + reply_rules.json` 中的 `templates` 数组，改成你喜欢的语气。

**Q: 如何查看回复历史？**
A: 查看 `replied_comments.json` 文件。

**Q: 关键词匹配不到怎么办？**
A: 系统会使用默认回复模板。可以在 `identity.json + reply_rules.json` 中添加新的关键词。

## 🔄 更新日志

### v2.0 (2026-03-06)
- ✨ 新增关键词智能匹配
- ✨ 新增回复模板随机选择
- ✨ 新增防重复机制
- ✨ 新增详细日志
- 📝 新增配置文档

### v1.0 (2026-03-05)
- 🎉 基础自动回复功能
