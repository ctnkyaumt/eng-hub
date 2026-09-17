"""Enrich existing lessons only. Reproducible, no external resources or build.

Style reference: teacher's PowerPoints in ref_materials/slides.
Curriculum: newest books in ref_materials/books (see book_alignment.py).
Activity formats inspired by the five sumeyyeogultekin.com links in README.
All questions reuse this lesson's authored language, never remote game content.
"""
from pathlib import Path
import copy
import json
import re
from collections import OrderedDict

ROOT = Path(__file__).resolve().parents[1]
FREQUENCY = {'always':'always','usually':'usually','normally':'usually','often':'often',
             'sometimes':'sometimes','never':'negative'}

# Meaningful categories, not the page on which an item happened to appear.
# Especially avoid "More Words 1" and two halves of the same vocabulary list.
SORT_GROUPS = {
    'g5/u4': [('Family members',['grandfather','grandmother','cousin']),('Daily routines',['wake up','brush teeth','have breakfast'])],
    'g5/u6': [('Vegetables',['pepper','cucumber','tomato']),('Drinks',['water','milk','ayran']),('Kitchen tools',['bowl','pan','pot'])],
    'g6/u1': [('People',['leader','listener','guide']),('School actions',['greet','follow','enter']),('Celebrations',['ceremony','celebration','parade'])],
    'g6/u2': [('Study actions',['review','revise','practise']),('Cardinal numbers',['one hundred','two hundred','five hundred']),('Ordinal numbers',['first','twelfth','fiftieth'])],
    'g6/u4': [('Jobs',['author','dentist','engineer']),('Homes',['apartment','address','entrance'])],
    'g6/u7': [('Outdoor activities',['hiking','climbing','sailing']),('Environmental problems',['pollution','rubbish','plastic'])],
    'g6/u8': [('Planets',['Mercury','Venus','Earth']),('Extreme weather',['storm','thunder','lightning'])],
    'g8/u2': [('Social life',['teenager','relationship','fashion']),('Opinion adjectives',['relaxing','impressive','unbearable'])],
    'g8/u4': [('Phone actions',['dial','pick up','hang up']),('Phone nouns',['line','extension','memo'])],
    'g8/u5': [('Internet nouns',['account','browser','search engine']),('Online actions',['download','upload','delete'])],
    'g8/u6': [('Extreme sports',['bungee-jumping','canoeing','rafting']),('Describing activities',['amusing','challenging','exciting'])],
    'g8/u7': [('Places',['historic site','resort','countryside']),('Describing places',['ancient','rural','urban'])],
    'g8/u8': [('Household chores',['make the bed','set the table','wash the dishes']),('Behaviour rules',['obey the rules','arrive on time','keep quiet'])],
    'g8/u9': [('Lab nouns',['lab','test tube','cell']),('Scientific actions',['discover','invent','explore'])],
    'g8/u10': [('Natural disasters',['earthquake','flood','drought']),('Emergency help',['rescue team','shelter','first aid'])],
}


def plain(text):
    return str(text or '').replace('*','')


def role_for(phrase, sentence):
    word = phrase.lower().replace('’', "'").strip(' .!?')
    if word in FREQUENCY: return FREQUENCY[word]
    if re.search(r"\b(?:not|never|no|don't|doesn't|didn't|can't|cannot|mustn't|shouldn't|won't|wasn't|weren't|isn't|aren't|hasn't|haven't)\b",word): return 'negative'
    if re.fullmatch(r'i|you|he|she|it|we|they|me|him|her|us|them|my|your|his|our|their|mine|yours|hers|ours|theirs',word): return 'pronoun'
    if sentence.rstrip().endswith('?'): return 'question'
    return 'form'


