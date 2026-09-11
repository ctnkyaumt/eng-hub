"""Illustrated Grade 6 lesson flow: vocabulary, language, practice, next topic.

Inspired by the supplied Grade 5 lesson and the two read-only reference decks.
Pictures recur deliberately in retrieval practice, as in the reference lessons.
"""
import copy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ORDER = {
 'revision': [['r1-school-language','r1-pronouns','r1-time-routines'],['r1-now-tags','r1-preferences','r2-possession'],['r2-quantity-ordering','r2-comparisons'],['r2-can-permission','r2-holidays-obligations']],
 'u1': [['articles','pronouns'],['imperatives','present-simple','frequency'],['existence-questions'],[]],
 'u2': [['present-progressive','now-vs-routine'],['question-tags-present','question-tags-progressive'],['possessives','how-often-adverbs'],['cardinal-ordinal']],
 'u3': [['have-got'],['whose'],['comparatives'],['superlatives','irregular-comparison']],
 'u4': [['arrangements'],['when-while'],['future-timetables','which'],['reflexive-pronouns']],
 'u5': [['was-were'],['past-be-tags','why-when'],['gerunds-infinitives','time-transport'],['place-movement']],
 'u6': [['past-regular'],['past-questions'],['past-negative'],['regular-past-tags']],
 'u7': [['past-irregular'],['irregular-past-questions','irregular-past-tags'],['must-mustnt'],['have-to']],
 'u8': [['going-to-plans'],['will-predictions'],['going-to-evidence'],['future-questions','future-tags']],
}
SPEAK = {
 'revision': [('Show a visitor around','Name two school places. Say what you can do there.'),('Meet a new friend','Describe a family member. Ask your partner about a favourite activity.'),('At a small cafe','Order a drink and a dish. Your partner is the waiter. Swap roles.'),('Plan a class outing','Choose a place and two activities. Say what everyone must bring.')],
 'u1': [('Build your welcome team','Choose a leader and a guide. Tell your partner how each person helps.'),('Teach a new student','Give two instructions. Then describe one thing your class does every day.'),('Plan a celebration','Choose an event. Ask your partner when and where it is. Give two jobs to the team.'),('Encourage your partner','Your partner is worried about a task. Give encouragement and suggest how you can help.')],
 'u2': [('Habits or now?','Say what you usually do after school. Then describe what you are doing now.'),('Check with a partner','Make two statements about your class. Add question tags and wait for replies.'),('Share a study tip','Ask how often your partner revises. Share one useful habit and explain how you do it.'),('Design a quiz','Choose a number from 100 to 500 and an ordinal from 1st to 50th. Your partner writes them.')],
 'u3': [('Describe a sports kit','Say what you have got for swimming or running. Ask about your partner’s kit.'),('Lost property desk','Choose two classroom objects. Ask whose they are and return them to their owners.'),('Choose a team leader','Compare two imaginary students using patient, organised and helpful.'),('Describe and guess','Describe an imaginary person. Include one comparative and one superlative.')],
 'u4': [('A family visit','Choose a job. Tell your partner who you are visiting and when the visit is arranged.'),('Two things at once','Describe two family members at home. Join their actions with while.'),('Find the right home','Ask which apartment your partner means. Agree on a time to visit it.'),('We did it ourselves','Plan a model room. Say what each person makes without help.')],
 'u5': [('Yesterday at the festival','You went to an event yesterday. Tell your partner where it was and how it was.'),('Interview a visitor','Ask why an event was crowded. Confirm one detail with a question tag.'),('Getting to the show','Choose transport and a meeting time. Tell your partner what you plan to do there.'),('Give directions','Place a hall, a tram stop and a park on paper. Give your partner directions between them.')],
 'u6': [('A travel diary','Choose a country. Describe two things you visited or tried there last summer.'),('Find out about a trip','Ask three past questions about a partner’s imaginary trip. Listen and report one answer.'),('At a food fair','Describe one dish you tried and one you did not try. Explain your choice.'),('Check the story','Tell your partner about a meal. Your partner checks two details with question tags.')],
 'u7': [('Our outdoor day','Describe three things you did outdoors last weekend. Use went, saw or found.'),('Interview an explorer','Ask where your partner went and what they saw. Check one answer with a question tag.'),('Protect this place','Choose a river or forest. Make two must rules and two mustn’t rules for visitors.'),('A greener class','Agree on one change to save resources. Explain what you have to do and what you don’t have to buy.')],
 'u8': [('Build a planet model','Choose a planet. Explain what you are going to use and how you are going to make it.'),('Life in the future','Make two predictions about homes or energy. Your partner says whether they agree.'),('Look at the evidence','Imagine dark clouds or a model near a table edge. Say what is going to happen and why.'),('Our future fair','Agree on a project. Ask about plans, make a prediction and check one detail with a question tag.')],
}
# One concrete picture cue for each authored example; no substring matching.
EXAMPLES = {
 'revision': ['science|laboratory','classroom|guide','get dressed|timetable','read silently|library','music|swimming','tiny house|camp','a bottle of water|soup','elephant|parrot','parrot|entrance','camp|a bottle of water'],
 'u1': ['leader|instruction|ceremony','listener|enter','review|flag|flag','pack|helpful','helpful|guide','flag|ceremony'],
 'u2': ['research|read silently|rest','pair|independent','revise|read aloud','share|diary','review|diary','revise|instruction','300|32nd'],
 'u3': ['bracelet|trainers|necklace','bracelet|bracelet','pocket|patient','pocket|bracelet','swimsuit|pocket'],
 'u4': ['designer|apartment','timetable|08:20','address|read silently','apartment|reporter','author|tiny house'],
 'u5': ['festival|musician|perform','local|timetable','crowded|musician','jazz|festival','tram|underpass','timetable|on foot'],
 'u6': ['food stall|dessert','soup|restaurant','food stall|apartment','main course|soup'],
 'u7': ['hiking|rubbish','smoke|rubbish','hiking|cuisine','protect|rubbish','a bottle of water|reusable'],
 'u8': ['orbit|plastic','storm|invent','save|drought','predict|orbit','orbit|helpful|ship'],
}
ACCENTS = {'revision':['#38bdf8','#6366f1'],'u1':['#38bdf8','#6366f1'],'u2':['#a78bfa','#38bdf8'],
 'u3':['#f472b6','#a78bfa'],'u4':['#fbbf24','#fb923c'],'u5':['#2dd4bf','#38bdf8'],
 'u6':['#fb923c','#f472b6'],'u7':['#4ade80','#2dd4bf'],'u8':['#a78bfa','#60a5fa']}


