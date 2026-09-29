#!/usr/bin/env python3
"""ENG HUB - Kaynak Yenileme Araci (Refresh Sources).

Kullanim:
    python refresh.py [--full]

Bu betik eltarena ve diger kaynaklardaki yeni kitap sunumlarini,
calisma kagitlarini ve oyun kataloglarini gunceller.
Standart Python kutuphanesiyle calisir (ek paket gerektirmez).
"""

import argparse
import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def find_app_root():
    here = os.path.dirname(os.path.abspath(__file__))
    # Durum 1: Paket kokunde ise (src/tools/fetch_catalog.py mevcut)
    if os.path.isfile(os.path.join(here, "src", "tools", "fetch_catalog.py")):
        return os.path.join(here, "src")
    # Durum 2: Repo kokunde ise (tools/fetch_catalog.py mevcut)
    if os.path.isfile(os.path.join(here, "tools", "fetch_catalog.py")):
        return here
    # Durum 3: src veya server icinden cagrildiysa
    parent = os.path.dirname(here)
    if os.path.isfile(os.path.join(parent, "tools", "fetch_catalog.py")):
        return parent
    return here


def run_refresh(full=False):
    app_root = find_app_root()
    tools_dir = os.path.join(app_root, "tools")
    fetch_catalog = os.path.join(tools_dir, "fetch_catalog.py")

    if not os.path.isfile(fetch_catalog):
        raise FileNotFoundError(f"fetch_catalog.py bulunamadi: {fetch_catalog}")

    print("ENG HUB kaynak katalogu guncelleniyor...", flush=True)
    subprocess.run([sys.executable, fetch_catalog, "--refresh"], cwd=app_root, check=True)

    if full:
        refresh_sources = os.path.join(tools_dir, "refresh_sources.py")
        if os.path.isfile(refresh_sources):
            try:
                import requests  # noqa: F401
                print("Tam kaynak yenilemesi yapiliyor (oyun havuzlari ve statik siteler)...", flush=True)
                subprocess.run([sys.executable, refresh_sources], cwd=app_root, check=True)
            except ImportError:
                print("Not: 'requests' modulu bulunamadigi icin tam yenileme atlandi, katalog basariyla guncellendi.", flush=True)

    return {"ok": True, "message": "Kaynaklar basariyla guncellendi."}


def main():
    parser = argparse.ArgumentParser(description="ENG HUB kaynaklarini yeniler.")
    parser.add_argument("--full", action="store_true", help="Oyun havuzlarini ve statik kopyalari da tara (ek paketler gerekir)")
    args = parser.parse_args()

    try:
        run_refresh(full=args.full)
        print("\nTamamlandi! Kaynaklar guncel.", flush=True)
    except Exception as exc:
        print(f"\nHata olustu: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
