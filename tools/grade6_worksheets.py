"""A4 worksheet renderer: measured text, fixed panels and original vector art.

No application build. Called by create_grade6.py --worksheets-only.
"""
import os
import random
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from grade6_worksheet_tasks import MISSIONS

W, H = A4
M = 36
CW = W - 2 * M
INK = colors.HexColor("#203342")
MUTED = colors.HexColor("#53636F")
LINE = colors.HexColor("#AEBBC3")
PALE = colors.HexColor("#F4F6F7")


class Sheet:
    def __init__(self, path, unit, task, kind, author):
        font_dir = Path(os.environ.get("G6_FONT_DIR", "C:/Windows/Fonts"))
        for name, filename in (("G6", "arial.ttf"), ("G6-Bold", "arialbd.ttf")):
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
        self.c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1, invariant=1)
        self.c.setTitle(f"Grade 6 | {unit['title']} | {kind}")
        self.c.setAuthor(author)
        self.unit, self.task, self.kind = unit, task, kind
        self.accent = colors.HexColor(task["accent"])

    def text(self, text, x, y, w, size=10.5, bold=False, color=INK, maxh=None):
        text = str(text).replace("*", "")
        style = ParagraphStyle("text", fontName="G6-Bold" if bold else "G6",
                               fontSize=size, leading=size * 1.32, textColor=color)
        p = Paragraph(escape(text).replace("\n", "<br/>"), style)
        _, height = p.wrap(w, 1000)
        if maxh is not None and height > maxh + .1:
            raise ValueError(f"{self.unit['id']} {self.kind}: text needs {height:.1f}, has {maxh}: {text}")
        assert x >= M - .1 and x + w <= W - M + .1, (text, x, w)
        assert y + height < H - 20, (text, y, height)
        p.drawOn(self.c, x, H - y - height)
        return height

    def line(self, x1, y1, x2, y2, color=LINE, width=.6, dash=None):
        c = self.c
        c.saveState()
        c.setStrokeColor(color)
        c.setLineWidth(width)
        if dash:
            c.setDash(*dash)
        c.line(x1, H - y1, x2, H - y2)
        c.restoreState()

    def box(self, x, y, w, h, fill=None, stroke=LINE, radius=7):
        c = self.c
        c.setLineWidth(.65)
        c.setStrokeColor(stroke or colors.white)
        c.setFillColor(fill or colors.white)
        c.roundRect(x, H - y - h, w, h, radius, stroke=bool(stroke), fill=1)

    def rule(self, x, y, w, count=1, gap=21):
        for n in range(count):
            self.line(x, y + n * gap, x + w, y + n * gap)

    def icon(self, kind, x, y, size=34, variant=0):
        """Small crisp diagrams drawn locally; independent of fonts and network."""
        c = self.c
        c.saveState()
        c.translate(x, H - y - size)
        c.scale(size / 40, size / 40)
        c.setStrokeColor(self.accent)
        c.setFillColor(colors.white)
        c.setLineWidth(1.5)
        def line(a,b,d,e): c.line(a,b,d,e)
        def poly(points):
            p=c.beginPath(); p.moveTo(*points[0])
            for pt in points[1:]: p.lineTo(*pt)
            p.close(); c.drawPath(p,stroke=1,fill=0)
        if kind == "tent":
            poly([(3,5),(20,34),(37,5)]); poly([(13,5),(20,22),(27,5)]); line(0,3,40,3)
        elif kind == "island":
            c.ellipse(3,3,37,11); line(20,9,22,31)
            for ex,ey in [(7,29),(11,37),(33,35),(36,26)]: line(22,31,ex,ey)
        elif kind in ("house","museum","factory"):
            if kind=="factory": poly([(4,5),(4,26),(15,20),(15,29),(27,22),(36,22),(36,5)])
            else: poly([(3,25),(20,37),(37,25)]); c.rect(6,5,28,20)
            for xx in (11,24): c.rect(xx,13,5,7)
        elif kind in ("clipboard","news","passport"):
            c.roundRect(7,3,26,34,3)
            if kind=="clipboard": c.roundRect(14,33,12,6,2)
            elif kind=="passport": c.circle(20,24,7); c.ellipse(17,17,23,31); line(13,24,27,24)
            for yy in (9,15): line(12,yy,28,yy)
            if kind=="news": line(12,22,28,22); line(12,28,28,28)
        elif kind == "sign":
            line(20,2,20,37); poly([(3,30),(29,30),(36,24),(29,18),(3,18)])
        elif kind == "flag":
            line(9,2,9,37); poly([(9,35),(33,32),(30,18),(9,21)]); line(3,2,17,2)
        elif kind == "book":
            poly([(20,5),(4,10),(4,34),(20,29),(36,34),(36,10)]); line(20,5,20,29)
            line(8,24,16,22); line(24,22,32,24)
        elif kind == "people":
            for xx in (11,29): c.circle(xx,29,5); c.roundRect(xx-7,7,14,14,4)
            line(15,16,25,16)
        elif kind == "wallet":
            widths=[29,23,36]; ww=widths[variant % 3]
            c.roundRect((40-ww)/2,10,ww,22,3); c.rect(26,17,9,7); c.circle(30,20.5,1)
            if variant==0:
                poly([(14,26),(16,22),(20,22),(17,19),(18,15),(14,18),(10,15),(11,19),(8,22),(12,22)])
            elif variant==1:
                p=c.beginPath(); p.moveTo(15,16); p.curveTo(2,24,12,29,15,24); p.curveTo(18,29,28,24,15,16); c.drawPath(p)
            else: c.circle(15,22,5)
        elif kind == "pencil":
            poly([(8,6),(12,18),(29,35),(36,28),(19,11)]); line(12,18,19,11); line(16,14,32,31)
        elif kind == "music":
            c.circle(10,9,5); c.circle(29,13,5); line(15,9,15,32); line(34,13,34,36); line(15,32,34,36)
        elif kind == "tram":
            c.roundRect(7,8,26,25,4); c.rect(11,19,18,9)
            c.circle(13,13,2); c.circle(27,13,2); line(11,2,15,8); line(29,2,25,8)
            line(20,33,20,38); line(13,38,27,38)
        elif kind == "cup":
            c.roundRect(7,7,23,23,3); c.ellipse(29,12,38,26); line(4,4,34,4)
            line(13,33,13,39); line(22,33,22,39)
        elif kind in ("globe","planet"):
            c.circle(20,20,12)
            if kind=="globe": c.ellipse(15,8,25,32); line(8,20,32,20)
            else: c.ellipse(1,14,39,26); c.circle(8,35,2)
        elif kind == "falling":
            line(3,8,37,8); line(29,8,29,2); poly([(27,28),(36,22),(30,13),(21,19)])
            line(17,32,21,27); line(12,26,17,23)
        elif kind == "bulb":
            c.circle(20,25,10); c.rect(15,7,10,8); line(16,3,24,3)
            for a,b,d,e in [(20,38,20,40),(4,25,0,25),(36,25,40,25)]: line(a,b,d,e)
        elif kind == "bottle":
            c.rect(16,32,8,6); c.roundRect(11,3,18,29,5); c.rect(11,13,18,11)
        elif kind == "bin":
            poly([(10,29),(13,3),(29,3),(32,29)]); line(7,31,35,31); c.rect(16,33,10,4)
            line(18,8,17,26); line(24,8,25,26)
        elif kind == "leaf":
            p=c.beginPath(); p.moveTo(7,6); p.curveTo(0,28,23,38,35,34); p.curveTo(39,13,20,0,7,6); c.drawPath(p)
            line(5,3,29,29); line(15,13,15,23); line(21,20,30,20)
        c.restoreState()

    def header(self, page, subtitle, teacher=False):
        label = "REVISION 1 + 2" if self.unit["id"] == "revision" else "THEME " + self.unit["id"][1:]
        self.text("ENG HUB  /  GRADE 6", M, 23, 250, 9, True, self.accent)
        self.text(label, W-M-130, 23, 130, 9, True, self.accent)
        title = "Teacher notes & answers" if teacher else self.task["title"]
        self.text(title, M, 44, CW-52, 22, True, maxh=30)
        self.icon(self.task["icon"], W-M-38, 47, 36)
        self.text(self.unit["title"], M, 77, CW, 11, color=MUTED, maxh=16)
        self.line(M, 101, W-M, 101, self.accent, 1.4)
        self.text(f"{self.kind.upper()}  /  {subtitle}", M, 110, CW, 9, True, self.accent, maxh=13)
        if teacher:
            self.text("Accept equivalent answers. Pair and creative tasks have more than one possible answer.", M, 130, CW, 9, color=MUTED, maxh=13)
        else:
            for label,x,w in (("Name",M,250),("Class",M+272,89),("Date",M+381,CW-381)):
                self.text(label,x,131,35,9,color=MUTED)
                self.rule(x+31,143,w-31)
        self.line(M, H-43, W-M, H-43)
        self.text("Original ENG HUB activities | Print A4 at 100% | Colour or grayscale",M,H-33,CW-50,7.5,color=MUTED)
        self.text(f"{page} / 2",W-M-32,H-33,32,8,True)

    def panel(self, code, title, y, h, x=M, w=CW):
        self.box(x,y,w,h)
        self.box(x+11,y+11,29,22,fill=self.accent,stroke=None,radius=5)
        self.text(code,x+15,y+15,24,9,True,colors.white,maxh=13)
        self.text(title,x+49,y+13,w-61,12,True,maxh=32)
        return x+13,y+43,w-26

    def page(self): self.c.showPage()
    def save(self): self.c.save()


