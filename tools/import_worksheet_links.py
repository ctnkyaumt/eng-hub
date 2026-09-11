"""Import direct worksheet/test links; keep online games in the games category.

Run: python tools/import_worksheet_links.py [--grade 8] [--unit 1]
Only fetch index pages. Documents remain attributed online links.
"""
import argparse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import unicodedata
from resource_kind import online_game
from fetch_worksheets import online_item, authored_item
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
HOST = "https://www.ingilizceciyiz.com/"


def fold(text):
    text = text.lower().replace("ı", "i")
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def extract_links(html, source):
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("article .entry-content") or soup.select_one(".entry-content")
    if article is None:
        raise ValueError("No article content: " + source)
    result, seen = [], set()
    previous = "Test"
    for a in article.select("a[href]"):
        title = a.get_text(" ", strip=True)
        link = urljoin(source, a["href"])
        normalized = fold(title + " " + unquote(link))
        if not title or "konu anlat" in normalized or "konu-anlat" in normalized or "sunusu" in normalized:
            continue
        if not (re.search(r"\.(pdf|docx?|zip)(?:$|\?)", link, re.I) or urlparse(link).hostname == "drive.google.com"):
            continue
        if link in seen:
            continue
        if "cevap" in fold(title):
            title = previous + " · " + title
        else:
            previous = title
        seen.add(link)
        result.append({"title": title, "link": link, "by": "İngilizceciyiz", "source": source})
    return result


def fetch_page(url):
    response = requests.get(url, timeout=35)
    if response.status_code == 404 and "calisma-kagidi-ve" in url:
        url = url.replace("calisma-kagidi-ve", "calisma-kagitlari-ve")
        response = requests.get(url, timeout=35)
    if response.status_code == 404:
        raise ValueError("Source index unavailable (404): " + url)
    response.raise_for_status()
    return extract_links(response.content, url)


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    compact = path.name in ("bank.json", "source-index.json")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=None if compact else 1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", type=int)
    ap.add_argument("--unit", type=int)
    args = ap.parse_args()
    catalog_path = ROOT / "app/data/catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    source_path = ROOT / "app/data/source-index.json"
    sources = json.loads(source_path.read_text(encoding="utf-8"))
    jobs = []
    for grade in catalog["grades"]:
        if args.grade and grade["no"] != args.grade:
            continue
        for unit in grade["units"]:
            if args.unit and unit["no"] != args.unit:
                continue
            key = grade["id"] + "/" + unit["id"]
            if unit["id"] == "revision" or unit.get("no", 0) == 0:
                continue
            if grade["no"] == 6:
                # Old unit URLs describe the retired ten-unit curriculum.
                continue
            if grade["no"] == 5:
                # These pages are linked from the current theme hub.
                for suffix in ("calisma-kagitlari-etkinlikler", "testleri"):
                    jobs.append((key, HOST + f'5-sinif-ingilizce-{unit["no"]}-unite-{suffix}/'))
                continue
            for suffix in ("calisma-kagidi-ve-etkinlikler", "test"):
                url = HOST + f'{grade["no"]}-sinif-ingilizce-{unit["no"]}-unite-{suffix}/'
                jobs.append((key, url))
    imported = {}
    refreshed = set()
    audit = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [(key, url, pool.submit(fetch_page, url)) for key, url in jobs]
        for key, url, future in futures:
            try:
                items = future.result()
                imported.setdefault(key, []).extend(items)
                refreshed.add(url)
                refreshed.update(item["source"] for item in items)
                audit.append({"unit": key, "url": url, "status": "ok", "documents": len(items)})
                print(key, len(items), url, flush=True)
            except Exception as exc:
                audit.append({"unit": key, "url": url, "status": "unavailable", "error": str(exc)})
                print("FAILED", url, str(exc), flush=True)
    removed = added = 0
    for grade in catalog["grades"]:
        for unit in grade["units"]:
            key = grade["id"] + "/" + unit["id"]
            if unit["id"] == "revision" or unit.get("no", 0) == 0:
                continue
            path = ROOT / "content" / key / "worksheets/manifest.json"
            if not path.exists():
                continue
            manifest = json.loads(path.read_text(encoding="utf-8"))
            old = manifest["items"]
            for item in old:
                if item.get("file") and not (path.parent / item["file"]).exists():
                    item.pop("file")
                    item.pop("size", None)
            games = [i for i in old if online_game(i)]
            removed += len(games)
            manifest["items"] = [i for i in old if not online_game(i) and i.get("source") not in refreshed]
            known = {i.get("link") for i in manifest["items"]}
            for item in imported.get(key, []):
                if item["link"] not in known:
                    manifest["items"].append(item)
                    known.add(item["link"])
                    added += 1
            local = [i for i in manifest["items"] if key.startswith("g6/") and authored_item(i)]
            manifest["items"] = local + [online_item(i) for i in manifest["items"] if i.get("link") and i not in local]
            save(path, manifest)
            bank_path = ROOT / "content" / key / "games/bank.json"
            bank = json.loads(bank_path.read_text(encoding="utf-8")) if bank_path.exists() else {"sets": [], "vocab": [], "online": []}
            online = bank.setdefault("online", [])
            known_games = {i.get("link") for i in online}
            for game in games:
                if game["link"] not in known_games:
                    online.append(game)
                    known_games.add(game["link"])
            if games:
                save(bank_path, bank)
            unit["counts"]["worksheets"] = sum(bool(i.get("file")) for i in manifest["items"])
            unit["has"]["worksheets"] = bool(manifest["items"])
            if key in sources:
                sources[key]["worksheets"] = [i for i in sources[key].get("worksheets", []) if not online_game(i)]
    save(catalog_path, catalog)
    save(source_path, sources)
    save(ROOT / "app/data/worksheet-source-audit.json", {
        "checkedAt": datetime.now(timezone.utc).isoformat(), "sources": audit})
    print(f"Added {added} document links; moved {removed} game entries out of worksheets.")


if __name__ == "__main__":
    main()
