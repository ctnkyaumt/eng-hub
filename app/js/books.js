/* Kitap sunumları — the source's book-presentation collection ---------------
   These live inside eltarena's own viewer, so they open online. The titles are
   listed offline so the teacher can see what a unit offers before connecting.
--------------------------------------------------------------------------- */
import { getUnit, getSites } from "./store.js";
import { el, mount, setCrumbs } from "./ui.js";

const SOURCE = "https://eltarena.com/materials";

function renderBookCard(it, fallbackUrl, isMirrored = false) {
  const link = it.link && it.link.startsWith("http") ? it.link : (it.url || fallbackUrl);
  const openBook = () => window.open(link, "_blank", "noopener");

  const thumbChildren = [];
  const cover = it.coverImage;

  if (cover) {
    const blurImg = el("img", {
      class: "book-thumb-blur absolute inset-0 h-full w-full scale-110 object-cover opacity-25 blur-2xl",
      src: cover,
      alt: "",
      "aria-hidden": "true",
      loading: "lazy",
    });
    const gradient = el("div", {
      class: "book-thumb-gradient absolute inset-0 bg-gradient-to-b from-white/20 via-transparent to-[#2f7fed]/10",
    });
    const mainImg = el("img", {
      class: "book-cover-img relative z-[1] h-full w-full object-cover object-top transition-transform duration-300 group-hover:scale-[1.03] motion-reduce:transition-none motion-reduce:group-hover:scale-100",
      src: cover,
      alt: it.title || "Kitap Sunumu",
      loading: "lazy",
    });

    mainImg.addEventListener("error", () => {
      blurImg.remove();
      gradient.remove();
      mainImg.replaceWith(
        el("div", { class: "book-thumb-fallback" }, [
          el("span", { class: "book-fallback-ic", text: isMirrored ? "📺" : "📚" }),
          el("span", { class: "book-fallback-txt", text: "Kapak görseli yok" }),
        ])
      );
    });

    thumbChildren.push(blurImg, gradient, mainImg);
  } else {
    thumbChildren.push(
      el("div", { class: "book-thumb-fallback" }, [
        el("span", { class: "book-fallback-ic", text: isMirrored ? "📺" : "📚" }),
        el("span", { class: "book-fallback-txt", text: "Kapak görseli yok" }),
      ])
    );
  }

  thumbChildren.push(
    el("span", {
      class: "book-badge-type absolute left-2.5 top-2.5 z-[2] rounded-full bg-white/90 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-[#1a5fc4] shadow-sm backdrop-blur-sm sm:text-xs",
      text: isMirrored ? "USB Sunum" : "Kitap Sunumu",
    })
  );

  thumbChildren.push(
    el("span", {
      class: `book-badge-online ${isMirrored ? "book-badge-usb" : ""} absolute bottom-3 right-3 z-[2] inline-flex items-center gap-1 rounded-full bg-[#f5a623] px-2.5 py-1 text-[11px] font-semibold text-white shadow-sm sm:text-xs`,
      text: isMirrored ? "📺 USB" : "🌐 ONLINE",
    })
  );

  const thumbBtn = el(
    "button",
    {
      type: "button",
      class: "book-thumb relative aspect-[3/4] w-full overflow-hidden focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2f7fed] focus-visible:ring-offset-2 cursor-pointer",
      "aria-label": `${it.title} online aç`,
      onclick: openBook,
    },
    thumbChildren
  );

  const bodyChildren = [
    el("h3", { class: "book-card-title", text: it.title, title: it.title, onclick: openBook }),
  ];
  if (it.desc) {
    bodyChildren.push(el("p", { class: "book-card-desc", text: it.desc, title: it.desc }));
  }
  bodyChildren.push(
    el("div", { class: "book-card-meta" }, [
      el("small", { text: it.by ? `Hazırlayan: ${it.by}` : (isMirrored ? "İnternet gerekmez" : "eltarena.com") }),
    ]),
    el("div", { class: "book-card-actions" }, [
      el("button", {
        type: "button",
        class: "btn primary book-open-btn",
        text: isMirrored ? "▶ AÇ" : "🌐 ONLINE AÇ",
        onclick: openBook,
      }),
    ])
  );

  return el(
    "article",
    {
      class: "book-card card group flex h-full w-full flex-col overflow-hidden rounded-2xl transition-transform duration-200 hover:-translate-y-1 motion-reduce:transition-none motion-reduce:hover:translate-y-0",
    },
    [thumbBtn, el("div", { class: "book-card-body" }, bodyChildren)]
  );
}

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
      el("p", { text: "Ders kitabı ve çalışma kitabı sunumları — kapaklarına tıklayarak kaynak sitede açabilirsiniz (internet gerekir)." }),
    ]),
    el("div", { style: "text-align:center;margin-bottom:26px" }, [
      el("button", {
        class: "btn primary big", text: "🌐 Kaynak sayfasını aç",
        onclick: () => window.open(pageUrl, "_blank", "noopener"),
      }),
    ]),
  ];

  if (mirrored.length) {
    parts.push(el("section", { class: "book-section" }, [
      el("h2", { class: "section-title", text: `USB'de hazır (${mirrored.length})` }),
      el("div", { class: "book-grid grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5" },
        mirrored.map((m) => renderBookCard(m, pageUrl, true))
      ),
    ]));
  }

  if (items.length) {
    parts.push(el("section", { class: "book-section" }, [
      el("h2", { class: "section-title", text: `Kaynaktaki sunumlar (${items.length})` }),
      el("div", { class: "book-grid grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5" },
        items.map((it) => renderBookCard(it, pageUrl, false))
      ),
    ]));
  }

  if (!mirrored.length && !items.length) {
    parts.push(el("div", { class: "empty" }, [
      el("span", { class: "emoji", text: "📚" }),
      el("b", { text: "Bu ünite için henüz kitap sunumu bulunmuyor." }),
    ]));
  }

  mount(screen, ...parts);
}
