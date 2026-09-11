#!/usr/bin/env python3
"""Take offline copies of the source's *static* web activities.

Several activities on eltarena are plain static pages (GitHub Pages / Netlify):
quiz games, "Bil ve Fethet" boards, slide-style unit presentations. Those can be
mirrored onto the USB and played with no internet at all.

Run:  python tools/mirror_sites.py [--grade 5] [--unit 1] [--force]

content/<grade>/<unit>/sites/<slug>/…            the copied page + assets
content/<grade>/<unit>/sites/manifest.json       what was copied and what it is

Dynamic platforms (wordwall, baamboozle, vocablitz, kahoot) are not mirrorable
and stay online links in the UI.
"""

import argparse
import json
import os
import posixpath
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, DATA, ensure, http_get, log, progress, safe_name  # noqa: E402

MIRRORABLE = (
    "rgbenglish.github.io",
    "canbay.netlify.app",
    "canbayelt.com",
    "6thgradersunit1wordwarsgeneral.netlify.app",
)
# eltarena hosts the book presentations as plain static sites, but they are slide
# players with hundreds of runtime-built assets: copying one takes many minutes
# and half-copied ones just fail to open. They stay online links unless --presentations.
MIRRORABLE_PATHS = (("eltarena.com", "/uploads/SUNUMLAR/"),)


def mirrorable(url):
    p = urllib.parse.urlparse(url or "")
    if p.hostname in MIRRORABLE:
        return True
    return any(p.hostname == h and p.path.startswith(pre) for h, pre in MIRRORABLE_PATHS)

ASSET_RE = re.compile(
    r"""(?:src|href|data-src|poster)\s*=\s*["']([^"'>]+)["']|url\(\s*["']?([^"')]+)["']?\s*\)""",
    re.I,
)
TEXTUAL = (".html", ".htm", ".css", ".js", ".json", ".svg", "")
SKIP_EXT = (".mp4", ".webm", ".zip", ".pdf")
MAX_FILES = 1200


def slug_for(url, title):
    p = urllib.parse.urlparse(url)
    path = p.path.rstrip("/")
    base = posixpath.basename(path)
    if "." in base:  # .../5REGULAR2NEW2/index.html -> 5REGULAR2NEW2
        base = posixpath.basename(posixpath.dirname(path))
    return safe_name(base or p.hostname.split(".")[0] or title, 60).replace(" ", "-").lower()


def kind_for(url, title):
    t = (url + " " + title).lower()
    if "/sunu" in t or "sunum" in t or "presentation" in t:
        return "presentation"
    return "game"


class Mirror:
    """Copy one static site into `dest`, keeping paths relative to its root."""

    def __init__(self, root_url, dest):
        p = urllib.parse.urlparse(root_url)
        self.origin = "%s://%s" % (p.scheme, p.netloc)
        # site root = the directory the entry page lives in
        self.base_path = p.path if p.path.endswith("/") else posixpath.dirname(p.path) + "/"
        self.dest = dest
        self.seen = set()
        self.count = 0
        self.failures = []

    def local_of(self, abs_url):
        """Path inside dest for an absolute same-origin URL, or None if outside."""
        p = urllib.parse.urlparse(abs_url)
        if "%s://%s" % (p.scheme, p.netloc) != self.origin:
            return None
        path = p.path
        if not path.startswith(self.base_path):
            # asset lives above the entry directory - keep it under _root/
            rel = "_root/" + path.lstrip("/")
        else:
            rel = path[len(self.base_path):]
        if not rel or rel.endswith("/"):
            rel += "index.html"
        return rel

    def rewrite(self, text, cur_rel):
        """Point absolute same-origin URLs at our local copy."""
        depth = cur_rel.count("/")
        up = "../" * depth

        def fix(m):
            raw = m.group(1) or m.group(2)
            if not raw or raw.startswith(("data:", "#", "mailto:", "javascript:")):
                return m.group(0)
            if raw.startswith(("http://", "https://", "//")):
                absu = ("https:" + raw) if raw.startswith("//") else raw
                loc = self.local_of(absu)
                if not loc:
                    return m.group(0)
                new = up + loc
            elif raw.startswith("/"):
                loc = self.local_of(self.origin + raw)
                if not loc:
                    return m.group(0)
                new = up + loc
            else:
                return m.group(0)
            return m.group(0).replace(raw, new)

        return ASSET_RE.sub(fix, text)

    def crawl(self, url, rel=None, depth=0, retries=2):
        if self.count >= MAX_FILES or depth > 3:
            return
        url = url.split("#")[0]
        if url in self.seen:
            return
        self.seen.add(url)

        rel = rel or self.local_of(url) or "index.html"
        ext = os.path.splitext(rel)[1].lower()
        if ext in SKIP_EXT:
            return

        try:
            raw, resp = http_get(url, timeout=45, retries=retries, binary=True)
        except Exception as exc:  # noqa: BLE001
            self.failures.append(url)
            log("mirror.log", "  eksik %s (%s)" % (url, exc))
            return

        ctype = (resp.headers.get("Content-Type") or "").lower()
        is_text = ext in TEXTUAL or "text" in ctype or "javascript" in ctype or "json" in ctype
        out = os.path.join(self.dest, rel.replace("/", os.sep))
        ensure(os.path.dirname(out))
        self.count += 1

        if not is_text:
            with open(out, "wb") as f:
                f.write(raw)
            return

        text = raw.decode("utf-8", "replace")
        links = []
        if ext in (".html", ".htm", "") or "html" in ctype:
            for m in ASSET_RE.finditer(text):
                links.append(m.group(1) or m.group(2))
            text = self.rewrite(text, rel)
        elif ext == ".css":
            for m in ASSET_RE.finditer(text):
                links.append(m.group(1) or m.group(2))
            text = self.rewrite(text, rel)

        with open(out, "w", encoding="utf-8") as f:
            f.write(text)

        for href in links:
            if not href or href.startswith(("data:", "#", "mailto:", "javascript:")):
                continue
            absu = urllib.parse.urljoin(url, href).split("#")[0]
            if self.local_of(absu):
                self.crawl(absu, depth=depth + 1)


