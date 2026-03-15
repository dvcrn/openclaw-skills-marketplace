# 🎉 browser-toggle v1.0.0 发布

> 一键启用/禁用 OpenClaw 内置浏览器，无需手动修改配置文件

---

## ✨ 功能特性

- ✅ **一键切换** - 无需手动编辑 `openclaw.json`
- ✅ **自动备份** - 修改前自动备份配置
- ✅ **失败恢复** - 配置失败可快速从备份恢复
- ✅ **跨平台** - 支持 Linux/macOS/Windows
- ✅ **无头模式** - 支持后台运行（不显示浏览器窗口）
- ✅ **独立空间** - 不访问个人浏览器数据

---

## 🚀 快速开始

### 安装

```bash
# 下载
wget https://github.com/your-username/browser-toggle/releases/download/v1.0.0/browser-toggle-v1.0.0.tar.gz

# 解压
tar -xzf browser-toggle-v1.0.0.tar.gz
cd browser-toggle-v1.0.0

# 安装
bash setup.sh
```

### 使用

```bash
# 启用内置浏览器
openclaw-browser --enable
openclaw gateway restart

# 查看状态
openclaw-browser --status

# 禁用
openclaw-browser --disable
openclaw gateway restart
```

---

## 📋 变更日志

### v1.0.0 (2026-02-28)

**新增：**
- ✅ 一键启用/禁用内置浏览器
- ✅ 自动备份配置文件
- ✅ 支持可视化/无头模式切换
- ✅ 从备份恢复功能
- ✅ 完整的文档和使用指南

**改进：**
- ✅ 自动检测 Chrome 安装路径
- ✅ 友好的命令行界面
- ✅ 详细的错误提示

---

## 📦 文件清单

| 文件 | 说明 |
|------|------|
| `browser-toggle-v1.0.0.tar.gz` | Skill 发布包 (8.1 KB) |
| `browser_toggle.py` | 主程序 |
| `setup.sh` | 安装脚本 |
| `README.md` | 项目说明 |
| `INSTALL.md` | 安装指南 |
| `使用指南.md` | 详细使用文档 |
| `SHARE.md` | 分享说明 |

---

## 🔧 系统要求

- **OpenClaw:** v2026.2.26+
- **Python:** 3.8+
- **Chrome/Chromium:** 已安装
- **操作系统:** Linux / macOS / Windows

---

## 📚 文档

- [README.md](https://github.com/your-username/browser-toggle/blob/main/README.md) - 项目说明
- [INSTALL.md](https://github.com/your-username/browser-toggle/blob/main/INSTALL.md) - 安装指南
- [使用指南.md](https://github.com/your-username/browser-toggle/blob/main/使用指南.md) - 详细使用文档

---

## 🐛 已知问题

暂无

---

## 📞 反馈与支持

- **问题反馈：** https://github.com/your-username/browser-toggle/issues
- **讨论区：** https://github.com/openclaw/openclaw/discussions
- **文档：** https://docs.openclaw.ai

---

## 📄 许可证

MIT License

---

## 🔗 相关链接

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Skill Hub](https://clawhub.com)

---

**🎊 感谢使用！**
