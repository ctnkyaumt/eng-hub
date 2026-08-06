/* Shared game shell: HUD, timer, scoring, end screen ------------------------ */
import { el, beep, confetti } from "../ui.js";

export class Game {
  /**
   * @param {object} o  {screen, title, emoji, total, time (seconds, 0 = none),
   *                     onRestart, backHash}
   */
  constructor(o) {
    Object.assign(this, o);
    this.score = 0;
    this.streak = 0;
    this.best = 0;
    this.done = 0;
    this.correct = 0;
    this._t0 = performance.now();
    this.build();
  }

  build() {
    this.elScore = el("b", { text: "0" });
    this.elStreak = el("b", { text: "0" });
    this.elProg = el("b", { text: `0/${this.total}` });
    this.bar = el("i", { style: "width:100%" });
    this.timebar = el("div", { class: "timebar" }, [this.bar]);
    this.stage = el("div", { class: "stage" });

    const hud = el("div", { class: "hud" }, [
      el("span", { class: "chip" }, [el("small", { text: "Puan" }), this.elScore]),
      el("span", { class: "chip streak" }, [el("small", { text: "Seri" }), this.elStreak]),
      el("span", { class: "chip" }, [el("small", { text: "İlerleme" }), this.elProg]),
      el("span", { class: "grow" }),
      el("button", { class: "btn", text: "↺ Yeniden", onclick: () => this.onRestart?.() }),
      el("button", { class: "btn", text: "✕ Çıkış", onclick: () => (location.hash = this.backHash) }),
    ]);

    this.frame = el("div", { class: "game-frame" }, [
      el("div", { class: "hero", style: "margin-bottom:4px" }, [
        el("span", { class: "kicker", text: this.title }),
      ]),
      hud,
      this.time ? this.timebar : null,
      this.stage,
    ]);
    this.screen.replaceChildren(this.frame);

    if (this.time) this.startTimer();
  }

  startTimer() {
    this.left = this.time;
    clearInterval(this._iv);
    this._iv = setInterval(() => {
      this.left -= 0.1;
      this.bar.style.width = Math.max(0, (this.left / this.time) * 100) + "%";
      this.timebar.classList.toggle("low", this.left < this.time * 0.25);
      if (this.left <= 0) {
        clearInterval(this._iv);
        this.finish("Süre doldu!");
      }
    }, 100);
  }

  addTime(sec) {
    if (!this.time) return;
    this.left = Math.min(this.time, this.left + sec);
  }

  hit(points = 10) {
    this.streak++;
    this.best = Math.max(this.best, this.streak);
    this.score += points + Math.min(this.streak, 8) * 2;
    this.correct++;
    this.elScore.textContent = this.score;
    this.elStreak.textContent = this.streak;
    if (this.streak > 1) {
      this.elStreak.parentElement.classList.remove("hot");
      void this.elStreak.parentElement.offsetWidth;
      this.elStreak.parentElement.classList.add("hot");
    }
    beep("ok");
  }

  miss() {
    this.streak = 0;
    this.elStreak.textContent = "0";
    beep("bad");
  }

  step() {
    this.done++;
    this.elProg.textContent = `${this.done}/${this.total}`;
  }

  finish(reason = "") {
    clearInterval(this._iv);
    const secs = Math.round((performance.now() - this._t0) / 1000);
    const pct = this.total ? this.correct / this.total : 0;
    const stars = pct >= 0.9 ? 3 : pct >= 0.65 ? 2 : pct >= 0.35 ? 1 : 0;
    if (stars >= 2) { beep("win"); confetti(document.body); }

    this.stage.replaceChildren(
      el("div", { class: "result" }, [
        el("div", { class: "big", text: String(this.score) }),
        el("div", { class: "stars", text: "★★★".slice(0, stars).padEnd(3, "☆") }),
        el("p", { text: reason || "Bitti!" }),
        el("p", { text: `${this.correct}/${this.total} doğru · en uzun seri ${this.best} · ${secs} sn` }),
        el("div", { class: "btns" }, [
          el("button", { class: "btn primary big", text: "↺ Tekrar oyna", onclick: () => this.onRestart?.() }),
          el("button", { class: "btn big", text: "🎮 Başka oyun", onclick: () => (location.hash = this.backHash) }),
        ]),
      ])
    );
    this.timebar.remove();
  }
}
