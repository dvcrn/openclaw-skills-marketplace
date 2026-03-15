# Server酱推送配置完成 ✅

**配置时间**: 2026-03-03
**SendKey**: SCT318129TjbbZCb4uk6oCF42SQEHefQ6Y
**状态**: ✅ 已启用

---

## ✅ 配置内容

```json
{
  "push_config": {
    "enabled": true,
    "serverchan_enabled": true,
    "serverchan_key": "SCT318129TjbbZCb4uk6oCF42SQEHefQ6Y"
  }
}
```

---

## 🧪 测试结果

```
✅ Server酱推送成功
```

测试消息已发送到微信！

---

## 📊 功能集成

### **1. 价格监控集成**
- ✅ 降价自动推送
- ✅ 推送内容包括：
  - 商品名称
  - 当前价格
  - 平均价格
  - 降价幅度
  - 购买链接

### **2. 推送格式示例**

```
🔔 商品降价提醒：Apple iPhone 15 Pro Max 256GB

💰 当前价格：¥9499
📊 平均价格：¥9943.07
📉 降价幅度：4.5%

🔗 购买链接：https://item.jd.com/100012043978.html

---
💰 薅羊毛系统自动监控
⏰ 2026-03-03 16:35:00
```

---

## 🚀 使用方法

### **方法1：运行监控脚本（带推送）**

```bash
cd /root/.openclaw/workspace/skills/wool-gathering/scripts
python3 price_monitor_with_push.py
```

### **方法2：手动发送推送**

```bash
python3 push_notification.py --title "标题" --content "内容" --method serverchan
```

---

## 📝 添加监控商品

编辑配置文件：
```bash
vi /root/.openclaw/workspace/skills/wool-gathering/assets/config_template.json
```

添加商品：
```json
{
  "items": [
    {
      "name": "iPhone 15 Pro Max",
      "platform": "jd",
      "item_id": "100012043978",
      "url": "https://item.jd.com/100012043978.html",
      "threshold": 0.9
    },
    {
      "name": "AirPods Pro 2",
      "platform": "taobao",
      "item_id": "560852934047",
      "url": "https://item.taobao.com/item.htm?id=560852934047",
      "threshold": 0.85
    }
  ]
}
```

**threshold说明**：
- `0.9` - 降价到90%时推送（即降价10%）
- `0.85` - 降价到85%时推送（即降价15%）
- `0.8` - 降价到80%时推送（即降价20%）

---

## 💰 免费额度

- ✅ **每天5条**消息
- ✅ 价格监控每天最多1-2条
- ✅ **完全够用！**

---

## ⏰ 定时任务（可选）

### **添加到青龙面板**

```bash
# 进入青龙容器
docker exec -it qinglong /bin/sh

# 添加定时任务（每小时检查一次价格）
echo "0 * * * * python3 /root/.openclaw/workspace/skills/wool-gathering/scripts/price_monitor_with_push.py" >> /ql/data/config/crontab.list
```

---

## 🔧 已集成的脚本

1. ✅ **price_monitor_with_push.py** - 价格监控（带推送）
2. ✅ **push_notification.py** - 推送工具
3. ✅ **spider_unified.py** - 统一爬虫（可添加推送）

---

## 📊 系统状态

| 功能 | 状态 | 说明 |
|------|------|------|
| **Server酱推送** | ✅ 已启用 | SendKey已配置 |
| **价格监控** | ✅ 已集成 | 降价自动推送 |
| **自动签到** | ✅ 已上线 | 每天8:00 |
| **数据库** | ✅ 正常 | SQLite |

---

## 🎯 下一步

### **可以立即使用**
1. ✅ 添加监控商品到配置文件
2. ✅ 运行 `python3 price_monitor_with_push.py`
3. ✅ 等待降价推送

### **可选优化**
1. ⏳ 添加定时任务（每小时自动检查）
2. ⏳ 配置更多推送方式（备选）

---

## 📞 常见问题

**Q：为什么没有收到推送？**
A：
1. 确认已关注「Server酱」服务号
2. 检查是否真的降价（threshold设置）
3. 查看运行日志

**Q：如何修改推送阈值？**
A：编辑配置文件中的 `threshold` 值（0.8-0.95）

**Q：如何关闭推送？**
A：设置 `push_config.enabled = false`

---

**配置文件**: `/root/.openclaw/workspace/skills/wool-gathering/assets/config_template.json`
**监控脚本**: `/root/.openclaw/workspace/skills/wool-gathering/scripts/price_monitor_with_push.py`

---

**最后更新**: 2026-03-03
**状态**: ✅ 配置完成，可以使用
