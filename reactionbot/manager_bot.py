from flask import Flask, request, jsonify
from datetime import datetime
from discord.ext import commands
import discord  # Discordライブラリをインポート

import threading
import requests
import json
import os

from reaction_button import ReactionButton, DropdownView

token = os.environ.get("DISCORD_TOKEN")

app = Flask(__name__)

intents = discord.Intents.default()  # デフォルトのインテントを使用
intents.message_content = True  # メッセージ内容の受信を有効化
intents.messages = True  # メッセージの受信を有効化

# client = discord.Client(intents=intents)  # クライアントを作成
client = commands.Bot(command_prefix="/", intents=intents)  # Botを作成

@app.route("/eval", methods=["POST"])
def eval():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "eval : " + "評価ボタンリクエストを取得しました。ボタンを送信します")
    
    # ポストで送られたデータを取得する
    data = request.json
    channel_id = data.get("channel_id")
    content = data.get("content")
    user_id = data.get("user_id")
    user_name = data.get("user_name")
    user_icon = data.get("user_icon")

    loop = client.loop  # Discordクライアントのイベントループを取得
    # 非同期タスクとしてDiscordメッセージ送信処理をスケジュール
    user_data = {"user_id": user_id, "user_name": user_name, "user_icon": user_icon}
    loop.create_task(async_eval(channel_id, content, user_data))
    return jsonify({"status": "success"})  # 成功ステータスをJSONで返す

@client.event
async def on_ready():  # Botが準備完了したときのイベント
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_ready : " + "Discord Botが起動しました")

@client.event
async def on_message(message):  # メッセージを受信したときのイベント
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "受信しました :", message.content)
    # 自身が送信したメッセージには反応しないまたは特定のチャンネル以外は無視
    if message.author == client.user:
        return

    if not message.content.strip():  # メッセージが空の場合
        return None
    
    # もし「おすすめ（直貼り）」チャンネルなら
    if message.channel.id == os.getenv("OSUSUME_CHOKUHARI_CHANNEL_ID"):
        discord_channel_id = message.channel.id
        content = message.content
        discord_user_name = message.author.name

        loop = client.loop  # Discordクライアントのイベントループを取得
        # 非同期タスクとしてDiscordメッセージ送信処理をスケジュール
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "直貼りに評価ボタンを送信します")
        user_data = {
            "user_id": message.author.id,
            "user_name": discord_user_name,
            "user_icon": message.author.avatar.url
        }
        loop.create_task(async_eval(discord_channel_id, content, user_data))

        # 個人チャンネルに転送する機能
        # 送信したユーザのIDを取得
        discord_user_id = message.author.id

        # ユーザIDからラインのユーザIDを取得
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "Discord IDからLINE IDを取得します")
        response = requests.get("http://userconfig:5002/get_line_id", params={"discord_user_id": discord_user_id})
        line_user_id = response.json()

        # ラインユーザIDからdiscord webhook URLを取得
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "LINE IDからDiscord webhook URLを取得します")
        response = requests.get("http://userconfig:5002/read_config", params={"user_id": line_user_id})
        discord_webhook_url = response.json().get("discord_webhook_url")

        if discord_webhook_url is None:  # チャンネルIDがない場合はNoneを返す
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "webhookURLが見つかりませんでした")
            return None

        main_content = {
            "avatar_url": message.author.avatar.url,
            "username": discord_user_name,
            "content": content,
        }

        headers = {'Content-Type': 'application/json'}

        # おすすめの転送または直貼りにURLコンテンツを送信する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "webhookに送信します", main_content)
        requests.post(discord_webhook_url, json.dumps(main_content), headers=headers)

        return None
    
    # await client.process_commands(message)  # コマンドを処理
    # return None
    
    # もし「/media」というメッセージなら
    # チャンネルが「個人」というカテゴリの中のチャンネルか調べる
    if message.content.startswith("/media") and message.channel.category.name == "個人":
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "mediaコマンドを受信しました")
        # 履歴をlimit個取得して、リストにして逆順にする
        messages = [message async for message in  message.channel.history(limit=32)][::-1]

        # messagesからurlのみを取得する
        # <url>とすることによって埋め込みを表示させない
        urls = [f"<{message.content}>" for message in messages if message.content.startswith("http")]

        # メッセージを送信する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "mediaコマンドの結果を送信します")
        await message.channel.send("\n".join(urls))  # 改行で「urls」を結合して送信する
    
    # もし「register」から始まる文字列ならDiscordとLINEのアカウントを連携する
    elif message.content.startswith("/register") and message.channel.id == 1335131602925129770:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "registerコマンドを受信しました")
        # ランダムな文字列を取得する
        random_code = message.content.split(" ")[1]
        # ランダムな文字列からLINEのユーザ情報を取得する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "LINEのユーザ情報取得リクエストを送信します")
        response = requests.get("http://userconfig:5002/get_line_data", params={"random_code": random_code})
        line_data = response.json()
        # Discordのユーザ情報を取得する
        discord_user_id = message.author.id
        discord_user_name = message.author.name
        if message.author.avatar is None:
            discord_user_icon = None
        else:
            discord_user_icon = message.author.avatar.url
        # LINEとDiscordのユーザ情報を連携する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "LINEとDiscordのユーザ情報連携リクエストを送信します")
        response = requests.post(
            "http://userconfig:5002/edit_config",
            json={
                "user_id": line_data["line_user_id"],
                "conf": {
                    "line_user_name": line_data["line_user_name"],
                    "line_picture_url": line_data["line_picture_url"],
                    "discord_user_id": discord_user_id,
                    "discord_user_name": discord_user_name,
                    "discord_user_icon": discord_user_icon
                }
            }
        )
        # 連携が成功したら「連携が完了しました」と送信する
        if response.status_code == 200:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "連携が完了しました")
            await message.channel.send("連携が完了しました")
        else:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "連携に失敗しました")
            await message.channel.send("連携に失敗しました")
        
        # 個人チャンネルを作成する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "on_message : " + "個人チャンネルを作成します")
        # チャンネルを作成してwebhookのURLを取得する
        discord_webhook_url = await async_add_channel(line_data["line_user_id"])

        # webhookのURLを登録する
        requests.post("http://userconfig:5002/edit_config", json={"user_id": line_data["line_user_id"], "conf": {"discord_webhook_url": discord_webhook_url}})

