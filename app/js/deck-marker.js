/* Marker tools: draw on the slide while teaching -----------------------------
   Pen, highlighter and eraser, exactly like the book presentations have. Each
   slide keeps its own strokes for the whole lesson, so going back and forth
   does not wipe what was written.
--------------------------------------------------------------------------- */
import { el, toast } from "./ui.js";

const TOOLS = {
  pen: { label: "Pen", icon: "✒️", width: 4, alpha: 1, cap: "round",
         colours: ["#ef4444", "#2563eb", "#16a34a", "#111827", "#f59e0b"] },
  highlighter: { label: "Highlighter", icon: "🖍️", width: 26, alpha: 0.18, cap: "butt",
                 colours: ["#fde047", "#86efac", "#f9a8d4", "#93c5fd", "#fdba74"] },
  eraser: { label: "Eraser", icon: "🧽", width: 30, alpha: 1, cap: "round", colours: [] },
};

export function createMarker({ deck, stage, getIndex }) {
  const canvas = el("canvas", { class: "marker-canvas" });
  const ctx = canvas.getContext("2d");
  // lives on the deck, not inside the scroller: a canvas in the stage would
  // widen it by the scrollbar and make both scrollbars appear
  deck.append(canvas);

  const strokes = new Map(); // slide index -> [{tool, points:[[x,y]…]}]
  let tool = null;
  let drawing = null;
  const colours = { pen: TOOLS.pen.colours[0], highlighter: TOOLS.highlighter.colours[0] };

  /* ------------------------------------------------------------- geometry */
  function resize() {
    const s = stage.getBoundingClientRect();
    const d = deck.getBoundingClientRect();
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    canvas.style.left = (s.left - d.left) + "px";
    canvas.style.top = (s.top - d.top) + "px";
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    canvas.width = Math.round(w);
    canvas.height = Math.round(h);
    redraw();
  }
  window.addEventListener("resize", resize);

  function line(s) {
    const t = TOOLS[s.tool];
    ctx.save();
    ctx.lineCap = t.cap;                     // highlighter keeps a flat, chisel tip
    ctx.lineJoin = t.cap === "butt" ? "bevel" : "round";
    ctx.lineWidth = t.width;
    if (s.tool === "eraser") {
      ctx.globalCompositeOperation = "destination-out";
      ctx.strokeStyle = "rgba(0,0,0,1)";
    } else {
      ctx.globalAlpha = t.alpha;
      ctx.strokeStyle = s.colour || t.colours[0];
    }
    ctx.beginPath();
    s.points.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
    if (s.points.length === 1) ctx.lineTo(s.points[0][0] + 0.1, s.points[0][1]);
    ctx.stroke();
    ctx.restore();
  }

  function redraw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const s of strokes.get(getIndex()) || []) line(s);
  }

  /* -------------------------------------------------------------- drawing */
  const pos = (e) => {
    const r = canvas.getBoundingClientRect();
    return [e.clientX - r.left, e.clientY - r.top];
  };

  canvas.addEventListener("pointerdown", (e) => {
    if (!tool) return;
    e.preventDefault();
    canvas.setPointerCapture(e.pointerId);
    drawing = { tool, colour: colours[tool], points: [pos(e)] };
    const list = strokes.get(getIndex()) || [];
    list.push(drawing);
    strokes.set(getIndex(), list);
    line(drawing);
  });

  canvas.addEventListener("pointermove", (e) => {
    if (!drawing) return;
    drawing.points.push(pos(e));
    line({ tool: drawing.tool, colour: drawing.colour, points: drawing.points.slice(-2) });
  });

  const stop = () => { drawing = null; };
  canvas.addEventListener("pointerup", stop);
  canvas.addEventListener("pointercancel", stop);
  canvas.addEventListener("pointerleave", stop);

  /* ----------------------------------------------------------------- menu */
  const menu = el("div", { class: "marker-menu hidden" });
  const items = {};

  function pick(name) {
    tool = tool === name ? null : name;
    for (const [k, node] of Object.entries(items)) node.classList.toggle("on", k === tool);
    deck.classList.toggle("marking", !!tool);
    btn.classList.toggle("on", !!tool);
    menu.classList.add("hidden");
  }

  for (const [name, t] of Object.entries(TOOLS)) {
    const row = el("button", { class: "mm-row", onclick: () => pick(name) }, [
      el("span", { class: "mm-ic", text: t.icon }),
      t.label,
    ]);
    items[name] = row;
    menu.append(row);
    if (!t.colours.length) continue;
    const swatches = el("div", { class: "mm-colours" }, t.colours.map((c) =>
      el("button", {
        class: "mm-dot" + (c === colours[name] ? " on" : ""),
        style: "background:" + c, title: c,
        onclick: (e) => {
          e.stopPropagation();
          colours[name] = c;
          [...swatches.children].forEach((n) => n.classList.toggle("on", n.title === c));
          if (tool !== name) pick(name); else menu.classList.add("hidden");
        },
      })
    ));
    menu.append(swatches);
  }
  menu.append(el("div", { class: "mm-sep" }));
  menu.append(el("button", {
    class: "mm-row", text: "Erase All",
    onclick: () => { strokes.set(getIndex(), []); redraw(); menu.classList.add("hidden"); },
  }));
  menu.append(el("button", {
    class: "mm-row", text: "End Drawing",
    onclick: () => { if (tool) pick(tool); else menu.classList.add("hidden"); },
  }));

  const btn = el("button", { class: "tb-btn", title: "Marker Tools (M)", text: "🖊️" });
  const wrap = el("div", { class: "marker-wrap" }, [btn, menu]);
  btn.onclick = (e) => {
    e.stopPropagation();
    menu.classList.toggle("hidden");
  };
  document.addEventListener("click", (e) => {
    if (!wrap.contains(e.target)) menu.classList.add("hidden");
  });

  return {
    button: wrap,
    slideChanged: () => { resize(); redraw(); },
    toggleMenu: () => menu.classList.toggle("hidden"),
    clearAll: () => { strokes.clear(); redraw(); toast("Tüm çizimler silindi"); },
    resize,
  };
}
