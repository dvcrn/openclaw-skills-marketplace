---
name: bit
description: "說明 bit-cli skill 的用途、安裝、必要設定與故障排查。"
---

# Bit CLI Skill（純說明型）

## Skill 用途與觸發情境

- 用途：提供 Bit URL Shortener CLI（`bit`）的使用入口，協助建立、查詢、更新、刪除短網址與查看點擊資料。
- 觸發情境：
- 使用者提到「短網址」、「bit-cli」、「bit create/list/get/update/delete/clicks」等需求。
- 使用者想用 OpenClaw 執行 Bit API 相關操作。
- 使用者需要確認 Bit API 是否可用（例如健康檢查）。

## 安裝指令（或 GitHub 連結到安裝章節）

- GitHub（本專案）：`https://github.com/ParinLL/bit-cli`
- README 安裝章節：`https://github.com/ParinLL/bit-cli#build-locally`
- 安全提醒：從原始碼建置前，先檢視來源 repo 內容與版本是否可信。
- 安裝指令：

```bash
git clone https://github.com/ParinLL/bit-cli.git
cd bit-cli
go build -o bit .
sudo mv bit /usr/local/bin/
```

- 不使用 `sudo` 的替代方式（安裝到使用者目錄）：

```bash
git clone https://github.com/ParinLL/bit-cli.git
cd bit-cli
go build -o bit .
mkdir -p "$HOME/.local/bin"
mv bit "$HOME/.local/bin/"
export PATH="$HOME/.local/bin:$PATH"
```

## 必要環境變數 / 權限

- 必要環境變數：
- `BIT_API_KEY`（必填）：Bit API 驗證金鑰。
- `BIT_API_URL`（選填）：Bit API Base URL，預設 `http://localhost:4000`。
- 權限需求：
- `bit` 可執行檔需在 PATH 中可被呼叫。
- 若用 `sudo mv` 安裝到 `/usr/local/bin`，需要系統管理員權限。
- 若目標 API 不是本機，需具備對該 API 的網路連線能力。

## 常見錯誤排查

- `bit: command not found`
- 原因：CLI 尚未安裝或不在 PATH。
- 排查：重新 `go build` 並確認 `which bit` 有輸出路徑。
- `401 Unauthorized` / `403 Forbidden`
- 原因：`BIT_API_KEY` 缺失或錯誤。
- 排查：重新設定 `BIT_API_KEY`，並確認伺服器端該 key 仍有效。
- `connection refused` / timeout
- 原因：`BIT_API_URL` 錯誤、Bit 服務未啟動、或網路不可達。
- 排查：先用 `bit ping` 測試，並確認 API 服務狀態與 URL。
- 指令執行成功但資料異常
- 原因：目標 ID 不存在、資料已刪除、或更新內容格式錯誤。
- 排查：先 `bit list` / `bit get <id>` 驗證資料狀態，再重試操作。
