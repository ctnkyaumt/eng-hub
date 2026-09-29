#!/usr/bin/env python3
"""ENG HUB - Otomatik Guncelleme CLI Baslaticisi."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# server/ klasorunu PYTHONPATH'e ekle
for cand in [os.path.join(HERE, "server"), os.path.join(HERE, "src", "server")]:
    if os.path.isdir(cand):
        sys.path.insert(0, cand)
        break

from updater import main

if __name__ == "__main__":
    main()
