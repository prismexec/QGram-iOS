#!/usr/bin/env python3
"""
QGram rebrand helper.

Запускать ИЗ КОРНЯ клона Telegram-iOS (после git clone --recursive):

    git clone --recursive -j8 https://github.com/TelegramMessenger/Telegram-iOS.git
    cd Telegram-iOS
    python3 /path/to/rebrand_to_qgram.py

Что делает:
  1. Массово заменяет строковые пользовательские упоминания "Telegram" -> "QGram"
     в .strings / Info.plist-подобных строках (НЕ трогает идентификаторы вроде
     "Telegram_xcodeproj", имена таргетов Bazel, пути submodules/Telegram*,
     импорты Swift-модулей — это всё сломает сборку).
  2. Заменяет отображаемое имя приложения (CFBundleDisplayName / CFBundleName)
     в найденных Info.plist-файлах.
  3. Формирует build-system/qgram_configuration.json из шаблона.
  4. НЕ трогает лицензии, авторские файлы, README апстрима.

Это НЕ переименовывает Swift target/module имена (Telegram, TelegramCore,
TelegramUI, Postbox и т.д.) — их трогать не нужно и не стоит: это внутренние
имена модулей Bazel/Xcode, они не видны пользователю и их переименование
потребует правки тысяч import-строк без функциональной пользы.

Пользователь увидит новое имя "QGram" только там, где строка реально идёт в UI:
localizable strings, launch screen, app icon name, bundle display name.
"""

import json
import os
import re
import sys

ROOT = os.getcwd()

# ВНИМАНИЕ: список ограничен пользовательскими текстовыми ресурсами.
# Если в репозитории появятся новые .lproj/Info.plist пути, добавь их сюда.
DISPLAY_NAME_KEYS = ["CFBundleDisplayName", "CFBundleName"]

OLD_BRAND = "Telegram"
NEW_BRAND = "QGram"

# Только эти паттерны считаются "пользовательским текстом", а не кодом/путём/модулем.
SAFE_TEXT_PATTERNS = [
    re.compile(r'"Telegram"'),           # ровно строковый литерал "Telegram"
    re.compile(r'>Telegram<'),           # XML-текст между тегами (plist strings)
]


def is_probably_code_or_path(line: str) -> bool:
    code_markers = ["import ", "BUILD", "bazel", ".bzl", "module.modulemap",
                     "submodules/Telegram", "TelegramCore", "TelegramUI",
                     "TelegramApi", "target_name", "//Telegram"]
    return any(m in line for m in code_markers)


def rebrand_strings_files():
    changed = []
    for dirpath, _, filenames in os.walk(ROOT):
        if "/.git" in dirpath or "\\.git" in dirpath:
            continue
        for fname in filenames:
            if not fname.endswith((".strings", ".stringsdict")):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                continue
            new_content = content
            for pat in SAFE_TEXT_PATTERNS:
                new_content = pat.sub(lambda m: m.group(0).replace(OLD_BRAND, NEW_BRAND), new_content)
            if new_content != content:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                changed.append(fpath)
    return changed


def rebrand_info_plists():
    changed = []
    for dirpath, _, filenames in os.walk(ROOT):
        if "/.git" in dirpath or "\\.git" in dirpath:
            continue
        for fname in filenames:
            if fname != "Info.plist":
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                continue
            new_content = content
            for key in DISPLAY_NAME_KEYS:
                # <key>CFBundleDisplayName</key>\n\t<string>Telegram</string>
                pattern = re.compile(
                    r'(<key>{}</key>\s*<string>)Telegram(</string>)'.format(re.escape(key))
                )
                new_content = pattern.sub(r'\1QGram\2', new_content)
            if new_content != content:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                changed.append(fpath)
    return changed


def write_qgram_configuration():
    template_path = os.path.join(ROOT, "build-system", "template_minimal_development_configuration.json")
    out_path = os.path.join(ROOT, "build-system", "qgram_configuration.json")
    if not os.path.exists(template_path):
        print("!! Не найден build-system/template_minimal_development_configuration.json — "
              "запусти скрипт из корня клона Telegram-iOS.")
        return None
    with open(template_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    cfg["bundle_id"] = "org.qgram.app"          # замени на свой уникальный bundle id
    cfg["app_specific_url_scheme"] = "qgram"    # tg:// -> qgram://
    cfg["api_id"] = "REPLACE_ME"                # получить на https://my.telegram.org/apps
    cfg["api_hash"] = "REPLACE_ME"
    cfg["team_id"] = "REPLACE_ME"               # Apple Developer Team ID

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return out_path


def main():
    if not os.path.exists(os.path.join(ROOT, "build-system")):
        print("Похоже, ты не в корне клона Telegram-iOS. Перейди в папку клона и запусти снова.")
        sys.exit(1)

    strings_changed = rebrand_strings_files()
    plist_changed = rebrand_info_plists()
    cfg_path = write_qgram_configuration()

    print("== Готово ==")
    print(f".strings/.stringsdict файлов изменено: {len(strings_changed)}")
    for p in strings_changed[:20]:
        print("  -", p)
    print(f"Info.plist файлов изменено: {len(plist_changed)}")
    for p in plist_changed[:20]:
        print("  -", p)
    if cfg_path:
        print(f"Создан конфиг: {cfg_path}")
        print("  -> ОБЯЗАТЕЛЬНО заполни api_id / api_hash / team_id перед сборкой.")
    print()
    print("Дальше руками:")
    print("  1. Замени иконку приложения (Info.plist -> AppIcon assets), т.к. лого Telegram "
          "использовать запрещено правилами апстрима.")
    print("  2. Проверь Launch Screen storyboard на текстовые упоминания бренда.")
    print("  3. Прогони: grep -r '\"Telegram\"' --include='*.strings' . (что осталось - реши руками)")


if __name__ == "__main__":
    main()
