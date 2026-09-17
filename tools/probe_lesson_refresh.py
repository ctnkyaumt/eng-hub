"""Probe authored lesson changes and local activity behavior, without a build."""
from pathlib import Path
import collections
import copy
import json
import subprocess
from lesson_refresh import enhance_slides, highlights, plain, cloze_rows
from book_alignment import align_slides, SECTIONS, source_ref

ROOT=Path(__file__).resolve().parents[1]
paths=sorted((ROOT/'content').glob('g*/*/presentation/slides.json'))
assert len(paths)==27
assert not list((ROOT/'content/g7').glob('*/presentation/slides.json'))
assert not (ROOT/'content/g5/revision/presentation/slides.json').exists()
counts=collections.Counter(); ranges=0
for path in paths:
    deck=json.loads(path.read_text(encoding='utf-8')); slides=deck['slides']
    unit='/'.join(path.parts[-4:-2])
    assert enhance_slides(slides,unit)==slides, (path,'regeneration changed payload')
    assert enhance_slides(align_slides(slides,unit),unit)==slides, (path,'book regeneration changed payload')
    if unit in SECTIONS:
        for section in SECTIONS[unit]:
            pages=[s for s in slides if s.get('bookAlignment') and s['title']==section['title']]
            assert len(pages)==len(section['examples'])
            assert all(s['bookSource']==source_ref(unit) for s in pages)
        if unit=='g8/u9':
            titles=[s['title'] for s in slides if s['type']=='grammar']
            assert titles.index('Science now — Present Continuous')<titles.index('Passive Voice — Present')
    original=[s for s in slides if not s.get('lessonRefresh')]
    words={w['en'] for s in original if s['type']=='vocab' for w in s['items']}
    sentences={plain(e['en']) for s in original for e in s.get('examples',[])}
    assert slides[-1]['type']=='end'
    added=[s for s in slides if s.get('lessonRefresh')]
    assert {'topic','unit'}=={s['activityScope'] for s in added}
    assert {'wordpairs','cloze','groupsort','quizbox'} <= {s['task']['kind'] for s in added}
    for s in added:
        t=s['task'];kind=t['kind'];counts[kind]+=1
        assert 'http' not in json.dumps(t), (path,'new activity requires network')
        if kind=='wordpairs':
            assert 3<=len(t['pairs'])<=6
            assert len({p['a'].lower() for p in t['pairs']})==len({p['b'].lower() for p in t['pairs']})==len(t['pairs'])
            assert all(p['a'] in words for p in t['pairs'])
        elif kind=='groupsort':
            rows=[w for g in t['groups'] for w in g['items']]
            assert 2<=len(t['groups'])<=3 and len(set(rows))==len(rows)
            assert all(w in words for w in rows)
            assert all(not g['label'].startswith('More Words') for g in t['groups'])
        elif kind=='cloze':
            assert 1<=len(t['sentences'])<=5
            for row in t['sentences']:
                assert row['text'].count('___')==1 and row['answer']
                assert row['text'].replace('___',row['answer']) in sentences
        elif kind=='quizbox':
            assert 1<=len(t['questions'])<=8
            assert all(q['q'] and q['answer'] for q in t['questions'])
    for slide in slides:
        if slide['type']=='vocab': assert slide['visualSequence']=='picture-label-swap'
        for example in slide.get('examples',[]):
            for lang in ('en','tr'):
                source=plain(example.get(lang,''));marks=example.get(lang+'Highlights',[])
                previous=0
                for mark in marks:
                    assert previous<=mark['start']<mark['end']<=len(source)
                    previous=mark['end']; ranges+=1
    if path.parts[-4]=='g6':
        alignment=json.loads((ROOT/'content/g6/curriculum.json').read_text(encoding='utf-8'))
        assert next(u['slides'] for u in alignment['units'] if u['id']==path.parts[-3])==len(slides)

for en,tr,phrases,title,expected in [
    ('She *usually* reads.','Genellikle okur.',['Genellikle'],'Routines','usually'),
    ("He *does not* swim.",'Yüzmez.',['mez'],'Simple Present','negative'),
    ('*Does* he swim?','Yüzer mi?',['mi'],'Questions','question'),
    ('She *plays* chess.','Satranç oynar.',['ar'],'Simple Present','ending'),
    ('She is *reading*.','Okuyor.',['uyor'],'Present Continuous','ending'),
]:
    e=dict(en=en,tr=tr,trEm=phrases); highlights(e,title)
    assert e['enHighlights'][0]['role']==expected
    assert e['trHighlights'][0]['role']==expected
    if 'plays' in en: assert plain(en)[e['enHighlights'][0]['start']:e['enHighlights'][0]['end']]=='s'
e=dict(en='They *are doing* an experiment.',tr='Deney yapıyorlar.',trEm=['ıyorlar'])
highlights(e,'Present Continuous')
assert [m['role'] for m in e['enHighlights']]==['form','ending']
assert plain(e['en'])[e['enHighlights'][1]['start']:e['enHighlights'][1]['end']]=='ing'
assert e['trHighlights'][0]['role']=='ending'
assert cloze_rows([dict(en='e düşer: ride → *riding*',tr='1. kural')],3)==[]
subprocess.run(['node',str(ROOT/'tools/probe_lesson_refresh.mjs')],check=True)
print(f'PASS: {len(paths)} existing decks, {sum(counts.values())} activities {dict(counts)}, {ranges} exact highlight ranges; content provenance and stable regeneration.')
