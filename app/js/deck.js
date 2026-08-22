/* Presentation deck v2 -------------------------------------------------------
   * content appears step by step (Next reveals the next item, then the slide)
   * every slide is scaled to fit the window, and scrolls when it cannot
   * slide types: title | vocab | grammar | compare | dialogue | scene
                  | practice | exercise | pages | end
   * edit mode lets the teacher drop pictures, text and shapes onto a slide
--------------------------------------------------------------------------- */
import { getSites, getSlides, getUnit, unitPath } from "./store.js";
import { el, mount, setCrumbs, beep, toast } from "./ui.js";
import { taskNode } from "./exercises.js";

if (!document.querySelector('link[href="/app/css/deck.css"]')) {
  document.head.append(el("link", { rel: "stylesheet", href: "/app/css/deck.css" }));
}

export async function startDeck(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const data = await getSlides(gid, uid);
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: `Ünite ${unit.no}`, hash: `#/${gid}/${uid}` },
    { label: "Sunum" },
  ]);

  const mirrored = await getSites(gid, uid, "presentation");
  const mirrorList = mirrored.length
    ? [
        el("h2", { class: "section-title", text: `Kaynaktan sunumlar (${mirrored.length})` }),
        el("div", { class: "list" }, mirrored.map((m) =>
          el("button", { class: "row", onclick: () => window.open(m.url, "_blank", "noopener") }, [
            el("span", { class: "ic", text: "📺" }),
            el("div", { class: "txt" }, [
              el("b", { text: m.title }),
              el("small", { text: m.by ? "Hazırlayan: " + m.by : "USB'de hazır" }),
            ]),
            el("span", { class: "go", text: "▶" }),
          ])
        )),
        el("div", { style: "margin-top:20px" }, [
          el("button", { class: "btn", text: "← Üniteye dön", onclick: () => (location.hash = `#/${gid}/${uid}`) }),
        ]),
      ]
    : [];

  if (!data) {
    return mount(screen,
      el("div", { class: "empty" }, [
        el("span", { class: "emoji", text: "📽️" }),
        el("p", { text: "Bu ünite için hazırlanmış sunum yok." }),
        el("p", { text: `PDF'i res/ klasörüne koyup tools/pdf_to_pages.py çalıştırın, sonra content/${gid}/${uid}/presentation/slides.json ekleyin.` }),
      ]),
      ...mirrorList
    );
  }

  const ctx = {
    gid, uid, grade, unit, data,
    base: `${unitPath(gid, uid)}/presentation/`,
    savePath: `content/${gid}/${uid}/presentation/slides.json`,
  };
  const slides = data.slides || [];
  let i = 0, step = 0, steps = [];

  const stage = el("div", { class: "deck-stage" });
  const wrap = el("div", { class: "slide-wrap" });
  stage.append(wrap);
  const bar = el("i", { style: "width:0%" });
  const stepbar = el("div", { class: "stepbar" });
  const count = el("span", { class: "count" });
  const dots = el("div", { class: "dots" });
  const editSlot = el("div");
  const markerSlot = el("span", { class: "marker-slot" });

  const deck = el("div", {
    class: "deck",
    style: `--a1:${data.accent?.[0] || "#38bdf8"};--a2:${data.accent?.[1] || "#6366f1"}`,
  }, [
    el("div", { class: "deck-bar" }, [
      el("span", { style: "font-size:20px", text: data.emoji || unit.emoji || "📘" }),
      el("div", {}, [
        el("div", { class: "title", text: data.title || unit.title }),
        el("div", { class: "sub", text: `${grade.title} · Ünite ${unit.no}` }),
      ]),
      el("span", { class: "grow" }),
      count,
      markerSlot,
      el("button", { class: "tb-btn", title: "Düzenle (E)", text: "✏️", onclick: toggleEdit }),
      el("button", { class: "tb-btn", title: "Tam ekran (F)", text: "⛶", onclick: toggleFull }),
      el("button", { class: "tb-btn", title: "Kapat (Esc)", text: "✕", onclick: () => close() }),
    ]),
    editSlot,
    el("div", { class: "deck-progress" }, [bar]),
    stepbar,
    stage,
    el("div", { class: "deck-foot" }, [
      el("button", { class: "btn", text: "← Önceki", onclick: prev }),
      dots,
      el("button", { class: "btn primary", text: "Sonraki →", onclick: next }),
    ]),
  ]);

  document.querySelectorAll(".deck").forEach((d) => d.remove()); // no stacking
  document.body.append(deck);
  mount(screen, ...mirrorList);

  dots.replaceChildren(...slides.map((_, n) =>
    el("button", { class: "dot", title: String(n + 1), onclick: () => show(n) })
  ));

  // marker tools live next to the edit button, like in the book presentations
  const { createMarker } = await import("./deck-marker.js");
  const marker = createMarker({ deck, stage, getIndex: () => i });
  markerSlot.append(marker.button);

  /* ------------------------------------------------------------- rendering */
  function show(n, atEnd = false) {
    i = Math.max(0, Math.min(slides.length - 1, n));
    const node = render(slides[i], ctx);
    wrap.replaceChildren(node);
    ctx.slideNode = node;
    steps = [...node.querySelectorAll(".step")];
    step = atEnd ? steps.length : 0;
    applySteps();
    drawOverlays(node, slides[i], ctx);
    stage.scrollTop = 0;
    count.textContent = `${i + 1} / ${slides.length}`;
    bar.style.width = ((i + 1) / slides.length) * 100 + "%";
    [...dots.children].forEach((d, k) => d.classList.toggle("on", k === i));
    if (editor?.isOn()) editor.rewire();
    marker.slideChanged();
    fit();
    setTimeout(fit, 60); // again once images/fonts settle
  }

  function applySteps() {
    steps.forEach((s, k) => s.classList.toggle("on", k < step));
    drawStepbar();
    fit();
    setTimeout(fit, 60); // again once images/fonts settle
  }

  /** One segment per hidden item, so the class can see how much is left. */
  function drawStepbar() {
    stepbar.classList.toggle("hidden", steps.length === 0);
    if (steps.length !== stepbar.children.length) {
      stepbar.replaceChildren(...steps.map(() => el("span")));
    }
    [...stepbar.children].forEach((s, k) => s.classList.toggle("on", k < step));
    stepbar.classList.toggle("done", step >= steps.length);
  }

  /** Keep slides readable first, then fit them to the available classroom
   *  viewport. Very tall slides scroll instead of shrinking into fine print. */
  function fit() {
    const node = ctx.slideNode;
    if (!node) return;
    node.style.transform = "none";
    wrap.style.height = "";
    const css = getComputedStyle(wrap);
    const padH = parseFloat(css.paddingTop) + parseFloat(css.paddingBottom);
    const padW = parseFloat(css.paddingLeft) + parseFloat(css.paddingRight);
    // 2px of slack keeps a rounding error from summoning a scrollbar
    const availH = stage.clientHeight - padH - 2;
    const availW = stage.clientWidth - padW - 2;
    const h = node.offsetHeight, w = node.offsetWidth;
    if (!h || !w) return;
    const minFit = node.classList.contains("exercise-slide") ? 0.82 : 0.76;
    const maxFit = node.classList.contains("title-slide") ? 1 : 1.08;
    const k = Math.max(minFit, Math.min(maxFit, availH / h, availW / w));
    node.style.transform = `scale(${k})`;
    wrap.style.height = h * k + "px";
  }
  window.addEventListener("resize", fit);

  function next() {
    if (step < steps.length) { step++; applySteps(); beep("tick"); return; }
    if (i < slides.length - 1) show(i + 1);
  }
  function prev() {
    if (step > 0) { step--; applySteps(); return; }
    if (i > 0) show(i - 1, true);
  }
  function revealAll() { step = steps.length; applySteps(); }

  /* ---------------------------------------------------------------- chrome */
  function toggleFull() {
    if (document.fullscreenElement) document.exitFullscreen();
    else deck.requestFullscreen?.();
  }

  let closed = false;
  function close(navigate = true) {
    if (closed) return;
    closed = true;
    document.removeEventListener("keydown", onKey);
    window.removeEventListener("resize", fit);
    window.removeEventListener("hashchange", onRouteChange);
    deck.remove();
    if (navigate && !mirrorList.length) location.hash = `#/${gid}/${uid}`;
  }

  function onRouteChange() {
    if (location.hash !== `#/${gid}/${uid}/sunum`) close(false);
  }

  let editor = null;
  async function toggleEdit() {
    if (!editor) {
      const mod = await import("./deck-edit.js");
      editor = mod.createEditor({ deck, editSlot, ctx, getSlide: () => slides[i], refresh: () => show(i, true) });
    }
    editor.toggle();
  }

  function onKey(e) {
    if (e.target instanceof Element && e.target.matches("input, textarea, [contenteditable=true]")) return;
    if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") { e.preventDefault(); next(); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); prev(); }
    else if (e.key === "ArrowDown") { e.preventDefault(); revealAll(); }
    else if (e.key === "Home") show(0);
    else if (e.key === "End") show(slides.length - 1);
    else if (e.key === "Escape" && !document.fullscreenElement) close();
    else if (e.key === "f" || e.key === "F") toggleFull();
    else if (e.key === "e" || e.key === "E") toggleEdit();
    else if (e.key === "m" || e.key === "M") marker.toggleMenu();
  }
  document.addEventListener("keydown", onKey);
  window.addEventListener("hashchange", onRouteChange);

  show(0);
}

