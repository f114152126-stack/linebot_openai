from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# ✅ 全域計數器
openai_call_count = 0


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global openai_call_count  # ← 要宣告 global

    text1 = event.message.text

    response = openai.ChatCompletion.create(
        model="gpt-5-nano",
        temperature=1,
        messages=[
            {
                "role": "system",
                "content": "你是一位活潑外向的飛行員，說話輕鬆幽默，喜歡用飛行比喻。"
            },
            {
                "role": "user",
                "content": text1
            }
        ]
    )

    # ✅ 每呼叫一次 +1
    openai_call_count += 1

    try:
        ret = response['choices'][0]['message']['content'].strip()
    except:
        ret = '發生錯誤！'

    # ✅ 把計數加到回覆中
    ret = f"{ret}\n\n✈️ 已起飛次數（呼叫OpenAI）：{openai_call_count}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ret)
    )


if __name__ == '__main__':
    app.run()
