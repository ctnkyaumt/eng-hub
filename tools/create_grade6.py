"""Write authored Grade 6 content. No app build and no network access.

Run with the bundled Python (reportlab/pypdf), optionally --books <read-only folder>.
Only g6 content and g6 catalog entries are written; other grades are untouched.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import re
from xml.sax.saxutils import escape

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
                word.update(textOnly=True, imageNote="Text card: no verified local picture for this meaning.")
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
    n = unit["id"].removeprefix("u")
    slides = [dict(type="title", kicker="REVISION 1 & 2" if n == "revision" else "THEME " + n,
                   title=unit["title"], titleTr=unit["titleTr"], emoji=unit["emoji"]),
              dict(type="scene", title="Our lesson", emoji=unit["emoji"],
                   bubbles=[{"text": goal} for goal in unit["goals"]])]
    offset = 0
    for group in unit["groups"]:
        for start in range(0, len(group["items"]), 4):
            block = items[offset + start:offset + start + 4]
            slides.append(dict(type="vocab", title=group["title"], items=block))
            slides.append(exercise("Word check", dict(kind="match", q="Match the words and meanings.",
                                   pairs=[{"a": w["en"], "b": w["tr"]} for w in block])))
        offset += len(group["items"])
    for g in unit["grammar"]:
        for en, tr in g["examples"]:
            example = dict(en=en, tr=plain(tr), trEm=STAR.findall(tr), textOnly=True)
            clock = re.search(r"\b([0-2]\d:[0-5]\d)\b", en)
            if clock:
                example["time"] = clock[1]
            slides.append(dict(type="grammar", title=g["title"], rule=g["rule"], grammarId=g["id"], examples=[example]))
        for row in g["checks"]:
            q = check_question(row, g["id"])
            slides.append(exercise("Language check", dict(kind="choose", q=q["q"],
                                   answer=q["answer"], options=q["options"]), grammarId=g["id"]))
    for start in (0, 2):
        slides.append(dict(type="dialogue", title="A conversation", dialogues=[dict(lines=[
            dict(who=who, text=text, tr=tr) for who, text, tr in unit["dialogue"][start:start + 2]])]))
    sentences = re.split(r"(?<=[.!?])\s+", unit["story"])
    half = (len(sentences) + 1) // 2
    for start in (0, half):
        slides.append(dict(type="scene", title=unit["storyTitle"], emoji="📖",
                           bubbles=[dict(text=" ".join(sentences[start:start + half]))]))
    for q, answer in unit["reading"]:
        slides.append(exercise("Reading check", dict(kind="flash", q=q, answer=answer)))
    # The established lesson format uses four large unit missions.
    # Text and identical visual choices are excluded from picture questions.
    selected, seen = [], set()
    for word in items:
        if not word.get("img") or word["img"] in seen:
            continue
        seen.add(word["img"])
        selected.append({**word, "audio": "/app/audio/words/" + slug(word["en"]) + ".wav"})
        if len(selected) == 4:
            break
    assert len(selected) == 4, f"Four verified local pictures required: {unit['id']}"
    for kind, title in (("dragmatch", "Picture match"), ("listenpicture", "Listen and find")):
        slides.append(dict(type="mission", title=title, task=dict(kind=kind, items=selected)))
    order = []
    for g in unit["grammar"]:
        for en, tr in g["examples"]:
            en, tr = plain(en), plain(tr)
            if 4 <= len(en.split()) <= 11 and not en.endswith("?"):
                order.append(dict(answer=en, tr=tr))
    slides.append(dict(type="mission", title="Sentence workshop", task=dict(kind="dragorder", sentences=order[:6])))
    slides.append(dict(type="mission", title="Your turn to speak", task=dict(kind="flash", q=unit["speaking"],
                       answer="Use the lesson examples to help. Check the target structures, then swap roles.")))
    slides.append(dict(type="end", title="Ready for more practice", titleTr="Oyunlar ve özgün çalışma kâğıtları", emoji="🎯"))
    return dict(title=unit["title"], titleTr=unit["titleTr"], emoji=unit["emoji"], authored=True,
                curriculum=EDITION, accent=["#0d9488", "#2563eb"], source=source_ref(unit), pages=[], slides=slides)


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
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

    font_dir = Path(os.environ.get("G6_FONT_DIR", "C:/Windows/Fonts"))
    for name, file in (("G6", "arial.ttf"), ("G6-Bold", "arialbd.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(font_dir / file)))
    normal = ParagraphStyle("body", fontName="G6", fontSize=10.5, leading=15, spaceAfter=6)
    small = ParagraphStyle("small", parent=normal, fontSize=9, leading=12)
    heading = ParagraphStyle("section", fontName="G6-Bold", fontSize=13, leading=17, spaceBefore=12, spaceAfter=8)
    navy = colors.HexColor("#15344c")
    width, height = A4
    def p(text, style=normal):
        return Paragraph(escape(text).replace("\n", "<br/>"), style)
    def h(text):
        return p(text, heading)
    def lines(count=2):
        return [p("________________________________________________________________________", small), Spacer(1, 5)] * count
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(navy)
        canvas.setFont("G6-Bold", 10)
        label = "REVISION 1 & 2" if unit["id"] == "revision" else "THEME " + unit["id"][1:]
        canvas.drawString(42, height - 34, f"ENG HUB     GRADE 6     {label}")
        canvas.setFont("G6", 9)
        canvas.drawString(42, height - 49, unit["title"])
        canvas.setStrokeColor(navy)
        canvas.line(42, height - 57, width - 42, height - 57)
        canvas.setFont("G6", 8)
        canvas.drawString(42, 28, "Original ENG HUB activities - curriculum aligned; no textbook exercises reproduced.")
        canvas.drawRightString(width - 42, 28, str(doc.page))
        canvas.restoreState()
    def write(name, pages):
        flow = []
        for i, page in enumerate(pages):
            if i:
                flow.append(PageBreak())
            flow.extend(page)
        SimpleDocTemplate(str(folder / name), pagesize=A4, leftMargin=42, rightMargin=42,
                          topMargin=72, bottomMargin=46, title=unit["title"] + " - " + name,
                          author=AUTHOR, pageCompression=1, invariant=1).build(flow, onFirstPage=footer, onLaterPages=footer)
    def student(title):
        return [h(title), p("Name: ________________________   Class: ______   Date: ______________", small)]
    checks = selected_checks(unit)
    half = (len(checks) + 1) // 2
    def quiz(qs, first=1):
        result = []
        for i, q in enumerate(qs, first):
            options = q["options"][:]
            random.Random(unit["id"] + str(i)).shuffle(options)
            result += [p(f"{i}. {q['q']}"), p("    ".join(f"{chr(65+j)}) {o}" for j, o in enumerate(options)), small)]
        return result
    all_words = [w for group in unit["groups"] for w in group["items"]]
    match_words = [group["items"][i] for group in unit["groups"] for i in (0, 1)]
    right = [w["tr"] for w in match_words]
    random.Random(unit["id"]).shuffle(right)
    table = Table([[p(f"{i+1}. {w['en']}  ____"), p(f"{chr(65+i)}. {right[i]}")]
                   for i, w in enumerate(match_words)], colWidths=[260, width - 344])
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    a1 = student("Worksheet A - Words and language") + [h("A1. Match the words and meanings."), table,
          h("A2. Choose the correct answer.")] + quiz(checks[:half])
    a2 = student("Worksheet A - Reading and writing") + [h("A3. " + unit["storyTitle"]), p(unit["story"])]
    for i, (q, _) in enumerate(unit["reading"], 1):
        a2 += [p(f"{i}. {q}")] + lines(1)
    a2 += [h("A4. True or false? Correct the false statements.")]
    for statement, _ in unit["truth"]:
        a2 += [p("T / F    " + statement)]
    a2 += lines(2) + [h("A5. Your own message"), p(unit["writing"])] + lines(6)
    b1 = student("Worksheet B - Language workshop") + [h("B1. Choose the correct answer.")] + quiz(checks[half:], half + 1)
    order = []
    for g in unit["grammar"]:
        for en, _ in g["examples"]:
            en = plain(en)
            if 4 <= len(en.split()) <= 9 and not en.endswith("?"):
                order.append(en)
    order = order[:3]
    b1 += [h("B2. Put the words in order. Keep the punctuation.")]
    for sentence in order:
        tokens = sentence.split()
        random.Random(sentence).shuffle(tokens)
        b1 += [p(" / ".join(tokens))] + lines(1)
    b2 = student("Worksheet B - Listening and speaking") + [h("B3. Listen twice. Complete the notes."),
          p("Your teacher will read a short message. Write a word, phrase or number.")]
    for q, _ in unit["listenQs"]:
        b2 += [p(q + ": _____________________________________________________"), Spacer(1, 10)]
    b2 += [h("B4. Pair task"), p(unit["speaking"]),
           p("First make notes. Speak without reading a full script. Then swap roles.")] + lines(5)
    b2 += [h("B5. Exit ticket"), p("Write two new words in sentences. Then write one question using today's grammar.")] + lines(5)
    b2 += [p("Self-check: [ ] I used the target language.  [ ] I listened and replied.  [ ] I checked my work.", small)]
    key1 = [h("Teacher key - Worksheet A"), p("Allow equivalent correct answers. These tasks are original; page references below identify curriculum scope.", small),
            h("A1. Vocabulary"), p("; ".join(f"{i+1}-{chr(65+right.index(w['tr']))}" for i, w in enumerate(match_words))),
            h("A2. Language"), p("\n".join(f"{i}. {q['answer']}" for i, q in enumerate(checks[:half], 1))),
            h("A3. Reading"), p("\n".join(f"{i}. {a}" for i, (_, a) in enumerate(unit["reading"], 1))),
            h("A4. True or false"), p("\n".join(f"{i}. " + ("True." if a else "False. " + CORRECTIONS[unit["id"]][i]) for i, (s, a) in enumerate(unit["truth"], 1))),
            h("A5. Sample writing"), p(unit["model"]),
            p("Writing / 8: task completed 0-2; target grammar 0-2; appropriate vocabulary 0-2; clarity and punctuation 0-2.", small)]
    key2 = [h("Teacher key - Worksheet B"), h("B1. Language"),
            p("\n".join(f"{i}. {q['answer']}" for i, q in enumerate(checks[half:], half + 1))),
            h("B2. Sentence order"), p("\n".join(f"{i}. {s}" for i, s in enumerate(order, 1))),
            h("B3. Teacher read-aloud script"), p("Read naturally twice. Pause between sentences. Students do not need a recording.", small),
            p(unit["listening"]), p("\n".join(f"{q}: {a}" for q, a in unit["listenQs"])),
            h("B4-B5. Speaking and exit ticket"), p("Answers vary. Award 0-2 each for target grammar, relevant vocabulary, responding to a partner and understandable delivery. Accept any correct exit questions and sentences."),
            h("Curriculum reference"), p(f"MEB English 6 Student's Book (2026), pp. {unit['sb'][0]}-{unit['sb'][1]}. " +
                (f"Workbook, pp. {unit['wb'][0]}-{unit['wb'][1]}." if unit["wb"] else "Revision 1 and Revision 2; the workbook starts at Theme 1."), small)]
    write("original-a.pdf", [a1, a2])
    write("original-b.pdf", [b1, b2])
    write("original-key.pdf", [key1, key2])
    return [dict(title=title, file=name, authored=True, curriculum=EDITION, by=AUTHOR, type="worksheet",
                 desc=desc, size=(folder / name).stat().st_size)
            for title, name, desc in (("Çalışma Kâğıdı A - Kelime, Dil ve Okuma", "original-a.pdf", "2 sayfa · özgün alıştırmalar"),
                                      ("Çalışma Kâğıdı B - Dil, Dinleme ve Konuşma", "original-b.pdf", "2 sayfa · özgün alıştırmalar"),
                                      ("Öğretmen Anahtarı - A ve B", "original-key.pdf", "2 sayfa · cevaplar, dinleme metni ve örnek yazma"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", type=Path)
    args = ap.parse_args()
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
    save(catalog_path, catalog)
    save(OUT / "curriculum.json", alignment)


if __name__ == "__main__":
    main()
