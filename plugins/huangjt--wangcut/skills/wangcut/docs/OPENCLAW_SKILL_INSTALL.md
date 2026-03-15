# OpenClaw 安装 Wangcut Skill 说明

本文档说明如何在 OpenClaw 中安装和使用自定义的 Wangcut 视频剪辑 Skill。

## 前置要求

- 已安装 [OpenClaw](https://openclaw.ai)
- 已安装 Python 3.8+ 和 requests 库 (`pip install requests`)

## 方法一：工作区 Skills（推荐）

将 skill 放在项目的 `/skills` 目录下，这是**最高优先级**的位置，仅对当前工作区生效。

### 步骤

1. **复制 skill 到工作区**

   将整个 `wangcut` 文件夹复制到你的 OpenClaw 工作区的 `skills` 目录：

   ```
   你的项目目录/
   └── skills/
       └── wangcut/
           ├── SKILL.md
           ├── config.example.ini
           └── scripts/
               └── wangcut_api.py
   ```

2. **创建配置文件**

   在项目根目录创建 `config.ini`，参考 `config.example.ini` 填写账号密码：

   ```ini
   [wangcut]
   username = 你的手机号
   password = 你的密码
   ```

3. **重启 OpenClaw 会话**

   Skills 在会话开始时加载，重启后生效。

## 方法二：共享 Skills（全局可用）

将 skill 放在 `~/.openclaw/skills` 目录，对所有 OpenClaw 工作区都可用。

### 步骤

1. **创建目录**（如果不存在）

   ```bash
   mkdir -p ~/.openclaw/skills
   ```

2. **复制 skill**

   ```bash
   cp -r wangcut ~/.openclaw/skills/
   ```

3. **创建配置文件**

   在你的**每个项目根目录**或 `~/.openclaw/` 下创建 `config.ini`。

## 方法三：使用 ClawHub（官方推荐）

ClawHub 是 OpenClaw 的公共 skills 注册中心。

### 发布到 ClawHub

1. 访问 https://clawhub.com
2. 注册并发布你的 skill
3. 其他人可以通过 `clawhub install wangcut` 安装

### 从 ClawHub 安装

```bash
clawhub install wangcut
```

默认安装到 `./skills` 目录。

## Skill 目录结构

一个完整的 skill 必须包含以下结构：

```
wangcut/
├── SKILL.md              # 必需：Skill 定义文件
├── config.example.ini    # 可选：配置模板
└── scripts/              # 可选：脚本目录
    └── wangcut_api.py
```

### SKILL.md 格式要求

```markdown
---
name: wangcut
description: |
  Skill 的描述，用于触发词匹配。
  TRIGGER when: 触发条件说明。
---

# Skill 标题

具体的使用说明...
```

## Skills 加载优先级

当同名 skill 存在于多个位置时，优先级如下：

1. **`/skills`** - 工作区 skills（最高优先级）
2. **`~/.openclaw/skills`** - 共享 skills
3. **bundled skills** - 内置 skills（最低优先级）

## 验证安装

启动 OpenClaw 后，使用以下命令验证 skill 是否加载：

```bash
openclaw skills check
```

或在对话中尝试触发：

```
查看最近的视频剪辑任务
```

## 使用示例

安装成功后，你可以在 OpenClaw 中使用以下命令：

### 创建视频任务

```
创建一个视频剪辑任务，文案是：
良心是什么？虽然不值钱，但它能让你心安。
```

### 查看任务列表

```
查看最近5个视频剪辑任务
```

### 等待并下载

```
等待任务 12575 完成并下载视频
```

## 配置说明

### config.ini 完整配置

```ini
[wangcut]
# 账号配置
username = 你的手机号
password = 你的密码

# API基础URL（通常不需要修改）
base_url = https://cloud.qinsilk.com/aicut/api/v1

# 素材文件夹ID（可选）
folder_id = 58

# 下载保存目录
download_dir = ./downloads

[task_defaults]
# 语音类型
voice_type = f_liuyuxi_20251009
# 语音速度 (0.5-2.0)
voice_speed = 1.3
# 语音音调
voice_pitch = 1
# 视频分辨率
resolution_width = 1080
resolution_height = 1920
# 字幕设置
subtitle_enabled = true
subtitle_font_size = 90
subtitle_font_color = yellow
subtitle_font = 江城律动宋
subtitle_position = 0.7
# 背景音乐
music_enabled = true
music_name = 夏季有你
music_volume = 0.4
```

## 安全注意事项

- **配置文件安全**: `config.ini` 包含敏感信息，请勿提交到版本控制
- **添加到 .gitignore**:
  ```
  config.ini
  downloads/
  __pycache__/
  ```
- **第三方 skills**: 使用第三方 skills 前请先阅读其内容

## 故障排除

### Skill 未加载

1. 检查目录结构是否正确
2. 确认 `SKILL.md` 格式正确
3. 重启 OpenClaw 会话

### API 调用失败

1. 检查 `config.ini` 中的账号密码
2. 确认网络连接正常
3. 查看 Python 脚本是否有语法错误

### 导入错误

确保已安装依赖：

```bash
pip install requests
```

## 参考资料

- [OpenClaw Skills 官方文档](https://docs.openclaw.ai/tools/skills)
- [ClawHub Skills 注册中心](https://clawhub.com)
- [Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills)
