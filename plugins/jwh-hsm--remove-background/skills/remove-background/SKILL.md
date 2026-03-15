---
name: remove-background
description: "remove-bg"
---

# SKILL.md - Remove Background Skill

## 简介
`remove-bg` 是一个用于 **去除图片单色背景并生成透明 PNG** 的本地技能。它基于 Pillow 实现，适合白色、淡灰等亮色背景的图片。

## 使用方式
在 OpenClaw 中调用技能时，使用以下命令格式：
```
skill remove-bg <input_image_path> <output_image_path> [threshold]
```
- `<input_image_path>`：待处理的原始图片（任意 Pillow 支持的格式）。
- `<output_image_path>`：生成的 PNG（必须以 `.png` 结尾），会保存透明背景。
- `threshold`（可选，默认 200）：判断像素是否为背景的亮度阈值。数值越高越保守，适用于背景较暗的情况。

## 示例
```powershell
skill remove-bg "C:\Users\Administrator\Pictures\Camera Roll\1108.png" "C:\Users\Administrator\.openclaw\workspace\1108_transparent.png"
```
若背景不是纯白，可调低阈值：
```powershell
skill remove-bg "...\photo.jpg" "...\photo_trans.png" 180
```

## 实现细节
脚本 `remove_bg.py` 位于同目录下，使用 Pillow 读取图像、遍历像素并根据阈值将符合条件的像素设为全透明，然后保存为 PNG。

---
*本技能遵守 OpenClaw 安全指南，仅在本地工作区读取/写入文件，不会向外部网络发送数据。*