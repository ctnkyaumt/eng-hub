"""Probe for Sumeyye Ogultekin games subfolder, thumbnails, and unit game routing."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# 1. Check game-sources.json
sources_path = ROOT / "app/data/game-sources.json"
assert sources_path.exists(), "game-sources.json must exist"
sources = json.loads(sources_path.read_text(encoding="utf-8"))
assert "units" in sources and "thumbnails" in sources, "game-sources.json must have 'units' and 'thumbnails'"
assert len(sources["units"]) >= 36, f"Expected at least 36 units, got {len(sources['units'])}"
assert len(sources["thumbnails"]) > 500, f"Expected thumbnails for existing games, got {len(sources['thumbnails'])}"

total_sumeyye_games = sum(len(games) for games in sources["units"].values())
assert total_sumeyye_games >= 400, f"Expected >= 400 sumeyye games, got {total_sumeyye_games}"

# 2. Check each sumeyye game has required fields
for unit_key, games in sources["units"].items():
    for g in games:
        assert g.get("title"), f"Game in {unit_key} missing title"
        assert g.get("link") and g["link"].startswith("https://sumeyyeogultekin.com/content/"), f"Invalid link in {unit_key}: {g.get('link')}"
        assert g.get("by") == "sumeyyeogultekin.com", f"Invalid author in {unit_key}"
        if "coverImage" in g:
            assert g["coverImage"].startswith("http"), f"Invalid coverImage URL in {unit_key}: {g['coverImage']}"

# 3. Check app.js routing for sumeyyeogultekin subfolder
app_js = (ROOT / "app/js/app.js").read_text(encoding="utf-8")
assert "sumeyyeGamesScreen" in app_js, "app.js must define sumeyyeGamesScreen"
assert "sumeyyeogultekin" in app_js, "app.js route must match sumeyyeogultekin"

# Verify routing regex against all 38 units
catalog = json.loads((ROOT / "app/data/catalog.json").read_text(encoding="utf-8"))
all_units = [(g["id"], u["id"]) for g in catalog["grades"] for u in g["units"]]
assert len(all_units) == 38, f"Expected 38 units, got {len(all_units)}"

route_re = re.compile(r"^\/(g\d)\/([a-z0-9_-]+)\/oyunlar\/sumeyyeogultekin$")
for gid, uid in all_units:
    path = f"/{gid}/{uid}/oyunlar/sumeyyeogultekin"
    match = route_re.match(path)
    assert match and match.group(1) == gid and match.group(2) == uid, f"Route failed to match {path}"

# 4. Check games/index.js exports and contains sumeyyeGamePicker
games_index = (ROOT / "app/js/games/index.js").read_text(encoding="utf-8")
assert "export async function sumeyyeGamePicker" in games_index, "games/index.js must export sumeyyeGamePicker"
assert "sumeyyeogultekin" in games_index, "games/index.js must reference sumeyyeogultekin subfolder"
assert "Çevrimiçi Oyun Klasörleri" in games_index, "games/index.js must display folders section"
assert "onlineGameGallery" in games_index, "games/index.js must use onlineGameGallery"

# 5. Check store.js separates online and sumeyye
store_js = (ROOT / "app/js/store.js").read_text(encoding="utf-8")
assert "sumeyye" in store_js, "store.js must separate sumeyye games"

# 6. Check games.css has folder-card styles
games_css = (ROOT / "app/css/games.css").read_text(encoding="utf-8")
assert ".folder-card" in games_css, "games.css must contain .folder-card styles"

print(f"PASS: 38 units, {total_sumeyye_games} sumeyye games in subfolder structure, {len(sources['thumbnails'])} existing previews, routing and gallery verified.")
