# 发布到 ClawHub 指南

## 准备发布

1. **确保文件完整**
   - SKILL.md - 技能说明文档
   - README.md - 项目介绍
   - package.json - 元数据
   - config.example.json - 示例配置
   - scripts/private-vault.sh - 加密脚本

2. **检查脚本权限**
   ```bash
   chmod +x scripts/private-vault.sh
   ```

3. **测试加密解密**
   ```bash
   ./scripts/private-vault.sh encrypt "test" "hello"
   ./scripts/private-vault.sh decrypt "test" "ENC[...]"
   ```

## 发布步骤

### 方式 1: 使用 clawhub CLI

```bash
# 登录 clawhub
clawhub login

# 发布技能
clawhub publish

# 或者指定版本
clawhub publish --version 1.0.0
```

### 方式 2: 手动上传到 GitHub

1. 创建 GitHub 仓库
2. 推送技能文件
3. 在 ClawHub 提交你的技能链接

### 方式 3: 打包分享

```bash
# 打包技能
tar -czf private-chat-v1.0.0.tar.gz private-chat/

# 用户可以手动安装
tar -xzf private-chat-v1.0.0.tar.gz -C ~/.openclaw/workspace/skills/
```

## 版本更新

更新 `package.json` 中的版本号，然后重新发布：

```bash
clawhub publish --version 1.1.0
```

## 社区贡献

欢迎提交 Issue 和 PR！

## 注意事项

- 不要提交 `config.json`（包含用户敏感配置）
- 确保 `.gitignore` 包含 config.json
- 测试通过后再发布
