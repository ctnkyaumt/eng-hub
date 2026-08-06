/* Kelime Kartları - flip to learn, unknown words come back ------------------ */
import { Game } from "./engine.js";
import { el, shuffle } from "../ui.js";

export function start(ctx) {
  let queue = shuffle(ctx.bank.words.filter((w) => w.en && w.tr)).slice(0, 24);
  const total = queue.length;

  const game = new Game({
    screen: ctx.screen, title: ctx.title, total,
    time: 0, backHash: ctx.backHash, onRestart: ctx.restart,
  });

  let learned = 0;

  function next() {
    if (!queue.length) return game.finish(`${learned}/${total} kelime öğrenildi`);
    const w = queue[0];

    const card = el("div", { class: "fc" }, [
      el("div", { class: "fc-inner" }, [
        el("div", { class: "fc-face" }, [
          el("small", { text: "ENGLISH" }),
          el("div", { text: (w.emoji ? w.emoji + " " : "") + w.en }),
        ]),
        el("div", { class: "fc-face back" }, [
          el("small", { text: "TÜRKÇE" }),
          el("div", { text: w.tr }),
        ]),
      ]),
    ]);
    card.onclick = () => card.classList.toggle("flipped");

    game.stage.replaceChildren(
      el("div", { class: "fc-stage" }, [
        card,
        el("p", { style: "color:var(--ink-dim)", text: "Karta tıkla veya boşluk tuşuna bas — çevir" }),
        el("div", { class: "fc-actions" }, [
          el("button", {
            class: "btn big", text: "🔁 Tekrar göster",
            onclick: () => { queue.push(queue.shift()); game.miss(); next(); },
          }),
          el("button", {
            class: "btn primary big", text: "✅ Biliyorum",
            onclick: () => { queue.shift(); learned++; game.hit(8); game.step(); next(); },
          }),
        ]),
      ])
    );
    game.card = card;
  }

  const onKey = (e) => {
    if (e.code === "Space") { e.preventDefault(); game.card?.classList.toggle("flipped"); }
  };
  document.addEventListener("keydown", onKey);
  new MutationObserver((_, obs) => {
    if (!document.body.contains(game.frame)) { document.removeEventListener("keydown", onKey); obs.disconnect(); }
  }).observe(document.getElementById("screen"), { childList: true });

  next();
}
