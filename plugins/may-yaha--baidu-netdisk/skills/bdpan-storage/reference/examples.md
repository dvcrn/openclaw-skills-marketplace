# 使用示例

本文档包含 bdpan-storage 的详细使用示例。

---

## 上传并分享

### 示例 1: 上传并分享单个文件

```
用户: 帮我上传并分享 ./report.pdf
AI: [执行 bdpan upload ./report.pdf report.pdf]
    [执行 bdpan share report.pdf]

    上传并分享成功！
    链接: https://pan.baidu.com/s/1xxxxxxx
    提取码: abcd
    有效期: 7 天
```

### 示例 2: 上传并分享文件夹

```
用户: 把 ./project 文件夹上传并分享
AI: [执行 bdpan upload ./project/ project/]
    [执行 bdpan share project]

    文件夹上传并分享成功！
    链接: https://pan.baidu.com/s/1xxxxxxx
    提取码: efgh
    有效期: 7 天
```

### 示例 3: 上传到子目录

```
用户: 上传 ./data.tar.gz 到 backup 目录并分享
AI: [执行 bdpan upload ./data.tar.gz backup/data.tar.gz]
    [执行 bdpan share backup/data.tar.gz]

    上传并分享成功！
    链接: https://pan.baidu.com/s/1xxxxxxx
    提取码: ijkl
    有效期: 7 天
```

---

## 下载文件

### 示例 4: 下载单个文件

```
用户: 从网盘下载 report.pdf
AI: [执行 bdpan download report.pdf ./report.pdf]

    正在下载 report.pdf → ./report.pdf ...
    ✓ 下载成功
```

### 示例 5: 下载文件夹

```
用户: 把 backup 文件夹下载到本地
AI: [执行 bdpan download backup/ ./backup/]

    正在下载 backup/ → ./backup/ ...
    ✓ 下载成功
```

---

## 文件列表

### 示例 6: 查看已上传文件

```
用户: 查看我上传了哪些文件
AI: [执行 bdpan ls]

    类型    大小          修改时间              文件名
    ------  ------------  --------------------  --------
    目录     -            2026-02-20 10:30:00  backup
    文件    1.5 MB        2026-02-25 15:20:00  report.pdf
    文件    256 KB        2026-02-24 09:15:00  config.yaml

    共 3 项
```

### 示例 7: 查看子目录

```
用户: 查看 backup 目录下的文件
AI: [执行 bdpan ls backup]

    类型    大小          修改时间              文件名
    ------  ------------  --------------------  --------
    文件    2.1 GB        2026-02-19 08:00:00  data-2026-02-19.tar.gz
    文件    1.8 GB        2026-02-18 08:00:00  data-2026-02-18.tar.gz

    共 2 项
```

---

## JSON 输出（用于脚本）

### 示例 8: JSON 格式文件列表

```
用户: 列出所有文件名（JSON 格式）
AI: [执行 bdpan ls --json]

    输出:
    [
      {
        "Name": "report.pdf",
        "IsDir": false,
        "Size": 1536000,
        "Modified": "2026-02-25T15:20:00Z"
      },
      {
        "Name": "backup",
        "IsDir": true,
        "Size": 0,
        "Modified": "2026-02-20T10:30:00Z"
      }
    ]
```

### 示例 9: 使用 jq 处理输出

```bash
# 提取所有文件名
bdpan ls --json | jq -r '.[].Name'

# 只列出文件（排除目录）
bdpan ls --json | jq '.[] | select(.IsDir == false)'

# 按大小排序
bdpan ls --json | jq 'sort_by(.Size) | reverse'

# 检查文件是否存在
bdpan ls --json | jq -e '.[] | select(.Name == "target.txt")'
```

---

## 认证流程

### 示例 10: WebView 登录（GUI 环境）

```
用户: 帮我登录百度网盘
AI: [执行 bdpan login]

    正在启动授权流程...
    [WebView 窗口弹出]

    ✓ 登录成功！
    用户: username@baidu.com
```

### 示例 11: OOB 登录（非 GUI 环境）

```
用户: 帮我登录百度网盘
AI: [执行 bdpan login]

    正在启动授权流程...

    请在浏览器中打开以下链接完成授权:
    https://openapi.baidu.com/oauth/2.0/authorize?response_type=device_code&client_id=xxx&device_code=yyyyy

    授权成功后，浏览器会显示授权码，请复制并粘贴到这里:
    [等待用户输入...]

用户: [粘贴授权码] abc123xyz
AI: [处理授权码]

    ✓ 登录成功！
    用户: username@baidu.com
```

---

## 转存分享文件到网盘

### 示例 15: 转存分享链接（提取码在链接中）

```
用户: 帮我把这个链接转存到网盘 https://pan.baidu.com/s/1xxxxx?pwd=abcd
AI: [执行 bdpan transfer "https://pan.baidu.com/s/1xxxxx?pwd=abcd"]

    ✓ 转存成功！
    文件已保存到：我的应用数据/bdpan/
```

### 示例 16: 转存到指定目录

```
用户: 把 https://pan.baidu.com/s/1xxxxx 转存到 shared 目录，提取码是 efgh
AI: [执行 bdpan transfer "https://pan.baidu.com/s/1xxxxx" -p efgh -d shared/]

    ✓ 转存成功！
    文件已保存到：我的应用数据/bdpan/shared/
```

### 示例 17: 转存并查看结果（JSON）

```bash
bdpan transfer "https://pan.baidu.com/s/1xxxxx?pwd=abcd" --json
# 输出:
# {
#   "status": "success",
#   "remote_path": "shared-file.pdf",
#   "share_link": "https://pan.baidu.com/s/1xxxxx",
#   "file_count": 1
# }
```

---

## 高级用法

### 示例 12: 批量上传

```bash
# 上传当前目录所有 PDF 文件
for f in *.pdf; do
  bdpan upload "$f" "documents/$f"
done

# 上传并记录结果
for f in *.pdf; do
  echo "上传 $f..."
  bdpan upload "$f" "documents/$f" --json | jq '.'
done
```

### 示例 13: 自动备份脚本

```bash
#!/bin/bash
# 每日备份脚本

DATE=$(date +%Y-%m-%d)
BACKUP_FILE="backup-${DATE}.tar.gz"

# 打包
tar -czf "/tmp/${BACKUP_FILE}" ~/important-data/

# 上传
bdpan upload "/tmp/${BACKUP_FILE}" "backup/${BACKUP_FILE}"

# 清理
rm "/tmp/${BACKUP_FILE}"

echo "备份完成: ${BACKUP_FILE}"
```

### 示例 14: 检查上传状态

```bash
# 检查文件是否已上传
check_uploaded() {
  local file=$1
  bdpan ls --json | jq -e ".[] | select(.Name == \"${file}\")" > /dev/null
}

if check_uploaded "report.pdf"; then
  echo "文件已存在"
else
  echo "文件不存在，开始上传..."
  bdpan upload ./report.pdf report.pdf
fi
```