def grammar_items(unit, checks):
    """One question per curriculum target; shorter options stay on their own line."""
    rows=[]
    for g in unit["grammar"]:
        q=next(q for q in checks if q["grammarId"]==g["id"])
        opts=[q["answer"],q["options"][1]]
        random.Random(unit["id"]+g["id"]).shuffle(opts)
        rows.append(dict(q, choices=opts))
    return rows


def sentence_items(unit):
    sentences=[]
    extras=[]
    for g in unit["grammar"]:
        first=True
        for en,_ in g["examples"]:
            en=en.replace("*","")
            if 4 <= len(en.split()) <= 9 and not en.endswith("?") and not en.startswith("Because "):
                (sentences if first else extras).append(en)
                first=False
    return (sentences+extras)[:3]


def mission_board(s):
    t=s.task
    x,y,w=s.panel("A1",t["mission"],155,281)
    s.text(t["instruction"],x,y,w,10,maxh=27)
    top=y+34
    if t.get("map"):
        gap=8; cell=(w-2*gap)/3
        icons=(("leaf","tram","house"),("book","music","cup"))
        for row, labels in enumerate((("PARK","TRAM STOP","HALL"),("LIBRARY","STAGE","CAFE"))):
            for col,label in enumerate(labels):
                xx=x+col*(cell+gap); yy=top+row*65
                s.box(xx,yy,cell,31,PALE)
                s.icon(icons[row][col],xx+7,yy+5,21)
                s.text(label,xx+34,yy+9,cell-41,9,True,maxh=13)
        s.line(x,top+42,x+w,top+42)
        s.text("F E S T I V A L   S T R E E T",x+120,top+45,w-240,8,True,MUTED,maxh=12)
        s.line(x,top+60,x+w,top+60)
    else:
        gap=9; cell=(w-2*gap)/3
        for i,(letter,title,facts,icon) in enumerate(t["cards"]):
            xx=x+i*(cell+gap)
            s.box(xx,top,cell,96,PALE)
            s.icon(icon,xx+8,top+8,29,i)
            s.text(letter,xx+cell-20,top+7,12,10,True,s.accent)
            s.text(title,xx+8,top+39,cell-16,9,True,maxh=13)
            s.text(facts,xx+8,top+55,cell-16,9,maxh=36)
    for i,(question,_) in enumerate(t["clues"]):
        yy=top+105+i*21
        s.text(f"{i+1}. {question}",x,yy,w-89,9.5,maxh=14)
        s.rule(x+w-82,yy+14,82)
    s.text("TALK  " + t["stretch"],x,top+173,w,9,True,s.accent,maxh=24)


