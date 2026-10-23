# Texts for the @prismgram_ios channel (Telegram HTML).
# Captions under a photo are limited to 1024 characters, other posts to 4096.

SOURCE_URL = "https://github.com/prismexec/QGram-iOS/releases/latest/download/source.json"
LATEST_IPA_URL = "https://github.com/prismexec/QGram-iOS/releases/latest/download/PrismGram.ipa"
SITE_URL = "https://prismexec.tech"
DEVELOPER = "@prismexec"

# Shown on the channel's profile page (255 characters max).
DESCRIPTION = (
    "PrismGram — Telegram для iPhone в духе AyuGram: "
    "👻 режим призрака, 🗑 удалённые сообщения, ✏️ история правок, без рекламы.\n"
    "Разработчик: @prismexec · prismexec.tech"
)

INSTALL = """<b>📲 Как установить PrismGram</b>

PrismGram — это IPA-файл. Перед установкой его нужно подписать: это делают Feather, ESign, Sideloadly или AltStore.

<b>Через Feather — проще всего</b>
1. Откройте <b>Sources → +</b> и вставьте ссылку (нажмите на неё, чтобы скопировать):
<code>{source}</code>
2. Найдите PrismGram в источнике и нажмите <b>Get</b>.
3. Подпишите своим сертификатом и установите.
Новые версии будут появляться в Feather сами.

<b>Через компьютер</b>
Скачайте IPA (кнопка под постом) и установите через Sideloadly или AltStore с обычным Apple ID. С бесплатным Apple ID приложение работает 7 дней, потом его нужно переподписать.

<b>Обновление</b>
Ставьте новую версию поверх старой: переписки и вход сохранятся.""".format(source=SOURCE_URL)

FAQ = """<b>❓ Частые вопросы</b>

<b>Это безопасно?</b>
<blockquote expandable>PrismGram собран из открытого кода официального Telegram для iOS. Переписки и вход хранятся только на вашем телефоне и идут напрямую на серверы Telegram, без посредников.</blockquote>
<b>Telegram за это не банит?</b>
<blockquote expandable>Сторонние клиенты Telegram официально разрешены: у него открытый API. Все функции PrismGram работают на вашем телефоне. Банят за спам и нарушения правил, а не за клиент.</blockquote>
<b>Почему не приходят уведомления?</b>
<blockquote expandable>Apple доставляет push-уведомления Telegram только в приложение, подписанное ключами Telegram. Переподписанный клиент их получить не может. Совет: оставьте официальный Telegram для уведомлений, а читайте в PrismGram.</blockquote>
<b>Как работает режим призрака?</b>
<blockquote expandable>Вы читаете сообщения, а у собеседника они остаются непрочитанными. «В сети» и «печатает» не отправляются, истории смотрятся без отметки. Включить: Настройки → PrismGram или удерживайте вкладку «Чаты». Когда вы отправляете сообщение, Telegram на миг показывает вас «в сети», и PrismGram сразу возвращает «не в сети».</blockquote>
<b>Почему видны не все удалённые сообщения?</b>
<blockquote expandable>Сохраняются только сообщения, которые приложение успело загрузить до удаления. Сервер Telegram удалённое не хранит.</blockquote>
<b>Приложение перестало открываться</b>
<blockquote expandable>Закончился срок подписи (с бесплатным Apple ID это 7 дней). Переподпишите IPA и установите поверх: данные сохранятся.</blockquote>
<b>Как обновиться?</b>
<blockquote expandable>PrismGram сам сообщает о новой версии. Проверить вручную: Настройки → PrismGram → «Проверить обновления». Если источник добавлен в Feather, обновление уже там.</blockquote>
Остались вопросы? Пишите {dev}""".format(dev=DEVELOPER)

WELCOME = """<b>PrismGram — Telegram для iPhone с функциями AyuGram</b>

👻 <b>Режим призрака</b>: без «прочитано», «в сети» и «печатает», истории смотрятся незаметно
🗑 <b>Удалённые сообщения</b> остаются в чате
✏️ <b>История правок</b>: видно, что было до изменения
🚫 <b>Без рекламы</b> в каналах
🔄 <b>Обновления</b> прямо в приложении

Разработчик: {dev} · <a href="{site}">prismexec.tech</a>""".format(dev=DEVELOPER, site=SITE_URL)


def release_caption(version, build, changelog):
    lines = ["<b>🚀 PrismGram {}</b> · сборка {}".format(version, build)]
    if changelog:
        lines += ["", "<b>Что нового</b>"]
        lines += ["• " + item for item in changelog]
    lines += ["", "IPA — в следующем сообщении."]
    return "\n".join(lines)
