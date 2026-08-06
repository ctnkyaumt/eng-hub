#!/usr/bin/env python3
"""Rebuild everything from the source in the right order.

Run (needs internet):  python tools/refresh.py [--full]

  default : catalog -> PDF pages -> game banks -> worksheets -> catalog -> check
  --full  : also re-mirror the static activity sites (slow)

Every step is resumable: files already on the USB are skipped.
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script, *args):
    print("\n=== %s %s ===" % (script, " ".join(args)))
    r = subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=False)
    if r.returncode:
        print("!! %s hata verdi (kod %d) - devam ediliyor" % (script, r.returncode))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="statik siteleri de yeniden kopyala")
    args = ap.parse_args()

    run("fetch_catalog.py", "--refresh")
    run("pdf_to_pages.py")
    run("fetch_games.py")
    run("fetch_worksheets.py")
    if args.full:
        run("mirror_sites.py")
    run("fetch_catalog.py")
    run("verify_content.py")


if __name__ == "__main__":
    main()
