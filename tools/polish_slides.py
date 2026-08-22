#!/usr/bin/env python3
"""Bring the grade-5 decks in line with the course book and add practice pages.

  * slide order follows res/book.pdf (its theme table lists the sub-themes in
    teaching order); sections the book does not cover are dropped
  * number cards store the digits instead of an emoji, so 11 no longer shows up
    as the "1234" glyph
  * one compact, varied activity break is inserted after every teaching
    section, built from that section's own words and examples

Run:  python tools/polish_slides.py [--unit 1] [--dry]
"""

import argparse
import glob
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT  # noqa: E402

# Teaching order per theme, taken from the book's contents table. Only grade 5
# needs reordering; the grade-8 decks are generated in teaching order already.
ORDER_BY_GRADE = {"g5": {}}
ORDER = ORDER_BY_GRADE["g5"]
ORDER.update({
    "u1": ["People at School", "Places at School", "A / AN / THE", "School Clubs",
           "Expressing Likes", "Do you like ...?", "School Rules — Verbs", "Imperatives",
           "Obligations — must / mustn't", "Countries", "Where are you from?",
           "National and Religious Days", "Quick Practice"],
    "u2": ["Verbs", "Classroom Rules", "School Subjects", "have got / has got",
           "What time? / When?", "Classroom Objects", "Days of the Week",
           "Numbers 1–20", "Numbers 21–100", "Telling the Time", "a.m. / p.m.",
           "There is / There are", "Is there ...? / Are there ...?", "Quick Practice"],
    "u3": ["Body Parts", "Physical Features", "What do/does ... look like?",
           "Describing People", "Clothes", "Accessories", "Adjectives", "Clothes Verbs",
           "Daily Routines", "Time Expressions", "Simple Present — Positive",
           "Negative & Question", "Question Tags", "Adverbs of Frequency",
           "How often ...?", "Quick Practice"],
    "u4": ["Family Members", "Daily Routines (1)", "Daily Routines (2)",
           "Hobbies and Activities", "Present Continuous — -ing", "Negative & Question",
           "Question Tags", "Simple Present vs Present Continuous", "Quick Practice"],
    "u5": ["Places for Recreation & Attractions", "Verbs", "Adjectives",
           "Parts of a House", "Furniture & Kitchen Utensils", "There is / There are",
           "Possessive 's", "Whose ...?", "Simple Present", "Comparative Adjectives",
           "Quick Practice"],
    "u6": ["Menu Sections", "Food — Vegetables & More", "Food — Sweet & Bakery",
           "Kitchen Utensils", "Adjectives", "Verbs", "Countable / Uncountable",
           "a / an · some · any", "How many? / How much?", "Asking for Permission",
           "Can I ...?", "have got / has got", "Have ... got? / Has ... got?",
           "Quick Practice"],
    "u7": ["Types of Animals", "Animals", "Body Parts of Animals", "Habitats",
           "Adjectives", "Verbs", "Expressing Ability — can / can't", "must / mustn't",
           "Comparative Adjectives", "Superlative Adjectives", "Quick Practice"],
    "u8": ["Planet Earth", "Holidays & Travel", "Holiday Activities", "Verbs",
           "Adjectives", "Simple Future — be going to", "Negative & Question",
           "Quick Practice"],
})

STAR = re.compile(r"\*(.+?)\*")
MAX_CARDS = 12   # vocabulary cards per slide before it is split in two
MAX_TASKS = 2    # practice tasks per slide - more than this and they shrink
BACK = chr(92)


def is_number(item):
    return bool(re.fullmatch(r"\d{1,3}", (item.get("tr") or "").strip()))


def starred_examples(slide):
    out = []
    pools = list(slide.get("examples") or [])
    for col in slide.get("columns") or []:
        pools += col.get("examples") or []
    for e in pools:
        m = STAR.search(e.get("en", ""))
        if m and len(m.group(1)) <= 22:
            out.append((e, m.group(1)))
    return out


def pic_index(slides):
    """english word -> its picture, so examples and tasks can show it"""
    out = {}
    for s in slides:
        if s.get("type") == "vocab":
            for it in s.get("items", []):
                if it.get("img"):
                    out.setdefault(it["en"].lower(), (it["img"], it["tr"]))
    return out


