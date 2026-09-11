"""Original Grade 6 lessons, aligned to the supplied 2026 MEB books.

Only the curriculum scope and word meanings come from the books. Stories,
examples, questions, dialogues and worksheet tasks are authored for ENG HUB.
SB/WB references use printed page numbers (also PDF page numbers).
"""


def words(title, rows):
    return {"title": title, "items": [dict(zip(("en", "tr"), row.split("|")))
                                      for row in rows.strip().splitlines()]}


def grammar(key, title, rule, examples, checks):
    return {"id": key, "title": title, "rule": rule,
            "examples": [row.split("|") for row in examples.strip().splitlines()],
            "checks": [row.split("|") for row in checks.strip().splitlines()]}


UNITS = [
    dict(id="u1", title="School Life", titleTr="Okul Hayatı", emoji="🏫", sb=[27, 40], wb=[9, 16],
         goals=["Describe school roles and routines.", "Ask about a celebration and give instructions."],
         groups=[
             words("People and responsibilities", """leader|lider
listener|dinleyici
permission|izin
instruction|yönerge
guide|rehber
helpful|yardımsever
support|desteklemek
volunteer|gönüllü olmak"""),
             words("School routines", """greet|selamlamak
follow|takip etmek
enter|girmek
pack|hazırlayıp çantaya koymak
term|dönem
regularly|düzenli olarak
carefully|dikkatlice
willingly|isteyerek"""),
             words("Days to celebrate", """ceremony|tören
celebration|kutlama
parade|geçit töreni
flag|bayrak
national anthem|ulusal marş
speech|konuşma
festival|festival
celebrate|kutlamak"""),
             words("Working together", """successful|başarılı
keen|hevesli
try|denemek
pass|sınavı geçmek
fail|başarısız olmak
cheerfully|neşeyle
before|önce
later|daha sonra""")],
         grammar=[
             grammar("articles", "A, an and the", "İlk kez söylenen tekil isim: a/an. Sesli sesle başlayan kelime: an. Bilinen, belirli isim: the.",
                     """Mina is *a* group leader.|Mina *bir* grup lideri.
There is *an* invitation on the desk.|Sıranın üzerinde *bir* davetiye var.
The invitation is for *the* school ceremony.|Davetiye *okul töreni* için.""",
                     """Arda carries *a* flag.|an|are|am
There is *an* empty chair near the stage.|a|are|am
I can see a flag. *The* flag is red.|A|An|Are"""),
             grammar("imperatives", "Classroom instructions", "Yönerge için fiilin yalın hâli kullanılır. Olumsuz yönerge: Don't + fiil.",
                     """*Listen* to the group leader.|Grup liderini *dinleyin*.
*Don't push* in the corridor.|Koridorda *itmeyin*.""",
                     """*Follow* the instructions, please.|Follows|Following|To follows
*Don't run* near the stage, please.|Doesn't run|Not running|Don't runs"""),
             grammar("present-simple", "School routines", "I/you/we/they + fiil; he/she/it + fiil-s. Olumsuz: don't/doesn't + yalın fiil. Soru: Do/Does + özne + yalın fiil?",
                     """Our leader *checks* the list every morning.|Liderimiz her sabah listeyi *kontrol eder*.
*Does* Ada *carry* the flag on Mondays?|Ada pazartesileri bayrağı *taşır mı*?
She *doesn't carry* it on Fridays.|Cuma günleri onu *taşımaz*.""",
                     """The guide *greets* visitors every day.|greet|greeting|are greet
Our leaders *don't leave* the hall untidy.|doesn't leave|not leave|don't leaves
*Does* your friend help at ceremonies?|Do|Is|Are"""),
             grammar("frequency", "How regularly?", "Always, usually, often, sometimes, never: ana fiilden önce; am/is/are'dan sonra gelir.",
                     """We *usually* pack our bags at night.|Çantalarımızı *genellikle* akşam hazırlarız.
Our teacher is *always* helpful.|Öğretmenimiz *her zaman* yardımseverdir.""",
                     """Choose the correct order: *We often greet visitors.*|We greet often visitors.|We greets often visitors.|We often greeting visitors.
Choose the correct order: *Lina is never late.*|Lina never is late.|Lina is late never.|Lina never late is."""),
             grammar("pronouns", "People and object pronouns", "Özne: I, you, he, she, it, we, they. Fiilden sonra nesne: me, you, him, her, it, us, them.",
                     """The new students are here. I can help *them*.|Yeni öğrenciler burada. *Onlara* yardım edebilirim.
This is our guide. *She* knows the school.|Bu bizim rehberimiz. *O* okulu tanıyor.""",
                     """We need some help. Please support *us*.|we|our|ours
Eren is the leader. Ask *him* about the parade.|he|his|they
Mina and Ada are listeners. *They* listen carefully.|Them|Her|Us"""),
             grammar("existence-questions", "People, places and times", "There is + tekil; there are + çoğul. Who: kim, when: ne zaman, what: ne, where: nerede.",
                     """*There are* two flags in the hall.|Salonda iki bayrak *var*.
*When* is the school ceremony?|Okul töreni *ne zaman*?""",
                     """*There is* a speech after the parade.|There are|Are there|There be
*Who* leads the group? Our English teacher.|Where|When|What time
*Where* is the ceremony? In the hall.|Who|When|How often
*What* do you carry? A flag.|Who|When|Where""")],
         storyTitle="The welcome team",
         story="Mina is a volunteer in the school welcome team. Every Monday, she greets new students at the gate. Eren is the group leader. He usually checks the names, and Mina shows the students their classrooms. Today is 23 April. There is a celebration in the garden. Two students carry flags. The headteacher gives a short speech before the music starts. Mina's job is to help the visitors. She listens carefully and answers their questions. The team never leaves rubbish in the garden.",
         reading=[("When does Mina usually greet new students?", "Every Monday."),
                  ("Who checks the names?", "Eren, the group leader."),
                  ("Where is the celebration?", "In the garden."),
                  ("What happens before the music?", "The headteacher gives a short speech.")],
         truth=[("Mina is the group leader.", False), ("Two students carry flags.", True), ("The team leaves rubbish behind.", False)],
         dialogue=[("Visitor", "Where is the ceremony?", "Tören nerede?"), ("Guide", "It is in the garden. Follow me, please.", "Bahçede. Lütfen beni takip edin."),
                   ("Visitor", "When does it start?", "Ne zaman başlıyor?"), ("Guide", "At ten. There are seats for you near the stage.", "Saat onda. Sahnenin yanında sizin için koltuklar var.")],
         listening="This is the plan for our school celebration. The parade starts at nine. The speech starts at half past nine. Ada carries the flag. The visitors sit in the garden.",
         listenQs=[("Parade time", "09:00"), ("Speech time", "09:30"), ("Flag carrier", "Ada"), ("Visitors' place", "The garden")],
         speaking="You are a guide and a visitor at a school event. Ask about the place, time and leader. Give two polite instructions. Swap roles.",
         writing="Design a welcome card for a new student. Write six sentences: two routines, one frequency sentence, one school location and two instructions.",
         model="Welcome to our school. We greet our teachers every morning. Our leader checks the classroom. We usually read after lunch. There is a library upstairs. Follow the signs. Don't run in the corridor."),

    dict(id="u2", title="Classroom Life", titleTr="Sınıf Hayatı", emoji="✏️", sb=[41, 54], wb=[17, 24],
         goals=["Compare routines with actions happening now.", "Check information with question tags and use numbers."],
         groups=[
             words("Study habits", """habit|alışkanlık
diary|günlük
research|araştırma
method|yöntem
review|gözden geçirmek
revise|tekrar etmek
practise|pratik yapmak
remember|hatırlamak"""),
             words("Learning together", """peer|akran
pair|ikili
group|grup
task|görev
share|paylaşmak
repeat|tekrarlamak
read aloud|sesli okumak
read silently|sessiz okumak"""),
             words("A useful routine", """brush|fırçalamak
rest|dinlenmek
focus|odaklanmak
mark|işaretlemek
effective|etkili
creative|yaratıcı
in turns|sırayla
together|birlikte"""),
             words("Numbers and order", """one hundred|yüz
one hundred and fifty|yüz elli
two hundred|iki yüz
five hundred|beş yüz
first|birinci
twelfth|on ikinci
twenty-third|yirmi üçüncü
fiftieth|ellinci""")],
         grammar=[
             grammar("present-progressive", "Right now", "Şimdi devam eden eylem: am/is/are + fiil-ing. Olumsuzda not eklenir; soruda am/is/are başa gelir.",
                     """Our group *is researching* a new topic now.|Grubumuz şimdi yeni bir konu *araştırıyor*.
*Are* you *reading* silently?|Sessizce *okuyor musun*?
I *am not resting* at the moment.|Şu anda *dinlenmiyorum*.""",
                     """Listen! Two peers *are reading* aloud.|reads|is reading|readed
The class *isn't resting* now; it is working.|aren't resting|doesn't resting|not rest
*Is* your partner marking the answers now?|Does|Do|Are"""),
             grammar("now-vs-routine", "Usually and today", "Every day/usually: geniş zaman. Now/at the moment: şimdiki zaman. Zaman ifadesi anlamı gösterir.",
                     """I usually *work* in pairs.|Genellikle ikili *çalışırım*.
Today I *am working* on my own.|Bugün tek başıma *çalışıyorum*.""",
                     """Every evening, Arda *reviews* his diary.|is reviewing|review|are reviewing
Right now, Arda *is sharing* his diary with a peer.|shares|share|are sharing"""),
             grammar("question-tags-present", "Checking a routine", "Olumlu geniş zaman cümlesi + don't/doesn't; olumsuz cümle + do/does. Sonda uygun özne zamiri kullanılır.",
                     """You revise every day, *don't you*?|Her gün tekrar yapıyorsun, *değil mi*?
Lina doesn't read aloud, *does she*?|Lina sesli okumuyor, *değil mi*?""",
                     """Eren usually works in a group, *doesn't he*?|don't he|isn't he|does he
The peers don't rest here, *do they*?|don't they|are they|does they"""),
             grammar("question-tags-progressive", "Checking an action now", "Şimdiki zamanda ek soru am/is/are ile kurulur. Olumlu cümleye olumsuz, olumsuz cümleye olumlu ek soru gelir.",
                     """They are sharing ideas, *aren't they*?|Fikirlerini paylaşıyorlar, *değil mi*?
Ada isn't writing now, *is she*?|Ada şimdi yazmıyor, *değil mi*?""",
                     """The teacher is marking a page, *isn't she*?|doesn't she|is she|aren't she
We aren't reading aloud, *are we*?|do we|aren't we|is we"""),
             grammar("possessives", "Whose study things?", "My, your, his, her, its, our, their bir isimden önce gelir ve sahipliği gösterir.",
                     """We are checking *our* answers.|*Kendi* cevaplarımızı kontrol ediyoruz.
Lina is reading *her* diary.|Lina *kendi* günlüğünü okuyor.""",
                     """The boys are sharing *their* research.|they|them|his
I write new words in *my* diary.|me|I|he"""),
             grammar("how-often-adverbs", "Frequency and word order", "How often? sorusunu every day, twice a week gibi ifadelerle cevapla. Often fiilden önce; carefully çoğunlukla nesneden sonra gelir.",
                     """*How often* do you revise vocabulary?|Kelimeleri *ne sıklıkla* tekrar edersin?
I read the instructions *carefully*.|Yönergeleri *dikkatlice* okurum.""",
                     """*How often* do you review? Twice a week.|What|Whose|How many
Choose the correct order: *She reads the task carefully.*|She carefully the task reads.|She the reads task carefully.|She reads carefully the task."""),
             grammar("cardinal-ordinal", "100 to 500; 1st to 50th", "Cardinal sayı miktarı, ordinal sayı sırayı gösterir. 100: one hundred. 21st: twenty-first. 40th: fortieth; 50th: fiftieth.",
                     """There are *three hundred* cards.|*Üç yüz* kart var.
This is the *thirty-second* task.|Bu, *otuz ikinci* görev.""",
                     """250 = *two hundred and fifty*|two hundred and fifteen|five hundred and twenty|twenty-five
40th = *fortieth*|fourteenth|fourth|forty
21st = *twenty-first*|twenty-one|twelfth|twenty-third
500 = *five hundred*|fifty|fifteenth|five thousand""")],
         storyTitle="A different study afternoon",
         story="Eren usually studies with one peer after school. They review words and read silently. On Wednesdays, Eren writes in his learning diary. Today his routine is different. He is working with three classmates on a research task. Ada is reading aloud. Tom is marking important words. Eren is checking their answers. They have two hundred cards, but they are only using the first fifty today. They take turns and share ideas. Their teacher visits the group twice a week.",
         reading=[("Who does Eren usually study with?", "One peer."), ("What is Ada doing today?", "She is reading aloud."),
                  ("How many cards have they got?", "Two hundred / 200."), ("How often does the teacher visit?", "Twice a week.")],
         truth=[("Eren writes in his diary on Wednesdays.", True), ("Tom is reading aloud today.", False), ("The group is using all 200 cards.", False)],
         dialogue=[("Ada", "You usually read silently, don't you?", "Genellikle sessiz okursun, değil mi?"), ("Eren", "Yes, but today I am reading to my group.", "Evet, ama bugün grubuma okuyorum."),
                   ("Ada", "How often do you revise these words?", "Bu kelimeleri ne sıklıkla tekrar ediyorsun?"), ("Eren", "Three times a week. This method helps me.", "Haftada üç kez. Bu yöntem bana yardımcı oluyor.")],
         listening="Our research group meets on Thursday. There are one hundred and fifty cards on the desk. We are using the twelfth task today. Maya is reading aloud while the others listen.",
         listenQs=[("Meeting day", "Thursday"), ("Number of cards", "150"), ("Task number", "12th / twelfth"), ("Reader", "Maya")],
         speaking="Partner A describes two study routines. Partner B checks them with question tags. Then describe two actions happening in your classroom now.",
         writing="Write a six-sentence study diary. Include two routines, two actions happening now, a frequency expression and a question tag.",
         model="I usually study with a peer. We review new words every evening. Today I am reading aloud. My partner is marking the answers. We check our diaries twice a week. This method is useful, isn't it?"),

    dict(id="u3", title="Personal Life", titleTr="Kişisel Hayat", emoji="🙋", sb=[55, 68], wb=[25, 32],
         goals=["Describe appearance, clothes and character respectfully.", "Ask about possessions and make comparisons."],
         groups=[
             words("Body parts", """back|sırt
leg|bacak
knee|diz
ankle|ayak bileği
heart|kalp
stomach|mide
skin|cilt
physical|fiziksel"""),
             words("Clothes and belongings", """trainers|spor ayakkabısı
swimsuit|mayo
tights|külotlu çorap
pocket|cep
necklace|kolye
bracelet|bileklik
wallet|cüzdan
jewellery|takı"""),
             words("Character", """patient|sabırlı
polite|kibar
caring|şefkatli
clever|zeki
organised|düzenli
independent|bağımsız
focused|odaklanmış
social|sosyal"""),
             words("Describing a person", """tidy|tertipli
serious|ciddi
rude|kaba
lazy|tembel
weak|güçsüz
lovely|hoş
brilliant|harika
look|görünüş""")],
         grammar=[
             grammar("have-got", "Possessions and appearance", "I/you/we/they have got; he/she/it has got. Olumsuz: haven't/hasn't got. Soru: Have/Has + özne + got?",
                     """Lina *has got* a silver bracelet.|Lina'nın gümüş bir bilekliği *var*.
*Have* you *got* your trainers?|Spor ayakkabıların *var mı*?
I *haven't got* a necklace.|Kolyem *yok*.""",
                     """My cousin *has got* curly hair.|have got|is got|are got
*Has* your brother got a wallet?|Have|Does|Is
We *haven't got* blue trainers.|hasn't got|don't got|isn't got"""),
             grammar("whose", "Whose belongings?", "Whose sahipliği sorar. İsim + 's ile cevap verilebilir. Whose is this? / Whose trainers are these?",
                     """*Whose* bracelet is this?|Bu *kimin* bilekliği?
It is *Maya's* bracelet.|Bu, *Maya'nın* bilekliği.""",
                     """*Whose* wallet is this? It belongs to Ben.|Who's|Where|Who
These are *Ada's* trainers. They belong to Ada.|Ada|Adas|Adas's"""),
             grammar("comparatives", "Comparing two", "Kısa sıfat + -er + than; uzun sıfatlarda more + sıfat + than. big/bigger, tidy/tidier.",
                     """This pocket is *bigger than* that pocket.|Bu cep, o cepten *daha büyük*.
Lina is *more patient than* her cousin.|Lina kuzeninden *daha sabırlı*.""",
                     """The red bracelet is *longer* than the blue one.|long|longest|more long
This wallet is *more colourful* than that one.|colourfuller|most colourful|colourfulest
My desk is *tidier* than it was before.|tidyer|tidiest|more tidyest"""),
             grammar("superlatives", "Comparing a group", "Üç veya daha fazlası arasında: the + sıfat-est / the most + uzun sıfat. Karşılaştırılan grubu belirt.",
                     """This is *the smallest* pocket on the jacket.|Bu, ceketin *en küçük* cebi.
That is *the most colourful* bracelet in the box.|O, kutudaki *en renkli* bileklik.""",
                     """Of these three bags, the green one is *the biggest*.|bigger|big|more big
This is *the most comfortable* swimsuit in the shop.|more comfortable|comfortabler|comfortable"""),
             grammar("irregular-comparison", "Good, better, best", "good/better/the best; bad/worse/the worst. Bunlara ayrıca more veya -er eklenmez.",
                     """This kit is *better* for swimming.|Bu takım yüzmek için *daha iyi*.
This is *the worst* pocket for a phone.|Bu, telefon için *en kötü* cep.""",
                     """Of the three kits, this is *the best*.|better|gooder|good
My old trainers are *worse* than my new ones.|badder|worst|the bad""")],
         storyTitle="The missing bracelet",
         story="Three friends are preparing a clothes display. Maya has got a green swimsuit and white trainers. Her cousin Leo has got blue trainers. Leo's trainers are bigger than Maya's. Noor has got a small wallet with two pockets. It is the smallest wallet on the table. The friends find a purple bracelet under a chair. Whose bracelet is it? Noor asks everyone politely. It belongs to Maya. Noor is patient and organised: she makes a list of all the clothes before they start the display.",
         reading=[("What colour are Leo's trainers?", "Blue."), ("How many pockets has Noor's wallet got?", "Two."),
                  ("Where is the bracelet?", "Under a chair."), ("Whose bracelet is it?", "Maya's.")],
         truth=[("Maya's trainers are bigger than Leo's.", False), ("Noor asks politely.", True), ("Noor makes a list after the display.", False)],
         dialogue=[("Noor", "Whose wallet is this?", "Bu kimin cüzdanı?"), ("Leo", "It is mine. Have you got one too?", "Benim. Senin de var mı?"),
                   ("Noor", "Yes. My wallet is smaller than yours.", "Evet. Benim cüzdanım seninkinden daha küçük."), ("Leo", "This one has got the biggest pocket of the three.", "Üçünün arasında en büyük cep bunda.")],
         listening="The lost property box has three things today. There is a red wallet, a blue bracelet and a pair of white trainers. The bracelet belongs to Leo. The trainers belong to Maya.",
         listenQs=[("Wallet colour", "Red"), ("Bracelet colour", "Blue"), ("Bracelet owner", "Leo"), ("Trainers owner", "Maya")],
         speaking="Choose three classroom objects. Ask whose they are. Compare two objects, then say which is the biggest or most colourful of the three.",
         writing="Write a description for a lost-property display. Include three belongings, one whose question, two comparisons and one superlative. Describe people respectfully.",
         model="We have got a wallet, a bracelet and some trainers. Whose bracelet is this? The wallet is smaller than my wallet. The trainers are more colourful than my trainers. The bracelet is the smallest item of the three."),
]

