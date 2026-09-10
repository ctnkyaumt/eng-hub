/* Game picker + dispatcher -------------------------------------------------- */
import { getBank, getUnit, getSites, getSlides, getStarterWords, unitPath } from "../store.js";
import { el, setCrumbs, toast } from "../ui.js";

if (!document.querySelector('link[href="/app/css/games.css"]')) {
  document.head.append(el("link", { rel: "stylesheet", href: "/app/css/games.css" }));
}

export const MODES = [
  {
    id: "sharpshooter", emoji: "🎯", name: "Sharpshooter",
    desc: "Nişan al, doğru kelimeyi vur. Baloncukları patlat, seri yap!",
    needs: () => true,
    load: () => import("./sharpshooter.js"),
  },
  {
    id: "hizli-test", emoji: "⚡", name: "Hızlı Test",
    desc: "Süreye karşı çoktan seçmeli. Doğru cevap süre kazandırır.",
    needs: (b) => b.questions.length >= 4,
    load: () => import("./quiz.js"),
  },
  {
    id: "eslestirme", emoji: "🃏", name: "Eşleştirme",
    desc: "Kartları çevir, İngilizce kelimeyi Türkçesiyle eşleştir.",
    needs: (b) => b.words.length >= 6,
    load: () => import("./memory.js"),
  },
  {
    id: "kelime-avi", emoji: "🔎", name: "Kelime Avı",
    desc: "Ünitenin kelimelerini bulmacada bul.",
    needs: (b) => b.words.filter((w) => /^[a-zA-Z ]{3,12}$/.test(w.en)).length >= 5,
    load: () => import("./wordsearch.js"),
  },
  {
    id: "karisik-harfler", emoji: "🔤", name: "Karışık Harfler",
    desc: "Harfleri doğru sıraya diz, kelimeyi kur.",
    needs: (b) => b.words.filter((w) => /^[a-zA-Z]{3,12}$/.test(w.en)).length >= 5,
    load: () => import("./scramble.js"),
  },
  {
    id: "kule", emoji: "🏗️", name: "Kule",
    desc: "Her doğru cevap bir kat. Üç can, ne kadar yükseğe?",
    needs: (b) => b.questions.length >= 6,
    load: () => import("./tower.js"),
  },
  {
    id: "kartlar", emoji: "📇", name: "Kelime Kartları",
    desc: "Çevir, öğren. Bilmediklerin tekrar gelir.",
    needs: (b) => b.words.length >= 4,
    load: () => import("./flashcards.js"),
  },
];

/** Flatten every source activity into one pool + merge slide vocabulary. */
async function buildBank(gid, uid) {
  const [bank, slides] = await Promise.all([getBank(gid, uid), getSlides(gid, uid)]);
  const questions = [];
  for (const s of bank.sets || []) {
    for (const q of s.questions) {
      if (q.a.some((a) => a.c) && q.a.length >= 2) questions.push({ ...q, from: s.name });
    }
  }

  const words = new Map();
  for (const w of bank.words || []) words.set(w.en.toLowerCase(), w);
  // slide vocabulary is hand-checked, so it wins on conflicts
  for (const sl of slides?.slides || []) {
    for (const v of sl.items || []) {
      if (v.en && v.tr) words.set(v.en.toLowerCase(), { en: v.en, tr: v.tr, emoji: v.emoji });
    }
  }

  if (words.size < 4) {
    for (const w of await getStarterWords(gid, uid)) words.set(w.en.toLowerCase(), w);
  }

  return {
    questions,
    words: [...words.values()],
    online: bank.online || [],
    imgBase: `${unitPath(gid, uid)}/games/img/`,
  };
}

function crumbs(grade, unit, gid, uid, last) {
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: `${unit.label || "Ünite"} ${unit.no}`, hash: `#/${gid}/${uid}` },
    last ? { label: "Oyunlar", hash: `#/${gid}/${uid}/oyunlar` } : { label: "Oyunlar" },
    last ? { label: last } : null,
  ].filter(Boolean));
}

export async function gamePicker(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const bank = await buildBank(gid, uid);
  crumbs(grade, unit, gid, uid);

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unit.label || "Ünite"} ${unit.no} · ${unit.title}` }),
    el("h1", { text: "Oyunlar" }),
    el("p", { text: `${bank.questions.length} soru · ${bank.words.length} kelime — hepsi çevrimdışı` }),
  ]);

  const cards = MODES.map((m, i) => {
    const ok = m.needs(bank);
    return el("button", {
      class: "card mode-card" + (ok ? "" : " dim"),
      style: `animation-delay:${i * 55}ms`,
      onclick: () => (ok ? (location.hash = `#/${gid}/${uid}/oyunlar/${m.id}`)
                        : toast("Bu ünitede bu oyun için yeterli veri yok.")),
    }, [
      el("span", { class: "glow" }),
      el("span", { class: "emoji", text: m.emoji }),
      el("h3", { text: m.name }),
      el("p", { text: m.desc }),
      ok ? null : el("small", { text: "veri yetersiz" }),
    ]);
  });

  const parts = [hero, el("div", { class: "grid g-3" }, cards)];

  const mirrored = await getSites(gid, uid, "game");
  if (mirrored.length) {
    parts.push(el("h2", { class: "section-title", text: `Kaynaktan çevrimdışı kopyalar (${mirrored.length})` }));
    parts.push(el("p", { style: "color:var(--ink-dim);margin:-6px 0 12px",
                         text: "Orijinal etkinlikler USB'ye kopyalandı — internet gerekmez." }));
    parts.push(el("div", { class: "list" }, mirrored.map((m) =>
      el("button", { class: "row", onclick: () => window.open(m.url, "_blank", "noopener") }, [
        el("span", { class: "ic", text: "🕹️" }),
        el("div", { class: "txt" }, [
          el("b", { text: m.title }),
          el("small", { text: m.by ? "Hazırlayan: " + m.by : "" }),
        ]),
        el("span", { class: "go", text: "▶" }),
      ])
    )));
  }

  if (bank.online.length) {
    parts.push(el("h2", { class: "section-title", text: `Kaynaktaki çevrimiçi oyunlar (${bank.online.length})` }));
    parts.push(el("p", { style: "color:var(--ink-dim);margin:-6px 0 12px", text: "Bunlar internet bağlantısı ister." }));
    parts.push(el("div", { class: "list" }, bank.online.map((o) =>
      el("button", { class: "row", onclick: () => window.open(o.link, "_blank", "noopener") }, [
        el("span", { class: "ic", text: "🌐" }),
        el("div", { class: "txt" }, [
          el("b", { text: o.title }),
          el("small", { text: o.by ? "Hazırlayan: " + o.by : new URL(o.link).hostname }),
        ]),
        el("span", { class: "go", text: "↗" }),
      ])
    )));
  }

  screen.replaceChildren(...parts);
}

export async function playGame(gid, uid, mode, screen) {
  const m = MODES.find((x) => x.id === mode);
  if (!m) return (location.hash = `#/${gid}/${uid}/oyunlar`);
  const { grade, unit } = await getUnit(gid, uid);
  const bank = await buildBank(gid, uid);
  crumbs(grade, unit, gid, uid, m.name);

  const mod = await m.load();
  const ctx = {
    screen, gid, uid, grade, unit, bank,
    title: `${m.emoji} ${m.name} · ${unit.title || "Ünite " + unit.no}`,
    backHash: `#/${gid}/${uid}/oyunlar`,
    restart: () => mod.start(ctx),
  };
  mod.start(ctx);
}
