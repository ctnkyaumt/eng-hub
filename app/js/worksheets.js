/* Worksheet screen: local files open in the machine's associated app --------- */
import { getUnit, getWorksheets, openLocal, unitPath } from "./store.js";
import { el, toast, setCrumbs } from "./ui.js";

const ICONS = { pdf: "📕", doc: "📘", docx: "📘", ppt: "📙", pptx: "📙", png: "🖼️", jpg: "🖼️", jpeg: "🖼️", zip: "🗜️" };

function human(bytes) {
  if (!bytes) return "";
  const u = ["B", "KB", "MB", "GB"];
  let i = 0, n = bytes;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(n < 10 && i ? 1 : 0)} ${u[i]}`;
}

export async function worksheetList(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const man = await getWorksheets(gid, uid);
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: `Ünite ${unit.no}`, hash: `#/${gid}/${uid}` },
    { label: "Çalışma Kâğıtları" },
  ]);

  const local = (man.items || []).filter((i) => i.file);
  const remote = (man.items || []).filter((i) => !i.file && i.link);

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · Ünite ${unit.no} · ${unit.title}` }),
    el("h1", { text: "Çalışma Kâğıtları" }),
    el("p", { text: local.length ? "Dosyaya tıklayın — bilgisayarın kendi programında açılır." : "" }),
  ]);

  const parts = [hero];

  if (!local.length && !remote.length) {
    parts.push(el("div", { class: "empty" }, [
      el("span", { class: "emoji", text: "📭" }),
      el("p", { text: "Bu ünite için çalışma kâğıdı bulunamadı." }),
      el("p", { text: "tools/fetch_worksheets.py çalıştırılarak indirilebilir." }),
    ]));
  }

  if (local.length) {
    parts.push(el("h2", { class: "section-title", text: `USB'de hazır (${local.length})` }));
    parts.push(el("div", { class: "list" }, local.map((it) => row(gid, uid, it))));
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

function row(gid, uid, it) {
  const rel = `${unitPath(gid, uid).slice(1)}/worksheets/${it.file}`;
  const ext = (it.file.split(".").pop() || "").toLowerCase();

  const open = async () => {
    try {
      await openLocal(rel);
      toast("Açılıyor: " + it.file);
    } catch (err) {
      // no desktop association (or headless) - fall back to the browser
      window.open("/" + rel, "_blank", "noopener");
    }
  };

  return el("div", { class: "row", onclick: open, role: "button", tabindex: "0",
                     onkeydown: (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } } }, [
    el("span", { class: "ic", text: ICONS[ext] || "📄" }),
    el("div", { class: "txt" }, [
      el("b", { text: it.title }),
      el("small", { text: [it.by && "Hazırlayan: " + it.by, human(it.size), ext.toUpperCase()].filter(Boolean).join(" · ") }),
    ]),
    el("button", {
      class: "btn", text: "Önizle",
      onclick: (e) => { e.stopPropagation(); window.open("/" + rel, "_blank", "noopener"); },
    }),
    el("span", { class: "go", text: "›" }),
  ]);
}
