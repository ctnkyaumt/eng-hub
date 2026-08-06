---
name: eng-hub-usb-app
description: "ENG HUB — the portable USB English-teaching app built in C:\\Users\\ev\\Desktop\\code\\eng-hub (what it is, how it runs, what is built)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0b0ab9da-d038-4464-822d-aec3c7cc6804
  modified: 2026-08-06T08:29:21.907Z
---

ENG HUB is a portable USB program for teaching MEB middle-school English (grades 5–8),
built from scratch in `C:\Users\ev\Desktop\code\eng-hub`. Runs on Windows and Pardus with
no installation, fully offline.

**How it runs:** `Start-Windows.bat` / `start-pardus.sh` → `server/enghub.py` (stdlib
`http.server` on 127.0.0.1:8777) → browser. Windows uses the bundled portable CPython in
`runtime/python-win/`; Pardus uses system `python3`. The `.bat` **must keep CRLF line
endings** — with LF, cmd cannot find its labels and falls straight through to the error branch.

**Menu:** Ana Menü → Sınıf (5–8) → Ünite 1–10 → SUNUM · OYUNLAR · ÇALIŞMA KÂĞITLARI · KİTAP SUNUMLARI.

**Built as of 2026-08-06:**
- Grade 5: 8 units, 371 slides authored from the MEB theme sheets in `res/5th grade/`,
  ordered by `res/book.pdf`'s theme table. 173 vocabulary cards use pictures cropped from
  those sheets.
- Grade 8: 10 units, 238 slides generated from `res/book_8.pdf` — see [[eng-hub-grade8-book-source]].
- Games: 15.370 questions + 3.012 word pairs harvested from eltarena's etkinlik.app API,
  played in 6 offline modes. 66 static source activities mirrored to the USB.
- Worksheets: 124 files downloaded; 191 book presentations stay as links.
- USB footprint ≈ 1.3 GB.

Content lives in `content/g<N>/u<M>/{presentation,games,worksheets,sites}/`; the UI is plain
ES modules in `app/js/`; every build/refresh script is in `tools/` (see [[eng-hub-tools]]).
