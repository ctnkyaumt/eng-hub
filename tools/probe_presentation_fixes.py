"""Regression probes for bilingual alignment and completed image coverage."""
import json
from pathlib import Path
from polish_slides import turkish_highlights

ROOT = Path(__file__).resolve().parents[1]
assert turkish_highlights('Routines', 'She *usually* listens to music.', 'Genellikle müzik dinler.') == ['Genellikle']
assert turkish_highlights('Routines', 'We *often* play basketball.', 'Sık sık basketbol oynarız.') == ['Sık sık']
assert turkish_highlights('Invitations', '*Would you like to* join our picnic?', 'Pikniğimize katılmak ister misin?') == ['ister misin']
assert turkish_highlights('Invitations', "*Why don't we* meet at the library?", 'Neden kütüphanede buluşmuyoruz?') == ['Neden', 'muyoruz']
assert turkish_highlights('New rule', 'An *unknown pattern* here.', 'Bütün cümle renklendirilmemeli.') == []
assert turkish_highlights('Unknown', 'I *love* apples.', 'Elma severim.') != ['Elma severim.']
assert turkish_highlights('Replies', '*Of course.*', 'Elbette.') == ['Elbette.']

words = pictures = 0
for path in (ROOT / 'content').glob('g*/u*/presentation/slides.json'):
    deck = json.loads(path.read_text('utf-8'))
    authored_g6 = path.parts[-4] == 'g6' and deck.get('authored') and deck.get('curriculum') == 'meb-english-6-2026'
    for slide in deck['slides']:
        if slide['type'] == 'vocab':
            for item in slide['items']:
                words += 1
                if item.get('num') is None and not (authored_g6 and item.get('textOnly') and item.get('imageNote')):
                    assert item.get('img'), (path, item['en'])
                    pictures += 1
                if item['en'].lower() == 'types of music':
                    assert item['img'] == '/app/img/concepts/types-of-music.svg'
        for example in slide.get('examples', []):
            if '*usually*' in example.get('en', ''):
                assert example['trEm'] == ['genellikle'], example
            if '*Would you like to*' in example.get('en', ''):
                assert example['trEm'] == ['ister misin'], example
print(f'PASS: precise Turkish highlights and {pictures} picture cards; {words-pictures} number/text cards.')
