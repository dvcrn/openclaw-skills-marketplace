# FTP Usage Guide (使用指南)

Drive configuration is automatically loaded from `config.json`. (云盘配置从 `config.json` 自动加载。)

## FTP Config
| Key (参数名) | Description (说明) |
| :--- | :--- |
| `user` | FTP Username (FTP 用户名). |
| `password` | FTP Password (FTP 密码). |
| `ip` | Server IP or Hostname (服务器 IP 或域名). |
| `port` | Port Number (端口号), default is `21`. |
| `tls` | Enable TLS (是否启用 TLS). `true` means using FTPS. |


## Quickly Usage (快速使用)

**Script (脚本):** `scrips/ftp_drive_tools.py`

### Global Options (通用参数)
- `--name <config_name>`: Specify the connection name or index in `config.json` (指定 `config.json` 中的连接名称或索引).

```shell
# List Directory (列出目录内容)
python scrips/ftp_drive_tools.py --name ftpDrive ls /Movies

# Upload File (上传本地文件)
python scrips/ftp_drive_tools.py --name ftpDrive put ./video.mp4 /Movies/video.mp4

# Download File (下载远程文件)
python scrips/ftp_drive_tools.py --name ftpDrive get /Movies/video.mp4 ./video.mp4

# Create Directory (创建远程目录)
python scrips/ftp_drive_tools.py --name ftpDrive mkdir /NewFolder

# Delete File or Directory (删除远程文件或目录)
# Use -d for directories (参数 -d 表示目标是目录)
python scrips/ftp_drive_tools.py --name ftpDrive rm /old.txt
python scrips/ftp_drive_tools.py --name ftpDrive rm /old_dir -d

# Rename or Move (重命名或移动)
python scrips/ftp_drive_tools.py --name ftpDrive mv /old.txt /new.txt

# Search Recursively (递归搜索关键字)
python scrips/ftp_drive_tools.py --name ftpDrive find keywords --path /

# **Handling Spaces & Special Characters (处理空格和特殊字符)**: If the filename or path contains spaces or special characters (like Chinese), you **MUST** wrap the path in double quotes (`"path"`). (如果文件名或路径中包含空格或特殊字符（如中文），您**必须**使用双引号包裹路径。)
python scrips/ftp_drive_tools.py --name ftpDrive get "周杰伦 - Intro.flac" "./周杰伦 - Intro.flac"


```