# 評価ボタンを追加して送信する
async def async_eval(channel_id, content, user_data):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "async_eval : " + "評価ボタンを追加して送信します")
    channel = await client.fetch_channel(channel_id)  # チャンネルを取得
    view = ReactionButton(timeout=None, content=content, send_channel=send_channel, user_data=user_data)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "async_eval : " + f"{user_data['user_name']} さんが共有した投稿はどうですか？")
    await channel.send(f"{user_data['user_name']} さんが共有した投稿はどうですか？", view=view)

# チャンネルを作成する
async def async_add_channel(line_user_id):
    GUILD_ID = 1333468554582032527  # 使用しているサーバのID
    guild = client.get_guild(GUILD_ID)  # ギルド情報を取得する

    channel_name = requests.get("http://userconfig:5002/read_config", params={"user_id": line_user_id}).json()["discord_user_name"]

    # チャンネルが既に存在するか確認
    existing_channel = discord.utils.get(guild.text_channels, name=channel_name)

    # 既にチャンネルが存在しないなら作成する
    if not existing_channel:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "async_add_channel : " + "新しい個人用チャンネルを作成します")
        # 指定したカテゴリを探す
        category = discord.utils.get(guild.categories, name="個人")

        # 新しいチャンネルを作成
        channel = await guild.create_text_channel(channel_name, category=category)

        # 新しいwebhookを作成
        webhook = await channel.create_webhook(name=channel_name+"-webhook")

        # 新しいwebhookのurlを取得
        webhook_url = webhook.url
    
    # チャンネルにコンテンツURLを送信する
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "async_add_channel : " + f"{channel_name} さんの新しい個人用チャンネルを作成しました！")
    await channel.send(f"{channel_name} さんの新しい個人用チャンネルを作成しました！")

    # webhookのurlを返す
    return webhook_url

# チャンネルを作成してコンテンツを送信する
async def send_channel(content, channel_name, user_data):  # contributor: 投稿者の名前
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "send_channel : " + "新しい個人用チャンネルにコンテンツを送信します")
    GUILD_ID = os.getenv("GUILD_ID")  # 使用しているサーバのID
    guild = client.get_guild(GUILD_ID)  # ギルド情報を取得する

    # チャンネルが既に存在するか確認
    existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
    channel = await client.fetch_channel(existing_channel.id)  # チャンネルを取得

    # webhookのurlを取得
    webhook = await channel.create_webhook(name=channel_name+"-webhook")
    webhook_url = webhook.url

    # コンテントを作成する
    main_content = {
            "avatar_url": user_data["user_icon"],
            "username": user_data["user_name"],
            "content": content,
        }

    headers = {'Content-Type': 'application/json'}

    # おすすめの転送または直貼りにURLコンテンツを送信する
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "send_channel : " + "webhookに送信します", main_content)
    requests.post(webhook_url, json.dumps(main_content), headers=headers)

def run_flask():
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    client.run(token)  # Botを起動
