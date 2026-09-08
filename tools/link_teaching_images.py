"""Attach exact educational image matches, without downloading image assets.

Fetch ARASAAC's English metadata into tools/cache/arasaac-en.json first.
Images are loaded from the attributed source only when their slide opens.
"""
import json
from pathlib import Path
import re
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    "art club": "art", "ballet club": "ballet", "chess club": "chess", "drama club": "theatre",
    "environment club": "environment", "film club": "cinema", "folk dance club": "dance",
    "maths club": "mathematics", "music club": "music", "science club": "science", "technology club": "technology",
    "act in plays": "act", "amazing": "surprising", "awesome": "fantastic", "be late": "late",
    "be responsible for": "responsibility", "big / large": "big", "board marker": "marker",
    "bookcase": "bookshelf", "brand-new": "new", "buddy": "friend", "mate": "friend",
    "can't stand": "hate", "challenging": "difficult", "colourful": "multicoloured",
    "count on": "trust", "dangerous": "danger", "debris": "rubble", "delete": "erase",
    "disappointing": "disappointment", "do an experiment": "experiment", "do experiments": "experiment",
    "draw pictures": "draw", "drink / beverage": "drink", "electric bulb": "light bulb",
    "enjoyable": "fun", "enormous": "enormous", "entertaining": "fun", "entertainment": "leisure",
    "exciting": "excitement", "extreme sport": "extreme sports", "fascinating": "interesting",
    "fatty": "fat", "feel annoyed": "annoyed", "feel bored": "bored", "feel exhausted": "exhausted",
    "feel happy": "happy", "feel relaxed": "relaxed", "feel so hungry": "hungry", "feel worried": "worried",
    "fighting": "fight", "fond of": "like", "giant / huge": "giant", "go skiing": "ski",
    "goggles": "swimming goggles", "have breakfast": "breakfast", "have lunch": "lunch",
    "healthcare": "health care", "hiking": "hike", "hire / rent": "rent", "historical sites": "monument",
    "hold on": "wait", "hang on": "wait", "holiday": "holidays", "hot air balloon": "balloon",
    "huge": "giant", "impressive": "surprising", "improvement": "improve", "incredible": "surprising",
    "individually": "alone", "isolated": "isolated", "jolly": "happy", "keep quiet": "be quiet",
    "laid-back": "relaxed", "loud": "noisy", "main dish": "main course", "make the dough": "knead",
    "meet friends": "meet", "noon": "midday", "obey the rules": "obey", "pan": "frying pan",
    "pay the bills": "pay", "peaceful": "peace", "play the guitar": "play guitar",
    "rarely": "seldom", "read a book": "read", "read books": "read", "relaxing": "relax",
    "rest / relax": "rest", "ride a roller coaster": "roller coaster", "rubbish bin / trash can": "rubbish bin",
    "scary": "frightening", "shelf": "shelves", "shorts": "short trousers", "sign in": "log in",
    "sing songs": "sing", "smart board": "interactive whiteboard", "social networking site": "social network",
    "solve problems": "solve", "starter / appetizer": "appetizer", "storm": "thunderstorm",
    "succeed": "success", "take a course": "course", "take a nap": "nap", "take a photo": "take pictures",
    "take photos": "take pictures", "take a tour": "tour", "take out the garbage": "take out the rubbish",
    "talk / speak": "speak", "terrible / awful": "bad", "terrific": "fantastic", "thrilling": "excitement",
    "tiring": "tired", "to-do list": "list", "unbelievable / incredible": "surprising", "unhealthy": "unhealthy",
    "view": "landscape", "visit relatives": "visit", "wash face": "wash your face",
    "watch movies": "watch a film", "water the flowers": "water plants", "wear": "wear clothes",
    "wildfire": "forest fire", "wooden": "wood", "write a diary": "write", "yummy": "delicious",
    "aftershock": "earthquake", "back up": "help", "bad line": "telephone",
    "be good at": "ability", "be happy": "happy", "bright": "bright", "browse": "surf the internet",
    "call back": "call", "come over": "visit", "comment": "commentary", "contact": "communicate",
    "discovery": "discover", "discoverer": "scientist", "diving suit": "wetsuit", "eco-friendly": "recycle",
    "emergency": "emergencies", "energetic": "active", "engaged": "busy", "equipment": "tools",
    "experience": "experience", "experienced": "expert", "facts": "information", "fancy": "elegant",
    "fantasy": "imagination", "fashionable": "fashion", "first aid": "first-aid kit",
    "folk music": "music", "fresh": "fresh", "friend request": "social network", "furry": "fur",
    "get in touch": "communicate", "get on well with somebody": "friendship", "habit": "routine",
    "half-term holiday": "holidays", "handmade": "craft", "heritage": "monument", "historical": "ancient",
    "homemade": "cook", "hospitable": "welcome", "ignore responsibilities": "ignore",
    "inexperienced": "beginner", "keep a promise": "promise", "keep in touch": "communicate",
    "kitchen chores": "cleaning", "local": "near", "log off": "log out", "log on": "log in",
    "loyalty": "loyal", "magical": "magic", "make it rest": "wait", "marinate": "marinade",
    "modern": "modern", "mutual": "together", "mysterious": "mystery", "natural": "nature",
    "old-fashioned": "old", "ordinary": "normal", "polite": "respect", "preheat": "heat",
    "priceless": "valuable", "put someone through": "telephone", "relationship": "relationship",
    "rescue team": "rescue", "reserve": "reservation", "ridiculous": "ridiculous",
    "run errands": "shopping", "scientific": "science", "share the chores": "cooperate",
    "side dish": "side dish", "silk": "silk", "snob": "arrogant", "social": "sociable",
    "some chores": "cleaning", "spring holiday": "holidays", "stay": "stay", "steel": "metal",
    "stylish": "elegant", "summer holiday": "holidays", "survive": "survive",
    "take care of a pet": "pet care", "take order": "waiter", "take risks": "risk",
    "taste": "taste", "tradition": "custom", "traditional": "custom", "trendy": "fashion",
    "truly": "true", "unbearable": "unbearable", "unconditional": "unconditional", "usually": "usually",
    "waiting to eat": "wait", "weekdays": "calendar", "winter holiday": "holidays",
}
# Word sense overrides: these exact IDs distinguish verbs, objects and traits.
OVERRIDES = {"bear": 2488, "boil": 5485, "support": 30008, "friendship": 8488,
             "trust": 36694, "cool": 11599, "pan": 2558, "light": 4679,
             "read books": 7141, "read a book": 7141, "glasses": 3329,
             "thick": 37063, "keep": 27511}
