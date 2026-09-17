/* Colours and precise rich-text ranges from the teacher's reference decks. */
import { el } from "./ui.js";

export function markedParts(text, highlights = []) {
  const source = String(text || "").replace(/\*/g, "");
  const ranges = [];
  for (const mark of highlights) {
    if (!Number.isInteger(mark.start) || !Number.isInteger(mark.end) || mark.start < 0 ||
        mark.end <= mark.start || mark.end > source.length ||
        ranges.some(r => mark.start < r.end && mark.end > r.start)) continue;
    ranges.push(mark);
  }
  ranges.sort((a, b) => a.start - b.start);
  const parts = []; let cursor = 0;
  for (const range of ranges) {
    if (range.start > cursor) parts.push({ text: source.slice(cursor, range.start) });
    parts.push({ text: source.slice(range.start, range.end), role: range.role });
    cursor = range.end;
  }
  if (cursor < source.length) parts.push({ text: source.slice(cursor) });
  return parts;
}

export function richNodes(text, highlights) {
  if (!highlights) {
    // Old/custom slides remain supported; never interpret lesson text as HTML.
    highlights = []; let offset = 0;
    for (const part of String(text || "").split(/(\*[^*]+\*)/g)) {
      if (part.startsWith("*") && part.endsWith("*")) {
        highlights.push({ start: offset, end: offset + part.length - 2, role: "form" });
        offset += part.length - 2;
      } else offset += part.length;
    }
  }
  const roles = new Set(["form", "negative", "question", "pronoun", "ending", "always", "usually", "often", "sometimes"]);
  return markedParts(text, highlights).map(p => p.role
    ? el("em", { class: `grammar-${roles.has(p.role) ? p.role : "form"}`, text: p.text }) : p.text);
}
