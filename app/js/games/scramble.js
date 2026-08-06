/* Karışık Harfler - rebuild the word from shuffled letters ------------------ */
import { Game } from "./engine.js";
import { el, shuffle, sample, beep } from "../ui.js";

const ROUND = 10;

export function start(ctx) {
  const pool = sample(
    ctx.bank.words.filter((w) => /^[a-zA-Z]{3,12}$/.test(w.en)),
    ROUND
  );

  const game = new Game({
    screen: ctx.screen, title: ctx.title, total: pool.length,
    time: 150, backHash: ctx.backHash, onRestart: ctx.restart,
  });

  let i = 0;

  function next() {
    if (i >= pool.length) return game.finish("Bütün kelimeler tamam!");
    const w = pool[i];
    const target = w.en.toUpperCase();

    let letters = shuffle([...target]);
    if (letters.join("") === target && target.length > 2) letters = shuffle(letters);

    const slots = el("div", { class: "scr-slots" });
    const pool2 = el("div", { class: "scr-pool" });
    const picked = [];

    const draw = () => {
      slots.replaceChildren(...[...target].map((_, n) =>
        el("button", {
          class: "tile slot", text: picked[n] || " ",
          onclick: () => { if (picked[n]) { picked.splice(n, 1); draw(); } },
        })
      ));
      pool2.replaceChildren(...letters.map((ch, n) =>
        el("button", {
          class: "tile", text: ch, disabled: used.has(n),
          style: used.has(n) ? "opacity:.25;pointer-events:none" : "",
          onclick: () => { used.add(n); picked.push(ch); check(); draw(); },
        })
      ));
    };

    const used = new Set();

    function check() {
      if (picked.length < target.length) return;
      const guess = picked.join("");
      if (guess === target) {
        game.hit(14);
        game.addTime(4);
        game.step();
        i++;
        [...slots.children].forEach((t) => t.classList.add("ok"));
        setTimeout(next, 600);
      } else {
        game.miss();
        [...slots.children].forEach((t) => t.classList.add("no"));
        setTimeout(() => { picked.length = 0; used.clear(); draw(); }, 600);
      }
    }

    game.stage.replaceChildren(
      el("div", { class: "scr-hint" }, [
        el("div", { style: "font-size:38px", text: w.emoji || "🔤" }),
        el("div", { text: w.tr }),
      ]),
      slots,
      el("div", { style: "height:4px" }),
      pool2,
      el("div", { style: "text-align:center" }, [
        el("button", {
          class: "btn", text: "💡 İlk harf",
          onclick: (e) => {
            e.target.disabled = true;
            const n = letters.findIndex((ch, k) => !used.has(k) && ch === target[picked.length]);
            if (n >= 0) { used.add(n); picked.push(letters[n]); beep("tick"); check(); draw(); }
          },
        }),
        el("button", {
          class: "btn", text: "↷ Atla", style: "margin-left:10px",
          onclick: () => { game.miss(); game.step(); i++; next(); },
        }),
      ])
    );

    draw();
  }

  next();
}