UNITS += [
    dict(id="u4", title="Family Life", titleTr="Aile Hayatı", emoji="👨‍👩‍👧", sb=[69, 82], wb=[33, 40],
         goals=["Talk about jobs, homes and family plans.", "Distinguish arrangements from timetables."],
         groups=[
             words("Jobs", """author|yazar
dentist|diş hekimi
engineer|mühendis
reporter|muhabir
cook|aşçı
pilot|pilot
lawyer|avukat
designer|tasarımcı"""),
             words("At work", """manager|yönetici
assistant|asistan
professor|profesör
officer|memur
company|şirket
factory|fabrika
employee|çalışan
employer|işveren"""),
             words("Homes", """apartment|apartman dairesi
address|adres
entrance|giriş
roof|çatı
upstairs|üst katta
downstairs|alt katta
floor|kat
key|anahtar"""),
             words("Inside a home", """bookshelf|kitaplık
drawer|çekmece
curtain|perde
carpet|halı
blanket|battaniye
pillow|yastık
refrigerator|buzdolabı
sink|lavabo""")],
         grammar=[
             grammar("arrangements", "Family arrangements", "Kesinleşmiş gelecek düzenlemesi: am/is/are + fiil-ing + gelecek zaman ifadesi (tomorrow, next Saturday).",
                     """We *are visiting* a designer tomorrow.|Yarın bir tasarımcıyı *ziyaret ediyoruz*.
My aunt *is moving* next Saturday.|Teyzem gelecek cumartesi *taşınıyor*.""",
                     """Our visit is arranged. We *are meeting* the author tomorrow.|met|meeting|is meeting
Mum's appointment is booked. She *is seeing* the dentist on Friday.|seeing|are seeing|saw"""),
             grammar("future-timetables", "Timetables", "Resmî program veya tarifede gelecek olaylar için geniş zaman kullanılır: The train leaves at ...",
                     """The workshop *starts* at eleven tomorrow.|Atölye yarın saat on birde *başlıyor*.
The next train *leaves* at 08:20.|Sonraki tren 08.20'de *kalkıyor*.""",
                     """According to the timetable, the flight *leaves* at 7 tomorrow.|leave|leaving|left
The office tour *begins* at noon next Monday, according to the programme.|begin|beginning|began"""),
             grammar("when-while", "When and while", "When bir olayın zamanını belirtir. While aynı anda süren iki eylemi bağlar. Gelecek anlamlı zaman yan cümlesinde genellikle geniş zaman kullanılır.",
                     """I check the address *when* I leave home.|Evden çıktığımda adresi kontrol ederim. (*When*: -dığında)
Dad reads *while* Mum draws.|Annem çizim yaparken babam okur. (*While*: -ken)""",
                     """*While* the cook is preparing lunch, the reporter is writing.|Whose|Which|Where
I will call you when I *arrive* at the apartment.|will arrive|arriving|arrives"""),
             grammar("which", "Choosing between things", "Which sınırlı seçenekler arasından hangisini sorduğumuzu gösterir. Which + isim + soru yapısı.",
                     """*Which* apartment is your uncle's, the first or the second?|Birinci mi ikinci mi, *hangi* daire amcanın?
*Which* job do you like, reporter or designer?|Muhabirlik mi tasarımcılık mı, *hangi* işi seviyorsun?""",
                     """*Which* floor is your home on, the first or the second?|Whose|Who|How often
*Which* key opens this door, the small one or the large one?|Who|When|How much"""),
             grammar("reflexive-pronouns", "Doing something yourself", "Özne ve nesne aynı kişiyse: myself, yourself, himself, herself, itself, ourselves, yourselves, themselves. By myself: tek başıma.",
                     """The author introduces *herself*.|Yazar *kendini* tanıtıyor.
We make the model house *ourselves*.|Maket evi *kendimiz* yapıyoruz.""",
                     """The children draw their dream home *themselves*.|himself|ourselves|herself
I carry my own bag *myself*.|yourself|himself|themselves
Leo introduces *himself* to the designer.|herself|itself|yourself""")],
         storyTitle="A visit and a new home",
         story="Lina's aunt is a designer. She works for a small company near the station. On Saturday, Lina and her father are visiting her office. Their train leaves at 09:40, and the office tour starts at eleven. After the tour, they are helping Lina's uncle at his new apartment. It is on the second floor. The entrance is next to a bakery. Lina is making a label for his key herself. While her father carries a bookshelf, her uncle checks the address on a box.",
         reading=[("What is Lina's aunt's job?", "She is a designer."), ("When does the train leave?", "At 09:40."),
                  ("Which floor is the new apartment on?", "The second floor."), ("Who makes the key label?", "Lina makes it herself.")],
         truth=[("The office tour starts at eleven.", True), ("The apartment is next to a hospital.", False), ("Lina's father carries a bookshelf.", True)],
         dialogue=[("Lina", "Which office are we visiting tomorrow?", "Yarın hangi ofisi ziyaret ediyoruz?"), ("Dad", "Your aunt's. The tour starts at eleven.", "Teyzeninkini. Tur saat on birde başlıyor."),
                   ("Lina", "Are we helping Uncle Sam afterwards?", "Sonra Sam amcaya yardım ediyor muyuz?"), ("Dad", "Yes. He is moving, and we are carrying the boxes ourselves.", "Evet. Taşınıyor ve kutuları kendimiz taşıyoruz.")],
         listening="Our family is visiting a factory on Tuesday. The tour starts at ten fifteen. My cousin is an engineer there. After the tour, we are visiting my aunt in her apartment on the third floor.",
         listenQs=[("Visit day", "Tuesday"), ("Tour start", "10:15"), ("Cousin's job", "Engineer"), ("Apartment floor", "Third / 3rd")],
         speaking="Plan a family visit to a workplace. Agree on an appointment and use a timetable. Ask which place to visit. Explain what each person can do themselves.",
         writing="Make a family agenda with six sentences. Include two arrangements, one timetable, one when or while sentence, a which question and a reflexive pronoun.",
         model="We are visiting my aunt on Sunday. She is showing us her office. The bus leaves at 09:10. I check our tickets when we leave home. Which stop is near the office? We carry our bags ourselves."),

    dict(id="u5", title="Life in the Neighbourhood & City", titleTr="Mahalle ve Şehir Hayatı", emoji="🏙️", sb=[83, 96], wb=[41, 48],
         goals=["Describe a past festival and travel around a city.", "Use was/were, reasons, prepositions and activity preferences."],
         groups=[
             words("Festivals and events", """festival|festival
audience|seyirci
musician|müzisyen
wedding|düğün
perform|sahne almak
organise|düzenlemek
raise money|para toplamak
local|yerel"""),
             words("Around the event", """crowded|kalabalık
pleased|memnun
tired|yorgun
jazz|caz
pop|pop müzik
rock|rock müzik
rap|rap müzik
creative|yaratıcı"""),
             words("Transport", """tram|tramvay
underground|metro
van|kamyonet
lorry|kamyon
motorcycle|motosiklet
ship|gemi
vehicle|araç
public transport|toplu taşıma"""),
             words("Finding the way", """sign|tabela
direction|yön
overpass|üst geçit
underpass|alt geçit
parking|park yeri
railway line|demiryolu hattı
on foot|yürüyerek
by car|arabayla""")],
         grammar=[
             grammar("was-were", "At yesterday's event", "Geçmişte durum veya yer: I/he/she/it was; you/we/they were. Olumsuz: wasn't/weren't. Soruda was/were başa gelir.",
                     """The local festival *was* busy yesterday.|Yerel festival dün kalabalık*tı*.
The musicians *weren't* tired.|Müzisyenler yorgun *değildi*.
*Were* you near the stage?|Sahnenin yanında *mıydın*?""",
                     """The audience *was* very pleased last night.|were|is|are
The trams *weren't* crowded yesterday.|wasn't|isn't|was
*Were* the musicians on the stage at eight yesterday?|Was|Are|Is"""),
             grammar("past-be-tags", "Checking past information", "Was/were ile başlayan geçmiş durum cümlesinde ek soru da was/were ile kurulur. Olumlu/olumsuz yönünü ters çevir.",
                     """The concert was local, *wasn't it*?|Konser yereldi, *değil mi*?
You weren't late, *were you*?|Geç kalmadın, *değil mi*?""",
                     """The musicians were ready, *weren't they*?|wasn't they|were they|didn't they
The van wasn't outside, *was it*?|wasn't it|were it|did it"""),
             grammar("why-when", "Reasons and time", "Why neden, when ne zaman anlamındadır. Why sorusuna because ile sebep verilebilir.",
                     """*Why* was the square crowded?|Meydan *neden* kalabalıktı?
*Because* there was a concert.|*Çünkü* konser vardı.""",
                     """*When* was the art event? Last Saturday.|Why|Who|Whose
Why were you tired? *Because* the walk was long.|When|Whose|Which"""),
             grammar("gerunds-infinitives", "Activities and plans", "Enjoy + fiil-ing; want/plan + to + yalın fiil. Like + -ing, etkinlik beğenisini anlatmanın bir yoludur.",
                     """I enjoy *listening* to jazz.|Caz *dinlemekten* keyif alırım.
We plan *to visit* the art festival.|Sanat festivalini *ziyaret etmeyi* planlıyoruz.""",
                     """The audience enjoys *watching* the dancers.|to watching|watch|to watch
They want *to organise* a local concert.|organising|organise|to organising"""),
             grammar("place-movement", "Places and movement", "Konum: in front of, behind, under, beside/next to, between, among, near. Hareket: across (karşıya), through (içinden), into (içine), out of (dışına), onto (üstüne).",
                     """The tram stop is *between* the park and the hall.|Tramvay durağı park ile salonun *arasında*.
Walk *through* the underpass.|Alt geçidin *içinden* yürüyün.""",
                     """The sign is *between* the two doors.|among|onto|through
The tram goes *through* a tunnel.|onto|among|between
The musician steps *onto* the stage.|among|between|behind
The visitors walk *out of* the hall into the garden.|between|among|under"""),
             grammar("time-transport", "Time and transport", "At + saat; on + gün/tarih; in + ay/yıl; for + süre. Ulaşım: by car/bus/tram, fakat on foot.",
                     """The show starts *on* Sunday *at* six.|Gösteri *pazar günü* *saat altıda* başlıyor.
We go there *on foot*.|Oraya *yürüyerek* gideriz.""",
                     """The art festival is *in* May.|at|on|by
The show was *on* Friday.|at|in|by
We travel to the event *by* tram.|on|at|in
The visitors were at the festival *for* two hours.|on|at|by""")],
         storyTitle="A festival diary",
         story="Yesterday was the local art festival. The square was crowded, but the library garden was quiet. Our favourite musicians were on the small stage at four. There was a sign between the two entrances. It showed the way to the tram stop. We enjoy travelling by tram because the roads near the square are busy. My little brother likes walking through the underpass. At the end of the afternoon, we were tired but pleased. We plan to visit the music event next month.",
         reading=[("Where was it quiet?", "In the library garden."), ("When were the musicians on stage?", "At four."),
                  ("Where was the sign?", "Between the two entrances."), ("Why do they enjoy travelling by tram?", "Because the roads near the square are busy.")],
         truth=[("The square was quiet.", False), ("The sign showed the way to the tram stop.", True), ("They plan to visit another event.", True)],
         dialogue=[("Noor", "The festival was crowded, wasn't it?", "Festival kalabalıktı, değil mi?"), ("Ben", "Yes, but the audience was pleased.", "Evet, ama seyirciler memnundu."),
                   ("Noor", "I enjoy travelling by tram. Which stop is near the hall?", "Tramvayla gitmekten hoşlanıyorum. Hangi durak salona yakın?"), ("Ben", "The stop beside the library. We can walk from there.", "Kütüphanenin yanındaki durak. Oradan yürüyebiliriz.")],
         listening="The music event was on Sunday. The jazz show was at five. The stage was behind the library. There was no parking near the event, so public transport was a useful choice.",
         listenQs=[("Event day", "Sunday"), ("Show time", "17:00 / five"), ("Stage location", "Behind the library"), ("Unavailable service", "Parking")],
         speaking="Describe an imaginary festival yesterday. Ask why and when, check one detail with a past question tag, then explain how to reach the event.",
         writing="Write a six-sentence festival review. Include was and were, a reason, a place preposition, a transport phrase and a plan using to + verb.",
         model="The festival was on Saturday. The musicians were excellent. The audience was pleased because the songs were exciting. The stage was behind the school. Public transport was useful. We plan to visit the next festival."),

    dict(id="u6", title="Life in the World & Culture", titleTr="Dünya ve Kültür Hayatı", emoji="🌍", sb=[97, 110], wb=[49, 56],
         goals=["Talk about countries, languages and food experiences.", "Describe completed events using regular past verbs."],
         groups=[
             words("Countries", """France|Fransa
Germany|Almanya
Italy|İtalya
Spain|İspanya
Denmark|Danimarka
Sweden|İsveç
Poland|Polonya
the Netherlands|Hollanda"""),
             words("Nationalities and languages", """French|Fransız; Fransızca
German|Alman; Almanca
Italian|İtalyan; İtalyanca
Spanish|İspanyol; İspanyolca
Danish|Danimarkalı; Danca
Swedish|İsveçli; İsveççe
Polish|Polonyalı; Lehçe
Dutch|Hollandalı; Hollandaca"""),
             words("Food and culture", """cuisine|mutfak kültürü
ingredient|malzeme
appetiser|iştah açıcı başlangıç yemeği
main course|ana yemek
dessert|tatlı
dumpling|içi doldurulmuş hamur yemeği
food stall|yiyecek standı
heritage|kültürel miras"""),
             words("Flavours and experiences", """crispy|çıtır
crunchy|kıtır
sour|ekşi
spicy|baharatlı
bitter|acı (tat)
homemade|ev yapımı
tradition|gelenek
capital|başkent""")],
         grammar=[
             grammar("past-regular", "A completed experience", "Geçmişte biten eylem: fiil + -ed. live/lived, try/tried, stop/stopped. Yesterday, last week gibi zaman ifadeleri kullanılır.",
                     """We *visited* a food market last Sunday.|Geçen pazar bir yiyecek pazarını *ziyaret ettik*.
Maya *tried* a homemade dessert.|Maya ev yapımı bir tatlı *denedi*.""",
                     """Last night, the chef *prepared* a new dish.|prepare|prepares|preparing
They *studied* the recipe yesterday.|studyed|study|studying
Our group *stopped* at a food stall last Saturday.|stoped|stop|stopping"""),
             grammar("past-negative", "What didn't happen?", "Geçmişte olumsuz: didn't + yalın fiil. Fiile ayrıca -ed eklenmez.",
                     """I *didn't taste* the spicy soup.|Baharatlı çorbayı *tatmadım*.
The visitors *didn't stay* for dinner.|Ziyaretçiler akşam yemeğine *kalmadı*.""",
                     """We didn't *visit* the pop-up market yesterday.|visited|visiting|visits
The chef *didn't heat* the dessert; it was served cold.|didn't heated|doesn't heated|not heated"""),
             grammar("past-questions", "Questions about a visit", "Did + özne + yalın fiil? Kısa cevap: Yes, ... did / No, ... didn't. Where/When/What/Why sorunun başına gelebilir.",
                     """*Did* you *enjoy* the food event?|Yemek etkinliğinden *keyif aldın mı*?
Where *did* they *stay*?|Nerede *kaldılar*?""",
                     """Did Noor *try* the Italian dish?|tried|tries|trying
Did the visitors like the appetiser? Yes, they *did*.|do|were|are
Where *did* you travel last summer?|do|does|are"""),
             grammar("regular-past-tags", "Checking a past experience", "Olumlu geçmiş fiil cümlesi + didn't + zamir; didn't ile olumsuz cümle + did + zamir.",
                     """You enjoyed the main course, *didn't you*?|Ana yemeği beğendin, *değil mi*?
Lina didn't order soup, *did she*?|Lina çorba sipariş etmedi, *değil mi*?""",
                     """The chef heated the bread, *didn't he*?|wasn't he|doesn't he|did he
They didn't visit Poland, *did they*?|didn't they|were they|do they""")],
         storyTitle="Our classroom culture market",
         story="Last Thursday, our class organised a culture market. Each group prepared a food poster and introduced a country. Leo's group presented Italy. Noor's group described Sweden. They used English for their presentations and practised a few Swedish words too. Maya prepared a poster about ingredients in a homemade dessert. Visitors listened to the groups and asked questions. I tried a crispy appetiser, but I didn't taste the spicy dish. At the end, we thanked the visitors and cleaned the room together.",
         reading=[("When was the culture market?", "Last Thursday."), ("Which country did Leo's group present?", "Italy."),
                  ("What was Maya's poster about?", "Ingredients in a homemade dessert."), ("What didn't the writer taste?", "The spicy dish.")],
         truth=[("Noor's group described Sweden.", True), ("The groups only spoke Swedish.", False), ("They cleaned the room afterwards.", True)],
         dialogue=[("Maya", "Did you visit the culture market?", "Kültür pazarını ziyaret ettin mi?"), ("Leo", "Yes. I enjoyed the homemade dishes.", "Evet. Ev yapımı yemekleri beğendim."),
                   ("Maya", "You tried the crispy appetiser, didn't you?", "Çıtır başlangıç yemeğini denedin, değil mi?"), ("Leo", "Yes, I did. But I didn't order a dessert.", "Evet. Ama tatlı sipariş etmedim.")],
         listening="Yesterday our group presented Denmark at a school event. We prepared four posters. The visitors asked about Danish words. We served an appetiser, but we didn't prepare a main course.",
         listenQs=[("Country presented", "Denmark"), ("Poster count", "Four"), ("Language mentioned", "Danish"), ("Dish not prepared", "A main course")],
         speaking="Interview a partner about an imaginary culture market. Ask three Did questions and one Where or When question. Check a detail with a past question tag.",
         writing="Write a six-sentence report about an imaginary food event. Use regular past verbs, one negative sentence and one question tag. Mention a country and a food description.",
         model="Yesterday we organised a culture event. Our group presented Spain. We prepared a poster about a traditional dish. I tasted a homemade dessert. I didn't order a spicy dish. We enjoyed the event, didn't we?"),
]

