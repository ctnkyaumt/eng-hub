#!/usr/bin/env python3
"""Attach the downloaded word pictures to the grade-8 vocabulary cards.

Matching is by the exact English word, so a card only ever gets its own picture.
Run fetch_word_images.py first, then polish_slides.py --grade 8 to turn the new
pictures into picture questions.

Run:  python tools/link_word_images.py [--grade 8] [--clear]
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, ROOT  # noqa: E402

WORDS_DIR = os.path.join(ROOT, "app", "img", "words")
WEB_PREFIX = "/app/img/words/"

# Contact-sheet review found these automatic Commons hits misleading (for
# example, "treasure" was a star cluster and "pan" was an ancient coin). A
# clear topic pictogram is safer than teaching the wrong visual association.
REJECTED = {
    "account", "argue", "attachment", "avalanche", "come over", "dial",
    "disaster", "do an experiment", "download", "fashion", "hang out",
    "hang up", "invent", "lab", "melt", "pan", "pick up", "share",
    "spoon", "spread", "square", "teenager", "to-do list", "treasure",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", type=int, default=8)
    ap.add_argument("--clear", action="store_true", help="baglantilari kaldir")
    args = ap.parse_args()

    index = {}
    idx_path = os.path.join(WORDS_DIR, "index.json")
    if os.path.isfile(idx_path):
        with open(idx_path, encoding="utf-8") as f:
            index = {k.lower(): v for k, v in json.load(f).items()}

    total = 0
    pattern = os.path.join(CONTENT, "g%d" % args.grade, "u*", "presentation", "slides.json")
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        n = 0
        for slide in data.get("slides", []):
            if slide.get("type") != "vocab":
                continue
            for item in slide.get("items", []):
                word = (item.get("en") or "").lower()
                name = None if word in REJECTED else index.get(word)
                if args.clear or not name:
                    if (item.get("img") or "").startswith(WEB_PREFIX):
                        item.pop("img", None)
                    continue
                if not os.path.isfile(os.path.join(WORDS_DIR, name)):
                    continue
                item["img"] = WEB_PREFIX + name
                n += 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        unit = os.path.normpath(path).split(os.sep)[-3]
        print("  %-4s %2d kelimeye gorsel" % (unit, n))
        total += n
    print("toplam %d" % total)


if __name__ == "__main__":
    main()
