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

It carries **the whole USB**: the program, the decks, the downloaded worksheets, the harvested
question banks, the mirrored activities and the pictures. The teacher's position — and it is
theirs to take — is that MEB's books and the worksheets shared on eltarena.com are already
public and this project only gathers them in one place; author names travel with every file in
the unit manifests. So do not strip content out of the repo again.

Only three files stay out, purely because GitHub refuses anything over 100 MB:
`res/book.pdf`, `res/book_8.pdf` and one 105 MB worksheet. They are attached to the release
instead, and nothing at runtime reads them (they are sources for rebuilding content).
`tools/cache/`, `tools/logs/` and `*.bak` are also ignored.

**Releases** are built by `.github/workflows/release.yml` when a `v*` tag is pushed: it lays the
program out as `eng-hub/{Start-Windows.bat, start-pardus.sh, README.md, src/}`, starts the
packaged server to prove the layout works, then publishes a full zip (~820 MB) and a lite zip
(~40 MB, program + presentations). The launchers detect both layouts, so the same file works in
the repo and in the package. The first-time README lives in `packaging/PACKAGE-README.md`.

`.gitattributes` pins `*.bat` to CRLF — see the launcher note in [[eng-hub-usb-app]].
