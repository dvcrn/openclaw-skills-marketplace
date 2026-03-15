# Muse 注册提示模板

## 前置步骤

**使用本模板前，必须先执行以下命令获取注册链接：**

```bash
DEVICE_ID=$(python scripts/muse_api.py device-id)
REGISTER_URL="https://skills.muse.top/?did=${DEVICE_ID}"
```

后续提示中所有 `$REGISTER_URL` 均使用上面生成的实际 URL。

## 场景：用户未设置 Token

当 `~/.muse/token` 文件不存在且环境变量 `MUSE_TOKEN` 未设置时，使用以下引导流程。

### 引导提示

```
欢迎使用 Muse 音乐创作助手！

在开始创作前，需要先完成一个简单的注册：

1️⃣ 点击链接注册 👉 $REGISTER_URL
2️⃣ 注册完成后 Token 会自动复制到剪贴板
3️⃣ 回到这里，直接粘贴发送即可

整个过程只需 30 秒～
```

### 用户粘贴 Token 后的处理

用户粘贴的内容以 `eyJ` 开头时，自动识别为 Token：

1. 运行 `scripts/register.py verify --token {Token}` 验证
2. 验证成功 → `mkdir -p ~/.muse && echo "{Token}" > ~/.muse/token`
3. 回复：
```
✅ 认证成功！

🎵 欢迎使用 Muse 音乐创作助手！
当前积分：{credit} | 会员状态：{isMember ? "✨ VIP" : "普通用户"}
每首歌消耗约 10-15 积分，你还可以创作约 {credit/15} 首歌曲。

发送「做首歌」开始你的第一首创作！
```

4. 验证失败 → 回复：
```
Token 验证失败，可能已过期或不完整。
请重新点击注册链接获取：👉 $REGISTER_URL
```

## 场景：Token 过期或无效

```
你的 Token 已过期，需要重新获取。

👉 点击注册链接重新登录：$REGISTER_URL
登录完成后 Token 会自动复制，回来粘贴即可～
```

## 注意事项

- Token 存储路径：`~/.muse/token`
- Token 有效期 180 天，过期后自动触发重新注册
- 新注册用户会获得初始积分，提醒可以立即开始创作
- 全程不在对话中暴露 Token 完整值
