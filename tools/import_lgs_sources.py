"""Import LGS resources from:
- https://www.ingilizceciyiz.com/lgs-ingilizce-ornek-sorular/
- https://www.ingilizceciyiz.com/lgs-ingilizce-deneme-sinavlari/
- https://www.ingilizceciyiz.com/lgs-ingilizce-sorulari/
- and all from https://www.dersingilizce.org/lgsfiles

Run:
    python tools/import_lgs_sources.py
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup
import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'app/data/lgs-sources.json'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'


def clean_title(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    # Strip common redundant suffixes
    text = re.sub(r'\s*(?:İÇİN TIKLAYINIZ|TIKLAYINIZ|İNDİR|PDF İNDİR)\s*$', '', text, flags=re.I)
    return text.strip()


def canonical(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), parts.query, ''))


def scrape_ingilizceciyiz_ornek(session: requests.Session) -> list:
    url = 'https://www.ingilizceciyiz.com/lgs-ingilizce-ornek-sorular/'
    print(f'Scraping {url}...', flush=True)
    r = session.get(url, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find('div', class_='entry-content') or soup

    items = []
    seen = set()
    for a in content.find_all('a', href=True):
        href = a['href'].strip()
        txt = clean_title(a.get_text(' ', strip=True))
        if not txt or href.startswith('#') or 'wp-admin' in href:
            continue

        # If it's a subpage for a specific monthly test, resolve to the PDF inside
        if 'lgs-ingilizce-ornek-sorulari' in href and not href.endswith('.pdf'):
            try:
                sub_r = session.get(href, timeout=10)
                sub_soup = BeautifulSoup(sub_r.text, 'html.parser')
                pdf_a = sub_soup.find('a', href=re.compile(r'\.pdf$', re.I))
                if pdf_a:
                    href = pdf_a['href'].strip()
            except Exception as e:
                print(f'  Failed resolving subpage {href}: {e}', flush=True)

        if '.pdf' in href.lower() or 'uploads' in href.lower():
            can = canonical(href)
            if can not in seen:
                seen.add(can)
                by = 'MEB' if 'meb' in txt.lower() or 'meb' in href.lower() else 'ingilizceciyiz.com'
                items.append({
                    'title': txt,
                    'link': href,
                    'by': by,
                    'desc': 'LGS İngilizce Örnek Soruları',
                    'source': 'ingilizceciyiz',
                    'sourcePage': url,
                })
    print(f'ingilizceciyiz ornek: {len(items)} items', flush=True)
    return items


def scrape_ingilizceciyiz_deneme(session: requests.Session) -> list:
    url = 'https://www.ingilizceciyiz.com/lgs-ingilizce-deneme-sinavlari/'
    print(f'Scraping {url}...', flush=True)
    r = session.get(url, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find('div', class_='entry-content') or soup

    items = []
    seen = set()

    for a in content.find_all('a', href=True):
        href = a['href'].strip()
        txt = clean_title(a.get_text(' ', strip=True))
        if not txt or href.startswith('#') or 'wp-admin' in href:
            continue

        if '8-sinif-ingilizce-1-unite-deneme-sinavi' in href:
            try:
                sub_r = session.get(href, timeout=10)
                sub_soup = BeautifulSoup(sub_r.text, 'html.parser')
                for sa in sub_soup.find_all('a', href=re.compile(r'\.pdf$', re.I)):
                    s_href = sa['href'].strip()
                    s_txt = clean_title(sa.get_text(' ', strip=True))
                    s_can = canonical(s_href)
                    if s_can not in seen:
                        seen.add(s_can)
                        items.append({
                            'title': s_txt or '8. Sınıf 1. Ünite Deneme Sınavı',
                            'link': s_href,
                            'by': 'ingilizceciyiz.com',
                            'desc': '1. Ünite Deneme Sınavı',
                            'source': 'ingilizceciyiz',
                            'sourcePage': href,
                        })
            except Exception as e:
                print(f'  Failed resolving subpage {href}: {e}', flush=True)
            continue

        if '.pdf' in href.lower() or 'uploads' in href.lower():
            can = canonical(href)
            if can not in seen:
                seen.add(can)
                # Detect author if present (e.g. BY HAKTAN KIRKKESELİ, BY ALTIN ORAN, etc.)
                m_by = re.search(r'\bby\s+([^,–—\(\)]+)', txt, flags=re.I)
                by = m_by.group(1).strip() if m_by else 'ingilizceciyiz.com'
                items.append({
                    'title': txt,
                    'link': href,
                    'by': by,
                    'desc': 'LGS İngilizce Deneme Sınavı',
                    'source': 'ingilizceciyiz',
                    'sourcePage': url,
                })
    print(f'ingilizceciyiz deneme: {len(items)} items', flush=True)
    return items


def scrape_ingilizceciyiz_cikmis(session: requests.Session) -> list:
    url = 'https://www.ingilizceciyiz.com/lgs-ingilizce-sorulari/'
    print(f'Scraping {url}...', flush=True)
    r = session.get(url, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find('div', class_='entry-content') or soup

    items = []
    seen = set()

    for a in content.find_all('a', href=True):
        href = a['href'].strip()
        txt = clean_title(a.get_text(' ', strip=True))
        if not txt or 'wp-admin' in href or href.startswith('#'):
            continue

        # Look for yearly question links (2018-2026)
        m_year = re.search(r'(20\d\d)\s+LGS', txt, flags=re.I)
        if not m_year and not href.endswith('.pdf'):
            continue

        pdf_link = None
        if href.endswith('.pdf') or 'uploads' in href:
            pdf_link = href
        elif re.search(r'20\d\d-lgs-ingilizce-sorulari', href):
            try:
                sub_r = session.get(href, timeout=10)
                sub_soup = BeautifulSoup(sub_r.text, 'html.parser')
                pdf_a = sub_soup.find('a', href=re.compile(r'\.pdf$', re.I))
                if pdf_a:
                    pdf_link = pdf_a['href'].strip()
            except Exception as e:
                print(f'  Failed resolving cikmis subpage {href}: {e}', flush=True)

        if pdf_link:
            can = canonical(pdf_link)
            if can not in seen:
                seen.add(can)
                year_match = re.search(r'(20\d\d)', txt) or re.search(r'(20\d\d)', pdf_link)
                year_str = year_match.group(1) if year_match else ''
                title = f'{year_str} LGS İngilizce Çıkmış Soruları ve Cevapları' if year_str else txt
                items.append({
                    'title': title,
                    'link': pdf_link,
                    'by': 'MEB ÖDSGM',
                    'desc': f'{year_str} LGS Çıkmış Sınav Kitapçığı ve Cevapları' if year_str else 'LGS Çıkmış Sorular',
                    'source': 'ingilizceciyiz',
                    'sourcePage': url,
                })

    # Sort reverse chronologically by year if possible
    def get_year(it):
        m = re.search(r'(20\d\d)', it['title'])
        return int(m.group(1)) if m else 0
    items.sort(key=get_year, reverse=True)

    print(f'ingilizceciyiz cikmis: {len(items)} items', flush=True)
    return items


def scrape_dersingilizce_all(session: requests.Session) -> dict:
    """Scrapes all 6 sections linked from https://www.dersingilizce.org/lgsfiles."""
    sections = {
        'dersingilizce-cikmis': {
            'title': 'LGS Çıkmış Sorular',
            'subtitle': '2018 - 2026 LGS İngilizce Çıkmış Sorular Arşivi',
            'emoji': '🏆',
            'url': 'https://www.dersingilizce.org/lgssorular',
            'desc': 'Çıkmış Sorular',
        },
        'dersingilizce-ornek': {
            'title': 'LGS MEB Örnek Soruları',
            'subtitle': '1-10. Ünite MEB Örnek Soruları ve Cevap Anahtarı',
            'emoji': '📝',
            'url': 'https://www.dersingilizce.org/orneksorular',
            'desc': 'MEB Örnek Soruları',
        },
        'dersingilizce-deneme': {
            'title': 'LGS Deneme Sınavları',
            'subtitle': 'Ünite Bazlı LGS Deneme Sınavları',
            'emoji': '📑',
            'url': 'https://www.dersingilizce.org/deneme',
            'desc': 'Deneme Sınavı',
        },
        'dersingilizce-kelime': {
            'title': 'LGS Kelime Testleri (PDF)',
            'subtitle': 'Ünite Sonu Kelime Değerlendirme Testleri',
            'emoji': '🔤',
            'url': 'https://www.dersingilizce.org/vocabularytest',
            'desc': 'Kelime Testi (PDF)',
        },
        'dersingilizce-online': {
            'title': 'Online Kelime Testleri',
            'subtitle': 'İnteraktif Wordwall Kelime Testleri',
            'emoji': '🎮',
            'url': 'https://www.dersingilizce.org/onlinetests',
            'desc': 'Online Kelime Testi',
        },
        'dersingilizce-worksheets': {
            'title': 'LGS Çalışma Kâğıtları ve Etkinlikler',
            'subtitle': '8. Sınıf LGS Worksheets, Revision ve Kelime Listeleri',
            'emoji': '📄',
            'url': 'https://www.dersingilizce.org/worksheets',
            'desc': 'Çalışma Kâğıdı ve Test',
        },
    }

    results = {}
    for sec_id, sec_info in sections.items():
        url = sec_info['url']
        print(f'Scraping dersingilizce {sec_id} from {url}...', flush=True)
        r = session.get(url, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = []
        seen = set()

        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            txt = clean_title(a.get_text(' ', strip=True))

            # If text is 'Star' or empty or icon, check parent or sibling container
            if not txt or txt.lower() in ('star', 'download', 'indir', 'tıklayınız'):
                parent = a.find_parent(['p', 'div', 'tr', 'li', 'td'])
                if parent:
                    p_txt = clean_title(parent.get_text(' ', strip=True))
                    if p_txt and p_txt.lower() not in ('star', 'download', 'indir', 'tıklayınız'):
                        txt = p_txt

            # Fix malformed drive link if two URLs were concatenated in page HTML
            if 'drive.google.com' in href:
                # E.g. https://drive.google.com/...https://drive.google.com/file/d/.../view
                all_drive = re.findall(r'https?://drive\.google\.com/file/d/[a-zA-Z0-9_-]+(?:/view(?:\?[^\s\"\']*)?)?', href)
                if all_drive:
                    href = all_drive[-1]  # Pick the actual target
                    if not href.endswith('/view') and '?' not in href:
                        href = href + '/view'

            if any(x in href for x in ['drive.google.com', '.pdf', 'docs.google', 'wordwall.net']) or ('test' in href and 'dersingilizce.org' not in href):
                can = canonical(href)
                if can not in seen and txt:
                    seen.add(can)
                    # For dersingilizce çıkmış sorular, ensure title is formatted cleanly
                    m_yr = re.search(r'(20\d\d)', txt)
                    if sec_id == 'dersingilizce-cikmis' and m_yr:
                        txt = f"{m_yr.group(1)} LGS İngilizce Soruları"

                    by = 'MEB' if 'meb' in txt.lower() or 'meb' in href.lower() else 'dersingilizce.org'
                    items.append({
                        'title': txt,
                        'link': href,
                        'by': by,
                        'desc': sec_info['desc'],
                        'source': 'dersingilizce',
                        'sourcePage': url,
                    })

        # Sort çıkmış sorular reverse chronologically
        if sec_id == 'dersingilizce-cikmis':
            def get_year(it):
                m = re.search(r'(20\d\d)', it['title'])
                return int(m.group(1)) if m else 0
            items.sort(key=get_year, reverse=True)

        results[sec_id] = {
            **sec_info,
            'items': items,
        }
        print(f'  -> {sec_id}: {len(items)} items', flush=True)

    return results


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': UA})

    # 1. Scrape ingilizceciyiz
    ing_ornek = scrape_ingilizceciyiz_ornek(session)
    ing_deneme = scrape_ingilizceciyiz_deneme(session)
    ing_cikmis = scrape_ingilizceciyiz_cikmis(session)

    # 2. Scrape dersingilizce
    ders_sections = scrape_dersingilizce_all(session)

    # 3. Assemble structured data
    sources = [
        {
            'id': 'ingilizceciyiz-ornek',
            'provider': 'ingilizceciyiz',
            'providerTitle': 'ingilizceciyiz.com',
            'title': 'LGS İngilizce Örnek Sorular',
            'subtitle': 'MEB ve yazar örnek soruları (ay ve yıl bazında)',
            'emoji': '📝',
            'sourceUrl': 'https://www.ingilizceciyiz.com/lgs-ingilizce-ornek-sorular/',
            'items': ing_ornek,
        },
        {
            'id': 'ingilizceciyiz-deneme',
            'provider': 'ingilizceciyiz',
            'providerTitle': 'ingilizceciyiz.com',
            'title': 'LGS İngilizce Deneme Sınavları',
            'subtitle': 'Sarmal, ünite ve genel LGS deneme sınavları',
            'emoji': '📑',
            'sourceUrl': 'https://www.ingilizceciyiz.com/lgs-ingilizce-deneme-sinavlari/',
            'items': ing_deneme,
        },
        {
            'id': 'ingilizceciyiz-cikmis',
            'provider': 'ingilizceciyiz',
            'providerTitle': 'ingilizceciyiz.com',
            'title': 'LGS İngilizce Çıkmış Sorular',
            'subtitle': '2018 - 2026 LGS İngilizce sınavları ve cevap anahtarları',
            'emoji': '🏆',
            'sourceUrl': 'https://www.ingilizceciyiz.com/lgs-ingilizce-sorulari/',
            'items': ing_cikmis,
        },
        {
            'id': 'dersingilizce-cikmis',
            'provider': 'dersingilizce',
            'providerTitle': 'dersingilizce.org',
            'title': ders_sections['dersingilizce-cikmis']['title'],
            'subtitle': ders_sections['dersingilizce-cikmis']['subtitle'],
            'emoji': ders_sections['dersingilizce-cikmis']['emoji'],
            'sourceUrl': ders_sections['dersingilizce-cikmis']['url'],
            'hubUrl': 'https://www.dersingilizce.org/lgsfiles',
            'items': ders_sections['dersingilizce-cikmis']['items'],
        },
        {
            'id': 'dersingilizce-ornek',
            'provider': 'dersingilizce',
            'providerTitle': 'dersingilizce.org',
            'title': ders_sections['dersingilizce-ornek']['title'],
            'subtitle': ders_sections['dersingilizce-ornek']['subtitle'],
            'emoji': ders_sections['dersingilizce-ornek']['emoji'],
            'sourceUrl': ders_sections['dersingilizce-ornek']['url'],
            'hubUrl': 'https://www.dersingilizce.org/lgsfiles',
            'items': ders_sections['dersingilizce-ornek']['items'],
        },
        {
            'id': 'dersingilizce-deneme',
            'provider': 'dersingilizce',
            'providerTitle': 'dersingilizce.org',
            'title': ders_sections['dersingilizce-deneme']['title'],
            'subtitle': ders_sections['dersingilizce-deneme']['subtitle'],
            'emoji': ders_sections['dersingilizce-deneme']['emoji'],
            'sourceUrl': ders_sections['dersingilizce-deneme']['url'],
            'hubUrl': 'https://www.dersingilizce.org/lgsfiles',
            'items': ders_sections['dersingilizce-deneme']['items'],
        },
        {
            'id': 'dersingilizce-kelime',
            'provider': 'dersingilizce',
            'providerTitle': 'dersingilizce.org',
            'title': ders_sections['dersingilizce-kelime']['title'],
            'subtitle': ders_sections['dersingilizce-kelime']['subtitle'],
            'emoji': ders_sections['dersingilizce-kelime']['emoji'],
            'sourceUrl': ders_sections['dersingilizce-kelime']['url'],
            'hubUrl': 'https://www.dersingilizce.org/lgsfiles',
            'items': ders_sections['dersingilizce-kelime']['items'],
        },
        {
            'id': 'dersingilizce-online',
            'provider': 'dersingilizce',
            'providerTitle': 'dersingilizce.org',
            'title': ders_sections['dersingilizce-online']['title'],
            'subtitle': ders_sections['dersingilizce-online']['subtitle'],
            'emoji': ders_sections['dersingilizce-online']['emoji'],
            'sourceUrl': ders_sections['dersingilizce-online']['url'],
            'hubUrl': 'https://www.dersingilizce.org/lgsfiles',
            'items': ders_sections['dersingilizce-online']['items'],
        },
        {
            'id': 'dersingilizce-worksheets',
            'provider': 'dersingilizce',
            'providerTitle': 'dersingilizce.org',
            'title': ders_sections['dersingilizce-worksheets']['title'],
            'subtitle': ders_sections['dersingilizce-worksheets']['subtitle'],
            'emoji': ders_sections['dersingilizce-worksheets']['emoji'],
            'sourceUrl': ders_sections['dersingilizce-worksheets']['url'],
            'hubUrl': 'https://www.dersingilizce.org/lgsfiles',
            'items': ders_sections['dersingilizce-worksheets']['items'],
        },
    ]

    total_items = sum(len(s['items']) for s in sources)
    ing_count = sum(len(s['items']) for s in sources if s['provider'] == 'ingilizceciyiz')
    ders_count = sum(len(s['items']) for s in sources if s['provider'] == 'dersingilizce')

    payload = {
        'updatedAt': datetime.now(timezone.utc).isoformat(),
        'hubUrls': {
            'ingilizceciyiz': [
                'https://www.ingilizceciyiz.com/lgs-ingilizce-ornek-sorular/',
                'https://www.ingilizceciyiz.com/lgs-ingilizce-deneme-sinavlari/',
                'https://www.ingilizceciyiz.com/lgs-ingilizce-sorulari/',
            ],
            'dersingilizce': 'https://www.dersingilizce.org/lgsfiles',
        },
        'counts': {
            'total': total_items,
            'ingilizceciyiz': ing_count,
            'dersingilizce': ders_count,
        },
        'sources': sources,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Successfully wrote {OUTPUT}!')
    print(f'Total: {total_items} items (ingilizceciyiz: {ing_count}, dersingilizce: {ders_count})')


if __name__ == '__main__':
    main()
