"""Book-led additions to existing lectures. Original examples; no PDF text copied.

Source editions are the user's ref_materials/books files. Page numbers below
are printed pages. Older PowerPoints guide presentation style, not curriculum.
Grade 6 already uses these exact books in content/g6/curriculum.json.
"""
import copy

BOOKS = {
    'g5': [
        {'file': 'ingilizce5_ders_kitabi.pdf', 'sha256': '8d59c95b5308343347cc0a439a76fc3f5a15c12af56f09c4296782ffa4c51c4b'},
        {'file': 'ingilizce5_calisma_kitabi.pdf', 'sha256': 'ca5dd51d9c136e56b8476c810c228b358e6d50ca54ea4fb6609cd11fc6fd972d'},
    ],
    'g8': [{'file': 'ref_book_8th.pdf', 'sha256': 'cfe63ba2aaecbe2e20ed3aa9567bb4bcf9f6c867b27ec88c12ac83b8cb5912f6'}],
}


def section(title, title_tr, rule, examples, before):
    return dict(title=title, titleTr=title_tr, rule=rule, examples=examples, before=before)


# Each row: English with teaching focus, Turkish, exact Turkish focus, visual.
# Pictures reference words in the same lesson; emoji is a deliberate fallback.
SECTIONS = {
    'g5/u1': [section('People and places — am / is / are', 'İnsanlar ve yerler',
        'I → *am*; he / she / it → *is*; you / we / they → *are*. Soru için bu sözcük başa gelir.', [
        ('I *am* a student.', 'Ben bir öğrenciyim.', ['yim'], 'student'),
        ('Our teacher *is* in the library.', 'Öğretmenimiz kütüphanede.', ['de.'], 'library'),
        ('*Are* the students in the classroom?', 'Öğrenciler sınıfta mı?', ['mı'], 'classroom'),
    ], 'A / AN / THE')],
    'g5/u2': [section('School routines — Simple Present', 'Okul rutinleri ve sorumluluklar',
        'I / you / we / they → yalın fiil; he / she / it → fiil + *-s*. *What time do ...?* saat sorar.', [
        ('We *tidy up* our desks after class.', 'Dersten sonra sıralarımızı toplarız.', ['toplarız'], 'tidy up'),
        ('The Maths lesson *starts* at nine.', 'Matematik dersi saat dokuzda başlar.', ['ar.'], 'Maths'),
        ('*What time* do your lessons finish?', 'Derslerin saat kaçta biter?', ['saat kaçta'], 'finish'),
    ], 'Classroom Rules')],
    'g5/u3': [section('Adverbs of Frequency', 'Ne sıklıkla?',
        '*always / usually / often / sometimes / never* çoğunlukla ana fiilden önce, am / is / are sonrasında gelir.', [
        ('I *always* wear my uniform at school.', 'Okulda her zaman üniformamı giyerim.', ['her zaman'], 'uniform'),
        ('She *sometimes* wears a hat.', 'O bazen şapka takar.', ['bazen'], 'hat'),
        ('My shoes are *usually* clean.', 'Ayakkabılarım genellikle temizdir.', ['genellikle'], 'shoes'),
    ], 'Simple Present — Positive')],
    'g5/u7': [section('Animal habitats', 'Hayvanlar nerede yaşar?',
        '*Where do ... live?* yaşam alanını sorar. Cevap: *They live in ...*', [
        ('*Where* do lions live?', 'Aslanlar nerede yaşar?', ['nerede'], 'lion'),
        ('Sharks live *in the sea*.', 'Köpek balıkları denizde yaşar.', ['denizde'], 'shark'),
        ('Monkeys live *in forests*.', 'Maymunlar ormanlarda yaşar.', ['ormanlarda'], 'monkey'),
    ], 'can / cannot')],
    'g8/u2': [section('Opinions and interests', 'Görüşler ve ilgi alanları',
        '*I think ...* görüş belirtir. *be fond of / be keen on / can’t stand + isim veya fiil-ing* beğeni anlatır.', [
        ('I *think* jazz is relaxing.', 'Bence caz rahatlatıcı.', ['Bence'], 'relaxing'),
        ('I am *fond of* listening to music.', 'Müzik dinlemekten hoşlanırım.', ['hoşlanırım'], 'types of music'),
        ("I *can't stand* loud music.", 'Gürültülü müziğe katlanamam.', ['katlanamam'], 'loud'),
    ], 'Preferences')],
    'g8/u3': [section('Food preferences and inquiries', 'Yemek tercihleri ve sorular',
        '*prefer A to B* tercih belirtir. *What / How + should + özne + fiil?* ile hazırlama sürecini sorarız.', [
        ('I *prefer* soup to salad.', 'Çorbayı salataya tercih ederim.', ['tercih ederim'], 'bowl'),
        ('What *should* we add next?', 'Sırada ne eklemeliyiz?', ['meliyiz'], 'ingredient'),
        ('How *should* I slice the bread?', 'Ekmeği nasıl dilimlemeliyim?', ['meliyim'], 'slice'),
    ], 'Imperatives')],
    'g8/u4': [section('Decisions now — will', 'Konuşurken verilen kararlar',
        'O anda verilen karar veya yardım teklifi: *will + yalın fiil*. *I will → I’ll*.', [
        ("The phone is ringing. I *will* answer it.", 'Telefon çalıyor. Ben açacağım.', ['acağım'], 'pick up'),
        ("She is busy. I *will* call back later.", 'O meşgul. Sonra tekrar arayacağım.', ['acağım'], 'get back'),
        ("You need a pen? I*'ll* get one for you.", 'Kaleme mi ihtiyacın var? Sana bir tane getireceğim.', ['eceğim'], 'memo'),
    ], 'On the Phone')],
    'g8/u5': [section('Accepting, refusing and explaining', 'Kabul etme, reddetme ve açıklama',
        'Bir isteğe *Sure / Of course* ile cevap verebiliriz. Reddederken *Sorry, ... because ...* ile neden açıklarız.', [
        ('*Sure*, I can help you upload the photo.', 'Tabii, fotoğrafı yüklemene yardım edebilirim.', ['Tabii'], 'upload'),
        ("Sorry, I *can't* reply now because I am doing homework.", 'Üzgünüm, ödev yaptığım için şimdi cevap veremem.', ['emem'], 'reply'),
        ('I cannot join the video call *because* my connection is slow.', 'Bağlantım yavaş olduğu için görüntülü aramaya katılamıyorum.', ['olduğu için'], 'connection'),
    ], 'Asking for Help')],
    'g8/u6': [section('Adventure preferences and reasons', 'Macera tercihleri ve nedenler',
        '*prefer A to B*; *would rather + yalın fiil + than + yalın fiil*. *because* bir neden ekler.', [
        ('I *prefer* rafting to motor racing.', 'Raftingi motor yarışına tercih ederim.', ['tercih ederim'], 'rafting'),
        ('I *would rather* go kayaking than go caving.', 'Mağaracılık yapmaktansa kanoya binmeyi tercih ederim.', ['tercih ederim'], 'kayaking'),
        ('I like paragliding *because* it is exciting.', 'Heyecan verici olduğu için yamaç paraşütünü severim.', ['olduğu için'], 'paragliding'),
    ], "should / shouldn't")],
    'g8/u7': [section('Describing and comparing places', 'Yerleri anlatma ve karşılaştırma',
        'Bir yeri *is / has* ile anlatabiliriz. Karşılaştırma: kısa sıfat + *-er than* veya *more + sıfat + than*.', [
        ('This town *has* an ancient castle.', 'Bu kasabanın eski bir kalesi var.', ['var'], 'ancient'),
        ('The countryside is *quieter* than the city.', 'Kırsal bölge şehirden daha sessiz.', ['daha sessiz'], 'countryside'),
        ('This palace is *more fascinating than* the museum.', 'Bu saray müzeden daha büyüleyici.', ['daha büyüleyici'], 'palace'),
    ], 'Simple Past — Regular'), section('Travel preferences and reasons', 'Tatil tercihleri ve nedenler',
        '*would rather + yalın fiil* veya *prefer + isim / fiil-ing* tercihi anlatır. *because* nedeni açıklar.', [
        ('I *would rather* visit a historic site than stay at a resort.', 'Bir tatil köyünde kalmaktansa tarihî bir yeri gezmeyi tercih ederim.', ['tercih ederim'], 'historic site'),
        ('We *prefer* rural holidays to city breaks.', 'Kırsalda tatil yapmayı şehir tatillerine tercih ederiz.', ['tercih ederiz'], 'rural'),
        ('I want to visit this town *because* it is peaceful.', 'Huzurlu olduğu için bu kasabayı ziyaret etmek istiyorum.', ['olduğu için'], 'peaceful'),
    ], 'Simple Past — Regular')],
    'g8/u8': [section('Sharing responsibilities', 'Sorumlulukları paylaşma',
        '*be responsible for / be in charge of + isim veya fiil-ing* sorumlu olduğumuz işi anlatır.', [
        ('I am *responsible for* setting the table.', 'Sofrayı kurmaktan sorumluyum.', ['sorumluyum'], 'set the table'),
        ('My brother is *in charge of* doing the laundry.', 'Erkek kardeşim çamaşır yıkamaktan sorumlu.', ['sorumlu'], 'do the laundry'),
        ('Who is *responsible for* washing the dishes?', 'Bulaşıkları yıkamaktan kim sorumlu?', ['sorumlu'], 'wash the dishes'),
    ], 'have to / has to'), section('Likes and dislikes about chores', 'Ev işleriyle ilgili beğeniler',
        '*like / enjoy / dislike / hate / can’t stand + fiil-ing* ev işleri hakkındaki duygularımızı anlatır.', [
        ('I *enjoy* setting the table.', 'Sofrayı kurmaktan keyif alırım.', ['keyif alırım'], 'set the table'),
        ('I *dislike* ironing.', 'Ütü yapmaktan hoşlanmam.', ['hoşlanmam'], 'iron'),
        ("I *can't stand* washing the dishes.", 'Bulaşık yıkamaya katlanamam.', ['katlanamam'], 'wash the dishes'),
    ], 'Asking for Help')],
    'g8/u9': [section('Science now — Present Continuous', 'Şu anda yapılan bilimsel çalışmalar',
        'Şu anda: *am / is / are + fiil-ing*. Olumsuzda *not* eklenir; soruda am / is / are başa gelir.', [
        ('The students *are doing* an experiment now.', 'Öğrenciler şimdi bir deney yapıyor.', ['ıyor'], 'do an experiment'),
        ('Ece *is examining* a cell at the moment.', 'Ece şu anda bir hücreyi inceliyor.', ['iyor'], 'cell'),
        ('*Are* they testing the new machine?', 'Yeni makineyi test ediyorlar mı?', ['mı'], 'high-tech'),
        ('They *are not using* the test tubes now.', 'Şimdi deney tüplerini kullanmıyorlar.', ['mıyorlar'], 'test tube'),
    ], 'Passive Voice — Present'), section('Science then — Simple Past', 'Geçmişte yapılan çalışmalar',
        'Geçmişte biten olay: düzenli fiil + *-ed* veya düzensiz fiilin ikinci hâli. *didn’t / Did* sonrasında yalın fiil.', [
        ('Our class *tested* the robot yesterday.', 'Sınıfımız dün robotu test etti.', ['etti'], 'high-tech'),
        ('Ece *found* a mistake in her results.', 'Ece sonuçlarında bir hata buldu.', ['buldu'], 'result'),
        ("We *didn't* finish the experiment yesterday.", 'Dün deneyi bitirmedik.', ['medik'], 'do an experiment'),
        ('*Did* they record the results?', 'Sonuçları kaydettiler mi?', ['mi'], 'result'),
    ], 'Passive Voice — Present')],
    'g8/u10': [section('Causes and results — because / so', 'Neden ve sonuç',
        '*because* neden, *so* sonuç bildirir. Aynı bağlantı için ikisini birlikte kullanmayız.', [
        ('The roads are closed *because* there is a flood.', 'Sel olduğu için yollar kapalı.', ['olduğu için'], 'flood'),
        ('There is a drought, *so* the fields are dry.', 'Kuraklık var, bu yüzden tarlalar kuru.', ['bu yüzden'], 'drought'),
        ('We stayed indoors *because* there was a storm.', 'Fırtına olduğu için içeride kaldık.', ['olduğu için'], 'storm'),
    ], 'Predictions — will')],
}


