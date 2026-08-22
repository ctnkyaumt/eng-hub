#!/usr/bin/env python3
"""Validate the generated teaching decks and their classroom interactions.

This is intentionally stricter than verify_content.py: it checks the lesson
contract introduced by polish_slides.py (large word pages, complete visuals,
three unit missions) and rejects known language regressions.

Run:  python tools/verify_lessons.py
"""

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, ROOT  # noqa: E402


MAX_CARDS = 8
MISSION_KINDS = ["dragmatch", "listenpicture", "dragorder"]
TURKISH = re.compile(r"[çğıöşüÇĞİÖŞÜ]")

# These exact strings were found in the full sentence audit. Keeping the list
# here prevents a future regeneration from quietly bringing them back.
LANGUAGE_REGRESSIONS = [
    "at weekend",
    "at nights",
    "small and round face",
    "watches series in her free time",
    "swim in a rough sea",
    "double Art classes",
    "go Mert go",
    "You don't joke.",
    "Birds must go to warm habitats",
    "I often read a book.",
    "They never watch a fashion show.",
    "I am not doing homework.",
]


def where(path):
    return os.path.relpath(path, CONTENT).replace("\\", "/").replace("/presentation/slides.json", "")


def has_visual(item):
    return bool(item.get("img") or item.get("emoji") or item.get("num") is not None)


def image_path(deck_path, name):
    if name.startswith("/app/"):
        return os.path.join(ROOT, name.lstrip("/").replace("/", os.sep))
    return os.path.join(os.path.dirname(deck_path), "img", name)


def app_asset_path(name):
    return os.path.join(ROOT, name.lstrip("/").replace("/", os.sep))


def word_audio_path(word):
    slug = re.sub(r"[^a-z0-9]+", "-", (word or "").lower()).strip("-")
    return app_asset_path("/app/audio/words/%s.wav" % slug) if slug else ""


def visual_signature(item):
    if item.get("img"):
        return "img", item["img"]
    if item.get("emoji"):
        return "emoji", item["emoji"]
    if item.get("num") is not None:
        return "num", str(item["num"])
    return None


def language_strings(slides):
    """Yield every English sentence field, including generated activities."""
    for slide in slides:
        for example in slide.get("examples") or []:
            yield "example", example.get("en", "")
        for column in slide.get("columns") or []:
            for example in column.get("examples") or []:
                yield "example", example.get("en", "")
        for dialogue in slide.get("dialogues") or []:
            for line in dialogue.get("lines") or []:
                yield "dialogue", line.get("text", "")
        for bubble in slide.get("bubbles") or []:
            yield "scene", bubble.get("text", "")
        for task in slide.get("tasks") or []:
            for key in ("q", "text", "statement", "clue", "answer", "explain"):
                if isinstance(task.get(key), str):
                    yield "activity", task[key]
        task = slide.get("task") or {}
        if isinstance(task.get("q"), str):
            yield "mission", task["q"]
        for sentence in task.get("sentences") or []:
            yield "mission", sentence.get("answer", "")


