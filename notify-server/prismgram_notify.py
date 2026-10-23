#!/usr/bin/env python3
"""
PrismGram Notify: push notifications for PrismGram through the ntfy app.

A second session of your Telegram account listens for new messages and sends a
notification to your ntfy topic. It never marks messages as read and never sets
"online", so PrismGram's ghost mode keeps working.

    python3 prismgram_notify.py login   # first time: phone number + code
    python3 prismgram_notify.py         # run
Settings come from environment variables (see .env.example).
"""

import asyncio
import datetime
import json
import os
import sys
import time
import urllib.request

from telethon import TelegramClient, events, functions, types, utils

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
NTFY_TOPIC = os.environ["NTFY_TOPIC"]
SHOW_TEXT = os.environ.get("SHOW_TEXT", "1") == "1"
SESSION = os.environ.get("SESSION_PATH", "/data/prismgram")

client = TelegramClient(SESSION, API_ID, API_HASH, device_model="PrismGram Notify", system_version="Linux", app_version="1.0")

_mute_cache = {}  # peer id -> (checked_at, muted)


async def is_muted(event):
    key = event.chat_id
    cached = _mute_cache.get(key)
    if cached and time.time() - cached[0] < 300:
        return cached[1]
    muted = False
    try:
        peer = await event.get_input_chat()
        settings = await client(functions.account.GetNotifySettingsRequest(peer=types.InputNotifyPeer(peer)))
        until = settings.mute_until
        if until is not None:
            if isinstance(until, datetime.datetime):
                muted = until > datetime.datetime.now(datetime.timezone.utc)
            else:
                muted = int(until) > time.time()
    except Exception as error:  # keep notifying if the check fails
        print("notify settings check failed:", error, flush=True)
    _mute_cache[key] = (time.time(), muted)
    return muted


def describe(message):
    if message.voice:
        return "🎤 Голосовое сообщение"
    if message.video_note:
        return "⏺ Видеосообщение"
    if message.sticker:
        return "Стикер"
    if message.gif:
        return "GIF"
    if message.photo:
        return "📷 Фото" + (": " + message.message if message.message else "")
    if message.video:
        return "🎬 Видео" + (": " + message.message if message.message else "")
    if message.poll:
        return "📊 Опрос"
    if message.geo:
        return "📍 Геопозиция"
    if message.contact:
        return "👤 Контакт"
    if message.document:
        return "📎 Файл" + (": " + message.message if message.message else "")
    return message.message or "Сообщение"


def open_link(event, chat):
    username = getattr(chat, "username", None)
    if username:
        return "tg://resolve?domain=" + username
    if event.is_private:
        return "tg://openmessage?user_id={}".format(event.sender_id)
    if isinstance(chat, types.Channel):
        return "tg://privatepost?channel={}&post={}".format(chat.id, event.id)
    return None


def send(title, body, click):
    payload = {"topic": NTFY_TOPIC, "title": title[:120], "message": body[:500], "tags": ["speech_balloon"]}
    if click:
        payload["click"] = click
    request = urllib.request.Request(NTFY_SERVER, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=15) as response:
        response.read()


@client.on(events.NewMessage(incoming=True))
async def on_message(event):
    try:
        if event.is_channel and not event.is_group:
            return  # broadcast channels
        if await is_muted(event) and not event.mentioned:
            return
        sender = await event.get_sender()
        chat = await event.get_chat()
        name = utils.get_display_name(sender) if sender else "Telegram"
        if event.is_private:
            title = name
        else:
            title = "{} · {}".format(name, utils.get_display_name(chat))
        body = describe(event.message) if SHOW_TEXT else "Новое сообщение"
        await asyncio.to_thread(send, title, body, open_link(event, chat))
    except Exception as error:
        print("failed to send a notification:", error, flush=True)


async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        await client.start()
        me = await client.get_me()
        print("Logged in as", utils.get_display_name(me))
        await asyncio.to_thread(send, "PrismGram Notify", "Уведомления подключены ✅", None)
        print("A test notification was sent to ntfy topic", NTFY_TOPIC)
        return
    await client.connect()
    if not await client.is_user_authorized():
        print("Not logged in. Run the login step first.", flush=True)
        sys.exit(1)
    print("PrismGram Notify is running, topic:", NTFY_TOPIC, flush=True)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