def plain(text):
    return text.replace('*','')


def exercise(title, task, **fields):
    return dict(type='exercise',title=title,tasks=[task],**fields)


def image_fields(word):
    return {k:v for k,v in word.items() if k=='img' or k.startswith('image')}


def illustrated_slides(unit, items):
    pictures=json.loads((ROOT/'tools/grade6-image-choices.json').read_text(encoding='utf-8'))
    getpic=lambda word: image_fields(pictures[word.lower()])
    slides=[dict(type='title',title=unit['title'],titleTr=unit['titleTr'],emoji=unit['emoji'])]
    rules={g['id']:g for g in unit['grammar']}
    cues={g['id']:names.split('|') for g,names in zip(unit['grammar'],EXAMPLES[unit['id']])}
    assert len(cues)==len(unit['grammar'])
    for section,group in enumerate(unit['groups']):
        block=items[section*8:section*8+8]
        heading=group['title'].replace('Revision 1: ','').replace('Revision 2: ','')
        common=dict(topic=heading,topicIndex=section+1)
        # Two short illustrated vocabulary pages, with retrieval between them.
        for half in range(2):
            four=block[half*4:half*4+4]
            slides.append(dict(type='vocab',title=heading,part=[half+1,2],items=four,**common))
            candidates=[w for w in four if w.get('img') and w.get('pictureQuiz',True)]
            if candidates:
                target=candidates[0]
                task=dict(kind='picture',q='Which word matches the picture?',answer=target['en'],
                          options=[w['en'] for w in four],tr=target['tr'],**image_fields(target))
                slides.append(exercise('Picture challenge',task,**common))
            else:
                slides.append(exercise('Say it in English',dict(kind='flash',q='Say the English word before you reveal it.',
                    clue=four[0]['tr'],answer=four[0]['en'],**image_fields(four[0])),**common))
        distinct=[];seen=set()
        for word in block:
            if (word.get('img') or word.get('num')) and word.get('pictureQuiz',True):
                key=word.get('img') or word.get('num')
                if key in seen:continue
                seen.add(key)
                distinct.append({**word,'audio':'/app/audio/words/'+re.sub('[^a-z0-9]+','-',word['en'].lower()).strip('-')+'.wav'})
        if len(distinct)>=4:
            kind='listenpicture' if section%2==0 else 'dragmatch'
            slides.append(dict(type='mission',title='Listen and find' if kind=='listenpicture' else 'Picture match',
                task=dict(kind=kind,items=distinct[:4]),**common))
        else:
            slides.append(exercise('Word partners',dict(kind='match',q='Match each word with its meaning.',
                pairs=[dict(a=w['en'],b=w['tr']) for w in block[2:6]]),**common))
        target=block[3]
        slides.append(exercise('True or false?',dict(kind='truefalse',q='Discuss, then choose.',
            statement=f'{target["en"]} means "{block[4]["tr"]}".',answer=False,
            explain=f'{target["en"]} means "{target["tr"]}".'),**common))
        for gid in ORDER[unit['id']][section]:
            g=rules[gid]
            checks=[]
            for index,row in enumerate(g['checks']):
                text,*wrong=row;answer=re.findall(r'\*(.+?)\*',text)[0];gap=re.sub(r'\*(.+?)\*','___',text)
                task=dict(kind='fill' if index%2==0 and len(answer)<32 else 'choose',q='Complete the sentence.' if index%2==0 and len(answer)<32 else gap,
                          text=gap,answer=answer,options=[answer,*wrong])
                checks.append(exercise('Language practice',task,grammarId=gid,**common))
            for i,(en,tr) in enumerate(g['examples']):
                cue=cues[gid][i]
                ex=dict(en=en,tr=plain(tr),trEm=re.findall(r'\*(.+?)\*',tr))
                if re.fullmatch(r'\d\d:\d\d',cue):ex['time']=cue
                elif re.fullmatch(r'\d+(st|nd|rd|th)?',cue):ex['num']=cue
                else:ex.update(getpic(cue))
                slides.append(dict(type='grammar',title=g['title'],rule=g['rule'],grammarId=gid,examples=[ex],**common))
                if i==1 and checks:slides.append(checks.pop(0))
            slides.extend(checks)
            # Rebuild a model immediately after the grammar that explains it.
            en,tr=g['examples'][0]
            if 4<=len(plain(en).split())<=14:
                slides.append(dict(type='mission',title='Sentence workshop',grammarId=gid,
                    task=dict(kind='dragorder',sentences=[dict(answer=plain(en),tr=plain(tr))]),**common))
        title,prompt=SPEAK[unit['id']][section]
        slides.append(exercise(title,dict(kind='flash',q=prompt,clue='Work with a partner. Take turns.',
            answer='Answers vary. Use the language in this section, listen to your partner, then swap roles.'),**common))
        # Dialogues belong next to the topic instead of being stacked at the end.
        if section in (1,2):
            start=0 if section==1 else 2
            slides.append(dict(type='dialogue',title='Try the conversation',dialogues=[dict(lines=[
                dict(who=who,text=text,tr=tr) for who,text,tr in unit['dialogue'][start:start+2]])],**common))
    sentences=re.split(r'(?<=[.!?])\s+',unit['story']);half=(len(sentences)+1)//2
    story_pic={'revision':'tiny house','u1':'leader','u2':'group','u3':'trainers','u4':'apartment','u5':'festival','u6':'food stall','u7':'hiking','u8':'orbit'}[unit['id']]
    for start in (0,half):
        slides.append(dict(type='scene',title=unit['storyTitle'],**getpic(story_pic),
            bubbles=[dict(text=' '.join(sentences[start:start+half]))]))
    for q,a in unit['reading']:
        slides.append(exercise('Read and remember',dict(kind='flash',q=q,answer=a)))
    for statement,answer in unit['truth']:
        slides.append(exercise('Check the story',dict(kind='truefalse',q='Does this match the story?',statement=statement,answer=answer)))
    slides.append(exercise('One-minute exit ticket',dict(kind='flash',q='Say two new words and make one sentence about today’s theme.',
        answer='Check the meaning of both words. Use one of today’s grammar patterns in your sentence.')))
    slides.append(dict(type='end',title='Well done!',titleTr='Oyunlar ve özgün çalışma kâğıtları',emoji=unit['emoji']))
    return slides
