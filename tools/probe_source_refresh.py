"""Offline Python probes for curriculum parsing and safe resource refresh."""
import json
from pathlib import Path
from unittest.mock import patch
import tempfile
from common import source_units
from fetch_catalog import classify
import fetch_worksheets as worksheets

parsed = source_units([{"title": "6. Sınıf", "units": [{"title": "1. TEMA", "id": 337}]},
                       {"title": "7. Sınıf", "units": [{"title": "10. ÜNİTE", "id": 10}]}])
assert parsed[6][1]["id"] == 337 and parsed[7][10]["id"] == 10
ws, off, online, extras, books = classify([
    {"type": "book-presentation", "previewLink": "https://example.com/current-book", "title": "Book"},
    {"type": "worksheet", "link": "https://wordwall.net/resource/123", "title": "Game"}])
assert not ws and len(online) == 1 and books[0]["link"].endswith("current-book")

with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as tmp:
    root = Path(tmp)
    dest = root / "content/g7/u1/worksheets"
    dest.mkdir(parents=True)
    (dest / "old.pdf").write_bytes(b"local worksheet")
    (root / "lesson.pdf").write_bytes(b"keep presentation source")
    old = {"items": [{"title": "Old", "link": "https://example.com/old", "file": "old.pdf", "size": 15}]}
    (dest / "manifest.json").write_text(json.dumps(old), encoding="utf-8")
    src = {"g7/u1": {"worksheets": [{"title": "Current", "link": "/uploads/current.pdf", "by": "Teacher"}]}}
    with patch.object(worksheets, "ROOT", root):
        worksheets.sync_worksheets(src)
        result = worksheets.purge_local_worksheets()
    assert result["removedFiles"] == 1
    assert not (dest / "old.pdf").exists()
    assert (root / "lesson.pdf").exists()
    items = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))["items"]
    assert items[0]["link"] == "https://eltarena.com/uploads/current.pdf"
    assert items[0]["by"] == "Teacher" and "file" not in items[0] and "size" not in items[0]

print("PASS: TEMA/UNITE parsing, resource classification, online-only manifests and scoped worksheet cleanup.")
