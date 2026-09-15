# LINE Claude Bot

LINE 官方帳號連接 Claude API 的聊天機器人。

## 技術棧

- Python 3.11
- Flask（Web 伺服器）
- LINE Bot SDK（Webhook 處理）
- Anthropic SDK（Claude API）
- Render（部署平台）

## 本地測試

```bash
pip install -r requirements.txt
cp .env.example .env  # 填入你的環境變數
python app.py
```

## 部署到 Render

1. Push 這份程式碼到 GitHub
2. 在 Render 建立 Web Service，連接 GitHub repo
3. 設定環境變數（見 .env.example）
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`

## 設定 Webhook

在 LINE Developers 後台：
- Webhook URL: `https://your-app-name.onrender.com/callback`
- 啟用 Webhook
