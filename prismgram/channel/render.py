#!/usr/bin/env python3
"""
Draws the images for the @prismgram_ios channel.

    python3 prismgram/channel/render.py avatar  out/avatar.png
    python3 prismgram/channel/render.py hero    out/hero.png
    python3 prismgram/channel/render.py release out/release.png 1.0.1 3754

Needs Pillow. Fonts are bundled in prismgram/channel/fonts (Inter, OFL).
"""

import datetime
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BRANDING = os.path.join(HERE, "..", "branding")
FONTS = os.path.join(HERE, "fonts")

# Same violet as the app icon.
TOP = (124, 92, 214)
BOTTOM = (84, 58, 160)
ON_DARK = (255, 255, 255)
ON_DARK_SOFT = (232, 222, 255)
CHIP = (234, 221, 255)
ON_CHIP = (33, 0, 93)

MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
          "августа", "сентября", "октября", "ноября", "декабря"]


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def gradient(width, height):
    """Diagonal violet gradient, like the icon background."""
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            t = (0.35 * x / width + 0.65 * y / height)
            pixels[x, y] = tuple(int(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3))
    return image


def cookie(size, waves=12, depth=0.06):
    """M3 Expressive 'cookie' shape as an alpha mask."""
    scale = 4
    big = size * scale
    mask = Image.new("L", (big, big), 0)
    draw = ImageDraw.Draw(mask)
    center = big / 2
    radius = big / 2 * (1 - depth)
    points = []
    for i in range(720):
        angle = 2 * math.pi * i / 720
        r = radius * (1 + depth * math.cos(waves * angle))
        points.append((center + r * math.cos(angle), center + r * math.sin(angle)))
    draw.polygon(points, fill=255)
    return mask.resize((size, size), Image.LANCZOS)


def soft_blob(canvas, box, color, alpha, waves=8, depth=0.08, blur=0):
    """Big decorative shape in the background."""
    x, y, size = box
    mask = cookie(size, waves=waves, depth=depth).point(lambda v: v * alpha // 255)
    if blur:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGB", (size, size), color)
    canvas.paste(layer, (x, y), mask)


def badge(size):
    """The app icon's paper-plane badge (transparent background)."""
    layer = Image.open(os.path.join(BRANDING, "AppIconLayer.png")).convert("RGBA")
    return layer.resize((size, size), Image.LANCZOS)


def chip(draw, x, y, text, text_font, fill=CHIP, color=ON_CHIP, pad_x=30, height=64):
    width = int(draw.textlength(text, font=text_font)) + pad_x * 2
    draw.rounded_rectangle((x, y, x + width, y + height), radius=height // 2, fill=fill)
    bbox = draw.textbbox((0, 0), text, font=text_font)
    text_y = y + (height - (bbox[3] - bbox[1])) / 2 - bbox[1]
    draw.text((x + pad_x, text_y), text, font=text_font, fill=color)
    return width


def render_avatar(path):
    size = 1024
    image = gradient(size, size)
    soft_blob(image, (-260, -300, 760), (150, 120, 235), 90, waves=7)
    soft_blob(image, (560, 600, 640), (70, 44, 140), 110, waves=9)
    # Telegram crops the avatar to a circle, so make the badge a bit bigger than on the icon.
    layer = badge(1180)
    image.paste(layer, ((size - 1180) // 2, (size - 1180) // 2), layer)
    image.save(path)


def render_hero(path):
    width, height = 1280, 720
    image = gradient(width, height)
    soft_blob(image, (820, -260, 760), (150, 120, 235), 80, waves=7)
    soft_blob(image, (-220, 420, 560), (70, 44, 140), 120, waves=9)
    layer = badge(640)
    image.paste(layer, (width - 640 + 40, (height - 640) // 2), layer)

    draw = ImageDraw.Draw(image)
    draw.text((80, 110), "Telegram для iPhone", font=font("Inter-SemiBold.otf", 38), fill=ON_DARK_SOFT)
    draw.text((74, 160), "PrismGram", font=font("InterDisplay-ExtraBold.otf", 132), fill=ON_DARK)

    chip_font = font("Inter-SemiBold.otf", 30)
    rows = [["Режим призрака", "Без рекламы"], ["Удалённые сообщения"], ["История правок", "Обновления"]]
    y = 350
    for row in rows:
        x = 80
        for text in row:
            x += chip(draw, x, y, text, chip_font) + 16
        y += 82
    image.save(path)


def render_release(path, version, build):
    width, height = 1280, 720
    image = gradient(width, height)
    soft_blob(image, (840, -240, 760), (150, 120, 235), 80, waves=7)
    soft_blob(image, (-200, 460, 520), (70, 44, 140), 120, waves=9)
    layer = badge(600)
    image.paste(layer, (width - 600 + 20, (height - 600) // 2), layer)

    draw = ImageDraw.Draw(image)
    chip(draw, 80, 120, "Обновление", font("Inter-SemiBold.otf", 30))
    draw.text((80, 214), "PrismGram", font=font("Inter-SemiBold.otf", 56), fill=ON_DARK_SOFT)
    draw.text((72, 270), version, font=font("InterDisplay-ExtraBold.otf", 200), fill=ON_DARK)
    today = datetime.date.today()
    date = "{} {} {}".format(today.day, MONTHS[today.month - 1], today.year)
    draw.text((80, 520), "сборка {}  ·  {}".format(build, date), font=font("Inter-Medium.otf", 36), fill=ON_DARK_SOFT)
    image.save(path)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    kind, path = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if kind == "avatar":
        render_avatar(path)
    elif kind == "hero":
        render_hero(path)
    elif kind == "release" and len(sys.argv) == 5:
        render_release(path, sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
        sys.exit(2)
    print("wrote " + path)


if __name__ == "__main__":
    main()