def highlights(example, title):
    en = example.get('en',''); source = plain(en); marks=[]; offset=0
    for part in re.split(r'(\*[^*]+\*)',en):
        if part.startswith('*') and part.endswith('*'):
            phrase=part[1:-1]; role=role_for(phrase,source)
            start=offset; end=start+len(phrase)
            # Retain root letters while drawing attention to the taught suffix.
            lower=phrase.lower(); heading=title.lower()
            suffix=None
            if re.fullmatch('[a-zA-Z]+',phrase):
                if ('continuous' in heading or heading=='right now') and lower.endswith('ing'): suffix='ing'
                elif ('past' in heading or heading=='a completed experience') and lower.endswith('ed'): suffix='ed'
                elif ('comparative' in heading or heading=='comparing two') and lower.endswith('er'): suffix='er'
                elif ('superlative' in heading or heading=='comparing a group') and lower.endswith('est'): suffix='est'
                elif ('simple present' in heading or heading=='school routines') and lower.endswith('s') and lower not in ('is','has','does','this','always'): suffix='es' if lower.endswith(('ches','shes','xes','oes','sses')) else 's'
            if suffix and len(phrase)>len(suffix)+1:
                start=end-len(suffix); role='ending'
            # A marked phrase can contain both an auxiliary and a verb ending.
            # Keep "are" green and "ing" red instead of colouring "are doing" alike.
            elif role == 'form' and ('continuous' in heading or heading=='right now'):
                verb=re.search(r'\b[a-zA-Z]{2,}ing\b',phrase)
                if verb:
                    ending=start+verb.end()-3
                    if ending>start: marks.append(dict(start=start,end=ending,role='form'))
                    marks.append(dict(start=ending,end=ending+3,role='ending'))
                    if ending+3<end: marks.append(dict(start=ending+3,end=end,role='form'))
                    offset+=len(phrase)
                    continue
            marks.append(dict(start=start,end=end,role=role))
            offset+=len(phrase)
        else: offset+=len(part)
    example['enHighlights']=marks
    tr=example.get('tr',''); translated=[]
    # Existing trEm contains precise Turkish words or suffixes. Preserve those spans.
    for phrase in sorted(set(example.get('trEm',[])),key=len,reverse=True):
        start=tr.lower().replace('i̇','i').find(phrase.lower().replace('i̇','i'))
        if start<0: continue
        end=start+len(phrase)
        if any(start<r['end'] and end>r['start'] for r in translated): continue
        roles={m['role'] for m in marks}
        role=next(iter(roles)) if len(roles)==1 else 'form'
        if 'ending' in roles and re.fullmatch(r'[ıiuü]?yor(?:um|sun|uz|sunuz|lar)?',phrase): role='ending'
        translations={'her zaman':'always','genellikle':'usually','normalde':'usually','sık sık':'often','bazen':'sometimes','asla':'negative','hiçbir zaman':'negative'}
        role=translations.get(phrase.lower(),role)
        translated.append(dict(start=start,end=end,role=role))
    example['trHighlights']=sorted(translated,key=lambda r:r['start'])


def activity(title, task, scope, **meta):
    return dict(type='mission',title=title,task=task,lessonRefresh=True,activityScope=scope,**meta)


def unique(items, key):
    found=set(); out=[]
    for item in items:
        value=key(item)
        if value in found: continue
        found.add(value);out.append(item)
    return out


def cloze_rows(examples, limit):
    rows=[]
    for example in examples:
        en=example.get('en',''); match=re.search(r'\*([^*]+)\*',en)
        if not match: continue
        # Spelling notes are teaching aids, not English gap-fill questions.
        if re.search('[çğıöşüÇĞİÖŞÜ→]', plain(en)): continue
        answer=match[1]
        if len(answer)>40 or len(plain(en))>155: continue
        rows.append(dict(text=plain(en[:match.start()])+'___'+plain(en[match.end():]),answer=answer,tr=example.get('tr','')))
    rows=unique(rows,lambda r:r['text'])
    # Repeated answer words are intentional; the bank provides one tile per gap.
    return rows[:limit]


