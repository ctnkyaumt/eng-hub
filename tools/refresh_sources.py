"""Refresh source data without building the app or regenerating lesson slides.

Force-fetches game JSON and static mirrors; checks online worksheet/book links.
Keeps last-known-good files on network errors; writes a dated audit report.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
from urllib.parse import urljoin
import requests

from common import ROOT, DATA, API, UA
from fetch_games import build_unit, fetch_set, clean_url
from fetch_worksheets import sync_worksheets, purge_local_worksheets
from mirror_sites import Mirror, mirrorable, kind_for, slug_for

ROOT = Path(ROOT)
DATA = Path(DATA)
report = {"checkedAt": datetime.now(timezone.utc).isoformat(), "games": [], "worksheets": [], "mirrors": [], "links": []}


def read(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    indent = None if path.name in ("bank.json", "_raw.json", "source-index.json") else 1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=indent), encoding="utf-8")


def run(script, *args):
    subprocess.run([sys.executable, str(ROOT / "tools" / script), *args], check=True)


def parallel(jobs, fn, label, workers=8):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fn, job): job for job in jobs}
        for i, future in enumerate(as_completed(futures), 1):
            future.result()  # programming errors must stop the refresh
            if i % 20 == 0 or i == len(jobs):
                print(f"{label}: {i}/{len(jobs)}", flush=True)


def refresh_bank(job):
    key, src = job
    path = ROOT / "content" / key / "games/_raw.json"
    raw = read(path, {})
    old = read(path.parent / "bank.json", {"sets": []})
    if key.startswith("g6/") and old.get("authored") and old.get("curriculum") == "meb-english-6-2026":
        report["games"].append({"unit": key, "status": "authored-preserved"})
        return
    failed = set()
    for item in src["offlineGames"]:
        code = item["code"]
        entry = {"unit": key, "code": code}
        try:
            data = fetch_set(code)
            if not isinstance(data.get("questions"), list) or not data["questions"]:
                raise ValueError("Empty or invalid question group")
            entry["changed"] = raw.get(code) != data
            raw[code] = data
            entry["status"] = "refreshed"
        except Exception as exc:
            failed.add(code)
            entry.update(status="retained" if code in raw else "unavailable", error=str(exc))
        report["games"].append(entry)
    save(path, raw)
    # Avoid a second network attempt for known failures without a raw cache.
    usable = {**src, "offlineGames": [i for i in src["offlineGames"] if i["code"] in raw]}
    build_unit(*key.split("/"), usable, True, False)
    bank_path = path.parent / "bank.json"
    bank = read(bank_path, {})
    present = {s["code"] for s in bank["sets"]}
    bank["sets"].extend(s for s in old["sets"] if s["code"] in failed and s["code"] not in present)
    save(bank_path, bank)


def refresh_mirror(job):
    key, item = job
    base = ROOT / "content" / key / "sites"
    slug = slug_for(item["link"], item["title"])
    dest = base / slug
    entry = {**item, "slug": slug, "kind": "game"}
    audit = {"unit": key, "url": item["link"]}
    base.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="refresh-", dir=base) as temp:
            m = Mirror(item["link"], temp)
            m.crawl(item["link"])
            if not (Path(temp) / "index.html").exists():
                raise ValueError("Entry page unavailable")
            # Preserve old assets if individual source assets fail.
            shutil.copytree(temp, dest, dirs_exist_ok=True)
            entry["files"] = m.count
            audit["failedAssets"] = m.failures
        audit["status"] = "partial" if m.failures else "refreshed"
    except Exception as exc:
        audit.update(status="retained", error=str(exc))
    if (dest / "index.html").exists():
        entry["path"] = slug + "/index.html"
    report["mirrors"].append(audit)
    return entry


def check_link(url):
    try:
        with requests.get(url, headers={"User-Agent": UA}, timeout=(8, 18), stream=True) as response:
            status = response.status_code
            entry = {"url": url, "http": status, "resolved": response.url,
                     "status": "ok" if status < 400 else "missing" if status in (404, 410) else "blocked"}
    except requests.RequestException as exc:
        entry = {"url": url, "status": "unreachable", "error": str(exc)}
    report["links"].append(entry)


def refresh_images(src):
    """Re-fetch images too: the bytes behind an unchanged URL can change."""
    targets = {}
    for key, source in src.items():
        base = ROOT / "content" / key / "games"
        raw = read(base / "_raw.json", {})
        for item in source["offlineGames"]:
            for q in raw.get(item["code"], {}).get("questions", []):
                for a in [q] + q.get("answers", []):
                    url = clean_url(a.get("image_path"))
                    if url:
                        prefix = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
                        targets.setdefault(url, set()).update((base / "img").glob(prefix + ".*"))
    report["images"] = []
    def image_job(job):
        url, files = job
        audit = {"url": url, "copies": len(files)}
        try:
            response = requests.get(url, headers={"User-Agent": UA}, timeout=(8, 20))
            response.raise_for_status()
            if not response.headers.get("Content-Type", "").startswith("image/") or not response.content:
                raise ValueError("Source did not return an image")
            changed = 0
            for path in files:
                if path.read_bytes() != response.content:
                    path.write_bytes(response.content)
                    changed += 1
            audit.update(status="refreshed", changed=changed)
        except Exception as exc:
            audit.update(status="retained", error=str(exc))
        report["images"].append(audit)
    parallel(list(targets.items()), image_job, "Game images", 6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-games", action="store_true", help="resume after game refresh")
    args = ap.parse_args()
    run("fetch_catalog.py", "--refresh")
    src = read(DATA / "source-index.json", {})
    if not args.skip_games:
        parallel(list(src.items()), refresh_bank, "Game banks")
        refresh_images(src)
    sync_worksheets(src)
    report["worksheetStorage"] = purge_local_worksheets()
    run("import_worksheet_links.py")
    for key, source in src.items():
        items, seen = [], set()
        for item in source["onlineGames"] + source["extras"]:
            if item["link"] not in seen and mirrorable(item["link"]) and kind_for(item["link"], item["title"]) == "game":
                seen.add(item["link"])
                items.append(item)
        # Multiple entries can share the same directory; refresh each unit serially.
        source["mirrorJobs"] = items
    def mirrors_for_unit(job):
        key, source = job
        bank = read(ROOT / "content" / key / "games/bank.json", {})
        if key.startswith("g6/") and bank.get("authored"):
            return
        items = [refresh_mirror((key, item)) for item in source["mirrorJobs"]]
        save(ROOT / "content" / key / "sites/manifest.json", {"items": items})
    parallel(list(src.items()), mirrors_for_unit, "Static activities", 4)
    urls = set()
    for key, source in src.items():
        for bucket in ("worksheets", "onlineGames", "books"):
            urls.update(urljoin(API, i["link"]) for i in source[bucket] if i.get("link"))
        path = ROOT / "content" / key / "worksheets/manifest.json"
        urls.update(urljoin(API, i["link"]) for i in read(path, {"items": []})["items"] if i.get("link"))
    parallel(sorted(urls), check_link, "Source links", 12)
    for values in report.values():
        if isinstance(values, list):
            values.sort(key=lambda x: (x.get("unit", ""), x.get("url", x.get("code", ""))))
    save(DATA / "source-audit.json", report)
    run("fetch_catalog.py")
    run("verify_content.py")
    print("Audit saved: app/data/source-audit.json", flush=True)


if __name__ == "__main__":
    main()
