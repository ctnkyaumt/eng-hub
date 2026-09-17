"""Import current-curriculum worksheet/test links from external sources:
- ingilizcecin.com (2020+)
- dersingilizce.org (worksheets only under PDF WORKSHEET DOWNLOAD LINKS)
- meb-odsgm (MEB ÖDSGM Beceri Temelli & LGS Örnek/Kazanım Testleri, Grades 7 & 8 only)

Run:
    python tools/import_worksheet_sources.py
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup
import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'app/data/worksheet-sources.json'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'

DERSINGILIZCE_URLS = {
    # Grade 5
    'g5/u1': 'https://www.dersingilizce.org/schoollife',
    'g5/u2': 'https://www.dersingilizce.org/classroomlife',
    'g5/u3': 'https://www.dersingilizce.org/personallife',
    'g5/u4': 'https://www.dersingilizce.org/familylife',
    'g5/u5': 'https://www.dersingilizce.org/city',
    'g5/u6': 'https://www.dersingilizce.org/lifeintheworld',
    'g5/u7': 'https://www.dersingilizce.org/partytime',
    'g5/u8': 'https://www.dersingilizce.org/lifeinthefuture',
    # Grade 6
    'g6/u1': 'https://www.dersingilizce.org/6schoollife',
    'g6/u2': 'https://www.dersingilizce.org/yummy',
    'g6/u3': 'https://www.dersingilizce.org/downtown',
    'g6/u4': 'https://www.dersingilizce.org/weather',
    'g6/u5': 'https://www.dersingilizce.org/fair',
    'g6/u6': 'https://www.dersingilizce.org/occupations',
    'g6/u7': 'https://www.dersingilizce.org/holidays',
    'g6/u8': 'https://www.dersingilizce.org/bookworms',
    # Grade 7
    'g7/u1': 'https://www.dersingilizce.org/appearance',
    'g7/u2': 'https://www.dersingilizce.org/sports',
    'g7/u3': 'https://www.dersingilizce.org/biographies',
    'g7/u4': 'https://www.dersingilizce.org/wildanimals',
    'g7/u5': 'https://www.dersingilizce.org/television',
    'g7/u6': 'https://www.dersingilizce.org/celebrations',
    'g7/u7': 'https://www.dersingilizce.org/dreams',
    'g7/u8': 'https://www.dersingilizce.org/publicbuildings',
    'g7/u9': 'https://www.dersingilizce.org/environment',
    'g7/u10': 'https://www.dersingilizce.org/planets',
    # Grade 8
    'g8/u1': 'https://www.dersingilizce.org/friendship',
    'g8/u2': 'https://www.dersingilizce.org/teenlife',
    'g8/u3': 'https://www.dersingilizce.org/kitchen',
    'g8/u4': 'https://www.dersingilizce.org/onthephone',
    'g8/u5': 'https://www.dersingilizce.org/internet',
    'g8/u6': 'https://www.dersingilizce.org/adventures',
    'g8/u7': 'https://www.dersingilizce.org/tourism',
    'g8/u8': 'https://www.dersingilizce.org/chores',
    'g8/u9': 'https://www.dersingilizce.org/science',
    'g8/u10': 'https://www.dersingilizce.org/naturalforces',
}

MEB_ODSGM_ITEMS = {
    # Grade 7 (only 7 and 8)
    'g7/u1': [
        {'title': '7. Sınıf 1. Ünite (Appearance and Personality) MEB Beceri Temelli Test Soruları',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/7.-Sinif-Ingilizce-1.-Unite-Test-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB Ölçme Değerlendirme Beceri Temelli Test'},
        {'title': '7. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],
    'g7/u2': [
        {'title': '7. Sınıf 2. Ünite (Sports) MEB Beceri Temelli Test Soruları',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/7.-Sinif-Ingilizce-2.-Unite-Test-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB Ölçme Değerlendirme Beceri Temelli Test'},
        {'title': '7. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],
    'g7/u3': [
        {'title': '7. Sınıf 3. Ünite (Biographies) MEB Beceri Temelli Test Soruları',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/7.-Sinif-Ingilizce-3.-Unite-Test-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB Ölçme Değerlendirme Beceri Temelli Test'},
        {'title': '7. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],
    'g7/u4': [
        {'title': '7. Sınıf 4. Ünite (Wild Animals) MEB Beceri Temelli Test Soruları',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/7.-Sinif-Ingilizce-4.-Unite-Test-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB Ölçme Değerlendirme Beceri Temelli Test'},
        {'title': '7. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],
    'g7/u5': [
        {'title': '7. Sınıf 5. Ünite (Television) MEB Beceri Temelli Test Soruları',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/7.-Sinif-Ingilizce-5.-Unite-Test-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB Ölçme Değerlendirme Beceri Temelli Test'},
        {'title': '7. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],
    'g7/u6': [
        {'title': '7. Sınıf 6. Ünite (Celebrations) MEB Beceri Temelli Test Soruları',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/7.-Sinif-Ingilizce-6.-Unite-Test-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB Ölçme Değerlendirme Beceri Temelli Test'},
        {'title': '7. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],
    'g7/u7': [
        {'title': '7. Sınıf 7. Ünite (Dreams) MEB ÖDSGM Kazanım ve Beceri Testi',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],
    'g7/u8': [
        {'title': '7. Sınıf 8. Ünite (Public Buildings) MEB Beceri Temelli Test Soruları',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/7.-Sinif-Ingilizce-8.-Unite-Test-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB Ölçme Değerlendirme Beceri Temelli Test'},
        {'title': '7. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],
    'g7/u9': [
        {'title': '7. Sınıf 9. Ünite (Environment) MEB Beceri Temelli Test Soruları',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/7.-Sinif-Ingilizce-9.-Unite-Test-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB Ölçme Değerlendirme Beceri Temelli Test'},
        {'title': '7. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],
    'g7/u10': [
        {'title': '7. Sınıf 10. Ünite (Planets) MEB Beceri Temelli Test Soruları',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/7.-Sinif-Ingilizce-10.-Unite-Test-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB Ölçme Değerlendirme Beceri Temelli Test'},
        {'title': '7. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/16aB8TwtZZWt8UUzMabfWVCJlBNkKbcTa/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Kazanım Kavrama Testleri Soru Kitapçığı ve Cevapları'},
    ],

    # Grade 8 (only 7 and 8)
    'g8/u1': [
        {'title': 'MEB LGS 1. Ünite (Friendship) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/1z2ElsNgAxnV2xXuOEsJrX1wKV_nv25Hh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf 1. Ünite (Friendship) LGS Çıkmış ve Örnek Sorular Derlemesi',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/10/LGS-ORNEK-SORULAR-UNIT-1.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'LGS Sınavında Çıkmış ve Yayımlanmış Sorular'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
        {'title': 'MEB LGS İngilizce Çıkmış Sorular (2018-2026)',
         'link': 'https://drive.google.com/file/d/1fbINALJeU9oaz5BPgyz0fvCRq4dcGZsg/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Geçmiş Yılların Resmi LGS İngilizce Sınav Kitapçıkları'},
    ],
    'g8/u2': [
        {'title': 'MEB LGS 2. Ünite (Teen Life) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/1baaFYvF96Fufk71oUafj8QJksgSTsu9f/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
        {'title': 'MEB LGS İngilizce Çıkmış Sorular (2018-2026)',
         'link': 'https://drive.google.com/file/d/1fbINALJeU9oaz5BPgyz0fvCRq4dcGZsg/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Geçmiş Yılların Resmi LGS İngilizce Sınav Kitapçıkları'},
    ],
    'g8/u3': [
        {'title': 'MEB LGS 3. Ünite (In The Kitchen) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/1bI8i9GI7AKC0VCLnXd45V9LTn9oN4Rs3/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
        {'title': 'MEB LGS İngilizce Çıkmış Sorular (2018-2026)',
         'link': 'https://drive.google.com/file/d/1fbINALJeU9oaz5BPgyz0fvCRq4dcGZsg/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Geçmiş Yılların Resmi LGS İngilizce Sınav Kitapçıkları'},
    ],
    'g8/u4': [
        {'title': 'MEB LGS 4. Ünite (On The Phone) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/1g3fc--K9GwTKAo4rx5rmAUmAuMlmAP-R/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf 4. Ünite MEB LGS Örnek ve Çıkmış Sorular',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/8.-SINIF-INGILIZCE-ORNEK-SORULAR-4.-UNITE-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'LGS Sınavında Çıkmış ve Yayımlanmış Sorular'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
    ],
    'g8/u5': [
        {'title': 'MEB LGS 5. Ünite (The Internet) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/13acirQdaMQtH_Nv_yaMF9NXqwwe0uomy/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf 5. Ünite MEB LGS Örnek ve Çıkmış Sorular',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/8.-SINIF-INGILIZCE-ORNEK-SORULAR-5.-UNITE-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'LGS Sınavında Çıkmış ve Yayımlanmış Sorular'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
    ],
    'g8/u6': [
        {'title': 'MEB LGS 6. Ünite (Adventures) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/1k4vyWVtddNvww4pUKIoCdVp6Gd6hYYtF/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf 6. Ünite MEB LGS Örnek ve Çıkmış Sorular',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/8.-SINIF-INGILIZCE-ORNEK-SORULAR-6.-UNITE-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'LGS Sınavında Çıkmış ve Yayımlanmış Sorular'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
    ],
    'g8/u7': [
        {'title': 'MEB LGS 7. Ünite (Tourism) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/1jixscj8ppPbhrKh-BPyeo5ZKVbIyLzd3/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf 7. Ünite MEB LGS Örnek ve Çıkmış Sorular',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/8.-SINIF-INGILIZCE-ORNEK-SORULAR-7.-UNITE-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'LGS Sınavında Çıkmış ve Yayımlanmış Sorular'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
    ],
    'g8/u8': [
        {'title': 'MEB LGS 8. Ünite (Chores) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/1RFRzRKU0QShcxqSvaExRc78MWxgPa4of/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf 8. Ünite MEB LGS Örnek ve Çıkmış Sorular',
         'link': 'https://ingilizceciyiz.com/wp-content/uploads/2020/12/8.-SINIF-INGILIZCE-ORNEK-SORULAR-8.-UNITE-by-ingilizceciyiz.com_.pdf',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'LGS Sınavında Çıkmış ve Yayımlanmış Sorular'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
    ],
    'g8/u9': [
        {'title': 'MEB LGS 9. Ünite (Science) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/1V-6ZR-xr6ieHjyRRl5PfGbzPV3IsDRm5/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
        {'title': 'MEB LGS İngilizce Çıkmış Sorular (2018-2026)',
         'link': 'https://drive.google.com/file/d/1fbINALJeU9oaz5BPgyz0fvCRq4dcGZsg/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Geçmiş Yılların Resmi LGS İngilizce Sınav Kitapçıkları'},
    ],
    'g8/u10': [
        {'title': 'MEB LGS 10. Ünite (Natural Forces) Örnek Soruları',
         'link': 'https://drive.google.com/file/d/1OYk7_vm584NnB4bkYhQBdYRSsOQxfakG/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'MEB ÖDSGM LGS Hazırlık Örnek Soru Fasikülü'},
        {'title': '8. Sınıf İngilizce MEB ÖDSGM Kazanım Kavrama Testleri Kitabı',
         'link': 'https://drive.google.com/file/d/1dk9qGPqbX4Kj07SEAMQrXZnt-HgiEXTh/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Tüm Üniteler Kazanım Kavrama Testleri ve Cevapları'},
        {'title': 'MEB LGS İngilizce Çıkmış Sorular (2018-2026)',
         'link': 'https://drive.google.com/file/d/1fbINALJeU9oaz5BPgyz0fvCRq4dcGZsg/view?usp=sharing',
         'by': 'MEB ÖDSGM', 'source': 'meb-odsgm', 'desc': 'Geçmiş Yılların Resmi LGS İngilizce Sınav Kitapçıkları'},
    ],
}


def canonical(url):
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip('/'), parsed.query, ''))


def extract_dersingilizce_worksheets(html, page_url):
    soup = BeautifulSoup(html, 'html.parser')
    header = None
    for h in soup.find_all(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'span'] and 'PDF WORKSHEET DOWNLOAD LINKS' in tag.get_text().upper()):
        header = h
        break
    if not header:
        return []
    sec = header.find_parent('section') or header.find_parent('div', class_=lambda c: c and 'comp-' in c)
    if not sec:
        return []

    items = []
    seen = set()
    for a in sec.find_all('a', href=True):
        link = a['href'].strip()
        title = a.get_text(' ', strip=True)
        title = re.sub(r'\s+', ' ', title).strip()
        if not title or title.lower() in ('star', 'tıklayınız', 'tiklayiniz', 'link'):
            continue
        if not ('drive.google.com' in link or link.lower().endswith('.pdf')):
            continue
        # Only worksheets: strictly exclude games and presentations/videos
        if any(k in title.lower() for k in ['game', 'oyun', 'jeopardy', 'wordwall', 'sunum', 'powerpoint', 'video', 'youtube']):
            continue
        if any(k in link.lower() for k in ['wordwall', 'youtube', 'docs.google.com/presentation']):
            continue
        canon = canonical(link)
        if canon in seen:
            continue
        seen.add(canon)
        items.append({
            'title': title,
            'link': link,
            'by': 'dersingilizce.org',
            'source': 'dersingilizce',
            'sourcePage': page_url,
        })
    return items


def scrape_dersingilizce():
    session = requests.Session()
    session.headers.update({'User-Agent': UA})
    results = {}
    print('Importing dersingilizce.org worksheets...', flush=True)
    for key, url in DERSINGILIZCE_URLS.items():
        try:
            r = session.get(url, timeout=12)
            items = extract_dersingilizce_worksheets(r.text, url)
            results[key] = items
            print(f'dersingilizce {key}: {len(items)} worksheets', flush=True)
        except Exception as e:
            print(f'dersingilizce {key} error: {e}', flush=True)
            results[key] = []
    return results


def main():
    data = json.loads(OUTPUT.read_text(encoding='utf-8')) if OUTPUT.exists() else {'units': {}}
    units = data.get('units', {})

    # 1. Scrape dersingilizce
    dersingilizce_data = scrape_dersingilizce()

    # 2. Merge into units
    for key in set(list(units.keys()) + list(dersingilizce_data.keys()) + list(MEB_ODSGM_ITEMS.keys())):
        existing = units.get(key, [])
        # Keep existing ingilizcecin items
        ingilizcecin_items = [it for it in existing if it.get('source') == 'ingilizcecin']
        new_dersingilizce = dersingilizce_data.get(key, [])
        new_meb = MEB_ODSGM_ITEMS.get(key, [])

        merged = ingilizcecin_items + new_dersingilizce + new_meb
        # Deduplicate
        seen = set()
        deduped = []
        for it in merged:
            c = canonical(it['link'])
            if c not in seen:
                seen.add(c)
                deduped.append(it)
        units[key] = deduped

    data['checkedAt'] = datetime.now(timezone.utc).isoformat()
    data['units'] = dict(sorted(units.items()))
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    total_items = sum(len(v) for v in units.values())
    total_ders = sum(len([i for i in v if i.get('source') == 'dersingilizce']) for v in units.values())
    total_meb = sum(len([i for i in v if i.get('source') == 'meb-odsgm']) for v in units.values())
    total_ing = sum(len([i for i in v if i.get('source') == 'ingilizcecin']) for v in units.values())
    print(f'Done! Total items: {total_items} (ingilizcecin: {total_ing}, dersingilizce: {total_ders}, meb-odsgm: {total_meb})', flush=True)


if __name__ == '__main__':
    main()
