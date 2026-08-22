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

# Exact, visually reviewed mappings supplement the positional worksheet rows.
# They are especially important after a vocabulary section has been split into
# several slides: the title repeats, but the English word remains unambiguous.
WORD_MAP = {
    # Unit 2 - classroom objects from the original theme sheet
    ("u2", "Classroom Objects", "coloured pencil"): "p02-03.png",
    ("u2", "Classroom Objects", "crayon"): "p02-04.png",
    ("u2", "Classroom Objects", "pencil"): "p02-01.png",
    ("u2", "Classroom Objects", "pen"): "p02-02.png",
    ("u2", "Classroom Objects", "rubber / eraser"): "p02-05.png",
    ("u2", "Classroom Objects", "sharpener"): "p02-06.png",
    ("u2", "Classroom Objects", "pencil case"): "p02-07.png",
    ("u2", "Classroom Objects", "book"): "p02-08.png",
    ("u2", "Classroom Objects", "dictionary"): "p02-09.png",
    ("u2", "Classroom Objects", "material"): "p02-10.png",
    ("u2", "Classroom Objects", "ruler"): "p02-11.png",
    ("u2", "Classroom Objects", "glue"): "p02-12.png",
    ("u2", "Classroom Objects", "school bag"): "p02-13.png",
    ("u2", "Classroom Objects", "poster"): "p02-14.png",
    ("u2", "Classroom Objects", "map"): "p02-15.png",
    ("u2", "Classroom Objects", "notice board"): "p02-16.png",
    ("u2", "Classroom Objects", "board"): "p02-17.png",
    ("u2", "Classroom Objects", "bookcase"): "p02-18.png",
    ("u2", "Classroom Objects", "bookshelf"): "p02-19.png",
    ("u2", "Classroom Objects", "desk"): "p02-20.png",
    ("u2", "Classroom Objects", "table"): "p02-21.png",
    ("u2", "Classroom Objects", "seat"): "p02-22.png",

    # Unit 3 - generated comparison diagrams
    **{("u3", "Physical Features", word): "/app/img/vocab/physical-%s.svg" % slug
       for word, slug in {
           "straight": "straight", "wavy": "wavy", "curly": "curly",
           "dark": "dark", "fair": "fair", "blonde": "blonde",
           "thin / slim": "thin", "medium weight": "medium-weight", "fat": "fat",
           "short": "short", "medium height": "medium-height", "tall": "tall",
           "small": "small", "average": "average", "big": "big",
           "round": "round", "oval": "oval", "square": "square",
       }.items()},

    # Unit 3 - clothing/accessories from the original theme sheet
    ("u3", "Clothes", "trousers / pants"): "p02-01.png",
    ("u3", "Clothes", "jeans"): "p02-02.png",
    ("u3", "Clothes", "coat"): "p02-03.png",
    ("u3", "Clothes", "raincoat"): "p02-04.png",
    ("u3", "Clothes", "jacket"): "p02-05.png",
    ("u3", "Clothes", "jumper / sweater"): "p02-06.png",
    ("u3", "Clothes", "cardigan"): "/app/img/vocab/cardigan.jpg",
    ("u3", "Clothes", "blouse"): "p02-07.png",
    ("u3", "Clothes", "shirt"): "p02-08.png",
    ("u3", "Clothes", "t-shirt"): "p02-09.png",
    ("u3", "Clothes", "dress"): "p02-10.png",
    ("u3", "Clothes", "skirt"): "/app/img/vocab/skirt.jpg",
    ("u3", "Clothes", "fancy dress / costume"): "p02-11.png",
    ("u3", "Clothes", "uniform"): "p02-12.png",
    ("u3", "Accessories", "gloves"): "p02-13.png",
    ("u3", "Accessories", "scarf"): "p02-14.png",
    ("u3", "Accessories", "headscarf"): "p02-15.png",
    ("u3", "Accessories", "socks"): "p02-16.png",
    ("u3", "Accessories", "bow"): "p02-17.png",
    ("u3", "Accessories", "hat"): "p02-18.png",
    ("u3", "Accessories", "cap"): "p02-19.png",
    ("u3", "Accessories", "shoes"): "p02-20.png",
    ("u3", "Accessories", "boots"): "p02-21.png",
    ("u3", "Accessories", "belt"): "p02-22.png",
    ("u3", "Accessories", "bag"): "p03-01.png",
    ("u3", "Accessories", "handbag"): "p03-02.png",
    ("u3", "Accessories", "backpack"): "p03-03.png",
    ("u3", "Accessories", "watch"): "p03-04.png",
    ("u3", "Accessories", "umbrella"): "p03-05.png",
    ("u3", "Accessories", "ring"): "p03-06.png",
    ("u3", "Accessories", "earrings"): "p03-07.png",
    ("u3", "Accessories", "necklace"): "p03-08.png",
    ("u3", "Adjectives", "long"): "/app/img/vocab/adjective-long.svg",
    ("u3", "Adjectives", "short"): "/app/img/vocab/adjective-short.svg",
    ("u3", "Adjectives", "new"): "/app/img/vocab/adjective-new.svg",

    # Other duplicate or ambiguous cards found by the all-deck audit
    ("u5", "Parts of a House", "flat / apartment"): "p02-01.png",
    ("u5", "Parts of a House", "sitting / living room"): "p02-02.png",
    ("u5", "Parts of a House", "bedroom"): "p02-03.png",
    ("u5", "Parts of a House", "dining room"): "p02-04.png",
    ("u5", "Parts of a House", "kitchen"): "p02-05.png",
    ("u5", "Parts of a House", "garden"): "p02-06.png",
    ("u5", "Parts of a House", "balcony"): "p02-07.png",
    ("u5", "Parts of a House", "terrace"): "p02-08.png",
    ("u5", "Parts of a House", "corridor / hallway"): "p02-09.png",
    ("u5", "Parts of a House", "floor"): "p02-10.png",
    ("u5", "Parts of a House", "ground"): "p02-11.png",
    ("u5", "Parts of a House", "roof"): "p02-12.png",
    ("u5", "Parts of a House", "stairs"): "p02-13.png",
    ("u5", "Parts of a House", "lift / elevator"): "p02-14.png",
    ("u5", "Parts of a House", "wall"): "p02-15.png",
    ("u5", "Parts of a House", "window"): "p02-16.png",
    ("u5", "Parts of a House", "door"): "p02-17.png",
    ("u5", "Furniture & Kitchen Utensils", "sofa"): "p02-18.png",
    ("u5", "Furniture & Kitchen Utensils", "armchair"): "p02-19.png",
    ("u5", "Furniture & Kitchen Utensils", "chair"): "p02-20.png",
    ("u5", "Furniture & Kitchen Utensils", "table"): "p02-21.png",
    ("u5", "Furniture & Kitchen Utensils", "bed"): "p02-22.png",
    **{("u6", "Food — Vegetables & More", word): "p01-%02d.png" % number
       for word, number in {
           "pepper": 13, "cucumber": 14, "tomato": 15, "beans": 16,
           "garlic": 17, "mushroom": 18, "lettuce": 19, "corn": 20,
           "lentil": 21, "cinnamon": 22, "olives": 23, "lemon": 24,
           "apple": 25, "meat": 26, "beef": 27, "fish": 28,
           "tuna": 29, "oil": 30, "egg": 31, "dairy products": 32,
       }.items()},
    **{("u6", "Food — Sweet & Bakery", word): "p02-%02d.png" % number
       for word, number in {
           "cheese": 1, "butter": 2, "sauce": 3, "spices": 4,
           "sugar": 5, "flour": 6, "nuts": 7, "jam": 8,
           "chocolate": 9, "sweet / candy": 10, "biscuit / cookie": 11,
           "muffin": 12, "pancake": 13, "tart": 14, "croissant": 15,
           "ice cream": 16, "bread": 17, "pasta": 18, "meatball": 19,
           "dough": 20, "water": 21, "fruit juice": 23,
       }.items()},
    ("u6", "Food — Sweet & Bakery", "ayran"): "/app/img/vocab/ayran.jpg",
    ("u6", "Kitchen Utensils", "plate"): "p02-24.png",
    ("u6", "Kitchen Utensils", "glass"): "p02-25.png",
    ("u6", "Kitchen Utensils", "cup"): "p02-26.png",
    ("u6", "Kitchen Utensils", "tablespoon"): "/app/img/vocab/tablespoon.svg",
    ("u6", "Kitchen Utensils", "teaspoon"): "/app/img/vocab/teaspoon.svg",
    ("u7", "Animals", "seal"): "/app/img/vocab/animal-seal.svg",
    **{("u8", "Holiday Activities", word): "p02-%02d.png" % number
       for word, number in {
           "climb a mountain": 1, "go sightseeing": 2, "go hiking": 3,
           "go fishing": 4, "go snorkelling": 5, "go scuba diving": 6,
           "swim": 7, "make a sandcastle": 8, "collect seashells": 9,
           "ride a camel": 10, "ride a bike": 11, "have a picnic": 12,
           "take a boat tour": 13, "visit a museum": 14,
       }.items()},
}

