---
name: eng-hub-github-repo
description: The public GitHub repo for ENG HUB and the rule about what is allowed in it
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0b0ab9da-d038-4464-822d-aec3c7cc6804
  modified: 2026-08-06T09:28:01.376Z
---

Public repo: **https://github.com/ctnkyaumt/eng-hub** (branch `main`, remote `origin`).

It carries the **program and the decks that were written for it** — `app/`, `server/`, `tools/`,
the launchers, `content/**/presentation/slides.json`, and a `memories/` folder mirroring the
notes in this memory directory. Everything else is deliberately left out by `.gitignore`:

- `res/` — MEB course books and theme sheets (other people's material, 280 MB)
- downloaded worksheets, harvested game banks, mirrored sites, cropped sheet pictures
- `runtime/` portable Python and `app/img/words/*.jpg` (refetchable)

The reason is both size (the USB build is ~1.3 GB) and redistribution: those files belong to
MEB and to the teachers who published on eltarena. Every one of them is rebuilt by
`python tools/refresh.py`. Keep it that way when adding files.

`.gitattributes` pins `*.bat` to CRLF — see the launcher note in [[eng-hub-usb-app]].