OVERRIDES.update({
    "attend": 21385, "crowded": 38445, "top": 5451, "bottom": 5355,
    "pot": 9086, "add": 8026, "cut": 10185, "fly": 6246,
    "stuffed": 38801, "evacuate": 37863, "hang out": 2255,
    "call": 36305, "call back": 36305, "pick up": 36306,
    "get back": 29714, "company": 8581, "file": 10310, "check": 39555,
    "die": 29862, "result": 32802, "relaxing": 31310,
    "science club": 32542, "scientific": 32542, "feel": 30197,
    "pack": 2931, "enormous": 4658, "huge": 4658, "giant / huge": 4658,
    "stylish": 37997, "fancy": 37997,
})
# These words need a purpose-made visual or a text cue; automatic homonyms
# (bank accounts, hanging laundry, election forms...) are not teaching images.
NO_AUTOMATCH = {"account", "hang up", "process", "gain", "order", "join"}
ALIASES.update({
    "advice": "advise", "art club": "painting", "board marker": "whiteboard marker",
    "attachment": "paperclip", "amazing": "surprised", "impressive": "surprised",
    "incredible": "surprised", "unbelievable / incredible": "surprised", "fascinating": "surprised",
    "bright": "brightness", "colourful": "colours", "cultural": "culture",
    "entertainment": "leisure time", "exciting": "excited", "thrilling": "excited",
    "enormous": "giant", "feel relaxed": "calm", "laid-back": "calm", "keep quiet": "silence",
    "first aid": "medicine cabinet", "handmade": "traditional craftwork", "healthcare": "health",
    "indoor": "inside", "involve": "participation", "isolated": "isolation", "meet friends": "friends",
    "smart board": "interactive white board", "storm": "stormy", "stylish": "style",
    "fancy": "style", "take out the garbage": "take out trash", "wash face": "soap the face",
    "wear": "get dressed", "water the flowers": "watering can", "sour": "lemon",
})