/* --------------------------------------------------------------- overlays */
function drawOverlays(node, slide, ctx) {
  const layer = el("div", { class: "layer" });
  for (const o of slide.overlays || []) layer.append(objNode(o, ctx));
  node.append(layer);
  node.__layer = layer;
}

export function objNode(o, ctx) {
  const n = el("div", {
    class: "obj",
    style: `left:${o.x}%;top:${o.y}%;width:${o.w}%;height:${o.h}%;` +
           (o.rot ? `transform:rotate(${o.rot}deg);` : ""),
  });
  n.__obj = o;

  if (o.type === "image" && o.src) {
    n.append(el("img", { src: o.src.startsWith("/") ? o.src : ctx.base + o.src, alt: "" }));
  } else if (o.type !== "text") {
    n.append(shapeSvg(o));
  }
  if (o.text) {
    n.append(el("div", {
      class: "txt-body",
      style: `color:${o.color || "#0f172a"};font-size:${o.size || 22}px;` +
             (o.type === "text" ? "text-shadow:0 1px 3px rgba(0,0,0,.35)" : ""),
      text: o.text,
    }));
  }
  n.append(el("div", { class: "handle" }));
  return n;
}

function shapeSvg(o) {
  const fill = o.fill || "#ffffff";
  const stroke = o.stroke || "rgba(15,23,42,.25)";
  let inner;
  if (o.type === "circle") inner = `<ellipse cx="50" cy="50" rx="49" ry="49" fill="${fill}" stroke="${stroke}" stroke-width="1"/>`;
  else if (o.type === "triangle") inner = `<polygon points="50,2 98,98 2,98" fill="${fill}" stroke="${stroke}" stroke-width="1"/>`;
  else if (o.type === "bubble") inner =
    `<rect x="1" y="1" width="98" height="74" rx="14" fill="${fill}" stroke="${stroke}" stroke-width="1"/>` +
    `<polygon points="20,74 22,97 40,74" fill="${fill}" stroke="${stroke}" stroke-width="1"/>`;
  else inner = `<rect x="1" y="1" width="98" height="98" rx="8" fill="${fill}" stroke="${stroke}" stroke-width="1"/>`;
  return el("div", {
    class: "shape",
    html: `<svg viewBox="0 0 100 100" preserveAspectRatio="none" width="100%" height="100%">${inner}</svg>`,
  });
}

