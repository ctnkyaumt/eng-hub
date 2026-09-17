/* Authored worksheets open locally; linked resources require internet. */

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
    { label: "Çalışma Kâğıtları ve Testler" },
  ]);

  const items = man.items || [];
  const ingilizcecinItems = man.ingilizcecin || [];
  const ingilizcecinCount = ingilizcecinItems.length;
  const isLocal = (it) => Boolean(it.file && !it.link);
  const hasLocal = items.some(isLocal);
  const hasOnline = items.some((it) => !isLocal(it)) || ingilizcecinCount > 0;

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unitLabel} · ${unit.title}` }),
    el("h1", { text: "Çalışma Kâğıtları ve Testler" }),
    el("p", { text: hasLocal
      ? (hasOnline ? "Yerel PDF'ler çevrimdışı açılır ve yazdırılır. Kaynak bağlantıları için internet gerekir." : "Bu PDF'ler çevrimdışı açılır ve yazdırılır.")
      : "Çalışma kâğıdı ve test bağlantıları için internet gerekir." }),
  ]);

  const parts = [hero];

  const isQuiz = (it) => it.type === "quiz" || (!it.type && /\b(test|quiz|deneme)\b/i.test(it.title || ""));
  const quizzes = items.filter(isQuiz);
  const worksheets = items.filter((it) => !isQuiz(it));

  const openResource = (it) => {
    if (it.link) {
      window.open(it.link, "_blank", "noopener");
    } else if (it.file) {
      window.open(`${unitPath(gid, uid)}/worksheets/${encodeURIComponent(it.file)}`, "_blank", "noopener");
    }
  };

  const renderList = (title, list, icon, local) => {
    if (!list.length) return;
    parts.push(el("h2", { class: "section-title", text: `${title} · ${local ? "Çevrimdışı" : "İnternet gerekli"} (${list.length})` }));
    parts.push(el("div", { class: "list" }, list.map((it) =>
      el("button", { class: "row", onclick: () => openResource(it) }, [
        el("span", { class: "ic", text: icon }),
        el("div", { class: "txt" }, [
          el("b", { text: it.title }),
          el("small", { text: [it.desc, it.by ? (it.by.startsWith("Hazırlayan:") ? it.by : "Hazırlayan: " + it.by) : null].filter(Boolean).join(" · ") }),
        ]),
        el("span", { class: "go", text: "↗" }),
      ])
    )));
  };

  // Local worksheets / tests
  renderList("Çalışma Kâğıtları", worksheets.filter(isLocal), "📄", true);
  renderList("Testler ve Quizler", quizzes.filter(isLocal), "📝", true);

  // Online worksheet folder for ingilizcecin (matches sumeyyeogultekin in games)
  parts.push(el("h2", { class: "section-title", text: "Çevrimiçi Çalışma Kâğıdı Klasörleri" }));
  const folderCard = el("button", {
    class: "card folder-card",
    style: "animation-delay: 90ms",
    onclick: () => {
      location.hash = `#/${gid}/${uid}/calisma/ingilizcecin`;
    },
  }, [
    el("span", { class: "glow" }),
    el("span", { class: "emoji", text: "📁" }),
    el("h3", { text: "ingilizcecin" }),
    el("p", { text: ingilizcecinCount ? "ingilizcecin.com çalışma kâğıtları ve testleri · İnternet gerekli" : "Bu ünite için henüz kaynak eklenmedi" }),
    el("div", { class: "badge-row" }, [
      el("span", { class: "badge " + (ingilizcecinCount ? "on" : "off"), text: `${ingilizcecinCount} kaynak` }),
    ]),
  ]);
  parts.push(el("div", { class: "grid g-3" }, [folderCard]));

  // Other online worksheets / tests
  renderList("Çalışma Kâğıtları", worksheets.filter((it) => !isLocal(it)), "📄", false);
  renderList("Testler ve Quizler", quizzes.filter((it) => !isLocal(it)), "📝", false);

  if (!items.length && !ingilizcecinCount) {
    parts.push(el("div", { class: "empty" }, [
      el("span", { class: "emoji", text: "📭" }),
      el("p", { text: "Bu ünite için çalışma kâğıdı veya test bulunamadı." }),
    ]));
  }

  screen.replaceChildren(...parts);
}

export async function ingilizcecinWorksheetPicker(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const unitLabel = unit.no ? `${unit.label || "Ünite"} ${unit.no}` : (unit.label || "Revizyon");
  const man = await getWorksheets(gid, uid);
  const items = man.ingilizcecin || [];
  const count = items.length;

  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: unitLabel, hash: `#/${gid}/${uid}` },
    { label: "Çalışma Kâğıtları", hash: `#/${gid}/${uid}/calisma` },
    { label: "ingilizcecin" },
  ]);

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unitLabel} · Çalışma Kâğıtları` }),
    el("h1", { text: "📁 ingilizcecin" }),
    el("p", { text: count
      ? `${count} çalışma kâğıdı ve test · ingilizcecin.com (2020+) · İnternet gerekli`
      : "Bu ünite için ingilizcecin kaynağı bulunamadı." }),
  ]);

  const parts = [hero];

  if (count > 0) {
    const listContainer = el("div", { class: "list" });
    const cards = items.map((it) => {
      const row = el("button", { class: "row", onclick: () => window.open(it.link, "_blank", "noopener") }, [
        el("span", { class: "ic", text: "📄" }),
        el("div", { class: "txt" }, [
          el("b", { text: it.title }),
          el("small", {
            text: [
              it.date ? `📅 ${it.date}` : null,
              it.by ? (it.by.startsWith("Hazırlayan:") ? it.by : "Hazırlayan: " + it.by) : null,
              it.desc || null,
            ].filter(Boolean).join(" · "),
          }),
        ]),
        el("span", { class: "go", text: "↗" }),
      ]);
      return { item: it, node: row };
    });

    listContainer.append(...cards.map((c) => c.node));

    const result = el("p", { class: "resource-search-result", role: "status", "aria-live": "polite" });
    const input = el("input", {
      type: "search",
      class: "resource-search",
      placeholder: "Çalışma kâğıdı, test veya yazar ara…",
      "aria-label": "Çalışma kâğıdı ara",
    });
    input.addEventListener("input", () => {
      const query = input.value.trim().toLocaleLowerCase("tr");
      let matches = 0;
      for (const { item, node } of cards) {
        const text = `${item.title} ${item.by || ""} ${item.desc || ""} ${item.date || ""}`.toLocaleLowerCase("tr");
        const visible = text.includes(query);
        node.hidden = !visible;
        if (visible) matches++;
      }
      result.textContent = query ? `${matches} kaynak bulundu` : "";
    });

    parts.push(el("section", { style: "display:flex; flex-direction:column; gap:8px;" }, [input, result, listContainer]));
  } else {
    parts.push(
      el("div", { class: "empty" }, [
        el("span", { class: "emoji", text: "📁" }),
        el("p", { text: "Bu ünitede ingilizcecin kaynağı henüz bulunmuyor." }),
        el("button", {
          class: "btn",
          style: "margin-top: 14px",
          onclick: () => { location.hash = `#/${gid}/${uid}/calisma`; },
          text: "← Çalışma Kâğıtları'na Dön",
        }),
      ])
    );
  }

  screen.replaceChildren(...parts);
}

