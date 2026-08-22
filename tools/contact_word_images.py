#!/usr/bin/env python3
"""Build labelled contact sheets for visually checking Grade-8 word photos.

Run: python tools/contact_word_images.py --out <folder>
"""

import argparse
import glob
import json
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

from common import ROOT, ensure


COLS = 5
ROWS = 4
CELL_W = 230
CELL_H = 175
PHOTO_H = 140


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    ensure(args.out)

    base = os.path.join(ROOT, "app", "img", "words")
    index_path = os.path.join(base, "index.json")
    with open(index_path, encoding="utf-8") as handle:
        index = json.load(handle)
    labels = {name: word for word, name in index.items()}
    paths = [p for p in sorted(glob.glob(os.path.join(base, "*.*")))
             if os.path.basename(p) in labels]
    font = ImageFont.load_default()

    for page, start in enumerate(range(0, len(paths), COLS * ROWS), 1):
        sheet = Image.new("RGB", (COLS * CELL_W, ROWS * CELL_H), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, path in enumerate(paths[start:start + COLS * ROWS]):
            x = (offset % COLS) * CELL_W
            y = (offset // COLS) * CELL_H
            with Image.open(path) as source:
                image = ImageOps.contain(source.convert("RGB"), (CELL_W - 10, PHOTO_H - 10))
            px = x + (CELL_W - image.width) // 2
            py = y + (PHOTO_H - image.height) // 2
            sheet.paste(image, (px, py))
            draw.rectangle((x, y, x + CELL_W - 1, y + CELL_H - 1), outline="#b7c0d0")
            draw.text((x + 7, y + PHOTO_H + 5), labels[os.path.basename(path)], fill="#111827", font=font)
        sheet.save(os.path.join(args.out, "word-images-%02d.jpg" % page), quality=88)
    print("%d images -> %d contact sheets" % (len(paths), page))


if __name__ == "__main__":
    main()