/* -------------------------------------------------------------- renderers */
/** Headings are never revealed step by step - the class must see the topic. */
function head(s) {
  return [
    s.title
      ? el("h2", {}, [
          s.title,
          s.part ? el("span", { class: "part", text: `${s.part[0]}/${s.part[1]}` }) : null,
        ])
      : null,
    s.titleTr ? el("p", { class: "sub-tr", text: s.titleTr }) : null,
  ];
}

function exNode(e, ctx) {
  return el("div", { class: "ex step" + (e.img ? " with-pic" : "") }, [
    e.img ? el("img", { class: "ex-pic", src: imgUrl(e.img, ctx), alt: "" }) : null,
    el("div", {}, [
      el("div", { class: "en", html: (e.en || "").replace(/\*(.+?)\*/g, "<em>$1</em>") }),
      e.tr ? el("div", { class: "tr", text: e.tr }) : null,
    ]),
  ]);
}

/** "/app/img/flags/tr.svg" stays as is; "p01-03.png" is a unit picture. */
function imgUrl(name, ctx) {
  return name.startsWith("/") ? name : ctx.base + "img/" + name;
}

/** Numbers show as two keycap digits instead of the unreadable 1234 glyph. */
function keycaps(text) {
  const box = el("span", { class: "num2" });
  for (const ch of String(text)) box.append(el("b", { text: ch }));
  return box;
}

