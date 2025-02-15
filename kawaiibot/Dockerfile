# 基本イメージとしてPythonの公式イメージを使用
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /app

# 必要なPythonライブラリをインストール
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

CMD [ "python", "/app/sns_data_converter.py" ]
