#!/usr/bin/env python3
"""Cut the vocabulary pictures out of the theme PDFs.

The MEB theme sheets are picture grids: a row of illustrations, the English word
under each one. This finds those illustration boxes and saves them one by one so
the slides can show real pictures instead of emoji.

Run:  python tools/crop_vocab.py [--grade 5] [--unit 1] [--sheet]

  content/g5/u1/presentation/img/p01-03.png   page 1, third picture found
  content/g5/u1/presentation/img/index.json   reading-order list per page
  --sheet   also write contact-sheet-pNN.png so the crops can be eyeballed

Needs:  pip install pymupdf pillow numpy
"""

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, ROOT, ensure  # noqa: E402

try:
    import fitz
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit("Gerekli:  pip install pymupdf pillow numpy")

DPI = 200
WHITE = 234          # a pixel is "ink" when its darkest channel is below this
MIN_SIDE = 60        # ignore anything smaller than this many pixels
MAX_SIDE_FRAC = 0.55 # ignore page-wide banners
MIN_COLOUR = 0.16    # share of clearly coloured pixels that marks an illustration


def segments(mask_1d, gap=6, min_len=8):
    """Runs of True separated by at least `gap` False values."""
    out, start, blanks = [], None, 0
    for i, v in enumerate(mask_1d):
        if v:
            if start is None:
                start = i
            blanks = 0
        elif start is not None:
            blanks += 1
            if blanks >= gap:
                if i - blanks - start >= min_len:
                    out.append((start, i - blanks))
                start, blanks = None, 0
    if start is not None and len(mask_1d) - start >= min_len:
        out.append((start, len(mask_1d)))
    return out


def colourfulness(block):
    """Share of pixels that are neither near-white nor near-grey text."""
    mx = block.max(axis=2).astype(np.int16)
    mn = block.min(axis=2).astype(np.int16)
    sat = mx - mn
    return float(((sat > 40) & (mx > 60)).mean())


def find_pictures(arr):
    """Illustration boxes on one rendered page, in reading order."""
    h, w, _ = arr.shape
    ink = arr.min(axis=2) < WHITE

    # Section frames and text strokes are thin; illustrations are solid blocks.
    # Dropping thin structures leaves only the pictures, so the frame no longer
    # glues a whole section into one blob.
    d = 6
    pad_l = np.pad(ink, ((0, 0), (d, 0)))[:, :-d]
    pad_r = np.pad(ink, ((0, 0), (0, d)))[:, d:]
    pad_u = np.pad(ink, ((d, 0), (0, 0)))[:-d, :]
    pad_d = np.pad(ink, ((0, d), (0, 0)))[d:, :]
    ink = ink & (pad_l | pad_r) & (pad_u | pad_d)

    boxes = []

    # rows of cards -> single cards -> the picture inside a card (the caption
    # under it is a separate sub-block, which is how we tell them apart)
    for y0, y1 in segments(ink.any(axis=1), gap=10, min_len=MIN_SIDE):
        if y1 - y0 > h * 0.9:
            continue
        for sy0, sy1 in segments(ink[y0:y1].any(axis=1), gap=4, min_len=MIN_SIDE):
            py0, py1 = y0 + sy0, y0 + sy1
            for x0, x1 in segments(ink[py0:py1].any(axis=0), gap=8, min_len=40):
                bw, bh = x1 - x0, py1 - py0
                if bw < MIN_SIDE or bh < MIN_SIDE:
                    continue
                if bw > w * MAX_SIDE_FRAC or bh > h * MAX_SIDE_FRAC:
                    continue
                if not 0.45 < bw / bh < 2.6:
                    continue
                if colourfulness(arr[py0:py1, x0:x1]) < MIN_COLOUR:
                    continue
                boxes.append((x0, py0, x1, py1))

    # reading order: top-to-bottom, then left-to-right inside a row
    boxes.sort(key=lambda b: (b[1] // 40, b[0]))
    return boxes


def contact_sheet(img, boxes, path):
    sheet = img.copy().convert("RGB")
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for n, (x0, y0, x1, y1) in enumerate(boxes, 1):
        d.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=4)
        d.text((x0 + 6, y0 + 6), str(n), fill=(255, 0, 0))
    sheet.save(path, quality=70)


def process(gid, uid, pdf, want_sheet):
    out = os.path.join(CONTENT, gid, uid, "presentation", "img")
    ensure(out)
    doc = fitz.open(pdf)
    index = {}

    for pno, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=DPI)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        arr = np.asarray(img)
        boxes = find_pictures(arr)
        names = []
        for n, (x0, y0, x1, y1) in enumerate(boxes, 1):
            name = "p%02d-%02d.png" % (pno, n)
            img.crop((x0, y0, x1, y1)).save(os.path.join(out, name), optimize=True)
            names.append(name)
        index["p%02d" % pno] = names
        if want_sheet and boxes:
            contact_sheet(img, boxes, os.path.join(out, "contact-p%02d.jpg" % pno))
        print("  %s/%s p%d -> %d gorsel" % (gid, uid, pno, len(names)))

    with open(os.path.join(out, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    return sum(len(v) for v in index.values())


def targets(grade, unit):
    for path in sorted(glob.glob(os.path.join(ROOT, "res", "*", "*", "*.pdf"))):
        parts = path.replace("\\", "/").split("/")
        gm = re.search(r"(\d+)", parts[-3])
        um = re.search(r"(\d+)", parts[-2])
        if not gm or not um:
            continue
        if grade and int(gm.group(1)) != grade:
            continue
        if unit and int(um.group(1)) != unit:
            continue
        yield "g%s" % gm.group(1), "u%s" % um.group(1), path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", type=int)
    ap.add_argument("--unit", type=int)
    ap.add_argument("--sheet", action="store_true", help="kontrol gorseli de uret")
    args = ap.parse_args()

    total = 0
    for gid, uid, pdf in targets(args.grade, args.unit):
        total += process(gid, uid, pdf, args.sheet)
    print("toplam %d gorsel" % total)


if __name__ == "__main__":
    main()
