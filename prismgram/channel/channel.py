#!/usr/bin/env python3
"""
Posts to the @prismgram_ios channel through a Telegram bot (BOT_TOKEN env).

    channel.py setup [all|profile|posts]
        Sets the avatar and description, then posts "How to install", "FAQ"
        and the pinned welcome post. Prints the new message ids.
    channel.py release BUILD IPA_PATH
        Posts the update card with the changelog from prismgram/app.json, then the IPA.

BOT_API (env) is the Bot API base URL, https://api.telegram.org by default.
A local Bot API server is needed for files over 50 MB (the IPA).
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import posts  # noqa: E402

KIT = os.path.dirname(HERE)
STATE_PATH = os.path.join(HERE, "state.json")
OUT = os.environ.get("CHANNEL_OUT", "out/channel")


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


APP = load_json(os.path.join(KIT, "app.json"), {})
CHANNEL = APP.get("channel", "@prismgram_ios")
CHANNEL_LINK = "https://t.me/" + CHANNEL.lstrip("@")


class TelegramError(Exception):
    pass


def call(method, fields=None, files=None, timeout=900):
    """Calls a Bot API method with curl (multipart, so text is never read as a file name)."""
    base = os.environ.get("BOT_API", "https://api.telegram.org").rstrip("/")
    url = "{}/bot{}/{}".format(base, os.environ["BOT_TOKEN"], method)
    command = ["curl", "-sS", "--max-time", str(timeout), url]
    for key, value in (fields or {}).items():
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)
        command += ["--form-string", "{}={}".format(key, value)]
    for key, path in (files or {}).items():
        command += ["-F", "{}=@{}".format(key, path)]
    result = subprocess.run(command, capture_output=True, text=True)
    try:
        answer = json.loads(result.stdout or "{}")
    except ValueError:
        answer = {}
    if not answer.get("ok"):
        raise TelegramError("{} failed: curl exit {}, {} {}".format(
            method, result.returncode, result.stdout[:1000], result.stderr[:500]))
    return answer["result"]


def buttons(*rows):
    return {"inline_keyboard": [[{"text": text, "url": url} for text, url in row] for row in rows]}


def post_link(message_id):
    return "{}/{}".format(CHANNEL_LINK, message_id) if message_id else CHANNEL_LINK


def render(kind, path, *args):
    subprocess.run([sys.executable, os.path.join(HERE, "render.py"), kind, path] + list(args), check=True)
    return path


def setup_profile():
    os.makedirs(OUT, exist_ok=True)
    call("setChatPhoto", {"chat_id": CHANNEL}, {"photo": render("avatar", os.path.join(OUT, "avatar.png"))})
    print("avatar set")
    try:
        call("setChatDescription", {"chat_id": CHANNEL, "description": posts.DESCRIPTION})
        print("description set")
    except TelegramError as error:
        if "not modified" not in str(error):
            raise
        print("description already up to date")


def setup_posts():
    os.makedirs(OUT, exist_ok=True)
    state = load_json(STATE_PATH, {})
    common = {"chat_id": CHANNEL, "parse_mode": "HTML", "disable_notification": "true"}

    install = call("sendMessage", dict(common, text=posts.INSTALL,
                                       link_preview_options={"is_disabled": True},
                                       reply_markup=buttons([("📥 Скачать IPA", posts.LATEST_IPA_URL)])))
    state["install_post"] = install["message_id"]
    print("install post:", post_link(state["install_post"]))

    faq = call("sendMessage", dict(common, text=posts.FAQ,
                                   link_preview_options={"is_disabled": True},
                                   reply_markup=buttons([("💬 Написать разработчику", "https://t.me/" + posts.DEVELOPER.lstrip("@"))])))
    state["faq_post"] = faq["message_id"]
    print("faq post:", post_link(state["faq_post"]))

    welcome = call("sendPhoto", dict(common, caption=posts.WELCOME, reply_markup=buttons(
        [("📥 Скачать IPA", posts.LATEST_IPA_URL), ("📲 Как установить", post_link(state["install_post"]))],
        [("❓ Вопросы", post_link(state["faq_post"])), ("🌐 prismexec.tech", posts.SITE_URL)],
    )), {"photo": render("hero", os.path.join(OUT, "hero.png"))})
    state["welcome_post"] = welcome["message_id"]
    print("welcome post:", post_link(state["welcome_post"]))

    call("unpinAllChatMessages", {"chat_id": CHANNEL})
    call("pinChatMessage", {"chat_id": CHANNEL, "message_id": str(state["welcome_post"]), "disable_notification": "true"})
    print("welcome post pinned")

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("Channel message ids:\n\n```json\n{}\n```\n".format(json.dumps(state, indent=2)))
    print("STATE " + json.dumps(state))


def release(build, ipa_path):
    os.makedirs(OUT, exist_ok=True)
    state = load_json(STATE_PATH, {})
    version = APP["version"]
    ipa_url = "https://github.com/prismexec/QGram-iOS/releases/download/build-{}/PrismGram.ipa".format(build)
    caption = posts.release_caption(version, build, APP.get("changelog") or [])
    visible = len(re.sub(r"<[^>]+>", "", caption).encode("utf-16-le")) // 2
    if visible > 1024:
        fail("the changelog is too long for a photo caption ({} of 1024 characters)".format(visible))
    card = call("sendPhoto", {
        "chat_id": CHANNEL,
        "parse_mode": "HTML",
        "caption": caption,
        "reply_markup": buttons([("📥 Скачать IPA", ipa_url), ("📲 Как установить", post_link(state.get("install_post")))]),
    }, {"photo": render("release", os.path.join(OUT, "release.png"), version, str(build))})
    print("update card:", post_link(card["message_id"]))
    document = call("sendDocument", {
        "chat_id": CHANNEL,
        "caption": "PrismGram {} ({})".format(version, build),
        "disable_notification": "true",
    }, {"document": ipa_path})
    print("IPA:", post_link(document["message_id"]))


def fail(message):
    print("channel: ERROR: " + message)
    sys.exit(1)


def main():
    if "BOT_TOKEN" not in os.environ:
        fail("BOT_TOKEN is not set")
    args = sys.argv[1:]
    try:
        if args[:1] == ["setup"]:
            what = args[1] if len(args) > 1 else "all"
            if what in ("all", "profile"):
                setup_profile()
            if what in ("all", "posts"):
                setup_posts()
        elif args[:1] == ["release"] and len(args) == 3:
            release(args[1], args[2])
        else:
            print(__doc__)
            sys.exit(2)
    except TelegramError as error:
        fail(str(error))


if __name__ == "__main__":
    main()
