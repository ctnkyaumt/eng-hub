#!/usr/bin/env python3
"""Give the grade-8 word cards real pictures.

Grade 8 has no MEB theme sheets to cut pictures out of, and the book's own
illustrations carry no captions, so a picture cannot be tied to a word from it.
Instead each picture-worthy word is looked up once on Wikimedia Commons (freely
licensed) and the thumbnail is stored on the USB, so lessons stay offline.

Only concrete words are listed: "grater" and "avalanche" photograph well,
"loyalty" and "available" do not, and a wrong picture teaches the wrong thing.
Where the bare word finds the wrong subject a better search phrase is given.

Run:  python tools/fetch_word_images.py [--force]
      python tools/link_word_images.py          (attach them to the slides)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, ensure, http_get, log, progress  # noqa: E402

DEST = os.path.join(ROOT, "app", "img", "words")
API = "https://commons.wikimedia.org/w/api.php"
# Wikimedia asks bots to identify themselves and to keep one request in flight
WM_UA = "ENGHUB/1.0 (offline classroom presentation tool for MEB English lessons)"
PAUSE = 2.0      # seconds between requests
COOLDOWN = 25.0  # wait this long when they answer 429 "slow down"

# word -> search phrase (None = search the word itself)
WORDS = {
    # unit 1 friendship
    "best friend": "best friends children", "concert": "rock concert crowd",
    "go for a walk": "people walking park", "come over": "guest at front door",
    "treasure": "treasure chest gold", "promise": "pinky promise hands",
    "secret": "whispering secret", "share": "children sharing food",
    # unit 2 teen life
    "teenager": "teenagers group", "fashion": "fashion clothes shop",
    "hang out": "teenagers hanging out park", "argue": "two people arguing",
    "types of music": "musical instruments collection",
    # unit 3 kitchen
    "bake": "baking bread oven", "boil": "boiling water pot", "bowl": "mixing bowl",
    "chop": "chopping vegetables knife", "dice": "diced vegetables",
    "fry": "frying pan food", "grater": "cheese grater", "mash": "mashed potatoes",
    "mix": "mixing dough bowl", "oven": "kitchen oven", "pan": "frying pan",
    "peel": "peeling potato", "pour": "pouring water glass", "saucepan": "saucepan",
    "slice": "slicing bread", "spoon": "wooden spoon", "spread": "spreading butter bread",
    "oil": "olive oil bottle", "recipe": "recipe book", "meal": "dinner meal table",
    "dessert": "dessert cake", "ingredient": "cooking ingredients",
    # unit 4 phone
    "dial": "rotary phone dial", "pick up": "answering telephone",
    "hang up": "hanging up telephone", "line": "telephone line pole", "memo": "sticky note memo",
    # unit 5 internet
    "browser": "web browser screen", "screen": "computer screen",
    "search engine": "search engine screen", "download": "download icon screen",
    "upload": "upload cloud icon", "attachment": "paper clip attachment",
    "account": "login screen account", "connection": "wifi router",
    # unit 6 adventures
    "bungee-jumping": "bungee jumping", "canoeing": "canoe paddling river",
    "caving": "caving cave explorer", "hang-gliding": "hang glider",
    "kayaking": "kayak paddling", "motor racing": "motor racing car",
    "paragliding": "paraglider flying", "rafting": "white water rafting",
    "skateboarding": "skateboarder skatepark", "extreme sports": "extreme sport jump",
    # unit 7 tourism
    "ancient": "ancient ruins temple", "architecture": "historic architecture building",
    "attraction": "tourist attraction crowd", "historic site": "historic site ruins",
    "square": "city square fountain", "resort": "beach resort hotel",
    "countryside": "countryside landscape", "bed and breakfast": "bed and breakfast house",
    "culture": "traditional folk dance", "rural": "rural village farm",
    "urban": "city skyline street", "destination": "airport departure board",
    # unit 8 chores
    "make the bed": "making the bed", "set the table": "setting the table",
    "wash the dishes": "washing dishes sink", "dry the dishes": "drying dishes towel",
    "load the dishwasher": "loading dishwasher", "empty the dishwasher": "open dishwasher dishes",
    "do the laundry": "laundry washing machine", "laundry": "laundry basket clothes",
    "iron": "ironing clothes iron", "clean up": "cleaning floor mop",
    "tidy up": "tidy room shelves", "take out the garbage": "taking out trash bag",
    "return books": "returning library books", "to-do list": "to do list notebook",
    # unit 9 science
    "lab": "science laboratory", "do an experiment": "student science experiment",
    "test tube": "test tubes rack", "cell": "plant cell microscope",
    "safety": "safety goggles lab", "explode": "explosion smoke",
    "genius": "albert einstein", "high-tech": "robot technology",
    "invent": "old invention machine", "vaccination": "vaccination injection arm",
    "cure": "medicine pills", "discover": "microscope discovery",
    # unit 10 natural forces
    "earthquake": "earthquake damaged building", "flood": "flooded street town",
    "drought": "drought cracked dry earth", "avalanche": "snow avalanche mountain",
    "landslide": "landslide road damage", "hurricane": "hurricane satellite image",
    "tornado": "tornado funnel storm", "tsunami": "tsunami wave coast",
    "volcano": "volcano eruption lava", "disaster": "disaster rescue rubble",
    "global warming": "melting glacier climate", "melt": "melting ice",
    "survivor": "rescue worker survivor",
}


def slug(word):
    return re.sub(r"[^a-z0-9]+", "-", word.lower()).strip("-")


def search(query):
    """Best Commons thumbnail for a query, preferring a title that matches."""
    url = (API + "?action=query&format=json&generator=search&gsrnamespace=6"
           "&gsrlimit=8&prop=imageinfo&iiprop=url&iiurlwidth=400&gsrsearch="
           + urllib.parse.quote("filetype:bitmap " + query))
    data = json.loads(http_get(url, timeout=45, retries=2,
                               headers={"User-Agent": WM_UA}))
    pages = list((data.get("query") or {}).get("pages", {}).values())
    pages.sort(key=lambda p: p.get("index", 99))
    words = [w for w in re.findall(r"[a-z]+", query.lower()) if len(w) > 3]

    def score(p):
        title = p.get("title", "").lower()
        return -sum(w in title for w in words)

    hits = [p for p in pages if p.get("imageinfo")]
    hits.sort(key=score)
    return hits[0]["imageinfo"][0]["thumburl"] if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    ensure(DEST)

    index = {}
    idx_path = os.path.join(DEST, "index.json")
    if os.path.isfile(idx_path) and not args.force:
        with open(idx_path, encoding="utf-8") as f:
            index = json.load(f)

    items = sorted(WORDS.items())
    ok = fail = skip = 0
    for n, (word, query) in enumerate(items, 1):
        progress(n, len(items), word)
        name = slug(word) + ".jpg"
        path = os.path.join(DEST, name)
        if os.path.isfile(path) and not args.force:
            index[word] = name
            skip += 1
            continue
        for attempt in range(3):
            try:
                time.sleep(PAUSE)
                url = search(query or word)
                if not url:
                    raise RuntimeError("sonuc yok")
                time.sleep(PAUSE)
                raw, _ = http_get(url, timeout=60, retries=1, binary=True,
                                  headers={"User-Agent": WM_UA})
                with open(path, "wb") as f:
                    f.write(raw)
                index[word] = name
                ok += 1
                break
            except Exception as exc:  # noqa: BLE001
                # 429 just means "too fast" - wait it out instead of giving up
                if "429" in str(exc) and attempt < 2:
                    time.sleep(COOLDOWN)
                    continue
                fail += 1
                log("word-images.log", "HATA %s -> %s" % (word, exc))
                break

    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print("indirilen %d  atlanan %d  basarisiz %d  (toplam %d kelime)"
          % (ok, skip, fail, len(index)))


if __name__ == "__main__":
    main()
