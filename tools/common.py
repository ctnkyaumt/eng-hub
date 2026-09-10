"""Shared helpers for the ENG HUB build tools."""

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
CACHE = os.path.join(TOOLS, "cache")
LOGS = os.path.join(TOOLS, "logs")
CONTENT = os.path.join(ROOT, "content")
DATA = os.path.join(ROOT, "app", "data")

API = "https://eltarena.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Grades we build. eltarena unit ids are looked up by their "N. ÜNİTE" title.
GRADES = [5, 6, 7, 8]
UNITS_PER_GRADE = 10

# Theme names per grade/unit. Grade 5 comes from the MEB Maarif theme sheets in
# res/; grades 6-8 from the unit titles used across the source material.
THEMES = {
    5: {
        1: ("School Life", "Okul Hayatı", "🏫"),
        2: ("Classroom Life", "Sınıf Hayatı", "✏️"),
        3: ("Personal Life", "Kişisel Hayat", "🙋"),
        4: ("Family Life", "Aile Hayatı", "👨‍👩‍👧"),
        5: ("Life in the Neighbourhood & City", "Mahalle ve Şehir Hayatı", "🏙️"),
        6: ("Life in the World", "Dünyada Hayat", "🌍"),
        7: ("Life in Nature", "Doğada Hayat", "🌳"),
        8: ("Life in the Universe & Future", "Evren ve Gelecek", "🚀"),
    },
    6: {
        1: ("School Life", "Okul Hayatı", "🏫"),
        2: ("Classroom Life", "Sınıf Hayatı", "✏️"),
        3: ("Personal Life", "Kişisel Hayat", "🙋"),
        4: ("Family Life", "Aile Hayatı", "👨‍👩‍👧"),
        5: ("Life in the Neighbourhood & City", "Mahalle ve Şehir Hayatı", "🏙️"),
        6: ("Life in the World & Culture", "Dünya ve Kültür Hayatı", "🌍"),
        7: ("Life in Nature & Global Problems", "Doğada Hayat ve Küresel Sorunlar", "🌳"),
        8: ("Life in the Universe & Future", "Evren ve Gelecekte Hayat", "🚀"),
    },
    7: {
        1: ("Appearance and Personality", "Görünüş ve Kişilik", "🧑‍🎤"),
        2: ("Sports", "Spor", "⚽"),
        3: ("Biographies", "Biyografiler", "📜"),
        4: ("Wild Animals", "Vahşi Hayvanlar", "🦁"),
        5: ("Television", "Televizyon", "📺"),
        6: ("Celebrations", "Kutlamalar", "🎉"),
        7: ("Dreams", "Hayaller", "💭"),
        8: ("Public Buildings", "Kamu Binaları", "🏛️"),
        9: ("Environment", "Çevre", "🌱"),
        10: ("Planets", "Gezegenler", "🪐"),
    },
    8: {
        1: ("Friendship", "Arkadaşlık", "🤝"),
        2: ("Teen Life", "Gençlik Hayatı", "🎧"),
        3: ("In the Kitchen", "Mutfakta", "🍲"),
        4: ("On the Phone", "Telefonda", "📞"),
        5: ("The Internet", "İnternet", "🌐"),
        6: ("Adventures", "Maceralar", "🧗"),
        7: ("Tourism", "Turizm", "🧳"),
        8: ("Chores", "Ev İşleri", "🧹"),
        9: ("Science", "Bilim", "🔬"),
        10: ("Natural Forces", "Doğa Güçleri", "🌋"),
    },
}

OFFLINE_GAME_HOST = "etkinlik.app"


def ensure(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)


def http_get(url, timeout=60, retries=3, headers=None, binary=False):
    """GET with a browser UA; returns bytes or text. Raises on final failure."""
    ctx = ssl.create_default_context()
    hdrs = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "tr,en;q=0.8"}
    hdrs.update(headers or {})
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                raw = r.read()
                return (raw, r) if binary else raw.decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001 - network is messy by nature
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise last


def get_json(url, **kw):
    return json.loads(http_get(url, **kw))


def load_grades(refresh=False):
    """The whole eltarena catalog, cached on disk so reruns are offline-safe."""
    ensure(CACHE)
    path = os.path.join(CACHE, "grades.json")
    if os.path.exists(path) and not refresh:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    data = get_json(API + "/api/grades")
    if not isinstance(data, list) or any(not source_units(data).get(g) for g in GRADES):
        raise ValueError("Incomplete source catalog; keeping the previous snapshot")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return data


def source_units(grades_json):
    """{grade_no: {unit_no: source_unit_dict}} for the grades we care about."""
    out = {}
    for g in grades_json:
        m = re.match(r"^(\d+)\.\s*Sınıf$", g.get("title", "").strip())
        if not m:
            continue
        no = int(m.group(1))
        if no not in GRADES:
            continue
        units = {}
        for u in g.get("units", []):
            um = re.match(r"^(\d+)\.\s*(?:ÜNİTE|TEMA)$", u.get("title", "").strip())
            if um:
                units[int(um.group(1))] = u
        out[no] = units
    return out


SAFE = re.compile(r"[^0-9A-Za-zÇĞİÖŞÜçğıöşü ._-]+")


def safe_name(text, maxlen=90):
    text = SAFE.sub("", (text or "").strip()).strip(" ._-")
    text = re.sub(r"\s+", " ", text)
    return (text[:maxlen] or "dosya").strip()


def drive_id(url):
    """Extract a Google Drive file id from any of its link shapes."""
    for pat in (r"/file/d/([-\w]{20,})", r"[?&]id=([-\w]{20,})", r"/d/([-\w]{20,})"):
        m = re.search(pat, url or "")
        if m:
            return m.group(1)
    return None


def log(name, msg):
    ensure(LOGS)
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + msg
    with open(os.path.join(LOGS, name), "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(msg)


def progress(i, total, label=""):
    pct = (i / total * 100) if total else 100
    sys.stdout.write("\r  [%-28s] %5.1f%% %s" % ("#" * int(pct / 3.6), pct, label[:46].ljust(46)))
    sys.stdout.flush()
    if i >= total:
        sys.stdout.write("\n")
