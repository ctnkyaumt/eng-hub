#!/usr/bin/env python3
"""Refresh teaching sources without a local build or slide regeneration.

Run (needs internet):  python tools/refresh.py [--full]

Catalog, game banks, worksheet links, imported links and static activities are
fetched again. Failed requests retain working local copies. --full is accepted
for backwards compatibility; static activities are always refreshed.
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="statik siteleri de yeniden kopyala")
    ap.parse_args()

    # Source maintenance must refresh cached content, never regenerate lessons.
    subprocess.run([sys.executable, os.path.join(HERE, "refresh_sources.py")], check=True)


if __name__ == "__main__":
    main()
