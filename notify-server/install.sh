#!/usr/bin/env bash
# PrismGram Notify installer. Run on your VPS:
#   bash <(curl -fsSL https://raw.githubusercontent.com/prismexec/QGram-iOS/claude/great-mayer-19dpjy/notify-server/install.sh)
set -euo pipefail
BASE="https://raw.githubusercontent.com/prismexec/QGram-iOS/claude/great-mayer-19dpjy/notify-server"
DIR="$HOME/prismgram-notify"

if ! command -v docker >/dev/null 2>&1; then
  echo "Устанавливаю Docker..."
  curl -fsSL https://get.docker.com | sh
fi

mkdir -p "$DIR/data" && cd "$DIR"
for f in prismgram_notify.py Dockerfile docker-compose.yml; do
  curl -fsSL "$BASE/$f" -o "$f"
done

if [ ! -f .env ]; then
  echo
  echo "Нужны api_id и api_hash с https://my.telegram.org/apps (те же, что для PrismGram)."
  read -rp "api_id: " API_ID
  read -rp "api_hash: " API_HASH
  TOPIC="prismgram-$(head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n')"
  cat > .env <<ENV
API_ID=$API_ID
API_HASH=$API_HASH
NTFY_TOPIC=$TOPIC
NTFY_SERVER=https://ntfy.sh
SHOW_TEXT=1
ENV
fi
TOPIC=$(grep '^NTFY_TOPIC=' .env | cut -d= -f2)

docker compose build
echo
echo "Сейчас войдите в Telegram: номер телефона, код из Telegram и пароль (если есть)."
docker compose run --rm notify python3 -u /app/prismgram_notify.py login
docker compose up -d

echo
echo "Готово! Теперь на iPhone:"
echo "  1. Установите приложение ntfy из App Store."
echo "  2. Нажмите + и подпишитесь на тему:  $TOPIC"
echo "     (сервер оставьте ntfy.sh)."
echo "Тестовое уведомление уже отправлено. Логи: cd $DIR && docker compose logs -f"
