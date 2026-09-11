#!/usr/bin/env python3
"""Harvest the source's game content into offline question banks.

The games on the source site are hosted players (etkinlik.app) whose questions
come from a public JSON endpoint. We keep the *questions* — the pedagogical
content for that unit — and play them inside ENG HUB's own offline games.

Run:  python tools/fetch_games.py [--grade 5] [--unit 1] [--no-images] [--force]

Writes content/<grade>/<unit>/games/bank.json (+ img/) with:
  sets[]    one entry per source activity: name, type, questions[]
  words[]   en/tr pairs mined from the questions, for matching / word games
  online[]  activities that can only run with internet (wordwall etc.)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, DATA, ensure, http_get, log, progress  # noqa: E402

ETK = "https://etkinlik.app"
QGROUP = ETK + "/api/unity/question-groups/code/%s"

# the API sometimes prefixes an already-absolute URL with its own storage root
DOUBLE = re.compile(r"^https?://[^/]+/storage/(?=https?://)")


def clean_url(u):
    if not u:
        return None
    u = DOUBLE.sub("", u.strip())
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("http"):
        return u
    return ETK + "/storage/" + u.lstrip("/")


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip())


# only real quote pairs - a bare ' is an apostrophe ("What's the meaning of ...")
QUOTED = re.compile(r'["“”]([^"“”]{2,45})["“”]|‘([^‘’]{2,45})’')
TO_ENGLISH = re.compile(r"in english|ingilizce", re.I)
TURKISH_ONLY = re.compile(r"[çğıöşüÇĞİÖŞÜ]")


def mine_words(question, correct):
    """'What does "canteen" mean?' + 'kantin'  ->  ('canteen', 'kantin').

    Works for every phrasing the source uses (mean / meaning of / ne demek /
    say ... in English) because it keys off the quoted term, not the wording.
    """
    q, c = norm(question), norm(correct)
    if not q or not c or len(c) > 45:
        return None
    m = QUOTED.search(q)
    if not m:
        return None
    term = norm(m.group(1) or m.group(2))
    if not term or len(term) > 45 or term.lower() == c.lower():
        return None
    # direction: "say X in English" asks for the English side, everything else
    # gives the English word and asks for its meaning
    if TO_ENGLISH.search(q) or (TURKISH_ONLY.search(term) and not TURKISH_ONLY.search(c)):
        return (c, term)
    return (term, c)


def fetch_set(code):
    return json.loads(http_get(QGROUP % code, timeout=60, retries=2))


def grab_image(url, img_dir, seen):
    """Download once per URL, return the local file name."""
    url = clean_url(url)
    if not url or not url.startswith("http"):
        return None
    key = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    if key in seen:
        return seen[key]
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        ext = ".png"
    name = key + ext
    path = os.path.join(img_dir, name)
    if not os.path.exists(path):
        try:
            raw, _ = http_get(url, timeout=60, retries=2, binary=True)
        except Exception:  # noqa: BLE001 - a missing picture must not stop the run
            seen[key] = None
            return None
        ensure(img_dir)
        with open(path, "wb") as f:
            f.write(raw)
    seen[key] = name
    return name


def build_unit(gid, uid, src, want_images, force):
    authored_path = os.path.join(CONTENT, gid, uid, "games", "bank.json")
    if gid == "g6" and os.path.isfile(authored_path):
        with open(authored_path, encoding="utf-8") as f:
            authored = json.load(f)
        if authored.get("authored") and authored.get("curriculum") == "meb-english-6-2026":
            return sum(len(s["questions"]) for s in authored["sets"]), len(authored["words"])
    games = src.get("offlineGames") or []
    online = src.get("onlineGames") or []
    base = os.path.join(CONTENT, gid, uid, "games")
    img_dir = os.path.join(base, "img")
    ensure(base)

    cache_path = os.path.join(base, "_raw.json")
    raw_cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as f:
                raw_cache = json.load(f)
        except ValueError:
            raw_cache = {}

    seen_img, sets, words = {}, [], {}

    for it in games:
        code = it["code"]
        try:
            data = fetch_set(code) if force else (raw_cache.get(code) or fetch_set(code))
            raw_cache[code] = data
        except Exception as exc:  # noqa: BLE001
            log("games.log", "HATA %s/%s %s -> %s" % (gid, uid, code, exc))
            data = raw_cache.get(code)
            if not data:
                continue

        questions = []
        for q in data.get("questions", []):
            answers = []
            for a in q.get("answers", []):
                answers.append({
                    "t": norm(a.get("answer_text")),
                    "c": bool(a.get("is_correct")),
                    "img": grab_image(a.get("image_path"), img_dir, seen_img) if want_images else None,
                })
            if not answers:
                continue
            correct = next((a["t"] for a in answers if a["c"]), "")
            qtext = norm(q.get("question_text"))
            if not correct and not qtext:
                continue
            questions.append({
                "q": qtext,
                "img": grab_image(q.get("image_path"), img_dir, seen_img) if want_images else None,
                "a": answers,
            })
            pair = mine_words(qtext, correct)
            if pair and pair[0].lower() not in words:
                words[pair[0].lower()] = pair

        if questions:
            sets.append({
                "code": code,
                "name": norm(it.get("title")) or norm(data.get("name")) or "Etkinlik",
                "by": it.get("by", ""),
                "type": data.get("question_type") or "multiple_choice",
                "questions": questions,
            })

    bank = {
        "sets": sets,
        "words": [{"en": en, "tr": tr} for en, tr in words.values()],
        "online": [{"title": o["title"], "link": o["link"], "by": o.get("by", "")} for o in online],
    }
    with open(os.path.join(base, "bank.json"), "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(raw_cache, f, ensure_ascii=False)

    return sum(len(s["questions"]) for s in sets), len(bank["words"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", type=int)
    ap.add_argument("--unit", type=int)
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--force", action="store_true", help="kayitli JSON yerine yeniden indir")
    args = ap.parse_args()

    with open(os.path.join(DATA, "source-index.json"), encoding="utf-8") as f:
        src = json.load(f)

    keys = sorted(src, key=lambda k: (int(k[1]), 0 if k.endswith("/revision") else int(k.split("/")[1][1:])))
    if args.grade:
        keys = [k for k in keys if k.startswith("g%d/" % args.grade)]
    if args.unit is not None:
        keys = [k for k in keys if k.endswith("/u%d" % args.unit) or (args.unit == 0 and k.endswith("/revision"))]

    tq = tw = 0
    for i, key in enumerate(keys, 1):
        gid, uid = key.split("/")
        progress(i - 1, len(keys), key)
        q, w = build_unit(gid, uid, src[key], not args.no_images, args.force)
        tq += q
        tw += w
    progress(len(keys), len(keys), "bitti")
    print("toplam soru: %d   kelime cifti: %d" % (tq, tw))

    import subprocess
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch_catalog.py")],
                   check=False)


if __name__ == "__main__":
    main()
