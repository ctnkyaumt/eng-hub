"""Import current-curriculum game links and published preview images, not players.

python tools/import_game_sources.py [--skip-existing] [--reuse-thumbnails]
No build. Failed pages retain previously imported entries. Images stay remote.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
import argparse
import json
import re

from bs4 import BeautifulSoup
from requests.utils import requote_uri

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'app/data/game-sources.json'
ORIGIN = 'https://sumeyyeogultekin.com'
CURRICULA = {
    'g5': ORIGIN + '/grade/v/curriculums/5-maarifmodeli',
    'g6': ORIGIN + '/grade/vi/curriculums/6-maarifmodeli',
    'g7': ORIGIN + '/grade/vii/curriculums/7-guncel-mufredat',
    'g8': ORIGIN + '/grade/viii/curriculums/8-guncel-mufredat',
}
UA = 'Mozilla/5.0 (compatible; EngHubResourceCatalog/1.0)'


def read(path, fallback):
    return json.loads(path.read_text(encoding='utf8')) if path.exists() else fallback


def canonical(url):
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip('/'), parsed.query, ''))


def image_url(value, base):
    if not (value or '').strip():
        return None
    value = requote_uri(urljoin(base, (value or '').strip()))
    if urlsplit(value).scheme not in ('http', 'https'):
        return None
    if re.search(r'default-content-image|android-chrome|favicon|(?:^|/)logo[.\-_]', value, re.I):
        return None
    return value


def fetch(url, head_only=False):
    with urlopen(Request(url, headers={'User-Agent': UA}), timeout=18) as response:
        if 'html' not in response.headers.get('Content-Type', '').lower():
            raise ValueError('Not an HTML page')
        # Open Graph metadata is in the head; avoid downloading whole game pages.
        data = response.read(131072 if head_only else 2000000).decode('utf8', errors='replace')
        return BeautifulSoup(data, 'html.parser'), response.url


def unit_for(grade, label):
    if re.match(r'^revision\b', label, re.I):
        return grade + '/revision'
    match = re.match(r'^(?:theme|unit)[\s-]*(\d+)\b', label, re.I)
    if not match:
        return None
    number = int(match[1])
    if not 1 <= number <= (8 if grade in ('g5', 'g6') else 10):
        return None
    return grade + '/u' + str(number)


def listing_cards(soup, page, unit):
    rows = []
    for anchor in soup.select('.contents-list a[href]'):
        link = urljoin(page, anchor['href'])
        if not re.fullmatch(r'https://sumeyyeogultekin\.com/content/\d+', link):
            continue
        title_node = anchor.select_one('.content-title')
        picture = anchor.select_one('img')
        title = title_node.get_text(' ', strip=True) if title_node else (picture or {}).get('alt', '')
        if not title:
            continue
        row = dict(title=title, link=link, by='sumeyyeogultekin.com', source='sumeyyeogultekin', sourcePage=page)
        cover = image_url((picture.get('data-src') or picture.get('src')) if picture else '', page)
        if cover:
            row['coverImage'] = cover
        rows.append(row)
    return list({canonical(row['link']): row for row in rows}.values())


def discover(grade, url):
    soup, final = fetch(url)
    jobs = {}
    for anchor in soup.select('a[href]'):
        link = urljoin(final, anchor['href'])
        unit = unit_for(grade, anchor.get_text(' ', strip=True))
        if unit and '/units/' in link and link.endswith('/categories'):
            jobs[link] = (unit, link)
    if not jobs:
        raise ValueError('No current-curriculum unit links found')
    return list(jobs.values())


def import_listing(job):
    unit, category = job
    soup, final = fetch(category)
    links = [urljoin(final, a['href']) for a in soup.select('a[href]')
             if a['href'].rstrip('/') == category.removesuffix('/categories') + '/games']
    if not links:
        return unit, category, [], 'no-games'
    page = links[0]; visited = set(); rows = []
    while page:
        if page in visited:
            raise ValueError('Pagination loop')
        visited.add(page)
        soup, final = fetch(page)
        if not soup.select_one('.contents-list'):
            raise ValueError('Game listing missing; retaining earlier import')
        rows.extend(listing_cards(soup, final, unit))
        next_page = soup.select_one('a[rel="next"]')
        page = urljoin(final, next_page['href']) if next_page else None
    return unit, category, rows, 'ok'


def published_thumbnail(url):
    soup, final = fetch(url, head_only=True)
    for selector in ('meta[property="og:image"]', 'meta[name="twitter:image"]', 'link[rel="image_src"]'):
        tag = soup.select_one(selector)
        if tag:
            image = image_url(tag.get('content') or tag.get('href'), final)
            if image:
                return dict(coverImage=image, sourcePage=final)
    return None


def existing_links():
    links = set()
    for path in (ROOT/'content').glob('g*/*/games/bank.json'):
        links.update(item['link'] for item in read(path, {}).get('online', []) if item.get('link'))
    for path in (ROOT/'content').glob('g*/*/sites/manifest.json'):
        links.update(item['link'] for item in read(path, {}).get('items', []) if item.get('kind') == 'game' and item.get('link'))
    return sorted({canonical(link) for link in links if urlsplit(link).scheme in ('http', 'https')})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-existing', action='store_true')
    parser.add_argument('--reuse-thumbnails', action='store_true')
    args = parser.parse_args()
    data = read(OUTPUT, {'units': {}, 'thumbnails': {}, 'listings': {}})
    jobs = []; failures = []
    for grade, url in CURRICULA.items():
        try:
            jobs.extend(discover(grade, url))
        except Exception as exc:
            failures.append(dict(url=url, error=str(exc)))
    with ThreadPoolExecutor(4) as pool:
        futures = {pool.submit(import_listing, job): job for job in jobs}
        for future in as_completed(futures):
            unit, category = futures[future]
            try:
                _, _, rows, status = future.result()
                # Revision has two source pages; replace only the page just checked.
                listing_prefix = category.removesuffix('/categories') + '/games'
                old = [r for r in data['units'].get(unit, []) if not r.get('sourcePage', '').startswith(listing_prefix)]
                data['units'][unit] = list({canonical(r['link']):r for r in old + rows}.values())
                data['listings'][category] = dict(unit=unit, status=status, games=len(rows))
                print(f'{unit}: {len(rows)} games ({status})', flush=True)
            except Exception as exc:
                failures.append(dict(url=category, error=str(exc)))
                print(f'{unit}: source unavailable; retained previous entries', flush=True)
    if not args.skip_existing:
        urls = [url for url in existing_links() if not args.reuse_thumbnails or url not in data['thumbnails']]
        with ThreadPoolExecutor(5) as pool:
            futures = {pool.submit(published_thumbnail, url):url for url in urls}
            for n, future in enumerate(as_completed(futures), 1):
                url = futures[future]
                try:
                    result = future.result()
                    if result:
                        data['thumbnails'][url] = result
                except Exception as exc:
                    failures.append(dict(url=url, error=str(exc)))
                if n % 50 == 0 or n == len(urls):
                    print(f'Existing thumbnail checks: {n}/{len(urls)}; {len(data["thumbnails"])} previews', flush=True)
    data.update(checkedAt=datetime.now(timezone.utc).isoformat(), curricula=CURRICULA,
                units=dict(sorted(data['units'].items())), thumbnails=dict(sorted(data['thumbnails'].items())),
                listings=dict(sorted(data['listings'].items())), failures=failures)
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=1)+'\n', encoding='utf8')
    print(f'Saved {sum(len(x) for x in data["units"].values())} linked games, {len(data["thumbnails"])} existing previews; {len(failures)} unavailable pages.')


if __name__ == '__main__':
    main()