def main():
    from teaching_diagrams import diagrams
    custom = diagrams()
    metadata = json.loads((ROOT / "tools/cache/arasaac-en.json").read_text(encoding="utf-8"))
    by_keyword = defaultdict(list)
    by_id = {p["_id"]: p for p in metadata}
    for pic in metadata:
        if pic.get("sex") or pic.get("violence"):
            continue
        for key in pic["keywords"]:
            for word in (key["keyword"], key.get("plural", "")):
                if word:
                    by_keyword[word.lower()].append(pic)
    paths = sorted((ROOT / "content").glob("*/*/presentation/slides.json"))
    decks = {p: json.loads(p.read_text(encoding="utf-8")) for p in paths}
    existing = {}
    for deck in decks.values():
        for slide in deck["slides"]:
            if slide["type"] == "vocab":
                for item in slide["items"]:
                    if item.get("img", "").startswith("/app/"):
                        existing.setdefault(item["en"].lower(), item["img"])
    manifest, missing = {}, set()
    for deck in decks.values():
        for slide in deck["slides"]:
            if slide["type"] != "vocab":
                continue
            for item in slide["items"]:
                if item["en"].lower() in custom:
                    item.update(img=custom[item["en"].lower()], imageFit="contain", imageSource="ENG HUB", imageConcept=item["en"].lower())
                    continue
                if (item.get("img") and item.get("imageSource") != "ARASAAC") or item.get("num") is not None:
                    continue
                word = item["en"].lower()
                if word in NO_AUTOMATCH:
                    if item.get("imageSource") == "ARASAAC":
                        for key in ("img", "imageSource", "imageConcept", "imageFit"):
                            item.pop(key, None)
                    missing.add(word)
                    continue
                if word in existing:
                    item["img"] = existing[word]
                    continue
                concept = ALIASES.get(word, word)
                choices = by_keyword.get(concept, [])
                choices = sorted(choices, key=lambda p: not any(k["keyword"].lower() == concept for k in p["keywords"]))
                pic = by_id.get(OVERRIDES.get(word)) or (choices[0] if choices else None)
                tr = item.get("tr", "").lower()
                if word == "fish":
                    pic = by_id[6592 if "tut" in tr else 2520]
                if word == "glass" and tr == "cam":
                    pic = by_id[9140]
                if word == "close" and "yakın" in tr:
                    pic = by_id[30383]
                if not pic:
                    missing.add(word)
                    continue
                pid = pic["_id"]
                item.update(img=f"https://static.arasaac.org/pictograms/{pid}/{pid}_500.png",
                            imageConcept=concept, imageSource="ARASAAC", imageFit="contain")
                manifest[word] = {"id": pid, "concept": concept,
                    "keywords": [k["keyword"] for k in pic["keywords"]],
                    "source": f"https://arasaac.org/pictograms/en/{pid}"}
    for path, deck in decks.items():
        path.write_text(json.dumps(deck, ensure_ascii=False, indent=1), encoding="utf-8")
    manifest_path = ROOT / "app/img/teaching-sources.json"
    prior = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    prior.update(manifest)
    for word in NO_AUTOMATCH:
        prior.pop(word, None)
    manifest_path.write_text(json.dumps(prior, ensure_ascii=False, indent=1), encoding="utf-8")
    print("New source illustrations:", len(manifest), "Unmatched:", len(missing))
    print(", ".join(sorted(missing)))


if __name__ == "__main__":
    main()
