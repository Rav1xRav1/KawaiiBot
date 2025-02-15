from flask import Flask, request, abort
from datetime import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, FollowEvent, UnfollowEvent, TextSendMessage

import secrets
import string
import requests

class LineBot:
    def __init__(self, access_token, channel_secret):
        self.line_bot_api = LineBotApi(access_token)
        self.handler = WebhookHandler(channel_secret)

    def create_app(self):
        app = Flask(__name__)

        @app.route("/callback", methods=['POST'])
        def callback():
            signature = request.headers['X-Line-Signature']
            body = request.get_data(as_text=True)
            app.logger.info("Request body: " + body)

            try:
                self.handler.handle(body, signature)
            except InvalidSignatureError:
                print("Invalid signature.")
                abort(400)

            return 'OK'

        @self.handler.add(MessageEvent, message=TextMessage)
        def handle_text_message(event):
            self.text_message(event)
    
        @self.handler.add(FollowEvent)
        def handle_follow_message(event):
            self.follow_message(event)
            # 追加されたときにDiscordと連携するためにランダムな文字列を送信する
            characters = string.ascii_letters + string.digits
            random_code = ''.join([secrets.choice(characters) for _ in range(16)])
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="/register " + random_code)
            )
            # ランダムな文字列をuserconfigに送信する
            profile = self.line_bot_api.get_profile(event.source.user_id)
            requests.post(
                "http://userconfig:5002/register",
                json={
                    "random_code": random_code,
                    "line_user_id": event.source.user_id,
                    "line_user_name": profile.display_name,
                    "line_picture_url": profile.picture_url
                }
            )
        
        @self.handler.add(UnfollowEvent)
        def handle_unfollow_message(event):
            self.unfollow_message(event)

        return app
    
    # ユーザIDを元にユーザ名を返すメソッド
    def get_username(self, user_id):
        # ユーザプロフィールからユーザ名を取得してファイルに記録する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_username : " + "ユーザ名を取得します")
        try:
            user_profile = self.line_bot_api.get_profile(user_id)
            user_display_name = user_profile.display_name
            requests.post("http://userconfig:5002/edit_config", json={"user_id": user_id, "conf": {"user_name": user_display_name}})
        except LineBotApiError as e:  # ブロックされた状態で読み込みに失敗したなら
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_username : " + "ブロックされておりユーザが見つかりませんでした")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_username : " + "Userconfigからユーザ名を取得します")
            try:
                # ユーザ名が記録されていないか探す
                response = requests.get("http://userconfig:5002/read_config", params={"user_id": user_id})
                user_display_name = response.json()["user_name"]
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_username : " + user_display_name + "を取得しました")
            except KeyError as e:
                # ユーザ名が記録されていないなら仮名を渡す
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_user_name : " + "ユーザ名が記録されていませんでした：No NAME")
                user_display_name = "No NAME"

        return user_display_name
    
    # ユーザIDを元にユーザのアイコンURLを返すメソッド
    def get_usericon(self, user_id):
        # ユーザのプロフィールからアイコンURLを取得してファイルに記録する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_usericon : " + "ユーザアイコンを取得します")
        try:
            user_profile = self.line_bot_api.get_profile(user_id)
            user_picture_url = user_profile.picture_url
            requests.post("http://userconfig:5002/edit_config", json={"user_id": user_id, "conf": {"picture_url": user_picture_url}})
        except LineBotApiError as e:  # ブロックされた状態で読み込みに失敗したなら
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_usericon : " + "ブロックされておりユーザが見つかりませんでした")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_usericon : " + "Userconfigからユーザアイコンを取得します")
            try:
                # ユーザ名が記録されていないか探す
                # user_picture_url = ec.read_user_config(user_id)["picture_url"]
                response = requests.get("http://userconfig:5002/read_config", params={"user_id": user_id})
                user_picture_url = response.json()["picture_url"]
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_usericon : " + user_picture_url + "を取得しました")
            except KeyError as e:
                # 無ければ何も返さない（defaultのアイコン）
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_usericon : " + "ユーザアイコンが記録されていませんでした：No ICON")
                return ""
        return user_picture_url
    
    # 以下のメソッドはサブクラスでオーバーライドされることを想定
    def text_message(self, event):
        pass  

    def follow_message(self, event):
        pass

    def unfollow_message(self, event):
        pass
