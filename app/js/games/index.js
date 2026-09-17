/* Game picker + dispatcher -------------------------------------------------- */
import { getBank, getUnit, getSites, getSlides, getStarterWords, unitPath } from "../store.js";
import { el, setCrumbs, toast } from "../ui.js";
import { sourceGameCard, onlineGameGallery } from "../game-resources.js";

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
    id: "balon-patlat", emoji: "🎈", name: "Balon Patlat",
    desc: "Balonlar kaçmadan doğru kelimeyi patlat. Beş can, bol seri!",
    needs: (b) => b.words.length >= 4 || b.questions.length >= 4,
    load: () => import("./arcade.js"),
  },
  {
    id: "kostebek-avi", emoji: "🐹", name: "Köstebek Avı",
    desc: "Saklanan köstebekleri izle, doğru kelime çıkınca yakala!",
    needs: (b) => b.words.length >= 4 || b.questions.length >= 4,
    load: () => import("./arcade.js"),
  },
  {
    id: "uzay-kosusu", emoji: "🚀", name: "Uzay Koşusu",
    desc: "Gemini yönlendir, doğru kelimenin şeridine geç. Uzaya açıl!",
    needs: (b) => b.words.length >= 4 || b.questions.length >= 4,
    load: () => import("./arcade.js"),
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
    desc: "Işıklı kuleni kat kat inşa et, bayrağını göğe taşı. Üç can!",
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
    sumeyye: bank.sumeyye || [],
    imgBase: `${unitPath(gid, uid)}/games/img/`,
  };
}

function crumbs(grade, unit, gid, uid, last) {
  const unitLabel = unit.no ? `${unit.label || "Ünite"} ${unit.no}` : (unit.label || "Revizyon");
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: unitLabel, hash: `#/${gid}/${uid}` },
    last ? { label: "Oyunlar", hash: `#/${gid}/${uid}/oyunlar` } : { label: "Oyunlar" },
    last ? { label: last } : null,
  ].filter(Boolean));
}

export async function gamePicker(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const unitLabel = unit.no ? `${unit.label || "Ünite"} ${unit.no}` : (unit.label || "Revizyon");
  const bank = await buildBank(gid, uid);
  crumbs(grade, unit, gid, uid);

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unitLabel} · ${unit.title}` }),
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
    parts.push(el('div', { class: 'source-game-grid' }, mirrored.map(m => sourceGameCard(m, true))));
  }

  const sumeyyeCount = (bank.sumeyye || []).length;
  parts.push(el("h2", { class: "section-title", text: "Çevrimiçi Oyun Klasörleri" }));
  const folderCard = el("button", {
    class: "card folder-card",
    style: "animation-delay: 90ms",
    onclick: () => {
      location.hash = `#/${gid}/${uid}/oyunlar/sumeyyeogultekin`;
    },
  }, [
    el("span", { class: "glow" }),
    el("span", { class: "emoji", text: "📁" }),
    el("h3", { text: "sumeyyeogultekin" }),
    el("p", { text: sumeyyeCount ? "Sümeyye Oğultekin çevrimiçi oyunları · İnternet gerekli" : "Bu ünite için henüz oyun eklenmedi" }),
    el("div", { class: "badge-row" }, [
      el("span", { class: "badge " + (sumeyyeCount ? "on" : "off"), text: `${sumeyyeCount} oyun` }),
    ]),
  ]);
  parts.push(el("div", { class: "grid g-3" }, [folderCard]));

  if (bank.online.length) {
    parts.push(el("h2", { class: "section-title", text: `Kaynaktaki çevrimiçi oyunlar (${bank.online.length})` }));
    parts.push(el("p", { style: "color:var(--ink-dim);margin:-6px 0 12px", text: "Bunlar internet bağlantısı ister." }));
    parts.push(onlineGameGallery(bank.online));
  }

  screen.replaceChildren(...parts);
}

export async function sumeyyeGamePicker(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const unitLabel = unit.no ? `${unit.label || "Ünite"} ${unit.no}` : (unit.label || "Revizyon");
  const bank = await buildBank(gid, uid);
  crumbs(grade, unit, gid, uid, "sumeyyeogultekin");

  const count = (bank.sumeyye || []).length;
  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unitLabel} · Oyunlar` }),
    el("h1", { text: "📁 sumeyyeogultekin" }),
    el("p", { text: count
      ? `${count} çevrimiçi oyun · Sümeyye Oğultekin · İnternet gerekli`
      : "Bu ünite için Sümeyye Oğultekin oyunu bulunamadı." }),
  ]);

  const parts = [hero];

  if (count > 0) {
    parts.push(onlineGameGallery(bank.sumeyye));
  } else {
    parts.push(
      el("div", { class: "empty" }, [
        el("span", { class: "emoji", text: "📁" }),
        el("p", { text: "Bu ünitede Sümeyye Oğultekin oyunu henüz bulunmuyor." }),
        el("button", {
          class: "btn",
          style: "margin-top: 14px",
          onclick: () => { location.hash = `#/${gid}/${uid}/oyunlar`; },
          text: "← Oyunlar'a Dön",
        }),
      ])
    );
  }

  screen.replaceChildren(...parts);
}

export async function playGame(gid, uid, mode, screen) {
  if (mode === "sumeyyeogultekin") {
    return sumeyyeGamePicker(gid, uid, screen);
  }
  const m = MODES.find((x) => x.id === mode);
  if (!m) return (location.hash = `#/${gid}/${uid}/oyunlar`);
  const { grade, unit } = await getUnit(gid, uid);
  const bank = await buildBank(gid, uid);
  crumbs(grade, unit, gid, uid, m.name);

  const mod = await m.load();
  const ctx = {
    screen, gid, uid, grade, unit, bank, mode,
    title: `${m.emoji} ${m.name} · ${unit.title || (unit.no ? "Ünite " + unit.no : (unit.label || "Revizyon"))}`,
    backHash: `#/${gid}/${uid}/oyunlar`,
    restart: () => mod.start(ctx),
  };
  mod.start(ctx);
}
