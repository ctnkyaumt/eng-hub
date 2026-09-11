"""Cache already-reviewed ARASAAC assets for Grade 6 offline use.

This never searches for new image matches. Meanings are reviewed in the authoring
source, with explicit exclusions for homonyms in create_grade6.py.
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import urllib.request
from grade6_content import UNITS

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "content/g6/shared/img"


def main():
    wanted = {w["en"].lower() for u in UNITS for g in u["groups"] for w in g["items"]}
    wanted.update(("write a diary", "share", "feel exhausted", "rest / relax"))
    images = {}
    for grade in ("g5", "g8"):
        for path in sorted((ROOT / "content" / grade).glob("u*/presentation/slides.json")):
            for slide in json.loads(path.read_text(encoding="utf-8"))["slides"]:
                if slide.get("type") != "vocab":
                    continue
                for word in slide["items"]:
                    name = word["en"].lower()
                    url = word.get("img", "")
                    match = re.fullmatch(r"https://static\.arasaac\.org/pictograms/(\d+)/\1_500\.png", url)
                    if name in wanted and match:
                        images[name] = dict(url=url, file=match[1] + ".png", source=f"https://arasaac.org/pictograms/en/{match[1]}")
    DEST.mkdir(parents=True, exist_ok=True)
    def download(item):
        dest = DEST / item["file"]
        if not dest.exists():
            request = urllib.request.Request(item["url"], headers={"User-Agent": "ENG-HUB educational offline materials"})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
            if not data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("Not a PNG: " + item["url"])
            dest.write_bytes(data)
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(download, {i["file"]: i for i in images.values()}.values()))
    (DEST.parent / "image-sources.json").write_text(json.dumps({
        "credit": "Pictograms: Sergio Palao / ARASAAC (Government of Aragon), CC BY-NC-SA. Original files, no changes.",
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/", "images": images
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Cached {len({i['file'] for i in images.values()})} existing pictograms for Grade 6.")


if __name__ == "__main__":
    main()
