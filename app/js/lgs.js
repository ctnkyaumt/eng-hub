/* ENG HUB - LGS section screen -----------------------------------------------
   Routes: #/lgs                 main LGS overview
           #/lgs/:category       specific category view with live search
--------------------------------------------------------------------------- */

import { getLgsSources } from "./store.js";
import { el, setCrumbs, toast } from "./ui.js";

const screen = document.getElementById("screen");

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
    placeholder: "Tüm LGS kaynaklarında ara (örnek, deneme, yıl, yazar, ünite)…",
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
    const q = searchBox.value.trim().toLocaleLowerCase("tr");
    if (!q) {
      contentContainer.style.display = "block";
      searchResultsList.style.display = "none";
      searchResultText.textContent = "";
      return;
    }

    contentContainer.style.display = "none";
    searchResultsList.style.display = "flex";

    const matches = allItems.filter((it) => {
      const txt = `${it.title} ${it.by || ""} ${it.desc || ""} ${it.categoryTitle || ""}`.toLocaleLowerCase("tr");
      return txt.includes(q);
    });

    searchResultText.textContent = `${matches.length} kaynak bulundu`;

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

  const listContainer = el("div", { class: "list" });
  const rows = items.map((it) => {
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
              it.desc || null,
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

  const searchBox = el("input", {
    type: "search",
    class: "resource-search",
    placeholder: "Bu kategoride ara (başlık, yazar, yıl, ünite)…",
    "aria-label": "Kategoride ara",
    style: "width: 100%; margin: 10px 0 6px;",
  });

  const searchResultText = el("p", { class: "resource-search-result", role: "status", "aria-live": "polite" });

  searchBox.addEventListener("input", () => {
    const q = searchBox.value.trim().toLocaleLowerCase("tr");
    let matches = 0;
    for (const { item, node } of rows) {
      const txt = `${item.title} ${item.by || ""} ${item.desc || ""}`.toLocaleLowerCase("tr");
      const visible = !q || txt.includes(q);
      node.hidden = !visible;
      if (visible) matches++;
    }
    searchResultText.textContent = q ? `${matches} kaynak bulundu` : "";
  });

  screen.replaceChildren(
    hero,
    actionButtons,
    el("section", { style: "display: flex; flex-direction: column; gap: 4px; margin-top: 18px;" }, [
      searchBox,
      searchResultText,
      listContainer,
    ])
  );
}
