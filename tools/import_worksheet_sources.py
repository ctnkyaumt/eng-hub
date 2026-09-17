"""Import current-curriculum worksheet/test links from ingilizcecin.com (2020 and later).

Run:
    python tools/import_worksheet_sources.py

Fetches archive pages for grades 5 to 8, extracts date from span.elementor-post-date,
and saves items created in 2020 or later to app/data/worksheet-sources.json.
No local build. Links remain attributed online resources.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'app/data/worksheet-sources.json'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def read_json(path, fallback):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else fallback


def canonical(url):
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip('/'), parsed.query, ''))


def get_soup(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=18) as res:
        return BeautifulSoup(res.read().decode('utf-8', errors='replace'), 'html.parser'), res.url


def parse_year(date_str):
    if not date_str:
        return None
    m = re.search(r'\b(20\d\d)\b', date_str)
    return int(m.group(1)) if m else None


def scrape_unit(unit_key, base_url):
    page = 1
    items = []
    failures = []
    while True:
        url = base_url if page == 1 else f'{base_url}page/{page}/'
        try:
            soup, _ = get_soup(url)
        except Exception as exc:
            # 404 or connection termination -> end of pagination
            if page == 1:
                failures.append(dict(url=url, error=str(exc)))
            break

        articles = soup.select('article.elementor-post')
        if not articles:
            break

        all_before_2020 = True
        for art in articles:
            title_el = art.select_one('.elementor-post__title a')
            date_el = art.select_one('.elementor-post-date')
            author_el = art.select_one('.elementor-post-author')
            excerpt_el = art.select_one('.elementor-post__excerpt')
            img_el = art.select_one('img')

            title = title_el.get_text(strip=True) if title_el else ''
            link = title_el['href'].strip() if title_el and 'href' in title_el.attrs else ''
            date_str = date_el.get_text(strip=True) if date_el else ''
            author = author_el.get_text(strip=True) if author_el else ''
            excerpt = excerpt_el.get_text(' ', strip=True) if excerpt_el else ''
            img = (img_el.get('src') or img_el.get('data-src')) if img_el else ''

            if not title or not link:
                continue

            year = parse_year(date_str)
            if year is not None and year >= 2020:
                all_before_2020 = False
                item = {
                    'title': title,
                    'link': link,
                    'date': date_str,
                    'year': year,
                    'by': author or 'ingilizcecin.com',
                    'desc': excerpt,
                    'source': 'ingilizcecin',
                    'sourcePage': url,
                }
                if img and img.startswith('http'):
                    item['coverImage'] = img
                items.append(item)
            elif year is not None and year < 2020:
                pass
            else:
                all_before_2020 = False

        if all_before_2020:
            break

        next_link = soup.select_one('a.page-numbers.next, .elementor-pagination a.next')
        if not next_link:
            break
        page += 1

    # Deduplicate by canonical link while preserving order
    seen = set()
    deduped = []
    for it in items:
        clean = canonical(it['link'])
        if clean not in seen:
            seen.add(clean)
            deduped.append(it)

    return unit_key, deduped, failures


def get_target_units():
    targets = []
    # Grades 5 and 6 have 8 units in the current curriculum
    for g in [5, 6]:
        for u in range(1, 9):
            targets.append((f'g{g}/u{u}', f'https://www.ingilizcecin.com/{g}-sinif-ingilizce/{g}-sinif-ingilizce-{u}-unite/'))
    # Grades 7 and 8 have 10 units
    for g in [7, 8]:
        for u in range(1, 11):
            targets.append((f'g{g}/u{u}', f'https://www.ingilizcecin.com/{g}-sinif-ingilizce/{g}-sinif-ingilizce-{u}-unite/'))
    return targets


def main():
    targets = get_target_units()
    data = read_json(OUTPUT, {'units': {}, 'failures': []})
    existing_units = data.get('units', {})

    print(f'Starting import for {len(targets)} units from ingilizcecin.com...', flush=True)
    all_failures = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(scrape_unit, key, url): key for key, url in targets}
        for fut in as_completed(futures):
            key = futures[fut]
            try:
                unit_key, rows, failures = fut.result()
                if rows or unit_key not in existing_units:
                    existing_units[unit_key] = rows
                all_failures.extend(failures)
                print(f'{unit_key}: {len(existing_units[unit_key])} items (>=2020)', flush=True)
            except Exception as exc:
                print(f'{key}: error ({exc}), retaining existing', flush=True)
                all_failures.append(dict(unit=key, error=str(exc)))

    data['checkedAt'] = datetime.now(timezone.utc).isoformat()
    data['source'] = 'https://www.ingilizcecin.com'
    data['units'] = dict(sorted(existing_units.items()))
    data['failures'] = all_failures

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    total_items = sum(len(v) for v in data['units'].values())
    print(f'Done! Saved {total_items} items across {len(data["units"])} units to {OUTPUT.name}', flush=True)


if __name__ == '__main__':
    main()
