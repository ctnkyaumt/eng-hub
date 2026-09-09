#!/usr/bin/env python3
"""Bring the grade-5 decks in line with the course book and add practice pages.

  * slide order follows res/book.pdf (its theme table lists the sub-themes in
    teaching order); sections the book does not cover are dropped
  * number cards store the digits instead of an emoji, so 11 no longer shows up
    as the "1234" glyph
  * one compact, varied activity break is inserted after every teaching
    section, built from that section's own words and examples
  * three larger end-of-unit missions add picture dragging, listening and
    sentence building without replacing the short activity breaks

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
MAX_CARDS = 4    # at most four large cards per teaching page
MAX_TASKS = 3    # distinct activities, each on its own page
BACK = chr(92)

HOURS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12,
}

# The English teaching point and its Turkish realization rarely occupy the
# same position in a sentence. These patterns identify the translated phrase
# rather than simply colouring the whole translation. Unusual rule-summary
# examples deliberately fall back to their complete short Turkish label.
TR_TERM_PATTERNS = {
    "playing": (r"(?:gitar )?çalmayı", r"(?:basketbol )?oynamayı"),
    "reading": (r"(?:kitap )?okumayı",), "drawing": (r"resim çizmeyi",),
    "must": (r"\S+m[ae]l[ıi]\S*",), "mustn't": (r"\S+m[ae]m[ae]l[ıi]\S*",),
    "should": (r"\S+m[ae]l[ıi]\S*",), "shouldn't": (r"\S+m[ae]m[ae]l[ıi]\S*",),
    "have got": (r"\b\S*sahib\S*", r"\bsahip\S*", r"\bvar\b"),
    "has got": (r"\b\S*sahib\S*", r"\bsahip\S*", r"\bvar\b"),
    "haven't got": (r"\byok\b",), "hasn't got": (r"\byok\b",),
    "at": (r"saat\s+[^,.;]+?(?:da|de|ta|te)\b",),
    "on": (r"(?:Pazartesi|Salı|Çarşamba|Perşembe|Cuma|Cumartesi|Pazar)(?: günü)?",),
    "o'clock": (r"tam saatler",), "half past": (r"Buçuk geçiyor",),
    "quarter past": (r"Çeyrek geçiyor",), "quarter to": (r"Çeyrek var",),
    "past": (r"geçiyor",), "to": (r"\bvar\b", r"\b\S+za\b"),
    "a.m.": (r"Sabah",), "p.m.": (r"Akşam", r"öğleden sonra", r"Gece"),
    "there is": (r"\bvar\b",), "there are": (r"\bvar\b",),
    "there isn't": (r"\byok\b",), "there aren't": (r"\byok\b",),
    "is there": (r"var mı",), "are there": (r"var mı",),
    "am": (r"kısa ve zayıfım",),
    "is": (r"orta boylu", r"\S+yor mu", r"\S+[ae]cak mı"),
    "wear": (r"giyerim",), "buy": (r"satın alırım",),
    "need": (r"ihtiyacım var",), "own": (r"sahibim",),
    "every": (r"\bher\b",), "every day": (r"her gün",),
    "in the morning": (r"sabahları",), "in the evenings": (r"akşamları",),
    "now": (r"\bşimdi\b",), "at the moment": (r"şu anda",),
    "go": (r"giderim",), "goes": (r"gider",), "watches": (r"izler",),
    "fishes": (r"balık tutar",),
    "don't": (r"\b(?:koşma|bağırma|atma|unutma|paylaşma|gitmem|giymezsin|oturmayız|yapmazsın)\b",),
    "doesn't": (r"\b(?:oynamaz|çizmez|sevmez|izlemez|gitmez)\b",),
    "do": (r"\bmısın\b", r"\bmı\b"), "does": (r"\bmı\b",),
    "do you": (r"değil mi", r"mısın"), "does she": (r"değil mi",),
    "don't you": (r"değil mi",), "doesn't she": (r"değil mi",),
    "aren't you": (r"değil mi",), "isn't she": (r"değil mi",),
    "are you": (r"değil mi", r"mısın"), "is she": (r"değil mi", r"mu"),
    "am watching": (r"televizyon izliyorum",), "is sleeping": (r"uyuyor",),
    "are swimming": (r"yüzüyorlar",), "am not": (r"yapmıyorum",),
    "isn't": (r"\S+miyor", r"müsait değil"), "aren't": (r"\S+mıyorsun",),
    "are": (r"\S+yor musun", r"\S+[ae]cek misin",),
    "listening": (r"dinliyor musun",),
    "'s": (r"\b\S+(?:'nın|'nin|'nun|'nün)\b",),
    "'": (r"\b\S+lerin\b", r"\b\S+ların\b", r"\b\S+mın\b"),
    "more comfortable than": (r"daha rahat",), "closer than": (r"daha yakın",),
    "bigger than": (r"daha büyük",), "better than": (r"daha iyidir",),
    "stronger than": (r"daha güçlüdür",), "heavier than": (r"daha ağırdır",),
    "more dangerous than": (r"daha tehlikelidir",), "scarier than": (r"daha korkutucudur",),
    "the strongest": (r"en güçlü",), "the largest": (r"en büyük",),
    "the tallest": (r"en uzun",), "the fastest": (r"en hızlı",),
    "the most colourful": (r"en renkli",),
    "some": (r"Birkaç", r"Biraz"), "any": (r"Hiç",),
    "can i": (r"\S+(?:abilir|ebilir) miyim",),
    "can": (r"\S+(?:abilir|ebilir)",), "can't": (r"\S+(?:amaz|emez)",),
    "am going to": (r"\S+eceğim",), "is going to": (r"\S+ecek",),
    "are going to": (r"\S+acaklar",), "am not going to": (r"\S+meyeceğim",),
    "isn't going to": (r"\S+meyecek",), "aren't going to": (r"\S+meyeceksin",),
    "going to": (r"\S+[ae]cek (?:misin|mı)",),
    "would you like to": (r"ister misin",), "how about": (r"ne dersin",),
    "let's": (r"\bHadi\b",), "why don't we": (r"neden .+mıyoruz",),
    "i'd love to": (r"Çok isterim",), "sure": (r"\bTabii\b",),
    "of course": (r"\bElbette\b",), "i'm sorry": (r"\bÜzgünüm\b",),
    "i'd love to, but": (r"Çok isterdim ama",),
    "maybe next time": (r"Belki başka zaman",),
    "will": (r"\bolacak\b", r"su altında kalır", r"dışarı çıkacağız", r"güvende olursun", r"toprak kurur"),
    "won't": (r"\S+mayacak",),
    "might": (r"\S+abilir",), "may": (r"\S+ebilir",),
    "if": (r"\S+(?:sa|se|san|sen)\b",),
    "stay away": (r"uzak dur",), "don't panic": (r"Panik yapma",),
    "prefer": (r"tercih ederim",), "would rather": (r"yeğler",),
    "enjoy": (r"hoşlanırlar", r"keyif aldın"), "love": (r"çok severiz",),
    "how often": (r"Ne sıklıkla",), "twice a week": (r"Haftada iki kez",),
    "hardly ever": (r"neredeyse hiç",), "always": (r"her zaman",),
    "chop": (r"\bdoğra\b",), "add": (r"\bekle\b",),
    "boil": (r"\bkaynat\b",), "first": (r"\bÖnce\b",),
    "then": (r"\bSonra\b",), "after that": (r"Ondan sonra",),
    "finally": (r"Son olarak",), "how many": (r"\bKaç\b",),
    "how much": (r"Ne kadar",), "three": (r"\bÜç\b",),
    "a cup of": (r"Bir fincan",),
    "could i speak to": (r"görüşebilir miyim",), "hold on": (r"Lütfen bekleyin",),
    "can i take a message": (r"Mesajınızı alabilir miyim",),
    "isn't available": (r"müsait değil",), "am calling": (r"arıyorum",),
    "is talking": (r"konuşuyor",), "aren't answering": (r"cevap vermiyorlar",),
    "can you": (r"yardım eder misin",), "could you": (r"gösterir misin", r"yardım eder misin"),
    "shall i": (r"göndereyim mi", r"ben mi kurayım"),
    "would you mind": (r"bakar mısın", r"çıkarır mısın"),
    "click on": (r"\btıkla\b",), "type": (r"\byaz\b",), "save": (r"\bkaydet\b",),
    "more exciting than": (r"daha heyecan vericidir",),
    "the most thrilling": (r"en heyecan verici",), "harder than": (r"daha zordur",),
    "the most dangerous": (r"en tehlikelisidir",),
    "visited": (r"ziyaret ettik",), "stayed": (r"kaldılar",),
    "didn't": (r"sevmedim",), "did": (r"keyif aldın mı",),
    "went": (r"gittik",), "saw": (r"gördüm",), "took": (r"fotoğraf çekti",),
    "ate": (r"yedik",), "have to": (r"zorunda\S*",), "has to": (r"zorunda\S*",),
    "don't have to": (r"zorunda değiliz",), "give me a hand": (r"el atar mısın",),
    "all right": (r"\bPeki\b",), "sorry": (r"\bÜzgünüm\b",),
    "i'm afraid": (r"\bKorkarım\b",), "not now": (r"Şimdi olmaz",),
    "are done": (r"\byapılır\b",), "is used": (r"\bkullanılır\b",),
    "are developed": (r"\bgeliştirilir\b",), "are written": (r"\byazılır\b",),
    "was invented": (r"icat edildi",), "was discovered": (r"keşfedildi",),
    "were built": (r"inşa edildi",), "was written": (r"yazıldı",),
}

# Context pictures for examples that do not repeat a vocabulary-card phrase.
# Specific content wins; title icons are reserved for grammatical formulae.
EXAMPLE_ICON_RULES = [
    (r"\borange\b", "🍊"), (r"\bapples?\b", "🍎"),
    (r"\bumbrella\b", "☂️"), (r"\bsun\b|\bsunny\b", "☀️"),
    (r"\bcinema\b|\bfilms?\b", "🎬"), (r"\bbasketball\b", "🏀"),
    (r"\bdraw(?:ing)?\b|\bpictures?\b", "🎨"), (r"\blisten\b", "👂"),
    (r"\braise your hand\b", "✋"), (r"\bquiet(?:ly)?\b", "🤫"),
    (r"\brubbish\b|\bgarbage\b", "🗑️"), (r"\brun\b", "🏃"),
    (r"\btime\b|\bo'clock\b|\ba\.m\.\b|\bp\.m\.\b", "🕒"),
    (r"\bgo to bed\b|\bsleep(?:ing)?\b", "🛏️"),
    (r"\bschool\b|\bclass(?:room)?\b", "🏫"),
    (r"\bday\b|\bweek\b|\bmonth\b|\byear\b|\bjanuary\b", "📅"),
    (r"\bwatch(?:es|ing)?\b.*\btv\b", "📺"), (r"\bguitar\b", "🎸"),
    (r"\bhomework\b|\bstudy(?:ing)?\b", "📚"), (r"\bcook(?:ing)?\b", "🍳"),
    (r"\bswim(?:ming)?\b", "🏊"), (r"\bpicnic\b", "🧺"),
    (r"\bfish(?:es|ing)?\b", "🎣"), (r"\bteeth\b", "🪥"),
    (r"\belevator\b|\blift\b", "🛗"), (r"\bparis\b", "🗼"),
    (r"\bjokes?\b", "😂"), (r"\bstreet fairs?\b", "🎪"),
    (r"\btomatoes?\b", "🍅"), (r"\bcoffee\b", "☕"),
    (r"\blions?\b", "🦁"), (r"\bbears?\b", "🐻"),
    (r"\belephants?\b", "🐘"), (r"\bcrocodiles?\b", "🐊"),
    (r"\bwhales?\b", "🐋"), (r"\bgiraffes?\b", "🦒"),
    (r"\bbirthday\b|\bparty\b", "🎉"), (r"\bnot feeling well\b", "🤒"),
    (r"\bsnow\b|\bweather\b", "🌨️"), (r"\bearthquakes?\b", "🏚️"),
    (r"\bstay calm\b|\bdon't panic\b", "🧘"), (r"\bwindows?\b", "🪟"),
    (r"\bphone\b|\bmessage\b", "☎️"), (r"\blog in\b|\busername\b|\bpassword\b", "🔐"),
    (r"\be-?mail\b|\blink\b", "🔗"), (r"\bfriend requests?\b|\bstrangers?\b", "👥"),
    (r"\bguide\b", "🧭"), (r"\bclimb(?:ing)?\b", "🧗"),
    (r"\bdivers?\b|\bscuba diving\b", "🤿"), (r"\bhotel\b", "🏨"),
    (r"\bantalya\b|\bplane\b", "✈️"), (r"\bphotographs?\b", "📷"),
    (r"\blaboratory\b|\bexperiments?\b", "🧪"), (r"\bscientists?\b", "🔬"),
    (r"\bmedicines?\b|\bpenicillin\b", "💊"), (r"\btelephone\b", "☎️"),
    (r"\bpyramids?\b", "🔺"), (r"\breport\b|\bwritten\b", "📄"),
]

TITLE_ICONS = {
    "A / AN / THE": "🔤", "Classroom Rules": "🏫", "a.m. / p.m.": "🕒",
    "There is / There are": "🏠", "Time Expressions": "📅",
    "Simple Present — Positive": "🔁", "Simple Present": "🔁",
    "Simple Present — Routines": "🔁", "Negative & Question": "❓",
    "Question Tags": "💬", "Present Continuous — -ing": "🎬",
    "Present Continuous": "🎬", "Simple Present vs Present Continuous": "⏱️",
    "Comparative Adjectives": "⚖️", "Superlative Adjectives": "🏆",
    "Making Invitations": "💌", "Accepting & Refusing": "💬",
    "Accepting & Refusing Requests": "💬", "Predictions with will": "🔮",
    "If Clauses (Type 1)": "🔀", "Giving Advice in a Disaster": "🛡️",
    "Preferences": "❤️", "How often ...?": "🔁", "Imperatives in Recipes": "👩‍🍳",
    "Sequencing Words": "1️⃣", "How much / How many": "🔢",
    "On the Phone": "☎️", "Asking for Help": "🙋", "Giving Instructions": "📋",
    "Internet Safety": "🛡️", "should / shouldn't": "🛡️", "must / mustn't": "⚠️",
    "Comparing Adventures": "⚖️", "Simple Past — Regular": "⏮️",
    "Simple Past — Irregular": "⏮️", "have to / has to": "📋",
    "Passive Voice — Present": "⚙️", "Passive Voice — Past": "🏛️",
}

# The Grade-8 glossary extras arrive from third-party activity banks without
# icons.  Every current card gets an intentional, topic-specific pictogram;
# real, hand-checked photos already linked to a card always take precedence.
VISUALS = {
    # Unit 1 - Friendship / routines
    "weekdays": "📅", "weekend": "🛋️", "write a diary": "📔",
    "come over": "🚪",
    "visit relatives": "👪", "wake up": "⏰", "walk the dog": "🐕",
    "wash face": "🧼", "watch tv": "📺", "water the flowers": "🪴",
    "ride a bike": "🚲", "run errands": "🛍️", "study": "📚",
    "take a course": "🏫", "take a nap": "😴", "take care of a pet": "🐾",
    "life": "🌱", "listen to music": "🎧", "meet friends": "🧑‍🤝‍🧑",
    "noon": "🕛", "play chess": "♟️", "read a book": "📖",
    "have breakfast": "🥞", "have dinner": "🍽️", "have lunch": "🥪",

    # Unit 2 - Teen life
    "hiking": "🥾", "horizon": "🌅", "how often": "🔁",
    "fashionable": "👗", "fast": "🏃", "folk music": "🪕",
    "follow": "👣", "form": "📝", "free time": "🕒", "gym": "🏋️",
    "hate": "😠", "energetic": "⚡", "enjoy": "😊", "enjoyable": "😄",
    "enlarge": "🔍", "exciting": "🤩", "exercise": "🏃",
    "fantasy": "🧚", "fascinating": "✨",

    # Unit 3 - In the kitchen
    "stir": "🥄", "strain": "🥣", "wrap": "🌯", "scoop": "🍨",
    "roll": "🌀", "season": "🧂", "shape": "🔷", "sprinkle": "✨",
    "place": "📍", "preheat": "🔥", "prepare": "👩‍🍳", "put": "👇",
    "remove": "📤", "rinse": "🚿", "roast": "🍗", "knead": "🥖",
    "make it rest": "⏲️", "make the dough": "🥣",
    "melt": "💧",

    # Unit 4 - On the phone
    "conversation": "💬", "customer service": "🎧", "delivery": "📦",
    "device": "📱", "discovery": "🔎", "disturb": "🔕",
    "easy way": "🛣️", "cell phone": "📱", "change": "🔄", "cheap": "🪙",
    "clearly": "🗣️", "communicate": "🗨️", "company": "🏢",
    "confirm": "✅", "badline": "📵", "bad line": "📵", "book": "📖",
    "busy": "🚫", "call": "☎️", "call back": "↩️",

    # Unit 5 - The Internet
    "friend request": "👥", "habit": "🔁", "ignore": "🙈",
    "important": "❗", "improve": "📈", "information": "ℹ️",
    "instant": "⚡", "isolated": "🏝️", "create": "✨", "dangerous": "⚠️",
    "develop": "🛠️", "file": "📄", "find": "🔍", "blog": "✍️",
    "break": "💔", "broken": "🛠️", "check": "✅",

    # Unit 6 - Adventures
    "indoor": "🏠", "inexperienced": "🐣", "goggle": "🥽", "goggles": "🥽",
    "height": "📏", "helmet": "⛑️", "hill": "⛰️",
    "historical sites": "🏛️", "hot air balloon": "🎈", "ice skating": "⛸️",
    "include": "➕", "incredible": "🤯", "individually": "👤",
    "diving suit": "🤿", "equipment": "🎒", "experience": "🗺️",
    "experienced": "🏅", "explore": "🧭", "extreme sport": "🧗",
    "feel": "🙂", "fighting": "🥊",

    # Unit 7 - Tourism
    "taste": "👅", "terrible / awful": "😖", "tradition": "🧿",
    "truly": "💯", "unbelievable / incredible": "🤯", "visit": "📍",
    "rich": "💰", "sightseeing": "🏙️", "summer": "🌻",
    "sunbath": "🏖️", "sunbathe": "🏖️", "sunny": "☀️",
    "mysterious": "🔮", "natural": "🌿", "palace": "🏰",
    "peaceful": "🕊️", "rainy": "🌧️", "relaxing": "😌",
    "heritage": "🏛️", "holiday": "🧳", "hospitable": "🤗",

    # Unit 8 - Chores
    "be good at": "🏅", "be responsible for": "📋", "kitchen chores": "🧹",
    "ignore responsibilities": "🙈", "share the chores": "🤝", "admire": "🌟",
    "be late": "⏰", "feel annoyed": "😠", "feel worried": "😟",
    "feel happy": "😊", "feel relaxed": "😌", "feel exhausted": "😫",
    "feel bored": "😑", "in fact,": "ℹ️", "for example,": "💡",
    "some chores": "🧺", "be happy": "😄", "can’t stand": "😖",
    "can't stand": "😖", "feel so hungry": "🍽️", "before the meal": "⏳",
    "waiting to eat": "⌛", "pay the bills": "🧾", "do the shopping": "🛒",

    # Unit 9 - Science
    "healthcare": "🏥", "improvement": "📊", "infection": "🦠",
    "ink": "🖋️", "electric bulb": "💡", "entertainment": "🎭",
    "explosion": "💥", "facts": "📚", "gain": "📈", "goldsmith": "💍",
    "gravity of the matter": "⚠️", "deserve": "⚖️", "diagnose": "🩺",
    "die": "🪦", "discoverer": "🔍",

    # Unit 10 - Natural forces
    "storm": "⛈️", "eruption": "🌋", "wildfire": "🔥", "lightning": "⚡",
    "thunder": "🌩️", "damage": "🏚️", "rescue team": "🚑",
    "emergency": "🚨", "shelter": "⛺", "warning": "⚠️",
    "aftershock": "📳", "debris": "🧱", "first aid": "🩹", "evacuate": "🚪",
}


def is_number(item):
    return bool(re.fullmatch(r"\d{1,3}", (item.get("tr") or "").strip()))


def example_time(text):
    """Return a canonical 12-hour HH:MM value when a sentence states a time."""
    plain = STAR.sub(BACK + "1", text or "").lower()
    explicit = re.search(r"(?<!\d)([01]?\d|2[0-3]):([0-5]\d)(?!\d)", plain)
    if explicit:
        return "%02d:%s" % (int(explicit.group(1)) % 12 or 12, explicit.group(2))
    hour_words = "|".join(HOURS)
    hit = re.search(r"\bhalf past (" + hour_words + r")\b", plain)
    if hit:
        return "%02d:30" % HOURS[hit.group(1)]
    hit = re.search(r"\bquarter past (" + hour_words + r")\b", plain)
    if hit:
        return "%02d:15" % HOURS[hit.group(1)]
    hit = re.search(r"\bquarter to (" + hour_words + r")\b", plain)
    if hit:
        return "%02d:45" % ((HOURS[hit.group(1)] - 2) % 12 + 1)
    hit = re.search(r"\b(" + hour_words + r") o'clock\b", plain)
    if hit:
        return "%02d:00" % HOURS[hit.group(1)]
    return None


TR_TERM_PATTERNS.update({
 "usually": (r"genellikle",), "often": (r"sık sık",), "sometimes": (r"bazen",), "never": (r"asla",),
 "do you like": (r"sever misin",), "open": (r"\baç\b",), "raise": (r"kaldır",),
 "try on": (r"denerim",), "look": (r"görünüyorsun",), "create": (r"tasarlar",),
 "in": (r"Ocak ayı", r"kışın", r"sabah"), "walks": (r"yürüyerek gider",),
 "are reading": (r"okuyoruz",), "plays": (r"oynar",),
 "are going to": (r"\S+[ae]ca[kğ]\S*", r"\S+[ae]ce[kğ]\S*"),
 "is": (r"orta boylu", r"\S+yor mu", r"\S+[ae]cak mı",),
 "going to": (r"\S+[ae]c[ae]k (?:misin|mı)",),
 "may": (r"\S+[ae]bilir",), "will": (r"\S+[ae]c[ae][kğ]\S*", r"su altında kalır", r"güvende olursun", r"toprak kurur",),
 "would rather": (r"yeğler", r"tercih ederim",),
 "stir": (r"karıştır",), "pour": (r"dök",), "serve": (r"servis et",), "next": (r"Sonra",),
 "speaking": (r"konuşuyorum",), "download": (r"indir",), "log in": (r"giriş yap",),
 "travelled": (r"seyahat ettik",), "enjoyed": (r"keyif aldım",), "bought": (r"aldım",),
 "is recycled": (r"geri dönüştürülür",), "was built": (r"inşa edildi",),
 "why don't we": (r"neden", r"m[ıiuü]yoruz",),
})
TR_TERM_PATTERNS["don't"] += (r"\baçma\b",)


def turkish_highlights(title, english, turkish):
    """Find the Turkish phrases that realize the starred English teaching point."""
    terms = list(dict.fromkeys(m.group(1).strip().lower().rstrip('.!?') for m in STAR.finditer(english or "")))
    if not terms or not turkish:
        return []

    # These are short metalinguistic labels rather than translated sentences.
    # Highlighting the whole label is the honest one-to-one correspondence.
    article_label = (title in ("A / AN / THE", "Countable / Uncountable", "a / an · some · any")
                     and set(terms) <= {"a", "an", "the", "two", "four", "five", "ten"})
    if (re.fullmatch(r"(?:\d+\. kural|tek heceli|iki\+ heceli|düzensiz(?: sıfatlar)?)", turkish, re.I)
            or turkish in ("e ile biten", "sessiz-sesli-sessiz", "sessiz + y")
            or article_label):
        return [turkish]

    found = []
    for term in terms:
        patterns = TR_TERM_PATTERNS.get(term) or TR_TERM_PATTERNS.get(term + '.')
        if not patterns:
            continue
        matches = []
        for pattern in patterns:
            matches.extend(re.finditer(pattern, turkish, re.I))
        if not matches:
            continue
        for match in matches:
            phrase = match.group(0)
            if phrase not in found:
                found.append(phrase)

    # Unknown alignment must never turn an entire sentence orange.
    if STAR.sub('', english or '').strip(' .!?') == '':
        return [turkish]
    return found


def ensure_visuals(slides):
    """Give every vocabulary card a real photo, pictogram or number tile."""
    generic = []
    for slide in slides:
        if slide.get("type") != "vocab":
            continue
        for item in slide.get("items", []):
            if item.get("img"):
                continue
            word = (item.get("en") or "").strip().lower()
            icon = VISUALS.get(word)
            if icon:
                item["emoji"] = icon
                continue
            if (item.get("emoji") and item.get("emoji") != "🧩") or is_number(item):
                continue
            if not icon:
                # This visible fallback makes a newly imported word impossible
                # to miss during QA; verify_lessons.py rejects it.
                icon = "🧩"
                generic.append(item.get("en") or "(blank)")
            item["emoji"] = icon
    return generic


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


def visual_index(slides):
    """English word -> reviewed visual, so every example can show context."""
    out = {}
    for s in slides:
        if s.get("type") == "vocab":
            for it in s.get("items", []):
                visual = {key: it[key] for key in ("img", "emoji", "num", "imageFit", "imageSource", "imageConcept") if key in it}
                if visual:
                    out.setdefault(it["en"].lower(), visual)
    return out


def example_icon(title, text):
    plain = STAR.sub(BACK + "1", text or "").lower()
    for pattern, icon in EXAMPLE_ICON_RULES:
        if re.search(pattern, plain):
            return icon
    return TITLE_ICONS.get(title, "📝")


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
    picture_tasks = []

    if slide.get("type") == "vocab":
        items = [i for i in slide["items"] if i.get("en") and i.get("tr")]
        if len(items) >= 4:
            pairs = rng.sample(items, min(4, len(items)))
            candidates.append({"kind": "match", "q": "Match the words",
                               "pairs": [{"a": p["en"], "b": p["tr"]} for p in pairs]})

        with_pic = [i for i in items if i.get("img")]
        unique_pictures = list({i["img"]: i for i in with_pic}.values())
        for target in rng.sample(unique_pictures, min(3, len(unique_pictures))):
            others = list(dict.fromkeys(i["en"] for i in items if i is not target
                and i.get("img") != target["img"] and i.get("tr") != target.get("tr")))
            if not others:
                continue
            picture_tasks.append({
                "kind": "picture", "q": "Which word matches the picture?", "img": target["img"],
                "imageFit": target.get("imageFit", "contain"),
                "imageSource": target.get("imageSource", ""),
                "answer": target["en"], "tr": target["tr"],
                "options": [target["en"]] + rng.sample(others, min(3, len(others))),
            })
        candidates.extend(picture_tasks[:1])

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
            alternatives = [other for other, _ in found if other is not e and other.get("tr")]
            truth = not alternatives or variant % 2 == 0
            # Keep the English sentence intact. Replacing an auxiliary with an
            # unrelated highlighted word used to create broken text such as
            # "go Mert go ...". A false item now pairs a valid sentence with a
            # different meaning instead.
            shown_tr = e.get("tr", "") if truth else alternatives[0].get("tr", "")
            candidates.append({
                "kind": "truefalse", "q": "Does the sentence match the meaning?",
                "statement": plain + (" — " + shown_tr if shown_tr else ""),
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
    shown = {t.get("img") for t in tasks if t["kind"] == "picture"}
    tasks.extend(t for t in picture_tasks if t["img"] not in shown)
    if not tasks:
        return []
    return [{
        "type": "exercise",
        "title": "Activity Break · " + task.get("q", "Complete the sentence"),
        "titleTr": "Use what you just learned · " + slide.get("title", ""),
        "tasks": [task],
    } for task in tasks]


def visual_item(item):
    """Small, stable payload shared by all three end-of-unit missions."""
    return {k: item[k] for k in ("en", "tr", "img", "emoji", "num", "imageFit", "imageSource", "imageConcept") if k in item}


def audio_name(word):
    return re.sub(r"[^a-z0-9]+", "-", word.lower()).strip("-") + ".wav"


def mission_sentences(slides):
    """Grammatically complete unit examples suitable for draggable ordering."""
    found = []
    for slide in slides:
        pools = list(slide.get("examples") or [])
        for col in slide.get("columns") or []:
            pools += col.get("examples") or []
        for example in pools:
            sentence = STAR.sub(r"\1", example.get("en", "")).strip()
            words = sentence.split()
            if not 4 <= len(words) <= 11 or "→" in sentence:
                continue
            key = sentence.lower()
            if any(old["answer"].lower() == key for old in found):
                continue
            found.append({"answer": sentence, "tr": example.get("tr", "")})
    return found


def make_missions(slides, rng):
    """Three substantial unit-final activities: see, hear, then construct."""
    words, seen = [], set()
    for slide in slides:
        if slide.get("type") != "vocab":
            continue
        for item in slide.get("items", []):
            key = (item.get("en") or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            words.append(visual_item(item))

    if len(words) < 4:
        return []
    photos = [w for w in words if w.get("img")]
    pictograms = [w for w in words if not w.get("img")]
    rng.shuffle(photos)
    rng.shuffle(pictograms)
    mixed = photos + pictograms
    first = mixed[:4]
    remaining = [w for w in mixed if w not in first]
    second = (remaining + first)[:4]
    for item in second:
        item["audio"] = "/app/audio/words/" + audio_name(item["en"])

    sentences = mission_sentences(slides)
    rng.shuffle(sentences)
    sentences = sentences[:3]
    if not sentences:
        # Every current unit has sentence examples, but retain a useful mission
        # if a future vocabulary-only unit is imported.
        sentences = [{
            "answer": "I can use %s in a sentence." % words[0]["en"],
            "tr": "%s kelimesini bir cümlede kullanabilirim." % words[0]["en"],
        }]

    return [
        {
            "type": "mission", "part": [1, 3],
            "title": "Unit Mission · Picture Dock",
            "titleTr": "Resimleri doğru İngilizce kelimelere sürükle.",
            "task": {"kind": "dragmatch", "q": "Drag each picture to its word.",
                     "items": first},
        },
        {
            "type": "mission", "part": [2, 3],
            "title": "Unit Mission · Listen & Find",
            "titleTr": "Dinle, doğru resmi bul ve dört turu tamamla.",
            "task": {"kind": "listenpicture", "q": "Listen, then choose the picture.",
                     "items": second},
        },
        {
            "type": "mission", "part": [3, 3],
            "title": "Unit Mission · Sentence Workshop",
            "titleTr": "Kelime parçalarını sürükleyerek ünite cümlelerini kur.",
            "task": {"kind": "dragorder", "q": "Drag the words into the correct order.",
                     "sentences": sentences},
        },
    ]


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

    body = [s for s in body if s["type"] not in ("exercise", "mission")]  # regenerate them
    from lesson_pacing import restore_teaching, pace_teaching, extra_missions
    body = restore_teaching(body)
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
    from lesson_examples import EXAMPLES
    for section in body:
        if section["type"] not in ("grammar", "compare"):
            continue
        known = {e["en"] for e in section.get("examples", [])}
        for en, tr in EXAMPLES.get(section.get("title"), []):
            if en not in known:
                section.setdefault("examples", []).append({"en": en, "tr": tr})
                known.add(en)
    generic_visuals = ensure_visuals(body)
    visuals = visual_index(body)
    thin = []
    out = []
    activity_no = 0
    for s in body:
        # a picture next to an example makes the rule concrete
        pools = list(s.get("examples") or [])
        for col in s.get("columns") or []:
            pools += col.get("examples") or []
        for e in pools:
            clock = example_time(e.get("en"))
            if clock:
                e["time"] = clock
                e.pop("img", None)
                e.pop("emoji", None)
                e.pop("num", None)
            else:
                e.pop("time", None)
            e["trEm"] = turkish_highlights(s.get("title"), e.get("en"), e.get("tr"))
            plain = STAR.sub(BACK+"1", e.get("en", "")).lower()
            hit = max((w for w in visuals if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", plain)),
                      key=len, default=None)
            if (not e.get("img") or e.get("imageSource") == "ARASAAC") and not e.get("time"):
                e.pop("emoji", None)
                e.pop("num", None)
                if hit:
                    e.update(visuals[hit])
                else:
                    e["emoji"] = example_icon(s.get("title"), e.get("en"))
        if s["type"] in ("grammar", "compare") and len(pools) < 3:
            thin.append(s.get("title"))
        # digits render as keycaps instead of the unreadable numbers emoji
        if s["type"] == "vocab":
            for it in s["items"]:
                if is_number(it):
                    it["num"] = it["tr"]
                    it.pop("emoji", None)
        out.extend(split_cards(s) if s["type"] == "vocab" else pace_teaching(s))
        if s["type"] not in ("practice", "exercise"):
            activities = make_exercise(s, rng, activity_no)
            out.extend(activities)
            if activities:
                activity_no += 1

    out.extend(make_missions(body, rng))
    out.extend(extra_missions(body, rng))
    missions = [s for s in out if s["type"] == "mission"]
    for n, mission in enumerate(missions, 1):
        mission["part"] = [n, len(missions)]
    # Pacing adds examples too; align every final example after pagination.
    for page in out:
        for example in page.get("examples", []):
            example["trEm"] = turkish_highlights(page.get("title"), example.get("en"), example.get("tr"))
    data["slides"] = head + out + tail
    if not dry:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)

    print("  %s  %2d slayt -> %2d  (cikarilan: %s)"
          % (unit, len(slides), len(data["slides"]), ", ".join(dropped) or "-"))
    if thin:
        print("     az ornekli (<3): %s" % ", ".join(thin))
    if generic_visuals:
        print("     genel gorsel (duzeltilmeli): %s" % ", ".join(generic_visuals))


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
