# PrismGram Notify

Уведомления для PrismGram через бесплатное приложение **ntfy** — без аккаунта Apple Developer.

На вашем VPS работает отдельная сессия Telegram. Когда вам пишут, она присылает уведомление
в ntfy («Аня: привет»); нажатие открывает чат в PrismGram. Сообщения не отмечаются прочитанными
и статус «в сети» не ставится — режим призрака не ломается. Каналы и чаты без звука не уведомляют
(кроме упоминаний).

## Установка (на VPS)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/prismexec/QGram-iOS/claude/great-mayer-19dpjy/notify-server/install.sh)
```

Скрипт поставит Docker (если его нет), спросит `api_id` и `api_hash` с my.telegram.org,
попросит войти в Telegram (номер, код, пароль) и запустит сервер. В конце покажет название темы.

На iPhone: App Store → **ntfy** → «+» → вставьте тему → подписаться.

## Важно

- Сессия хранится только на вашем VPS (`~/prismgram-notify/data`). Не отдавайте этот файл никому.
- Тема ntfy — как пароль: кто её знает, видит ваши уведомления. Тексты проходят через сервер ntfy.sh.
  Чтобы не показывать текст, поставьте `SHOW_TEXT=0` в `~/prismgram-notify/.env` и выполните
  `docker compose up -d` в этой папке.
- Логи: `cd ~/prismgram-notify && docker compose logs -f`. Остановить: `docker compose down`.
