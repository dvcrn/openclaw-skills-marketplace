## QQ 音乐播放器 Skill 使用示例

### 示例 1: 用户想听歌

**用户：** "我想听歌"

**AI 响应流程：**

1. 读取 `/projects/.openclaw/skills/qq-music-radio/SKILL.md`
2. 执行启动脚本：`/projects/.openclaw/skills/qq-music-radio/start.sh`
3. 获取公网地址（从日志或进程信息）
4. 返回访问地址并说明

**响应示例：**

```
✅ QQ 音乐播放器已启动！

🌐 访问地址：
https://d77457c7c3d05421-14-22-11-163.serveousercontent.com

🎵 功能特性：
• AI 智能推荐 - 自动选择并播放
• 后端智能过滤 - 只播放可用歌曲
• 连续播放 - 永不停歇
• 精美界面 - 沉浸体验

📱 使用说明：
1. 点击上方链接打开播放器
2. 点击"🎧 开始播放"按钮
3. 等待3-5秒加载推荐歌曲
4. 享受音乐！🎵

💡 提示：
• 播放器会自动过滤无法播放的歌曲
• 播放完自动加载新的推荐
• 支持手机和电脑访问
```

---

### 示例 2: 用户说"打开音乐电台"

**用户：** "打开音乐电台"

**AI 响应流程：**

1. 触发 QQ 音乐播放器 skill
2. 执行 `start.sh` 脚本
3. 检查服务器和隧道状态
4. 如果已运行，直接返回地址
5. 如果未运行，启动并返回地址

**响应示例（已运行）：**

```
✅ QQ 音乐播放器正在运行！

🌐 访问地址：
https://d77457c7c3d05421-14-22-11-163.serveousercontent.com

📊 当前状态：
• 服务器运行中 ✓
• 公网隧道已建立 ✓
• 播放器可用 ✓

直接点击链接即可使用！🎵
```

---

### 示例 3: 结合 Canvas 展示

**用户：** "打开音乐播放器并显示在这里"

**AI 响应流程：**

1. 启动播放器（如果未启动）
2. 获取公网地址
3. 使用 `canvas` 工具展示播放器页面

```javascript
// 执行启动脚本
const result = await exec({
    command: '/projects/.openclaw/skills/qq-music-radio/start.sh',
    yieldMs: 5000
});

// 获取公网地址（从环境变量或日志）
const publicUrl = 'https://xxx.serveousercontent.com';

// 使用 Canvas 展示
await canvas({
    action: 'present',
    url: publicUrl,
    width: 1200,
    height: 900
});
```

**响应示例：**

```
✅ 播放器已打开！

🎵 现在你可以：
• 点击"开始播放"开始听歌
• 使用播放控制按钮
• 查看即将播放的歌曲列表
• 调整音量

享受音乐吧！🎵
```

---

### 示例 4: 停止播放器

**用户：** "关闭音乐播放器"

**AI 响应流程：**

1. 执行停止脚本：`/projects/.openclaw/skills/qq-music-radio/stop.sh`
2. 确认停止成功

```javascript
await exec({
    command: '/projects/.openclaw/skills/qq-music-radio/stop.sh'
});
```

**响应示例：**

```
✅ QQ 音乐播放器已停止

📊 已停止：
• 服务器进程 ✓
• 公网隧道 ✓

如需再次使用，说"打开音乐播放器"即可。
```

---

### 示例 5: 检查状态

**用户：** "音乐播放器状态"

**AI 响应流程：**

1. 检查服务器进程
2. 检查隧道进程
3. 测试健康检查端点
4. 返回详细状态

```javascript
// 检查进程
const serverRunning = await exec({
    command: 'pgrep -f "node server-qqmusic.js"'
});

const tunnelRunning = await exec({
    command: 'pgrep -f "ssh.*serveo.net"'
});

// 健康检查
const health = await exec({
    command: 'curl -s http://localhost:3000/health'
});
```

**响应示例：**

```
📊 QQ 音乐播放器状态

🖥 服务器：
• 状态: ✅ 运行中
• PID: 1194042
• 端口: 3000
• 健康检查: 通过

🌐 公网隧道：
• 状态: ✅ 已建立
• PID: 1163921
• 地址: https://xxx.serveousercontent.com

💡 访问播放器：
https://xxx.serveousercontent.com
```

---

## 高级用法

### 自动重启

如果检测到服务器崩溃，自动重启：

```javascript
// 检查健康状态
const health = await fetch('http://localhost:3000/health').catch(() => null);

if (!health) {
    console.log('服务器未响应，正在重启...');
    
    // 停止旧进程
    await exec({ command: '/projects/.openclaw/skills/qq-music-radio/stop.sh' });
    
    // 等待清理
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 重新启动
    await exec({ command: '/projects/.openclaw/skills/qq-music-radio/start.sh' });
}
```

### 定期健康检查

使用 cron job 定期检查并重启（如果需要）：

```javascript
await cron({
    action: 'add',
    job: {
        name: 'QQ音乐播放器健康检查',
        schedule: {
            kind: 'every',
            everyMs: 300000  // 每5分钟
        },
        payload: {
            kind: 'agentTurn',
            message: '检查 QQ 音乐播放器状态，如果崩溃则重启'
        },
        sessionTarget: 'isolated'
    }
});
```

---

## 注意事项

1. **隧道稳定性** - serveo.net 隧道可能会断开，需要定期检查
2. **URL 变化** - 每次重启隧道，URL 可能会改变（除非使用固定子域名）
3. **端口冲突** - 确保 3000 端口未被其他服务占用
4. **网络要求** - 需要稳定的互联网连接

---

这个 skill 现在已经完全可用了！只需说相关关键词，就会自动启动播放器并返回访问地址！🎵
