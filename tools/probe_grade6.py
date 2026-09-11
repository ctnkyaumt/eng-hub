"""Offline probes for the authored Grade 6 curriculum and refresh preservation.

Optional --books checks the supplied PDFs read-only for provenance and long
copied passages. Requires PyMuPDF for PDF checks (no app build).
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
from unittest.mock import patch
import wave

import fitz
import fetch_games
import fetch_worksheets
from create_grade6 import UNITS, ROOT, questions, source_ref, CORRECTIONS


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run(books=None):
    alignment = read(ROOT / "content/g6/curriculum.json")
    assert [u["id"] for u in UNITS] == ["revision", *[f"u{i}" for i in range(1, 9)]]
    catalog = read(ROOT / "app/data/catalog.json")
    totals = dict(slides=0, words=0, questions=0, pdfs=0, pages=0)
    audio = set()
    authored_text = []
    for unit in UNITS:
        base = ROOT / "content/g6" / unit["id"]
        deck = read(base / "presentation/slides.json")
        bank = read(base / "games/bank.json")
        manifest = read(base / "worksheets/manifest.json")
        expected_ids = {g["id"] for g in unit["grammar"]}
        assert deck["authored"] and bank["authored"]
        assert deck["source"] == source_ref(unit)
        assert expected_ids == {s["grammarId"] for s in deck["slides"] if s.get("grammarId")}
        assert expected_ids == {q["grammarId"] for s in bank["sets"] for q in s["questions"] if q.get("grammarId")}
        words = bank["words"]
        assert len({w["en"].lower() for w in words}) == len(words) == 32
        assert len([w for w in words if re.fullmatch("[a-zA-Z]{3,12}", w["en"])]) >= 5
        assert len([w for w in words if re.fullmatch("[a-zA-Z ]{3,12}", w["en"])]) >= 5
        all_q = [q for s in bank["sets"] for q in s["questions"]]
        assert len(all_q) >= 6
        for q in all_q:
            assert q["q"].strip() and len(q["a"]) == 4
            assert len({a["t"].strip().casefold() for a in q["a"]}) == 4
            assert sum(a["c"] is True for a in q["a"]) == 1
        for slide in deck["slides"]:
            if slide["type"] == "vocab":
                assert 1 <= len(slide["items"]) <= 4
                for item in slide["items"]:
                    assert item.get("img") or item.get("num") or (item.get("textOnly") and item.get("imageNote"))
                    if item.get("img"):
                        assert item["img"].startswith("/") and (ROOT / item["img"].lstrip("/")).is_file()
                    slug = re.sub("[^a-z0-9]+", "-", item["en"].lower()).strip("-")
                    audio.add(ROOT / "app/audio/words" / (slug + ".wav"))
            elif slide["type"] == "grammar":
                assert len(slide["examples"]) == 1
                ex = slide["examples"][0]
                assert ex["trEm"] and all(mark in ex["tr"] for mark in ex["trEm"])
                authored_text.append(ex["en"].replace("*", ""))
            elif slide["type"] == "exercise":
                assert len(slide["tasks"]) == 1
                task = slide["tasks"][0]
                if task["kind"] == "match":
                    assert all(set(p) == {"a", "b"} and p["a"] and p["b"] for p in task["pairs"])
            elif slide["type"] == "mission" and slide["task"]["kind"] in ("dragmatch", "listenpicture"):
                choices = slide["task"]["items"]
                assert len(choices) == len({w["img"] for w in choices}) == 4
        for i, (_, answer) in enumerate(unit["truth"], 1):
            if not answer:
                assert CORRECTIONS[unit["id"]][i]
        assert len(manifest["items"]) == 3
        for item in manifest["items"]:
            assert fetch_worksheets.authored_item(item)
            path = base / "worksheets" / item["file"]
            assert path.stat().st_size == item["size"]
            with fitz.open(path) as doc:
                assert len(doc) == 2, (path, len(doc))
                for page in doc:
                    assert "ENG HUB" in page.get_text()
                    # Check rendered text boxes remain within the page margins.
                    for block in page.get_text("dict")["blocks"]:
                        for line in block.get("lines", []):
                            for span in line["spans"]:
                                x0, y0, x1, y1 = span["bbox"]
                                assert 20 <= x0 < x1 <= page.rect.width - 20, (path, span)
                                assert 15 <= y0 < y1 <= page.rect.height - 15, (path, span)
                                assert "\ufffd" not in span["text"]
                totals["pages"] += len(doc)
            totals["pdfs"] += 1
        entry = next(u for g in catalog["grades"] if g["id"] == "g6" for u in g["units"] if u["id"] == unit["id"])
        assert all(entry["has"].values()) and entry["counts"]["games"] == len(all_q)
        assert entry["counts"]["worksheets"] == 3 and entry["counts"]["worksheetLinks"] == 0
        totals["slides"] += len(deck["slides"])
        totals["words"] += len(words)
        totals["questions"] += len(all_q)
        authored_text.extend([unit["story"], unit["listening"], unit["model"], *[q["complete"] for q in questions(unit)]])
    for path in audio:
        with wave.open(str(path)) as clip:
            assert clip.getnframes() / clip.getframerate() > 0.2, path
            samples = clip.readframes(clip.getnframes())
            assert any(samples), path

    # Real maintenance functions, isolated filesystem, no network.
    with tempfile.TemporaryDirectory(prefix="g6-probe-", dir=ROOT) as temp:
        root = Path(temp)
        ws = root / "content/g6/u1/worksheets"
        ws.mkdir(parents=True)
        local = read(ROOT / "content/g6/u1/worksheets/manifest.json")["items"]
        for item in local:
            (ws / item["file"]).write_bytes(b"authored-pdf")
        (ws / "retired.pdf").write_bytes(b"old external worksheet")
        (ws / "manifest.json").write_text(json.dumps({"items": local}), encoding="utf-8")
        src = {"g6/u1": {"worksheets": [{"title": "New remote", "link": "/uploads/new.pdf"}]}}
        with patch.object(fetch_worksheets, "ROOT", root):
            fetch_worksheets.sync_worksheets(src)
            fetch_worksheets.purge_local_worksheets()
        kept = read(ws / "manifest.json")["items"]
        assert kept[:3] == local and len(kept) == 4
        assert not (ws / "retired.pdf").exists()
        assert all((ws / i["file"]).read_bytes() == b"authored-pdf" for i in local)
        games = root / "content/g6/u1/games"
        games.mkdir(parents=True)
        original_bank = (ROOT / "content/g6/u1/games/bank.json").read_bytes()
        (games / "bank.json").write_bytes(original_bank)
        with patch.object(fetch_games, "CONTENT", str(root / "content")), patch.object(fetch_games, "fetch_set", side_effect=AssertionError("Unexpected network access")):
            fetch_games.build_unit("g6", "u1", {"offlineGames": [{"code": "stale"}]}, True, True)
        assert (games / "bank.json").read_bytes() == original_bank

    if books:
        def tokens(text):
            return re.findall(r"[a-z]+", text.lower())
        reference = set()
        for book in alignment["books"]:
            path = books / book["file"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == book["sha256"], "Source book changed"
            with fitz.open(path) as doc:
                assert len(doc) == book["pages"]
                seq = tokens(" ".join(p.get_text() for p in doc))
            reference.update(tuple(seq[i:i+14]) for i in range(len(seq)-13))
        for passage in authored_text:
            seq = tokens(passage)
            overlaps = [" ".join(seq[i:i+14]) for i in range(len(seq)-13) if tuple(seq[i:i+14]) in reference]
            assert not overlaps, ("Copied 14-word passage", overlaps)
        print("PASS: both book hashes unchanged; no matching 14-word passages in authored texts.")
    print("PASS: Grade 6 schema, all seven game modes, grammar coverage, PDFs, offline media, maintenance preservation.")
    print(totals, f"; {len(audio)} playable word recordings")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", type=Path)
    run(ap.parse_args().books)
