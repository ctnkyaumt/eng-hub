"""Python probe for sharpshooter game data and online-only worksheet integrity."""
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
catalog_path = ROOT / "app/data/catalog.json"
assert catalog_path.exists(), "catalog.json missing"
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

seed_path = ROOT / "app/data/sharpshooter-words.json"
assert seed_path.exists(), "sharpshooter-words.json missing"
seed = json.loads(seed_path.read_text(encoding="utf-8")).get("units", {})

grades = catalog.get("grades", [])
assert len(grades) == 4, f"Expected 4 grades, got {len(grades)}"
g5 = next(g for g in grades if g["id"] == "g5")
assert len([u for u in g5["units"] if u["id"] != "revision"]) == 8, f"Grade 5 must have 8 themes"
assert any(u["id"] == "revision" for u in g5["units"]), "Grade 5 must have revision unit"
g6 = next(g for g in grades if g["id"] == "g6")
assert len([u for u in g6["units"] if u["id"] != "revision"]) == 8, f"Grade 6 must have 8 themes"
assert any(u["id"] == "revision" for u in g6["units"]), "Grade 6 must have revision unit"

total_units = 0
for g in grades:
    for u in g["units"]:
        key = f"{g['id']}/{u['id']}"
        bank_path = ROOT / "content" / key / "games/bank.json"
        slides_path = ROOT / "content" / key / "presentation/slides.json"
        bank = json.loads(bank_path.read_text(encoding="utf-8")) if bank_path.exists() else {"sets": [], "words": []}
        slides = json.loads(slides_path.read_text(encoding="utf-8")) if slides_path.exists() else {"slides": []}

        words = {w["en"].lower(): w for w in bank.get("words", []) if w.get("en") and w.get("tr")}
        for s in slides.get("slides", []):
            for it in s.get("items", []):
                if it.get("en") and it.get("tr"):
                    words[it["en"].lower()] = it

        if len(words) < 4:
            for w in seed.get(key, []):
                if w.get("en") and w.get("tr"):
                    words[w["en"].lower()] = w

        assert len(words) >= 4, f"{key}: insufficient shooter vocabulary ({len(words)} found)"

        # Check question simulation
        word_list = list(words.values())
        for _ in range(5):
            sample_words = random.sample(word_list, min(15, len(word_list)))
            for sw in sample_words:
                pool = [w for w in word_list if w["en"] != sw["en"] and w["tr"].lower() != sw["tr"].lower()]
                distractors = random.sample(pool, min(3, len(pool)))
                options = [sw["en"]] + [d["en"] for d in distractors]
                assert len(options) >= 2, f"{key}: too few options"
                assert len(set(options)) == len(options), f"{key}: duplicate choices"

        # Imported worksheets stay online; authored Grade 6 PDFs are retained.
        from fetch_worksheets import authored_item
        expected_local = set()
        ws_path = ROOT / "content" / key / "worksheets/manifest.json"
        if ws_path.exists():
            ws_man = json.loads(ws_path.read_text(encoding="utf-8"))
            for it in ws_man.get("items", []):
                if key.startswith("g6/") and authored_item(it):
                    expected_local.add(it["file"])
                    assert (ws_path.parent / it["file"]).is_file()
                    continue
                assert "file" not in it, f"{key}: worksheet item has local 'file' attribute: {it}"
                assert "size" not in it, f"{key}: worksheet item has 'size' attribute: {it}"
                assert it.get("link"), f"{key}: worksheet item missing online link"

        # Verify no local worksheet files exist in the unit folder
        ws_dir = ROOT / "content" / key / "worksheets"
        if ws_dir.exists():
            local_files = [p for p in ws_dir.glob("*") if p.is_file() and p.name != "manifest.json"]
            assert {p.name for p in local_files} == expected_local, f"{key}: unexpected local worksheet files: {local_files}"

        total_units += 1

assert total_units == 38, f"Expected 38 units, got {total_units}"
print(f"PASS: {total_units} units verified. Sharpshooter coverage, online imports and authored local worksheets.")
