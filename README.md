# ENG HUB

Taşınabilir İngilizce ders yardımcısı (5, 6, 7 ve 8. sınıflar). USB'ye kopyala, tak, çalıştır — **kurulum gerektirmez.**
Çekirdek sunumlar, yerel oyunlar ve özgün 6. sınıf çalışma kâğıtları yerel olarak çalışır; zengin dış kaynak kütüphaneleri (ingilizcecin, dersingilizce, MEB ÖDSGM, Sümeyye Oğultekin oyunları ve kitap sunumları) internet bağlantısıyla tek tıkla açılır.
Windows ve Pardus/Linux üzerinde aynı şekilde çalışır.

```
ANA MENÜ → 5 / 6. Sınıf (Revizyon + 1…8. Tema) · 7 / 8. Sınıf (1…10. Ünite) → SUNUM · OYUNLAR · ÇALIŞMA KÂĞITLARI · KİTAP SUNUMLARI
```

## Çalıştırma

| Sistem | Ne yapmalı |
| --- | --- |
| **Windows** | `Start-Windows.bat` dosyasına çift tıklayın (USB'deki taşınabilir Python kullanılır, hiçbir şey kurulmaz). |
| **Pardus / Linux** | `start-pardus.sh` dosyasına çift tıklayın veya terminalde `./start-pardus.sh` çalıştırın. |

Tarayıcı otomatik olarak `http://127.0.0.1:8777` adresini açar. Kapatmak için konsol penceresini kapatmanız yeterlidir.

## İçeride Ne Var?

| Bölüm | İçerik Özeti |
| --- | --- |
| **Sunum** | **27 zengin ders:** 5. sınıf (8 tema), 6. sınıf (revizyon + 8 tema) ve 8. sınıf (10 ünite). Adım adım açılan görsel kelime kartları, çift dilli dil bilgisi vurguları, diyaloglar ve **330 yerel interaktif alıştırma** (hafıza, gruplama, eksik kelimeler, soru kutuları). |
| **Oyunlar** | **10 yerel oyun modu:** Sharpshooter, Balon Patlat, Köstebek Avı, Uzay Koşusu, Hızlı Test, Eşleştirme, Kelime Avı, Karışık Harfler, Kule, Kelime Kartları (15.000+ soru, 3.000+ kelime çifti). Ayrıca 38 ünitenin tümünde **sumeyyeogultekin** klasörü (443 çevrimiçi oyun ve önizlemeleri) ile zengin Wordwall oyunları. |
| **Çalışma Kâğıtları ve Testler** | • **6. Sınıf Özgün Kâğıtlar:** 18 çalışma kâğıdı + 9 öğretmen anahtarı (toplam 54 sayfa yerel PDF).<br>• **ingilizcecin:** 2020 sonrası 469 güncel çalışma kâğıdı ve test (özel arama filtreli klasör).<br>• **dersingilizce:** 154 PDF çalışma kâğıdı (özel klasör).<br>• **MEB ÖDSGM:** Sadece 7 ve 8. sınıflar için 50 resmi Beceri Temelli Test, Kazanım Kavrama Testi ve LGS soru kitapçığı (özel klasör). |
| **Kitap Sunumları** | MEB ve yayıncıların ders ve çalışma kitaplarına ait interaktif dijital sunum bağlantıları (internet gerekir). |

## Sunum Özellikleri & Kontroller

- **Adım Adım Anlatım:** `Boşluk` veya `→` tuşlarıyla içerik adım adım açılır; `↓` o slaydın kalanını tek seferde gösterir.
- **Duyarlı Yerleşim:** Akıllı tahta ve projektör çözünürlüklerine göre otomatik ölçeklenir; taşmaları kaydırma çubuğuyla önler.
- **Kalem Araçları (`M` veya 🖊️):** Tahtaya çizim yapmak için Pen, Highlighter, Eraser ve 5 farklı renk seçeneği. Çizimler slayt bazında saklanır.
- **Slayt Düzenleme (`E` veya ✏️):** Slayda bilgisayardan görsel, metin kutusu veya şekil ekleme, boyutlandırma ve kaydetme (`Ctrl+S`).

### Kısayollar

| Tuş | İşlev | Tuş | İşlev |
| --- | --- | --- | --- |
| `→` / `Boşluk` | Sonraki adım / slayt | `F` | Tam ekran aç / kapat |
| `←` | Önceki adım / slayt | `M` | Kalem araçları menüsü |
| `↓` | Slayt içeriğini hemen aç | `E` | Slayt düzenleme modu |
| `Esc` | Sunumdan çık | `A` `B` `C` `D` | Hızlı Test'te şık seçimi |

## Müfredat & İçerik Yapısı

- **5. Sınıf:** 2026 Maarif Modeli temaları, tema föyleri kaynaklı resimli kelimeler, interaktif alıştırmalar ve revizyon bölümü.
- **6. Sınıf:** 2026 Maarif Modeli 8 tema ve revizyon için özgün hazırlanan 9 ders sunumu (681 slayt), seslendirmeler, 18 özgün çalışma kâğıdı ve öğretmen anahtarları.
- **7. Sınıf:** 10 ünite için oyun havuzları, Sharpshooter, çalışma kâğıdı klasörleri ve MEB ÖDSGM beceri temelli testleri.
- **8. Sınıf:** LGS hazırlık odaklı 10 ünite sunumu, gerçek soru havuzları, MEB ÖDSGM LGS çıkmış ve örnek soruları.

## Klasör Yapısı

```
eng-hub/
├─ Start-Windows.bat / start-pardus.sh   # Başlatıcılar
├─ server/enghub.py                      # Yerel HTTP sunucusu (127.0.0.1:8777)
├─ runtime/python-win/                   # Taşınabilir Python (Windows)
├─ app/                                  # Web arayüzü (HTML / CSS / JS)
├─ content/g5/u1/...                     # Ünite içerikleri (sunum, oyun, kâğıt)
└─ tools/                                # İçerik denetim ve yenileme betikleri
```

## Bakım ve Doğrulama

Harici kaynak bağlantılarını yenilemek veya içerik bütünlüğünü doğrulamak için (Python gereklidir):

```bash
# Tüm kaynakları ve bağlantıları denetleyip yenilemek için:
python tools/refresh.py

# İçerik ve bağlantı bütünlüğünü kontrol etmek için:
python tools/verify_content.py
python tools/probe_worksheet_sources.py
python tools/probe_game_folders.py
```

## Kaynaklar ve Teşekkür

Materyaller MEB ders kitapları, [eltarena.com](https://eltarena.com), [ingilizcecin.com](https://www.ingilizcecin.com), [dersingilizce.org](https://www.dersingilizce.org), MEB ÖDSGM ve [sumeyyeogultekin.com](https://sumeyyeogultekin.com) üzerinde paylaşılan değerli öğretmen çalışmalarından derlenmiştir. Emeği geçen tüm meslektaşlarımıza teşekkür ederiz.

