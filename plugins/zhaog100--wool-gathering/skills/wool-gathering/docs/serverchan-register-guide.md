# Server酱注册教程

## 🎯 什么是Server酱？

Server酱是一款「程序员和服务器之间的通信软件」，也就是从服务器推报警和日志到手机的工具。
- 官网：https://sct.ftqq.com/
- 免费：每天5条消息
- 推送方式：微信服务号

---

## 📱 注册步骤（3分钟完成）

### **步骤1：访问官网**
打开浏览器，访问：https://sct.ftqq.com/

### **步骤2：微信扫码登录**
1. 页面会显示一个二维码
2. 用微信扫描二维码
3. 确认登录

### **步骤3：绑定微信服务号**
1. 登录后，系统会提示你绑定微信服务号
2. 扫码关注「Server酱」服务号
3. 关注成功后，返回网页

### **步骤4：获取SendKey**
1. 登录后，点击页面上的「SendKey」
2. 复制你的SendKey（格式：SCT开头的字符串）
3. 例如：`SCTxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🔑 SendKey示例

```
正确的格式：
SCT1234567890abcdefghijklmnopqrstuv

错误的格式（缺少SCT前缀）：
1234567890abcdefghijklmnopqrstuv

错误的格式（太短）：
SCT12345
```

---

## ⚙️ 配置到薅羊毛技能

### **方法1：告诉我SendKey**
把你的SendKey发给我，我会帮你配置。

### **方法2：自己配置**
编辑配置文件：
```bash
vi /root/.openclaw/workspace/skills/wool-gathering/assets/config_template.json
```

修改这部分：
```json
{
  "push_config": {
    "serverchan_enabled": true,
    "serverchan_key": "你的SendKey"
  }
}
```

---

## 🧪 测试推送

配置完成后，运行测试：

```bash
cd /root/.openclaw/workspace/skills/wool-gathering/scripts
python3 push_notification.py --title "测试推送" --content "Server酱配置成功！" --method serverchan
```

如果成功，你会在微信收到消息！

---

## 💰 免费额度说明

- **免费版**：每天5条消息
- **足够使用**：价格监控每天最多1-2条
- **升级版**：如果需要更多，可以付费升级

---

## ❓ 常见问题

**Q：没有收到推送怎么办？**
A：
1. 检查是否关注了「Server酱」服务号
2. 检查SendKey是否正确
3. 运行测试命令查看错误信息

**Q：每天5条够用吗？**
A：
- 自动签到：不需要推送（自己运行）
- 价格监控：每天最多1-2条降价提醒
- 完全够用！

**Q：如何获取更多额度？**
A：
1. 付费升级（9.9元/月，100条/天）
2. 使用PushPlus（免费200条/天）

---

## 📞 下一步

1. 访问：https://sct.ftqq.com/
2. 微信扫码登录
3. 复制SendKey
4. 把SendKey告诉我

我会帮你：
- 更新配置文件
- 测试推送功能
- 集成到价格监控

---

**注册链接**: https://sct.ftqq.com/
**预计耗时**: 3分钟
**难度**: ⭐（非常简单）

---

**最后更新**: 2026-03-03
