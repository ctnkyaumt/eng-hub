"""Download the explicitly selected Grade 6 illustrations; never search or guess.

The reviewed word senses and credits live in grade6-image-choices.json.
Existing files and the source/reference PowerPoints are never changed.
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    images = json.loads((ROOT / 'tools/grade6-image-choices.json').read_text(encoding='utf-8'))
    targets = {}
    for item in images.values():
        match = re.fullmatch(r'/content/g6/shared/img/(\d+)\.png', item['img'])
        if match:
            targets[match[1]] = ROOT / item['img'].lstrip('/')
    def fetch(pair):
        pid, dest = pair
        if dest.exists():
            return
        url = f'https://static.arasaac.org/pictograms/{pid}/{pid}_500.png'
        request = urllib.request.Request(url, headers={'User-Agent':'ENG-HUB classroom materials'})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
        except Exception as exc:
            raise RuntimeError(f'{pid}: {exc}') from exc
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError(url)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(fetch, targets.items()))
    print(f'{len(targets)} local ARASAAC illustrations available.')


if __name__ == '__main__':
    main()
