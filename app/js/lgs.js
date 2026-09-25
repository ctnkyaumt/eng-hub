/* ENG HUB - LGS section screen -----------------------------------------------
   Routes: #/lgs                 main LGS overview
           #/lgs/:category       specific category view with live search & sections
--------------------------------------------------------------------------- */

import { getLgsSources } from "./store.js";
import { el, setCrumbs, toast } from "./ui.js";

const screen = document.getElementById("screen");

function normText(str) {
  return (str || "")
    .toLocaleLowerCase("tr")
    .replace(/i̇/g, "i")
    .replace(/ı/g, "i")
    .replace(/ğ/g, "g")
    .replace(/ü/g, "u")
    .replace(/ş/g, "s")
    .replace(/ö/g, "o")
    .replace(/ç/g, "c")
    .trim();
}

export async function lgsScreen(catId) {
  const data = await getLgsSources();
  const sources = data.sources || [];

  if (catId) {
    const category = sources.find((s) => s.id === catId);
    if (!category) {
      toast("Kategori bulunamadı.");
      location.hash = "#/lgs";
      return;
    }
    renderCategoryDetail(category, data);
  } else {
    renderLgsHome(data);
  }
}

function renderLgsHome(data) {
  setCrumbs([{ label: "Ana Menü", hash: "#/" }, { label: "LGS İngilizce" }]);

  const sources = data.sources || [];
  const ingSources = sources.filter((s) => s.provider === "ingilizceciyiz");
  const dersSources = sources.filter((s) => s.provider === "dersingilizce");

  const totalCount = data.counts?.total || sources.reduce((a, s) => a + (s.items?.length || 0), 0);
  const ingCount = data.counts?.ingilizceciyiz || ingSources.reduce((a, s) => a + (s.items?.length || 0), 0);
  const dersCount = data.counts?.dersingilizce || dersSources.reduce((a, s) => a + (s.items?.length || 0), 0);

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: "ÖZEL BÖLÜM · LGS HAZIRLIK" }),
    el("h1", { text: "🎯 LGS İngilizce Kaynak Merkezi" }),
    el("p", {
      text: "ingilizceciyiz.com ve dersingilizce.org çıkmış sorular, MEB örnek soruları, denemeler ve çalışma kâğıtları · İnternet gerekli",
    }),
    el("div", { class: "badge-row", style: "justify-content: center; margin-top: 14px;" }, [
      el("span", { class: "badge on", text: `Toplam ${totalCount} kaynak` }),
      el("span", { class: "badge on", text: `ingilizceciyiz (${ingCount})` }),
      el("span", { class: "badge on", text: `dersingilizce (${dersCount})` }),
      el("span", { class: "badge", text: "İnternet gerekli" }),
    ]),
  ]);

  // Quick external source links bar
  const sourceHubsBar = el("div", { class: "lgs-hubs-bar" }, [
    el("span", { class: "lgs-hubs-title", text: "Kaynak Sayfaları:" }),
    el("a", {
      href: "https://www.ingilizceciyiz.com/lgs-ingilizce-ornek-sorular/",
      target: "_blank",
      rel: "noopener",
      class: "btn lgs-hub-btn",
      text: "📝 ingilizceciyiz Örnek Sorular ↗",
    }),
    el("a", {
      href: "https://www.ingilizceciyiz.com/lgs-ingilizce-deneme-sinavlari/",
      target: "_blank",
      rel: "noopener",
      class: "btn lgs-hub-btn",
      text: "📑 ingilizceciyiz Denemeler ↗",
    }),
    el("a", {
      href: "https://www.ingilizceciyiz.com/lgs-ingilizce-sorulari/",
      target: "_blank",
      rel: "noopener",
      class: "btn lgs-hub-btn",
      text: "🏆 ingilizceciyiz Çıkmış Sorular ↗",
    }),
    el("a", {
      href: "https://www.dersingilizce.org/lgsfiles",
      target: "_blank",
      rel: "noopener",
      class: "btn lgs-hub-btn",
      text: "📂 dersingilizce.org/lgsfiles ↗",
    }),
  ]);

  // Prepare all items for global search
  const allItems = [];
  sources.forEach((s) => {
    (s.items || []).forEach((it) => {
      allItems.push({ ...it, categoryTitle: s.title, categoryEmoji: s.emoji });
    });
  });

  const searchBox = el("input", {
    type: "search",
    class: "resource-search",
    placeholder: "Tüm LGS kaynaklarında ara (örnek, sarmal, deneme, yıl, ünite)…",
    "aria-label": "LGS kaynaklarında ara",
    style: "width: 100%; margin: 10px 0 6px;",
  });

  const searchResultText = el("p", { class: "resource-search-result", role: "status", "aria-live": "polite" });
  const searchResultsList = el("div", { class: "list", style: "margin-top: 10px; display: none;" });

  const renderCard = (s, i) =>
    el(
      "button",
      {
        class: "card folder-card lgs-folder-card",
        style: `animation-delay: ${i * 45}ms`,
        onclick: () => {
          location.hash = `#/lgs/${s.id}`;
        },
      },
      [
        el("span", { class: "glow" }),
        el("span", { class: "emoji", text: s.emoji || "📁" }),
        el("h3", { text: s.title }),
        el("p", { text: s.subtitle }),
        el("div", { class: "badge-row" }, [
          el("span", { class: "badge on", text: `${s.items?.length || 0} kaynak` }),
          el("span", { class: "badge", text: s.providerTitle || s.provider }),
        ]),
      ]
    );

  const ingGrid = el("div", { class: "grid g-3" }, ingSources.map(renderCard));
  const dersGrid = el("div", { class: "grid g-3" }, dersSources.map(renderCard));

  const contentContainer = el("div", {}, [
    el("div", { class: "lgs-group-header" }, [
      el("h2", { class: "section-title", text: `ingilizceciyiz.com Kaynakları (${ingCount} kaynak)` }),
    ]),
    ingGrid,
    el("div", { class: "lgs-group-header", style: "margin-top: 32px;" }, [
      el("h2", { class: "section-title", text: `dersingilizce.org Kaynakları · lgsfiles (${dersCount} kaynak)` }),
    ]),
    dersGrid,
  ]);

  searchBox.addEventListener("input", () => {
    const q = normText(searchBox.value);
    if (!q) {
      contentContainer.style.display = "block";
      searchResultsList.style.display = "none";
      searchResultText.textContent = "";
      return;
    }

    contentContainer.style.display = "none";
    searchResultsList.style.display = "flex";

    const matches = allItems.filter((it) => {
      const txt = normText(`${it.title} ${it.by || ""} ${it.desc || ""} ${it.section || ""} ${it.subSection || ""} ${it.categoryTitle || ""}`);
      return txt.includes(q);
    });

    searchResultText.textContent = matches.length > 0 ? `${matches.length} kaynak bulundu` : "Eşleşen kaynak bulunamadı.";

    if (!matches.length) {
      searchResultsList.replaceChildren(
        el("div", { class: "empty" }, [
          el("span", { class: "emoji", text: "🔍" }),
          el("p", { text: `"${searchBox.value}" ile eşleşen LGS kaynağı bulunamadı.` }),
        ])
      );
    } else {
      searchResultsList.replaceChildren(
        ...matches.map((it) =>
          el(
            "button",
            {
              class: "row",
              onclick: () => window.open(it.link, "_blank", "noopener"),
            },
            [
              el("span", { class: "ic", text: it.categoryEmoji || "📄" }),
              el("div", { class: "txt" }, [
                el("b", { text: it.title }),
                el("small", {
                  text: [
                    it.categoryTitle,
                    it.section && it.section !== it.categoryTitle ? it.section : null,
                    it.by ? (it.by.startsWith("Hazırlayan:") ? it.by : "Hazırlayan: " + it.by) : null,
                    it.desc || null,
                  ]
                    .filter(Boolean)
                    .join(" · "),
                }),
              ]),
              el("span", { class: "go", text: "↗" }),
            ]
          )
        )
      );
    }
  });

  screen.replaceChildren(
    hero,
    sourceHubsBar,
    el("section", { style: "display: flex; flex-direction: column; gap: 4px; margin-bottom: 24px;" }, [
      searchBox,
      searchResultText,
      searchResultsList,
    ]),
    contentContainer
  );
}

