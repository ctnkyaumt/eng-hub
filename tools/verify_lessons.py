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

with open(os.path.join(ROOT, 'app/img/commons-teaching-sources.json'), encoding='utf-8') as source_file:
    COMMONS_IMAGES = {item['img'] for item in json.load(source_file).values()}


MAX_CARDS = 4
MISSION_KINDS = ["dragmatch", "listenpicture", "dragorder"]
TURKISH = re.compile(r"[çğıöşüÇĞİÖŞÜ]")
STAR = re.compile(r"\*(.+?)\*")
HOURS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12,
}

REQUIRED_VISUALS = {
    ("g5/u3", "Adjectives", "long"): "/app/img/vocab/adjective-long.svg",
    ("g5/u3", "Adjectives", "short"): "/app/img/vocab/adjective-short.svg",
    ("g5/u3", "Adjectives", "new"): "/app/img/vocab/adjective-new.svg",
    ("g5/u7", "Animals", "seal"): "/app/img/vocab/animal-seal.svg",
}

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
    return bool(item.get("img") or item.get("emoji") or item.get("num") is not None
                or item.get("time"))


def image_path(deck_path, name):
    if name.startswith("/app/"):
        return os.path.join(ROOT, name.lstrip("/").replace("/", os.sep))
    return os.path.join(os.path.dirname(deck_path), "img", name)


def valid_image(deck_path, name):
    if name in COMMONS_IMAGES:
        return True
    if name.startswith("https://"):
        return bool(re.fullmatch(r"https://static\.arasaac\.org/pictograms/(\d+)/\1_500\.png", name))
    return os.path.isfile(image_path(deck_path, name))


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
    if item.get("time"):
        return "time", item["time"]
    return None


def expected_time(text):
    plain = STAR.sub(r"\1", text or "").lower()
    explicit = re.search(r"(?<!\d)([01]?\d|2[0-3]):([0-5]\d)(?!\d)", plain)
    if explicit:
        return "%02d:%s" % (int(explicit.group(1)) % 12 or 12, explicit.group(2))
    hour_words = "|".join(HOURS)
    for phrase, minute, offset in (("half past", 30, 0), ("quarter past", 15, 0),
                                   ("quarter to", 45, -1)):
        hit = re.search(r"\b" + phrase + r" (" + hour_words + r")\b", plain)
        if hit:
            hour = ((HOURS[hit.group(1)] + offset - 1) % 12) + 1
            return "%02d:%02d" % (hour, minute)
    hit = re.search(r"\b(" + hour_words + r") o'clock\b", plain)
    return "%02d:00" % HOURS[hit.group(1)] if hit else None


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
             "word_audio": 0, "example_visuals": 0, "sentences": 0,
             "clocks": 0, "bilingual_highlights": 0}
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
                if not item.get('img') and item.get('num') is None:
                    problems.append("%s: missing vocabulary picture for %r" % (unit, item.get('en')))
                signature = visual_signature(item)
                if signature:
                    same_visual.setdefault(signature, []).append(item.get("en"))
                if not has_visual(item):
                    problems.append("%s: no visual for %r" % (unit, item.get("en")))
                elif item.get("emoji") == "🧩":
                    problems.append("%s: generic visual for %r" % (unit, item.get("en")))
                elif item.get("img"):
                    stats["pictures"] += 1
                    if not valid_image(path, item["img"]):
                        problems.append("%s: missing picture %s" % (unit, item["img"]))
                else:
                    stats["pictograms"] += 1

                required = REQUIRED_VISUALS.get((unit, slide.get("title"),
                                                 (item.get("en") or "").lower()))
                if required and item.get("img") != required:
                    problems.append("%s: %r must use reviewed visual %s" %
                                    (unit, item.get("en"), required))

                audio = word_audio_path(item.get("en"))
                if audio and audio not in checked_word_audio:
                    checked_word_audio.add(audio)
                    if not os.path.isfile(audio) or os.path.getsize(audio) <= 44:
                        problems.append("%s: missing word audio for %r" % (unit, item.get("en")))
                    else:
                        stats["word_audio"] += 1
            for signature, words in same_visual.items():
                distinct = sorted(set(words))
                # Related words may intentionally share an attributed concept
                # illustration. Picture quizzes exclude identical image choices.
                if len(distinct) > 1 and not any(i.get("imageConcept") for i in items if i.get("en") in distinct):
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
                if example.get("img") and not valid_image(path, example["img"]):
                    problems.append("%s: missing example picture %s" %
                                    (unit, example["img"]))
                clock = expected_time(example.get("en"))
                if clock:
                    if example.get("time") != clock:
                        problems.append("%s: %r needs clock %s, found %r" %
                                        (unit, example.get("en"), clock, example.get("time")))
                    else:
                        stats["clocks"] += 1
                if STAR.search(example.get("en") or ""):
                    marks = example.get("trEm") or []
                    if not marks:
                        problems.append("%s: no Turkish highlight for %r" %
                                        (unit, example.get("en")))
                    elif any(str(mark).lower() not in (example.get("tr") or "").lower()
                             for mark in marks):
                        problems.append("%s: Turkish highlight is not in translation for %r" %
                                        (unit, example.get("en")))
                    else:
                        stats["bilingual_highlights"] += 1

        missions = [slide for slide in slides if slide.get("type") == "mission"]
        kinds = [(slide.get("task") or {}).get("kind") for slide in missions]
        if kinds[:3] != MISSION_KINDS or len(kinds) < 4:
            problems.append("%s: missions are %r, expected %r" % (unit, kinds, MISSION_KINDS))
        stats["missions"] += len(missions)
        for slide in slides:
            if slide.get("type") == "exercise" and len(slide.get("tasks", [])) != 1:
                problems.append("%s: activity must have one large task per page" % unit)
            if slide.get("type") == "grammar":
                if len(slide.get("chips", [])) > 1 or len(slide.get("examples", [])) > 1:
                    problems.append("%s: grammar page mixes patterns/examples" % unit)
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
        if len(missions) >= 3:
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
          "text/numbers: {pictograms}   missions: {missions}   offline audio refs: {audio}   "
          "language fields checked: {sentences}"
          .format(audio=stats["mission_audio"], **stats))
    print("unique word audio: {word_audio}   examples with visuals: {example_visuals}   "
          "accurate clocks: {clocks}   bilingual highlights: {bilingual_highlights}"
          .format(**stats))
    if problems:
        print("\n%d lesson problems:" % len(problems))
        for problem in problems[:80]:
            print("  - " + problem)
        if len(problems) > 80:
            print("  ... and %d more" % (len(problems) - 80))
        return 1
    print("Media references, clocks, bilingual highlights, vocabulary audio and language checks pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
