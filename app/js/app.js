/* ENG HUB - router + menu screens ------------------------------------------
   Routes:  #/                     main menu (grades)
            #/g5                   unit list
            #/g5/u1                unit menu
            #/g5/u1/sunum          presentation deck
            #/g5/u1/oyunlar        game picker
            #/g5/u1/oyunlar/quiz   a game
            #/g5/u1/calisma        worksheets
--------------------------------------------------------------------------- */
import { getCatalog, getUnit, unitPath } from "./store.js";
import { el, toast, setCrumbs } from "./ui.js";

const screen = document.getElementById("screen");

const GRADE_EMOJI = { 5: "🎒", 6: "🧭", 7: "🚀", 8: "🏆" };
const GRADE_SUB = {
  5: "Merhaba İngilizce!",
  6: "Keşfetmeye devam",
  7: "Daha ileriye",
  8: "LGS'ye hazır",
};

/* ---------------------------------------------------------------- routing */
const routes = [
  [/^\/?$/, home],
  [/^\/(g\d)$/, gradeScreen],
  [/^\/(g\d)\/([a-z0-9_-]+)$/, unitScreen],
  [/^\/(g\d)\/([a-z0-9_-]+)\/sunum$/, presentationScreen],
  [/^\/(g\d)\/([a-z0-9_-]+)\/oyunlar$/, gamesScreen],
  [/^\/(g\d)\/([a-z0-9_-]+)\/oyunlar\/([a-z0-9_-]+)$/, playScreen],
  [/^\/(g\d)\/([a-z0-9_-]+)\/calisma$/, worksheetsScreen],
  [/^\/(g\d)\/([a-z0-9_-]+)\/kitap$/, booksScreen],
];

async function render() {
  const path = decodeURIComponent(location.hash.replace(/^#/, "")) || "/";
  for (const [re, fn] of routes) {
    const m = path.match(re);
    if (m) {
      screen.classList.remove("fade");
      try {
        await fn(...m.slice(1));
      } catch (err) {
        console.error(err);
        screen.replaceChildren(
          el("div", { class: "empty" }, [
            el("span", { class: "emoji", text: "😕" }),
            el("p", { text: "Bu bölüm yüklenemedi: " + err.message }),
          ])
        );
      }
      screen.focus({ preventScroll: true });
      window.scrollTo({ top: 0 });
      return;
    }
  }
  location.hash = "#/";
}

export function go(hash) {
  location.hash = hash;
}
window.addEventListener("hashchange", render);

/* ------------------------------------------------------------- screen: home */
async function home() {
  setCrumbs([{ label: "Ana Menü" }]);
  const cat = await getCatalog();

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: "İngilizce Öğretmeni Yardımcısı" }),
    el("h1", { text: "ENG HUB" }),
    el("p", { text: "Sunumlar ve oyunlar çevrimdışı · Çalışma kâğıtları için internet gerekli" }),
  ]);

  const cards = cat.grades.map((g, i) => {
    const ready = g.units.filter((u) => u.has.presentation || u.has.games || u.has.worksheets).length;
    return el(
      "button",
      {
        class: "card grade",
        "data-g": String(g.no),
        style: `animation-delay:${i * 60}ms`,
        onclick: () => go(`#/${g.id}`),
      },
      [
        el("span", { class: "glow" }),
        el("span", { class: "emoji", text: GRADE_EMOJI[g.no] || "📘" }),
        el("div", { class: "num", text: g.no + "." }),
        el("h3", { text: g.title }),
        el("p", { text: GRADE_SUB[g.no] || "" }),
        el("div", { class: "badge-row" }, [
          el("span", { class: "badge", text: g.units.some(u => u.id === "revision") ? `${g.units.filter(u => u.id !== "revision").length} tema + revizyon` : `${g.units.length} ${g.no <= 6 ? "tema" : "ünite"}` }),
          el("span", { class: ready ? "badge on" : "badge off", text: `${ready} hazır` }),
        ]),
      ]
    );
  });

  screen.replaceChildren(hero, el("div", { class: "grid g-4" }, cards));
}