def grammar_panel(s, rows):
    x,y,w=s.panel("A2","Language choices",448,339)
    s.text("Circle the correct choice. Then read each complete sentence.",x,y,w,10,maxh=14)
    gap=21; col=(w-gap)/2; nrows=(len(rows)+1)//2
    step=min(70,(282-17)/nrows)
    for i,q in enumerate(rows):
        xx=x+(i%2)*(col+gap); yy=y+26+(i//2)*step
        height=s.text(f"{i+1}. {q['q']}",xx,yy,col,10,maxh=step-25)
        s.text(" / ".join(q["choices"]),xx+13,yy+height+3,col-13,9.5,True,s.accent,maxh=26)
    if len(rows) <= 6:
        yy=y+26+nrows*step+5
        s.text("MAKE IT YOURS  Change a person, place or time in one sentence.",x,yy,w,9,True,s.accent,maxh=13)
        s.rule(x,yy+37,w)


def reading_page(s, unit):
    s.header(2,"READ / NOTICE / CREATE")
    x,y,w=s.panel("A3",unit["storyTitle"],155,248)
    height=s.text(unit["story"],x,y,w,10.5,maxh=112)
    qtop=y+height+9; gap=22; col=(w-gap)/2
    for i,(question,_) in enumerate(unit["reading"]):
        xx=x+(i%2)*(col+gap); yy=qtop+(i//2)*47
        s.text(f"{i+1}. {question}",xx,yy,col,9.5,maxh=26)
        s.rule(xx,yy+39,col)
    assert qtop+86 <= 397, (unit['id'],qtop)
    x,y,w=s.panel("A4","Fact detective",415,148)
    for i,(statement,_) in enumerate(unit["truth"]):
        yy=y+i*19
        s.text(f"{i+1}. {statement}",x,yy,w-60,9.5,maxh=14)
        s.text("T / F",x+w-39,yy,39,9,True)
    s.text("Circle T or F. Fix the false detail(s) below.",x,y+58,w,8.5,color=MUTED,maxh=12)
    s.rule(x,y+80,w,2,17)
    x,y,w=s.panel("A5",s.task["product"],575,212)
    hh=s.text(unit["writing"],x,y,w,10,maxh=40)
    s.rule(x,y+hh+23,w,6,18)


def workshop_page(s,unit,sentences):
    s.header(1,"BUILD / LISTEN / REPORT")
    x,y,w=s.panel("B1","Sentence studio",155,297)
    s.text("Put the words in order. Use every word. Keep the punctuation.",x,y,w,10,maxh=14)
    for i,sentence in enumerate(sentences):
        tokens=sentence.split()
        random.Random(sentence).shuffle(tokens)
        yy=y+29+i*72
        s.box(x,yy,w,31,PALE)
        s.text(f"{i+1}   " + " / ".join(tokens),x+9,yy+8,w-18,10,maxh=27)
        s.rule(x,yy+55,w)
    x,y,w=s.panel("B2","Radio notes",464,221)
    s.text("Listen to your teacher twice. First listen for the topic; then fill in the four boxes.",x,y,w,10,maxh=27)
    gap=14; col=(w-gap)/2
    for i,(question,_) in enumerate(unit["listenQs"]):
        xx=x+(i%2)*(col+gap); yy=y+37+(i//2)*65
        s.box(xx,yy,col,55,PALE)
        s.text(f"{i+1}  {question}",xx+10,yy+9,col-20,10,True,maxh=14)
        s.rule(xx+10,yy+44,col-20)
    x,y,w=s.panel("+","One-sentence reporter",697,90)
    s.text("Use two details from your radio notes in one sentence. Compare with a partner.",x,y,w,10,maxh=27)
    s.rule(x,y+35,w)


def pair_page(s):
    t=s.task
    s.header(2,"ASK / AGREE / SHARE")
    x,y,w=s.panel("B3",t["pair_title"],155,361)
    s.text("Choose A or B. Fold on the dotted line and keep your half facing you. Ask your partner for the missing details. Do not show your answers.",x,y,w,10,maxh=40)
    top=y+51; gap=22; col=(w-gap)/2
    s.line(x+w/2,top-4,x+w/2,top+198,dash=(3,3))
    for role in range(2):
        xx=x+role*(col+gap)
        s.box(xx,top,col,194,PALE)
        s.text("PARTNER " + "AB"[role],xx+11,top+10,col-22,11,True,s.accent,maxh=15)
        for i,(label,answer) in enumerate(t["pair_rows"]):
            yy=top+39+i*38
            s.text(label,xx+11,yy,col-22,8.5,True,MUTED,maxh=12)
            if i%2 == role:
                s.text(answer,xx+11,yy+14,col-22,10,maxh=14)
            else:
                s.rule(xx+11,yy+29,col-22)
    s.text("QUESTION HELP",x,top+209,w,8.5,True,s.accent,maxh=12)
    s.text(t["ask"],x,top+226,w,9.5,maxh=39)
    x,y,w=s.panel("B4","Your team decision",528,184)
    s.text(t["decision"],x,y,w-127,10,maxh=53)
    s.text(t["frame"],x,y+57,w-127,9.5,True,s.accent,maxh=39)
    s.rule(x,y+108,w-127,2,19)
    s.box(x+w-111,y,111,122,PALE)
    s.text(t["draw"],x+w-101,y+8,91,8.5,color=MUTED,maxh=24)
    x,y,w=s.panel("B5","Say your decision. Tick what you used:",724,63)
    s.text("[ ] " + "   [ ] ".join(t["checklist"]),x,y,w,8.5,maxh=12)


def key_page_a(s,unit,rows,corrections):
    s.header(1,"WORKSHEET A / ANSWERS",teacher=True)
    x,y,w=s.panel("A1",s.task["mission"],155,115)
    s.text("   |   ".join(f"{i}. {a}" for i,(_,a) in enumerate(s.task["clues"],1)),x,y,w,10.5,maxh=28)
    s.text("Extension: accept a relevant spoken sentence supported by the cards or map.",x,y+37,w,9.5,maxh=27)
    x,y,w=s.panel("A2","Language choices",282,152)
    col=(w-20)/2
    for i,q in enumerate(rows):
        s.text(f"{i+1}. {q['answer']}",x+(i%2)*(col+20),y+(i//2)*19,col,9.5,maxh=26)
    x,y,w=s.panel("A3","Reading answers",446,139)
    for i,(_,a) in enumerate(unit["reading"]):
        s.text(f"{i+1}. {a}",x,y+i*22,w,10,maxh=27)
    x,y,w=s.panel("A4","Fact detective",597,111)
    for i,(_,a) in enumerate(unit["truth"],1):
        answer="True." if a else "False. " + corrections[i]
        s.text(f"{i}. {answer}",x,y+(i-1)*19,w,9.5,maxh=26)
    s.text("A5 sample and assessment are on the next page.",M+12,727,CW-24,10,True,s.accent,maxh=15)
    refs=f"Curriculum scope: MEB English 6 (2026), Student's Book pp. {unit['sb'][0]}-{unit['sb'][1]}."
    if unit['wb']: refs+=f" Workbook pp. {unit['wb'][0]}-{unit['wb'][1]}."
    s.text(refs,M+12,752,CW-24,8.5,color=MUTED,maxh=27)


def key_page_b(s,unit,sentences):
    s.header(2,"MODEL / LISTENING / PAIR TASK",teacher=True)
    x,y,w=s.panel("A5","Sample writing",155,120)
    s.text(unit["model"],x,y,w,9.5,maxh=66)
    x,y,w=s.panel("B1","Sentence studio",287,109)
    for i,sentence in enumerate(sentences):
        s.text(f"{i+1}. {sentence}",x,y+i*18,w,9.5,maxh=26)
    x,y,w=s.panel("B2","Read-aloud script and radio notes",408,158)
    s.text("Read twice at a natural pace. Pause between sentences; allow note-taking on the second reading.",x,y,w,8.5,color=MUTED,maxh=24)
    hh=s.text(unit["listening"],x,y+29,w,10,maxh=54)
    s.text(" | ".join(f"{i}. {a}" for i,(_,a) in enumerate(unit["listenQs"],1)),x,y+hh+36,w,9,True,maxh=27)
    x,y,w=s.panel("B3","Information gap: completed plan",578,93)
    s.text(" | ".join(f"{q}: {a}" for q,a in s.task["pair_rows"]),x,y,w,9.5,maxh=39)
    x,y,w=s.panel("B4","Team task: one possible response",683,104)
    s.text(s.task["sample"],x,y,w,9.5,maxh=40)
    s.text("Speaking / 4: three B5 checks + listening and replying. Writing / 8: task, grammar, vocabulary, clarity (0-2 each).",x,y+36,w,8,maxh=22)


def make_pdfs(unit,folder,checks,corrections,author,edition):
    task=MISSIONS[unit["id"]]
    rows=grammar_items(unit,checks)
    sentences=sentence_items(unit)
    assert len(sentences)==3
    a=Sheet(folder/"original-a.pdf",unit,task,"Worksheet A",author)
    a.header(1,"SOLVE / CHOOSE / TALK")
    mission_board(a); grammar_panel(a,rows); a.page()
    reading_page(a,unit); a.page(); a.save()
    b=Sheet(folder/"original-b.pdf",unit,task,"Worksheet B",author)
    workshop_page(b,unit,sentences); b.page()
    pair_page(b); b.page(); b.save()
    key=Sheet(folder/"original-key.pdf",unit,task,"Teacher key",author)
    key_page_a(key,unit,rows,corrections); key.page()
    key_page_b(key,unit,sentences); key.page(); key.save()
    return [dict(title=title,file=name,authored=True,curriculum=edition,by=author,type="worksheet",
                 desc=desc,size=(folder/name).stat().st_size)
            for title,name,desc in (
                ("Çalışma Kâğıdı A - Tema Görevi, Dil ve Okuma","original-a.pdf","2 sayfa · görsel bulmaca, okuma ve yaratıcı yazma"),
                ("Çalışma Kâğıdı B - Dinle, Konuş ve Tasarla","original-b.pdf","2 sayfa · dinleme, bilgi boşluğu ve eşli tasarım"),
                ("Öğretmen Anahtarı - A ve B","original-key.pdf","2 sayfa · cevaplar, dinleme metni ve değerlendirme"))]
