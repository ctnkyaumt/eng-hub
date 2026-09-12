/* Kule: build a lit skyline, lose a floor on mistakes, keep an honest height. */
import { Game } from "./engine.js";
import { createSession } from "./session.js";
import { el, mount, shuffle, sample } from "../ui.js";

const ROUND = 15, LIVES = 3;

export function start(ctx) {
  const pool = sample(ctx.bank.questions, ROUND);
  const game = new Game({ screen: ctx.screen, title: ctx.title, total: pool.length,
    time: 0, backHash: ctx.backHash, onRestart: ctx.restart });
  game.frame.classList.add("tower-frame");
  let i = 0, lives = LIVES, locked = false, height = 0, bestHeight = 0, buttons = [];
  const floors = [];
  const stack = el("div", { class: "tower-stack" });
  const roof = el("div", { class: "tower-roof", "aria-hidden": "true" }, [
    el("span", { class: "tower-flag" }), el("i"), el("i"), el("i"),
  ]);
  const tower = el("div", { class: "tower-building", "aria-hidden": "true" }, [
    roof, stack, el("div", { class: "tower-base" }, [el("i"), el("b"), el("i")]),
  ]);
  const heightLabel = el("b", { text: "0 kat" });
  const milestone = el("span", { text: "İlk katı inşa et" });
  const scene = el("div", { class: "tower-scene", role: "img", "aria-label": "Kule: 0 kat" }, [
    el("div", { class: "tower-moon", "aria-hidden": "true" }),
    el("div", { class: "tower-cloud cloud-one", "aria-hidden": "true" }),
    el("div", { class: "tower-cloud cloud-two", "aria-hidden": "true" }),
    el("div", { class: "tower-skyline", "aria-hidden": "true" }, Array.from({ length: 7 }, () => el("i"))),
    el("div", { class: "tower-crane", "aria-hidden": "true" }, [el("i"), el("b"), el("em")]),
    el("div", { class: "tower-height" }, [heightLabel, milestone]),
    tower, el("div", { class: "tower-ground", "aria-hidden": "true" }),
  ]);
  const body = el("div", { class: "tower-body" });
  const question = el("div", { class: "tower-question" });
  const hearts = el("span", { class: "tower-lives", text: `♥ ${LIVES} / ${LIVES}` });
  const feedback = el("div", { class: "tower-feedback", role: "status", "aria-live": "polite",
    text: "Temel hazır. Her doğru cevapla bir kat yüksel!" });
  const pause = el("button", { class: "btn", text: "Duraklat (P)", onclick: () => session.togglePause() });
  mount(body,
    el("div", { class: "tower-controls" }, [hearts, pause]),
    el("p", { class: "tower-help", text: "Doğru cevap: +1 kat. Yanlış cevap: −1 kat ve −1 can. Süre sınırı yok. Tıkla / dokun veya 1–9'a bas." }),
    question, feedback);
  mount(game.stage, el("div", { class: "tower-wrap" }, [scene, body]));
  const session = createSession(game, {
    key(e) {
      if (/^[1-9]$/.test(e.key)) { e.preventDefault(); buttons[Number(e.key) - 1]?.click(); }
    },
    onPause(paused) {
      pause.textContent = paused ? "Devam et (P)" : "Duraklat (P)";
      buttons.forEach(b => { b.disabled = paused || locked; });
    },
  });

  function updateTower() {
    bestHeight = Math.max(bestHeight, height);
    heightLabel.textContent = `${height} kat`;
    milestone.textContent = height >= 10 ? "Gökyüzünün mimarı" : height >= 5 ? "Şehrin üzerinde" : "Hedef: 5 kat";
    scene.setAttribute("aria-label", `Kule: ${height} kat. En yüksek: ${bestHeight} kat.`);
    scene.classList.toggle("tower-high", height >= 5);
    scene.classList.toggle("tower-summit", height >= 10);
    scene.style.setProperty("--built", height);
  }
  function finish() {
    session.stop();
    game.finish(`${lives <= 0 ? "Canlar bitti." : "İnşaat tamam!"} Kulen: ${height} kat · En yüksek: ${bestHeight} kat`);
    const result = game.stage.firstElementChild;
    game.stage.replaceChildren(el("div", { class: "tower-wrap tower-finished" }, [scene, result]));
  }
  function next() {
    if (lives <= 0 || i >= pool.length) return finish();
    locked = false;
    scene.classList.remove("tower-damage", "tower-added");
    const q = pool[i], answers = shuffle(q.a);
    buttons = answers.map((a, n) => el("button", { class: "ans", onclick: () => choose(a, answers),
      "aria-label": `${n + 1}: ${a.t || "Görsel"}` }, [
      el("small", { class: "key", text: String(n + 1) }),
      a.img ? el("img", { src: ctx.bank.imgBase + a.img, alt: a.t || `Seçenek ${n + 1}` }) : null,
      a.t || "",
    ]));
    buttons.forEach(b => { b.disabled = session.paused; });
    mount(question,
      q.img ? el("img", { class: "q-img", src: ctx.bank.imgBase + q.img, alt: "Soru görseli" }) : null,
      el("div", { class: "q-text", text: q.q || "Doğru olanı seç" }),
      el("div", { class: "answers" }, buttons));
  }
  function choose(a, answers) {
    if (locked || session.paused || !session.active) return;
    locked = true;
    buttons.forEach((b, n) => {
      b.disabled = true;
      if (answers[n].c) b.classList.add("right");
      else if (answers[n] === a) b.classList.add("wrong");
    });
    if (a.c) {
      game.hit(12);
      height++;
      const floor = el("div", { class: "tower-floor", style: `--floor-hue:${205 + Math.floor((height - 1) / 5) * 24}` }, [
        el("small", { text: String(height) }), el("i"), el("i"), el("i"),
      ]);
      stack.prepend(floor);
      floors.push(floor);
      scene.classList.add("tower-added");
      feedback.textContent = height === 5 ? "5 kat! Artık şehrin üzerindesin." : height === 10 ?
        "10 kat! Gökyüzüne ulaştın!" : `Doğru! ${height}. kat yerleştirildi.`;
    } else {
      lives--;
      const floor = floors.pop();
      if (floor) {
        height--;
        const rubble = floor.cloneNode(true);
        rubble.classList.add("tower-rubble");
        rubble.style.bottom = `${70 + height * 22}px`;
        scene.append(rubble);
        rubble.addEventListener("animationend", () => rubble.remove(), { once: true });
        floor.remove();
        if (matchMedia("(prefers-reduced-motion: reduce)").matches) rubble.remove();
      }
      game.miss();
      scene.classList.add("tower-damage");
      const right = answers.filter(v => v.c).map(v => v.t || `${answers.indexOf(v) + 1}. görsel`).join(" / ");
      feedback.textContent = `${floor ? "Bir kat düştü." : "Temel sağlam."} Doğru cevap: ${right}`;
    }
    hearts.textContent = `♥ ${lives} / ${LIVES}`;
    updateTower();
    game.step();
    i++;
    session.after(a.c ? .95 : 2, next);
  }
  next();
}