WORD_EMOJI = {
    ("u2", "Days of the Week", day): icon
    for day, icon in zip(
        ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"),
        ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"),
    )
}


def unit_of(path):
    return os.path.normpath(path).split(os.sep)[-3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="sayfa basina gorsel sayisini yaz")
    ap.add_argument(
        "--clear",
        action="store_true",
        help="yerel tema foyu gorsel baglantilarini kaldir",
    )
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
        vocab_slides = [s for s in data.get("slides", []) if s.get("type") == "vocab"]
        for s in vocab_slides:
            for it in s.get("items", []):
                # This tool owns unit-local crop links. Preserve separately
                # reviewed global assets such as country flags and Commons art.
                if not (it.get("img") or "").startswith("/app/"):
                    it.pop("img", None)

        if not args.clear:
            # A section may now span several classroom-sized slides. Flatten
            # its parts before applying the original worksheet reading order.
            for (map_unit, title), (page, start, count) in MAP.items():
                if map_unit != unit:
                    continue
                items = [it for s in vocab_slides if s.get("title") == title
                         for it in s.get("items", [])]
                crops = index.get(page, [])[start - 1: start - 1 + count]
                if len(crops) != count or count != len(items):
                    print("  ! %s / %s: %d gorsel, %d kelime - atlandi"
                          % (unit, title, len(crops), len(items)))
                    continue
                for it, name in zip(items, crops):
                    it["img"] = name
                    n += 1

            # Exact mappings remain safe regardless of how many parts a title
            # occupies and deliberately override a positional source image.
            for s in vocab_slides:
                for it in s.get("items", []):
                    word_key = (unit, s.get("title"), (it.get("en") or "").lower())
                    name = WORD_MAP.get(word_key)
                    if name:
                        if not it.get("img"):
                            n += 1
                        it["img"] = name
                    icon = WORD_EMOJI.get(word_key)
                    if icon:
                        it["emoji"] = icon

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print("  %s  %3d kelimeye gorsel" % (unit, n))
        total += n

    if not args.check:
        print("toplam %d" % total)


if __name__ == "__main__":
    main()
