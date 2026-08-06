#!/usr/bin/env python3
"""Check that everything the catalog promises actually exists on the USB.

Run:  python tools/verify_content.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, DATA, ROOT  # noqa: E402


def main():
    cat_path = os.path.join(DATA, "catalog.json")
    if not os.path.isfile(cat_path):
        sys.exit("catalog.json yok - once: python tools/fetch_catalog.py")
    with open(cat_path, encoding="utf-8") as f:
        cat = json.load(f)

    problems = []
    stats = {"unite": 0, "sunum": 0, "oyun": 0, "kagit": 0, "kopya": 0, "bos": 0}

    for g in cat["grades"]:
        for u in g["units"]:
            stats["unite"] += 1
            base = os.path.join(CONTENT, g["id"], u["id"])
            where = "%s/%s" % (g["id"], u["id"])

            slides = os.path.join(base, "presentation", "slides.json")
            if os.path.isfile(slides):
                stats["sunum"] += 1
                with open(slides, encoding="utf-8") as f:
                    data = json.load(f)
                for p in data.get("pages", []):
                    if not os.path.isfile(os.path.join(base, "presentation", "pages", p)):
                        problems.append("%s: eksik sayfa gorseli %s" % (where, p))
                if not data.get("slides"):
                    problems.append("%s: slides.json bos" % where)

            bank = os.path.join(base, "games", "bank.json")
            if os.path.isfile(bank):
                with open(bank, encoding="utf-8") as f:
                    b = json.load(f)
                n = sum(len(s.get("questions", [])) for s in b.get("sets", []))
                if n:
                    stats["oyun"] += 1
                missing = 0
                for s in b.get("sets", []):
                    for q in s["questions"]:
                        for name in [q.get("img")] + [a.get("img") for a in q["a"]]:
                            if name and not os.path.isfile(os.path.join(base, "games", "img", name)):
                                missing += 1
                if missing:
                    problems.append("%s: %d oyun gorseli eksik" % (where, missing))

            man = os.path.join(base, "worksheets", "manifest.json")
            if os.path.isfile(man):
                with open(man, encoding="utf-8") as f:
                    items = json.load(f).get("items", [])
                local = [i for i in items if i.get("file")]
                if local:
                    stats["kagit"] += 1
                for i in local:
                    if not os.path.isfile(os.path.join(base, "worksheets", i["file"])):
                        problems.append("%s: eksik dosya %s" % (where, i["file"]))

            sites = os.path.join(base, "sites", "manifest.json")
            if os.path.isfile(sites):
                with open(sites, encoding="utf-8") as f:
                    for it in json.load(f).get("items", []):
                        if it.get("path"):
                            stats["kopya"] += 1
                            if not os.path.isfile(os.path.join(base, "sites", it["path"])):
                                problems.append("%s: eksik kopya %s" % (where, it["path"]))

            if not (u["has"]["presentation"] or u["has"]["games"] or u["has"]["worksheets"]):
                stats["bos"] += 1

    for f in ("app/index.html", "server/enghub.py", "Start-Windows.bat", "start-pardus.sh"):
        if not os.path.isfile(os.path.join(ROOT, f)):
            problems.append("eksik dosya: " + f)

    print("unite: %d   sunumlu: %d   oyunlu: %d   kagitli: %d   cevrimdisi kopya: %d   bos unite: %d"
          % (stats["unite"], stats["sunum"], stats["oyun"], stats["kagit"], stats["kopya"], stats["bos"]))
    if problems:
        print("\n%d sorun:" % len(problems))
        for p in problems[:60]:
            print("  - " + p)
        if len(problems) > 60:
            print("  ... ve %d tane daha" % (len(problems) - 60))
        sys.exit(1)
    print("Her sey yerinde.")


if __name__ == "__main__":
    main()
