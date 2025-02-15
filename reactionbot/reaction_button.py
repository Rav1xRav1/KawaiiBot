import discord
import requests

from datetime import datetime


# Discordのボタンを操作するクラス
class ReactionButton(discord.ui.View):
    def __init__(self, timeout=180, content="", send_channel=None, user_data={}):
        super().__init__(timeout=timeout)
        self.content = content
        self.send_channel = send_channel
        self.user_data = user_data
    
    # メッセージとしてYESボタンを送信する
    @discord.ui.button(label="YES", style=discord.ButtonStyle.success)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "yes : " + f"{interaction.user.name} さんがYESボタンを押しました")
        await interaction.response.send_message(f"{interaction.user.mention} さん興味あり！")
        # ユーザ名のチャンネルを作成し、コンテンツを送信する ※既にチャンネルがあるときは送信だけ行われる
        await self.send_channel(self.content, interaction.user.name, self.user_data)

    # メッセージとしてNOボタンを送信する
    @discord.ui.button(label="NO", style=discord.ButtonStyle.gray)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "no : " + f"{interaction.user.name} さんがNOボタンを押しました")
        await interaction.response.send_message(f"{interaction.user.mention} さん興味なし！ (<{self.content}>)")

"""
これより下は使用していない
"""

# DropDownの確定を操作するクラス
class DropDownEnterButton(discord.ui.View):
    def __init__(self, timeout=180, user_id="", user_name="", add_channel=None):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.user_name = user_name
        self.add_channel = add_channel
    
    # メッセージとしてOKボタンを送信する
    @discord.ui.button(label="OK", style=discord.ButtonStyle.success)
    async def ok(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "ok : " + f"{interaction.user.name} さんがOKボタンを押しました")
        await interaction.response.send_message(
            f"{interaction.user.mention} さんが `{self.user_name}` を選択しました\n新しいチャンネルが作成されます。チャンネル名 : {interaction.user.name}"
            )

        # チャンネルを追加して返り値としてwebhookのURLを取得する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "ok : " + f"{interaction.user.name} さんのチャンネルを追加します")
        webhook_url = await self.add_channel(interaction.user.name)
        
        # channel_id = interaction.channel.id
        # ボタンを押したユーザIDを取得する
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "ok : " + f"{interaction.user.name} さんのユーザ情報登録リクエストをします")
        user_id = interaction.user.id
        requests.post(
            "http://userconfig:5002/edit_config",
            json={
                "user_id": self.user_id,
                "conf": {
                    "discord_user_id": user_id,
                    "discord_user_name": interaction.user.name,
                    "discord_webhook_url": webhook_url
                }
            }
        )

    # メッセージとしてCANCELボタンを送信する
    @discord.ui.button(label="CANCEL", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "cancel : " + f"{interaction.user.name} さんがCANCELボタンを押しました")
        await interaction.response.send_message(f"キャンセルしました\n登録しなおすには再度 `/register` を実行してください")

# ドロップダウンメニューの挙動を定義するクラス
class Dropdown(discord.ui.Select):
    def __init__(self, options, add_channel):
        super().__init__(placeholder="連携するLINEアカウントを選択してください", min_values=1, max_values=1, options=options)
        self.add_channel = add_channel  # チャンネルを追加するメソッド

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        selected_option = next(option for option in self.options if option.value == selected_value)
        selected_description = selected_option.description 

        # edit_messageを使って表示をButtonViewへ変更する。
        await interaction.response.edit_message(
            content=f"`{selected_description}` が選択されました。よろしいですか？",
            view=DropDownEnterButton(user_id=selected_value,
                                     user_name=selected_description,
                                     add_channel=self.add_channel)
        )

# ドロップダウンメニューのビューを定義するクラス
# 現在使用していない
class DropdownView(discord.ui.View):
    def __init__(self, content=None, add_channel=None):
        super().__init__()
        # ドロップダウンメニューのリスト
        options = []
        for user_id, user_name in content.items():
            options.append(discord.SelectOption(label=user_id, description=user_name, value=user_id))
        # viewにセレクトを追加
        self.add_item(Dropdown(options=options, add_channel=add_channel))

