#!/usr/bin/env python3
"""Draws prismgram/branding/AppBadge@3x.png: the pill shown next to the Dynamic Island."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "..", "channel", "fonts", "InterDisplay-ExtraBold.otf")
OUT = os.path.join(HERE, "..", "AppBadge@3x.png")

S = 4                      # supersampling
H = 66                     # same height as the Swiftgram badge (@3x)
TEXT = "PRISMGRAM"
font = ImageFont.truetype(FONT, 31 * S)
probe = ImageDraw.Draw(Image.new("L", (1, 1)))
box = probe.textbbox((0, 0), TEXT, font=font)
text_x = 64 * S
W = (text_x + (box[2] - box[0])) // S + 24

img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
grad = Image.new("RGBA", (W * S, H * S))
start, end = (140, 100, 240), (92, 60, 180)
for x in range(W * S):
    t = x / (W * S)
    color = tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3)) + (255,)
    grad.paste(color, (x, 0, x + 1, H * S))
mask = Image.new("L", (W * S, H * S), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, W * S - 1, H * S - 1), radius=H * S // 2, fill=255)
img.paste(grad, (0, 0), mask)

draw = ImageDraw.Draw(img)
# Paper plane from the app icon (1024 px coordinates), fitted into a 38 px box.
scale = (38 * S) / 455
ox, oy = 18 * S, 12 * S
def plane(points):
    return [(ox + (x - 280) * scale, oy + (y - 318) * scale) for x, y in points]
draw.polygon(plane([(280, 508), (725, 318), (480, 560)]), fill=(255, 255, 255, 255))
draw.polygon(plane([(484, 566), (735, 322), (565, 750), (525, 630)]), fill=(255, 255, 255, 205))
draw.polygon(plane([(470, 580), (520, 630), (458, 668)]), fill=(255, 255, 255, 165))

text_y = (H * S - (box[3] - box[1])) / 2 - box[1]
draw.text((text_x, text_y), TEXT, font=font, fill=(255, 255, 255, 255))
img.resize((W, H), Image.LANCZOS).save(OUT)
print("wrote {} ({}x{})".format(OUT, W, H))
