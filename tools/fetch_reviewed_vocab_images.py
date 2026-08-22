#!/usr/bin/env python3
"""Download a tiny, manually reviewed set of Wikimedia vocabulary images.

Unlike fetch_word_images.py, this list uses exact Commons file names and keeps
the source/licence beside the mapping. Do not add an automatic search result
here without inspecting it first.

Run: python tools/fetch_reviewed_vocab_images.py [--force]
"""

import argparse
import os
import urllib.parse

from common import ROOT, ensure, http_get


DEST = os.path.join(ROOT, "app", "img", "vocab")
COMMONS_REDIRECT = "https://commons.wikimedia.org/wiki/Special:Redirect/file/"
USER_AGENT = "ENGHUB/1.0 (offline classroom presentation tool for MEB English lessons)"

FILES = {
    "ayran.jpg": {
        "commons": "Ayran in a beer glass.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Ayran_in_a_beer_glass.jpg",
        "credit": "E4024, CC BY-SA 4.0",
    },
    "skirt.jpg": {
        "commons": "Skirt.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Skirt.jpg",
        "credit": "David Ring / Europeana Fashion / MoMu, CC0",
    },
    "cardigan.jpg": {
        "commons": "Cardigan (clothing).jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Cardigan_(clothing).jpg",
        "credit": "David Ring / Europeana Fashion / MoMu, CC0",
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    ensure(DEST)

    written = skipped = 0
    for output, info in FILES.items():
        target = os.path.join(DEST, output)
        if os.path.isfile(target) and not args.force:
            skipped += 1
            continue
        url = COMMONS_REDIRECT + urllib.parse.quote(info["commons"]) + "?width=700"
        raw, _ = http_get(url, timeout=60, retries=2, binary=True,
                          headers={"User-Agent": USER_AGENT})
        with open(target, "wb") as handle:
            handle.write(raw)
        written += 1
    print("reviewed Commons images: written %d, skipped %d" % (written, skipped))


if __name__ == "__main__":
    main()
