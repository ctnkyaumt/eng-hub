/* Worksheets are always opened at their online source. */
import { getUnit, getWorksheets } from "./store.js";
import { el, setCrumbs } from "./ui.js";

export async function worksheetList(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const man = await getWorksheets(gid, uid);
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: `${unit.label || "Ünite"} ${unit.no}`, hash: `#/${gid}/${uid}` },
    { label: "Çalışma Kâğıtları" },
  ]);

  const remote = (man.items || []).filter((i) => i.link);

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unit.label || "Ünite"} ${unit.no} · ${unit.title}` }),
    el("h1", { text: "Çalışma Kâğıtları" }),
    el("p", { text: "Tüm çalışma kâğıtları kaynak sitede açılır — internet bağlantısı gerekir." }),
  ]);

  const parts = [hero];

  if (!remote.length) {
    parts.push(el("div", { class: "empty" }, [
      el("span", { class: "emoji", text: "📭" }),
      el("p", { text: "Bu ünite için çalışma kâğıdı bulunamadı." }),
    ]));
  }

  if (remote.length) {
    parts.push(el("h2", { class: "section-title", text: `İnternet gerekli (${remote.length})` }));
    parts.push(el("div", { class: "list" }, remote.map((it) =>
      el("button", { class: "row", onclick: () => window.open(it.link, "_blank", "noopener") }, [
        el("span", { class: "ic", text: "🌐" }),
        el("div", { class: "txt" }, [
          el("b", { text: it.title }),
          el("small", { text: it.by ? "Hazırlayan: " + it.by : "" }),
        ]),
        el("span", { class: "go", text: "↗" }),
      ])
    )));
  }

  screen.replaceChildren(...parts);
}
