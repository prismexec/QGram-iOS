#!/usr/bin/env python3
"""
Turns a Swiftgram (Telegram-iOS fork) checkout into PrismGram.

Usage (from anywhere):
    python3 prismgram/apply_prismgram.py /path/to/swiftgram-checkout

Steps:
  1. Applies every patch in prismgram/patches (AyuGram-style features).
  2. Replaces the app icon glyph and colors.
  3. Renames the user-visible app name "Swiftgram" -> "PrismGram"
     (Info.plist strings, permission texts, settings titles).
     Module / target names stay untouched so the Bazel build keeps working.

The script stops with an error if anything it expects is missing, so a broken
upstream update shows up immediately instead of producing a half-patched app.
"""

import glob
import json
import os
import re
import subprocess
import sys

KIT_DIR = os.path.dirname(os.path.abspath(__file__))
NEW_NAME = "PrismGram"
OLD_NAME = "Swiftgram"

# Gradient behind the icon glyph: violet -> cyan.
ICON_GRADIENT = [
    "srgb:0.48235,0.18431,0.96863,1.00000",
    "srgb:0.00000,0.76078,1.00000,1.00000",
]


def fail(message):
    print("apply_prismgram: ERROR: " + message)
    sys.exit(1)


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def apply_patches(root):
    patches = sorted(glob.glob(os.path.join(KIT_DIR, "patches", "*.patch")))
    if not patches:
        fail("no patches found")
    for patch in patches:
        name = os.path.basename(patch)
        check = subprocess.run(["git", "apply", "--check", patch], cwd=root)
        if check.returncode != 0:
            fail("patch {} does not apply to this checkout".format(name))
        subprocess.run(["git", "apply", "--whitespace=nowarn", patch], cwd=root, check=True)
        print("applied " + name)


def apply_icon(root):
    icon_dir = os.path.join(root, "Telegram", "Telegram-iOS", "Swiftgram.icon")
    icon_json_path = os.path.join(icon_dir, "icon.json")
    if not os.path.exists(icon_json_path):
        fail("app icon not found at " + icon_json_path)
    icon = json.loads(read(icon_json_path))

    glyph_name = icon["groups"][0]["layers"][0]["image-name"]
    glyph_path = os.path.join(icon_dir, "Assets", glyph_name)
    if not os.path.exists(glyph_path):
        fail("icon glyph not found at " + glyph_path)
    write(glyph_path, read(os.path.join(KIT_DIR, "branding", "prism.svg")))

    icon["fill"]["linear-gradient"] = ICON_GRADIENT
    icon["fill"]["orientation"] = {"start": {"x": 0.2, "y": 0}, "stop": {"x": 0.8, "y": 1.0}}
    write(icon_json_path, json.dumps(icon, indent=2) + "\n")
    print("replaced app icon")


def rename_in_file(path, transform):
    content = read(path)
    updated = transform(content)
    if updated != content:
        write(path, updated)
        return True
    return False


def apply_name(root):
    changed = []

    # Info.plist fragments live inside Telegram/BUILD. Only touch <string> values.
    build_path = os.path.join(root, "Telegram", "BUILD")
    def fix_build(content):
        return re.sub(r"<string>([^<]*)</string>",
                      lambda m: "<string>" + m.group(1).replace(OLD_NAME, NEW_NAME) + "</string>",
                      content)
    if rename_in_file(build_path, fix_build):
        changed.append(build_path)

    # Permission texts and other InfoPlist.strings.
    def fix_strings_values(content):
        # "key" = "value";  -> rename only inside the value
        return re.sub(r'^(\s*"[^"]*"\s*=\s*")(.*)(";\s*)$',
                      lambda m: m.group(1) + m.group(2).replace(OLD_NAME, NEW_NAME) + m.group(3),
                      content, flags=re.MULTILINE)

    patterns = [
        os.path.join(root, "Telegram", "Telegram-iOS", "*.lproj", "InfoPlist.strings"),
        os.path.join(root, "Telegram", "Telegram-iOS", "*.lproj", "AppIntentVocabulary.plist"),
        os.path.join(root, "Swiftgram", "SGStrings", "Strings", "*.lproj", "*.strings"),
    ]
    for pattern in patterns:
        for path in glob.glob(pattern):
            if path.endswith(".strings"):
                if rename_in_file(path, fix_strings_values):
                    changed.append(path)

    # A few hard-coded titles in Swift code ("Swiftgram" string literals only).
    swift_files = [
        "Swiftgram/SGSettingsUI/Sources/SGSettingsController.swift",
        "submodules/TelegramCallsUI/Sources/CallKitIntegration.swift",
        "submodules/DebugSettingsUI/Sources/DebugController.swift",
        "submodules/PasscodeUI/Sources/PasscodeEntryControllerNode.swift",
        "submodules/PasscodeUI/Sources/PasscodeSetupControllerNode.swift",
        "submodules/PasscodeUI/Sources/PasscodeEntryController.swift",
        "submodules/ChatListUI/Sources/ChatListController.swift",
        "submodules/TelegramUI/Sources/ChatInterfaceStateContextMenus.swift",
        "submodules/TelegramUI/Components/PeerInfo/PeerInfoScreen/Sources/PeerInfoSettingsItems.swift",
        "submodules/SettingsUI/Sources/Data and Storage/WebBrowserSettingsController.swift",
    ]
    for relative_path in swift_files:
        path = os.path.join(root, relative_path)
        if not os.path.exists(path):
            print("warning: {} not found, skipping".format(relative_path))
            continue
        if rename_in_file(path, lambda c: c.replace('"{}"'.format(OLD_NAME), '"{}"'.format(NEW_NAME))):
            changed.append(path)

    if not any(p == build_path for p in changed):
        fail("app display name was not found in Telegram/BUILD")
    print("renamed app in {} files".format(len(changed)))


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    root = os.path.abspath(sys.argv[1])
    if not os.path.exists(os.path.join(root, "build-system", "Make", "Make.py")):
        fail("{} is not a Swiftgram / Telegram-iOS checkout".format(root))
    apply_patches(root)
    apply_icon(root)
    apply_name(root)
    print("PrismGram sources are ready.")


if __name__ == "__main__":
    main()
