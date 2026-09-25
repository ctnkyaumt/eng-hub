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
  const dersingilizceItems = man.dersingilizce || [];
  const dersingilizceCount = dersingilizceItems.length;
  const mebOdsgmItems = man.mebOdsgm || [];
  const mebOdsgmCount = mebOdsgmItems.length;
  const isMebGrade = gid === "g7" || gid === "g8";

  const isLocal = (it) => Boolean(it.file && !it.link);
  const hasLocal = items.some(isLocal);
  const hasOnline =
    items.some((it) => !isLocal(it)) ||
    ingilizcecinCount > 0 ||
    dersingilizceCount > 0 ||
    (isMebGrade && mebOdsgmCount > 0);

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

  // Online worksheet folders
  parts.push(el("h2", { class: "section-title", text: "Çevrimiçi Çalışma Kâğıdı Klasörleri" }));
  const folderCards = [
    el("button", {
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
    ]),
    el("button", {
      class: "card folder-card",
      style: "animation-delay: 140ms",
      onclick: () => {
        location.hash = `#/${gid}/${uid}/calisma/dersingilizce`;
      },
    }, [
      el("span", { class: "glow" }),
      el("span", { class: "emoji", text: "📁" }),
      el("h3", { text: "dersingilizce" }),
      el("p", { text: dersingilizceCount ? "dersingilizce.org PDF çalışma kâğıtları · İnternet gerekli" : "Bu ünite için henüz kaynak eklenmedi" }),
      el("div", { class: "badge-row" }, [
        el("span", { class: "badge " + (dersingilizceCount ? "on" : "off"), text: `${dersingilizceCount} kaynak` }),
      ]),
    ]),
  ];

  if (isMebGrade) {
    folderCards.push(el("button", {
      class: "card folder-card",
      style: "animation-delay: 190ms",
      onclick: () => {
        location.hash = `#/${gid}/${uid}/calisma/meb-odsgm`;
      },
    }, [
      el("span", { class: "glow" }),
      el("span", { class: "emoji", text: "📁" }),
      el("h3", { text: "MEB ÖDSGM" }),
      el("p", { text: mebOdsgmCount ? "MEB ÖDSGM Beceri Temelli ve Kazanım Testleri · İnternet gerekli" : "Bu ünite için henüz kaynak eklenmedi" }),
      el("div", { class: "badge-row" }, [
        el("span", { class: "badge " + (mebOdsgmCount ? "on" : "off"), text: `${mebOdsgmCount} kaynak` }),
      ]),
    ]));
  }

  parts.push(el("div", { class: "grid g-3" }, folderCards));

  // Other online worksheets / tests
  renderList("Çalışma Kâğıtları", worksheets.filter((it) => !isLocal(it)), "📄", false);
  renderList("Testler ve Quizler", quizzes.filter((it) => !isLocal(it)), "📝", false);

  if (!items.length && !ingilizcecinCount && !dersingilizceCount && (!isMebGrade || !mebOdsgmCount)) {
    parts.push(el("div", { class: "empty" }, [
      el("span", { class: "emoji", text: "📭" }),
      el("p", { text: "Bu ünite için çalışma kâğıdı veya test bulunamadı." }),
    ]));
  }

  screen.replaceChildren(...parts);
}

async function renderWorksheetFolderPicker(gid, uid, screen, {
  folderName,
  sourceKey,
  kickerType,
  badgeSubtitle,
  emptyMessage,
}) {
  const { grade, unit } = await getUnit(gid, uid);
  const unitLabel = unit.no ? `${unit.label || "Ünite"} ${unit.no}` : (unit.label || "Revizyon");
  const man = await getWorksheets(gid, uid);
  const items = man[sourceKey] || [];
  const count = items.length;

  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: unitLabel, hash: `#/${gid}/${uid}` },
    { label: "Çalışma Kâğıtları", hash: `#/${gid}/${uid}/calisma` },
    { label: folderName },
  ]);

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unitLabel} · ${kickerType}` }),
    el("h1", { text: `📁 ${folderName}` }),
    el("p", { text: count
      ? `${count} ${badgeSubtitle}`
      : emptyMessage }),
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
        node.style.display = visible ? "" : "none";
        node.classList.toggle("hidden", !visible);
        if (visible) matches++;
      }
      result.textContent = query ? `${matches} kaynak bulundu` : "";
    });

    parts.push(el("section", { style: "display:flex; flex-direction:column; gap:8px;" }, [input, result, listContainer]));
  } else {
    parts.push(
      el("div", { class: "empty" }, [
        el("span", { class: "emoji", text: "📁" }),
        el("p", { text: emptyMessage }),
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

export async function ingilizcecinWorksheetPicker(gid, uid, screen) {
  return renderWorksheetFolderPicker(gid, uid, screen, {
    folderName: "ingilizcecin",
    sourceKey: "ingilizcecin",
    kickerType: "Çalışma Kâğıtları",
    badgeSubtitle: "çalışma kâğıdı ve test · ingilizcecin.com (2020+) · İnternet gerekli",
    emptyMessage: "Bu ünite için ingilizcecin kaynağı bulunamadı.",
  });
}

export async function dersingilizceWorksheetPicker(gid, uid, screen) {
  return renderWorksheetFolderPicker(gid, uid, screen, {
    folderName: "dersingilizce",
    sourceKey: "dersingilizce",
    kickerType: "Çalışma Kâğıtları",
    badgeSubtitle: "PDF çalışma kâğıdı · dersingilizce.org · İnternet gerekli",
    emptyMessage: "Bu ünite için dersingilizce çalışma kâğıdı bulunamadı.",
  });
}

export async function mebOdsgmWorksheetPicker(gid, uid, screen) {
  if (gid !== "g7" && gid !== "g8") {
    location.hash = `#/${gid}/${uid}/calisma`;
    return;
  }
  return renderWorksheetFolderPicker(gid, uid, screen, {
    folderName: "MEB ÖDSGM",
    sourceKey: "mebOdsgm",
    kickerType: "MEB Testleri",
    badgeSubtitle: "resmi MEB ÖDSGM testi ve soru fasikülü · İnternet gerekli",
    emptyMessage: "Bu ünite için MEB ÖDSGM kaynağı bulunamadı.",
  });
}

