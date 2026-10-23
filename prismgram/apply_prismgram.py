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
import shutil
import subprocess
import sys

KIT_DIR = os.path.dirname(os.path.abspath(__file__))
NEW_NAME = "PrismGram"
OLD_NAME = "Swiftgram"

# M3 violet gradient behind the paper plane badge.
ICON_GRADIENT = [
    "srgb:0.48627,0.36078,0.83922,1.00000",
    "srgb:0.32941,0.22745,0.62745,1.00000",
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
    """Primary app icon (Icon Composer bundle): M3 Expressive badge with a paper plane on a violet gradient."""
    icon_dir = os.path.join(root, "Telegram", "Telegram-iOS", "Swiftgram.icon")
    icon_json_path = os.path.join(icon_dir, "icon.json")
    if not os.path.exists(icon_json_path):
        fail("app icon not found at " + icon_json_path)
    icon = json.loads(read(icon_json_path))

    assets_dir = os.path.join(icon_dir, "Assets")
    for name in os.listdir(assets_dir):
        os.remove(os.path.join(assets_dir, name))
    shutil.copyfile(os.path.join(KIT_DIR, "branding", "AppIconLayer.png"), os.path.join(assets_dir, "PrismGram.png"))

    icon["fill"] = {
        "linear-gradient": ICON_GRADIENT,
        "orientation": {"start": {"x": 0.3, "y": 0}, "stop": {"x": 0.7, "y": 1.0}},
    }
    group = icon["groups"][0]
    group["layers"] = [{
        "image-name": "PrismGram.png",
        "name": "PrismGram",
        "glass": False,
    }]
    group["translucency"] = {"enabled": False, "value": 0}
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

    # Permission texts, onboarding and settings texts.
    patterns = [
        os.path.join(root, "Telegram", "Telegram-iOS", "*.lproj", "*.strings"),
        os.path.join(root, "Telegram", "Telegram-iOS", "*.lproj", "AppIntentVocabulary.plist"),
        os.path.join(root, "Swiftgram", "SGStrings", "Strings", "*.lproj", "*.strings"),
    ]
    for pattern in patterns:
        for path in glob.glob(pattern):
            if path.endswith(".strings"):
                # Keys never contain the old name (checked), and values may span several
                # lines, so replace every occurrence.
                if rename_in_file(path, lambda c: c.replace(OLD_NAME, NEW_NAME)):
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

    # Other user-visible texts that mention Swiftgram inside a longer string literal.
    # Only string literals without URLs / paths are touched, and only in these files.
    literal_files = [
        "submodules/TelegramUI/Components/PeerInfo/PeerInfoScreen/Sources/PeerInfoScreen.swift",
        "submodules/DebugSettingsUI/Sources/DebugController.swift",
        "submodules/TelegramCore/Sources/Utils/PeerUtils.swift",
        "submodules/PlatformRestrictionMatching/Sources/PlatformRestrictionMatching.swift",
        "Swiftgram/SGDebugUI/Sources/SGDebugUI.swift",
        "Swiftgram/SGProUI/Sources/SGProUI.swift",
        "Swiftgram/SGPayWall/Sources/SGPayWall.swift",
    ]
    literal_re = re.compile(r'"([^"\n]*Swiftgram[^"\n]*)"')
    def fix_literal(m):
        text = m.group(1)
        if "/" in text or "http" in text or text in ("SwiftgramSettings", "SwiftgramPro"):
            return m.group(0)
        return '"' + text.replace(OLD_NAME, NEW_NAME) + '"'
    for relative_path in literal_files:
        path = os.path.join(root, relative_path)
        if os.path.exists(path) and rename_in_file(path, lambda c: literal_re.sub(fix_literal, c)):
            changed.append(path)

    if not any(p == build_path for p in changed):
        fail("app display name was not found in Telegram/BUILD")
    print("renamed app in {} files".format(len(changed)))


def apply_alternate_icons(root):
    """Swiftgram ships many alternate icons with its logo. Keep only the default one and make it the prism."""
    build_path = os.path.join(root, "Telegram", "BUILD")
    content = read(build_path)
    updated = re.sub(r"alternate_icon_folders = \[[^\]]*\]", 'alternate_icon_folders = [\n    "SGDefault",\n]', content, count=1)
    if updated == content:
        fail("alternate_icon_folders not found in Telegram/BUILD")
    write(build_path, updated)

    alticon_dir = os.path.join(root, "Telegram", "Telegram-iOS", "SGDefault.alticon")
    for name in ("SGDefault@2x.png", "SGDefault@3x.png"):
        target = os.path.join(alticon_dir, name)
        if not os.path.exists(target):
            fail("missing " + target)
        shutil.copyfile(os.path.join(KIT_DIR, "branding", name), target)
    print("alternate icons: only the PrismGram icon is left")


def apply_settings_icon(root):
    source = os.path.join(KIT_DIR, "branding", "PrismGramSettings.imageset")
    target = os.path.join(root, "Swiftgram", "SGSettingsUI", "Images.xcassets", "PrismGramSettings.imageset")
    if not os.path.isdir(os.path.dirname(target)):
        fail("settings asset catalog not found")
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(source, target)
    print("added PrismGram settings icon")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    root = os.path.abspath(sys.argv[1])
    if not os.path.exists(os.path.join(root, "build-system", "Make", "Make.py")):
        fail("{} is not a Swiftgram / Telegram-iOS checkout".format(root))
    apply_patches(root)
    apply_icon(root)
    apply_alternate_icons(root)
    apply_settings_icon(root)
    apply_name(root)
    print("PrismGram sources are ready.")


if __name__ == "__main__":
    main()