UNITS += [
    dict(id="u7", title="Life in Nature & Global Problems", titleTr="Doğada Hayat ve Küresel Sorunlar", emoji="🌳", sb=[111, 124], wb=[57, 64],
         goals=["Describe a past outdoor adventure.", "Explain obligations and suggest actions to protect nature."],
         groups=[
             words("Outdoor activities", """hiking|doğa yürüyüşü
climbing|tırmanış
sailing|yelken sporu
rafting|rafting
snowboarding|snowboard sporu
camp|kamp yapmak
cycle|bisiklete binmek
fish|balık tutmak"""),
             words("An outdoor adventure", """adventure|macera
ride|binmek
run|koşmak
ski|kayak yapmak
pick|toplamak
plant|dikmek
danger|tehlike
responsibility|sorumluluk"""),
             words("Problems", """pollution|kirlilik
rubbish|çöp
plastic|plastik
smoke|duman
energy|enerji
heat|ısı
destroy|yok etmek
increase|artırmak"""),
             words("Solutions", """protect|korumak
prevent|önlemek
reduce|azaltmak
recycle|geri dönüştürmek
reusable|yeniden kullanılabilir
replace|yerine koymak
remove|kaldırmak
save|tasarruf etmek""")],
         grammar=[
             grammar("past-irregular", "Past adventures", "Bazı geçmiş fiiller -ed almaz: go/went, see/saw, take/took, eat/ate, drink/drank, ride/rode, run/ran, find/found.",
                     """We *went* hiking on Sunday.|Pazar günü doğa yürüyüşüne *gittik*.
Lina *saw* rubbish near the river.|Lina nehrin yanında çöp *gördü*.""",
                     """Yesterday, the group *took* reusable bottles.|taked|take|takes
Leo *rode* his bike to the camp last week.|rided|ride|rides
After the hike, we *drank* water.|drinked|drunk|drink"""),
             grammar("irregular-past-questions", "Questions and negatives", "Düzensiz fiiller de did/didn't sonrasında yalın hâle döner: Did you go? / I didn't go.",
                     """*Did* you *see* any smoke?|Hiç duman *gördün mü*?
We *didn't leave* our rubbish there.|Çöpümüzü orada *bırakmadık*.""",
                     """Did the campers *find* any plastic bottles?|found|finded|finds
We didn't *swim* in the river.|swam|swum|swimming"""),
             grammar("irregular-past-tags", "Checking an adventure", "Düzensiz geçmiş fiille olumlu cümle + didn't; olumsuz cümle + did. Özneye uygun zamiri seç.",
                     """Maya found the path, *didn't she*?|Maya patikayı buldu, *değil mi*?
They didn't eat here, *did they*?|Burada yemek yemediler, *değil mi*?""",
                     """Your friends went sailing, *didn't they*?|weren't they|don't they|did they
The guide didn't see smoke, *did she*?|didn't she|was she|does she"""),
             grammar("must-mustnt", "Obligation and prohibition", "Must + yalın fiil zorunluluk; mustn't + yalın fiil yasak bildirir. Must üçüncü tekilde değişmez.",
                     """We *must protect* this habitat.|Bu yaşam alanını *korumalıyız*.
Visitors *mustn't leave* rubbish here.|Ziyaretçiler buraya çöp *bırakmamalı*.""",
                     """It is forbidden to enter this area. We *mustn't* enter.|must|have to|has to
Everyone *must use* the marked path; it is a camp rule.|must uses|must to use|must using"""),
             grammar("have-to", "Rules and necessity", "I/you/we/they have to; he/she/it has to + yalın fiil. Don't/doesn't have to: zorunlu değil. Mustn't: yasak. Bunlar farklı anlamlardır.",
                     """Every camper *has to carry* a water bottle.|Her kampçının su şişesi *taşıması gerekir*.
We *don't have to buy* new bags; we can reuse these.|Yeni çanta *almak zorunda değiliz*; bunları tekrar kullanabiliriz.""",
                     """The rule says each group *has to* sort its rubbish.|have to|has|must to
The activity is optional. You *don't have to* join.|mustn't|have to|must
*Does* each visitor have to bring a bottle?|Do|Is|Has""")],
         storyTitle="The river team",
         story="Last weekend, six friends went hiking with their teacher. They took water in reusable bottles and ate lunch near a river. After lunch, Noor found plastic bags under a tree. The group did not touch any sharp objects. They told their teacher and picked up safe litter with gloves. The teacher explained the camp rules: everyone has to use the marked path, and visitors must not leave rubbish. The friends came home with an idea. They want to replace single-use bags with reusable ones at school.",
         reading=[("Who went with the six friends?", "Their teacher."), ("What did Noor find?", "Plastic bags."),
                  ("What did they do about sharp objects?", "They did not touch them; they told the teacher."), ("What do they want to replace?", "Single-use bags.")],
         truth=[("They took reusable bottles.", True), ("They touched sharp objects.", False), ("Visitors can leave rubbish at the camp.", False)],
         dialogue=[("Noor", "You took a reusable bottle, didn't you?", "Yeniden kullanılabilir bir şişe aldın, değil mi?"), ("Leo", "Yes. We have to bring our own water.", "Evet. Kendi suyumuzu getirmemiz gerekiyor."),
                   ("Noor", "Did you see any rubbish near the river?", "Nehrin yanında hiç çöp gördün mü?"), ("Leo", "Yes. We must tell our teacher and help safely.", "Evet. Öğretmenimize söylemeli ve güvenli şekilde yardım etmeliyiz.")],
         listening="On Saturday, our group went cycling. We saw rubbish beside a lake. Our teacher gave us gloves. We collected twelve plastic bottles. Everyone had a reusable bag for the clean-up.",
         listenQs=[("Activity", "Cycling"), ("Rubbish location", "Beside a lake"), ("Equipment from the teacher", "Gloves"), ("Number of bottles", "Twelve / 12")],
         speaking="Describe an imaginary trip using went, saw and took. Partner B checks a detail with a question tag. Agree on two rules and one optional activity.",
         writing="Write a short eco-camp report: three past events with irregular verbs, one must rule, one have to rule and one optional action with don't have to.",
         model="We went hiking yesterday. We saw litter near the path. We took it to a bin with our teacher. Visitors must protect the forest. Everyone has to follow the camp rules. We don't have to buy new bags because we can reuse our old ones."),

    dict(id="u8", title="Life in the Universe & Future", titleTr="Evren ve Gelecekte Hayat", emoji="🚀", sb=[125, 138], wb=[65, 72],
         goals=["Talk about planets, extreme weather and life in the future.", "Distinguish plans, evidence and predictions."],
         groups=[
             words("The solar system", """Mercury|Merkür
Venus|Venüs
Earth|Dünya
Mars|Mars
Jupiter|Jüpiter
Saturn|Satürn
Uranus|Uranüs
Neptune|Neptün"""),
             words("Space words", """Sun|Güneş
Moon|Ay
orbit|yörünge
atmosphere|atmosfer
distance|mesafe
bright|parlak
visible|görünür
alive|canlı"""),
             words("Extreme weather", """storm|fırtına
thunder|gök gürültüsü
lightning|şimşek
flood|sel
drought|kuraklık
tornado|hortum
blizzard|tipi
hurricane|kasırga"""),
             words("Future life", """technology|teknoloji
invent|icat etmek
predict|tahmin etmek
expert|uzman
evidence|kanıt
intention|niyet
population|nüfus
source|kaynak""")],
         grammar=[
             grammar("going-to-plans", "Plans and intentions", "Önceden verilen karar: am/is/are going to + yalın fiil. Olumsuzda am/is/are'dan sonra not gelir.",
                     """We *are going to make* a planet model.|Bir gezegen modeli *yapacağız*.
Lina *isn't going to use* plastic for it.|Lina bunun için plastik *kullanmayacak*.""",
                     """Our plan is ready. We *are going to study* Mars tomorrow.|is going to study|going study|are going study
Ada has decided to draw Saturn. She *is going to draw* it tonight.|are going to draw|going to draw|is going draw"""),
             grammar("going-to-evidence", "Evidence now", "Şu anda görülen kanıta dayanarak beklenen olay için be going to kullanılır. Kanıtı cümlede belirt.",
                     """Look at the dark sky. It *is going to rain*.|Karanlık gökyüzüne bak. *Yağmur yağacak*.
That model is falling. It *is going to break*.|O model düşüyor. *Kırılacak*.""",
                     """Look! The cup is falling. It *is going to break*.|are going to break|is going break|going to break
The clouds are very dark. A storm *is going to start*.|are going to start|is going start|going start"""),
             grammar("will-predictions", "Predictions and hopes", "I think / I hope / I'm sure + will + yalın fiil geleceğe dair tahmin verir. Olumsuz: won't + yalın fiil. Tahminler kesin bilgi değildir.",
                     """I think future homes *will save* more energy.|Bence gelecekteki evler daha çok enerji *tasarrufu yapacak*.
I hope the river *won't dry* up.|Umarım nehir *kurumaz*.""",
                     """I think people *will invent* new kinds of vehicles.|will invents|will invented|will inventing
I hope tomorrow *won't be* stormy.|won't is|won't being|won't was"""),
             grammar("future-questions", "Asking about the future", "Will + özne + yalın fiil? / Am-Is-Are + özne + going to + yalın fiil? Yardımcı fiile uygun kısa cevap kullan.",
                     """*Will* the weather *change* tomorrow?|Yarın hava *değişecek mi*?
*Are* you *going to visit* the planetarium?|Planetaryumu *ziyaret edecek misin*?""",
                     """*Are* they going to present their model on Friday?|Will|Do|Does
Will the new technology help? Yes, it *will*.|is|does|did
Is Maya going to join us? No, she *isn't*.|won't|doesn't|aren't"""),
             grammar("future-tags", "Checking a future idea", "Will cümlesi + won't; won't cümlesi + will. Be going to yapısında ek soru am/is/are ile kurulur.",
                     """Your model will be ready, *won't it*?|Modelin hazır olacak, *değil mi*?
They are going to help, *aren't they*?|Yardım edecekler, *değil mi*?
She isn't going to travel, *is she*?|Seyahat etmeyecek, *değil mi*?""",
                     """The experts won't arrive late, *will they*?|won't they|are they|do they
Lina is going to draw Earth, *isn't she*?|won't she|doesn't she|is she
We will save energy, *won't we*?|don't we|aren't we|will we""")],
         storyTitle="The future classroom",
         story="Our science club is going to hold a future fair next month. Noor is going to make a model of the solar system. Leo is going to collect pictures of extreme weather. His display will include floods, droughts and blizzards. Maya wants to invent a classroom lamp that uses less energy. She thinks new technology will help schools in the future. These are ideas and predictions, not facts about the future. The group has a clear plan: they are going to use old boxes for every model.",
         reading=[("When is the fair?", "Next month."), ("Who is making a solar system model?", "Noor."),
                  ("What does Maya want to invent?", "A classroom lamp that uses less energy."), ("What materials are they going to use?", "Old boxes.")],
         truth=[("Leo is collecting extreme weather pictures.", True), ("Maya's prediction is a certain fact.", False), ("They plan to buy new plastic boxes.", False)],
         dialogue=[("Maya", "What are you going to show at the fair?", "Fuarda ne göstereceksin?"), ("Noor", "A model of the solar system. It will be ready soon.", "Bir Güneş sistemi modeli. Yakında hazır olacak."),
                   ("Maya", "You are going to use old boxes, aren't you?", "Eski kutuları kullanacaksın, değil mi?"), ("Noor", "Yes. I think the visitors will like that idea.", "Evet. Bence ziyaretçiler bu fikri beğenecek.")],
         listening="Our future fair is on Friday. Noor is going to show a model of Mars. Leo has three pictures of floods. Maya thinks future schools will use less energy. They are going to meet at the library at four.",
         listenQs=[("Fair day", "Friday"), ("Noor's planet", "Mars"), ("Number of flood pictures", "Three"), ("Meeting place", "The library")],
         speaking="Plan a future fair with a partner. Say what you are going to make. Add two predictions beginning I think or I hope. Check one plan and one prediction with question tags.",
         writing="Write six sentences about a future school. Include two going to plans, two will/won't predictions, one example of present evidence and one future question tag.",
         model="We are going to make a model classroom. We are going to use old boxes. I think our future school will save water. I hope it won't waste energy. Look at the loose roof on our model; it is going to fall. Our friends will help us, won't they?"),
]

