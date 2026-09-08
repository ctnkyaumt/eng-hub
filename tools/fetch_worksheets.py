#!/usr/bin/env python3
"""Download every worksheet into content/<grade>/<unit>/worksheets/.

Run:  python tools/fetch_worksheets.py [--grade 5] [--unit 1] [--force]

Resumable: files already on disk are skipped, so re-running only picks up what
failed last time. Google Drive links are resolved through the direct-download
endpoint, including the "file too large to scan" confirmation page.
Failures are logged to tools/logs/worksheets.log and stay in the manifest as
online links so nothing disappears from the UI.
"""

import argparse
import http.cookiejar
import json
import mimetypes
import os
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import API, CONTENT, DATA, UA, drive_id, ensure, log, progress, safe_name  # noqa: E402

EXT_BY_TYPE = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/msword": ".doc",
    "application/vnd.ms-powerpoint": ".ppt",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "application/zip": ".zip",
}

opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
)
opener.addheaders = [("User-Agent", UA), ("Accept", "*/*")]


def fetch(url, timeout=120):
    return opener.open(url, timeout=timeout)


def disposition_name(resp):
    cd = resp.headers.get("Content-Disposition") or ""
    m = re.search(r"filename\*=UTF-8''([^;]+)", cd) or re.search(r'filename="?([^";]+)"?', cd)
    return urllib.parse.unquote(m.group(1)) if m else ""


def ext_for(resp, fallback_name=""):
    for cand in (os.path.splitext(disposition_name(resp))[1], os.path.splitext(fallback_name)[1]):
        if cand and len(cand) <= 6:
            return cand.lower()
    ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    return EXT_BY_TYPE.get(ctype) or mimetypes.guess_extension(ctype) or ".bin"


def download_drive(fid):
    """Return (response, ) for a Drive file, walking the confirm page if needed."""
    url = "https://drive.google.com/uc?export=download&id=" + fid
    resp = fetch(url)
    ctype = (resp.headers.get("Content-Type") or "").lower()
    if "text/html" not in ctype:
        return resp
    body = resp.read().decode("utf-8", "replace")
    # newer Drive: a <form action="https://drive.usercontent.google.com/download"> with hidden inputs
    form = re.search(r'action="(https://drive\.usercontent\.google\.com/download[^"]*)"', body)
    if form:
        action = form.group(1).replace("&amp;", "&")
        fields = dict(re.findall(r'name="([^"]+)"\s+value="([^"]*)"', body))
        return fetch(action + ("&" if "?" in action else "?") + urllib.parse.urlencode(fields))
    token = re.search(r"confirm=([0-9A-Za-z_-]+)", body)
    if token:
        return fetch(url + "&confirm=" + token.group(1))
    raise RuntimeError("drive: onay sayfasi cozulemedi")


def download(item, dest_dir, index):
    link = item.get("link") or ""
    fid = drive_id(link) if "drive.google.com" in link else None

    if fid:
        resp = download_drive(fid)
        hint = disposition_name(resp)
    elif link.startswith("/"):
        resp = fetch(API + link)
        hint = os.path.basename(link)
    elif link.startswith("http"):
        resp = fetch(link)
        hint = os.path.basename(urllib.parse.urlparse(link).path)
    else:
        raise RuntimeError("desteklenmeyen baglanti")

    ext = ext_for(resp, hint)
    if ext in (".html", ".htm"):
        raise RuntimeError("dosya yerine web sayfasi dondu (erisim izni?)")

    name = "%02d %s%s" % (index, safe_name(item.get("title") or hint or "calisma"), ext)
    path = os.path.join(dest_dir, name)
    with open(path, "wb") as f:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
    if os.path.getsize(path) < 1024:
        os.remove(path)
        raise RuntimeError("dosya bos geldi")
    return name, os.path.getsize(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", type=int, help="sadece bu sinif")
    ap.add_argument("--unit", type=int, help="sadece bu unite")
    ap.add_argument("--force", action="store_true", help="var olan dosyalari da yeniden indir")
    args = ap.parse_args()

    with open(os.path.join(DATA, "source-index.json"), encoding="utf-8") as f:
        src = json.load(f)

    keys = sorted(src, key=lambda k: (int(k[1]), int(k.split("/")[1][1:])))
    if args.grade:
        keys = [k for k in keys if k.startswith("g%d/" % args.grade)]
    if args.unit:
        keys = [k for k in keys if k.endswith("/u%d" % args.unit)]

    total = sum(len(src[k]["worksheets"]) for k in keys)
    done = ok = fail = skip = 0
    print("Toplam %d calisma kagidi\n" % total)

    for key in keys:
        gid, uid = key.split("/")
        items = src[key]["worksheets"]
        if not items:
            continue
        dest = os.path.join(CONTENT, gid, uid, "worksheets")
        ensure(dest)

        existing = {f for f in os.listdir(dest) if not f.endswith(".json")}
        manifest = []

        for i, it in enumerate(items, 1):
            from resource_kind import online_game
            if online_game(it):
                continue
            done += 1
            entry = {"title": it["title"], "desc": it["desc"], "by": it["by"], "link": it["link"]}
            prefix = "%02d " % i
            already = next((f for f in existing if f.startswith(prefix)), None)
            if already and not args.force:
                entry["file"] = already
                entry["size"] = os.path.getsize(os.path.join(dest, already))
                skip += 1
                manifest.append(entry)
                progress(done, total, "%s atlandi" % key)
                continue
            try:
                name, size = download(it, dest, i)
                entry["file"] = name
                entry["size"] = size
                ok += 1
            except Exception as exc:  # noqa: BLE001
                fail += 1
                log("worksheets.log", "HATA %s #%d %s -> %s" % (key, i, it["title"][:60], exc))
            manifest.append(entry)
            progress(done, total, key)

        manifest_path = os.path.join(dest, "manifest.json")
        if os.path.isfile(manifest_path):
            with open(manifest_path, encoding="utf-8") as f:
                previous = json.load(f).get("items", [])
            links = {item.get("link") for item in manifest}
            manifest.extend(item for item in previous if item.get("source") and item.get("link") not in links)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({"items": manifest}, f, ensure_ascii=False, indent=1)

    print("\nindirilen: %d  atlanan: %d  basarisiz: %d" % (ok, skip, fail))
    if fail:
        print("ayrintilar: tools/logs/worksheets.log")
    print("catalog guncelleniyor...")
    import subprocess
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch_catalog.py")],
                   check=False)


if __name__ == "__main__":
    main()
