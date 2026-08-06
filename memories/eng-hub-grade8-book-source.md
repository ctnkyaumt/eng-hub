---
name: eng-hub-grade8-book-source
description: "Where the grade-8 presentation content comes from in res/book_8.pdf (page map, glossary, unit functions)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0b0ab9da-d038-4464-822d-aec3c7cc6804
  modified: 2026-08-06T08:30:07.148Z
---

`res/book_8.pdf` is the MEB 8th-grade Student's Book (Bilim ve Kültür Yayınları, 174 pages)
and is the source of truth for the grade-8 decks in [[eng-hub-usb-app]].

**Page map (1-based PDF pages):** unit openers at 9, 25, 41, 57, 73, 89, 105, 121, 137, 153;
GLOSSARY on 169–170; bibliography 171.

**Vocabulary** comes from the GLOSSARY, which is already split by unit — that list is copied
verbatim into `tools/g8_vocab.py`, grouped into 2–3 named sections per unit, with Turkish
meanings and icons added there. Entries the glossary wraps across two lines
("get on well with / somebody", "keep/break / promises") must be joined back.

**Grammar sections** follow the functions printed on each unit opener page:
1 Friendship — inquiries, accepting/refusing, apologizing · 2 Teen Life — opinions, preferences,
likes/dislikes · 3 In the Kitchen — inquiries, preferences, describing processes · 4 On the
Phone — decisions at the time of speaking, phone conversations · 5 The Internet — excuses,
accepting/refusing · 6 Adventures — comparisons, reasons, preferences · 7 Tourism — comparisons,
experiences, describing places · 8 Chores — responsibilities, obligation · 9 Science — past
events, current actions · 10 Natural Forces — reasons and results, predictions.

Text extracts cleanly with PyMuPDF (unlike the grade-5 theme sheets, which are image-only and
need rendering + cropping).

Rebuild: `python tools/build_g8.py` then `python tools/polish_slides.py --grade 8`.
