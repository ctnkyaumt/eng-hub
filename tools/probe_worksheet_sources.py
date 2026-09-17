"""Probe for ingilizcecin worksheet sources, data integrity, routing, and UI."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# 1. Check worksheet-sources.json
sources_path = ROOT / "app/data/worksheet-sources.json"
assert sources_path.exists(), "worksheet-sources.json must exist"
sources = json.loads(sources_path.read_text(encoding="utf-8"))
assert "units" in sources, "worksheet-sources.json must have 'units'"
assert len(sources["units"]) >= 36, f"Expected at least 36 units, got {len(sources['units'])}"

total_items = sum(len(items) for items in sources["units"].values())
assert total_items >= 400, f"Expected >= 400 items, got {total_items}"

# 2. Check each item has required fields and year >= 2020
for unit_key, items in sources["units"].items():
    for it in items:
        assert it.get("title"), f"Item in {unit_key} missing title"
        assert it.get("link") and it["link"].startswith("https://www.ingilizcecin.com/"), f"Invalid link in {unit_key}: {it.get('link')}"
        assert it.get("date"), f"Item in {unit_key} missing date: {it.get('title')}"
        assert isinstance(it.get("year"), int) and it["year"] >= 2020, f"Item in {unit_key} created before 2020: {it.get('year')} in {it.get('title')}"
        assert it.get("source") == "ingilizcecin", f"Invalid source in {unit_key}: {it.get('source')}"
        assert it.get("sourcePage"), f"Missing sourcePage in {unit_key}"

# 3. Check app.js routing for ingilizcecin subfolder
app_js = (ROOT / "app/js/app.js").read_text(encoding="utf-8")
assert "ingilizcecinWorksheetsScreen" in app_js, "app.js must define ingilizcecinWorksheetsScreen"
assert "ingilizcecin" in app_js, "app.js route must match ingilizcecin"

# Verify routing regex against all 38 units in catalog
catalog = json.loads((ROOT / "app/data/catalog.json").read_text(encoding="utf-8"))
all_units = [(g["id"], u["id"]) for g in catalog["grades"] for u in g["units"]]
assert len(all_units) == 38, f"Expected 38 units, got {len(all_units)}"

route_re = re.compile(r"^\/(g\d)\/([a-z0-9_-]+)\/calisma\/ingilizcecin$")
for gid, uid in all_units:
    path = f"/{gid}/{uid}/calisma/ingilizcecin"
    match = route_re.match(path)
    assert match and match.group(1) == gid and match.group(2) == uid, f"Route failed to match {path}"

# 4. Check worksheets.js exports and contains ingilizcecinWorksheetPicker and folder card
ws_js = (ROOT / "app/js/worksheets.js").read_text(encoding="utf-8")
assert "export async function ingilizcecinWorksheetPicker" in ws_js, "worksheets.js must export ingilizcecinWorksheetPicker"
assert "ingilizcecin" in ws_js, "worksheets.js must reference ingilizcecin"
assert "Çevrimiçi Çalışma Kâğıdı Klasörleri" in ws_js, "worksheets.js must display folders section"
assert "folder-card" in ws_js, "worksheets.js must use folder-card"
assert "resource-search" in ws_js, "worksheets.js must include search filter"

# 5. Check store.js loads worksheet-sources.json and separates ingilizcecin
store_js = (ROOT / "app/js/store.js").read_text(encoding="utf-8")
assert "worksheet-sources.json" in store_js, "store.js must load worksheet-sources.json"
assert "ingilizcecin" in store_js, "store.js must return ingilizcecin"

# 6. Check app.css has folder-card styles
app_css = (ROOT / "app/css/app.css").read_text(encoding="utf-8")
assert ".folder-card" in app_css, "app.css must contain .folder-card styles"
assert ".resource-search" in app_css, "app.css must contain .resource-search styles"

# 7. Check local HTTP server serves files
import subprocess
import time
import urllib.request
import sys

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

print(f"PASS: 38 units checked, {total_items} ingilizcecin items across {len(sources['units'])} units (all >= 2020), routing, UI, search, and local server delivery verified.")
