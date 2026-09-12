/* Original offline arcade games; reuse the unit vocabulary/question pool. */
import { Game } from "./engine.js";
import { rounds } from "./sharpshooter.js";
import { createSession } from "./session.js";
import { el, mount } from "../ui.js";

const SETTINGS = {
  "balon-patlat": { theme: "balloons", action: "Doğru balonu patlat!", seconds: 18,
    help: "Anlamı oku, doğru balona tıkla / dokun veya 1–4'e bas. Balonlar kaçmadan eşleştir!" },
  "kostebek-avi": { theme: "moles", action: "Doğru köstebeği yakala!", seconds: 18,
    help: "Anlamı oku. Doğru köstebek dışarı çıkınca tıkla / dokun veya 1–4'e bas." },
  "uzay-kosusu": { theme: "space", action: "Doğru kelimenin şeridine geç!", seconds: 14,
    help: "← → veya 1–4 ile şerit seç; dokunarak da seçebilirsin. Kelimeler gemiye ulaşınca cevap kilitlenir." },
};

export function start(ctx) {
  const config = SETTINGS[ctx.mode];
  const pool = rounds(ctx.bank);
  const game = new Game({ screen: ctx.screen, title: ctx.title, total: pool.length,
    time: 0, backHash: ctx.backHash, onRestart: ctx.restart });
  game.frame.classList.add("arcade-frame", `arcade-${config.theme}`);
  if (!pool.length) { game.finish("Bu oyun için en az dört farklı kelime gerekli."); return; }

  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let index = 0, lives = 5, elapsed = 0, locked = false, lane = -1, targets = [];
  const hearts = el("span", { class: "arcade-lives" });
  const timer = el("span", { class: "arcade-clock" });
  const pause = el("button", { class: "btn", text: "Duraklat (P)", onclick: () => session.togglePause() });
  const prompt = el("div", { class: "arcade-prompt" });
  const status = el("div", { class: "arcade-status", role: "status", "aria-live": "polite" });
  const field = el("div", { class: `arcade-field ${config.theme}`, "aria-label": config.action });
  const ship = el("div", { class: "arcade-ship", "aria-hidden": "true" }, [el("i"), el("b"), el("em")]);
  const progress = el("i");
  const runway = el("div", { class: "arcade-time", "aria-hidden": "true" }, [progress]);
  mount(game.stage,
    el("p", { class: "arcade-help", text: `${config.help} Beş can. P: duraklat.` }),
    el("div", { class: "arcade-controls" }, [hearts, timer, pause]), prompt, runway, field, status);
  if (config.theme === "space") field.append(ship);
  const session = createSession(game, {
    tick, key: keyboard,
    onPause(paused) {
      pause.textContent = paused ? "Devam et (P)" : "Duraklat (P)";
      syncButtons(paused);
    },
  });

  function syncButtons(paused = session.paused) {
    targets.forEach(t => { t.button.disabled = paused || locked || (config.theme === "moles" && !t.up); });
  }
  function finish() {
    session.stop();
    game.finish(lives <= 0 ? "Canlar bitti. Yeniden deneyebilirsin!" : "Harika! Tur tamamlandı.");
  }
  function next() {
    if (index >= pool.length || lives <= 0) return finish();
    elapsed = 0; locked = false; lane = -1;
    targets.forEach(t => t.button.remove());
    field.classList.remove("answer-hit", "answer-miss");
    const q = pool[index];
    mount(prompt, q.img ? el("img", { src: ctx.bank.imgBase + q.img, alt: "Soru görseli" }) : null,
      el("h2", { text: q.q || "Doğru görseli seç" }));
    status.textContent = config.action;
    hearts.textContent = `♥ ${lives} / 5`;
    field.style.setProperty("--lanes", q.a.length);
    targets = q.a.map((a, n) => {
      const button = el("button", { class: "arcade-target", "aria-label": `${n + 1}: ${a.t || "Görsel"}`,
        style: `--slot:${n};--hue:${[338, 194, 42, 270][n]}`, onclick: () => select(n) }, [
        config.theme === "moles" ? el("span", { class: "mole-head", "aria-hidden": "true" }, [el("i"), el("b")]) : null,
        el("small", { text: String(n + 1) }),
        a.img ? el("img", { src: ctx.bank.imgBase + a.img, alt: a.t || `Seçenek ${n + 1}` }) : null,
        el("span", { class: "arcade-label", text: a.t || "" }),
      ]);
      if (config.theme === "space") button.setAttribute("aria-pressed", "false");
      field.append(button);
      return { a, button, up: true };
    });
    updatePositions();
    syncButtons();
  }
  function select(n) {
    if (!session.active || session.paused || locked || !targets[n] || targets[n].button.disabled) return;
    if (config.theme !== "space") return answer(n);
    lane = n;
    targets.forEach((t, j) => {
      t.button.classList.toggle("selected", j === lane);
      t.button.setAttribute("aria-pressed", String(j === lane));
    });
    ship.style.left = `${(lane + .5) / targets.length * 100}%`;
    ship.classList.add("steered");
    status.textContent = `Şerit ${lane + 1} seçildi. Kelimeler yaklaşırken şerit değiştirebilirsin.`;
  }
  function answer(n) {
    if (locked) return;
    locked = true;
    const correct = targets[n]?.a.c === true;
    const right = targets.find(t => t.a.c);
    targets.forEach((t, j) => {
      t.button.classList.remove("mole-down");
      t.button.classList.toggle("right", !!t.a.c);
      t.button.classList.toggle("wrong", j === n && !correct);
    });
    field.classList.add(correct ? "answer-hit" : "answer-miss");
    if (correct) game.hit(12);
    else { lives--; game.miss(); }
    hearts.textContent = `♥ ${lives} / 5`;
    const answerText = right.a.t || `${targets.indexOf(right) + 1}. görsel`;
    status.textContent = correct ? `Doğru! ${answerText}${game.streak > 1 ? ` · ${game.streak}'li seri!` : ""}` :
      `${n < 0 ? "Süre doldu." : "Bir can gitti."} Doğru cevap: ${answerText}`;
    syncButtons();
    game.step();
    index++;
    session.after(correct ? 1 : 2, next);
  }
  function keyboard(e) {
    const number = Number(e.key);
    if (number >= 1 && number <= targets.length) { e.preventDefault(); select(number - 1); }
    if (config.theme === "space" && ["ArrowLeft", "ArrowRight"].includes(e.key)) {
      e.preventDefault();
      select(lane < 0 ? (e.key === "ArrowLeft" ? 0 : targets.length - 1) :
        Math.max(0, Math.min(targets.length - 1, lane + (e.key === "ArrowLeft" ? -1 : 1))));
    }
  }
  function updatePositions() {
    const p = Math.min(1, elapsed / config.seconds);
    timer.textContent = `${Math.ceil(config.seconds - elapsed)} sn`;
    progress.style.width = `${(1 - p) * 100}%`;
    field.classList.toggle("hurry", p > .75);
    targets.forEach((t, n) => {
      if (config.theme === "balloons") {
        t.button.style.left = `${n % 2 ? 75 : 25}%`;
        t.button.style.top = `${(n < 2 ? 32 : 78) - (reduced ? 0 : p * 10)}%`;
      } else if (config.theme === "moles") {
        // All targets surface every 3 seconds; each stays readable for >2 seconds.
        t.up = reduced || elapsed < 2 || (elapsed + n * .45) % 3 < 2.25;
        t.button.classList.toggle("mole-down", !t.up);
      } else {
        t.button.style.top = `${reduced ? 35 : 20 + p * 51}%`;
      }
    });
    if (config.theme === "space" && lane < 0) {
      ship.style.left = "50%";
      ship.classList.remove("steered");
    }
    syncButtons();
  }
  function tick(dt) {
    if (locked) return;
    elapsed = Math.min(config.seconds, elapsed + dt);
    updatePositions();
    if (elapsed >= config.seconds) answer(config.theme === "space" ? lane : -1);
  }
  next();
}
