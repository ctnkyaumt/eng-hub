---
name: eng-hub-deck-behaviour
description: How the ENG HUB presentation deck behaves and the decisions behind it
metadata: 
  node_type: memory
  type: project
  originSessionId: 0b0ab9da-d038-4464-822d-aec3c7cc6804
  modified: 2026-08-06T08:30:32.527Z
---

Behaviour the teacher asked for in the deck of [[eng-hub-usb-app]] (`app/js/deck.js`,
`deck-edit.js`, `deck-marker.js`, `exercises.js`):

- **Step reveal.** "Sonraki" uncovers one item at a time, then moves to the next slide;
  `↓` reveals the rest. Headings and the title/end slides are never stepped — the class must
  see the topic straight away. A segmented bar under the top bar shows how many steps are left.
- **Fit to window.** Each slide is scaled between 0.55× and 1.8× so sparse slides grow and
  crowded ones shrink; below 0.55× the stage scrolls. 2px of slack is subtracted, otherwise
  a rounding error summons scrollbars.
- **Crowded pages split** (max 12 vocabulary cards, 2 practice tasks) with a `1/2` badge.
- **Practice slides** after every content slide: match, multiple choice, picture→word,
  fill-the-gap, sentence ordering. Generated from the slide's own words and starred examples.
  All task wording is **English**; only the word meanings are Turkish.
- **Editor (✏️ / `E`)**: add pictures, text, rectangles, circles, triangles and speech bubbles;
  drag to move, corner to resize. Coordinates are percentages. Saves through
  `POST /api/save` back into `slides.json`, keeping a `.bak`.
- **Marker tools (🖊️ / `M`)**: Pen / Highlighter / Eraser with 5 colours each, plus Erase All
  and End Drawing — same menu as the source book presentations. Strokes are kept per slide.
  The canvas is attached to the deck, **not** inside the scrolling stage; inside it, the
  scrollbar width made both scrollbars appear.
- Emoji that Windows cannot draw (flags, the 🔢 "1234" glyph) are replaced with SVG flags and
  two-digit keycap boxes.
