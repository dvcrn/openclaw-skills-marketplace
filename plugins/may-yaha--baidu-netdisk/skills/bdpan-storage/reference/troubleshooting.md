# 故障排除指南

本指南涵盖了使用 bdpan CLI 时的常见问题和解决方案。

---

## 认证问题

### Token 过期

**症状：**
```
错误: Token 过期
Error: Token expired
```

**解决方案：**
```bash
bdpan logout
bdpan login
```

### WebView 无法打开

**症状：** 登录过程中浏览器或 WebView 窗口未出现。

**解决方案：**
工具会自动降级到 OOB（Out-of-Band）模式，按以下步骤操作：

1. 复制控制台显示的授权链接：
   ```
   https://openapi.baidu.com/oauth/...?device_code=xxxxx
   ```

2. 在浏览器中打开该链接

3. 完成授权后，浏览器会显示授权码

4. 复制授权码并粘贴到命令行提示处

5. 按回车确认

**示例输出：**
```
请在浏览器中打开以下链接完成授权:
https://openapi.baidu.com/oauth/2.0/authorize?response_type=device_code&client_id=...&device_code=xxxxx

授权成功后，浏览器会显示授权码，请复制并粘贴到这里:
[等待用户输入授权码...]
```

### 授权后登录失败

**症状：** 授权页面完成但登录仍然失败。

**解决方案：**
```bash
# 清除配置并重试
rm ~/.config/bdpan/config.json
bdpan login
```

---

## 文件操作问题

### 路径不在允许范围

**症状：**
```
错误: 路径不在允许范围内
Error: Path not in allowed range
```

**解决方案：**
确保所有路径都在 `/apps/bdpan/` 目录下。

错误：
```bash
bdpan ls /my-documents
bdpan upload ./file.txt /other/file.txt
```

正确：
```bash
bdpan ls my-documents
bdpan upload ./file.txt my-documents/file.txt
```

### 使用中文路径导致下载/上传失败

**症状：**
```
错误: 文件不存在
# 实际原因：使用了 "/我的应用数据/bdpan/..." 而不是 "/apps/bdpan/..."
```

**说明：**
百度网盘界面中显示的 **"我的应用数据"** 是中文显示名，对应的 API 实际路径是 **`/apps`**。两个方向都需要映射：
- **调用命令时**：中文路径 → API 路径（`我的应用数据` → `/apps`）
- **展示给用户时**：API 路径 → 中文路径（`/apps` → `我的应用数据`）

**路径映射：**
| 用户可见名称 | API 实际路径 |
|-------------|-------------|
| 我的应用数据 | `/apps` |
| 我的应用数据/bdpan | `/apps/bdpan` |

**解决方案：**
调用命令时使用相对路径或英文 API 绝对路径，展示给用户时转换为中文名：

```bash
# ✅ 命令中使用 API 路径
bdpan download report.pdf ./report.pdf

# ✅ 展示给用户时使用中文名
# "文件已上传到：我的应用数据/bdpan/report.pdf"

# ❌ 命令中使用中文路径
bdpan download /我的应用数据/bdpan/report.pdf ./report.pdf

# ❌ 展示给用户时暴露 API 路径
# "文件已上传到：/apps/bdpan/report.pdf"
```

### 文件不存在

**症状：**
```
错误: 文件不存在
Error: File not found
```

**解决方案：**
1. 检查本地文件是否存在：
   ```bash
   ls -la <本地路径>
   ```
2. 检查远程文件是否存在：
   ```bash
   bdpan ls
   ```

### 上传/下载超时

**症状：** 操作耗时过长并超时。

**解决方案：**
1. 大文件可能需要最多 30 分钟
2. 检查网络连接稳定性
3. 对于非常大的文件，考虑先压缩/分割：
   ```bash
   # 上传前压缩
   tar -czf archive.tar.gz large-folder/
   bdpan upload archive.tar.gz backup/archive.tar.gz
   ```

### 转存失败

**症状：**
```
错误: 转存失败
Error: Transfer failed
```

**常见原因及解决方案：**

1. **分享链接已失效**：联系分享者重新生成链接
2. **提取码错误**：确认提取码是否正确
   ```bash
   # 提取码通过 -p 传入
   bdpan transfer "https://pan.baidu.com/s/1xxxxx" -p abcd
   # 或包含在链接中
   bdpan transfer "https://pan.baidu.com/s/1xxxxx?pwd=abcd"
   ```
3. **网盘空间不足**：清理网盘空间后重试

### 权限不足

**症状：**
```
错误: 权限不足
Error: Permission denied
```

**解决方案：**
1. 检查本地文件权限：
   ```bash
   ls -l <本地路径>
   ```
2. 确保您对目标目录有写入权限：
   ```bash
   ls -ld <目标目录>
   ```

---

## 安装问题

### 命令未找到

**症状：** `bdpan: command not found`

**解决方案：**
```bash
# 重新运行安装脚本
cd skills/tool/bdpan-storage
bash scripts/install.sh

# 或者检查 ~/.local/bin 是否在 PATH 中
echo $PATH

# 如果缺失则添加到 PATH（添加到 ~/.zshrc 或 ~/.bashrc）
export PATH="$HOME/.local/bin:$PATH"
```

### 下载了错误的架构

**症状：** 二进制文件无法运行或提示 "exec format error"

**解决方案：**
```bash
# 删除现有二进制文件
rm ~/.local/bin/bdpan

# 重新安装
cd skills/tool/bdpan-storage
bash scripts/install.sh
```

---

## JSON 输出问题

### 无效的 JSON 输出

**症状：** `--json` 输出无法被解析。

**解决方案：**
1. 确保 stdout 中没有错误消息
2. 检查输出中只有 JSON 内容
3. 使用 `jq` 验证：
   ```bash
   bdpan ls --json | jq .
   ```

---

## 平台特定问题

### macOS

#### Gatekeeper 阻止

**症状：** 无法打开应用，因为它来自身份不明的开发者。

**解决方案：**
```bash
xattr -d com.apple.quarantine ~/.local/bin/bdpan
```

### Linux

#### 缺少依赖

**症状：** 二进制文件运行失败，提示缺少库。

**解决方案：**
安装所需依赖（特定于发行版）：
```bash
# Debian/Ubuntu
sudo apt-get install libc6

# Fedora/RHEL
sudo dnf install glibc
```

### Windows (WSL)

#### 路径问题

**症状：** Windows 路径无法正常工作。

**解决方案：**
在 WSL 中始终使用 Unix 风格路径：
```bash
# 正确
bdpan upload ./file.txt file.txt

# 错误
bdpan upload .\\file.txt file.txt
```

---

## 获取帮助

### 检查版本

```bash
bdpan version
```

### 获取命令帮助

```bash
bdpan --help
bdpan upload --help
bdpan download --help
```

### 启用调试模式

```bash
# 检查配置位置
ls -la ~/.config/bdpan/

# 查看配置文件（如果存在）
cat ~/.config/bdpan/config.json
```
