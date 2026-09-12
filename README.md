# ENG HUB

Taşınabilir İngilizce ders yardımcısı. USB'ye kopyala, tak, çalıştır — **kurulum yok.** Sunumlar, oyunlar ve özgün 6. sınıf çalışma kâğıtları çevrimdışı; dış kaynak belge bağlantıları ve kitap sunumları internet ister.
Windows ve Pardus/Linux üzerinde aynı şekilde çalışır.

```
ANA MENÜ → 5 / 6. Sınıf (Revizyon + 1…8. Tema) · 7 / 8. Sınıf (1…10. Ünite) → SUNUM · OYUNLAR · ÇALIŞMA KÂĞITLARI · KİTAP SUNUMLARI
```

## Çalıştırma

| Sistem | Ne yapmalı |
| --- | --- |
| Windows | `Start-Windows.bat` dosyasına çift tıklayın |
| Pardus / Linux | `start-pardus.sh` dosyasına çift tıklayın (veya terminalde `./start-pardus.sh`) |

Tarayıcı kendiliğinden açılır. Kapatmak için siyah konsol penceresini kapatın.

**Python:** Windows'ta USB'deki taşınabilir Python (`runtime/python-win/`) kullanılır — bilgisayara
hiçbir şey kurulmaz, yönetici yetkisi gerekmez. Pardus'ta sistemdeki `python3` kullanılır (Pardus'ta
hazır gelir). Hiçbiri yoksa açılış ekranı kurulumu adım adım anlatır.

## İçeride ne var

| Bölüm | İçerik |
| --- | --- |
| **Sunum** | **5. sınıf** 1–8. tema (303 slayt) ve **8. sınıf** 1–10. ünite (227 slayt) için animasyonlu ders sunumu — sesli 1115 büyük görsel kelime kartı, doğru akrep/yelkovanlı saat örnekleri, İngilizce–Türkçe eşlenmiş vurgular, 168 kısa etkinlik molası ve ünite başına 3 büyük final görevi (54 sayfa: resim sürükleme, çevrimdışı ses ve cümle kurma). 5. sınıf sunumlarının sonunda orijinal MEB tema föyünün sayfaları da var. |
| **Oyunlar** | 10 çevrimdışı oyun modu: Sharpshooter, Balon Patlat, Köstebek Avı, Uzay Koşusu, Hızlı Test, Eşleştirme, Kelime Avı, Karışık Harfler, Kule, Kelime Kartları. 15.000+ soru ve 3.000+ kelime çifti, ünite ünite ayrılmış. Ayrıca kaynaktaki 66 statik etkinliğin çevrimdışı kopyası. |
| **Çalışma Kâğıtları** | 6. sınıfta **18 özgün çalışma kâğıdı + 9 ayrı öğretmen anahtarı**, toplam 54 PDF sayfası çevrimdışı açılır ve yazdırılır. Dışarıdan derlenen belgeler kaynak bağlantısından açılır; onlar için internet gerekir. |
| **Kitap Sunumları** | Kaynaktaki ders/çalışma kitabı sunumlarının listesi. Bunlar yüzlerce parçadan oluşan slayt oynatıcıları olduğu için USB'ye kopyalanmıyor; **bağlantı olarak** açılır (internet gerekir). |

İnternet isteyen etkinlikler (Wordwall, Vocablitz, Baamboozle vb.) ayrı bir listede "İnternet gerekli"
başlığıyla durur — bağlantı varsa tek tıkla açılır.

### Sunum nasıl çalışır

* İçerik **tek tek açılır**: her "Sonraki" bir kelime/örnek daha gösterir, hepsi bitince sonraki
  slayda geçer. `↓` tuşu o slaydın kalanını bir anda açar.
* Slayt önce **ekrana göre yeniden düzenlenir**, sonra okunabilirlik sınırına kadar küçültülür;
  hâlâ sığmıyorsa yazıyı minik yapmak yerine kaydırılır ve her slayt başa sarar.
* Her öğretim bölümünün arkasından tek bir **Activity Break** gelir: eşleştirme, resimli soru,
  doğru/yanlış, cevabı açma, çoktan seçmeli, boşluk doldurma, cümle sıralama veya diyalog rolü.
  Görevler doğrudan bir önceki bölümün kendi kelime, örnek ve konuşmalarından üretilir.
