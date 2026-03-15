# Claw\_OpenWebUI\_API

讓 OpenClaw 整合 Open WebUI RAG 知識庫 API。

## 功能

* 📤 上傳文件到知識庫
* 🔍 搜尋知識庫
* 💬 對話時自動引用知識庫
* 📊 列出已上傳檔案

## 前置需求

1. Open WebUI 已安裝並運行
2. 取得 API Token
3. Python 3 + requests 函式庫

## 安裝

```bash
# 安裝 requests
pip install requests

# 設定環境變數
export OPENWEBUI\_URL="http://你的伺服器IP:3000"
export OPENWEBUI\_API\_KEY="你的API\_Token"
```

## 使用方式

### 上傳檔案

```bash
python3 scripts/upload.py --file document.pdf
```

### 搜尋知識庫

```bash
python3 scripts/search.py --query "關鍵字"
```

### 對話

```bash
python3 scripts/chat.py --message "你好"
```

### 列出檔案

```bash
python3 scripts/list\_files.py
```

## 取得 API Token

1. 登入 Open WebUI
2. 管理員開通API功能 →進入設定 → 帳號
3. 產生 API Token

## 授權

MIT License

