/* Kule - every correct answer adds a floor, three lives ---------------------- */
import { Game } from "./engine.js";
import { el, mount, shuffle, sample } from "../ui.js";

const ROUND = 15;
const LIVES = 3;

export function start(ctx) {
  const pool = sample(ctx.bank.questions, ROUND);
  const game = new Game({
    screen: ctx.screen, title: ctx.title, total: pool.length,
    time: 0, backHash: ctx.backHash, onRestart: ctx.restart,
  });

  let i = 0, lives = LIVES, locked = false;

  const tower = el("div", { class: "tower" }, [el("div", { class: "climber", text: "🧗" })]);
  const body = el("div", { class: "tower-body" });
  const hearts = el("div", { style: "font-size:26px;letter-spacing:6px", text: "❤️".repeat(LIVES) });

  game.stage.replaceChildren(el("div", { class: "tower-wrap" }, [tower, body]));

  function next() {
    if (i >= pool.length) return game.finish(`Kule tamam! ${game.correct} kat`);
    if (lives <= 0) return game.finish(`Kule yıkıldı — ${game.correct} kat`);
    const q = pool[i];
    locked = false;

    const answers = shuffle(q.a);
    const buttons = answers.map((a) =>
      el("button", { class: "ans", onclick: () => choose(a, buttons, answers) }, [
        a.img ? el("img", { src: ctx.bank.imgBase + a.img, alt: "" }) : null,
        a.t || "",
      ])
    );

    mount(
      body,
      hearts,
      q.img ? el("img", { class: "q-img", src: ctx.bank.imgBase + q.img, alt: "" }) : null,
      el("div", { class: "q-text", text: q.q || "Doğru olanı seç" }),
      el("div", { class: "answers" }, buttons)
    );
  }

  function choose(a, buttons, answers) {
    if (locked) return;
    locked = true;
    buttons.forEach((b, n) => {
      b.disabled = true;
      if (answers[n].c) b.classList.add("right");
      else if (answers[n] === a) b.classList.add("wrong");
    });

    if (a.c) {
      game.hit(12);
      const floor = el("div", { class: "floor", text: String(game.correct) });
      tower.insertBefore(floor, tower.firstChild);
      const climber = tower.querySelector(".climber");
      climber.style.animation = "none";
      void climber.offsetWidth;
      climber.style.animation = "";
    } else {
      lives--;
      hearts.textContent = "❤️".repeat(Math.max(0, lives)) + "🖤".repeat(LIVES - Math.max(0, lives));
      tower.querySelector(".floor")?.remove();
      game.miss();
    }
    game.step();
    i++;
    setTimeout(next, a.c ? 520 : 950);
  }

  next();
}
