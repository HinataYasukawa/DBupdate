import os
import json
from flask import Flask, request, abort
import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Flaskアプリケーションの設定
app = Flask(__name__)

# LINEメッセージの検証用ヘッダー
HEADERS = {
    'Authorization': f'Bearer {LINE_ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def add_to_notion(company_name, phase):
    url = f"https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "企業名": {"title": [{"text": {"content": company_name}}]},
            "選考フェーズ": {"rich_text": [{"text": {"content": phase}}]}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

@app.route("/webhook", methods=['POST'])
def webhook():
    body = request.get_json()
    events = body.get("events", [])
    
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            message_text = event["message"]["text"]
            
            # メッセージから企業名と選考フェーズを抽出（例として単純な処理）
            if "企業名：" in message_text and "次回選考フェーズ：" in message_text:
                lines = message_text.split("\n")
                company_name = lines[0].replace("■企業名：", "").strip()
                phase = lines[2].replace("■次回選考フェーズ：", "").strip()
                
                # Notionにデータを追加
                if add_to_notion(company_name, phase):
                    return "Notionに登録しました", 200
                else:
                    return "Notionへの登録に失敗しました", 500
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
