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

INSTALL_TEMPLATE = """<b>📲 Как установить PrismGram</b>

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
Ставьте новую версию поверх старой: переписки и вход сохранятся.{sidestore}"""


def install_text(sidestore_link=None):
    extra = ""
    if sidestore_link:
        extra = ('\n\n<b>Без компьютера каждые 7 дней</b>\n'
                 'SideStore переподписывает приложение прямо на телефоне. '
                 '<a href="{}">Подробная инструкция по SideStore</a>'.format(sidestore_link))
    return INSTALL_TEMPLATE.format(source=SOURCE_URL, sidestore=extra)

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


SIDESTORE_SITE = "https://sidestore.io"
SIDESTORE_DOCS = "https://docs.sidestore.io"

SIDESTORE_1 = """<b>🧩 SideStore: установка (часть 1 из 2)</b>

SideStore — магазин приложений, который сам переподписывает PrismGram прямо на iPhone. Компьютер нужен один раз, а не каждые 7 дней. Это бесплатно: хватит обычного Apple ID.

<b>Что понадобится</b>
• iPhone с iOS 14 или новее, на iPhone должен стоять код-пароль
• компьютер с Windows, macOS или Linux и кабель для iPhone
• Apple ID. Лучше завести отдельный, не основной: его пароль вводится в SideStore

<b>Шаг 1. Подготовьте компьютер</b>
• Windows: установите iTunes с сайта Apple (не из Microsoft Store)
• macOS: ничего ставить не нужно
• Linux: установите usbmuxd
Затем скачайте программу <b>iloader</b>: ссылка есть на сайте SideStore (кнопка под постом).

<b>Шаг 2. Установите SideStore</b>
1. Подключите iPhone кабелем, разблокируйте его и нажмите «Доверять этому компьютеру».
2. Откройте iloader и войдите в Apple ID.
3. Выберите свой iPhone и нажмите <b>Install SideStore</b>. iloader установит SideStore и сразу добавит в него файл сопряжения (pairing file). Без этого файла SideStore работать не будет.

<b>Шаг 3. Разрешите SideStore на iPhone</b>
1. Настройки → Основные → VPN и управление устройством → ваш Apple ID → <b>Доверять</b>.
2. Настройки → Конфиденциальность и безопасность → <b>Режим разработчика</b> → включить. iPhone перезагрузится, после этого подтвердите «Включить».

<b>Шаг 4. Поставьте VPN для SideStore</b>
Установите из App Store <b>LocalDevVPN</b> и включите в нём VPN. Это не настоящий VPN: трафик никуда не уходит. Он нужен, чтобы SideStore мог подписывать приложения прямо на телефоне. Включайте его перед каждой установкой и обновлением.

<b>Шаг 5.</b> Откройте SideStore и войдите в тот же Apple ID.

Как поставить PrismGram — в следующем посте 👇"""

SIDESTORE_2 = """<b>🧩 SideStore: установка PrismGram (часть 2 из 2)</b>

Перед установкой включите <b>LocalDevVPN</b>.

<b>Способ 1. Через источник — обновления появятся сами</b>
1. SideStore → вкладка <b>Sources</b> → <b>+</b>.
2. Вставьте ссылку (нажмите на неё, чтобы скопировать):
<code>{source}</code>
3. Откройте источник PrismGram и нажмите кнопку установки.

<b>Способ 2. Через файл</b>
1. Скачайте IPA из закреплённого сообщения в канале (или кнопкой под постом) и сохраните в «Файлы».
2. SideStore → <b>My Apps</b> → <b>+</b> вверху → выберите PrismGram.ipa.

<b>Если SideStore спросит про расширения</b>
Выберите <b>Remove App Extensions</b> (удалить расширения). С бесплатным Apple ID можно держать не больше 3 приложений, и расширения тоже считаются. На чаты это не влияет: виджеты и «Поделиться» при переподписи всё равно не работают.

<b>Каждые 7 дней</b>
Подпись бесплатного Apple ID действует 7 дней. Включите LocalDevVPN → SideStore → <b>My Apps</b> → <b>Refresh All</b>. Компьютер не нужен. Удобнее обновлять заранее, раз в 3–4 дня.

<b>Если что-то не работает</b>
• Ошибка подключения: не включён LocalDevVPN.
• Ошибка pairing file: подключите iPhone к компьютеру и в iloader заново установите файл сопряжения.
• «Maximum number of apps»: занято 3 приложения. Удалите лишнее, подписанное этим Apple ID.
• «Maximum App IDs»: можно не больше 10 новых App ID за 7 дней. Подождите или используйте другой Apple ID.
• PrismGram не открывается: прошли 7 дней. Сделайте Refresh All.

Переписки и вход при обновлении и переподписи сохраняются.
Вопросы: {dev}""".format(source=SOURCE_URL, dev=DEVELOPER)
