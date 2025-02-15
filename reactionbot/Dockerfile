# 基本イメージとしてPythonの公式イメージを使用
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /reaction_bot

# 必要なPythonライブラリをインストール
COPY requirements.txt /reaction_bot/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /reaction_bot/

CMD [ "python", "manager_bot.py" ]