def choose_tasks(candidates, preferred):
    """Pick one task per preferred kind, then fill any remaining slot."""
    picked, used = [], set()
    for kind in preferred:
        hit = next((t for t in candidates if t["kind"] == kind and id(t) not in used), None)
        if hit:
            picked.append(hit)
            used.add(id(hit))
    for task in candidates:
        if len(picked) >= MAX_TASKS:
            break
        if id(task) not in used:
            picked.append(task)
            used.add(id(task))
    return picked[:MAX_TASKS]


def make_exercise(slide, rng, variant=0):
    """One compact, varied activity break built from the preceding section."""
    candidates = []

    if slide.get("type") == "vocab":
        items = [i for i in slide["items"] if i.get("en") and i.get("tr")]
        if len(items) >= 4:
            pairs = rng.sample(items, min(4, len(items)))
            candidates.append({"kind": "match", "q": "Match the words",
                               "pairs": [{"a": p["en"], "b": p["tr"]} for p in pairs]})

        with_pic = [i for i in items if i.get("img")]
        if with_pic:
            target = rng.choice(with_pic)
            others = [i["en"] for i in items if i is not target]
            candidates.append({
                "kind": "picture", "q": "Which word matches the picture?", "img": target["img"],
                "answer": target["en"], "tr": target["tr"],
                "options": [target["en"]] + rng.sample(others, min(3, len(others))),
            })

        if items:
            target = rng.choice(items)
            candidates.append({
                "kind": "flash", "q": "Guess the English word",
                "clue": target["tr"], "answer": target["en"],
            })

        if len(items) >= 2:
            target = rng.choice(items)
            truth = variant % 2 == 0
            shown = target["tr"] if truth else rng.choice([i["tr"] for i in items if i is not target])
            candidates.append({
                "kind": "truefalse", "q": "True or false?",
                "statement": '"%s" means "%s".' % (target["en"], shown),
                "answer": truth,
                "explain": '%s = %s' % (target["en"], target["tr"]),
            })

        if len(items) >= 4:
            target = rng.choice(items)
            others = [i["en"] for i in items if i is not target]
            candidates.append({
                "kind": "choose", "q": 'Which word means "%s"?' % target["tr"],
                "answer": target["en"],
                "options": [target["en"]] + rng.sample(others, min(3, len(others))),
            })

        patterns = [
            ("match", "picture"), ("truefalse", "choose"),
            ("flash", "match"), ("picture", "truefalse"),
        ]
    else:
        found = starred_examples(slide)
        words = list(dict.fromkeys(w for _, w in found))
        for e, word in found[:3]:
            plain = STAR.sub(r"\1", e["en"])
            candidates.append({
                "kind": "fill", "text": plain.replace(word, "___", 1),
                "answer": word, "options": [word] + [x for x in words if x != word][:3],
                "tr": e.get("tr", ""),
            })

        long_ex = [e for e, _ in found if 3 <= len(STAR.sub(r"\1", e["en"]).split()) <= 8]
        if long_ex:
            e = long_ex[-1]
            candidates.append({
                "kind": "order", "q": "Put the sentence in order",
                "answer": STAR.sub(r"\1", e["en"]), "tr": e.get("tr", ""),
            })

        if found:
            e, word = found[variant % len(found)]
            plain = STAR.sub(r"\1", e["en"])
            candidates.append({
                "kind": "flash", "q": "Complete the sentence aloud",
                "clue": plain.replace(word, "___", 1), "answer": word,
                "tr": e.get("tr", ""),
            })
            alternatives = [w for w in words if w != word]
            truth = not alternatives or variant % 2 == 0
            shown = plain if truth else plain.replace(word, alternatives[0], 1)
            candidates.append({
                "kind": "truefalse", "q": "Does the sentence match the meaning?",
                "statement": shown + (" — " + e.get("tr", "") if e.get("tr") else ""),
                "answer": truth, "explain": "Correct: " + plain,
            })

        # Dialogue sections do not use starred grammar examples. Turn a real
        # exchange from the section into a short whole-class role-play instead.
        if not found and slide.get("type") == "dialogue":
            exchange = next((d for d in slide.get("dialogues", [])
                             if len(d.get("lines", [])) >= 2), None)
            if exchange:
                first, second = exchange["lines"][:2]
                candidates.append({
                    "kind": "flash", "q": "Role-play: what comes next?",
                    "clue": "%s: %s" % (first.get("who", "A"), first.get("text", "")),
                    "answer": "%s: %s" % (second.get("who", "B"), second.get("text", "")),
                })

        if not found and slide.get("type") == "scene":
            bubbles = slide.get("bubbles", [])
            if len(bubbles) >= 2:
                candidates.append({
                    "kind": "flash", "q": "Role-play: what comes next?",
                    "clue": bubbles[0].get("text", ""),
                    "answer": bubbles[1].get("text", ""),
                })

        patterns = [
            ("fill", "order"), ("truefalse", "fill"), ("flash", "order"),
        ]

    tasks = choose_tasks(candidates, patterns[variant % len(patterns)]) if candidates else []
    if not tasks:
        return []
    return [{
        "type": "exercise",
        "title": "Activity Break",
        "titleTr": "Use what you just learned · " + slide.get("title", ""),
        "tasks": tasks,
    }]


