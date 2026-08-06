/* Hızlı Test - timed multiple choice ---------------------------------------- */
import { Game } from "./engine.js";
import { el, mount, shuffle, sample } from "../ui.js";

const ROUND = 12;
const KEYS = ["A", "B", "C", "D", "E", "F"];

export function start(ctx) {
  const pool = sample(ctx.bank.questions, ROUND);
  const game = new Game({
    screen: ctx.screen, title: ctx.title, total: pool.length,
    time: 75, backHash: ctx.backHash, onRestart: ctx.restart,
  });

  let i = 0;
  let locked = false;

  function next() {
    if (i >= pool.length) return game.finish("Tüm sorular bitti!");
    const q = pool[i];
    locked = false;

    const answers = shuffle(q.a);
    const buttons = answers.map((a, n) =>
      el("button", { class: "ans", onclick: () => choose(a, buttons, answers) }, [
        el("span", { class: "key", text: KEYS[n] }),
        a.img ? el("img", { src: ctx.bank.imgBase + a.img, alt: "" }) : null,
        a.t || (a.img ? "" : "—"),
      ])
    );

    mount(
      game.stage,
      q.img ? el("img", { class: "q-img", src: ctx.bank.imgBase + q.img, alt: "" }) : null,
      el("div", { class: "q-text", text: q.q || "Doğru olanı seç" }),
      el("div", { class: "answers" }, buttons)
    );
    game.keymap = { buttons, answers };
  }

  function choose(a, buttons, answers) {
    if (locked) return;
    locked = true;
    buttons.forEach((b, n) => {
      b.disabled = true;
      if (answers[n].c) b.classList.add("right");
      else if (answers[n] === a) b.classList.add("wrong");
    });
    if (a.c) { game.hit(10); game.addTime(3); } else { game.miss(); }
    game.step();
    i++;
    setTimeout(next, a.c ? 520 : 950);
  }

  const onKey = (e) => {
    const idx = KEYS.indexOf(e.key.toUpperCase());
    if (idx >= 0 && game.keymap?.buttons[idx]) game.keymap.buttons[idx].click();
  };
  document.addEventListener("keydown", onKey);
  const stop = new MutationObserver(() => {
    if (!document.body.contains(game.frame)) {
      document.removeEventListener("keydown", onKey);
      stop.disconnect();
    }
  });
  stop.observe(document.getElementById("screen"), { childList: true });

  next();
}