# The app has one Revision route; it covers both opening revision sections.
UNITS.insert(0, dict(
    id="revision", title="Revision", titleTr="Genel Tekrar", emoji="🔄", sb=[15, 26], wb=None,
    goals=["Review school, personal and family life.", "Review the city, food, animals and holiday plans."],
    groups=[
        words("Revision 1: school", """library|kütüphane
laboratory|laboratuvar
canteen|kantin
playground|oyun alanı
science|fen bilimleri
music|müzik
timetable|ders programı
club|kulüp"""),
        words("Revision 1: personal and family life", """cousin|kuzen
grandparents|büyükanne ve büyükbaba
curly hair|kıvırcık saç
straight hair|düz saç
jeans|kot pantolon
raincoat|yağmurluk
get dressed|giyinmek
have breakfast|kahvaltı yapmak"""),
        words("Revision 2: places and food", """park|park
museum|müze
restaurant|restoran
tiny house|minik ev
soup|çorba
salad|salata
a slice of cake|bir dilim kek
a bottle of water|bir şişe su"""),
        words("Revision 2: nature and holidays", """forest|orman
desert|çöl
ocean|okyanus
island|ada
elephant|fil
parrot|papağan
camping|kamp yapma
swimming|yüzme""")],
    grammar=[
        grammar("r1-school-language", "Revision 1: school language", "A/an + tekil isim; the + bilinen isim. There is/are varlığı gösterir. Yönerge: yalın fiil. Must: kural veya zorunluluk.",
                """*There is* a science club in our school.|Okulumuzda fen kulübü *var*.
We *must listen* in the laboratory.|Laboratuvarda *dinlemeliyiz*.""",
                """There is *an* art room upstairs.|a|are|am
*There are* two clubs after school.|There is|There be|Is there
*Close* the door, please.|Closes|Closing|To closes
You *must* follow the laboratory rules.|mustn't|doesn't|is"""),
        grammar("r1-pronouns", "Revision 1: people and belongings", "Özne: I/he/she/we/they. Nesne: me/him/her/us/them. İsim önünde sahiplik: my/his/her/our/their.",
                """This is *our* classroom.|Bu *bizim* sınıfımız.
The guide knows *us*.|Rehber *bizi* tanıyor.""",
                """These are my cousins. *They* live nearby.|Them|Their|Us
We need a guide. Can you help *us*?|we|our|ours
Ben has a blue bag. This is *his* bag.|he|him|they"""),
        grammar("r1-time-routines", "Revision 1: time and habits", "Rutin: geniş zaman. He/she/it ile -s; does/doesn't sonrası yalın fiil. What time? saati, How often? sıklığı sorar.",
                """Maya *gets dressed* at seven.|Maya saat yedide *giyinir*.
*What time* does the club start?|Kulüp *saat kaçta* başlıyor?""",
                """My cousin *has* breakfast at eight every day.|have|having|is have
08:30 is *half past eight*.|half past nine|quarter past eight|quarter to eight
*How often* do you swim? Every Saturday.|What time|Whose|How many
Ben doesn't *walk* to school.|walks|walking|walked"""),
        grammar("r1-now-tags", "Revision 1: now and usually", "Şu an: am/is/are + -ing. Rutin: geniş zaman. Ek soru yardımcı fiili ve özneyi tekrar eder; olumlu/olumsuz yönü değişir.",
                """I usually *read* at home.|Genellikle evde *okurum*.
Today I *am reading* in the library.|Bugün kütüphanede *okuyorum*.""",
                """Look! The club members *are singing*.|sings|is singing|singed
Ada studies every day, *doesn't she*?|isn't she|don't she|does she
They are swimming, *aren't they*?|don't they|are they|isn't they
Choose the correct order: *We often visit our cousins.*|We visit often our cousins.|We visits often our cousins.|We often visiting our cousins."""),
        grammar("r1-preferences", "Revision 1: preferences", "Like/enjoy + -ing etkinlik beğenisini anlatır. Prefer A to B ile iki seçeneği karşılaştırabiliriz.",
                """I enjoy *playing* the guitar.|Gitar *çalmaktan* keyif alırım.
I *prefer swimming to* running.|Yüzmeyi koşmaya *tercih ederim*.""",
                """Lina enjoys *reading* stories.|read|to reading|reads
I prefer camping *to* staying in a hotel.|than|from|at"""),
        grammar("r2-possession", "Revision 2: homes and possession", "Have/has got sahipliği gösterir. There is/are bir yerde ne bulunduğunu söyler. In, on, under, next to konumu gösterir.",
                """The tiny house *has got* two windows.|Minik evin iki penceresi *var*.
Our tent is *next to* a tree.|Çadırımız bir ağacın *yanında*.""",
                """The house *has got* a small kitchen.|have got|are got|is got
The bag is *under* the table, on the floor below it.|on|over|into"""),
        grammar("r2-quantity-ordering", "Revision 2: food and quantity", "Sayılabilen çoğullar: how many; sayılamayanlar: how much. Some olumlu cümlede ve kibar istekte; any çoğunlukla olumsuz/soru cümlesinde. A bowl/slice/bottle of miktar belirtir.",
                """*How much* water have we got?|*Ne kadar* suyumuz var?
Can I have *a bowl of* soup, please?|Lütfen *bir kâse* çorba alabilir miyim?""",
                """*How many* apples have we got?|How much|Whose|What time
*How much* soup would you like?|How many|Which many|How often
There isn't *any* milk in the bottle.|many|a|an
Can I have a *slice* of cake, please?|bottle|bowlfuls|glass"""),
        grammar("r2-comparisons", "Revision 2: comparing animals", "İki varlık: -er/more ... than. Bir grup içinde: the -est/the most. Karşılaştırmayı verilen bilgiye göre yap.",
                """In this picture, the elephant is *bigger than* the deer.|Bu resimde fil geyikten *daha büyük*.
This is *the smallest* bird in our picture.|Bu, resmimizdeki *en küçük* kuş.""",
                """This tree is *taller* than that tree.|tallest|tall|more tall
Of these three birds, this is *the most colourful*.|more colourful|colourfuller|colourfulest"""),
        grammar("r2-can-permission", "Revision 2: ability and permission", "Can + yalın fiil yetenek anlatır. Can I ...? izin ister. Kısa cevap: Yes, you can / No, you can't.",
                """This bird *can fly*.|Bu kuş *uçabilir*.
*Can I* open the window?|Pencereyi *açabilir miyim*?""",
                """A parrot can *fly*.|flies|flying|flew
Can I sit here? Yes, you *can*.|do|are|have"""),
        grammar("r2-holidays-obligations", "Revision 2: holiday plans", "Plan: am/is/are going to + yalın fiil. Have/has to + yalın fiil zorunluluk bildirir. Where ile yer sorulur.",
                """We *are going to camp* by the lake.|Gölün yanında *kamp yapacağız*.
Everyone *has to bring* a water bottle.|Herkes su şişesi *getirmek zorunda*.""",
                """Our plan is ready. We *are going to visit* an island.|is going to visit|going visit|are going visit
*Where* are you going to stay? In a tiny house.|When|Who|How many
Every visitor *has to* follow the park rules.|have to|must to|has""")],
    storyTitle="Our weekend club plan",
    story="Our school nature club meets every Friday. We usually read about animals in the library, but today we are planning a weekend trip. My cousin Maya is checking a map. We are going to stay in a tiny house near a forest. It has got a kitchen and two bedrooms. There is a small restaurant next to it. We can walk by the lake and watch birds. Everyone has to bring a raincoat. I am packing a bottle of water and some sandwiches. We are excited, aren't we?",
    reading=[("When does the club meet?", "Every Friday."), ("What is Maya doing?", "Checking a map."),
             ("Where are they going to stay?", "In a tiny house near a forest."), ("What does everyone have to bring?", "A raincoat.")],
    truth=[("They usually read about animals in the library.", True), ("The tiny house has three bedrooms.", False), ("A restaurant is next to the house.", True)],
    dialogue=[("Maya", "Where are we going to stay?", "Nerede kalacağız?"), ("Leo", "In a tiny house. It has got two bedrooms.", "Minik bir evde. İki yatak odası var."),
              ("Maya", "Can I bring some fruit?", "Biraz meyve getirebilir miyim?"), ("Leo", "Yes. We have to bring our water bottles too.", "Evet. Su şişelerimizi de getirmemiz gerekiyor.")],
    listening="Our club meets at half past three on Friday. This weekend we are going to visit a forest. There are four people in our group. We have to bring raincoats. We are taking soup for lunch.",
    listenQs=[("Meeting time", "15:30 / half past three"), ("Destination", "A forest"), ("Group size", "Four"), ("Lunch", "Soup")],
    speaking="Partner A asks about school routines, time and family. Partner B asks about a holiday plan, food quantities and an activity you can do. Swap roles.",
    writing="Write a weekend club message. Include one routine, one action now, a place, a food quantity, a going to plan and a rule.",
    model="Our club meets on Fridays. Today we are checking a map. There is a lake near our camp. I have got a bottle of water. We are going to watch birds. Everyone has to follow the park rules."
))
