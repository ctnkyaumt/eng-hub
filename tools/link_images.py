#!/usr/bin/env python3
"""Attach cropped sheet pictures to the vocabulary cards in slides.json.

Matching is done from an explicit table rather than guessed: a wrong picture is
worse than no picture. Each entry says which page a section's illustrations come
from and where in that page's reading order they start. crop_vocab.py must have
run first; `--check` prints the crop count per page so new entries can be added.

Run:  python tools/link_images.py [--check] [--clear]
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT  # noqa: E402

# (unit, slide title) -> (page key, 1-based start in reading order, how many)
MAP = {
    ("u1", "People at School"): ("p01", 1, 6),
    ("u1", "Places at School"): ("p01", 7, 8),

    ("u2", "School Subjects"): ("p05", 1, 12),

    ("u3", "Body Parts"): ("p01", 1, 20),
    ("u3", "Daily Routines"): ("p04", 1, 16),

    ("u4", "Family Members"): ("p01", 1, 11),
    ("u4", "Daily Routines (1)"): ("p01", 12, 12),
    ("u4", "Daily Routines (2)"): ("p02", 1, 8),
    ("u4", "Hobbies and Activities"): ("p02", 9, 20),

    ("u5", "Places for Recreation & Attractions"): ("p01", 1, 20),

    ("u7", "Body Parts of Animals"): ("p02", 1, 10),
    ("u7", "Habitats"): ("p02", 11, 10),

    ("u8", "Planet Earth"): ("p01", 1, 20),
}


def unit_of(path):
    return os.path.normpath(path).split(os.sep)[-3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="sayfa basina gorsel sayisini yaz")
    ap.add_argument("--clear", action="store_true", help="tum gorsel baglantilarini kaldir")
    args = ap.parse_args()

    total = 0
    for path in sorted(glob.glob(os.path.join(CONTENT, "g5", "u*", "presentation", "slides.json"))):
        unit = unit_of(path)
        idx_path = os.path.join(os.path.dirname(path), "img", "index.json")
        index = {}
        if os.path.isfile(idx_path):
            with open(idx_path, encoding="utf-8") as f:
                index = json.load(f)

        if args.check:
            print(unit, {k: len(v) for k, v in sorted(index.items()) if v})
            continue

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        n = 0
        for s in data.get("slides", []):
            if s.get("type") != "vocab":
                continue
            for it in s.get("items", []):
                it.pop("img", None)
            if args.clear:
                continue
            key = (unit, s.get("title"))
            if key not in MAP:
                continue
            page, start, count = MAP[key]
            crops = index.get(page, [])[start - 1: start - 1 + count]
            if len(crops) != count or count != len(s["items"]):
                print("  ! %s / %s: %d gorsel, %d kelime - atlandi"
                      % (unit, s["title"], len(crops), len(s["items"])))
                continue
            for it, name in zip(s["items"], crops):
                it["img"] = name
                n += 1

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print("  %s  %3d kelimeye gorsel" % (unit, n))
        total += n

    if not args.check:
        print("toplam %d" % total)


if __name__ == "__main__":
    main()
