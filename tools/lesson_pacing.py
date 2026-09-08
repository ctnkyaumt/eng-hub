"""Small teaching pages and section-specific speaking missions. No build step."""
import copy
import re
from lesson_examples import RULES

INVITATIONS = [
    ("Would you like to", "*Would you like to* join our picnic?", "Pikniğimize katılmak ister misin?", "🧺"),
    ("Would you like to", "*Would you like to* play chess after school?", "Okuldan sonra satranç oynamak ister misin?", "♟️"),
    ("How about", "*How about* having lunch together?", "Birlikte öğle yemeği yemeye ne dersin?", "🥪"),
    ("How about", "*How about* visiting a museum on Sunday?", "Pazar günü bir müzeyi gezmeye ne dersin?", "🏛️"),
    ("Let's", "*Let's* go for a walk in the park.", "Hadi parkta yürüyüşe çıkalım.", "🌳"),
    ("Let's", "*Let's* watch a film at my house.", "Hadi benim evimde bir film izleyelim.", "🎬"),
    ("Why don't we", "*Why don't we* meet at the library?", "Neden kütüphanede buluşmuyoruz?", "📚"),
    ("Why don't we", "*Why don't we* invite our classmates?", "Neden sınıf arkadaşlarımızı davet etmiyoruz?", "👥"),
]

CHALLENGES = {
    "Making Invitations": "Invite your partner to a weekend activity. Agree on a place and a time.",
    "Accepting & Refusing": "Your partner invites you out. Accept once, then refuse politely with a reason.",
    "On the Phone": "Caller: ask for a friend. Receiver: your friend is out. Take a message, then swap roles.",
    "Imperatives in Recipes": "Teach your partner how to make a sandwich. Give three short instructions.",
    "Sequencing Words": "Explain a simple recipe. Your partner repeats the steps in the same order.",
    "Preferences": "Plan a music afternoon. Compare your preferences and choose something you both like.",
    "How often ...?": "Interview your partner about two hobbies. Report one answer to the class.",
    "Internet Safety": "Your partner gets a message from a stranger. Give two safety instructions.",
    "Giving Instructions": "Help your partner open a browser and save a worksheet. Give the steps aloud.",
    "Comparing Adventures": "Choose an adventure for a class trip. Compare two activities and explain your choice.",
    "Simple Past — Regular": "Describe yesterday's trip: a place, an activity and your opinion. Ask your partner a question.",
    "Simple Past — Irregular": "Tell your partner three things about your last holiday: where you went, what you saw and what you ate.",
    "have to / has to": "Share the housework. Give each family member a job and report their responsibilities.",
    "Predictions with will": "You are a weather reporter. Make two predictions for tomorrow and one uncertain prediction.",
    "If Clauses (Type 1)": "Plan a picnic. Say what you will do if it rains. Your partner adds another possible situation.",
    "Giving Advice in a Disaster": "Make an emergency plan. Give your partner two useful pieces of advice.",
    "Passive Voice — Present": "Describe how objects are used in a laboratory. Your partner guesses the object.",
    "Passive Voice — Past": "Choose an invention. Tell your partner when it was invented and who invented it, if you know.",
    "Classroom Rules": "You are the teacher. Give three classroom instructions; your partner acts them out.",
    "Asking for Permission": "You are at a cafe. Ask permission for two things; your partner gives different replies.",
    "Clothes Verbs": "Act out a clothes-shopping conversation. Try something on and describe how it looks.",
    "There is / There are": "Describe a room without naming it. Your partner draws or guesses the room.",
    "Simple Future — be going to": "Plan a holiday together. Say where you are going to go and two things you are going to do.",
    "Comparative Adjectives": "Choose two things from this unit. Make two comparisons; your partner checks them.",
    "Superlative Adjectives": "Make an animal record card. Give two facts using superlatives.",
}


def restore_teaching(slides):
    result = []
    for slide in slides:
        if slide.get("paced"):
            if slide.get("teachingSource"):
                result.append(slide["teachingSource"])
        else:
            result.append(slide)
    return result


def pace_teaching(slide):
    if slide["type"] not in ("grammar", "compare"):
        return [slide]
    source = copy.deepcopy(slide)
    examples = list(slide.get("examples", []))
    for col in slide.get("columns", []):
        examples.extend(dict(e, focus=col["title"]) for e in col.get("examples", []))
    if slide.get("title") == "Making Invitations":
        for focus, en, tr, emoji in INVITATIONS:
            examples.append(dict(en=en, tr=tr, emoji=emoji, trEm=[tr], focus=focus))
    if not examples:
        return [slide]
    pages = []
    for example in examples:
        marks = re.findall(r"\*(.+?)\*", example["en"])
        focus = example.get("focus") or " / ".join(dict.fromkeys(marks)) or slide["title"]
        # Each English example gets a full page; its translation is a separate Next step.
        page = {"type": "grammar", "title": slide["title"], "titleTr": slide.get("titleTr", ""),
                "chips": [focus], "examples": [example], "paced": True}
        rule = RULES.get(focus.lower().strip(".!?"))
        if not rule:
            # Preserve explanations that teach one concept, or a sentence
            # specifically about this focus, without displaying other forms.
            for sentence in re.split(r"(?<=\.)\s+|\s+·\s+", slide.get("rule") or ""):
                terms = re.findall(r"\*(.+?)\*", sentence)
                if len(terms) <= 1 and (not terms or len(examples) == 1 or
                    focus.lower() in sentence.lower() or not slide.get("chips")):
                    rule = sentence
                    break
        if rule:
            page["rule"] = rule
        pages.append(page)
    # Keep all examples of the same form together, in first-seen order.
    order = list(dict.fromkeys(p["chips"][0] for p in pages))
    pages.sort(key=lambda p: order.index(p["chips"][0]))
    for n, page in enumerate(pages, 1):
        page["part"] = [n, len(pages)]
    pages[0]["teachingSource"] = source
    return pages


def extra_missions(slides, rng):
    """Retrieve a section's language, then transfer it to a partner conversation."""
    result = []
    for slide in slides:
        if slide["type"] not in ("grammar", "compare", "dialogue"):
            continue
        examples = list(slide.get("examples", []))
        for col in slide.get("columns", []):
            examples.extend(col.get("examples", []))
        if examples:
            example = rng.choice(examples)
            plain = example["en"].replace("*", "")
            result.append({"type": "mission", "title": "Unit Mission · Say It Your Way",
                "titleTr": slide["title"], "task": {"kind": "flash",
                "q": CHALLENGES.get(slide["title"], "Read the model. Change one detail. Your partner makes a new sentence."),
                "clue": plain, "answer": "Check: keep the same grammar pattern and use words from this unit.",
                "tr": example.get("tr", "")}})
        else:
            for dialogue in slide.get("dialogues", [])[:1]:
                lines = dialogue.get("lines", [])
                if len(lines) < 2:
                    continue
                result.append({"type": "mission", "title": "Unit Mission · Partner Challenge",
                    "titleTr": slide["title"], "task": {"kind": "flash",
                    "q": "Work in pairs. Reply, then swap roles and change the situation.",
                    "clue": lines[0]["text"], "answer": "Model reply: " + lines[1]["text"]}})
    return result
