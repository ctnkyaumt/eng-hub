---
name: eng-hub-tools
description: What each script in eng-hub/tools/ does and the order to run them
metadata: 
  node_type: memory
  type: project
  originSessionId: 0b0ab9da-d038-4464-822d-aec3c7cc6804
  modified: 2026-08-06T08:29:45.804Z
---

Build/refresh pipeline for [[eng-hub-usb-app]]. `tools/refresh.py` runs the whole chain;
individually, in dependency order:

| script | job |
| --- | --- |
| `fetch_catalog.py` | snapshots eltarena's open `/api/grades` JSON → `app/data/catalog.json`, `source-index.json`, `books.json`. Re-run after any content change — the menu counts come from it. |
| `pdf_to_pages.py` | renders `res/**/*.pdf` pages to webp for the deck's "Kaynak sayfalar" view |
| `crop_vocab.py` | cuts individual illustrations out of the theme sheets (`--sheet` writes a numbered contact sheet to check by eye) |
| `link_images.py` | attaches those crops to vocabulary cards from an **explicit hand-checked table** — automatic matching once put flags on pronoun cards, so wrong pictures are worse than none |
| `fetch_games.py` | pulls etkinlik.app question banks + images per unit |
| `fetch_worksheets.py` | downloads worksheets (Drive confirm-page handling, resumable) |
| `mirror_sites.py` | offline copies of static source activities; **skips slide-player presentations by default** (`--presentations` to force — each is 300+ runtime-built files and takes many minutes) |
| `build_g8.py` + `g8_vocab.py` | generate the grade-8 decks from `res/book_8.pdf` |
| `polish_slides.py` | orders grade-5 slides by the book, generates the interactive practice slides, splits crowded pages (max 12 cards / 2 tasks), converts number cards to keycaps. **Idempotent** — merges earlier splits before re-splitting. |
| `verify_content.py` | reports missing files, empty units, broken paths |
| `fetch_flags.py`, `get_python_win.py` | country flags (KKTC is hand-drawn: `app/img/flags/kktc.svg`), portable Windows Python |

Only external dependency: `pymupdf`, `pillow`, `numpy` (PDF/image tools). The app itself and
`server/enghub.py` are pure standard library.
