#!/usr/bin/env python3
"""Put country flags on the USB as SVG files.

Windows has no flag emoji, so 🇹🇷 shows up as the letters "TR". These SVGs are
stored once under app/img/flags/ and used by the Countries slides instead.

Run:  python tools/fetch_flags.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, ROOT, ensure, http_get, log  # noqa: E402

DEST = os.path.join(ROOT, "app", "img", "flags")
CDN = "https://flagcdn.com/%s.svg"

# English name on the slide -> flagcdn code
CODES = {
    "Türkiye": "tr", "Germany": "de", "France": "fr", "Italy": "it", "Spain": "es",
    "Russia": "ru", "the USA": "us", "the UK": "gb", "England": "gb-eng",
    "Scotland": "gb-sct", "Northern Ireland": "gb-nir", "Wales": "gb-wls",
    "Canada": "ca", "Mexico": "mx", "Australia": "au", "Greece": "gr", "Egypt": "eg",
    "Argentina": "ar", "Brazil": "br", "Japan": "jp", "China": "cn",
    "South Korea": "kr", "Azerbaijan": "az", "Uzbekistan": "uz",
    "Turkmenistan": "tm", "Kazakhstan": "kz", "Kyrgyzstan": "kg",
    "Northern Cyprus": "kktc",  # flagcdn has no KKTC entry - drawn by hand
}
LOCAL_ONLY = {"kktc"}  # already on the USB, never downloaded


def main():
    ensure(DEST)
    got = 0
    for name, code in sorted(set(CODES.items())):
        path = os.path.join(DEST, code + ".svg")
        if code in LOCAL_ONLY:
            got += os.path.exists(path)
            continue
        if not os.path.exists(path):
            try:
                raw, _ = http_get(CDN % code, timeout=45, retries=2, binary=True)
            except Exception as exc:  # noqa: BLE001
                log("flags.log", "HATA %s (%s) -> %s" % (name, code, exc))
                continue
            with open(path, "wb") as f:
                f.write(raw)
        got += 1
    print("%d bayrak hazir: %s" % (got, DEST))

    # write them onto every Countries slide we can find
    import glob
    n = 0
    for p in glob.glob(os.path.join(CONTENT, "g*", "u*", "presentation", "slides.json")):
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        touched = False
        for s in data.get("slides", []):
            if s.get("type") != "vocab":
                continue
            for it in s.get("items", []):
                code = CODES.get(it.get("en"))
                if code and os.path.exists(os.path.join(DEST, code + ".svg")):
                    it["img"] = "/app/img/flags/%s.svg" % code
                    it.pop("emoji", None)
                    touched = True
                    n += 1
        if touched:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
    print("%d kelime kartina bayrak baglandi" % n)


if __name__ == "__main__":
    main()
