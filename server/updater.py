#!/usr/bin/env python3
"""ENG HUB - Otomatik Guncelleme ve Gecis Motoru (Auto-Update & Migration).

GitHub Releases uzerinden en guncel ENG HUB surumunu denetler,
indirir, kullanici ozellestirmelerini (duzenlenen slaytlar, yuklenen resimler)
koruyarak ve tasiyarak uygulamayi gunceller.
Standart Python kutuphanesiyle calisir (ek paket gerektirmez).
"""

import json
import os
import re
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

REPO = "ctnkyaumt/eng-hub"
GITHUB_API_LATEST = f"https://api.github.com/repos/{REPO}/releases/latest"
UA = "ENG-HUB-Updater/1.0"
DEFAULT_FALLBACK_VERSION = "v1.7.0"


def find_root_paths():
    """Uygulamanin kok dizinini ve paket duzeninde (src/) olup olmadigini belirler."""
    here = os.path.dirname(os.path.abspath(__file__))  # server/
    parent = os.path.dirname(here)                     # eng-hub/ or src/

    # Durum 1: parent dizini 'src' ise, gercek paket koku bir ust dizindir
    if os.path.basename(parent).lower() == "src":
        app_root = os.path.dirname(parent)
        is_pkg_layout = True
    elif os.path.isdir(os.path.join(parent, "src", "server")):
        app_root = parent
        is_pkg_layout = True
    else:
        app_root = parent
        is_pkg_layout = False

    return app_root, is_pkg_layout


