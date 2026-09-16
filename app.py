"""
LINE Claude Bot — Webhook 伺服器
<<<<<<< HEAD
接收 LINE 訊息 → 搜尋網路 → 呼叫 Claude API → 回覆使用者
"""
import os
=======
接收 LINE 訊息 → 呼叫 Claude API → 回覆使用者
"""
import os
import json
import hashlib
import hmac
import base64
>>>>>>> 081e1c4a13651547825e0b59c6d3ad3fee52e45a
from http import HTTPStatus
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, TextMessage, ReplyMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import anthropic
<<<<<<< HEAD
from duckduckgo_search import DDGS
=======
>>>>>>> 081e1c4a13651547825e0b59c6d3ad3fee52e45a

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


<<<<<<< HEAD
# ─── 搜尋函式 ─────────────────────────────────────────────
def search_web(query, max_results=3):
    """使用 DuckDuckGo 搜尋網路"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if results:
                # 組合搜尋結果
                search_text = "搜尋結果：\n\n"
                for i, r in enumerate(results, 1):
                    search_text += f"{i}. {r['title']}\n{r['body']}\n來源: {r['href']}\n\n"
                return search_text
        return "找不到相關結果"
    except Exception as e:
        return f"搜尋發生錯誤: {str(e)}"


def should_search(text):
    """判斷是否需要搜尋（簡單關鍵字判斷）"""
    search_keywords = ["搜尋", "查找", "查詢", "最新", "現在", "今天", "最近",
                       "什麼是", "是什麼", "怎麼", "如何", "為什麼", "誰是"]
    return any(keyword in text for keyword in search_keywords)


# ─── 訊息處理 ─────────────────────────────────────────────
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """收到文字訊息時，搜尋網路、呼叫 Claude 並回覆"""
=======
# ─── 訊息處理 ─────────────────────────────────────────────
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """收到文字訊息時，呼叫 Claude 並回覆"""
>>>>>>> 081e1c4a13651547825e0b59c6d3ad3fee52e45a
    user_text = event.message.text
    reply_token = event.reply_token

    print(f"收到訊息: {user_text}")

    try:
<<<<<<< HEAD
        # 判斷是否需要搜尋
        if should_search(user_text):
            print(f"觸發網路搜尋: {user_text}")
            search_results = search_web(user_text)
            # 將搜尋結果附帶給 Claude
            prompt = f"用戶問題：{user_text}\n\n網路搜尋結果：\n{search_results}\n\n請根據以上搜尋結果回答用戶的問題。如果搜尋結果不夠，可以用你自己的知識補充。"
        else:
            prompt = user_text

        # 呼叫 Claude API（透過第三方代理）
=======
        # 呼叫 Claude API
>>>>>>> 081e1c4a13651547825e0b59c6d3ad3fee52e45a
        response = claude_client.messages.create(
            model="glm-5.2",
            max_tokens=1024,
            messages=[
<<<<<<< HEAD
                {"role": "user", "content": prompt}
=======
                {"role": "user", "content": user_text}
>>>>>>> 081e1c4a13651547825e0b59c6d3ad3fee52e45a
            ],
        )
        reply_text = response.content[0].text

    except Exception as e:
<<<<<<< HEAD
        print(f"API error: {e}")
=======
        print(f"Claude API error: {e}")
>>>>>>> 081e1c4a13651547825e0b59c6d3ad3fee52e45a
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
