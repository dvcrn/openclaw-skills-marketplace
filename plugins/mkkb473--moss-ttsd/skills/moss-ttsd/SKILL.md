---
name: moss-ttsd
description: "MOSI Studio 双人对话合成（moss-ttsd）：将两个角色的对话文本合成为 单段连续音频，两人声音自然交替。 当前版本限制：仅支持 2 人对话，仅支持中文和英文。 触发词：多说话人、双人对话、对话合成、两个角色、两种声音、两个人说话、 \"multi-speaker\"、\"dialogue synthesis\"、\"两人对话\"。 注意：如果用户要求超过 2 个说话人，需明确告知当前版本限制， 建议分段合成后拼接。 在飞书渠道：合成完成后优先发送语音气泡，不要发文件附件， 不要只回文字说\"已生成\"。具体发送方法参见 mosi-tts skill 第 5 节。"
---

# MOSS-TTSD 双人对话合成

将两个角色的对话文本合成为一段连续音频，两个声音自然交替出现。

**当前版本限制**
- 仅支持 **2 个说话人**（S1 / S2）
- 仅支持**中文**和**英文**，其他语言不可用
- 不支持中英混合超过50%比例的文本

---

## 快速开始

脚本路径：`~/.openclaw/skills/moss-ttsd/scripts/mosi_dialogue.sh`

```bash
bash ~/.openclaw/skills/moss-ttsd/scripts/mosi_dialogue.sh \
  --text "[S1] 你好，今天感觉怎么样？
[S2] 还不错，谢谢你问！你呢？
[S1] 我也挺好的，最近天气真舒服。
[S2] 是啊，特别适合出去走走。" \
  --voice1 2001257729754140672 \
  --voice2 2002941772480647168 \
  --output ~/.openclaw/workspace/dialogue.wav
```

---

## 文本格式

每行以 `[S1]` 或 `[S2]` 开头，标识说话人，换行分隔：

```
[S1] 第一句话
[S2] 回应的话
[S1] 继续说
[S2] 继续回应
```

**注意**：
- 不要在 `[S1]` / `[S2]` 标签内加其他标点
- 每行只能有一个说话人
- 建议每行文字不超过 100 字

---

## 音色选择

从 `mosi-tts` skill 的内置音色列表中各为 S1、S2 挑选：

| 音色 ID | 名称 | 风格 |
|---------|------|------|
| 2001257729754140672 | 阿树 | 随性自然（男，默认） |
| 2001931510222950400 | 程述 | 播客理性（男） |
| 2002941772480647168 | 阿宁 | 温柔亲切（女） |
| 2020009311371005952 | 台湾女声 | 柔和疗愈（女） |
| 2020008594694475776 | 北京男声 | 清晰标准（男） |
| 2001898421836845056 | 子琪 | 活力明亮（女） |
| 2001910895478837248 | 小满 | 甜美开朗（女） |
| 2002991117984862208 | 梁子 | 专业沉稳（男） |

也可使用通过 `mosi-tts` skill 克隆得到的自定义 voice_id。

---

## 完整参数说明

```
--text,    -t  TEXT    对话文本（必填，含 [S1]/[S2] 标签）
--voice1,  -1  ID      S1 的音色 ID（必填）
--voice2,  -2  ID      S2 的音色 ID（选填，不填则同 S1）
--output,  -o  PATH    输出 WAV 路径
                       （默认: ~/.openclaw/workspace/dialogue.wav）
--duration,-d  SECS    预期总时长（秒，可选，影响语速）
--api-key, -k  KEY     覆盖 MOSI_TTS_API_KEY 环境变量
```

---

## 环境准备

API Key 配置同 `mosi-tts` skill，读取 `MOSI_TTS_API_KEY` 环境变量。
详见 `mosi-tts` skill 的"环境准备"章节。

依赖：`curl`、`node`（均为基础环境自带）

---

## 常见问题

**Q：能生成 3 个人的对话吗？**
当前版本仅支持 2 人（S1 / S2），暂不支持 3 人及以上。
如需模拟多人对话，可分段合成后用 `ffmpeg` 拼接：
```bash
ffmpeg -i part1.wav -i part2.wav \
  -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1" \
  ~/.openclaw/workspace/merged.wav
```

**Q：支持日语/韩语吗？**
当前版本仅支持中文和英文，其他语言无法保证正常合成。

**Q：输出是什么格式？**
WAV（24kHz）。在飞书渠道必须转成语音气泡发送，
参考 `mosi-tts` skill 第 5 节（飞书语音气泡）的 `mosi_feishu_voice.sh` 脚本：
```bash
bash ~/.openclaw/skills/mosi-tts/scripts/mosi_feishu_voice.sh \
  --wav ~/.openclaw/workspace/dialogue.wav \
  --chat-id "oc_xxxxxxxxxxxxxxxx"
```
