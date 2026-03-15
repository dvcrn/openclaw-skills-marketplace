---
name: drive-tools
description: "Drive Tools (云盘工具)."
---

# drive-tools

This `drive-tools` skill helps you connect and manage your personal drives.

## Quick Install (快速安装)
```
npx degit SmileTM/s-drive-client/skills/drive-tools drive-tools
```

## Directory Structure (目录结构)

```
drive-tools
├── SKILL.md                    # Skill documentation (技能说明文档)
├── config.json                 # Configuration file (配置文件)
├── ftp_usage_guide.md          # FTP usage guide (FTP 使用指南)
├── smb_usage_guide.md          # SMB usage guide (SMB 使用指南)
├── webdav_usage_guide.md       # WebDAV usage guide (WebDAV 使用指南)
└── scripts/                    # Scripts directory (脚本目录)
    ├── ftp_drive_tools.py      # FTP drive tools (FTP 云盘工具)
    ├── smb_drive_tools.py      # SMB drive tools (SMB 云盘工具)
    └── webdav_drive_tools.py   # WebDAV drive tools (WebDAV 云盘工具)
```


## How to Use Drive Tools (如何使用云盘工具)

### Step 1: Understand Needs (第一步：了解需求)
Understand the user's needs, determine which type of drive needs to be accessed and managed, and guide the user to configure the connection information. 

(明确用户的需求，确认需要访问管理的是哪种类型的云盘，并引导用户配置相关连接信息。)

### Step 2: Load Usage Guide (第二步：加载对应类型使用指南)
According to the type of drive the user needs to access, load the usage guide for the corresponding drive type.

(根据用户需要访问云盘的类型，加载对应类型云盘使用指南。)

### Step 3: Guide Configuration of Drive Information (第三步：引导用户配置相关云盘信息)
Guide the user to configure the drive information based on the protocol requirements and record it in `config.json` following the specified format. Note: Do not modify existing values without user confirmation. Pay special attention to the `name` field, as it will be used to identify the drive in subsequent operations. 

(根据对应云盘类型所需配置信息，引导用户进行配置，并将相关信息按照相关格式记录到 `config.json`。注意不要改动配置文件中原有的值，如需改变一定要提示用户进行确认。尤其要注意`name`字段，用户后续会用name进行描述指定的云盘操作)

### Step 4: Execute Commands and Return Results (第四步：执行命令并返回结果)
Execute the corresponding commands based on user requirements and return the results. If the tool fails, notify the user immediately. 

(根据用户的需求，执行相应命令，并返回结果。若工具返回失败，应立即通知用户。)


## Usage Note (使用注意)

Please ensure you confirm the whitelist path before retrieving files. Do not use the default path for downloading. It is recommended to download files to the `downloads` directory within a whitelist path that has send permissions, such as the default whitelist path for `openclaw`: `~/.openclaw/media`.Please remember at all times. 

(请务必在获取文件前确认白名单路径，不要使用默认路径进行下载，最好将文件下载到有发送权限的白名单目录下的 `downloads` 中，比如 `openclaw` 的默认白名单路径 `~/.openclaw/media`。 请务必在任何时候都要记住。)

Example: FTP downloading `video.mp4`:
```bash
python scripts/ftp_drive_tools.py --name ftpDrive get /Movies/video.mp4 ~/.openclaw/media/downloads/video.mp4
```

## Usage Guide (使用指南)
- [smb](smb_usage_guide.md)
- [ftp](ftp_usage_guide.md)
- [webdav](webdav_usage_guide.md)