def get_current_version(app_root=None):
    """Mevcut surum bilgisini VERSION.txt dosyasindan okur."""
    if not app_root:
        app_root, is_pkg_layout = find_root_paths()
    else:
        is_pkg_layout = os.path.isdir(os.path.join(app_root, "src"))

    candidates = [
        os.path.join(app_root, "VERSION.txt"),
        os.path.join(app_root, "src", "VERSION.txt"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            try:
                with open(c, "r", encoding="utf-8") as f:
                    line = f.readline().strip()
                    if line:
                        parts = line.split()
                        return parts[0]
            except Exception:
                pass

    return DEFAULT_FALLBACK_VERSION


def parse_version(v_str):
    """'v1.7.0' veya '1.6' gibi surum dizgilerini karsilastirilabilir (major, minor, patch) demetine cevirir."""
    if not v_str:
        return (0, 0, 0)
    m = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", str(v_str).strip())
    if not m:
        return (0, 0, 0)
    major = int(m.group(1) or 0)
    minor = int(m.group(2) or 0)
    patch = int(m.group(3) or 0)
    return (major, minor, patch)


def is_newer(remote_v, local_v):
    return parse_version(remote_v) > parse_version(local_v)


def check_for_updates():
    """GitHub API'sinden en son surumu kontrol eder."""
    current_v = get_current_version()
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        GITHUB_API_LATEST,
        headers={
            "User-Agent": UA,
            "Accept": "application/vnd.github.v3+json",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            return {
                "ok": False,
                "error": "GitHub API istek siniri asildi. Lutfen biraz sonra tekrar deneyin.",
            }
        return {"ok": False, "error": f"GitHub sunucusundan hata alindi: HTTP {exc.code}"}
    except Exception as exc:
        return {"ok": False, "error": f"Baglanti kurulamadi: {exc}"}

    tag_name = data.get("tag_name", "").strip()
    name = data.get("name") or tag_name
    body = data.get("body", "").strip()
    published_at = data.get("published_at", "")

    # Uygun zip varligini sec (lite olmayan tam paket tercih edilir)
    assets = data.get("assets", [])
    selected_asset = None
    for a in assets:
        aname = a.get("name", "")
        if aname.endswith(".zip") and "-lite" not in aname:
            selected_asset = a
            break
    if not selected_asset and assets:
        for a in assets:
            if a.get("name", "").endswith(".zip"):
                selected_asset = a
                break

    download_url = selected_asset.get("browser_download_url") if selected_asset else None
    size_bytes = selected_asset.get("size", 0) if selected_asset else 0
    size_mb = round(size_bytes / (1024 * 1024), 1) if size_bytes else None

    update_available = is_newer(tag_name, current_v) if tag_name else False

    return {
        "ok": True,
        "currentVersion": current_v,
        "latestVersion": tag_name,
        "updateAvailable": update_available,
        "releaseName": name,
        "releaseNotes": body,
        "publishedAt": published_at,
        "downloadUrl": download_url,
        "assetName": selected_asset.get("name") if selected_asset else None,
        "sizeBytes": size_bytes,
        "sizeMb": size_mb,
    }


def safe_copy_file(src_path, dst_path):
    """Tek bir dosyayi kopyalar; Windows'ta kilitli dosyalar icin hata atlamasi yapar."""
    try:
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
    except (PermissionError, OSError):
        # Kilitli runtime dosyalari (calisan python.exe veya dll)
        pass


def copy_tree_safe(src_dir, dst_dir):
    """Klasor agacini guvenle kopyalar; mevcut ozel dosyalari silmez, kilitli dosyalarda takilmaz."""
    os.makedirs(dst_dir, exist_ok=True)
    for root, dirs, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        dest_root = os.path.join(dst_dir, rel)
        os.makedirs(dest_root, exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dest_file = os.path.join(dest_root, f)
            safe_copy_file(src_file, dest_file)


def download_file(url, dest_path, progress_cb=None):
    """Dosyayi 64KB'lik bloklar halinde indirir ve ilerlemeyi bildirir."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90, context=ctx) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            while True:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if progress_cb and total:
                    progress_cb("downloading", downloaded, total)


def apply_update(download_url=None, progress_cb=None):
    """Guncellemeyi indirir, kullanici verilerini koruyarak tasir ve uygular."""
    new_version = None
    if not download_url:
        info = check_for_updates()
        if not info.get("ok"):
            return info
        download_url = info.get("downloadUrl")
        new_version = info.get("latestVersion")

    if not download_url:
        return {"ok": False, "error": "Guncelleme paketi indirme adresi bulunamadi."}

    app_root, is_pkg_layout = find_root_paths()
    temp_dir = os.path.join(app_root, "temp_work", "update")
    zip_path = os.path.join(temp_dir, "update.zip")
    extract_dir = os.path.join(temp_dir, "extracted")

    try:
        # 1. Indirme
        if progress_cb:
            progress_cb("downloading", 0, 100)
        download_file(download_url, zip_path, progress_cb)

        # 2. Dogrulama ve Acma
        if progress_cb:
            progress_cb("extracting", 50, 100)
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # Zip icindeki kok klasor genelde 'eng-hub/' dir
        candidate_root = os.path.join(extract_dir, "eng-hub")
        if not os.path.isdir(candidate_root):
            candidate_root = extract_dir

        # 3. Gecis / Koruma (Migration): Ogretmenin duzenledigi slaytlari tespit et ve sakla
        if progress_cb:
            progress_cb("migrating", 75, 100)

        saved_user_slides = {}
        target_content_dir = os.path.join(app_root, "src", "content") if is_pkg_layout else os.path.join(app_root, "content")
        if os.path.isdir(target_content_dir):
            for root, dirs, files in os.walk(target_content_dir):
                if "slides.json.bak" in files and "slides.json" in files:
                    rel_dir = os.path.relpath(root, target_content_dir)
                    slides_file = os.path.join(root, "slides.json")
                    bak_file = os.path.join(root, "slides.json.bak")
                    try:
                        with open(slides_file, "r", encoding="utf-8") as sf:
                            saved_user_slides[rel_dir] = {
                                "slides": sf.read(),
                                "bak": open(bak_file, "rb").read(),
                            }
                    except Exception:
                        pass

        # 4. Kok baslaticilari ve betikleri guncelle
        for fname in [
            "Start-Windows.bat", "start-pardus.sh", "Refresh-Windows.bat",
            "refresh.py", "Update-Windows.bat", "updater.py", "README.md", "VERSION.txt"
        ]:
            src_f = os.path.join(candidate_root, fname)
            dst_f = os.path.join(app_root, fname)
            if os.path.isfile(src_f):
                safe_copy_file(src_f, dst_f)

        # 5. Program klasorlerini guncelle
        candidate_src = os.path.join(candidate_root, "src") if os.path.isdir(os.path.join(candidate_root, "src")) else candidate_root
        target_src = os.path.join(app_root, "src") if is_pkg_layout else app_root

        for item in ["app", "server", "tools", "content", "res", "memories", "VERSION.txt"]:
            src_item = os.path.join(candidate_src, item)
            dst_item = os.path.join(target_src, item)
            if os.path.isfile(src_item):
                safe_copy_file(src_item, dst_item)
            elif os.path.isdir(src_item):
                copy_tree_safe(src_item, dst_item)

        # 6. Ogretmenin duzenledigi slaytlari geri yukle (ve yeni kaynagi upstream olarak kaydet)
        for rel_dir, data in saved_user_slides.items():
            unit_dir = os.path.join(target_content_dir, rel_dir)
            if os.path.isdir(unit_dir):
                slides_file = os.path.join(unit_dir, "slides.json")
                bak_file = os.path.join(unit_dir, "slides.json.bak")
                upstream_file = os.path.join(unit_dir, "slides.upstream.json")
                if os.path.isfile(slides_file):
                    try:
                        shutil.copy2(slides_file, upstream_file)
                    except Exception:
                        pass
                try:
                    with open(slides_file, "w", encoding="utf-8") as sf:
                        sf.write(data["slides"])
                    with open(bak_file, "wb") as bf:
                        bf.write(data["bak"])
                except Exception:
                    pass

        # 7. VERSION.txt dosyasini guncelle
        if not new_version:
            new_version = get_current_version(candidate_root)
        stamp = f"{new_version}  {time.strftime('%Y-%m-%d')}\n"
        for v_path in [
            os.path.join(app_root, "VERSION.txt"),
            os.path.join(target_src, "VERSION.txt"),
        ]:
            try:
                with open(v_path, "w", encoding="utf-8") as vf:
                    vf.write(stamp)
            except Exception:
                pass

        if progress_cb:
            progress_cb("done", 100, 100)

        return {
            "ok": True,
            "message": f"ENG HUB basariyla {new_version} surumune guncellendi!",
            "newVersion": new_version,
        }
    except Exception as exc:
        return {"ok": False, "error": f"Guncelleme sirasinda hata olustu: {exc}"}
    finally:
        # Gecici dosyalari temizle
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            tw = os.path.join(app_root, "temp_work")
            if os.path.isdir(tw) and not os.listdir(tw):
                os.rmdir(tw)
        except Exception:
            pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ENG HUB Otomatik Guncelleme Araci")
    parser.add_argument("--check", action="store_true", help="Guncellemeleri denetle")
    parser.add_argument("--apply", action="store_true", help="Guncellemeyi indir ve kur")
    parser.add_argument("--version", action="store_true", help="Mevcut surumu goster")
    args = parser.parse_args()

    if args.version:
        print(f"ENG HUB Surumu: {get_current_version()}")
        return

    if args.check or not args.apply:
        print("Guncellemeler denetleniyor...")
        res = check_for_updates()
        if not res.get("ok"):
            print(f"Hata: {res.get('error')}", file=sys.stderr)
            sys.exit(1)
        print(f"Mevcut Surum : {res.get('currentVersion')}")
        print(f"En Son Surum : {res.get('latestVersion')}")
        if res.get("updateAvailable"):
            print(f"Yeni bir guncelleme mevcut: {res.get('releaseName')}")
            if res.get("sizeMb"):
                print(f"Boyut: ~{res.get('sizeMb')} MB")
            print("Guncellemek icin: python updater.py --apply")
        else:
            print("Surumunuz guncel.")
        return

    if args.apply:
        def pcb(status, cur, tot):
            pct = int(cur / tot * 100) if tot else 0
            sys.stdout.write(f"\r  [{status}] %{pct} ({cur}/{tot})")
            sys.stdout.flush()

        print("Guncelleme baslatiliyor...")
        res = apply_update(progress_cb=pcb)
        print()
        if res.get("ok"):
            print(res.get("message"))
        else:
            print(f"Guncelleme basarisiz: {res.get('error')}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
