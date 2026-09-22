# ENG HUB — İlk kullanım

Taşınabilir İngilizce ders yardımcısı. **Kurulum gerektirmez, USB'den tak-çalıştır.**
Windows ve Pardus/Linux'ta aynı şekilde çalışır.

## 1. Kur (2 dakika)

1. `eng-hub.zip` dosyasını **USB belleğe** çıkarın (masaüstüne de olur).
2. Klasörün içi şöyle görünmeli:

```
eng-hub/
├─ Start-Windows.bat    ← Windows'ta buna çift tıklayın
├─ start-pardus.sh      ← Pardus/Linux'ta buna çift tıklayın
├─ README.md            ← bu dosya
└─ src/                 ← programın kendisi (dokunmayın)
```

3. Sisteminize uygun başlatıcıya çift tıklayın. Tarayıcı kendiliğinden açılır.

Kapatmak için açılan **siyah konsol penceresini** kapatın.

> **Pardus'ta çalışmıyorsa:** dosyaya sağ tık → *Özellikler* → *İzinler* →
> "Dosyanın çalıştırılmasına izin ver" işaretli olmalı. Terminalden:
> `chmod +x start-pardus.sh && ./start-pardus.sh`

## 2. Python gerekir mi?

Kendiniz kurmanıza gerek yok:

- **Windows:** paketin içindeki taşınabilir Python kullanılır. Bilgisayara hiçbir şey
  kurulmaz, yönetici yetkisi istemez.
- **Pardus/Linux:** sistemdeki `python3` kullanılır (Pardus'ta hazır gelir).

Hiçbiri bulunamazsa açılış ekranı ne yapmanız gerektiğini yazar.

## 3. İçeride ne var

```
ANA MENÜ → Sınıf (5, 6, 7, 8) / LGS Hazırlık → SUNUM · OYUNLAR · ÇALIŞMA KÂĞITLARI · KİTAP SUNUMLARI
```

| Bölüm | Ne var |
| --- | --- |
| **Sunum** | 5, 6 ve 8. sınıflar için 27 tam ünite dersi: görsel kelime kartları, çift dilli dil bilgisi vurguları ve 330 interaktif yerel alıştırma. |
| **Oyunlar** | 10 yerel oyun modu: Sharpshooter, Balon Patlat, Köstebek Avı, Uzay Koşusu, Hızlı Test, Eşleştirme, Kelime Avı, Karışık Harfler, Kule, Kelime Kartları. Ayrıca her ünitede **sumeyyeogultekin** klasörü (443 çevrimiçi oyun ve kapak önizlemeleri) ile zengin Wordwall oyunları. |
| **Çalışma Kâğıtları ve Testler** | 6. sınıfta 18 özgün çalışma kâğıdı + 9 öğretmen anahtarı (yerel PDF). Ayrıca **ingilizcecin** (469 güncel belge), **dersingilizce** (154 PDF kâğıdı) ve **MEB ÖDSGM** (7-8. sınıf resmi testleri) klasörleri. Dış kaynak bağlantıları için internet gerekir. |
| **LGS Hazırlık Merkezi** | Ana menüden doğrudan erişilen LGS merkezi: **ingilizceciyiz.com** ve **dersingilizce.org** (lgsfiles) arşivinden 210+ çıkmış soru kitapçığı (2018-2026), MEB örnek soruları, denemeler, kelime testleri ve çalışma kâğıtları (canlı arama filtreli). |
| **Kitap Sunumları** | Kaynak sitedeki ders ve çalışma kitabı sunumlarının listesi (internet gerekir). |

## 4. Ders sırasında işinize yarayacak tuşlar

| Tuş | İşlev |
| --- | --- |
| `→` / `Boşluk` | Sonraki adım (bir kelime/örnek daha) |
| `↓` | Sayfanın kalanını bir anda aç |
| `←` | Geri |
| `F` | Tam ekran |
| `M` | **Kalem araçları** — tahtaya yazmak için (Pen, Highlighter, Eraser) |
| `E` | **Düzenleme** — slayda resim, yazı, şekil ekleme |
| `Esc` | Sunumu kapat |

Çizimleriniz slayt başına saklanır; düzenlemeler 💾 ile kaydedilir.

## 5. Sorun giderme

| Belirti | Çözüm |
| --- | --- |
| Tarayıcı açılmıyor | Adres çubuğuna `http://127.0.0.1:8777` yazın |
| "Python bulunamadı" | Windows'ta `src/runtime/` klasörünün silinmediğinden emin olun |
| Sayfa boş geliyor | Konsol penceresini kapatıp başlatıcıya tekrar çift tıklayın |
| Antivirüs uyarısı | Program yerel bir web sunucusu açar (yalnız 127.0.0.1). Güvenli. |

## Kaynak ve emek

Ders materyalleri MEB ders kitaplarından, [eltarena.com](https://eltarena.com), ingilizcecin.com,
dersingilizce.org ve MEB ÖDSGM üzerinde paylaşılan çalışmalardan derlenmiştir; hazırlayanların adları
her dosyanın yanında korunur. Bu paket tüm bu zengin kaynakları tek bir düzenli merkezde toplar.

Kaynak kodu ve geliştirme notları: <https://github.com/ctnkyaumt/eng-hub>
