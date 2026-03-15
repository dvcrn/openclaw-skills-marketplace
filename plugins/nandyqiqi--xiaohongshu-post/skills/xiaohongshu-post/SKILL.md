---
name: xiaohongshu-post
description: "在小红书创作服务平台发布图文帖子。包括： (1) 从本地桌面跨权限上传图片到小红书， (2) 填写标题和正文， (3) 发布帖子。当用户要求发布小红书帖子、上传图片到小红书、或需要在小红书发图文时使用此skill。"
---

# 小红书发帖Skill

## 使用前提

确保用户已登录小红书创作服务平台 (https://creator.xiaohongshu.com)。

## 完整发布流程

### 步骤1: 打开发布页面

```
URL: https://creator.xiaohongshu.com/publish/publish?source=official
```

### 步骤2: 处理图片上传（关键 - 跨权限）

浏览器无法直接访问用户桌面文件，需要中转：

1. **扫描桌面找图片**
```powershell
Get-ChildItem -Path $env:USERPROFILE\Desktop | Select-Object Name
```

2. **复制到允许的目录**
```powershell
# 假设图片名为 xxx.png
New-Item -ItemType Directory -Path '\tmp\openclaw\uploads' -Force
Copy-Item -Path (Join-Path $env:USERPROFILE 'Desktop\xxx.png') -Destination '\tmp\openclaw\uploads\' -Force
```

3. **上传到小红书**（关键步骤）
   
   **流程A: 首次上传**
   - 点击「上传图文」切换到图文模式 (ref=e109)
   - 点击「上传图片」按钮 (ref=e128)
   - **立即**调用 upload 命令（无延迟）:
   ```json
   {
     "action": "upload",
     "paths": ["C:\\tmp\\openclaw\\uploads\\xxx.png"]
     "profile": "chrome"
   }
   ```
   
   **流程B: 继续上传多张图片**
   - 每上传一张后，页面会显示"1/18"等计数
   - 点击图片区域的加号按钮继续添加 (ref=e179)
   - 再次调用 upload 上传下一张图片

### 步骤3: 填写内容

1. **填写标题** - 定位标题输入框 (ref=e192)，type 输入标题文字
2. **填写正文** - 定位正文输入框 (ref=e201)，type 输入正文内容

### 步骤4: 发布

1. 点击「发布」按钮 (ref=e480)
2. 页面显示"发布成功"即完成

## 关键技术点

1. **upload必须在点击上传按钮后立即调用**，中间不能有延迟，否则file input会丢失
2. **每次上传一张图片后需要重新点击加号按钮**才能继续上传下一张
3. **浏览器控制服务可能不稳定**，如果遇到timeout需要重新连接Chrome relay
4. **使用profile=chrome**而不是openclaw，因为用户已登录的会话在chrome profile中

## 常见问题

- **页面显示账号异常**: 需要用户在手机端或网页端完成实名认证/绑定手机
- **上传后页面刷新**: 可能触发了某些限制，尝试重新填写并发布
- **Choose File按钮无法点击**: 尝试用JavaScript evaluate方式触发，或等待页面加载完成后重试
- **upload上传不成功**: 一定要先点击「上传图片」按钮，**立即**再调用 upload（中间不要有延迟）
- **发布后页面刷新数据丢失**: 小红书平台限制，点击发布后页面会刷新，可尝试先保存草稿再手动发布
- **浏览器控制服务超时**: 需要用户重新点击Chrome扩展图标连接relay
