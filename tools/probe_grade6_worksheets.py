"""Probe the actual printable output: layout, answers and partner information gaps.

Uses PyMuPDF; no app build or network. Run after --worksheets-only.
"""
import json
from pathlib import Path
import re

import fitz

from grade6_content import UNITS
from grade6_worksheet_tasks import MISSIONS

ROOT = Path(__file__).resolve().parents[1]


def normal(text):
    return re.sub(r"\s+", " ", text.replace("*", "")).strip()


def check_layout(page, context):
    assert abs(page.rect.width-595.276)<.1 and abs(page.rect.height-841.890)<.1, context
    lines=[]
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines",[]):
            rect=fitz.Rect(line["bbox"])
            text="".join(s["text"] for s in line["spans"])
            assert rect.x0>=35 and rect.x1<=page.rect.width-35, (context,text,rect)
            assert rect.y0>=20 and rect.y1<=page.rect.height-20, (context,text,rect)
            assert "\ufffd" not in text and "\u25a0" not in text, (context,text)
            lines.append((rect,text))
    for i,(a,ta) in enumerate(lines):
        for b,tb in lines[i+1:]:
            overlap=a & b
            assert overlap.is_empty or overlap.width<1 or overlap.height<1, (context,"overlapping text",ta,tb)
    panels=[d["rect"] for d in page.get_drawings()
            if abs(d["rect"].x0-36)<.2 and abs(d["rect"].width-(page.rect.width-72))<.2
            and d["rect"].height>50]
    for rect,text in lines:
        for panel in panels:
            if rect.intersects(panel):
                assert panel.contains(rect), (context,"text crosses panel",text,rect,panel)
    for drawing in page.get_drawings():
        if len(drawing['items'])!=1:
            continue  # Rounded panel borders are not answer rules.
        for item in drawing["items"]:
            if item[0]!="l":
                continue
            a,b=item[1:3]
            if abs(a.y-b.y)<.1 and 155<a.y<798 and abs(a.x-b.x)>80:
                assert any(p.contains(a) and p.contains(b) for p in panels), (context,"answer line outside panel",item)


def main():
    pages=0
    assert set(MISSIONS)=={u['id'] for u in UNITS}
    assert len({m['mission'] for m in MISSIONS.values()})==9
    for unit in UNITS:
        folder=ROOT/'content/g6'/unit['id']/'worksheets'
        task=MISSIONS[unit['id']]
        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        assert len(manifest['items'])==3
        docs={}
        for item in manifest['items']:
            path=folder/item['file']
            assert item['authored'] and not item.get('link')
            assert item['size']==path.stat().st_size
            doc=fitz.open(path)
            assert len(doc)==2, path
            docs[item['file']]=doc
            for number,page in enumerate(doc,1):
                check_layout(page,f"{unit['id']}/{item['file']}:{number}")
                assert f'{number} / 2' in page.get_text()
                pages+=1
        a=docs['original-a.pdf']; b=docs['original-b.pdf']; key=docs['original-key.pdf']
        student_text=normal(' '.join(p.get_text() for p in a))
        key_text=normal(' '.join(p.get_text() for p in key))
        assert normal(task['mission']) in student_text
        for question,answer in task['clues']:
            assert normal(question) in student_text
            assert normal(answer) in key_text
        for grammar in unit['grammar']:
            # The first example for every target must remain in the worksheet and key.
            source=grammar['checks'][0][0]
            answer=re.search(r'\*(.*?)\*',source).group(1)
            question=re.sub(r'\*(.*?)\*','___',source)
            assert normal(question) in student_text,(unit['id'],grammar['id'])
            assert normal(answer) in key_text
        for field in ('story','model','listening'):
            assert normal(unit[field]) in (student_text if field=='story' else key_text),(unit['id'],field)
        # Each partner can find exactly the two details missing from the other half.
        pair_page=b[1]
        middle=pair_page.rect.width/2
        left=normal(pair_page.get_text(clip=fitz.Rect(49,249,middle-11,443)))
        right=normal(pair_page.get_text(clip=fitz.Rect(middle+11,249,546,443)))
        for i,(label,answer) in enumerate(task['pair_rows']):
            assert label in left and label in right,(unit['id'],label,left,right)
            # Match complete lines, not substrings such as the number 5 in 150.
            halves=[pair_page.get_text(clip=fitz.Rect(49,249,middle-11,443)),
                    pair_page.get_text(clip=fitz.Rect(middle+11,249,546,443))]
            assert answer in halves[i%2].splitlines(),(unit['id'],answer)
            assert answer not in halves[1-i%2].splitlines(),(unit['id'],'leaked pair answer',answer)
            assert normal(f'{label}: {answer}') in key_text
        for doc in docs.values(): doc.close()
    print(f'PASS: {pages} A4 pages; margins, no text overlap, panel containment, all grammar targets, scripts, keys, 36 complementary partner details.')


if __name__=='__main__':
    main()
