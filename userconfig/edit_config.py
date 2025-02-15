import json
from flask import Flask, request, jsonify
from datetime import datetime


app = Flask(__name__)

class EditConfig:
    # configファイルを編集するメソッド
    @classmethod
    def edit_user_config(cls, user_id, **conf):
        try:  # ファイルを読み込む
            with open("./data/Userconfig.json", "r") as f:
                file = json.load(f)
        except FileNotFoundError as e:  # ファイルがなければ新しく作る
            file = {}
        
        # 一層目のuseridが無ければ追加する
        if not user_id in file.keys():
            file[user_id] = {}

        # 該当する項目を追加する
        for k, v in zip(conf.keys(), conf.values()):
            file[user_id][k] = v

        # 書き込む
        with open("./data/Userconfig.json", "w") as f:
            json.dump(file, f, indent=4)
    
    # configファイルを読み込むメソッド
    @classmethod
    def read_user_config(cls, line_user_id):
        try:  # ファイルを読み込む
            with open("./data/Userconfig.json", "r") as f:
                return json.load(f)[line_user_id]
        except FileNotFoundError as e:  # 無ければ空の辞書を返す
            return {}
        except json.decoder.JSONDecodeError as e:
            return {}
    
    # 引数を受け取らず{user_id: user_name}の形式で返すメソッド
    @classmethod
    def get_user_id_username(cls):
        try:  # ファイルを読み込む
            with open("./data/Userconfig.json", "r") as f:
                file = json.load(f)
            return {user_id: data.get("user_name") for user_id, data in file.items()}
        except FileNotFoundError as e:  # 無ければ空の辞書を返す
            return {}
    
    # discord IDからLINE IDを取得して値を返すメソッド
    @classmethod
    def get_line_id(cls, discord_user_id):
        try:  # ファイルを読み込む
            with open("./data/Userconfig.json", "r") as f:
                file = json.load(f)
        except FileNotFoundError as e:  # 無ければ空の辞書を返す
            return {}
        
        # discord_user_idが一致するものを探す
        for key, value in file.items():
            if value.get('discord_user_id') == int(discord_user_id):
                return key
        
        return None  # 一致するものがなければNoneを返す
    
    # アカウント連携のためのランダムな文字列をLINEのユーザ情報を保存するためのメソッド
    @classmethod
    def register(cls, random_code, line_user_id, line_user_name, line_picture_url):
        try:  # ファイルを読み込む
            with open("./data/RegisterCode.json", "r") as f:
                file = json.load(f)
        except FileNotFoundError as e:  # 無ければ空の辞書を返す
            file = {}
        
        file[random_code] = {
            "line_user_id": line_user_id,
            "line_user_name": line_user_name,
            "line_picture_url": line_picture_url,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 書き込む
        with open("./data/RegisterCode.json", "w") as f:
            json.dump(file, f, indent=4)
    
    # ランダムな文字列から保存したラインの情報を取得するメソッド
    @classmethod
    def get_line_data(cls, random_code):
        try:  # ファイルを読み込む
            with open("./data/RegisterCode.json", "r") as f:
                file = json.load(f)
                return file[random_code]
        except FileNotFoundError as e:  # 無ければ空の辞書を返す
            return None
        except KeyError as e:  # ランダムな文字列が存在しない場合
            return None

# configファイルを編集するエンドポイント
@app.route('/edit_config', methods=['POST'])
def edit_config():
    data = request.json
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "edit_config : " + "リクエストを受信しました :", data)
    user_id = data.get('user_id')
    conf = data.get('conf')
    if user_id and conf:
        EditConfig.edit_user_config(user_id, **conf)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "edit_config : " + "configファイルを編集しました")
        return jsonify({"status": "success"}), 200
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "edit_config : " + "リクエストが不正です")
    return jsonify({"status": "error", "message": "Invalid input"}), 400

# configファイルを読み込むエンドポイント
@app.route('/read_config', methods=['GET'])
def read_config():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "read_config : " + "リクエストを受信しました")
    user_id = request.args.get('user_id')
    if user_id:
        config = EditConfig.read_user_config(user_id)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "read_config : " + "configファイルを読み込みました")
        return jsonify(config), 200
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "read_config : " + "リクエストが不正です")
    return jsonify({"status": "error", "message": "Invalid input"}), 400

# Discord IDからLINE IDを取得して値を返すエンドポイント
# Discord直貼り
@app.route('/get_line_id', methods=['GET'])
def get_line_id():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_line_id : " + "リクエストを受信しました")
    result = EditConfig.get_line_id(request.args.get('discord_user_id'))
    if result:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_line_id : " + "LINE IDを取得しました")
        return jsonify(result), 200
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_line_id : " + "データが見つかりませんでした")
    return jsonify({"status": "error", "message": "No data found"}), 400

# アカウント連携のためのランダムな文字列をLINEのユーザ情報を保存するためのエンドポイント
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "register : " + "リクエストを受信しました :", data)
    random_code = data.get('random_code')
    line_user_id = data.get('line_user_id')
    line_user_name = data.get('line_user_name')
    line_picture_url = data.get('line_picture_url')
    if random_code and line_user_id and line_user_name and line_picture_url:
        EditConfig.register(random_code, line_user_id, line_user_name, line_picture_url)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "register : " + "LINEのユーザ情報を保存しました")
        return jsonify({"status": "success"}), 200
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "register : " + "リクエストが不正です")
    return jsonify({"status": "error", "message": "Invalid input"}), 400

# ランダムな文字列から保存したラインの情報を取得するエンドポイント
@app.route('/get_line_data', methods=['GET'])
def get_line_data():
    random_code = request.args.get('random_code')
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_line_data : " + "リクエストを受信しました :", random_code)
    if random_code:
        result = EditConfig.get_line_data(random_code)
        if result:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_line_data : " + "LINEのユーザ情報を取得しました")
            return jsonify(result), 200
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "get_line_data : " + "データが見つかりませんでした")
        return jsonify({"status": "error", "message": "No data found"}), 400

# Flaskアプリケーションを実行する
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002)
