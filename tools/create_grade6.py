"""Write authored Grade 6 content. No app build and no network access.

Run with the bundled Python (reportlab/pypdf), optionally --books <read-only folder>.
Only g6 content and g6 catalog entries are written; other grades are untouched.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import random
import re

from grade6_content import UNITS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content/g6"
AUTHOR = "ENG HUB - özgün içerik"
EDITION = "meb-english-6-2026"
STAR = re.compile(r"\*(.+?)\*")
CORRECTIONS = {
    "revision": {2: "The tiny house has two bedrooms."},
    "u1": {1: "Eren is the group leader; Mina is a volunteer.", 3: "The team never leaves rubbish behind."},
    "u2": {2: "Ada is reading aloud; Tom is marking important words.", 3: "They are only using the first fifty cards."},
    "u3": {1: "Leo's trainers are bigger than Maya's.", 3: "Noor makes a list before the display."},
    "u4": {2: "The entrance is next to a bakery."},
    "u5": {1: "The square was crowded; the library garden was quiet."},
    "u6": {2: "They used English and practised a few Swedish words."},
    "u7": {2: "They did not touch sharp objects; they told their teacher.", 3: "Visitors must not leave rubbish."},
    "u8": {2: "It is a prediction, not a certain fact.", 3: "They are going to use old boxes."},
}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def plain(text):
    return text.replace("*", "")


def slug(text):
    return re.sub("[^a-z0-9]+", "-", text.lower()).strip("-")


def existing_pictures():
    """Reuse only existing local teaching assets, preserving their credits."""
    pictures = {}
    for grade in ("g5", "g8"):
        for path in sorted((ROOT / "content" / grade).glob("u*/presentation/slides.json")):
            deck = json.loads(path.read_text(encoding="utf-8"))
            for slide in deck["slides"]:
                if slide.get("type") != "vocab":
                    continue
                for item in slide.get("items", []):
                    name = item.get("img", "")
                    if not name or name.startswith("http"):
                        continue
                    resolved = ROOT / name.lstrip("/") if name.startswith("/") else path.parent / "img" / name
                    if not resolved.is_file():
                        continue
                    pic = {k: v for k, v in item.items() if k.startswith("image")}
                    pic.update(img="/" + resolved.relative_to(ROOT).as_posix(), imageFit="contain")
                    for key in item["en"].lower().split(" / "):
                        pictures.setdefault(key, pic)
    cached = OUT / "shared/image-sources.json"
    if cached.exists():
        for name, item in json.loads(cached.read_text(encoding="utf-8"))["images"].items():
            pictures.setdefault(name, dict(img="/content/g6/shared/img/" + item["file"],
                imageSource="Sergio Palao / ARASAAC (Government of Aragon), CC BY-NC-SA",
                imageCredit=item["source"], imageFit="contain"))
    # Homonyms: these existing pictures depict another sense of the word.
    for name in ("rock", "fish", "cook", "assistant", "heat", "local", "polite", "support"):
        pictures.pop(name, None)
    pictures["flag"] = dict(img="/app/img/flags/tr.svg", imageConcept="Turkish flag", imageSource="Existing ENG HUB flag")
    pictures["rock"] = dict(img="/app/img/concepts/types-of-music.svg", imageConcept="music genres", imageSource="ENG HUB")
    pictures["jazz"] = pictures["rock"]
    if "company" in pictures:
        pictures["factory"] = pictures.pop("company")
    # Same concepts, different book spellings. Never infer a picture by substring.
    aliases = {"appetiser": "starter", "public transport": "public transportation",
               "laboratory": "lab", "the netherlands": "netherlands", "curly hair": "curly",
               "straight hair": "straight", "a bottle of water": "water", "a slice of cake": "cake",
               "main course": "main dish", "brush": "brush teeth", "diary": "write a diary",
               "rest": "rest", "festival": "street fair", "tired": "feel exhausted",
               "fish": "go fishing", "camp": "camp in the forest", "climbing": "climb a mountain",
               "ski": "go skiing", "swimming": "swim", "camping": "camp in the forest",
               "apartment": "apartment", "refrigerator": "fridge"}
    for key, value in aliases.items():
        if value in pictures and key not in pictures:
            pictures[key] = pictures[value]
    reviewed = ROOT / "tools/grade6-image-choices.json"
    if reviewed.exists():
        pictures.update(json.loads(reviewed.read_text(encoding="utf-8")))
    return pictures


NUMBERS = {"one hundred": "100", "one hundred and fifty": "150", "two hundred": "200",
           "five hundred": "500", "first": "1st", "twelfth": "12th", "twenty-third": "23rd", "fiftieth": "50th"}


def vocab(unit, pictures):
    result = []
    for group in unit["groups"]:
        for word in group["items"]:
            word = copy.deepcopy(word)
            if word["en"] in NUMBERS:
                word["num"] = NUMBERS[word["en"]]
            elif word["en"].lower() in pictures:
                word.update(pictures[word["en"].lower()])
            else:
                raise ValueError("Missing reviewed illustration: " + word["en"])
            result.append(word)
    return result


def check_question(row, grammar_id):
    sentence, *wrong = row
    marked = STAR.findall(sentence)
    assert len(marked) == 1, sentence
    answer = marked[0]
    assert len(wrong) == 3 and len(set([answer, *wrong])) == 4, row
    return dict(q=STAR.sub("___", sentence), answer=answer, options=[answer, *wrong],
                complete=plain(sentence), grammarId=grammar_id)


def questions(unit):
    return [check_question(row, g["id"]) for g in unit["grammar"] for row in g["checks"]]


def make_bank(unit, items):
    rng = random.Random("g6-" + unit["id"])
    sets = []
    for source, target, title in (("en", "tr", "Vocabulary: English to Turkish"),
                                  ("tr", "en", "Vocabulary: Turkish to English")):
        rows = []
        for word in items:
            alternatives = sorted({w[target] for w in items if w[target] != word[target]})
            opts = [word[target], *rng.sample(alternatives, 3)]
            rng.shuffle(opts)
            rows.append({"q": f"{word[source]} - choose the meaning." if source == "en"
                         else f"{word[source]} - choose the English word.",
                         "a": [{"t": o, "c": o == word[target]} for o in opts]})
        sets.append(dict(code=f"g6-{unit['id']}-{source}", name=title, by=AUTHOR, type="multiple_choice", questions=rows))
    rows = []
    for q in questions(unit):
        opts = q["options"][:]
        rng.shuffle(opts)
        rows.append({"q": q["q"], "grammarId": q["grammarId"], "explanation": q["complete"],
                     "a": [{"t": o, "c": o == q["answer"]} for o in opts]})
    sets.append(dict(code=f"g6-{unit['id']}-grammar", name="Grammar in context", by=AUTHOR,
                     type="multiple_choice", questions=rows))
    return dict(authored=True, curriculum=EDITION, by=AUTHOR, sets=sets,
                words=[{"en": w["en"], "tr": w["tr"]} for w in items], online=[])


def exercise(title, task, **extra):
    return dict(type="exercise", title=title, tasks=[task], **extra)


def make_deck(unit, items):
    from grade6_pacing import illustrated_slides, ACCENTS
    return dict(title=unit["title"], titleTr=unit["titleTr"], emoji=unit["emoji"], authored=True,
                curriculum=EDITION, visualStyle="illustrated", accent=ACCENTS[unit["id"]],
                source=source_ref(unit), pages=[], slides=illustrated_slides(unit, items))


def source_ref(unit):
    return dict(studentBook={"file": "ingilizce6_ders_kitabi.pdf", "pages": unit["sb"]},
                workbook={"file": "ingilizce6_calisma_kitabi.pdf", "pages": unit["wb"]} if unit["wb"] else None,
                note="Curriculum reference only. All passages and tasks are original ENG HUB work.")


def selected_checks(unit):
    # At least one check for every target before adding a second/third example.
    rows = []
    for index in range(max(len(g["checks"]) for g in unit["grammar"])):
        for g in unit["grammar"]:
            if index < len(g["checks"]):
                rows.append(check_question(g["checks"][index], g["id"]))
    return rows[:16]


def make_pdfs(unit, folder):
    from grade6_worksheets import make_pdfs as render_pdfs
    return render_pdfs(unit, folder, selected_checks(unit), CORRECTIONS[unit["id"]], AUTHOR, EDITION)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", type=Path)
    modes = ap.add_mutually_exclusive_group()
    modes.add_argument("--slides-only", action="store_true", help="Preserve worksheets, banks and catalog; update lessons and alignment only.")
    modes.add_argument("--worksheets-only", action="store_true", help="Update only the three local worksheet PDFs and manifest per Grade 6 theme.")
    args = ap.parse_args()
    if args.worksheets_only:
        for unit in UNITS:
            folder = OUT / unit["id"] / "worksheets"
            folder.mkdir(parents=True, exist_ok=True)
            save(folder / "manifest.json", {"items": make_pdfs(unit, folder)})
            print(f"{unit['id']}: 2 worksheets + teacher key, 6 A4 pages")
        return
    pictures = existing_pictures()
    sources = []
    if args.books:
        from pypdf import PdfReader
        for name in ("ingilizce6_ders_kitabi.pdf", "ingilizce6_calisma_kitabi.pdf"):
            path = args.books / name
            sources.append(dict(file=name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                pages=len(PdfReader(path).pages)))
    elif (OUT / "curriculum.json").exists():
        sources = json.loads((OUT / "curriculum.json").read_text(encoding="utf-8"))["books"]
    alignment = dict(curriculum=EDITION, author=AUTHOR, books=sources, units=[])
    catalog_path = ROOT / "app/data/catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    grade = next(g for g in catalog["grades"] if g["id"] == "g6")
    for unit in UNITS:
        base = OUT / unit["id"]
        items = vocab(unit, pictures)
        bank = make_bank(unit, items)
        deck = make_deck(unit, items)
        save(base / "presentation/slides.json", deck)
        if not args.slides_only:
            save(base / "games/bank.json", bank)
            ws = base / "worksheets"
            ws.mkdir(parents=True, exist_ok=True)
            manifests = make_pdfs(unit, ws)
            save(ws / "manifest.json", {"items": manifests})
            # Retired old-curriculum site copies are not current-theme games.
            save(base / "sites/manifest.json", {"items": [], "curriculum": EDITION})
        qcount = sum(len(s["questions"]) for s in bank["sets"])
        entry = next(u for u in grade["units"] if u["id"] == unit["id"])
        entry["has"].update(presentation=True, games=True, worksheets=True)
        entry["counts"].update(games=qcount, worksheets=3, worksheetLinks=0, offlineSites=0)
        entry["onlineGames"] = 0
        alignment["units"].append(dict(id=unit["id"], title=unit["title"], source=source_ref(unit),
            grammar=[{"id": g["id"], "title": g["title"]} for g in unit["grammar"]],
            vocabulary=[g["title"] for g in unit["groups"]], slides=len(deck["slides"]), words=len(items),
            questions=qcount, worksheets=2, answerKeys=1,
            textCards=[w["en"] for w in items if w.get("textOnly")]))
        print(f"{unit['id']}: {len(deck['slides'])} slides, {len(items)} words, {qcount} questions; 2 worksheets + key")
    if not args.slides_only:
        save(catalog_path, catalog)
    save(OUT / "curriculum.json", alignment)


if __name__ == "__main__":
    main()
