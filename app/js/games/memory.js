/* Eşleştirme - flip two cards, match English with Turkish ------------------- */
import { Game } from "./engine.js";
import { el, shuffle, sample } from "../ui.js";

const PAIRS = 8;

export function start(ctx) {
  const pairs = sample(ctx.bank.words.filter((w) => w.en && w.tr), PAIRS);
  const cards = shuffle(
    pairs.flatMap((w, idx) => [
      { id: idx, side: "en", text: (w.emoji ? w.emoji + " " : "") + w.en },
      { id: idx, side: "tr", text: w.tr },
    ])
  );

  const game = new Game({
    screen: ctx.screen, title: ctx.title, total: pairs.length,
    time: 120, backHash: ctx.backHash, onRestart: ctx.restart,
  });

  let open = [];
  let busy = false;

  const nodes = cards.map((c) => {
    const n = el("button", { class: "mem" }, [el("span", { text: c.text })]);
    n.onclick = () => flip(c, n);
    return n;
  });

  game.stage.replaceChildren(el("div", { class: "mem-grid" }, nodes));

  function flip(card, node) {
    if (busy || node.classList.contains("open") || node.classList.contains("done")) return;
    node.classList.add("open");
    open.push({ card, node });
    if (open.length < 2) return;

    busy = true;
    const [a, b] = open;
    if (a.card.id === b.card.id && a.card.side !== b.card.side) {
      a.node.classList.add("done");
      b.node.classList.add("done");
      game.hit(12);
      game.step();
      open = [];
      busy = false;
      if (game.done >= pairs.length) game.finish("Hepsi eşleşti!");
    } else {
      a.node.classList.add("miss");
      b.node.classList.add("miss");
      game.miss();
      setTimeout(() => {
        for (const o of open) o.node.classList.remove("open", "miss");
        open = [];
        busy = false;
      }, 700);
    }
  }
}
