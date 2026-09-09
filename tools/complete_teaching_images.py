"""Apply reviewed Commons photos and original meaning diagrams, without a build."""
import html
import json
from pathlib import Path
from concept_scenes import scenes

ROOT = Path(__file__).resolve().parents[1]


def main():
    diagrams = scenes()
    commons = json.loads((ROOT / 'app/img/commons-teaching-sources.json').read_text('utf-8'))
    symbols = {'fresh': 37842, 'emergency': 37501, 'take care of a pet': 34308}
    missing = set()
    for path in sorted((ROOT / 'content').glob('g*/u*/presentation/slides.json')):
        data = json.loads(path.read_text('utf-8'))
        for slide in data['slides']:
            if slide['type'] != 'vocab':
                continue
            for item in slide['items']:
                word = item['en'].lower()
                if word in commons:
                    item.update(img=commons[word]['img'], imageSource='Wikimedia Commons', imageFit='contain', imageConcept=word)
                elif word in diagrams:
                    item.update(img=diagrams[word], imageSource='ENG HUB', imageFit='contain', imageConcept=word)
                elif word in symbols:
                    pid = symbols[word]
                    item.update(img=f'https://static.arasaac.org/pictograms/{pid}/{pid}_500.png', imageSource='ARASAAC', imageFit='contain', imageConcept=word)
                elif not item.get('img') and item.get('num') is None:
                    missing.add(word)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), 'utf-8')
    credits = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>Teaching photo credits</title>',
               '<style>body{max-width:850px;margin:40px auto;padding:20px;font:18px/1.6 system-ui}a{color:#096b91}article{border-bottom:1px solid #ddd;padding:16px 0}</style>',
               '<h1>Teaching photo credits</h1><p>Photos linked from Wikimedia Commons. Originals are unchanged; displayed proportionally.</p>']
    for word, item in commons.items():
        e = {k:html.escape(v, quote=True) for k,v in item.items()}
        license_text = f'<a href="{e["licenseUrl"]}">{e["license"]}</a>' if e['licenseUrl'] else e['license']
        credits.append(f'<article><h2>{html.escape(word)}</h2><a href="{e["source"]}">{e["title"]}</a><p>{e["author"]} · {license_text}</p></article>')
    credits.append('</html>')
    (ROOT / 'app/img/teaching-credits.html').write_text('\n'.join(credits), 'utf-8')
    assert not missing, f'Missing images: {sorted(missing)}'
    print(f'Applied {len(commons)} Commons mappings, {len(diagrams)} original scenes, {len(symbols)} symbols. No missing nonnumeric vocabulary images.')


if __name__ == '__main__':
    main()
