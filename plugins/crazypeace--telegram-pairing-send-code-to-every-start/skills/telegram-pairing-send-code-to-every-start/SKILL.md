---
name: telegram-pairing-send-code-to-every-start
description: "Modify OpenClaw's Telegram pairing logic so unapproved users receive pairing codes on every /start message before approval. Use when users need to repeatedly access pairing codes after the initial request, ensuring consistent access to pairing instructions even if the initial code was missed or lost."
---

# Telegram 配对消息持续响应技能

## 概述
此技能描述如何修改 OpenClaw 的 Telegram 配对逻辑，使未批准的用户在配对被批准前，每次发送 `/start` 消息时都能收到配对码回复。

## 何时使用此技能
- 需要让未批准的用户每次发送 `/start` 都收到配对消息（而非仅首次）
- 用户可能错过首次配对消息，需要重新获取配对码
- 提升用户体验，确保用户始终能获得配对指引

## 执行步骤

### 1. 找到需要修改的文件
在你正在运行的代码中搜索下面的代码段

```
async function issuePairingChallenge(params) {
  const { code, created } = await params.upsertPairingRequest({
    id: params.senderId,
    meta: params.meta
  });
  if (!created) return { created: false };
  params.onCreated?.({ code });
  const replyText = params.buildReplyText?.({
    code,
    senderIdLine: params.senderIdLine
  }) ?? buildPairingReply({
    channel: params.channel,
    idLine: params.senderIdLine,
    code
  });
  try {
    await params.sendPairingReply(replyText);
  } catch (err) {
    params.onReplyError?.(err);
  }
  return {
    created: true,
    code
  };
}
```

### 2. 实施修改
将条件判断从 `if (created)` 修改为 `if (code)`:

```
async function issuePairingChallenge(params) {
  const { code, created } = await params.upsertPairingRequest({
    id: params.senderId,
    meta: params.meta
  });
  if (!code) return { created: false }; // <-- 关键修改点
  params.onCreated?.({ code });
  const replyText = params.buildReplyText?.({
    code,
    senderIdLine: params.senderIdLine
  }) ?? buildPairingReply({
    channel: params.channel,
    idLine: params.senderIdLine,
    code
  });
  try {
    await params.sendPairingReply(replyText);
  } catch (err) {
    params.onReplyError?.(err);
  }
  return {
    created: true,
    code
  };
}
```


### 3. 重启服务
修改完成后需要重启 OpenClaw 服务以使更改生效:

```bash
openclaw gateway restart
```

## 一些建议
在寻找需要修改的文件时, 建议先搜索 `async function issuePairingChallenge(params)` 可以帮助你先大幅缩小处理范围, 过滤出需要修改的文件.

一个建议的起始目录为 /usr/lib/node_modules/openclaw/

## 验证修改
- 让未配对的用户发送 `/start` 命令
- 确认用户收到配对码消息
- 再次发送 `/start` 命令，确认用户再次收到相同的配对码

## 注意事项
- 修改系统文件前务必备份原始文件
- 修改后的文件在 OpenClaw 更新时可能会被覆盖，需要重新应用修改

## 故障排除
- 如果修改不生效，请确认是否正确重启了 OpenClaw 服务
- 如果找不到文件路径，请确认 OpenClaw 的实际安装路径
- 如果权限不足，请使用适当的权限提升方法（如 sudo）
- 如需回滚，请使用备份文件替换修改后的文件
