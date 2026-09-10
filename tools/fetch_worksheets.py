"""Maintain online-only worksheet manifests. Never download worksheet files."""
import json
from pathlib import Path
import shutil
from urllib.parse import urljoin
from common import ROOT, API
from resource_kind import online_game

ROOT = Path(ROOT)


def online_item(item):
    return {**{k: v for k, v in item.items() if k not in ("file", "size")},
            "link": urljoin(API, item["link"])}


def sync_worksheets(sources):
    for key, source in sources.items():
        path = ROOT / "content" / key / "worksheets/manifest.json"
        previous = json.loads(path.read_text(encoding="utf-8"))["items"] if path.exists() else []
        items = list(source.get("worksheets", []))
        # The old grade-6 unit indices describe a different curriculum.
        if not key.startswith("g6/"):
            items.extend(i for i in previous if i.get("source"))
        unique = {i["link"]: online_item(i) for i in items if i.get("link") and not online_game(i)}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"items": list(unique.values())}, ensure_ascii=False, indent=1), encoding="utf-8")


def purge_local_worksheets():
    """Keep only manifests, including in retired units; validate every target."""
    content = (ROOT / "content").resolve()
    files = size = 0
    for folder in content.glob("g*/u*/worksheets"):
        if not folder.resolve().is_relative_to(content):
            raise ValueError("Worksheet folder outside content root")
        manifest = folder / "manifest.json"
        if manifest.exists():
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["items"] = [online_item(i) for i in data["items"] if i.get("link")]
            manifest.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        for target in folder.iterdir():
            if target.name == "manifest.json":
                continue
            if not target.resolve().is_relative_to(content):
                raise ValueError("Refusing to remove a path outside content")
            if target.is_dir():
                members = list(target.rglob("*"))
                if any(not p.resolve().is_relative_to(content) for p in members):
                    raise ValueError("Refusing a worksheet directory with external links")
                size += sum(p.stat().st_size for p in members if p.is_file())
                files += sum(p.is_file() for p in members)
                shutil.rmtree(target)
            else:
                size += target.stat().st_size
                files += 1
                target.unlink()
    result = {"removedFiles": files, "freedBytes": size, "mode": "online-only"}
    print(f"Worksheets online-only: removed {files} files, freed {size / 1024**2:.1f} MiB", flush=True)
    return result


if __name__ == "__main__":
    src = json.loads((ROOT / "app/data/source-index.json").read_text(encoding="utf-8"))
    sync_worksheets(src)
    purge_local_worksheets()
