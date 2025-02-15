docker compose down $(docker compose config --services | grep -v ngrok)
