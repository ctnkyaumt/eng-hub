"""Probe for LGS section, sources, routing, sections/subsections, search filtering, and server delivery."""
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

# 1. Check lgs-sources.json
data_path = ROOT / "app/data/lgs-sources.json"
assert data_path.exists(), "lgs-sources.json must exist"
data = json.loads(data_path.read_text(encoding="utf-8"))

assert "sources" in data, "lgs-sources.json missing 'sources'"
assert "counts" in data, "lgs-sources.json missing 'counts'"
assert "hubUrls" in data, "lgs-sources.json missing 'hubUrls'"

# Required URLs from user request
req_urls = [
    "https://www.ingilizceciyiz.com/lgs-ingilizce-ornek-sorular/",
    "https://www.ingilizceciyiz.com/lgs-ingilizce-deneme-sinavlari/",
    "https://www.ingilizceciyiz.com/lgs-ingilizce-sorulari/",
    "https://www.dersingilizce.org/lgsfiles",
]
found_urls = set()
for s in data["sources"]:
    if s.get("sourceUrl"):
        found_urls.add(s["sourceUrl"])
    if s.get("hubUrl"):
        found_urls.add(s["hubUrl"])

for u in req_urls:
    assert u in found_urls, f"Required source URL not found in lgs sources: {u}"

# Verify providers
sources_by_id = {s["id"]: s for s in data["sources"]}
assert "ingilizceciyiz-ornek" in sources_by_id
assert "ingilizceciyiz-deneme" in sources_by_id
assert "ingilizceciyiz-cikmis" in sources_by_id
assert "dersingilizce-cikmis" in sources_by_id
assert "dersingilizce-ornek" in sources_by_id
assert "dersingilizce-deneme" in sources_by_id
assert "dersingilizce-kelime" in sources_by_id
assert "dersingilizce-online" in sources_by_id
assert "dersingilizce-worksheets" in sources_by_id

# Verify item counts
total = sum(len(s["items"]) for s in data["sources"])
assert total >= 200, f"Expected >= 200 items, got {total}"
assert len(sources_by_id["ingilizceciyiz-ornek"]["items"]) >= 40
assert len(sources_by_id["ingilizceciyiz-deneme"]["items"]) >= 75
assert len(sources_by_id["ingilizceciyiz-cikmis"]["items"]) == 9  # 2018-2026
assert len(sources_by_id["dersingilizce-cikmis"]["items"]) == 9   # 2018-2026
assert len(sources_by_id["dersingilizce-ornek"]["items"]) >= 10
assert len(sources_by_id["dersingilizce-worksheets"]["items"]) >= 35

# Check section headings in ingilizceciyiz-deneme
deneme_sections = set(it.get("section") for it in sources_by_id["ingilizceciyiz-deneme"]["items"])
assert "8. Sınıf İngilizce Sarmal Deneme Sınavları" in deneme_sections, "Missing Sarmal Deneme section"
assert "8. Sınıf İngilizce Ünite Deneme Sınavları" in deneme_sections, "Missing Ünite Deneme section"
assert any("Genel" in s for s in deneme_sections), "Missing Genel Deneme section"

# Check that NO item is titled "Star"
for s in data["sources"]:
    for it in s["items"]:
        assert it.get("title"), f"Missing title in {s['id']}"
        assert it["title"].strip().lower() != "star", f"Found invalid 'Star' title in {s['id']}"
        assert it.get("link"), f"Missing link in {s['id']}"
        assert it["link"].startswith("http"), f"Invalid link in {s['id']}: {it['link']}"
        assert it.get("source"), f"Missing source in {s['id']}"
        assert it.get("section"), f"Missing section heading in {s['id']}: {it['title']}"

# 2. Check app.js routing and home screen
app_js = (ROOT / "app/js/app.js").read_text(encoding="utf-8")
assert "lgsScreen" in app_js, "app.js must import/define lgsScreen"
assert "go(\"#/lgs\")" in app_js or "go('#/lgs')" in app_js, "app.js must navigate to #/lgs"
assert "LGS" in app_js, "app.js home screen must feature LGS section"

# 3. Check store.js
store_js = (ROOT / "app/js/store.js").read_text(encoding="utf-8")
assert "getLgsSources" in store_js, "store.js must export getLgsSources"
assert "lgs-sources.json" in store_js, "store.js must load lgs-sources.json"

# 4. Check lgs.js
lgs_js_path = ROOT / "app/js/lgs.js"
assert lgs_js_path.exists(), "app/js/lgs.js must exist"
lgs_js = lgs_js_path.read_text(encoding="utf-8")
assert "export async function lgsScreen" in lgs_js
assert "resource-search" in lgs_js
assert "lgs-section-heading" in lgs_js
assert "lgs-pill" in lgs_js
assert "updateVisibility" in lgs_js
assert "normText" in lgs_js

# 5. Check CSS for hidden override and LGS pill/section styling
app_css = (ROOT / "app/css/app.css").read_text(encoding="utf-8")
assert "lgs-section-heading" in app_css, "app.css missing lgs-section-heading"
assert "lgs-pill" in app_css, "app.css missing lgs-pill"
assert "[hidden]" in app_css and "!important" in app_css, "app.css must have [hidden] with !important"

# 6. Test with local server
server_proc = subprocess.Popen([sys.executable, "server/enghub.py", "--no-browser"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(1.2)
try:
    for endpoint in ["/app/data/lgs-sources.json", "/app/js/lgs.js", "/app/js/store.js", "/app/js/app.js", "/app/css/app.css"]:
        req = urllib.request.Request(f"http://127.0.0.1:8777{endpoint}")
        with urllib.request.urlopen(req, timeout=5) as res:
            assert res.status == 200, f"Server returned {res.status} for {endpoint}"
            body = res.read()
            assert len(body) > 0, f"Empty response for {endpoint}"
            if endpoint == "/app/data/lgs-sources.json":
                parsed = json.loads(body.decode("utf-8"))
                assert len(parsed["sources"]) >= 9
finally:
    server_proc.terminate()
    server_proc.wait(timeout=3)

print(f"PASS: LGS probe successful. {len(data['sources'])} categories, {total} total resources verified with sections & search.")
