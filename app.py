"""
LINE Claude Bot — Webhook 伺服器
接收 LINE 訊息 → 呼叫 Claude API → 回覆使用者
"""
import os
import json
import hashlib
import hmac
import base64
from http import HTTPStatus
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, TextMessage, ReplyMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import anthropic

# ─── 環境變數 ─────────────────────────────────────────────
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
API_BASE_URL = os.environ.get("API_BASE_URL", "https://yuanyuaicloud.cn")

# ─── 初始化 ───────────────────────────────────────────────
app = Flask(__name__)
handler = WebhookHandler(CHANNEL_SECRET)

# LINE SDK
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
line_api = ApiClient(configuration)
messaging_api = MessagingApi(line_api)

# Claude SDK（支援第三方 API）
claude_client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    base_url=API_BASE_URL,
)

# ─── Webhook 路由 ─────────────────────────────────────────
@app.route("/", methods=["GET"])
def health_check():
    """健康檢查 — Render 需要 200 回應"""
    return "LINE Claude Bot is running.", HTTPStatus.OK


@app.route("/callback", methods=["POST"])
def callback():
    """LINE Webhook 入口"""
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(403)
    except Exception as e:
        print(f"Webhook error: {e}")
        abort(500)

    return "OK", HTTPStatus.OK


# ─── 訊息處理 ─────────────────────────────────────────────
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """收到文字訊息時，呼叫 Claude 並回覆"""
    user_text = event.message.text
    reply_token = event.reply_token

    print(f"收到訊息: {user_text}")

    try:
        # 呼叫 Claude API
        response = claude_client.messages.create(
            model="glm-5.2",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": user_text}
            ],
        )
        reply_text = response.content[0].text

    except Exception as e:
        print(f"Claude API error: {e}")
        reply_text = f"抱歉，處理訊息時發生錯誤：{str(e)}"

    # 回覆 LINE
    try:
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )
    except Exception as e:
        print(f"LINE reply error: {e}")


# ─── 啟動伺服器 ───────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting LINE Claude Bot on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
