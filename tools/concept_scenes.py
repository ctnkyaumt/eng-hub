"""Original vector teaching situations for concepts that photographs obscure.

These are diagrams, not generic emoji substitutions. Each scene shows a
concrete example; context captions support abstract vocabulary.
"""
from teaching_diagrams import write, text

BLUE, GREEN, RED, GOLD = '#168aad', '#229978', '#df5261', '#edb547'


def rect(x, y, w, h, fill='white', radius=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="#28465c" stroke-width="3"/>'


def line(d, color='#28465c', width=6):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def circle(x, y, r, fill):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'


def person(x, y, color=BLUE, scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})">'+circle(0,0,23,'#f1c8a7')+line('M-13 -7q13-19 28 0','#594738',9)+rect(-26,30,52,67,color)+line('M-15 98v44m30-44v44M-26 42l-22 45m74-45 22 45')+'</g>'


def arrow(x, y, length=100, color=BLUE):
    return line(f'M{x} {y}v24m-12-12 12 12 12-12',color) if length == 0 else line(f'M{x} {y}h{length}m-18-13 18 13-18 13',color)


def tick(x, y):
    return line(f'M{x} {y}l13 14 30-36',GREEN,9)


def cross(x,y):
    return line(f'M{x-12} {y-12}l24 24m0-24-24 24',RED,8)


def heart(x, y, size=1):
    return f'<path transform="translate({x} {y}) scale({size})" d="M0 12C-38-22-58 19 0 57C58 19 38-22 0 12" fill="#df5261"/>'


def caption(value):
    return text(250,305,value,22)


def book(x,y):
    return rect(x,y,64,78,BLUE,4)+line(f'M{x+9} {y}v78','#75d6ed',4)


def screen(body):
    return rect(55,40,390,235)+rect(55,40,390,35,'#dbe6ee')+circle(75,57,5,RED)+circle(93,57,5,GOLD)+body


def plate(x,y,r=62):
    return circle(x,y,r,'#e0eaf1')+circle(x,y,r-10,'white')+circle(x-16,y,18,GREEN)+circle(x+15,y+9,15,RED)


def calendar(busy=False):
    body=rect(65,55,370,200)+rect(65,55,370,45,BLUE)+text(250,86,'TODAY',23,'white')
    for n in range(4):
        body+=rect(88+n*85,120,70,108,RED if busy else '#dff4e9')+text(123+n*85,152,f'{10+n}:00',14)
        body+=cross(123+n*85,193) if busy else tick(104+n*85,193)
    return body


