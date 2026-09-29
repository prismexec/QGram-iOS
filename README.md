# QGram (форк Telegram-iOS) — план сборки и фичи «чтение удалённых сообщений»

## 0. Реальность, которую нужно понимать заранее

- Это не «фотка» и не 5-минутная задача. Telegram-iOS — открытый проект на ~1M+ строк
  Swift/Objective-C/C++, собирается **Bazel + Xcode**, **только на macOS**.
  Источник: [github.com/TelegramMessenger/Telegram-iOS](https://github.com/TelegramMessenger/Telegram-iOS).
- GitHub Actions даёт `macos-14` runner — на нём можно собрать, но сборка занимает
  1.5–3 часа (первый прогон без кеша — дольше) и жрёт macOS-минуты по повышенному тарифу.
- Чтобы получить **установленный** IPA на реальный iPhone (не симулятор), нужен:
  - платный Apple Developer аккаунт (Team ID),
  - `api_id` / `api_hash` с [my.telegram.org/apps](https://my.telegram.org/apps),
  - сертификат подписи (.p12) и provisioning profile (.mobileprovision) — без них
    workflow соберёт **unsigned** артефакт, который на живом устройстве не запустится
    без sideload-инструмента (AltStore/Sideloadly) или jailbreak.
- По правилам самого Telegram (см. README апстрима): переименовывать форк — можно и нужно,
  **запрещено** только использовать имя «Telegram» как имя твоего приложения и их
  фирменный логотип (белый самолётик в синем круге). Это я учёл в скрипте ниже.

## 1. Что уже сделано в этом комплекте

| Файл | Назначение |
|---|---|
| [rebrand_to_qgram.py](rebrand_to_qgram.py) | Скрипт переименования Telegram → QGram в пользовательских строках (.strings, Info.plist), генерирует `qgram_configuration.json` |
| [.github/workflows/build-ipa.yml](.github/workflows/build-ipa.yml) | GitHub Actions workflow: клонирует репо, ставит нужный Xcode, гоняет Bazel-сборку, собирает IPA, кладёт артефакт |

## 2. Порядок действий (руками, один раз)

```bash
# 1. Клонируешь апстрим (НЕ форкаешь на GitHub заранее, чтобы не тащить чужую историю в приватный форк —
#    либо форкаешь через github.com/TelegramMessenger/Telegram-iOS -> Fork, дальше клонируешь свой форк)
git clone --recursive -j8 https://github.com/TelegramMessenger/Telegram-iOS.git QGram-iOS
cd QGram-iOS

# 2. Прогоняешь ребрендинг
python3 ../rebrand_to_qgram.py

# 3. Заполняешь build-system/qgram_configuration.json:
#    - api_id / api_hash с my.telegram.org/apps
#    - team_id из Keychain Access -> Certificates -> твой сертификат -> Organizational Unit

# 4. Заменяешь иконку приложения на свою (не самолётик Telegram) —
#    Telegram-iOS/Telegram/Telegram-iOS/Resources/AppIcons и Assets.xcassets/AppIcon*

# 5. Коммитишь и пушишь в свой репозиторий на GitHub
git remote set-url origin https://github.com/<твой-юзер>/QGram-iOS.git
git add -A && git commit -m "Rebrand to QGram"
git push -u origin main
```

## 3. Настройка секретов в GitHub (Settings → Secrets and variables → Actions)

Нужны для workflow `build-ipa.yml`:

| Secret | Значение |
|---|---|
| `TG_API_ID` | из my.telegram.org/apps |
| `TG_API_HASH` | из my.telegram.org/apps |
| `QGRAM_BUNDLE_ID` | например `org.qgram.app` |
| `APPLE_TEAM_ID` | из Apple Developer аккаунта |
| `IOS_CERT_P12_BASE64` | `base64 -i cert.p12 \| pbcopy` — сертификат подписи в base64 |
| `IOS_CERT_PASSWORD` | пароль от .p12 |
| `IOS_PROVISION_PROFILE_BASE64` | `base64 -i profile.mobileprovision \| pbcopy` |

Без последних трёх (`IOS_CERT_*`, `IOS_PROVISION_*`) собранный `.ipa` будет unsigned —
подойдёт только для дальнейшей ресайнинга локально (например через Sideloadly) или
для запуска на симуляторе.

## 4. Фича «чтение удалённых сообщений» (как в AyuGram)

### Как это работает у AyuGram и почему это возможно
Telegram-протокол **не хранит удалённые сообщения на сервере** после удаления —
клиент просто получает событие "удалить у себя эти message_id". AyuGram/Nekogram
и подобные форки перехватывают это событие **на уровне локального клиента**:
вместо того чтобы физически стирать сообщение из локальной базы, они:
1. Оставляют текст сообщения в локальном хранилище (Postbox/SQLite),
2. Помечают его флагом `isDeletedRemotely`,
3. В UI чата рисуют такое сообщение полупрозрачным / с бейджем «Удалено»,
   вместо того чтобы убрать его из ленты.

Это работает **только для сообщений, которые клиент уже успел получить и сохранить
локально до момента удаления** — то есть нельзя «прочитать» то, что удалили до того,
как твой QGram успел это скачать (это не бэкдор к серверу Telegram, это просто отказ
удалять локальную копию).

### Где это в реальном коде Telegram-iOS
В апстриме уже есть заготовка на уровне хранилища:
[`submodules/Postbox/Sources/DeletedMessagesView.swift`](https://github.com/TelegramMessenger/Telegram-iOS/blob/master/submodules/Postbox/Sources/DeletedMessagesView.swift) —
`MutableDeletedMessagesView` слушает операции `.Remove` по `peerId` и собирает список
`currentDeletedMessages: [MessageId]`, которые исчезли из индекса. Это ядро механизма
слежения за удалением — но сам **UI и логика "не стирать данные сообщения"** там не
реализованы (в апстриме Telegram эта view используется для внутренних целей, не для
показа удалённых юзеру).

### Что реально нужно доработать (план, не готовый код)

1. **Слой хранения (Postbox)**
   - Найти место, где `MessageHistoryTable` физически удаляет строку сообщения при
     обработке `updateDeleteMessages` / `.Remove` операции.
   - Вместо `DELETE` — делать `UPDATE`, помечая сообщение флагом (например, добавить
     bit в `MessageFlags` типа `.isRemotelyDeleted`), сохраняя текст/медиа.
   - Учитывать TTL/автоочистку базы, чтобы такие сообщения не удалялись при обычной
     чистке кэша.

2. **Слой UI (Telegram-iOS/Sources ChatController/ChatMessageItem)**
   - В `ChatHistoryEntry`/`ChatMessageItem` добавить рендер-вариант: полупрозрачный
     бабл, бейдж "Удалено" + иконка корзины (как в примере, который я тебе
     сгенерировал ранее).
   - Убедиться, что такие сообщения не попадают под обычную логику "message removed
     from view" в `ChatHistoryViewUpdate`.

3. **Синхронизация с сервером**
   - При обработке входящего `updates.deleteMessages` / `updateDeleteChannelMessages`
     не выполнять физическое удаление из Postbox, только выставлять флаг.
   - Опционально: добавить настройку в UI ("Показывать удалённые сообщения") —
     как это сделано в AyuGram — чтобы это было явным выбором пользователя, а не
     скрытым поведением.

4. **Юридический момент**
   - Это модифицирует протокол-совместимое поведение клиента, не взламывает сервер
     Telegram и не требует MTProto-патчей — юридически это ближе к тому, что уже
     легально делают AyuGram/Nekogram/Exteragram (они существуют открыто годами).
   - Но: раскрытие удалённых сообщений собеседника без его согласия — это уже вопрос
     этики использования, не мой запрет, а то, что тебе стоит иметь в виду при
     дистрибуции.

Я не пишу здесь готовый Swift-патч на тысячи строк "с нуля" — с реальным кодом Postbox
и ChatController придётся работать внутри Xcode с полным контекстом проекта (эти файлы
завязаны на десятки соседних типов). План выше — конкретная карта, где именно копать.

## 5. Итоговый чеклист

- [ ] Форкнуть/клонировать `TelegramMessenger/Telegram-iOS`
- [ ] Прогнать `rebrand_to_qgram.py`
- [ ] Заполнить `qgram_configuration.json` (api_id/api_hash/team_id)
- [ ] Заменить иконку и лого
- [ ] Реализовать флаг `isRemotelyDeleted` в Postbox + UI-рендер (см. раздел 4)
- [ ] Запушить в свой GitHub, добавить секреты
- [ ] Запустить `build-ipa.yml` вручную (Actions → Run workflow)
- [ ] Если нужен установленный IPA — добавить сертификат/профиль подписи в секреты