* Her ünitenin sonunda ayrıca üç büyük **Unit Mission** vardır: resimleri doğru kelime alanına
  sürükleme, sesi dinleyip doğru resmi bulma ve kelimeleri sürükleyerek cümle kurma. Fare,
  dokunmatik ekran ve tıklayarak seçme yöntemlerinin üçü de desteklenir.
* Konu sırası **ders kitabına** göredir (`res/book.pdf` tema tablosu); kitapta olmayan konular çıkarıldı.
* Her kelime kartında görsel vardır. Mümkün olan yerde gerçek resim kullanılır: 5. sınıfta **tema
  föyünün kendi görselleri**, 8. sınıfta **Wikimedia Commons** fotoğrafları; fotoğrafın açıkça
  anlatmadığı soyut kelimelerde ise anlamı belirgin bir piktogram veya sayı kartı gösterilir.
* Ünite kapağı, yeni ve tahminî eşleme yapmak yerine o ünitede zaten kontrol edilmiş üç kelime
  görselini kullanır.
* Diyaloglar **konuşma balonu** olarak gösterilir.
* Başlıklar ve kapak sayfası **tek seferde** görünür; sadece içerik adım adım açılır.
* Üstteki **adım çubuğu** o slaytta kaç parça kaldığını gösterir.
* Kelime ve etkinlik ızgaraları projektör boyutuna göre sütun değiştirir; etkinlik slaytları
  okunamayacak kadar küçülmez (en az %82), gerekirse kayar.
