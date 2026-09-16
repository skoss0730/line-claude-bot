# LINE + Claude 聊天機器人 — 完整部署指南

> 建立日期：2026-09-15
> 狀態：基本框架完成，待修正第三方 API 模型名稱

---

## 📋 整體架構

```
LINE 官方帳號
    ↓ (使用者傳訊息)
Webhook → Render 雲端主機
    ↓ (呼叫 API)
第三方 Claude API (yuanyuaicloud.cn)
    ↓ (回傳回應)
LINE 官方帳號 (回覆使用者)
```

---

## 🔧 所需資源清單

| 資源 | 狀態 | 說明 |
|------|------|------|
| LINE 官方帳號 | ✅ 已有 | 需要 Channel Secret + Access Token |
| GitHub 帳號 | ✅ skoss0730 | 用於儲存程式碼 |
| 第三方 API | ✅ yuanyuaicloud.cn | Claude API 代理 |
| Render 帳號 | ✅ 已有 | 免費部署平台 |

---

## 📝 完整操作流程

### Phase 1：LINE Developers 後台設定

#### 1.1 取得 Channel Secret

```
LINE Developers 後台 → https://developers.line.biz/console/
→ 選擇 Channel → Basic settings 頁籤
→ Channel secret → 複製
```

格式：`2131d325e8da0bfabb45d647d30e880d`

#### 1.2 取得 Channel Access Token

```
LINE Developers 後台
→ 選擇 Channel → Messaging API 頁籤
→ Channel access token (long-lived)
→ 點「Issue」按鈕
→ 複製 Token
```

⚠️ **重要：如果機器人回覆失敗（403 invalid token），需要重新 Issue 新的 Token**

#### 1.3 設定 Webhook URL

```
Messaging API 頁籤
→ Webhook URL → 填入：https://你的應用名.onrender.com/callback
→ 點「Update」
→ 點「Verify」→ 應顯示 ✅ Success
```

#### 1.4 開關設定

| 設定 | 狀態 | 位置 |
|------|------|------|
| Use webhook | ✅ 開啟 | Messaging API 頁籤 |
| Auto-reply messages | ❌ 關閉 | Messaging API 頁籤 |

---

### Phase 2：建立 GitHub Repo

#### 2.1 建立 Repo

```
瀏覽器 → https://github.com/new
→ Repository name：line-claude-bot
→ Description：LINE Claude Bot
→ 選 Public（Render 免費方案需要）
→ 不要勾 Initialize（本地已有程式碼）
→ 點「Create repository」
```

#### 2.2 推送程式碼（在 PowerShell 中執行）

```powershell
cd C:\Users\Winnie\line-claude-bot

git init
git branch -M main
git add -A
git commit -m "feat: LINE Claude bot initial version"
git remote add origin https://github.com/skoss0730/line-claude-bot.git
git push -u origin main
```

⚠️ **注意：必須先 `cd` 到 `line-claude-bot` 資料夾，否則會報 `not a git repository`**

⚠️ **如果遠端有 README 衝突：**
```powershell
git pull origin main --allow-unrelated-histories --no-edit
git push -u origin main
```

---

### Phase 3：Render 部署

#### 3.1 建立 Web Service

```
Render Dashboard → https://dashboard.render.com
→ New ＋ → Web Service
→ Source Code → GitHub → 授權
→ 選擇 line-claude-bot repo → Connect
```

#### 3.2 設定

| 欄位 | 填入 |
|------|------|
| Name | `line-claude-bot` |
| Region | Singapore（離台灣近） |
| Branch | `main` |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |

#### 3.3 環境變數（Advanced 展開）

| Key | Value |
|-----|-------|
| `PORT` | `10000` |
| `CHANNEL_SECRET` | `2131d325e8da0bfabb45d647d30e880d` |
| `CHANNEL_ACCESS_TOKEN` | `（從 LINE Developers 取得的 Token）` |
| `ANTHROPIC_API_KEY` | `（第三方 API Key）` |
| `API_BASE_URL` | `https://yuanyuaicloud.cn` |

#### 3.4 部署

```
→ 點「Create Web Service」
→ 等待部署完成（約 2-5 分鐘）
→ 完成後會看到「line-claude-bot is live!」
```

---

### Phase 4：設定 LINE Webhook URL

部署完成後會得到網址：

```
https://line-claude-bot-gedx.onrender.com
```

回到 LINE Developers 後台：

```
Webhook URL → https://line-claude-bot-gedx.onrender.com/callback
→ Update → Verify → ✅ Success
```

---

### Phase 5：測試

1. 打開 LINE → 找到您的官方帳號
2. 傳送文字訊息
3. 等待回覆（首次可能需等 30 秒，Render 從休眠喚醒）

---

## 🐛 常見問題排查

### 1. 部署失敗：`Could not open requirements file`

**原因**：GitHub repo 中沒有 requirements.txt

**解法**：確認本地有 requirements.txt 並重新推送
```powershell
cd C:\Users\Winnie\line-claude-bot
git add -A
git commit -m "fix: add requirements.txt"
git push
```

### 2. Verify 失敗：`invalid token`

**原因**：Channel Access Token 無效或過期

**解法**：
1. LINE Developers → Messaging API → 重新 Issue Token
2. Render → Environment → 更新 CHANNEL_ACCESS_TOKEN
3. 回 LINE 後台重新 Verify

### 3. Webhook 200 但機器人不回覆

**原因**：Claude API 模型名稱不被第三方支援

**解法**：修改 app.py 中的 `model` 參數為第三方支援的模型名稱
```python
# 目前（可能不被支援）
model="claude-haiku-4-5-20251001"

# 改成第三方支援的名稱（需確認）
model="claude-3-haiku-20240307"
```

### 4. Render 休眠後要等

**原因**：免費版在 15 分鐘無請求後會自動休眠

**解法**：正常現象，有人發訊息後會自動喚醒（約 30 秒）

---

## 📁 專案檔案結構

```
line-claude-bot/
├── app.py              # 主程式（Flask + LINE Bot SDK + Claude API）
├── requirements.txt    # Python 相依套件
├── .env.example        # 環境變數範本（不含敏感資訊）
├── .gitignore          # Git 忽略清單
└── README.md           # 專案說明
```

---

## 🔑 模型名稱

| 提供者 | 模型名稱 |
|--------|----------|
| 第三方 yuanyuaicloud.cn | `glm-5.2` |

> 模型名稱在 app.py 第 77 行的 `model` 參數設定

---

## 🔐 安全提醒

- **不要**把 API Key、Token 推到 GitHub
- `.gitignore` 已排除 `.env` 檔案
- Render 的環境變數會自動遮蔽
- 正式使用時請重新產生所有 Key