def enhance_slides(slides, unit=None):
    base=copy.deepcopy([s for s in slides if not s.get('lessonRefresh')])
    vocab=OrderedDict(); grammar=OrderedDict()
    for index,slide in enumerate(base):
        if slide['type']=='vocab':
            key=slide.get('topic') or slide.get('title','Vocabulary')
            group=vocab.setdefault(key,dict(items=[],last=index,meta={}))
            group['items'].extend(slide.get('items',[]));group['last']=index
            group['meta']={k:slide[k] for k in ('topic','topicIndex') if k in slide}
            slide['visualSequence']='picture-label-swap'
        if slide['type'] in ('grammar','compare'):
            if slide.get('rule'):
                rule=dict(en=slide['rule']); highlights(rule,'Rule')
                slide['ruleHighlights']=rule['enHighlights']
            key=slide.get('grammarId') or slide.get('title','Language')
            group=grammar.setdefault(key,dict(examples=[],last=index,title=slide.get('title','Language'),meta={}))
            examples=list(slide.get('examples',[]))
            for col in slide.get('columns',[]):examples.extend(col.get('examples',[]))
            for example in examples: highlights(example,slide.get('title',''))
            group['examples'].extend(examples);group['last']=index
            group['meta']={k:slide[k] for k in ('topic','topicIndex','grammarId') if k in slide}
    additions={}; allwords=[]; allexamples=[]
    for title,group in vocab.items():
        words=unique([w for w in group['items'] if w.get('en') and w.get('tr')],lambda w:w['en'].lower())
        # Equal translations make pairs ambiguous. Keep only one such word per board.
        words=unique(words,lambda w:w['tr'].lower());group['items']=words;allwords+=words
        if len(words)>=3:
            additions.setdefault(group['last'],[]).append(activity('Word pairs',dict(kind='wordpairs',q='Find each English word and its Turkish partner.',pairs=[dict(a=w['en'],b=w['tr']) for w in words[:6]]),'topic',titleTr=title,**group['meta']))
    for group in grammar.values():
        allexamples+=group['examples'];rows=cloze_rows(group['examples'],3)
        if len(rows)>=2:
            additions.setdefault(group['last'],[]).append(activity('Missing words',dict(kind='cloze',q='Complete the sentences. Use each tile once.',sentences=rows),'topic',titleTr=group['title'],**group['meta']))
    final=[]
    # Topic categories come from the lesson, with ambiguous cross-topic words removed.
    counts={}
    for group in vocab.values():
        for word in group['items']: counts[word['en'].lower()]=counts.get(word['en'].lower(),0)+1
    groups=[]
    for title,group in vocab.items():
        if title.startswith('More Words'): continue
        items=[w['en'] for w in group['items'] if counts[w['en'].lower()]==1]
        if len(items)>=2: groups.append(dict(label=title,items=items[:3]))
    if unit in SORT_GROUPS:
        available={w['en'] for w in allwords}
        groups=[dict(label=label,items=items) for label,items in SORT_GROUPS[unit]]
        assert all(word in available for group in groups for word in group['items']), unit
    if len(groups)>=2: final.append(activity('Sort the words',dict(kind='groupsort',q='Choose a word, then choose its group.',groups=groups[:3]),'unit'))
    rows=cloze_rows([g['examples'][0] for g in grammar.values() if g['examples']]+allexamples,5)
    if rows: final.append(activity('Unit word challenge',dict(kind='cloze',q='Bring the language together. Fill every gap.',sentences=rows),'unit'))
    questions=[]
    for group in grammar.values():
        for row in cloze_rows(group['examples'],1):
            questions.append(dict(q='Complete: '+row['text'],answer=row['text'].replace('___',row['answer']),tr=row['tr']))
    for group in vocab.values():
        if group['items']:
            w=group['items'][-1];questions.append(dict(q='How do you say “'+w['tr']+'” in English?',answer=w['en']))
    if questions: final.append(activity('Open a question box',dict(kind='quizbox',q='Pick a box. Answer aloud, then check together.',questions=questions[:8]),'unit'))
    out=[]
    for index,slide in enumerate(base):
        if slide['type']=='end': out.extend(final);final=[]
        out.append(slide);out.extend(additions.get(index,[]))
    out.extend(final)
    return out


def main():
    paths=sorted((ROOT/'content').glob('g*/*/presentation/slides.json'))
    counts={}; total=0
    for path in paths:
        data=json.loads(path.read_text(encoding='utf-8'))
        from book_alignment import align_slides, source_ref, BOOKS
        unit='/'.join(path.parts[-4:-2])
        data['slides']=align_slides(data['slides'],unit)
        if path.parts[-4] in BOOKS: data['bookAlignment']=source_ref(unit)
        data['slides']=enhance_slides(data['slides'],unit); data['lessonStyle']='reference-reveals-v1'
        path.write_text(json.dumps(data,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
        n=sum(bool(s.get('lessonRefresh')) for s in data['slides']);total+=n
        if path.parts[-4]=='g6': counts[path.parts[-3]]=len(data['slides'])
    alignment=ROOT/'content/g6/curriculum.json'
    if alignment.exists():
        data=json.loads(alignment.read_text(encoding='utf-8'))
        for unit in data['units']:
            if unit['id'] in counts: unit['slides']=counts[unit['id']]
        alignment.write_text(json.dumps(data,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
    print(f'{len(paths)} existing decks enhanced; {total} additional offline activities. No new decks.')


if __name__=='__main__': main()