def merge_parts(body):
    """Undo an earlier split so the script can be run again safely."""
    out = []
    for s in body:
        prev = out[-1] if out else None
        if (prev and s.get("part") and s["type"] == "vocab"
                and prev["type"] == "vocab"
                and s.get("title") == prev.get("title")):
            prev["items"] += s["items"]
            continue
        if s.get("part") and s["type"] == "vocab":
            s = dict(s)
            s.pop("part", None)
        out.append(s)
    return out


def split_cards(slide):
    """Long word lists become two (or three) slides of equal size."""
    items = slide.get("items") or []
    if len(items) <= MAX_CARDS:
        return [slide]
    parts = -(-len(items) // MAX_CARDS)
    size = -(-len(items) // parts)
    out = []
    for n in range(parts):
        chunk = dict(slide)
        chunk["items"] = items[n * size:(n + 1) * size]
        chunk["part"] = [n + 1, parts]
        out.append(chunk)
    return out


def polish(path, dry):
    parts = os.path.normpath(path).split(os.sep)
    grade, unit = parts[-4], parts[-3]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rng = random.Random(unit)
    slides = data["slides"]

    head = [s for s in slides if s["type"] == "title"]
    tail = [s for s in slides if s["type"] in ("pages", "end")]
    body = [s for s in slides if s["type"] not in ("title", "pages", "end")]

    body = [s for s in body if s["type"] != "exercise"]  # regenerate them
    order = ORDER_BY_GRADE.get(grade, {}).get(unit)
    dropped = []
    if order:
        rank = {t: n for n, t in enumerate(order)}
        keep, drop = [], []
        for s in body:
            (keep if s.get("title") in rank else drop).append(s)
        keep.sort(key=lambda s: rank[s["title"]])
        dropped = [s.get("title") for s in drop]
        body = keep

    body = merge_parts(body)
    pics = pic_index(body)
    thin = []
    out = []
    activity_no = 0
    for s in body:
        # a picture next to an example makes the rule concrete
        pools = list(s.get("examples") or [])
        for col in s.get("columns") or []:
            pools += col.get("examples") or []
        for e in pools:
            plain = STAR.sub(BACK+"1", e.get("en", "")).lower()
            hit = max((w for w in pics if re.search(BACK+"b"+re.escape(w)+BACK+"b", plain)),
                      key=len, default=None)
            if hit:
                e["img"] = pics[hit][0]
        if s["type"] in ("grammar", "compare") and len(pools) < 3:
            thin.append(s.get("title"))
        # digits render as keycaps instead of the unreadable numbers emoji
        if s["type"] == "vocab":
            for it in s["items"]:
                if is_number(it):
                    it["num"] = it["tr"]
                    it.pop("emoji", None)
        out.extend(split_cards(s) if s["type"] == "vocab" else [s])
        if s["type"] not in ("practice", "exercise"):
            activities = make_exercise(s, rng, activity_no)
            out.extend(activities)
            if activities:
                activity_no += 1

    data["slides"] = head + out + tail
    if not dry:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)

    print("  %s  %2d slayt -> %2d  (cikarilan: %s)"
          % (unit, len(slides), len(data["slides"]), ", ".join(dropped) or "-"))
    if thin:
        print("     az ornekli (<3): %s" % ", ".join(thin))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", type=int, default=5)
    ap.add_argument("--unit", type=int)
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    pat = os.path.join(CONTENT, "g%d" % args.grade,
                       "u%d" % args.unit if args.unit else "u*",
                       "presentation", "slides.json")
    for path in sorted(glob.glob(pat)):
        polish(path, args.dry)


if __name__ == "__main__":
    main()