function renderCategoryDetail(category, data) {
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: "LGS İngilizce", hash: "#/lgs" },
    { label: category.title },
  ]);

  const items = category.items || [];
  const count = items.length;

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${category.providerTitle || category.provider} · LGS Kaynakları` }),
    el("h1", { text: `${category.emoji || "📁"} ${category.title}` }),
    el("p", { text: `${category.subtitle} · ${count} kaynak · İnternet gerekli` }),
  ]);

  const actionButtons = el("div", { class: "lgs-action-bar" }, [
    el("button", {
      class: "btn primary",
      onclick: () => window.open(category.sourceUrl, "_blank", "noopener"),
      text: `🌐 Kaynak Sayfasını Aç (${category.providerTitle || "Web"}) ↗`,
    }),
    ...(category.hubUrl && category.hubUrl !== category.sourceUrl
      ? [
          el("button", {
            class: "btn",
            onclick: () => window.open(category.hubUrl, "_blank", "noopener"),
            text: "📂 dersingilizce.org/lgsfiles ↗",
          }),
        ]
      : []),
    el("button", {
      class: "btn",
      onclick: () => {
        location.hash = "#/lgs";
      },
      text: "← Tüm LGS Kategorileri",
    }),
  ]);

  // Group items by section -> subsection
  const sectionMap = new Map();
  for (const it of items) {
    const secName = it.section || "Genel Kaynaklar";
    const subName = it.subSection || secName;
    if (!sectionMap.has(secName)) {
      sectionMap.set(secName, new Map());
    }
    const subMap = sectionMap.get(secName);
    if (!subMap.has(subName)) {
      subMap.set(subName, []);
    }
    subMap.get(subName).push(it);
  }

  const uniqueSections = Array.from(sectionMap.keys());
  let activeSectionFilter = "all";

  // Build DOM structures for sections and rows
  const sectionBlocks = [];

  for (const [secName, subMap] of sectionMap.entries()) {
    const secContainer = el("div", { class: "lgs-section-block", "data-section": secName });
    const secHeader = el("h2", { class: "lgs-section-heading", text: secName });
    secContainer.append(secHeader);

    const subBlocks = [];

    for (const [subName, subItems] of subMap.entries()) {
      const subContainer = el("div", { class: "lgs-sub-block" });
      // Only show sub-heading if it adds detail beyond the main section heading
      if (subName && subName !== secName && subMap.size > 1) {
        subContainer.append(el("h3", { class: "lgs-subsection-heading", text: subName }));
      }

      const listContainer = el("div", { class: "list" });
      const rows = subItems.map((it) => {
        const isOnlineTest = category.id === "dersingilizce-online" || it.link.includes("wordwall");
        const isExam = /deneme|sınav|sorular/i.test(it.title);
        const icon = isOnlineTest ? "🎮" : isExam ? "📝" : "📄";

        const node = el(
          "button",
          {
            class: "row",
            onclick: () => window.open(it.link, "_blank", "noopener"),
          },
          [
            el("span", { class: "ic", text: icon }),
            el("div", { class: "txt" }, [
              el("b", { text: it.title }),
              el("small", {
                text: [
                  it.by ? (it.by.startsWith("Hazırlayan:") ? it.by : "Hazırlayan: " + it.by) : null,
                  it.desc && it.desc !== secName ? it.desc : null,
                ]
                  .filter(Boolean)
                  .join(" · "),
              }),
            ]),
            el("span", { class: "go", text: "↗" }),
          ]
        );
        return { item: it, node };
      });

      listContainer.append(...rows.map((r) => r.node));
      subContainer.append(listContainer);
      secContainer.append(subContainer);

      subBlocks.push({ name: subName, container: subContainer, rows });
    }

    sectionBlocks.push({ name: secName, container: secContainer, subBlocks });
  }

  // Filter Pills (if more than 1 section)
  let filterPillsContainer = null;
  if (uniqueSections.length > 1) {
    const pillButtons = [];
    const allPill = el("button", {
      class: "lgs-pill active",
      text: `Tümü (${count})`,
      onclick: () => {
        activeSectionFilter = "all";
        pillButtons.forEach((b) => b.classList.remove("active"));
        allPill.classList.add("active");
        updateVisibility();
      },
    });
    pillButtons.push(allPill);

    for (const secName of uniqueSections) {
      const secCount = items.filter((it) => (it.section || "Genel Kaynaklar") === secName).length;
      const pill = el("button", {
        class: "lgs-pill",
        text: `${secName} (${secCount})`,
        onclick: () => {
          activeSectionFilter = secName;
          pillButtons.forEach((b) => b.classList.remove("active"));
          pill.classList.add("active");
          updateVisibility();
        },
      });
      pillButtons.push(pill);
    }

    filterPillsContainer = el("div", { class: "lgs-filter-pills" }, pillButtons);
  }

  const searchBox = el("input", {
    type: "search",
    class: "resource-search",
    placeholder: "Bu kategoride ara (başlık, yazar, yıl, sarmal, ünite)…",
    "aria-label": "Kategoride ara",
    style: "width: 100%; margin: 10px 0 6px;",
  });

  const searchResultText = el("p", { class: "resource-search-result", role: "status", "aria-live": "polite" });

  function updateVisibility() {
    const q = normText(searchBox.value);
    let totalVisible = 0;

    for (const secBlock of sectionBlocks) {
      let secVisible = 0;
      const pillMatch = activeSectionFilter === "all" || secBlock.name === activeSectionFilter;

      for (const subBlock of secBlock.subBlocks) {
        let subVisible = 0;
        for (const { item, node } of subBlock.rows) {
          const txt = normText(`${item.title} ${item.by || ""} ${item.desc || ""} ${item.section || ""} ${item.subSection || ""}`);
          const queryMatch = !q || txt.includes(q);
          const visible = pillMatch && queryMatch;

          node.hidden = !visible;
          node.style.display = visible ? "" : "none";
          node.classList.toggle("hidden", !visible);

          if (visible) {
            subVisible++;
            totalVisible++;
          }
        }

        const isSubVis = subVisible > 0;
        subBlock.container.hidden = !isSubVis;
        subBlock.container.style.display = isSubVis ? "" : "none";
        subBlock.container.classList.toggle("hidden", !isSubVis);

        if (isSubVis) secVisible += subVisible;
      }

      const isSecVis = secVisible > 0;
      secBlock.container.hidden = !isSecVis;
      secBlock.container.style.display = isSecVis ? "" : "none";
      secBlock.container.classList.toggle("hidden", !isSecVis);
    }

    if (q) {
      searchResultText.textContent = totalVisible > 0 ? `${totalVisible} kaynak bulundu` : "Eşleşen kaynak bulunamadı.";
    } else if (activeSectionFilter !== "all") {
      searchResultText.textContent = `${totalVisible} kaynak gösteriliyor`;
    } else {
      searchResultText.textContent = "";
    }
  }

  searchBox.addEventListener("input", updateVisibility);

  const sectionsWrapper = el("div", { class: "lgs-sections-wrapper" }, sectionBlocks.map((b) => b.container));

  screen.replaceChildren(
    hero,
    actionButtons,
    el("section", { style: "display: flex; flex-direction: column; gap: 4px; margin-top: 18px;" }, [
      searchBox,
      ...(filterPillsContainer ? [filterPillsContainer] : []),
      searchResultText,
      sectionsWrapper,
    ])
  );
}
