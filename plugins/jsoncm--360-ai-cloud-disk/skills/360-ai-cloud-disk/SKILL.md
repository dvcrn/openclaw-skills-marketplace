---
name: 360-ai-cloud-disk
description: "360 AI云盘文件管理工具"
---

# 360 AI Cloud Disk

360 AI云盘文件管理工具

## 功能列表

- **file-list**: 获取云盘指定路径下的文件和文件夹列表，支持分页查询。返回文件名、大小、创建时间、修改时间等详细信息。
- **file-search**: 在云盘中根据关键词搜索文件和文件夹，支持按文件类型筛选和分页查询。返回符合条件的文件详细信息。
- **make-dir**: 在云盘中创建新文件夹，支持指定路径。
- **file-move**: 移动云盘中的文件或文件夹到指定位置。支持批量移动多个文件。
- **file-rename**: 重命名云盘中的文件或文件夹。
- **file-share**: 生成云盘文件的分享链接。支持批量生成多个文件的分享链接。
- **file-save**: 通过URL或文本内容保存文件到云盘
- **file-upload-stdio**: 将本地文件上传到云盘指定路径。支持批量上传多个文件。
- **user-info**: 获取360AI云盘用户详细信息。
- **get-download-url**: 获取云盘中文件的下载链接。可以通过文件NID或路径获取。

## 快速开始

1. 获取 API Key: [360 AI云盘 MCP 控制台](https://www.yunpan.com/v2/mcp)
2. 配置环境变量: `export API_KEY="your_key"`

## 调用方式

```bash
python3 executor.py <tool-name> [param1=value1] [param2=value2]
```

## 文档

- [工具详细参数](references/tools.md)
- [配置说明](references/configuration.md)
- [故障排查](references/troubleshooting.md)