/* ------------------------------------------------------------ screen: grade */
async function gradeScreen(gid) {
  const cat = await getCatalog();
  const g = cat.grades.find((x) => x.id === gid);
  if (!g) return go("#/");
  setCrumbs([{ label: "Ana Menü", hash: "#/" }, { label: g.title }]);

  const hasRev = g.units.some((u) => u.id === "revision");
  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: g.title }),
    el("h1", { text: hasRev ? "Revizyon ve Temalar" : g.no <= 6 ? "Temalar" : "Üniteler" }),
    el("p", { text: hasRev ? "Bir revizyon veya tema seçin" : g.no <= 6 ? "Bir tema seçin" : "Bir ünite seçin" }),
  ]);

  const cards = g.units.map((u, i) => {
    const any = u.has.presentation || u.has.games || u.has.worksheets || (u.books || 0) > 0;
    return el(
      "button",
      {
        class: "card unit-card" + (any ? "" : " dim"),
        "data-g": String(g.no),
        style: `animation-delay:${i * 45}ms`,
        onclick: () => (any ? go(`#/${g.id}/${u.id}`) : toast("Bu ünite için henüz içerik yok.")),
      },
      [
        el("span", { class: "glow" }),
        el("span", { class: "emoji", text: u.emoji || "📗" }),
        el("div", { class: "no", text: u.no ? `${(u.label || "Ünite").toLocaleUpperCase("tr")} ${u.no}` : (u.label || "Revizyon").toLocaleUpperCase("tr") }),
        el("h3", { text: u.title || "—" }),
        el("p", { text: u.titleTr || "" }),
        el("div", { class: "badge-row" }, [
          el("span", { class: "badge " + (u.has.presentation ? "on" : "off"), text: "Sunum" }),
          el("span", { class: "badge " + (u.has.games ? "on" : "off"), text: "Oyun" }),
          el("span", { class: "badge " + (u.has.worksheets ? "on" : "off"), text: "Kâğıt" }),
          ...(u.books ? [el("span", { class: "badge on", text: "Kitap" })] : []),
        ]),
      ]
    );
  });

  screen.replaceChildren(hero, el("div", { class: "grid g-3" }, cards));
}

/* ------------------------------------------------------------- screen: unit */
async function unitScreen(gid, uid) {
  const { grade, unit } = await getUnit(gid, uid);
  const unitLabel = unit.no ? `${unit.label || "Ünite"} ${unit.no}` : (unit.label || "Revizyon");
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: unitLabel },
  ]);

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unitLabel}` }),
    el("h1", { text: unit.title || unitLabel }),
    el("p", { text: unit.titleTr || "" }),
  ]);

  const mk = (emoji, title, desc, hash, ok, whenEmpty) =>
    el(
      "button",
      { class: "card section-card" + (ok ? "" : " dim"), onclick: () => (ok ? go(hash) : toast(whenEmpty)) },
      [
        el("span", { class: "glow" }),
        el("span", { class: "emoji", text: emoji }),
        el("h3", { text: title }),
        el("p", { text: ok ? desc : whenEmpty }),
      ]
    );

  screen.replaceChildren(
    hero,
    el("div", { class: "grid g-3" }, [
      mk("📽️", "SUNUM", "Ünite anlatımı, kelimeler ve gramer", `#/${gid}/${uid}/sunum`,
         unit.has.presentation, "Bu ünite için sunum eklenmedi."),
      mk("🎮", "OYUNLAR",
         unit.counts.games ? `${unit.counts.games} soruluk oyun havuzu` : "Sharpshooter ve ünite kelime oyunları",
         `#/${gid}/${uid}/oyunlar`,
         unit.has.games, "Bu ünite için oyun verisi yok."),
      mk("📄", "ÇALIŞMA KÂĞITLARI", `${unit.counts.worksheetLinks || 0} bağlantı · İnternet gerekli`, `#/${gid}/${uid}/calisma`,
         unit.has.worksheets, "Bu ünite için çalışma kâğıdı yok."),
      mk("📚", "KİTAP SUNUMLARI", `${unit.books || 0} kaynak sunumu`, `#/${gid}/${uid}/kitap`,
         (unit.books || 0) > 0, "Bu ünite için kitap sunumu yok."),
    ])
  );
}

/* ------------------------------------------------- screens loaded on demand */
async function presentationScreen(gid, uid) {
  const { startDeck } = await import("./deck.js");
  await startDeck(gid, uid, screen);
}

async function gamesScreen(gid, uid) {
  const { gamePicker } = await import("./games/index.js");
  await gamePicker(gid, uid, screen);
}

async function playScreen(gid, uid, mode) {
  const { playGame } = await import("./games/index.js");
  await playGame(gid, uid, mode, screen);
}

async function worksheetsScreen(gid, uid) {
  const { worksheetList } = await import("./worksheets.js");
  await worksheetList(gid, uid, screen);
}

async function booksScreen(gid, uid) {
  const { bookList } = await import("./books.js");
  await bookList(gid, uid, screen);
}

/* ----------------------------------------------------------------- chrome  */
document.getElementById("btn-home").onclick = () => go("#/");
document.getElementById("btn-back").onclick = () => history.back();
document.getElementById("btn-full").onclick = () => {
  if (document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen?.();
};

document.addEventListener("keydown", (e) => {
  if (e.target.matches("input, textarea")) return;
  if (e.key === "Backspace") { e.preventDefault(); history.back(); }
  if (e.key === "f" || e.key === "F") document.getElementById("btn-full").click();
});

export { unitPath };
render();
