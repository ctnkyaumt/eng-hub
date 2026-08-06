# ENG HUB — İlk kullanım

Taşınabilir İngilizce ders yardımcısı. **Kurulum yok, internet yok.**
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
ANA MENÜ → Sınıf (5, 6, 7, 8) → Ünite → SUNUM · OYUNLAR · ÇALIŞMA KÂĞITLARI · KİTAP SUNUMLARI
```

| Bölüm | Ne var |
| --- | --- |
| **Sunum** | 5. sınıf 8 tema + 8. sınıf 10 ünite — 600'den fazla slayt. İçerik tek tek açılır, her konudan sonra alıştırma sayfası gelir. |
| **Oyunlar** | 6 çevrimdışı oyun: Hızlı Test, Eşleştirme, Kelime Avı, Karışık Harfler, Kule, Kelime Kartları. |
| **Çalışma Kâğıtları** | 124 dosya. Tıklayınca bilgisayarın kendi PDF programında açılır. |
| **Kitap Sunumları** | Kaynak sitedeki ders/çalışma kitabı sunumlarının listesi (internet ister). |

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

Ders materyalleri MEB ders kitaplarından ve [eltarena.com](https://eltarena.com)
üzerinde paylaşan öğretmenlerin çalışmalarından derlenmiştir; hazırlayanların adları
her dosyanın yanında korunur. Bu paket onları tek yerde, internetsiz kullanılabilir
hâlde toplar.

Kaynak kodu ve geliştirme notları: <https://github.com/ctnkyaumt/eng-hub>
