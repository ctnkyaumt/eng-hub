"""Probe game modules and optional running app, without a local build."""
import argparse
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--url", help="Existing local app URL, for HTTP asset probes")
args = parser.parse_args()
for module in ("arcade", "session", "tower", "index"):
    subprocess.run(["node", "--check", str(ROOT / f"app/js/games/{module}.js")], check=True)
subprocess.run(["node", str(ROOT / "tools/probe_arcade.mjs")], check=True)
if args.url:
    for asset in ("/", "/app/css/games.css", "/app/css/arcade.css", "/app/css/tower.css",
                  "/app/js/games/arcade.js", "/app/js/games/session.js", "/app/js/games/tower.js",
                  "/app/js/games/index.js", "/app/data/catalog.json"):
        with urllib.request.urlopen(args.url.rstrip("/") + asset, timeout=10) as response:
            assert response.status == 200, asset
            assert response.read(), asset
    print("PASS: running app serves all game assets.")
