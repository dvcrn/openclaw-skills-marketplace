## WebDav Usage Guide (使用指南)

Drive Configuration is automatically loaded from `config.json`. (云盘配置从 `config.json` 自动加载。)

##### WebDAV Config
| Key (参数名) | Description (说明) |
| :--- | :--- |
| `user` | WebDAV Account (WebDAV 账号) (usually an email address). |
| `password` | **App Password (应用授权码)**. Note: Services like Nutstore require a dedicated app password, not the login password. (注意：很多服务，如坚果云，需要使用专用的应用密码而非登录密码。) |
| `url` | WebDAV Server URL (WebDAV 服务器完整 API 地址) (e.g., `https://dav.jianguoyun.com/dav/`). |


## Quickly Usage (快速使用)

**Script (脚本):** `scrips/webdav_drive_tools.py`

### Global Options (通用参数)
- `--name <config_name>`: Specify the connection name or index in `config.json` (指定 `config.json` 中的连接名称或索引).

```shell
# List Directory (列出目录内容)
python scrips/webdav_drive_tools.py --name webdavDrive ls /Photos

# Upload File (上传本地文件)
python scrips/webdav_drive_tools.py --name webdavDrive put ./img.jpg /Photos/img.jpg

# Download File (下载远程文件)
python scrips/webdav_drive_tools.py --name webdavDrive get /Photos/img.jpg ./img.jpg

# Create Directory (创建远程目录)
python scrips/webdav_drive_tools.py --name webdavDrive mkdir /Documents/Work

# Delete File or Directory (删除远程文件或目录)
python scrips/webdav_drive_tools.py --name webdavDrive rm /Photos/old_file.txt
python scrips/webdav_drive_tools.py --name webdavDrive rm /Photos/OldFolder

# Rename or Move (重命名或移动)
python scrips/webdav_drive_tools.py --name webdavDrive mv /old_name.txt /new_name.txt

# Search Recursively (递归搜索关键字)
python scrips/webdav_drive_tools.py --name webdavDrive find keyword --path /

# **Handling Spaces & Special Characters (处理空格和特殊字符)**: If the filename or path contains spaces or special characters (like Chinese), you **MUST** wrap the path in double quotes (`"path"`). (如果文件名或路径中包含空格或特殊字符（如中文），您**必须**使用双引号包裹路径。)
python scrips/webdav_drive_tools.py --name webdavDrive get "周杰伦 - Intro.flac" "./周杰伦 - Intro.flac"

```