def scenes():
    out={}
    def add(name, body): out[name.lower()]=write(name,body)
    # Direction matters: the same exchange teaches two different viewpoints.
    for name,focus in [('borrow',390),('lend',100)]:
        add(name,person(100,104)+person(390,104,GREEN)+book(213,132)+arrow(150,230,190)+circle(focus,73,30,GOLD)+text(focus,82,'ME',18)+caption('Today: a book → tomorrow: return it'))
    add('ordinary', ''.join(rect(65+n*95,103,75,125,'#b9c9d6') for n in range(4))+arrow(250,48,0)+caption('One of many • the same as the others'))
    add('special',''.join(rect(65+n*95,103,75,125,GOLD if n==2 else '#b9c9d6') for n in range(4))+text(292,180,'★',44)+caption('Different from all the others'))
    add('casual',line('M165 85l55-25h60l55 25 35 65-50 25-15-30v115H195V145l-15 30-50-25z',BLUE,8)+line('M220 61q30 38 60 0',BLUE)+caption('T-shirt + jeans • a day off'))
    for name,count in [('experience',4),('experienced',5),('inexperienced',0)]:
        add(name,person(110,100)+rect(205,65,220,190)+text(315,99,'PROJECTS DONE',18)+''.join(text(250+n%3*60,151+n//3*57,'✓' if n<count else '–',37,GREEN if n<count else '#b1c0ca') for n in range(6))+caption('Learning by doing'))
    add('available',calendar()+caption('Time for a friend'))
    add('busy',calendar(True)+caption('Every hour has a task'))
    add('side dish',plate(175,155,90)+plate(362,175,47)+arrow(362,75,0)+caption('A small salad beside the main meal'))
    add('taste',person(165,95)+line('M185 106h110l35 15',GOLD,8)+circle(303,106,14,RED)+caption('Try a little food first'))
    add('order',person(105,105)+person(380,105,GREEN)+rect(175,70,145,110)+text(248,105,'MENU',22)+plate(248,145,25)+arrow(169,222,145)+caption('“Soup, please.”'))
    add('reserve',rect(90,130,320,35,'#b78357')+line('M120 165v85m260-85v85')+rect(180,65,140,64)+text(250,91,'ECE',24)+text(250,116,'19:00',20)+caption('A table saved for tonight'))
    add('contain',rect(115,60,270,195,'#dbeef5')+circle(180,130,26,RED)+circle(310,177,32,BLUE)+rect(220,90,48,58,GOLD)+caption('Three things inside one box'))
    add('scary',rect(145,100,210,150,'#3b4264')+line('M122 103l128-66 128 66','#3b4264',16)+rect(175,135,40,45,GOLD)+rect(285,135,40,45,GOLD)+rect(235,190,35,60,'#12172b')+circle(388,50,28,GOLD)+caption('A dark house at midnight'))
    add('survive',line('M30 230q25-28 50 0t50 0t50 0t50 0t50 0t50 0t50 0t50 0',BLUE)+person(250,91,GOLD,.8)+circle(250,180,43,RED)+circle(250,180,23,'#f4f8fc')+tick(365,130)+caption('Rescued • safe and alive'))
    add('stay',rect(65,145,370,70,'#c8ddea')+rect(75,118,93,40)+line('M65 145v100m370-30v30')+text(300,96,'MON → TUE → WED',23)+caption('Three nights in a hotel'))
    add('join',person(83,112)+person(312,112,GREEN)+person(405,112,GREEN)+arrow(150,168,95)+caption('One more person in the group'))
    add('social',person(105,117)+person(250,117,GREEN)+person(395,117,GOLD)+rect(65,25,190,60)+text(160,65,'Hello!',27)+rect(285,35,150,60)+text(360,75,'Hi!',27))
    add('loyalty',person(155,110)+person(345,110,GREEN)+heart(250,113,.8)+text(250,64,'THEN • NOW • ALWAYS',24)+line('M190 191h120',GREEN)+caption('Still by your side'))
    add('unconditional',heart(250,55,1.5)+person(110,122)+person(390,122,GREEN)+text(250,226,'✓ happy',20)+text(250,255,'✓ sad',20)+caption('Love in every situation'))
    add('priceless',rect(160,65,180,160,GOLD)+person(215,120,BLUE,.5)+person(285,120,GREEN,.5)+heart(250,125,.5)+text(250,270,'No amount of money',24))
    add('damage',rect(135,65,230,175,'#dbe6ee')+line('M230 65l38 45-40 35 39 28-34 67',RED,9)+caption('It was whole. Now it is broken.'))
    add('relationship',person(140,108)+person(360,108,GREEN)+line('M175 182h150',RED,7)+heart(250,115,.6)+caption('A connection between people'))
    add('snob',person(140,113)+person(365,83,GOLD)+text(360,51,'“Only the best!”',20)+cross(225,190)+caption('Looking down on others'))
    add('ridiculous',rect(35,65,430,205,'#dceff8')+line('M40 80q25-20 50 0t50 0t50 0t50 0t50 0t50 0t50 0t50 0',BLUE,4)+line('M150 164q100-145 200 0z',GOLD,7)+line('M250 162v62q0 35-27 12',GOLD,7)+circle(99,188,9,'white')+circle(382,221,14,'white')+caption('An umbrella under the sea?'))
    add('unbearable',person(160,115)+rect(317,55,45,155)+circle(339,229,38,RED)+rect(328,84,23,150,RED)+text(391,106,'45°C',25)+line('M94 98l-28-22m27 40-37 3m42 18-29 26',RED)+caption('Too much to tolerate'))
    add('energetic',person(235,103,GREEN)+line('M105 108l-30 45h40l-22 44M371 83l-30 45h40l-22 44',GOLD,10)+caption('Ready to run, play and move!'))
    for name,label in [('engaged','BEEP • BEEP'),('extension','Reception → 204')]:
        add(name,rect(165,42,170,225,'#26384d')+rect(182,67,136,153,'#dff4e9')+text(250,135,label,16)+text(250,181,'☎',48)+circle(250,244,10,'white')+caption('The line is in use' if name=='engaged' else 'One office inside the building'))
    add('easy way',circle(80,180,24,BLUE)+circle(420,180,24,GREEN)+arrow(113,180,270,GREEN)+line('M80 125q70-120 150 0t190 0','#a0b0c0',4)+caption('A direct route • fewer steps'))
    add('clearly',rect(50,70,180,150,'#e0e5ea')+text(140,165,'A B C',36,'#b9c3cd')+rect(270,70,180,150)+text(360,165,'A B C',36)+tick(335,250)+caption('Easy to see and understand'))
    add('confirm',screen(text(250,129,'Tuesday • 14:00',24)+rect(155,170,190,62,'#dff4e9')+text(250,211,'YES ✓',26,GREEN)))
    add('browse',screen(''.join(rect(88+n*110,101,94,91,'#c7e4ef')+line(f'M{100+n*110} 218h68',BLUE) for n in range(3))+arrow(330,250,70)))
    add('comment',screen(rect(90,95,300,64,'#dbeaf5')+text(240,135,'A photo from our trip',18)+rect(122,186,274,57)+text(259,223,'“What a lovely place!”',18)))
    add('habit',text(250,67,'MON  TUE  WED  THU  FRI',25)+''.join(tick(65+n*85,118) for n in range(5))+rect(190,180,120,62,BLUE)+text(250,220,'READ',25,'white')+caption('The same action every day'))
    add('take risks',line('M40 240h155m110 0h155','#836f55',14)+line('M195 240l55-110 55 110',GOLD,7)+person(250,103,BLUE,.65)+caption('A difficult crossing • a possible fall'))
    add('extreme',rect(55,140,390,42,'#dce5ed')+rect(370,140,75,42,RED)+arrow(250,90,160,RED)+text(95,220,'LOW',20)+text(405,220,'HIGH',20)+caption('At the far end of the scale'))
    add('disappointing',text(130,60,'EXPECTED',22)+text(370,60,'GOT',22)+text(130,151,'★★★★★',25,GOLD)+text(370,151,'★☆☆☆☆',25,RED)+person(250,204,BLUE,.45)+caption('Much less than you hoped for'))
    add('all-inclusive',rect(40,75,420,170)+text(250,116,'ONE PRICE',27)+text(110,176,'ROOM',19)+text(250,176,'FOOD',19)+text(390,176,'DRINKS',19)+''.join(tick(x,211) for x in [90,230,370]))
    add('mysterious',rect(150,75,200,180,'#35466e')+text(250,202,'?',105,'white')+line('M150 98l100-42 100 42',GOLD)+caption('What could be inside?'))
    add('doing chores',line('M145 56v149',BLUE,12)+line('M145 205l-40 60h80z',GOLD,15)+rect(260,171,100,87,BLUE)+line('M271 173q39-65 78 0')+caption('Sweep • clean • tidy'))
    add('arrive on time',circle(145,147,87,'white')+line('M145 147V88m0 59h-50')+text(145,265,'09:00',28)+person(350,105,GREEN)+tick(335,60)+caption('The lesson starts at 09:00'))
    add('break a promise',rect(55,52,170,90)+text(140,91,'“I will come.”',19)+tick(119,126)+rect(275,52,170,90)+text(360,91,'No one came.',19)+cross(360,118)+line('M155 227h65l20-24 20 45 20-21h65',RED)+caption('Words and actions do not agree'))
    add('be good at',person(115,112)+rect(235,70,190,175)+text(330,120,'MATHS',26)+text(330,185,'10 / 10',35,GREEN)+tick(307,225))
    add('In fact,',rect(45,70,190,145)+text(140,121,'“Two?”',28)+text(140,178,'○ ○',35)+arrow(240,142,35)+rect(295,70,160,145)+text(375,121,'Actually…',23)+text(375,178,'● ● ●',29,GREEN)+caption('Check what is really true'))
    add('For example,',rect(65,45,370,90,'#dbeaf5')+text(250,102,'FRUIT',32)+arrow(250,142,0)+circle(160,234,34,RED)+circle(340,234,34,GOLD)+text(160,290,'apple',22)+text(340,290,'orange',22))
    add('before the meal',rect(40,65,170,170)+line('M79 128h90m-70 0v-28h44v28M109 149v45m28-45v45',BLUE)+arrow(224,150,60)+plate(380,151,65)+caption('Wash your hands → then eat'))
    add('process',''.join(rect(38+n*160,110,105,100,BLUE if n==0 else GREEN if n==2 else GOLD)+text(90+n*160,174,str(n+1),38,'white') for n in range(3))+arrow(152,160,38)+arrow(312,160,38)+caption('One stage leads to the next'))
    add('gain',rect(85,164,120,95,BLUE)+rect(300,76,120,183,GREEN)+text(145,214,'10',34,'white')+text(360,169,'20',34,'white')+arrow(210,100,75,GREEN)+caption('You have more than before'))
    add('goldsmith',person(145,84)+rect(58,210,384,28,'#b88960')+line('M80 238v42m340-42v42')+circle(320,178,26,GOLD)+circle(320,178,15,'#f4f8fc')+line('M238 107l45 83',BLUE,9)+rect(217,90,60,22,'#6c7984')+caption('Making jewellery by hand'))
    add('gravity of the matter',circle(250,70,24,RED)+line('M250 110v110m-20-23 20 23 20-23',BLUE,9)+line('M60 256h380',GREEN,12)+caption('Earth pulls objects down'))
    add('deserve',book(75,100)+text(107,232,'PRACTICE',19)+arrow(162,156,110)+circle(365,145,58,GOLD)+text(365,164,'★',60,'white')+line('M339 190l-15 69 41-20 36 20-15-69',GOLD,8)+caption('Hard work earns a reward'))
    # Religious festivals: welcoming guests and sharing food, no sacrifice scene.
    for name,label in [('Eid al-Fitr (Festival of Ramadan)','After Ramadan'),('Eid al-Adha (Festival of Sacrifice)','Sharing with others')]:
        add(name,circle(408,55,27,GOLD)+circle(422,45,25,'#f4f8fc')+person(105,115)+person(395,115,GREEN)+plate(250,205,50)+text(250,70,'EID',32)+caption(label))
    # Distinct genre panels, with visual instruments that support each label.
    body=''
    for n,label in enumerate(['ROCK','JAZZ','CLASSICAL']):
        x=20+n*160
        body+=rect(x,50,140,224,['#fde7d9','#e3edf9','#e4f1e9'][n])+text(x+70,250,label,19)
        if n==0: body+=circle(x+60,165,30,RED)+circle(x+78,139,23,RED)+line(f'M{x+75} 143l36-63',GOLD,11)
        elif n==1: body+=line(f'M{x+54} 83h20v86q0 40 32 0',GOLD,16)+line(f'M{x+99} 166l12-30 21 22',GOLD,10)
        else:
            body+=rect(x+23,101,95,102,'#26384d',2)
            for k in range(6): body+=rect(x+25+k*15,159,14,43,'white',0)
    add('types of music',body)
    return out
