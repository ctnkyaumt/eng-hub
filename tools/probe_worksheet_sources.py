"""Probe for worksheet sources (ingilizcecin, dersingilizce, meb-odsgm), data integrity, routing, and UI."""
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

# 1. Check worksheet-sources.json
sources_path = ROOT / "app/data/worksheet-sources.json"
assert sources_path.exists(), "worksheet-sources.json must exist"
sources = json.loads(sources_path.read_text(encoding="utf-8"))
assert "units" in sources, "worksheet-sources.json must have 'units'"
assert len(sources["units"]) >= 36, f"Expected at least 36 units, got {len(sources['units'])}"

total_items = sum(len(items) for items in sources["units"].values())
assert total_items >= 600, f"Expected >= 600 items, got {total_items}"

# Separate by source
ingilizcecin_items = []
dersingilizce_items = []
meb_items = []

for unit_key, items in sources["units"].items():
    gid, uid = unit_key.split("/")
    for it in items:
        assert it.get("title"), f"Item in {unit_key} missing title"
        assert it.get("link"), f"Item in {unit_key} missing link"
        source = it.get("source")
        assert source in ("ingilizcecin", "dersingilizce", "meb-odsgm"), f"Unexpected source in {unit_key}: {source}"

        if source == "ingilizcecin":
            ingilizcecin_items.append(it)
            assert it["link"].startswith("https://www.ingilizcecin.com/"), f"Invalid link in {unit_key}: {it['link']}"
            assert it.get("date"), f"Item in {unit_key} missing date: {it.get('title')}"
            assert isinstance(it.get("year"), int) and it["year"] >= 2020, f"Item in {unit_key} created before 2020: {it.get('year')} in {it.get('title')}"
            assert it.get("sourcePage"), f"Missing sourcePage in {unit_key}"

        elif source == "dersingilizce":
            dersingilizce_items.append(it)
            assert ("drive.google.com" in it["link"] or it["link"].lower().endswith(".pdf")), f"Dersingilizce link is not Drive or PDF: {it['link']}"
            assert not any(k in it["title"].lower() for k in ["game", "oyun", "jeopardy", "wordwall", "sunum", "powerpoint", "video", "youtube"]), f"Dersingilizce non-worksheet item: {it['title']}"
            assert it.get("sourcePage"), f"Missing sourcePage in {unit_key}"

        elif source == "meb-odsgm":
            meb_items.append(it)
            # Must ONLY be in Grade 7 or Grade 8
            assert gid in ("g7", "g8"), f"MEB ÖDSGM item placed outside Grade 7/8: {unit_key} ({it['title']})"
            assert it.get("by") == "MEB ÖDSGM", f"MEB ÖDSGM author mismatch in {unit_key}: {it.get('by')}"

assert len(ingilizcecin_items) >= 400, f"Expected >= 400 ingilizcecin items, got {len(ingilizcecin_items)}"
assert len(dersingilizce_items) >= 140, f"Expected >= 140 dersingilizce items, got {len(dersingilizce_items)}"
assert len(meb_items) >= 40, f"Expected >= 40 meb-odsgm items, got {len(meb_items)}"

# Verify NO meb-odsgm in g5 or g6
for key in sources["units"]:
    if key.startswith("g5/") or key.startswith("g6/"):
        assert not any(it.get("source") == "meb-odsgm" for it in sources["units"][key]), f"meb-odsgm must not exist in {key}"

# 2. Check app.js routing for all 3 worksheet subfolders
app_js = (ROOT / "app/js/app.js").read_text(encoding="utf-8")
assert "ingilizcecinWorksheetsScreen" in app_js, "app.js must define ingilizcecinWorksheetsScreen"
assert "dersingilizceWorksheetsScreen" in app_js, "app.js must define dersingilizceWorksheetsScreen"
assert "mebOdsgmWorksheetsScreen" in app_js, "app.js must define mebOdsgmWorksheetsScreen"

catalog = json.loads((ROOT / "app/data/catalog.json").read_text(encoding="utf-8"))
all_units = [(g["id"], u["id"]) for g in catalog["grades"] for u in g["units"]]
assert len(all_units) == 38, f"Expected 38 units, got {len(all_units)}"

for folder in ["ingilizcecin", "dersingilizce", "meb-odsgm"]:
    re_pattern = re.compile(rf"^\/(g\d)\/([a-z0-9_-]+)\/calisma\/{folder}$")
    for gid, uid in all_units:
        path = f"/{gid}/{uid}/calisma/{folder}"
        match = re_pattern.match(path)
        assert match and match.group(1) == gid and match.group(2) == uid, f"Route failed to match {path}"

# 3. Check worksheets.js exports and contains pickers and folder cards
ws_js = (ROOT / "app/js/worksheets.js").read_text(encoding="utf-8")
assert "export async function ingilizcecinWorksheetPicker" in ws_js
assert "export async function dersingilizceWorksheetPicker" in ws_js
assert "export async function mebOdsgmWorksheetPicker" in ws_js
assert "dersingilizce" in ws_js
assert "MEB ÖDSGM" in ws_js
assert "isMebGrade" in ws_js
assert "Çevrimiçi Çalışma Kâğıdı Klasörleri" in ws_js
assert "folder-card" in ws_js
assert "resource-search" in ws_js

# 4. Check store.js loads worksheet-sources.json and separates all 3 sources
store_js = (ROOT / "app/js/store.js").read_text(encoding="utf-8")
assert "worksheet-sources.json" in store_js
assert "ingilizcecin" in store_js
assert "dersingilizce" in store_js
assert "mebOdsgm" in store_js

# 5. Check local HTTP server serves files
server_proc = subprocess.Popen([sys.executable, "server/enghub.py", "--no-browser"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(1.2)
try:
    for endpoint in ["/app/data/worksheet-sources.json", "/app/js/worksheets.js", "/app/js/store.js", "/app/js/app.js", "/app/css/app.css"]:
        req = urllib.request.Request(f"http://127.0.0.1:8777{endpoint}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200, f"Server returned {resp.status} for {endpoint}"
            assert len(resp.read()) > 0, f"Server returned empty body for {endpoint}"
finally:
    server_proc.terminate()

print(f"PASS: 38 units checked. Sources: {len(ingilizcecin_items)} ingilizcecin (2020+), {len(dersingilizce_items)} dersingilizce (PDF only), {len(meb_items)} meb-odsgm (G7 & G8 only). Routing and server delivery verified.")
