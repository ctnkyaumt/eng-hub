/* Repeat only new teaching setup; examples and translations stay independent. */
export function setupKey(kind, text) {
  return kind + ":" + String(text || "").normalize("NFKC")
    .replace(/\*/g, "").replace(/[‘’]/g, "'").replace(/\s+/g, " ").trim().toLowerCase();
}

export function earlierSetup(slides, index) {
  const seen = new Set();
  for (const slide of slides.slice(0, index)) {
    if (!["grammar", "compare"].includes(slide.type)) continue;
    if (slide.rule) seen.add(setupKey("rule", slide.rule));
    for (const chip of slide.chips || []) seen.add(setupKey("chip", chip));
  }
  return seen;
}
