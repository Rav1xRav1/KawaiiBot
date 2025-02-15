from line_bot_base import LineBot
from sent_to_discord import Discord
from datetime import datetime
import os, requests

# 環境変数から設定を読み込み
ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")


class SharingBot(LineBot):
    def __init__(self, access_token, channel_secret):
        super().__init__(access_token, channel_secret)
        self.discord = Discord(
            OSUSUME="https://discord.com/api/webhooks/1333781563661619250/PwPkzJXcNK9KEZhwEOAJnMsXQ15BJCDD9PYViYCUkJUu2BHCwkI8udLBNeWJT3pwdo6Y",
            JOINLINE="https://discord.com/api/webhooks/1334014871632740403/UfWoJccnAKJ-sg9lxGHGw6y8cVyfEG33BSQs6_7ritCOyhp9aGC1mp2Cez_pwpAiZmf-"
        )

    def text_message(self, event):
        user_message = event.message.text

        # Discordにメッセージを送信する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text_message : " + "Discordのおすすめに送信します")
        user_name = self.get_username(event.source.user_id)
        user_icon = self.get_usericon(event.source.user_id)

        self.discord.send_message(sent_to="OSUSUME",
                                  content=user_message, 
                                  line_id=event.source.user_id,
                                  username=user_name,
                                  usericon=user_icon)
        
        # 送信したメッセージに対して評価ボタンを送信する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text_message : " + "評価ボタンを送信します")
        self.discord.send_eval(content=user_message,
                               user_id=event.source.user_id,
                               user_name=user_name,
                               user_icon=user_icon)
    
    def follow_message(self, event):
        # Discordにメッセージを送信する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "follow_message : " + "フォローイベントを検知しました")
        user_name = self.get_username(event.source.user_id)
        user_icon = self.get_usericon(event.source.user_id)
        self.discord.send_message(sent_to="JOINLINE",
                                content=f"{user_name} さんがLINEに参加しました！", 
                                username=user_name,
                                usericon=user_icon)
    
    def unfollow_message(self, event):
        # Discordにメッセージを送信する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "unfollow_message : " + "フォロー解除イベントを検知しました")
        user_name = self.get_username(event.source.user_id)
        user_icon = self.get_usericon(event.source.user_id)
        self.discord.send_message(sent_to="JOINLINE",
                                  content=f"{user_name} さんがLINEから離脱しました！", 
                                  username=user_name,
                                  usericon=user_icon)

if __name__ == "__main__":
    bot = SharingBot(ACCESS_TOKEN, CHANNEL_SECRET)
    app = bot.create_app()
    app.run(host='0.0.0.0', port=5000)
