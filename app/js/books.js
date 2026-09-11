/* Kitap sunumları — the source's book-presentation collection ---------------
   These live inside eltarena's own viewer, so they open online. The titles are
   listed offline so the teacher can see what a unit offers before connecting.
--------------------------------------------------------------------------- */
import { getUnit, getSites } from "./store.js";
import { el, mount, setCrumbs } from "./ui.js";

const SOURCE = "https://eltarena.com/materials";

export async function bookList(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const unitLabel = unit.no ? `${unit.label || "Ünite"} ${unit.no}` : (unit.label || "Revizyon");
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: unitLabel, hash: `#/${gid}/${uid}` },
    { label: "Kitap Sunumları" },
  ]);

  const all = await fetch("/app/data/books.json", { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : {}))
    .catch(() => ({}));
  const items = all[`${gid}/${uid}`] || [];
  const mirrored = await getSites(gid, uid, "presentation");

  const pageUrl = unit.sourceUnitId
    ? `${SOURCE}?grade=${grade.no}&unit=${unit.sourceUnitId}&type=book-presentation`
    : SOURCE;

  const parts = [
    el("div", { class: "hero" }, [
      el("span", { class: "kicker", text: `${grade.title} · ${unitLabel} · ${unit.title}` }),
      el("h1", { text: "Kitap Sunumları" }),
      el("p", { text: "Ders kitabı ve çalışma kitabı sunumları — kaynak sitede açılır (internet gerekir)." }),
    ]),
    el("div", { style: "text-align:center;margin-bottom:26px" }, [
      el("button", {
        class: "btn primary big", text: "🌐 Kaynak sayfasını aç",
        onclick: () => window.open(pageUrl, "_blank", "noopener"),
      }),
    ]),
  ];

  if (mirrored.length) {
    parts.push(el("h2", { class: "section-title", text: `USB'de hazır (${mirrored.length})` }));
    parts.push(el("div", { class: "list" }, mirrored.map((m) =>
      el("button", { class: "row", onclick: () => window.open(m.url, "_blank", "noopener") }, [
        el("span", { class: "ic", text: "📺" }),
        el("div", { class: "txt" }, [
          el("b", { text: m.title }),
          el("small", { text: m.by ? "Hazırlayan: " + m.by : "İnternet gerekmez" }),
        ]),
        el("span", { class: "go", text: "▶" }),
      ])
    )));
  }

  if (items.length) {
    parts.push(el("h2", { class: "section-title", text: `Kaynaktaki sunumlar (${items.length})` }));
    parts.push(el("div", { class: "list" }, items.map((it) => {
      const link = it.link && it.link.startsWith("http") ? it.link : pageUrl;
      return el("button", { class: "row", onclick: () => window.open(link, "_blank", "noopener") }, [
        el("span", { class: "ic", text: "📚" }),
        el("div", { class: "txt" }, [
          el("b", { text: it.title }),
          el("small", { text: it.by ? "Hazırlayan: " + it.by : "eltarena.com" }),
        ]),
        el("span", { class: "go", text: "↗" }),
      ]);
    })));
  }

  mount(screen, ...parts);
}
