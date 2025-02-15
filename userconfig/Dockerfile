# 基本イメージとしてPythonの公式イメージを使用
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /userconfig

# 必要なPythonライブラリをインストール
COPY requirements.txt /userconfig/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /userconfig/

CMD [ "python", "/userconfig/edit_config.py" ]

