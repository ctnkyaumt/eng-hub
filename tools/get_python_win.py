#!/usr/bin/env python3
"""Put a portable Python for Windows on the USB (runtime/python-win/).

Run once, on any machine with internet:  python tools/get_python_win.py

Start-Windows.bat prefers this copy, so ENG HUB then runs on Windows machines
that have no Python at all - no installer, no admin rights, no internet.
"""

import io
import os
import sys
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, UA, ensure  # noqa: E402

VERSION = "3.11.9"
URL = "https://www.python.org/ftp/python/%s/python-%s-embed-amd64.zip" % (VERSION, VERSION)
DEST = os.path.join(ROOT, "runtime", "python-win")


def main():
    if os.path.exists(os.path.join(DEST, "python.exe")):
        print("Zaten kurulu: %s" % DEST)
        return
    print("Indiriliyor: %s" % URL)
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        blob = r.read()
    ensure(DEST)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        z.extractall(DEST)

    # the embeddable build ships with imports restricted by a ._pth file;
    # enable site so the stdlib zip + our own paths resolve normally
    for name in os.listdir(DEST):
        if name.endswith("._pth"):
            path = os.path.join(DEST, name)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            text = text.replace("#import site", "import site")
            if "import site" not in text:
                text += "\nimport site\n"
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

    size = sum(os.path.getsize(os.path.join(DEST, f)) for f in os.listdir(DEST)
               if os.path.isfile(os.path.join(DEST, f)))
    print("Hazir: %s (%.1f MB)" % (DEST, size / 1e6))


if __name__ == "__main__":
    main()