function vcardMedia(v, ctx) {
  // not lazy: the files are local and lazy images never load inside a scaled slide
  if (v.img) return el("img", { class: "pic", src: imgUrl(v.img, ctx), alt: v.en });
  if (v.num !== undefined) return keycaps(v.num);
  return v.emoji ? el("span", { class: "ic", text: v.emoji }) : null;
}

/** Use only pictures already attached to reviewed vocabulary cards. This keeps
 *  the unit cover specific without guessing at new word/image matches. */
function unitPictures(ctx, limit = 3) {
  const seen = new Set();
  const out = [];
  for (const slide of ctx.data.slides || []) {
    if (slide.type !== "vocab") continue;
    for (const item of slide.items || []) {
      if (!item.img || seen.has(item.img)) continue;
      seen.add(item.img);
      out.push({ src: imgUrl(item.img, ctx), alt: item.en || "" });
      if (out.length >= limit) return out;
    }
  }
  return out;
}

function titleVisual(s, ctx) {
  if (s.cover) {
    return el("div", { class: "unit-visual" }, [
      el("img", { class: "cover", src: imgUrl(s.cover, ctx), alt: "" }),
    ]);
  }
  const pictures = unitPictures(ctx);
  if (pictures.length) {
    return el("div", { class: "unit-visual" }, pictures.map((p) =>
      el("img", { class: "cover-card", src: p.src, alt: p.alt })
    ));
  }
  return el("div", { class: "big-emoji", text: s.emoji || ctx.data.emoji || "📘" });
}

