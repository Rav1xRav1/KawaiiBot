#!/bin/bash

# デフォルトではバックグラウンドで実行
BACKGROUND=true

# 引数を解析
while getopts "f" opt; do
  case ${opt} in
    f )
      BACKGROUND=false
      ;;
    \? )
      echo "Usage: cmd [-f]"
      exit 1
      ;;
  esac
done

# コマンドの実行
if [ "$BACKGROUND" = true ]; then
  docker compose up -d --build --no-deps $(docker compose config --services | grep -v ngrok)
else
  docker compose up --build --no-deps $(docker compose config --services | grep -v ngrok)
fi
