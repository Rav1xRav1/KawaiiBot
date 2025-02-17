from datetime import datetime

import json
import requests


class Discord:
    def __init__(self, **url):
        # 初期化メソッド。渡されたURLをインスタンス変数に保存する
        self.url = url

    # Discordにメッセージを送信するメソッド
    def send_message(self, sent_to, content="", line_id="", username="", usericon=""):
        main_content = {
            "avatar_url": usericon,
            "username": username,
            "content": content
        }

        headers = {'Content-Type': 'application/json'}
        
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "send_message : " + "webhookに送信します", main_content)

        # おすすめの転送または直貼りにURLコンテンツを送信する
        requests.post(self.url[sent_to], json.dumps(main_content), headers=headers)

        # おすすめ行きでないならNoneを返す
        if sent_to != "OSUSUME":
            return None

        # line_idと連携しているDiscordのwebhookURLを取得する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "send_message : " + "line_idと連携しているDiscordのwebhookURLを取得します")
        response = requests.get(f"http://userconfig:5002/read_config", params={"user_id": line_id})
        if "discord_webhook_url" not in response.json():  # チャンネルIDがない場合はNoneを返す
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "send_message : " + "webhookURLが見つかりませんでした")
            return None
        
        # line_idと連携しているDiscordのwebhookURLにコンテンツを送信する
        discord_webhook_url = response.json()["discord_webhook_url"]
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "send_message : " + "line_idと連携しているDiscordのwebhookURLにも送信します", discord_webhook_url)
        requests.post(discord_webhook_url, json.dumps(main_content), headers=headers)
    
    # 評価用のメッセージ送信をリクエストするメソッド
    def send_eval(self, content, user_id, user_name, user_icon):
        data = {
            "channel_id": "1333781222047875102",  # 固定のチャンネルID
            "content": content,
            "user_id": user_id,
            "user_name": user_name,
            "user_icon": user_icon
        }

        # ローカルサーバーに評価リクエストを送信する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "send_eval : " + "管理botに評価ボタンリクエストを送信します", data)
        res = requests.post("http://reactionbot:5001/eval", json=data)
        # サーバーからのレスポンスを出力する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "send_eval : " + "サーバレスポンス : " + str(res.json()))
