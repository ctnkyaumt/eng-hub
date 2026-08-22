#!/usr/bin/env python3
"""Build labelled contact sheets for reviewing cropped Grade-5 source art.

Run: python tools/contact_grade5_images.py --unit 3 --out <folder>
"""

import argparse
import glob
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

from common import CONTENT, ensure


COLS = 6
CELL_W = 190
CELL_H = 165
IMAGE_H = 135


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    ensure(args.out)

    base = os.path.join(CONTENT, "g5", "u%d" % args.unit, "presentation", "img")
    font = ImageFont.load_default()
    pages = 0
    pictures = 0
    for page_key in sorted({os.path.basename(p)[:3] for p in glob.glob(os.path.join(base, "p??-*.png"))}):
        paths = sorted(glob.glob(os.path.join(base, page_key + "-*.png")))
        if not paths:
            continue
        rows = (len(paths) + COLS - 1) // COLS
        sheet = Image.new("RGB", (COLS * CELL_W, rows * CELL_H), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, path in enumerate(paths):
            x = (offset % COLS) * CELL_W
            y = (offset // COLS) * CELL_H
            with Image.open(path) as source:
                image = ImageOps.contain(source.convert("RGB"), (CELL_W - 10, IMAGE_H - 8))
            sheet.paste(image, (x + (CELL_W - image.width) // 2, y + (IMAGE_H - image.height) // 2))
            draw.rectangle((x, y, x + CELL_W - 1, y + CELL_H - 1), outline="#b7c0d0")
            draw.text((x + 7, y + IMAGE_H + 5), os.path.basename(path), fill="#111827", font=font)
        sheet.save(os.path.join(args.out, "g5-u%d-%s.jpg" % (args.unit, page_key)), quality=90)
        pages += 1
        pictures += len(paths)
    print("%d images -> %d contact sheets" % (pictures, pages))


if __name__ == "__main__":
    main()
