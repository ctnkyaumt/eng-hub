#!/usr/bin/env python3
"""Build the grade-8 presentations from the course book.

Source of truth is res/book_8.pdf (MEB 8th grade Student's Book):

  * vocabulary - every unit's own GLOSSARY list (book pages 169-170), grouped
    into sections and translated in tools/g8_vocab.py
  * grammar    - the functions the unit opener page states ("Making comparisons",
    "Expressing obligation", …), written here with starred keywords so
    polish_slides.py can turn them into fill-in-the-blank and ordering practice
  * extra words - whatever the unit's activity bank adds on top of the glossary,
    appended after it so the book always comes first

Run:  python tools/build_g8.py [--unit 1] [--words 60]
      python tools/polish_slides.py --grade 8     (practice slides + splitting)
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, THEMES, ensure  # noqa: E402
from g8_vocab import sections as book_sections  # noqa: E402

ACCENTS = {
    1: ["#f472b6", "#8b5cf6"], 2: ["#38bdf8", "#6366f1"], 3: ["#fb923c", "#ef4444"],
    4: ["#34d399", "#0ea5e9"], 5: ["#60a5fa", "#4f46e5"], 6: ["#f59e0b", "#dc2626"],
    7: ["#22d3ee", "#0284c7"], 8: ["#a78bfa", "#6366f1"], 9: ["#4ade80", "#059669"],
    10: ["#f87171", "#7c3aed"],
}

# Structures the syllabus lists for each grade-8 theme.
GRAMMAR = {
1: [
 {"type": "grammar", "title": "Making Invitations", "titleTr": "Davet etme",
  "rule": "Birini bir şeye davet ederken *Would you like to ...?*, *How about ...?* veya *Let's ...* kullanırız.",
  "chips": ["Would you like to ...?", "How about ...?", "Let's ...", "Why don't we ...?"],
  "examples": [
   {"en": "*Would you like to* come to my birthday party?", "tr": "Doğum günü partime gelmek ister misin?"},
   {"en": "*How about* going to the cinema tonight?", "tr": "Bu akşam sinemaya gitmeye ne dersin?"},
   {"en": "*Let's* study together at the library.", "tr": "Hadi kütüphanede birlikte çalışalım."},
   {"en": "*Why don't we* play basketball after school?", "tr": "Okuldan sonra neden basketbol oynamıyoruz?"}]},
 {"type": "compare", "title": "Accepting & Refusing", "titleTr": "Kabul etme ve reddetme",
  "rule": "Daveti kabul ederken sevinç, reddederken *özür + mazeret* belirtiriz.",
  "columns": [
   {"title": "ACCEPT ✅", "tone": "good", "examples": [
    {"en": "*I'd love to*, thanks!", "tr": "Çok isterim, teşekkürler!"},
    {"en": "*Sure*, that sounds great.", "tr": "Tabii, kulağa harika geliyor."},
    {"en": "*Of course*, I'll be there.", "tr": "Elbette, orada olacağım."}]},
   {"title": "REFUSE ⛔", "tone": "bad", "examples": [
    {"en": "*I'm sorry*, I can't. I have to study.", "tr": "Üzgünüm, gelemem. Ders çalışmam gerek."},
    {"en": "*I'd love to, but* I'm busy tomorrow.", "tr": "Çok isterdim ama yarın meşgulüm."},
    {"en": "*Maybe next time*, I'm not feeling well.", "tr": "Belki başka zaman, kendimi iyi hissetmiyorum."}]}]},
 {"type": "dialogue", "title": "Talking with Friends", "titleTr": "Arkadaşlarla konuşma",
  "dialogues": [
   {"lines": [{"who": "Ali", "text": "Would you like to join our chess club?"},
              {"who": "Deniz", "text": "I'd love to! When do you meet?"}]},
   {"lines": [{"who": "Ece", "text": "How about a picnic on Sunday?"},
              {"who": "Mert", "text": "I'm sorry, I can't. I'm visiting my grandparents."}]},
   {"lines": [{"who": "Sena", "text": "Let's watch a film tonight."},
              {"who": "Kaan", "text": "Sure, that sounds great!"}]}]},
],
2: [
 {"type": "grammar", "title": "Simple Present — Routines", "titleTr": "Geniş zaman: günlük hayat",
  "rule": "Alışkanlıklardan ve düzenli işlerden bahsederken geniş zaman kullanırız. He / She / It ile fiile *-s* eklenir.",
  "chips": ["always", "usually", "often", "sometimes", "never"],
  "examples": [
   {"en": "I *go* to the gym twice a week.", "tr": "Haftada iki kez spor salonuna giderim."},
   {"en": "She *watches* series in her free time.", "tr": "O boş zamanında dizi izler."},
   {"en": "We *don't* stay up late on school nights.", "tr": "Okul gecelerinde geç saate kadar oturmayız."},
   {"en": "*Does* he play the guitar? — Yes, he does.", "tr": "O gitar çalar mı? — Evet, çalar."}]},
 {"type": "grammar", "title": "Preferences", "titleTr": "Tercihleri anlatma",
  "rule": "*prefer*, *would rather* ve *like/love/enjoy + V-ing* ile tercihlerimizi söyleriz.",
  "chips": ["prefer ... to ...", "would rather", "enjoy + V-ing"],
  "examples": [
   {"en": "I *prefer* pop music *to* jazz.", "tr": "Pop müziği caza tercih ederim."},
   {"en": "She *would rather* read a book than watch TV.", "tr": "O televizyon izlemektense kitap okumayı yeğler."},
   {"en": "They *enjoy* hanging out with friends.", "tr": "Arkadaşlarıyla vakit geçirmekten hoşlanırlar."},
   {"en": "We *love* going to concerts.", "tr": "Konserlere gitmeyi çok severiz."}]},
 {"type": "grammar", "title": "How often ...?", "titleTr": "Sıklık sorma",
  "rule": "Bir işin ne sıklıkla yapıldığını *How often ...?* ile sorarız. Cevapta sıklık zarfı veya *once / twice / three times a week* kullanılır.",
  "examples": [
   {"en": "*How often* do you go swimming?", "tr": "Ne sıklıkla yüzmeye gidersin?"},
   {"en": "I go swimming *twice a week*.", "tr": "Haftada iki kez yüzmeye giderim."},
   {"en": "He *hardly ever* plays computer games.", "tr": "O neredeyse hiç bilgisayar oyunu oynamaz."},
   {"en": "They *always* have breakfast together.", "tr": "Onlar her zaman birlikte kahvaltı yaparlar."}]},
],
3: [
 {"type": "grammar", "title": "Imperatives in Recipes", "titleTr": "Tariflerde emir cümleleri",
  "rule": "Tarif verirken fiilin yalın hâli ile emir cümlesi kurarız.",
  "chips": ["chop", "stir", "boil", "add", "pour", "serve"],
  "examples": [
   {"en": "*Chop* the onions into small pieces.", "tr": "Soğanları küçük parçalar hâlinde doğra."},
   {"en": "*Add* a teaspoon of salt.", "tr": "Bir çay kaşığı tuz ekle."},
   {"en": "*Boil* the water for five minutes.", "tr": "Suyu beş dakika kaynat."},
   {"en": "*Don't* forget to stir the soup.", "tr": "Çorbayı karıştırmayı unutma."}]},
 {"type": "grammar", "title": "Sequencing Words", "titleTr": "Sıralama ifadeleri",
  "rule": "Tarifin adımlarını *first, then, next, after that, finally* ile sıralarız.",
  "chips": ["first", "then", "next", "after that", "finally"],
  "examples": [
   {"en": "*First*, wash the vegetables.", "tr": "Önce sebzeleri yıka."},
   {"en": "*Then*, slice the tomatoes.", "tr": "Sonra domatesleri dilimle."},
   {"en": "*After that*, mix everything in a bowl.", "tr": "Ondan sonra her şeyi bir kasede karıştır."},
   {"en": "*Finally*, serve the salad cold.", "tr": "Son olarak salatayı soğuk servis et."}]},
 {"type": "compare", "title": "How much / How many", "titleTr": "Miktar sorma",
  "rule": "Sayılabilen isimler için *How many*, sayılamayanlar için *How much* kullanılır.",
  "columns": [
   {"title": "HOW MANY 🔢", "tone": "good", "examples": [
    {"en": "*How many* eggs do we need?", "tr": "Kaç yumurtaya ihtiyacımız var?"},
    {"en": "*How many* potatoes are there?", "tr": "Kaç patates var?"},
    {"en": "We need *three* tomatoes.", "tr": "Üç domatese ihtiyacımız var."}]},
   {"title": "HOW MUCH ⚖️", "tone": "bad", "examples": [
    {"en": "*How much* flour do you need?", "tr": "Ne kadar una ihtiyacın var?"},
    {"en": "*How much* sugar is there?", "tr": "Ne kadar şeker var?"},
    {"en": "Add *a cup of* milk.", "tr": "Bir fincan süt ekle."}]}]},
],
4: [
 {"type": "grammar", "title": "On the Phone", "titleTr": "Telefonda konuşma kalıpları",
  "rule": "Telefonda kibar kalıplar kullanırız: *Could I speak to ...?*, *Hold on, please.*, *Can I take a message?*",
  "chips": ["Could I speak to ...?", "Hold on, please.", "Can I take a message?", "Speaking."],
  "examples": [
   {"en": "*Could I speak to* Mr Yılmaz, please?", "tr": "Bay Yılmaz ile görüşebilir miyim, lütfen?"},
   {"en": "*Hold on*, please. I'll put you through.", "tr": "Lütfen bekleyin. Sizi bağlıyorum."},
   {"en": "*Can I take a message*?", "tr": "Mesajınızı alabilir miyim?"},
   {"en": "Sorry, she *isn't available* right now.", "tr": "Üzgünüm, şu anda müsait değil."}]},
 {"type": "grammar", "title": "Present Continuous", "titleTr": "Şimdiki zaman: şu an olanlar",
  "rule": "Konuşma anında olan işler için *am / is / are + V-ing* kullanılır.",
  "examples": [
   {"en": "I *am calling* about the delivery.", "tr": "Gönderi hakkında arıyorum."},
   {"en": "She *is talking* on the phone now.", "tr": "O şimdi telefonda konuşuyor."},
   {"en": "They *aren't answering* the phone.", "tr": "Telefona cevap vermiyorlar."},
   {"en": "*Are* you *listening* to me?", "tr": "Beni dinliyor musun?"}]},
 {"type": "dialogue", "title": "A Phone Call", "titleTr": "Bir telefon görüşmesi",
  "dialogues": [
   {"lines": [{"who": "Operator", "text": "Good morning, customer service. How can I help you?"},
              {"who": "Ayşe", "text": "Hello, I'm calling about my order."}]},
   {"lines": [{"who": "Operator", "text": "Could you give me your order number?"},
              {"who": "Ayşe", "text": "Sure, it's 4517."}]},
   {"lines": [{"who": "Operator", "text": "Hold on, please. I'll check it for you."},
              {"who": "Ayşe", "text": "Thank you very much."}]}]},
],
5: [
 {"type": "grammar", "title": "Asking for Help", "titleTr": "Yardım isteme",
  "rule": "İnternette veya bilgisayarda yardım isterken *Can you ...?*, *Could you ...?*, *Shall I ...?* kullanılır.",
  "chips": ["Can you ...?", "Could you ...?", "Shall I ...?", "Would you mind ...?"],
  "examples": [
   {"en": "*Can you* help me download this file?", "tr": "Bu dosyayı indirmeme yardım eder misin?"},
   {"en": "*Could you* show me how to log in?", "tr": "Nasıl giriş yapacağımı gösterir misin?"},
   {"en": "*Shall I* send you the link?", "tr": "Sana bağlantıyı göndereyim mi?"},
   {"en": "*Would you mind* checking my e-mail?", "tr": "E-postama bakar mısın?"}]},
 {"type": "grammar", "title": "Giving Instructions", "titleTr": "Yönerge verme",
  "rule": "Bilgisayar yönergelerinde emir cümleleri kullanılır: *click, type, open, save, download*.",
  "chips": ["click on", "type", "open", "save", "download", "log in"],
  "examples": [
   {"en": "*Click on* the download button.", "tr": "İndir düğmesine tıkla."},
   {"en": "*Type* your username and password.", "tr": "Kullanıcı adını ve şifreni yaz."},
   {"en": "*Save* the file to your desktop.", "tr": "Dosyayı masaüstüne kaydet."},
   {"en": "*Don't* share your password with anyone.", "tr": "Şifreni kimseyle paylaşma."}]},
 {"type": "compare", "title": "Internet Safety", "titleTr": "İnternet güvenliği: yapılması ve yapılmaması gerekenler",
  "columns": [
   {"title": "DO ✅", "tone": "good", "examples": [
    {"en": "You *should* use a strong password.", "tr": "Güçlü bir şifre kullanmalısın."},
    {"en": "You *should* log out on public computers.", "tr": "Ortak bilgisayarlarda çıkış yapmalısın."},
    {"en": "You *should* tell an adult about strange messages.", "tr": "Garip mesajları bir yetişkine söylemelisin."}]},
   {"title": "DON'T ⛔", "tone": "bad", "examples": [
    {"en": "You *shouldn't* accept friend requests from strangers.", "tr": "Yabancılardan arkadaşlık isteği kabul etmemelisin."},
    {"en": "You *shouldn't* share personal information.", "tr": "Kişisel bilgilerini paylaşmamalısın."},
    {"en": "You *mustn't* click on suspicious links.", "tr": "Şüpheli bağlantılara tıklamamalısın."}]}]},
],
6: [
 {"type": "compare", "title": "should / shouldn't", "titleTr": "Tavsiye verme",
  "rule": "Tavsiye verirken *should*, uyarırken *shouldn't* kullanırız.",
  "columns": [
   {"title": "should ✅", "tone": "good", "examples": [
    {"en": "You *should* wear a helmet.", "tr": "Kask takmalısın."},
    {"en": "You *should* check the weather first.", "tr": "Önce hava durumunu kontrol etmelisin."},
    {"en": "Beginners *should* go with a guide.", "tr": "Yeni başlayanlar rehberle gitmeli."}]},
   {"title": "shouldn't ⛔", "tone": "bad", "examples": [
    {"en": "You *shouldn't* climb alone.", "tr": "Yalnız tırmanmamalısın."},
    {"en": "You *shouldn't* forget your equipment.", "tr": "Ekipmanını unutmamalısın."},
    {"en": "You *shouldn't* swim in a rough sea.", "tr": "Dalgalı denizde yüzmemelisin."}]}]},
 {"type": "grammar", "title": "must / mustn't", "titleTr": "Zorunluluk ve yasak",
  "rule": "Kural ve zorunluluk için *must*, yasak için *mustn't* kullanılır. *should* tavsiyedir, *must* daha güçlüdür.",
  "examples": [
   {"en": "You *must* follow the safety rules.", "tr": "Güvenlik kurallarına uymalısın."},
   {"en": "Divers *must* have a licence.", "tr": "Dalgıçların lisansı olmalı."},
   {"en": "You *mustn't* go rafting without a life jacket.", "tr": "Can yeleği olmadan raftinge gitmemelisin."},
   {"en": "We *mustn't* leave rubbish in nature.", "tr": "Doğaya çöp bırakmamalıyız."}]},
 {"type": "grammar", "title": "Comparing Adventures", "titleTr": "Karşılaştırma",
  "rule": "İki etkinliği karşılaştırırken *more ... than*, en üstünü söylerken *the most ...* kullanılır.",
  "examples": [
   {"en": "Rafting is *more exciting than* hiking.", "tr": "Rafting, doğa yürüyüşünden daha heyecan vericidir."},
   {"en": "Paragliding is *the most thrilling* sport for me.", "tr": "Yamaç paraşütü benim için en heyecan verici spordur."},
   {"en": "Climbing is *harder than* cycling.", "tr": "Tırmanmak, bisiklet sürmekten daha zordur."},
   {"en": "Scuba diving is *the most dangerous* of all.", "tr": "Tüplü dalış hepsinin arasında en tehlikelisidir."}]},
],
7: [
 {"type": "grammar", "title": "Simple Past — Regular", "titleTr": "Geçmiş zaman: düzenli fiiller",
  "rule": "Geçmişte biten işler için fiile *-ed* eklenir. Olumsuz ve soruda *didn't / did* kullanılır, fiil yalın kalır.",
  "chips": ["visited", "travelled", "stayed", "enjoyed"],
  "examples": [
   {"en": "We *visited* Cappadocia last summer.", "tr": "Geçen yaz Kapadokya'yı ziyaret ettik."},
   {"en": "They *stayed* at a lovely hotel.", "tr": "Güzel bir otelde kaldılar."},
   {"en": "I *didn't* like the food there.", "tr": "Oradaki yemekleri sevmedim."},
   {"en": "*Did* you *enjoy* the tour? — Yes, I did.", "tr": "Turdan keyif aldın mı? — Evet."}]},
 {"type": "grammar", "title": "Simple Past — Irregular", "titleTr": "Geçmiş zaman: düzensiz fiiller",
  "rule": "Bazı fiiller *-ed* almaz, ikinci hâlleri ezberlenir.",
  "chips": ["go → went", "see → saw", "take → took", "eat → ate", "buy → bought"],
  "examples": [
   {"en": "We *went* to Antalya by plane.", "tr": "Antalya'ya uçakla gittik."},
   {"en": "I *saw* the ancient theatre.", "tr": "Antik tiyatroyu gördüm."},
   {"en": "She *took* a lot of photographs.", "tr": "Bir sürü fotoğraf çekti."},
   {"en": "We *ate* delicious local food.", "tr": "Nefis yöresel yemekler yedik."}]},
 {"type": "dialogue", "title": "Talking about a Holiday", "titleTr": "Tatili anlatma",
  "dialogues": [
   {"lines": [{"who": "Deniz", "text": "Where did you go last summer?"},
              {"who": "Efe", "text": "I went to Bodrum with my family."}]},
   {"lines": [{"who": "Deniz", "text": "What did you do there?"},
              {"who": "Efe", "text": "We swam every day and visited the castle."}]},
   {"lines": [{"who": "Deniz", "text": "How was the weather?"},
              {"who": "Efe", "text": "It was sunny and really hot."}]}]},
],
8: [
 {"type": "grammar", "title": "have to / has to", "titleTr": "Sorumluluklar",
  "rule": "Yapmak zorunda olduğumuz işler için *have to*, He/She/It için *has to* kullanılır. Zorunlu olmadığında *don't have to*.",
  "examples": [
   {"en": "I *have to* tidy my room every weekend.", "tr": "Her hafta sonu odamı toplamak zorundayım."},
   {"en": "He *has to* walk the dog after school.", "tr": "Okuldan sonra köpeği gezdirmek zorunda."},
   {"en": "We *don't have to* do the dishes today.", "tr": "Bugün bulaşık yıkamak zorunda değiliz."},
   {"en": "*Do* you *have to* help your mother?", "tr": "Annene yardım etmek zorunda mısın?"}]},
 {"type": "grammar", "title": "Asking for Help", "titleTr": "Yardım isteme ve teklif etme",
  "rule": "Kibar rica için *Could you ...?* ve *Would you mind + V-ing?*, yardım teklifi için *Shall I ...?* kullanılır.",
  "chips": ["Could you ...?", "Would you mind ...?", "Shall I ...?", "Can you give me a hand?"],
  "examples": [
   {"en": "*Could you* help me with the laundry?", "tr": "Çamaşırlarda bana yardım eder misin?"},
   {"en": "*Would you mind* taking out the rubbish?", "tr": "Çöpü çıkarır mısın?"},
   {"en": "*Shall I* set the table?", "tr": "Masayı ben mi kurayım?"},
   {"en": "Can you *give me a hand* in the kitchen?", "tr": "Mutfakta bana el atar mısın?"}]},
 {"type": "compare", "title": "Accepting & Refusing Requests", "titleTr": "Ricayı kabul etme ve reddetme",
  "columns": [
   {"title": "ACCEPT ✅", "tone": "good", "examples": [
    {"en": "*Sure*, no problem.", "tr": "Tabii, sorun değil."},
    {"en": "*Of course*, I'll do it now.", "tr": "Elbette, şimdi yaparım."},
    {"en": "*All right*, I'm coming.", "tr": "Peki, geliyorum."}]},
   {"title": "REFUSE ⛔", "tone": "bad", "examples": [
    {"en": "*Sorry*, I'm busy at the moment.", "tr": "Üzgünüm, şu anda meşgulüm."},
    {"en": "*I'm afraid* I can't right now.", "tr": "Korkarım şu an yapamam."},
    {"en": "*Not now*, I have to finish my homework.", "tr": "Şimdi olmaz, ödevimi bitirmem gerek."}]}]},
],
9: [
 {"type": "grammar", "title": "Passive Voice — Present", "titleTr": "Edilgen çatı: geniş zaman",
  "rule": "İşi kimin yaptığı önemli değilse edilgen kullanılır: *am / is / are + V3*.",
  "examples": [
   {"en": "Experiments *are done* in the laboratory.", "tr": "Deneyler laboratuvarda yapılır."},
   {"en": "This machine *is used* by scientists.", "tr": "Bu makine bilim insanları tarafından kullanılır."},
   {"en": "New medicines *are developed* every year.", "tr": "Her yıl yeni ilaçlar geliştirilir."},
   {"en": "The results *are written* in a report.", "tr": "Sonuçlar bir rapora yazılır."}]},
 {"type": "grammar", "title": "Passive Voice — Past", "titleTr": "Edilgen çatı: geçmiş zaman",
  "rule": "Geçmişte yapılan işler için *was / were + V3*. Yapan kişi *by* ile belirtilir.",
  "chips": ["was invented", "was discovered", "were built", "was written"],
  "examples": [
   {"en": "The telephone *was invented* by Alexander Graham Bell.", "tr": "Telefon, Alexander Graham Bell tarafından icat edildi."},
   {"en": "Penicillin *was discovered* in 1928.", "tr": "Penisilin 1928'de keşfedildi."},
   {"en": "The pyramids *were built* thousands of years ago.", "tr": "Piramitler binlerce yıl önce inşa edildi."},
   {"en": "This book *was written* by a Turkish scientist.", "tr": "Bu kitap bir Türk bilim insanı tarafından yazıldı."}]},
 {"type": "dialogue", "title": "Inventions", "titleTr": "İcatlar hakkında konuşma",
  "dialogues": [
   {"lines": [{"who": "Zeynep", "text": "Who was the light bulb invented by?"},
              {"who": "Berk", "text": "It was invented by Thomas Edison."}]},
   {"lines": [{"who": "Zeynep", "text": "When was the first computer built?"},
              {"who": "Berk", "text": "It was built in the 1940s."}]},
   {"lines": [{"who": "Zeynep", "text": "What is graphene used for?"},
              {"who": "Berk", "text": "It is used in electronics and medicine."}]}]},
],
10: [
 {"type": "grammar", "title": "Predictions with will", "titleTr": "Gelecek tahminleri",
  "rule": "Gelecekle ilgili tahminlerde *will* kullanılır. Emin değilsek *may / might* deriz.",
  "chips": ["will", "won't", "may", "might"],
  "examples": [
   {"en": "There *will* be a storm tomorrow.", "tr": "Yarın fırtına olacak."},
   {"en": "The river *won't* flood this year.", "tr": "Nehir bu yıl taşmayacak."},
   {"en": "It *might* snow in the mountains.", "tr": "Dağlarda kar yağabilir."},
   {"en": "Scientists *may* predict earthquakes one day.", "tr": "Bilim insanları bir gün depremleri tahmin edebilir."}]},
 {"type": "grammar", "title": "If Clauses (Type 1)", "titleTr": "Koşul cümleleri",
  "rule": "Gerçekleşmesi mümkün durumlar için *If + geniş zaman, will + fiil* yapısı kullanılır.",
  "examples": [
   {"en": "*If* it rains, the streets *will* flood.", "tr": "Yağmur yağarsa sokaklar su altında kalır."},
   {"en": "*If* an earthquake happens, we *will* go outside.", "tr": "Deprem olursa dışarı çıkacağız."},
   {"en": "*If* you stay calm, you *will* be safer.", "tr": "Sakin kalırsan daha güvende olursun."},
   {"en": "The soil *will* dry *if* it doesn't rain.", "tr": "Yağmur yağmazsa toprak kurur."}]},
 {"type": "grammar", "title": "Giving Advice in a Disaster", "titleTr": "Afetlerde tavsiye",
  "rule": "Afet anındaki davranışlar için *should / shouldn't* ve emir cümleleri kullanılır.",
  "examples": [
   {"en": "You *should* keep an emergency bag ready.", "tr": "Hazır bir afet çantası bulundurmalısın."},
   {"en": "You *shouldn't* use the lift during an earthquake.", "tr": "Deprem sırasında asansörü kullanmamalısın."},
   {"en": "*Stay away* from windows.", "tr": "Pencerelerden uzak dur."},
   {"en": "*Don't panic* and follow the instructions.", "tr": "Panik yapma ve talimatlara uy."}]},
],
}

# Unit 10's activity bank has no usable word pairs, so its list is written here.
EXTRA_WORDS = {
10: [("earthquake", "deprem"), ("flood", "sel"), ("storm", "fırtına"), ("hurricane", "kasırga"),
     ("tornado", "hortum"), ("avalanche", "çığ"), ("landslide", "toprak kayması"),
     ("drought", "kuraklık"), ("volcano", "yanardağ"), ("eruption", "patlama"),
     ("wildfire", "orman yangını"), ("lightning", "şimşek"), ("thunder", "gök gürültüsü"),
     ("tsunami", "tsunami"), ("damage", "hasar"), ("rescue team", "kurtarma ekibi"),
     ("emergency", "acil durum"), ("shelter", "sığınak"), ("survivor", "hayatta kalan"),
     ("warning", "uyarı"), ("aftershock", "artçı sarsıntı"), ("debris", "enkaz"),
     ("first aid", "ilk yardım"), ("evacuate", "tahliye etmek")],
}

BAD_EN = re.compile(r"[0-9?\"]|^\s*$")


def clean_tr(text):
    text = re.sub(r"^\s*\d+\.\s*", "", text or "")     # "1. baharat katmak" -> "baharat katmak"
    text = re.split(r"\s+\d+\.\s+", text)[0]           # drop the second sense
    text = text.split(";")[0].strip(" ,.")
    if len(text) > 22 and "," in text:      # keep only the first sense
        text = text.split(",")[0].strip()
    return text.strip()


def words_of(unit, limit):
    path = os.path.join(CONTENT, "g8", "u%d" % unit, "games", "bank.json")
    pairs = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            bank = json.load(f)
        for w in bank.get("words", []):
            en, tr = (w.get("en") or "").strip(), clean_tr(w.get("tr"))
            if not en or not tr or BAD_EN.search(en) or len(en) > 26 or len(tr) > 34:
                continue
            pairs.append((en, tr))
    pairs += EXTRA_WORDS.get(unit, [])

    seen, out = set(), []
    for en, tr in pairs:
        k = en.lower()
        if k in seen or k == tr.lower():
            continue
        seen.add(k)
        out.append({"en": en, "tr": tr})
        if len(out) >= limit:
            break
    return out


def build(unit, limit):
    theme = THEMES[8][unit]
    slides = [{
        "type": "title", "kicker": "UNIT %d" % unit,
        "title": theme[0], "titleTr": theme[1], "emoji": theme[2],
    }]

    # 1) the book's own glossary, section by section
    book = book_sections(unit)
    known = set()
    for title, title_tr, items in book:
        slides.append({
            "type": "vocab", "title": title, "titleTr": title_tr, "items": items,
        })
        known.update(i["en"].lower() for i in items)
    n_book = sum(len(i) for _, _, i in book)

    # 2) anything else the unit's activities use, after the book words
    extra = [w for w in words_of(unit, limit) if w["en"].lower() not in known]
    for n in range(0, len(extra), 12):
        slides.append({
            "type": "vocab",
            "title": "More Words %d" % (n // 12 + 1) if len(extra) > 12 else "More Words",
            "titleTr": "%s — ek kelimeler" % theme[1],
            "items": extra[n:n + 12],
        })

    slides += [json.loads(json.dumps(s)) for s in GRAMMAR.get(unit, [])]

    quiz = [i for _, _, items in book for i in items][:7]
    if quiz:
        slides.append({
            "type": "practice", "title": "Quick Practice",
            "titleTr": "Hızlı tekrar — cevabı görmek için tıkla",
            "items": [{"q": "%s → ?" % w["tr"], "a": w["en"]} for w in quiz],
        })
    slides.append({
        "type": "end", "emoji": "🎯", "title": "Well done!",
        "titleTr": "Şimdi oyunlarla pekiştirelim.",
    })

    data = {
        "title": theme[0], "titleTr": theme[1], "emoji": theme[2],
        "accent": ACCENTS[unit], "pages": [], "slides": slides,
        "source": "res/book_8.pdf",
    }
    dest = os.path.join(CONTENT, "g8", "u%d" % unit, "presentation")
    ensure(dest)
    with open(os.path.join(dest, "slides.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("  u%-2d %2d slayt  (kitap %d + ek %d kelime)"
          % (unit, len(slides), n_book, len(extra)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", type=int)
    ap.add_argument("--words", type=int, default=60, help="unite basina kelime siniri")
    args = ap.parse_args()
    for u in ([args.unit] if args.unit else range(1, 11)):
        build(u, args.words)


if __name__ == "__main__":
    main()