def source_ref(unit):
    grade, number = unit.split('/'); number = int(number[1:])
    start = 27 + (number - 1) * 14 if grade == 'g5' else 9 + (number - 1) * 16
    source = dict(books=BOOKS[grade], studentPages=[start, start + (13 if grade == 'g5' else 15)])
    if grade == 'g5':
        start = 9 + (number - 1) * 6
        source['workbookPages'] = [start, start + 5]
    return source


def align_slides(slides, unit):
    base = copy.deepcopy([s for s in slides if not s.get('bookAlignment') and not s.get('lessonRefresh')])
    if unit not in SECTIONS:
        return base
    words = {w['en'].lower(): w for s in base if s['type'] == 'vocab' for w in s['items']}
    for n, spec in enumerate(SECTIONS[unit], 1):
        pages = []
        for i, (en, tr, focus, word) in enumerate(spec['examples'], 1):
            # No new remote assets: reuse the lesson's existing media resolution/cache.
            visual = words.get(word.lower(), {})
            example = dict(en=en, tr=tr, trEm=focus)
            example.update({k: visual[k] for k in ('img', 'imageFit', 'imageSource', 'imageConcept', 'emoji') if k in visual})
            if not example.get('img') and not example.get('emoji'):
                raise ValueError(f'{unit}: missing picture for {word}')
            pages.append(dict(type='grammar', title=spec['title'], titleTr=spec['titleTr'],
                grammarId=f'book-{unit.replace("/", "-")}-{n}', rule=spec['rule'],
                examples=[example], part=[i, len(spec['examples'])], paced=True,
                bookAlignment=True, bookSource=source_ref(unit)))
        anchor = next((i for i, s in enumerate(base) if s.get('title') == spec['before']), None)
        if anchor is None:
            # Titles in old decks vary. Stay before language teaching / unit practice.
            anchor = next(i for i, s in enumerate(base) if s['type'] in ('grammar', 'mission', 'end'))
        base[anchor:anchor] = pages
    return base