ASSET_IN_JS = re.compile(r"""["']([\w./\-]+\.(?:png|jpg|jpeg|gif|svg|webp|mp3|mp4|css|js|json))["']""", re.I)
MAX_SLIDES = 400


def probe_slides(m, base_url):
    """iSpring-style exports build their data/slideN.js paths at runtime, so the
    HTML never mentions them - probe for the numbered files, then pull in every
    picture those slide scripts name."""
    if not os.path.isfile(os.path.join(m.dest, "data", "player.js")):
        return 0

    misses, n, got = 0, 1, 0
    while misses < 3 and n < MAX_SLIDES:
        found = False
        for ext in ("js", "css"):
            rel = "data/slide%d.%s" % (n, ext)
            before = m.count
            m.crawl(urllib.parse.urljoin(base_url, rel), rel=rel, retries=1)
            found = found or m.count > before
        misses = 0 if found else misses + 1
        got += bool(found)
        n += 1

    data_dir = os.path.join(m.dest, "data")
    names = set()
    for fn in os.listdir(data_dir) if os.path.isdir(data_dir) else []:
        if fn.endswith((".js", ".css")):
            with open(os.path.join(data_dir, fn), encoding="utf-8", errors="replace") as f:
                names.update(ASSET_IN_JS.findall(f.read()))
    for name in names:
        if name.startswith(("http", "//", "data:")):
            continue
        rel = name if name.startswith("data/") else "data/" + name.lstrip("./")
        if not os.path.isfile(os.path.join(m.dest, rel.replace("/", os.sep))):
            m.crawl(urllib.parse.urljoin(base_url, rel), rel=rel, retries=1)
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", type=int)
    ap.add_argument("--unit", type=int)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--presentations", action="store_true",
                    help="slayt oynaticili sunumlari da kopyala (yavas, yuz MB'lar)")
    args = ap.parse_args()

    with open(os.path.join(DATA, "source-index.json"), encoding="utf-8") as f:
        src = json.load(f)

    keys = sorted(src, key=lambda k: (int(k[1]), 0 if k.endswith("/revision") else int(k.split("/")[1][1:])))
    if args.grade:
        keys = [k for k in keys if k.startswith("g%d/" % args.grade)]
    if args.unit:
        keys = [k for k in keys if k.endswith("/u%d" % args.unit)]

    jobs = []
    for key in keys:
        authored_path = os.path.join(CONTENT, key, "games", "bank.json")
        if key.startswith("g6/") and os.path.isfile(authored_path):
            with open(authored_path, encoding="utf-8") as f:
                bank = json.load(f)
            if bank.get("authored") and bank.get("curriculum") == "meb-english-6-2026":
                continue
        pool = (src[key]["worksheets"] + src[key]["onlineGames"]
                + src[key]["extras"] + src[key].get("books", []))
        seen_links = set()
        for it in pool:
            if it["link"] in seen_links or not mirrorable(it["link"]):
                continue
            if not args.presentations and kind_for(it["link"], it["title"]) == "presentation":
                continue
            seen_links.add(it["link"])
            jobs.append((key, it))

    print("%d statik etkinlik kopyalanacak\n" % len(jobs))
    done = ok = fail = 0
    per_unit = {}

    for key, it in jobs:
        done += 1
        gid, uid = key.split("/")
        slug = slug_for(it["link"], it["title"])
        dest = os.path.join(CONTENT, gid, uid, "sites", slug)
        entry = {
            "title": it["title"], "by": it.get("by", ""), "link": it["link"],
            "slug": slug, "kind": kind_for(it["link"], it["title"]),
        }
        progress(done, len(jobs), "%s %s" % (key, slug))

        if os.path.isfile(os.path.join(dest, "index.html")) and not args.force:
            entry["path"] = slug + "/index.html"
            per_unit.setdefault(key, []).append(entry)
            continue

        m = Mirror(it["link"], dest)
        try:
            m.crawl(it["link"])
            probe_slides(m, it["link"])
        except Exception as exc:  # noqa: BLE001
            log("mirror.log", "HATA %s %s -> %s" % (key, it["link"], exc))
        if os.path.isfile(os.path.join(dest, "index.html")):
            entry["path"] = slug + "/index.html"
            entry["files"] = m.count
            ok += 1
        else:
            log("mirror.log", "BOS %s %s" % (key, it["link"]))
            fail += 1
        per_unit.setdefault(key, []).append(entry)

    for key, items in per_unit.items():
        gid, uid = key.split("/")
        d = os.path.join(CONTENT, gid, uid, "sites")
        ensure(d)
        with open(os.path.join(d, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump({"items": items}, f, ensure_ascii=False, indent=1)

    print("\nkopyalanan: %d  basarisiz: %d" % (ok, fail))


if __name__ == "__main__":
    main()
