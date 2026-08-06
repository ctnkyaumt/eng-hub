#!/usr/bin/env python3
"""Render the theme PDFs in res/ into page images the app can show.

Run:  python tools/pdf_to_pages.py [--dpi 150] [--force]

res/<N>th grade/unit <M>/*.pdf  ->  content/g<N>/u<M>/presentation/pages/pNN.webp
plus a pages.json listing them. The rendered pages power the deck's
"Kaynak sayfalar" view, so the original MEB sheet is always one click away.

Needs PyMuPDF:  pip install pymupdf
"""

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, ROOT, ensure  # noqa: E402

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF gerekli:  pip install pymupdf")


def targets():
    """Yield (gid, uid, pdf_path) for everything under res/."""
    for path in sorted(glob.glob(os.path.join(ROOT, "res", "*", "*", "*.pdf"))):
        parts = path.replace("\\", "/").split("/")
        gm = re.search(r"(\d+)", parts[-3])
        um = re.search(r"(\d+)", parts[-2])
        if not gm or not um:
            continue
        yield "g%s" % gm.group(1), "u%s" % um.group(1), path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    n = 0
    for gid, uid, pdf in targets():
        out = os.path.join(CONTENT, gid, uid, "presentation", "pages")
        ensure(out)
        doc = fitz.open(pdf)
        names = []
        for i, page in enumerate(doc, 1):
            name = "p%02d.webp" % i
            dest = os.path.join(out, name)
            if args.force or not os.path.exists(dest):
                page.get_pixmap(dpi=args.dpi).pil_save(dest, format="WEBP", quality=82)
            names.append(name)
        with open(os.path.join(out, "pages.json"), "w", encoding="utf-8") as f:
            json.dump({"source": os.path.basename(pdf), "pages": names}, f, ensure_ascii=False)
        print("%s/%s  %2d sayfa  <- %s" % (gid, uid, len(names), os.path.basename(pdf)))
        n += 1
    print("%d unite islendi." % n)


if __name__ == "__main__":
    main()