function render(s, ctx) {
  const box = (cls, kids) => el("div", { class: "slide " + (cls || "") }, kids);

  switch (s.type) {
    case "title": // shown all at once - it is the cover of the lesson
      return box("title-slide", [
        el("div", { class: "title-layout" }, [
          titleVisual(s, ctx),
          el("div", { class: "title-copy" }, [
            el("div", { class: "theme-no", text: s.kicker || `THEME ${ctx.unit.no}` }),
            el("h1", { text: s.title }),
            el("p", { class: "sub-tr", style: "font-size:clamp(16px,2.4vw,24px)", text: s.titleTr || "" }),
          ]),
        ]),
      ]);

    case "vocab":
      return box("", [
        ...head(s),
        el("div", { class: "vocab-grid" }, (s.items || []).map((v) =>
          el("div", { class: "vcard step" }, [
            vcardMedia(v, ctx),
            el("div", { class: "en", text: v.en }),
            el("div", { class: "tr", text: v.tr }),
          ])
        )),
      ]);

    case "grammar":
      return box("", [
        ...head(s),
        s.rule ? el("div", { class: "rule-box step", html: s.rule.replace(/\*(.+?)\*/g, "<b>$1</b>") }) : null,
        s.chips ? el("div", { class: "chips" }, s.chips.map((c) => el("div", { class: "chip-word step", text: c }))) : null,
        s.examples ? el("div", { class: "ex-list" }, s.examples.map((e) => exNode(e, ctx))) : null,
      ]);

    case "compare":
      return box("", [
        ...head(s),
        s.rule ? el("div", { class: "rule-box step", html: s.rule.replace(/\*(.+?)\*/g, "<b>$1</b>") }) : null,
        el("div", { class: "compare" }, (s.columns || []).map((c) =>
          el("div", { class: "col " + (c.tone || "") }, [
            el("h3", { class: "step", text: c.title }),
            ...(c.examples || []).map((e) => exNode(e, ctx)),
          ])
        )),
      ]);

    case "dialogue":
      // rendered as a chat: each speaker gets their own bubble, sides alternate
      return box("", [
        ...head(s),
        el("div", { class: "dlg" }, (s.dialogues || []).map((d) =>
          el("div", { class: "bubble step" }, (d.lines || []).map((l, k) =>
            el("div", { class: "speech " + (k % 2 ? "right" : ""), style: "margin-bottom:14px" }, [
              l.text,
              el("small", { text: l.who }),
            ])
          ))
        )),
      ]);

    case "scene":
      return box("", [
        ...head(s),
        el("div", { class: "scene" }, [
          s.img
            ? el("img", { class: "art step", src: imgUrl(s.img, ctx), alt: "" })
            : el("div", { class: "big-emoji step", style: "text-align:center", text: s.emoji || "💬" }),
          el("div", {}, (s.bubbles || []).map((b, k) =>
            el("div", { class: "speech step " + (k % 2 ? "right" : ""), }, [
              b.text,
              b.tr ? el("small", { text: b.tr }) : null,
            ])
          )),
        ]),
      ]);

    case "practice":
      return box("", [
        ...head(s),
        el("div", { class: "list" }, (s.items || []).map((q) => {
          const row = el("div", { class: "quizrow step" }, [
            el("span", { text: "❓" }),
            el("span", { text: q.q }),
            el("span", { class: "a", text: q.a }),
          ]);
          row.onclick = () => { row.classList.toggle("open"); beep("tick"); };
          return row;
        })),
      ]);

    case "exercise":
      return box("exercise-slide", [
        ...head(s),
        el("div", { class: "exercise-grid" + ((s.tasks || []).length === 1 ? " single" : "") }, (s.tasks || []).map((t) => {
          const n = taskNode(t, ctx);
          n.classList.add("step");
          return n;
        })),
      ]);

    case "pages":
      return box("", [
        ...head(s),
        el("div", { class: "pages-strip" }, (ctx.data.pages || []).map((p) => {
          const img = el("img", { class: "step", src: ctx.base + "pages/" + p, alt: "", loading: "lazy" });
          img.onclick = () => {
            const lb = el("div", { class: "lightbox" }, [el("img", { src: img.src, alt: "" })]);
            lb.onclick = () => lb.remove();
            document.body.append(lb);
          };
          return img;
        })),
      ]);

    case "end":
      return box("end-slide", [
        el("div", { class: "big-emoji", text: s.emoji || "🎉" }),
        el("h2", { text: s.title || "Hadi oynayalım!" }),
        el("p", { class: "sub-tr", text: s.titleTr || "" }),
        el("div", { class: "end-actions" }, [
          el("button", {
            class: "btn primary big", text: "🎮 Oyunlara git",
            onclick: () => { document.querySelector(".deck")?.remove(); location.hash = `#/${ctx.gid}/${ctx.uid}/oyunlar`; },
          }),
          el("button", {
            class: "btn big", text: "📄 Çalışma kâğıtları",
            onclick: () => { document.querySelector(".deck")?.remove(); location.hash = `#/${ctx.gid}/${ctx.uid}/calisma`; },
          }),
        ]),
      ]);

    default:
      return box("", [el("h2", { class: "step", text: s.title || "" })]);
  }
}

export { toast };
