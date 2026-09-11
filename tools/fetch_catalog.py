#!/usr/bin/env python3
"""Build app/data/catalog.json from the eltarena source + what is on disk.

Run:  python tools/fetch_catalog.py [--refresh]
      --refresh  re-download the source catalog instead of using tools/cache.

Re-runnable at any time: it only describes what exists, it never downloads
worksheets or game data (those have their own scripts).
"""

import argparse
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (  # noqa: E402
    CONTENT, DATA, GRADES, OFFLINE_GAME_HOST, THEMES, UNITS_PER_GRADE,
    ensure, load_grades, source_units,
)


def host_of(link):
    try:
        return urllib.parse.urlparse(link).hostname or ""
    except ValueError:
        return ""


def classify(resources):
    """Split a unit's source resources into the buckets the UI cares about."""
    worksheets, offline_games, online_games, extras, books = [], [], [], [], []
    for r in resources or []:
        # book presentations are opened through their "Önizle" viewer
        link = r.get("fileUrl") or r.get("link") or r.get("previewLink") or ""
        rtype = r.get("type")
        item = {
            "title": (r.get("title") or "").strip(),
            "desc": (r.get("description") or "").strip(),
            "by": (r.get("createdBy") or "").strip(),
            "link": link,
            "type": rtype,
        }
        from resource_kind import online_game
        if rtype in ("worksheet", "file") and online_game(item):
            online_games.append(item)
        elif rtype in ("worksheet", "file"):
            worksheets.append(item)
        elif rtype == "game":
            if host_of(link) == OFFLINE_GAME_HOST:
                code = urllib.parse.parse_qs(urllib.parse.urlparse(link).query).get("code", [None])[0]
                if code:
                    item["code"] = code
                    offline_games.append(item)
                    continue
            if link.startswith("http"):
                online_games.append(item)
        elif rtype == "book-presentation":
            books.append(item)
            if link.startswith("http"):
                extras.append(item)
        elif rtype in ("quiz", "summary", "flashcards", "video"):
            if link.startswith("http"):
                extras.append(item)
    return worksheets, offline_games, online_games, extras, books


def unit_state(gid, uid, src_ws, src_games):
    """What is actually present on disk for this unit right now."""
    base = os.path.join(CONTENT, gid, uid)

    slides = os.path.join(base, "presentation", "slides.json")
    has_pres = os.path.isfile(slides)

    bank = os.path.join(base, "games", "bank.json")
    n_bank = 0
    if os.path.isfile(bank):
        try:
            with open(bank, encoding="utf-8") as f:
                data = json.load(f)
            n_bank = sum(len(s.get("questions", [])) for s in data.get("sets", []))
        except (OSError, ValueError):
            n_bank = 0

    man = os.path.join(base, "worksheets", "manifest.json")
    n_ws = n_ws_links = 0
    if os.path.isfile(man):
        try:
            with open(man, encoding="utf-8") as f:
                items = json.load(f).get("items", [])
                n_ws = len([i for i in items if i.get("file")])
                n_ws_links = len(items)
        except (OSError, ValueError):
            n_ws = 0

    # offline copies of the source's static activities
    sites = os.path.join(base, "sites", "manifest.json")
    n_site_games = n_site_pres = 0
    if os.path.isfile(sites):
        try:
            with open(sites, encoding="utf-8") as f:
                for it in json.load(f).get("items", []):
                    if not it.get("path"):
                        continue
                    if it.get("kind") == "presentation":
                        n_site_pres += 1
                    else:
                        n_site_games += 1
        except (OSError, ValueError):
            pass

    return {
        "has": {
            "presentation": has_pres or n_site_pres > 0,
            "games": True,
            "worksheets": n_ws_links > 0 or bool(src_ws),
        },
        "counts": {
            "games": n_bank,
            "worksheets": n_ws,
            "worksheetLinks": n_ws_links - n_ws,
            "offlineSites": n_site_games + n_site_pres,
            "sourceWorksheets": len(src_ws),
            "sourceGames": len(src_games),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="re-download the source catalog")
    args = ap.parse_args()

    grades_json = load_grades(refresh=args.refresh)
    src = source_units(grades_json)

    catalog = {"generated": __import__("time").strftime("%Y-%m-%d %H:%M"), "grades": []}
    per_unit_source = {}

    for no in GRADES:
        gid = "g%d" % no
        grade = {"id": gid, "no": no, "title": "%d. Sınıf" % no, "units": []}
        if no in (5, 6) and "revision" in src.get(no, {}):
            su = src[no]["revision"]
            uid = "revision"
            ws, off, onl, extras, books = classify(su.get("resources") if su else [])
            state = unit_state(gid, uid, ws, off)
            grade["units"].append({
                "id": uid, "no": 0,
                "label": "Revizyon",
                "title": "Revision", "titleTr": "Genel Tekrar", "emoji": "🔄",
                "sourceUnitId": su.get("id") if su else None,
                "onlineGames": len(onl),
                "books": len(books),
                **state,
            })
            per_unit_source[(gid, uid)] = {
                "worksheets": ws, "offlineGames": off,
                "onlineGames": onl, "extras": extras, "books": books,
            }
        for un in range(1, (8 if no in (5, 6) else UNITS_PER_GRADE) + 1):
            uid = "u%d" % un
            theme = THEMES.get(no, {}).get(un, ("", "", "📘"))
            su = src.get(no, {}).get(un)
            ws, off, onl, extras, books = classify(su.get("resources") if su else [])
            state = unit_state(gid, uid, ws, off)
            grade["units"].append({
                "id": uid, "no": un,
                "label": "Tema" if no in (5, 6) else "Ünite",
                "title": theme[0], "titleTr": theme[1], "emoji": theme[2],
                "sourceUnitId": su.get("id") if su else None,
                "onlineGames": len(onl),
                "books": len(books),
                **state,
            })
            per_unit_source[(gid, uid)] = {
                "worksheets": ws, "offlineGames": off,
                "onlineGames": onl, "extras": extras, "books": books,
            }
        catalog["grades"].append(grade)

    ensure(DATA)
    with open(os.path.join(DATA, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)

    # the raw per-unit resource lists feed the downloader scripts
    ensure(os.path.join(DATA))
    flat = {"%s/%s" % k: v for k, v in per_unit_source.items()}
    with open(os.path.join(DATA, "source-index.json"), "w", encoding="utf-8") as f:
        json.dump(flat, f, ensure_ascii=False)

    # book presentations live in their own file: the UI links out to them
    books = {"%s/%s" % k: v["books"] for k, v in per_unit_source.items() if v["books"]}
    with open(os.path.join(DATA, "books.json"), "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=1)

    tot_ws = sum(len(v["worksheets"]) for v in per_unit_source.values())
    tot_off = sum(len(v["offlineGames"]) for v in per_unit_source.values())
    tot_on = sum(len(v["onlineGames"]) for v in per_unit_source.values())
    print("catalog.json yazildi.")
    print("  siniflar        : %d" % len(catalog["grades"]))
    print("  calisma kagidi  : %d" % tot_ws)
    print("  cevrimdisi oyun : %d (etkinlik.app)" % tot_off)
    print("  cevrimici oyun  : %d" % tot_on)


if __name__ == "__main__":
    main()
