"""Python probe verifying book presentation cover images, data integrity and UI.

Run: python tools/probe_books.py
"""
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_PATH = os.path.join(ROOT, "app", "data", "books.json")
CATALOG_PATH = os.path.join(ROOT, "app", "data", "catalog.json")
JS_PATH = os.path.join(ROOT, "app", "js", "books.js")
CSS_PATH = os.path.join(ROOT, "app", "css", "app.css")

# 1. Verify books.json structure and cover images
assert os.path.isfile(BOOKS_PATH), "books.json not found"
with open(BOOKS_PATH, encoding="utf-8") as f:
    books_data = json.load(f)

assert len(books_data) > 0, "books.json is empty"

# Verify g6/revision specifically (the user's explicit example)
g6_rev = books_data.get("g6/revision", [])
assert len(g6_rev) >= 5, f"g6/revision expected >=5 books, got {len(g6_rev)}"
first_book = g6_rev[0]
assert first_book.get("title") == "My Teacher Workbook 6 - Revision"
assert "coverImage" in first_book and first_book["coverImage"].startswith("https://eltarena.com/uploads/")
assert "1788368364503_c5caf5062c36440d.webp" in first_book["coverImage"]
print(f"Verified g6/revision book 1 cover: {first_book['coverImage']}")

# Verify g6/u1 supplemental Buddy 6 cover
g6_u1 = books_data.get("g6/u1", [])
buddy = [b for b in g6_u1 if "Buddy 6" in b.get("title", "")]
assert len(buddy) == 1, "Buddy 6 not found in g6/u1"
assert buddy[0].get("coverImage") == "https://forenelt.idea-host.com/buddy6/theme1/files/thumb/1.jpg"
print(f"Verified Buddy 6 cover: {buddy[0]['coverImage']}")

# Verify overall coverage
total_books = sum(len(items) for items in books_data.values())
with_cover = sum(len([b for b in items if b.get("coverImage")]) for items in books_data.values())
coverage_pct = (with_cover / total_books) * 100
assert coverage_pct > 85, f"Expected >85% cover coverage, got {coverage_pct:.1f}%"
print(f"Verified book presentation coverage: {with_cover}/{total_books} ({coverage_pct:.1f}%) have cover images")

# 2. Verify books.js UI code matches eltarena structure & user selector
with open(JS_PATH, encoding="utf-8") as f:
    js_code = f.read()

# Selector components from user request:
# section > div.grid.grid-cols-2.gap-3.sm:gap-4.md:grid-cols-3.lg:grid-cols-4.xl:grid-cols-5 > article:nth-child(1) > button > img.relative.z-[1].h-full.w-full.object-cover.object-top.transition-transform.duration-300.group-hover:scale-[1.03].motion-reduce:transition-none.motion-reduce:group-hover:scale-100
assert 'section' in js_code
assert 'grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5' in js_code
assert 'article' in js_code
assert 'book-card' in js_code
assert 'book-thumb' in js_code
assert 'relative z-[1] h-full w-full object-cover object-top transition-transform duration-300 group-hover:scale-[1.03] motion-reduce:transition-none motion-reduce:group-hover:scale-100' in js_code
assert 'renderBookCard' in js_code
assert 'addEventListener("error"' in js_code, "Missing fallback image error handling"
print("Verified app/js/books.js DOM structure and selector alignment.")

# 3. Verify app/css/app.css has all required styling
with open(CSS_PATH, encoding="utf-8") as f:
    css_code = f.read()

assert '.book-grid' in css_code
assert '.card.book-card' in css_code
assert '.book-thumb' in css_code
assert 'aspect-ratio: 3 / 4' in css_code
assert '.book-cover-img' in css_code
assert '.book-thumb-fallback' in css_code
assert '.book-badge-type' in css_code
assert '.book-badge-online' in css_code
print("Verified app/css/app.css style declarations.")

# 4. Network probe: verify sample cover images load (HTTP 200)
headers = {"User-Agent": "Mozilla/5.0"}
sample_urls = [
    first_book["coverImage"],
    buddy[0]["coverImage"],
]
for url in sample_urls:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        assert resp.status == 200, f"Failed to load image: {url} status {resp.status}"
        data = resp.read()
        assert len(data) > 1000, f"Image file too small ({len(data)} bytes): {url}"
print(f"Verified network HTTP 200 on sample covers ({len(sample_urls)} checked).")

# 5. Server probe: verify local server serves updated files
import subprocess
import time

server_proc = subprocess.Popen([sys.executable, "server/enghub.py", "--no-browser"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(1.2)
try:
    for endpoint in ["/app/data/books.json", "/app/js/books.js", "/app/css/app.css"]:
        req = urllib.request.Request(f"http://127.0.0.1:8777{endpoint}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200, f"Server returned {resp.status} for {endpoint}"
            assert len(resp.read()) > 0, f"Server returned empty body for {endpoint}"
    print("Verified local HTTP server serves books.json, books.js, and app.css with 200 OK.")
finally:
    server_proc.terminate()

print("ALL BOOK PROBES PASSED!")