* Bayraklar emoji değil **SVG resim** (Windows'ta emoji bayrak görünmüyor).
* Her gramer örneğinin yanında cümleyi anlatan **bağlamsal bir görsel** çıkar; alıştırmalarda
  **resimli soru** vardır. Her kelime kartındaki 🔊 düğmesi paketlenmiş çevrimdışı kaydı oynatır.
* Kalabalık kelime sayfaları bölünür (en fazla 8 büyük kart); etkinlik molalarında en fazla 2 görev olur.
* Etkinlik yönergeleri **İngilizce** (Match the words, True or false?, Reveal answer, Try again …).

### Kalem araçları (🖊️ düğmesi veya `M`)

Kitap sunumlarındaki "Marker Tools" gibi: **Pen**, **Highlighter** (yassı uçlu, açık renk),
**Eraser**, **Erase All** (o slayttaki her şeyi sil), **End Drawing** (çizimi bırak).
Pen ve Highlighter'ın altında **5'er renk** var; renge tıklamak o aracı da seçer.
Çizimler slayt başına saklanır — ileri gidip geri dönünce yazdıkların yerinde durur.

### Slayt düzenleme (✏️ düğmesi veya `E`)

| Düğme | Ne yapar |
| --- | --- |
| 🖼️ Resim | Bilgisayardan resim seçer, USB'ye kopyalar, slayda ekler |
| 🅰️ Yazı | Serbest yazı kutusu ekler |
| ▭ ⬭ △ 💬 | Dikdörtgen, daire, üçgen, konuşma balonu ekler |
| ✎ Metin / 🎨 Renk | Seçili nesnenin yazısını / rengini değiştirir |
| 🗑️ Sil | Seçili nesneyi siler (`Delete` tuşu da olur) |
| 💾 Kaydet | `slides.json` dosyasına yazar, eski hâli `.bak` olarak kalır (`Ctrl+S`) |

Nesne sürüklenerek taşınır, sağ alt köşesinden boyutlandırılır. Konumlar yüzde saklandığı için her
ekran boyutunda aynı yerde durur. Şeklin içine yazı yazmak için şekli seçip ✎ Metin'e basın.

## Kısayollar

| Tuş | İşlev |
| --- | --- |
| `←` `→` `Boşluk` | Sonraki adım / slayt |
| `↓` | Slaydın kalanını aç |
| `F` | Tam ekran |
| `E` | Düzenleme modu |
| `M` | Kalem araçları menüsü |
| `Esc` | Sunumu kapat |
| `Backspace` | Geri |
| `A` `B` `C` `D` | Hızlı Test'te şık seç |

## 8. sınıf sunumları nereden geliyor?

8. sınıf için elimizde MEB tema föyü yoktu. Sunumlar iki kaynaktan üretildi:

* **Kelimeler** — ünitenin kendi etkinlik havuzundan (`content/g8/uN/games/bank.json`) çıkarılan
  gerçek kelime çiftleri; temizlenip en fazla 8 kartlık slaytlara bölündü.
* **Gramer** — MEB 8. sınıf müfredatının o ünitede öğrettiği yapılar, `tools/build_g8.py` içinde
  yazılı. Örnek cümlelerdeki `*yıldızlı*` kelimeler alıştırmaları otomatik üretir.

Değiştirmek için `tools/build_g8.py` içindeki `GRAMMAR` tablosunu düzenleyip şunu çalıştırın:

```bash
python tools/build_g8.py && python tools/link_word_images.py && python tools/polish_slides.py --grade 8
powershell -ExecutionPolicy Bypass -File tools/build_mission_audio.ps1
```

## 6. sınıf: 2026 MEB kitaplarına göre özgün materyaller

Revizyon 1-2 ve sekiz tema için dokuz ders sunumu (681 slayt), 288 kelime kaydı ve
714 özgün oyun sorusu vardır. On oyun modu da her bölümde kullanılabilir. Sunumlar
küçük kelime grupları, Türkçe açıklamalı dil yapıları, özgün diyaloglar ve okumalar,
etkileşimli alıştırmalar, resim eşleştirme, dinleme ve cümle kurma görevleri içerir.
280 kelime kartının tamamında görsel, sekiz sayı kartında büyük rakamlar bulunur.
Her konu içinde resim soruları, dinleme/eşleştirme, kısa dil bilgisi örnekleri,
cümle kurma ve eşli konuşma dönüşümlü ilerler. Dil bilgisi örnekleri de görseldir.
Kelime görselleri ve telaffuzları çevrimdışıdır. Soyut anlamlara kısa bağlam ipuçları eklenir.

Her bölümde iki özgün çalışma kâğıdı ve ayrı öğretmen anahtarı bulunur. Anahtarda
cevaplar, yanlış ifadelerin düzeltmeleri, öğretmenin okuyacağı dinleme metni,
örnek yazma cevabı ve kısa değerlendirme ölçütleri vardır.

Kaynaklar: MEB English 6 Student's Book ve Workbook (2026). Kitaplar yalnızca
müfredat kapsamı için okunur; kitap alıştırmaları veya sayfaları bu materyallere
kopyalanmaz. Tema-sayfa eşleştirmesi ve kaynak dosya doğrulamaları
`content/g6/curriculum.json` içindedir. Özgün metinler `tools/grade6_content.py`,
üretici `tools/create_grade6.py` içindedir. Üretim için ReportLab ve pypdf gerekir;
`G6_FONT_DIR` Arial yazı tiplerinin klasörünü değiştirebilir. Yalnızca 6. sınıf
içeriği ve katalogdaki 6. sınıf kayıtları güncellenir. Uygulama derlenmez.

Yalnızca dersleri yenilemek için `python tools/create_grade6.py --slides-only` kullanılır;
çalışma kâğıtları ve oyun havuzları korunur. Konu sırası `tools/grade6_pacing.py`,
incelenmiş görsel seçimleri ve atıflar `tools/grade6-image-choices.json` içindedir.
Eksik seçili görselleri `python tools/prepare_grade6_visuals.py` indirir.

Bakım komutları özgün 6. sınıf oyun havuzlarını ve PDF'lerini korur. Dış kaynaktan
indirilen eski çalışma kâğıtları yine yerelde tutulmaz. Lite pakette çalışma kâğıtları
ve oyunlar bulunmadığından bu içerik için tam paket veya depo kullanılır.

## 7. sınıfa sunum eklemek

Bu sınıfta oyunlar, çalışma kâğıtları ve çevrimdışı kopyalar var; **sunum yok**. Eklemek için:

1. PDF'i `res/<N>th grade/unit <M>/` klasörüne koyun (örn. `res/6th grade/unit 3/`).
2. `python tools/pdf_to_pages.py` — sayfaları görsele çevirir.
3. `content/g<N>/u<M>/presentation/slides.json` dosyasını oluşturun.
   Şablon olarak `content/g5/u1/presentation/slides.json` dosyasını kopyalayın.
4. `python tools/fetch_catalog.py` — menü kendini günceller.

Kaynak PDF yoksa 8. sınıftaki gibi kelime havuzundan üretme yolunu izleyebilirsiniz:
`tools/build_g8.py` dosyasını örnek alın.

`slides.json` slayt tipleri: `title`, `vocab`, `grammar`, `compare`, `dialogue`, `practice`,
`exercise`, `mission`, `scene`, `pages`, `end`. İngilizce örnekte `*yıldız*` arasına aldığınız
kısım renkli vurgulanır; `polish_slides.py` karşılık gelen Türkçe ifadeyi `trEm` alanına ekler.

## Klasörler

```
Start-Windows.bat / start-pardus.sh   başlatıcılar
server/enghub.py                      yerel sunucu (yalnız 127.0.0.1)
runtime/python-win/                   taşınabilir Python (Windows yedeği)
app/                                  arayüz (HTML/CSS/JS)
content/g5/u1/…                       ünite içerikleri
  presentation/  games/  worksheets/  sites/
res/                                  orijinal PDF'ler (kaynak)
tools/                                içerik üretme betikleri
```

## Bakım (internet gerekir)

```bash
python tools/refresh.py
```

Katalog, oyun soruları, çalışma kâğıdı bağlantıları, ek belge bağlantıları ve statik oyun kopyaları
kaynaktan yeniden alınır. Sunum slaytları yeniden üretilmez; yerel derleme yapılmaz.
Bağlantılar kontrol edilir; sonuçlar `app/data/source-audit.json` dosyasına tarihli yazılır.
Erişilemeyen kaynaklarda çalışan yerel dosya korunur. `--full` eski komutlarla uyum için kabul edilir.
Sonunda `verify_content.py` dosyaları kontrol eder. Tek tek çalıştırmak isterseniz:

| Betik | İşi |
| --- | --- |
| `tools/fetch_catalog.py` | menüyü ve sayıları günceller |
| `tools/pdf_to_pages.py` | `res/` içindeki PDF'leri sayfa görsellerine çevirir |
| `tools/fetch_games.py` | ünite soru havuzlarını indirir |
| `tools/fetch_worksheets.py` | çalışma kâğıtlarını çevrimiçi bağlantı olarak günceller; yerel kopyaları kaldırır |
| `tools/mirror_sites.py` | statik etkinliklerin çevrimdışı kopyasını alır (`--presentations` ile kitap sunumları da, çok yavaş) |
| `tools/crop_vocab.py` | tema föyündeki resimleri tek tek kesip çıkarır (`--sheet` ile kontrol görseli) |
| `tools/link_images.py` | kesilen resimleri kelime kartlarına bağlar (eşleme tablosu dosyanın içinde) |
| `tools/polish_slides.py` | kelime sayfalarını büyütüp böler; doğru saatleri, iki dilli vurguları, kısa molaları ve üç ünite final görevini üretir |
| `tools/build_mission_audio.ps1` | bütün kelime kartları ve final dinleme görevleri için çevrimdışı WAV dosyaları üretir |
| `tools/build_vocab_illustrations.py` | boy, kilo, yüz şekli, uzunluk, durum ve kaşık boyutu gibi karşılaştırmalar için açık SVG çizimleri üretir |
| `tools/fetch_reviewed_vocab_images.py` | yalnız elle denetlenmiş Commons dosyalarını indirir; kaynak/lisans bilgisi görsellerin yanındadır |
| `tools/contact_grade5_images.py` | 5. sınıf kaynak görsellerini etiketli kontrol sayfalarında gösterir |
| `tools/contact_word_images.py` | 8. sınıf kelime fotoğraflarını gözle denetlemek için etiketli kontrol sayfaları üretir |
| `tools/fetch_flags.py` | ülke bayraklarını SVG olarak indirir ve kartlara bağlar |
| `tools/build_g8.py` | 8. sınıf sunumlarını kelime havuzu + müfredat yapılarından üretir |
| `tools/verify_content.py` | eksik dosya var mı diye bakar |
| `tools/verify_lessons.py` | büyük kelime sayfalarını, tüm görselleri, saatleri, iki dilli vurguları, final görevlerini, sesleri ve dil düzeltmelerini doğrular |
| `tools/get_python_win.py` | USB'ye taşınabilir Python koyar |

Gerekli tek harici paket: `pymupdf` (yalnız `pdf_to_pages.py` için) — `pip install pymupdf`.

## Kaynak ve emek

Ders materyalleri [eltarena.com](https://eltarena.com) üzerinde paylaşılan öğretmen çalışmalarından
derlenmiştir. Hazırlayanların adları her çalışma kâğıdının ve etkinliğin yanında korunur.
5. sınıf tema föyleri MEB Maarif Modeli içeriğidir. Bu USB sınıf içi kullanım içindir.

## Hazır paket (kurulum gerektirmez)

En kolay yol: [Releases](https://github.com/ctnkyaumt/eng-hub/releases) sayfasından zip'i indirin,
USB'ye çıkarın, başlatıcıya çift tıklayın.

| Dosya | İçerik |
| --- | --- |
| `eng-hub-vX.Y.Z.zip` | Tam paket — sunumlar, oyunlar, çalışma kâğıtları, çevrimdışı etkinlikler |
| `eng-hub-vX.Y.Z-lite.zip` | Sadece program ve sunumlar (çok daha küçük) |
| `book.pdf`, `book_8.pdf` | Ders kitapları — programın çalışması için gerekmez, içeriği yeniden üretmek isteyenler için |

Paketin yapısı:

```
eng-hub/
├─ Start-Windows.bat
├─ start-pardus.sh
├─ README.md      ← ilk kullanım kılavuzu
└─ src/           ← program ve içerik
```

Yeni sürüm yayınlamak için `v1.2.3` gibi bir etiket gönderin; `.github/workflows/release.yml`
paketi hazırlar, paketlenmiş sunucuyu ayağa kaldırıp çalıştığını doğrular ve zip'leri yükler.

## Depo hakkında

Depoda **her şey** var: program, sunumlar, çalışma kâğıdı bağlantıları, oyun soru havuzları,
kopyalanan etkinlikler ve resimler. MEB kitapları ile eltarena'da paylaşılan çalışmalar zaten
herkese açık; bu proje onları tek yerde, internetsiz kullanılabilir hâlde topluyor ve her dosyanın
yanında hazırlayanın adı duruyor.

GitHub 100 MB üstü dosya kabul etmediği için yalnızca iki ders kitabı PDF'i depoda değil — onlar Releases sayfasında. İçeriği kaynaktan yeniden üretmek için:

```bash
python tools/refresh.py
```

Proje notları ortak `C:\Users\user\Desktop\code\0.MEMORIES\eng-hub.md` dosyasında tutulur.

### Revizyon (5. ve 6. Sınıf)

5. ve 6. sınıfta Maarif Modeli müfredatında yer alan Revizyon bölümü eklenmiştir:
- **5. Sınıf Revizyon:** 20 etkinlik soru havuzu (Jeopardy, Kule, Bilgi Çarkı), 56 çevrimiçi oyun bağlantısı, 10 çalışma kâğıdı bağlantısı ve 11 kitap/çalışma sunumu bağlantısı içerir.
- **6. Sınıf Revizyon:** Kitabın iki revizyon bölümüne uygun özgün çevrimdışı sunum, iki çalışma kâğıdı, öğretmen anahtarı ve yenilenmiş kelime/dil bilgisi oyun havuzu içerir. Mevcut kitap sunumu bağlantıları da açılabilir.

### Sharpshooter

38 tema/ünite ve revizyon bölümünün Oyunlar menüsünde çevrimdışı çalışır. Anlamı oku, hareket eden
baloncuktaki doğru kelimeyi fare, dokunma veya 1–4 tuşlarıyla vur. Atışın değdiği ilk
baloncuk parçacıklarla patlar; yanlış cevap iki puan ve bir can kaybettirir.
Beş can, beş dakika, en fazla 15 soru; duraklatma ve yeniden başlatma var.
Veri eksik temalar için özgün başlangıç kelimeleri paketlenmiştir.
6. sınıf 2026–2027 Maarif modelinin sekiz temasını ve revizyon bölümünü kullanır; eski on ünite
materyalleri yeni temaların menülerinde gösterilmez.
Oyun, [Cram Sharpshooter](https://www.cram.com/flashcards/7-sinif-1-unite-ozel-yayin-13019462/games/sharpshooter)
eşleştirme fikrinden esinlenen özgün bir yerel uygulamadır; Cram kodu veya görselleri kopyalanmamıştır.

Dış kaynak çalışma kâğıtları bakım komutlarıyla indirilmez. Kaynak URL ve hazırlayan
bilgisi manifestte saklanır; belgenin güncel sürümü tıklanınca kaynak siteden açılır.
Özgün 6. sınıf PDF'leri bu kuralın dışındadır ve bakım sırasında korunur.
