/* Original worksheets are local; imported resources open at their source. */
import { getUnit, getWorksheets, unitPath } from "./store.js";
import { el, setCrumbs } from "./ui.js";

export async function worksheetList(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const unitLabel = unit.no ? `${unit.label || "Ünite"} ${unit.no}` : (unit.label || "Revizyon");
  const man = await getWorksheets(gid, uid);
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: unitLabel, hash: `#/${gid}/${uid}` },
    { label: "Çalışma Kâğıtları" },
  ]);

  const local = (man.items || []).filter((i) => i.authored && i.file);
  const remote = (man.items || []).filter((i) => i.link && !local.includes(i));

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unitLabel} · ${unit.title}` }),
    el("h1", { text: "Çalışma Kâğıtları" }),
    el("p", { text: local.length
      ? "Özgün çalışma kâğıtlarını açıp yazdırabilirsiniz. Öğretmen anahtarları ayrı dosyadadır; internet gerekmez."
      : "Tüm çalışma kâğıtları kaynak sitede açılır — internet bağlantısı gerekir." }),
  ]);

  const parts = [hero];

  if (!remote.length && !local.length) {
    parts.push(el("div", { class: "empty" }, [
      el("span", { class: "emoji", text: "📭" }),
      el("p", { text: "Bu ünite için çalışma kâğıdı bulunamadı." }),
    ]));
  }

  if (local.length) {
    parts.push(el("h2", { class: "section-title", text: `Özgün materyaller · Çevrimdışı (${local.length})` }));
    parts.push(el("div", { class: "list" }, local.map((it) =>
      el("button", { class: "row", onclick: () => window.open(
        `${unitPath(gid, uid)}/worksheets/${encodeURIComponent(it.file)}`, "_blank", "noopener") }, [
        el("span", { class: "ic", text: "📄" }),
        el("div", { class: "txt" }, [
          el("b", { text: it.title }),
          el("small", { text: [it.desc, it.by].filter(Boolean).join(" · ") }),
        ]),
        el("span", { class: "go", text: "↗" }),
      ])
    )));
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