def main():
    problems = []
    stats = {"decks": 0, "slides": 0, "words": 0, "pictures": 0,
             "pictograms": 0, "missions": 0, "mission_audio": 0,
             "word_audio": 0, "example_visuals": 0, "sentences": 0}
    checked_word_audio = set()

    paths = sorted(glob.glob(os.path.join(CONTENT, "g*", "u*", "presentation", "slides.json")))
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        slides = data.get("slides") or []
        unit = where(path)
        stats["decks"] += 1
        stats["slides"] += len(slides)

        for slide in slides:
            if slide.get("type") != "vocab":
                continue
            items = slide.get("items") or []
            if len(items) > MAX_CARDS:
                problems.append("%s: %s has %d word cards (max %d)" %
                                (unit, slide.get("title"), len(items), MAX_CARDS))
            same_visual = {}
            for item in items:
                stats["words"] += 1
                signature = visual_signature(item)
                if signature:
                    same_visual.setdefault(signature, []).append(item.get("en"))
                if not has_visual(item):
                    problems.append("%s: no visual for %r" % (unit, item.get("en")))
                elif item.get("emoji") == "🧩":
                    problems.append("%s: generic visual for %r" % (unit, item.get("en")))
                elif item.get("img"):
                    stats["pictures"] += 1
                    if not os.path.isfile(image_path(path, item["img"])):
                        problems.append("%s: missing picture %s" % (unit, item["img"]))
                else:
                    stats["pictograms"] += 1

                audio = word_audio_path(item.get("en"))
                if audio and audio not in checked_word_audio:
                    checked_word_audio.add(audio)
                    if not os.path.isfile(audio) or os.path.getsize(audio) <= 44:
                        problems.append("%s: missing word audio for %r" % (unit, item.get("en")))
                    else:
                        stats["word_audio"] += 1
            for signature, words in same_visual.items():
                distinct = sorted(set(words))
                if len(distinct) > 1:
                    problems.append("%s: %s reuses %r for %r" %
                                    (unit, slide.get("title"), signature, distinct))

        for slide in slides:
            pools = list(slide.get("examples") or [])
            for column in slide.get("columns") or []:
                pools += column.get("examples") or []
            for example in pools:
                if not has_visual(example):
                    problems.append("%s: no visual for example %r" %
                                    (unit, example.get("en")))
                    continue
                stats["example_visuals"] += 1
                if example.get("img") and not os.path.isfile(image_path(path, example["img"])):
                    problems.append("%s: missing example picture %s" %
                                    (unit, example["img"]))

        missions = [slide for slide in slides if slide.get("type") == "mission"]
        kinds = [(slide.get("task") or {}).get("kind") for slide in missions]
        if kinds != MISSION_KINDS:
            problems.append("%s: missions are %r, expected %r" % (unit, kinds, MISSION_KINDS))
        stats["missions"] += len(missions)
        for slide in missions[:2]:
            task = slide.get("task") or {}
            items = task.get("items") or []
            if len(items) != 4 or any(not has_visual(item) for item in items):
                problems.append("%s: %s needs four visual choices" % (unit, slide.get("title")))
            if task.get("kind") == "listenpicture":
                for item in items:
                    audio = item.get("audio")
                    if not audio:
                        problems.append("%s: no offline audio for %r" % (unit, item.get("en")))
                    elif not os.path.isfile(app_asset_path(audio)):
                        problems.append("%s: missing offline audio %s" % (unit, audio))
                    else:
                        stats["mission_audio"] += 1
        if len(missions) == 3:
            sentences = (missions[2].get("task") or {}).get("sentences") or []
            if not sentences:
                problems.append("%s: sentence mission is empty" % unit)
            for item in sentences:
                count = len((item.get("answer") or "").split())
                if not 4 <= count <= 11:
                    problems.append("%s: sentence mission has %d words: %r" %
                                    (unit, count, item.get("answer")))

        for kind, text in language_strings(slides):
            if not text:
                continue
            stats["sentences"] += 1
            for bad in LANGUAGE_REGRESSIONS:
                if bad in text.replace("*", ""):
                    problems.append("%s: language regression in %s: %r" % (unit, kind, text))
            if kind == "dialogue" and TURKISH.search(text.replace("Türkiye", "")):
                problems.append("%s: Turkish translation stored as dialogue text: %r" % (unit, text))

    print("decks: {decks}   slides: {slides}   words: {words}   real pictures: {pictures}   "
          "pictograms/numbers: {pictograms}   missions: {missions}   offline audio refs: {audio}   "
          "language fields checked: {sentences}"
          .format(audio=stats["mission_audio"], **stats))
    print("unique word audio: {word_audio}   examples with visuals: {example_visuals}"
          .format(**stats))
    if problems:
        print("\n%d lesson problems:" % len(problems))
        for problem in problems[:80]:
            print("  - " + problem)
        if len(problems) > 80:
            print("  ... and %d more" % (len(problems) - 80))
        return 1
    print("Every word and example has a visual, vocabulary audio is complete, duplicate card visuals are gone, "
          "and the language checks pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
