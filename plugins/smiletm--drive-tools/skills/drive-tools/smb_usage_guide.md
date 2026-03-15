## Usage Guide (使用指南)

Drive configuration is automatically loaded from `config.json`. (云盘配置从 `config.json` 自动加载。)

##### SMB
| Key (参数名) | Description (说明) |
| :--- | :--- |
| `user` | SMB Username (SMB 用户名). |
| `password` | SMB Password (SMB 密码). |
| `ip` | Server IP Address (服务器 IP 地址) (e.g., `192.168.1.100`). |
| `share` | **Share Name (共享名称)**. Shared folder name on the server (e.g., `C$` or `Downloads`). |
| `domain` | **Domain (域名)**. Default is `WORKGROUP`. Required for specific domain environments. (默认为 `WORKGROUP`。某些特定的域环境连接时需要指定。) |

## Quickly Usage (快速使用)

**Script (脚本):** `scrips/smb_drive_tools.py`

### Global Options (通用参数)
- `--name <config_name>`: Specify the connection name or index in `config.json` (指定 `config.json` 中的连接名称或索引).

```shell
# List Directory (列出目录内容)
python scrips/smb_drive_tools.py --name smbDrive ls /Documents

# Upload File (上传本地文件: local_path -> remote_path)
python scrips/smb_drive_tools.py --name smbDrive put ./data.zip /backups/data.zip

# Download File (下载远程文件: remote_path -> local_path)
python scrips/smb_drive_tools.py --name smbDrive get /movies/demo.mp4 ./demo.mp4

# Create Directory (创建远程目录)
python scrips/smb_drive_tools.py --name smbDrive mkdir /projects/new_folder

# Delete File or Directory (删除远程文件或目录)
# Use -d for directories (参数 -d 表示目标是目录)
python scrips/smb_drive_tools.py --name smbDrive rm /old_file.txt
python scrips/smb_drive_tools.py --name smbDrive rm /old_folder -d

# Rename or Move (重命名或移动: old_path -> new_path)
python scrips/smb_drive_tools.py --name smbDrive mv /old_name.txt /new_name.txt

# Search Recursively (递归搜索关键字)
python scrips/smb_drive_tools.py --name smbDrive find keyword --path /

# **Handling Spaces & Special Characters (处理空格和特殊字符)**: If the filename or path contains spaces or special characters (like Chinese), you **MUST** wrap the path in double quotes (`"path"`). (如果文件名或路径中包含空格或特殊字符（如中文），您**必须**使用双引号包裹路径。)
python scrips/smb_drive_tools.py --name smbDrive get "周杰伦 - Intro.flac" "./周杰伦 - Intro.flac"
```