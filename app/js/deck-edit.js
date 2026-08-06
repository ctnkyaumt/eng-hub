/* Slide editor: drop pictures, text and shapes onto any slide ----------------
   Objects are stored per slide in slides.json as `overlays`, with positions in
   percent so they stay put at every window size. Saving writes the file back to
   the USB through the local server (a .bak copy is kept).
--------------------------------------------------------------------------- */
import { objNode } from "./deck.js";
import { el, toast } from "./ui.js";

const SHAPES = [
  ["rect", "▭ Dikdörtgen"],
  ["circle", "⬭ Daire"],
  ["triangle", "△ Üçgen"],
  ["bubble", "💬 Balon"],
];

export function createEditor({ deck, editSlot, ctx, getSlide, refresh }) {
  let on = false;
  let sel = null;
  let dirty = false;

  const file = el("input", { type: "file", accept: "image/*", style: "display:none" });
  file.onchange = () => file.files[0] && addImage(file.files[0]);

  const bar = el("div", { class: "edit-bar" }, [
    el("button", { class: "btn", text: "🖼️ Resim", onclick: () => file.click() }),
    el("button", { class: "btn", text: "🅰️ Yazı", onclick: () => addObj({ type: "text", text: "Yazı", color: "#ffffff", size: 26, w: 26, h: 9 }) }),
    ...SHAPES.map(([t, label]) =>
      el("button", { class: "btn", text: label, onclick: () => addObj({ type: t, fill: "#ffffff", text: "" }) })
    ),
    el("span", { class: "sep" }),
    el("button", { class: "btn", text: "✎ Metin", onclick: editText }),
    el("button", { class: "btn", text: "🎨 Renk", onclick: editColour }),
    el("button", { class: "btn", text: "🗑️ Sil", onclick: removeSel }),
    el("span", { class: "sep" }),
    el("button", { class: "btn primary", text: "💾 Kaydet", onclick: save }),
    el("span", { class: "note", text: "Sürükle: taşı · köşe: boyutlandır · Delete: sil" }),
    file,
  ]);

  /* ------------------------------------------------------------- selection */
  function layer() {
    return ctx.slideNode?.__layer;
  }

  function select(node) {
    layer()?.querySelectorAll(".obj").forEach((n) => n.classList.remove("sel"));
    sel = node || null;
    sel?.classList.add("sel");
  }

  function addObj(props) {
    const slide = getSlide();
    slide.overlays = slide.overlays || [];
    const o = { x: 34, y: 34, w: 24, h: 18, ...props };
    slide.overlays.push(o);
    const n = objNode(o, ctx);
    layer()?.append(n);
    wire(n);
    select(n);
    dirty = true;
  }

  async function addImage(f) {
    const name = Date.now() + "-" + f.name.replace(/[^\w.\-]+/g, "_").toLowerCase();
    const rel = `content/${ctx.gid}/${ctx.uid}/presentation/img/${name}`;
    try {
      const r = await fetch("/api/upload?path=" + encodeURIComponent(rel), {
        method: "POST", body: await f.arrayBuffer(),
      });
      const j = await r.json();
      if (!j.ok) throw new Error(j.error);
      addObj({ type: "image", src: name, w: 28, h: 24 });
      toast("Resim eklendi");
    } catch (err) {
      toast("Resim yüklenemedi: " + err.message, true);
    }
    file.value = "";
  }

  function removeSel() {
    if (!sel) return toast("Önce bir nesne seçin");
    const slide = getSlide();
    slide.overlays = (slide.overlays || []).filter((o) => o !== sel.__obj);
    sel.remove();
    sel = null;
    dirty = true;
  }

  function editText() {
    if (!sel) return toast("Önce bir nesne seçin");
    const v = prompt("Yazı:", sel.__obj.text || "");
    if (v === null) return;
    sel.__obj.text = v;
    dirty = true;
    redrawOne();
  }

  function editColour() {
    if (!sel) return toast("Önce bir nesne seçin");
    const o = sel.__obj;
    const key = o.type === "text" ? "color" : "fill";
    const v = prompt("Renk (örn. #ffd166):", o[key] || "#ffffff");
    if (!v) return;
    o[key] = v;
    dirty = true;
    redrawOne();
  }

  function redrawOne() {
    const o = sel.__obj;
    const fresh = objNode(o, ctx);
    sel.replaceWith(fresh);
    wire(fresh);
    select(fresh);
  }

  /* -------------------------------------------------------------- dragging */
  function wire(n) {
    n.addEventListener("pointerdown", (e) => {
      if (!on) return;
      e.preventDefault();
      e.stopPropagation();
      select(n);
      const o = n.__obj;
      const host = ctx.slideNode.getBoundingClientRect();
      const resize = e.target.classList.contains("handle");
      const sx = e.clientX, sy = e.clientY;
      const s0 = { x: o.x, y: o.y, w: o.w, h: o.h };

      const move = (ev) => {
        const dx = ((ev.clientX - sx) / host.width) * 100;
        const dy = ((ev.clientY - sy) / host.height) * 100;
        if (resize) {
          o.w = Math.max(4, s0.w + dx);
          o.h = Math.max(4, s0.h + dy);
          n.style.width = o.w + "%";
          n.style.height = o.h + "%";
        } else {
          o.x = s0.x + dx;
          o.y = s0.y + dy;
          n.style.left = o.x + "%";
          n.style.top = o.y + "%";
        }
        dirty = true;
      };
      const up = () => {
        window.removeEventListener("pointermove", move);
        window.removeEventListener("pointerup", up);
      };
      window.addEventListener("pointermove", move);
      window.addEventListener("pointerup", up);
    });

    n.addEventListener("dblclick", (e) => { e.stopPropagation(); editText(); });
  }

  function wireAll() {
    layer()?.querySelectorAll(".obj").forEach(wire);
  }

  /* ------------------------------------------------------------------ save */
  async function save() {
    try {
      const r = await fetch("/api/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: ctx.savePath, data: ctx.data }),
      });
      const j = await r.json();
      if (!j.ok) throw new Error(j.error);
      dirty = false;
      toast("Kaydedildi: " + ctx.savePath);
    } catch (err) {
      toast("Kaydedilemedi: " + err.message, true);
    }
  }

  const onKey = (e) => {
    if (!on || e.target.matches("input, textarea")) return;
    if (e.key === "Delete") { e.preventDefault(); removeSel(); }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") { e.preventDefault(); save(); }
  };
  document.addEventListener("keydown", onKey);

  return {
    toggle() {
      on = !on;
      deck.classList.toggle("editing", on);
      if (on) {
        editSlot.replaceChildren(bar);
        wireAll();
        toast("Düzenleme açık — nesne ekleyip sürükleyin, sonra Kaydet");
      } else {
        editSlot.replaceChildren();
        select(null);
        if (dirty) toast("Kaydedilmemiş değişiklik var (E ile geri dön, 💾 Kaydet)", true);
      }
    },
    isOn: () => on,
    rewire: wireAll,
  };
}
