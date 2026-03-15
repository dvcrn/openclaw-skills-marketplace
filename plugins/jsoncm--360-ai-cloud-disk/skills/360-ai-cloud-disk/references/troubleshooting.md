# 故障排查

## 常见问题

### 问题 1: `ModuleNotFoundError: No module named 'dotenv'`

**解决方案:**
```bash
pip3 install python-dotenv
```

### 问题 2: HTTP 模式连接失败

**原因**: 网络问题或 API 端点配置错误

**解决方案:**
```bash
# 检查网络连接
curl -I $MCP_HTTP_URL

# 检查环境变量
echo $MCP_HTTP_URL
echo $API_KEY
```

### 问题 3: npx 模式下载失败

**原因**: 网络问题或包名错误

**解决方案:**
```bash
# 检查包名是否正确
npx $MCP_NPX_PACKAGE --version

# 手动测试下载
npx @your-org/your-mcp-server --help
```

### 问题 4: `API Error: 401 Unauthorized`

**原因**: API_KEY 无效或未配置

**解决方案:**
```bash
# 检查环境变量
echo $API_KEY

# 或检查 .env 文件
cat .env | grep API_KEY
```

### 问题 5: 工具调用超时

**原因**: MCP Server 启动慢或网络延迟

**解决方案:**
- HTTP 模式：增加 `MCP_HTTP_TIMEOUT`
- npx 模式：修改 executor.py 中的 timeout 参数
- 检查网络连接
- 确认 MCP Server 正常运行

## 路径规范

- 文件路径必须以 `/` 开头（如 `/文档/test.txt`）
- 文件夹路径必须以 `/` 结尾（如 `/文档/`）
- 多个文件用 `|` 分隔（如 `/file1.txt|/file2.txt`）

## 安全注意事项

1. **API 密钥安全**
   - ❌ 不要将 `API_KEY` 提交到代码仓库
   - ❌ 不要在日志中打印 `API_KEY`
   - ✅ 使用 `.env` 文件管理敏感信息
   - ✅ 将 `.env` 加入 `.gitignore`

2. **数据操作风险**
   - ⚠️ `file-move`、`file-rename` 会直接修改云盘文件结构
   - ⚠️ 操作前建议先用 `file-list` 确认路径
   - ⚠️ 批量操作时特别注意路径格式
