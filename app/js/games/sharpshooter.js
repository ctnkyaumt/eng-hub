/* Original offline implementation inspired by Cram's matching shooter. */
import { Game } from "./engine.js";
import { el, sample, shuffle, mount } from "../ui.js";

export function rounds(bank) {
  const words = [...new Map(bank.words.filter(w => w.en?.trim() && w.tr?.trim())
    .map(w => [w.en.trim().toLowerCase(), w])).values()];
  if (words.length >= 4) return sample(words, 15).map(w => ({
    q: w.tr, a: shuffle([{ t: w.en, c: true }, ...sample(words.filter(v =>
      v.en !== w.en && v.tr.toLocaleLowerCase("tr") !== w.tr.toLocaleLowerCase("tr")), 3)
      .map(v => ({ t: v.en, c: false }))]),
  })).filter(q => q.a.length >= 2);
  return sample(bank.questions.filter(q => q.a.filter(a => a.c).length === 1 &&
    q.a.filter(a => a.t || a.img).length >= 2), 15).map(q => ({ ...q,
    a: shuffle([...q.a.filter(a => a.c), ...sample(q.a.filter(a => !a.c), 3)]) }));
}

let dispose = () => {};

export function start(ctx) {
  dispose();
  const pool = rounds(ctx.bank);
  if (!pool.length) {
    ctx.screen.replaceChildren(el("div", { class: "empty" }, [
      el("h2", { text: "Bu tema için kelime ekleyin" }),
      el("p", { text: "Her satıra İngilizce = Türkçe yazın. En az dört farklı kelime kullanın." }),
      el("textarea", { id: "shooter-words", rows: "8", "aria-label": "İngilizce ve Türkçe kelimeler",
        placeholder: "school = okul\nclassroom = sınıf\nteacher = öğretmen\nstudent = öğrenci" }),
      el("p", { id: "shooter-error", role: "status" }),
      el("button", { class: "btn primary", text: "Oyunu başlat", onclick: () => {
        const words = document.getElementById("shooter-words").value.split("\n").map(line => {
          const [en, ...tr] = line.split("="); return { en: en.trim(), tr: tr.join("=").trim() };
        }).filter(w => w.en && w.tr);
        if (new Set(words.map(w => w.en.toLowerCase())).size < 4 ||
            new Set(words.map(w => w.tr.toLocaleLowerCase("tr"))).size < 2) {
          document.getElementById("shooter-error").textContent = "En az dört farklı İngilizce kelime ve iki farklı anlam gerekli.";
          return;
        }
        ctx.bank.words = words;
        start(ctx);
      } }),
      el("a", { class: "btn", href: ctx.backHash, text: "Oyunlara dön" }),
    ]));
    return;
  }
  const game = new Game({ screen: ctx.screen, title: ctx.title, total: pool.length,
    time: 0, backHash: ctx.backHash, onRestart: ctx.restart });
  game.frame.classList.add("shooter-frame");
  let active = true, frame = 0, index = 0, lives = 5, paused = false;
  let pending = null, delay = 0;
  let locked = false, remaining = 300, last = performance.now(), nodes = [], shot = null;
  let aim = { x: .5, y: .3 }, particles = [], elapsed = 0;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const status = el("div", { class: "shooter-status", role: "status", "aria-live": "polite" });
  const prompt = el("div", { class: "shooter-prompt" });
  const field = el("div", { class: "shooter-field", "aria-label": "Atış alanı" });
  const cannon = el("div", { class: "shooter-cannon", "aria-hidden": "true" });
  const beam = el("div", { class: "shooter-beam", "aria-hidden": "true" });
  const clock = el("span");
  const hearts = el("span");
  const pause = el("button", { class: "btn", text: "Duraklat", onclick: () => {
    paused = !paused; pause.textContent = paused ? "Devam et" : "Duraklat";
    field.classList.toggle("paused", paused);
    nodes.forEach(n => { n.button.disabled = paused || n.popped || locked; });
  } });
  mount(game.stage, el("p", { class: "shooter-help", text:
    "Anlamı oku, eşleşen baloncuğa nişan al ve tıkla / dokun. 1–4 tuşlarıyla da ateş edebilirsin. Beş can, beş dakika." }),
    el("div", { class: "shooter-controls" }, [hearts, clock, pause]), prompt, field, status);
  field.append(beam, cannon);

  function stop() {
    active = false; cancelAnimationFrame(frame); pending = null;
    window.removeEventListener("keydown", key);
    window.removeEventListener("hashchange", stop);
    document.removeEventListener("visibilitychange", visibility);
  }
  dispose = stop;
  function finish(message) { stop(); game.finish(message); }
  function visibility() {
    if (document.hidden && !paused) pause.click();
  }
  function next() {
    if (!active || !game.frame.isConnected) return;
    if (index >= pool.length || lives <= 0) return finish(lives <= 0 ? "Canlar bitti. Tekrar dene!" : "Hedefler tamamlandı!");
    locked = false; shot = null; particles.forEach(p => p.el.remove()); particles = [];
    nodes.forEach(n => n.button.remove());
    const q = pool[index];
    mount(prompt, q.img ? el("img", { src: ctx.bank.imgBase + q.img, alt: "Soru görseli" }) : null,
      el("h2", { text: q.q || "Doğru görseli vur" }));
    status.textContent = "Doğru eşleşmeyi vur.";
    hearts.textContent = `♥ ${lives} / 5`;
    nodes = q.a.map((a, i) => {
      const button = el("button", { class: "shooter-bubble", "aria-label": `${i + 1}: ${a.t || "Görsel"}`,
        onclick: e => { e.stopPropagation(); fire(n.x, n.y); } }, [
        el("small", { text: String(i + 1) }),
        a.img ? el("img", { src: ctx.bank.imgBase + a.img, alt: a.t || `Seçenek ${i + 1}` }) : null,
        el("span", { text: a.t }),
      ]);
      const n = { button, a, x: 0, y: 0, homeX: i % 2 ? .73 : .27, homeY: i < 2 ? .26 : .66, popped: false, phase: i * 1.8 };
      button.disabled = paused;
      field.append(button); return n;
    });
  }
  function fire(x, y) {
    if (!active || paused || locked || shot) return;
    aim = { x, y };
    const width = field.clientWidth, height = field.clientHeight;
    const dx = (x - .5) * width, dy = (y - .94) * height, len = Math.hypot(dx, dy);
    if (len < 1) return;
    shot = { x: width * .5, y: height * .94, dx: dx / len, dy: dy / len };
    beam.style.opacity = "1";
  }
  field.addEventListener("pointermove", e => {
    const r = field.getBoundingClientRect(); aim = { x: (e.clientX-r.left)/r.width, y: (e.clientY-r.top)/r.height };
  });
  field.addEventListener("click", e => {
    const r = field.getBoundingClientRect(); fire((e.clientX-r.left)/r.width, (e.clientY-r.top)/r.height);
  });
  function key(e) {
    if (e.target.matches("input, textarea") || e.ctrlKey || e.altKey || e.metaKey || e.repeat) return;
    const n = nodes[Number(e.key)-1];
    if (n && !n.popped) { e.preventDefault(); fire(n.x, n.y); }
  }
  window.addEventListener("keydown", key);
  window.addEventListener("hashchange", stop);
  document.addEventListener("visibilitychange", visibility);
  function hit(n) {
    n.popped = true; n.button.disabled = true;
    n.button.classList.add("popped");
    for (let j = 0; j < 14; j++) {
      const p = el("i", { class: "shooter-particle", style: `background:${n.a.c ? "#74ffd2" : "#ff8caa"}` });
      field.append(p); const a = j * Math.PI * 2 / 14;
      particles.push({ el: p, x: n.x * field.clientWidth, y: n.y * field.clientHeight,
        vx: Math.cos(a)*160, vy: Math.sin(a)*160, life: 0.65 });
    }
    shot = null; beam.style.opacity = "0";
    if (n.a.c) { locked = true; game.hit(5); game.step(); index++;
      status.textContent = "İsabet! + puan";
      nodes.forEach(v => { v.button.disabled = true; });
      pending = next; delay = .75;
    } else {
      lives--; hearts.textContent = `♥ ${lives} / 5`; game.miss();
      game.score = Math.max(0, game.score-2); game.elScore.textContent = game.score;
      status.textContent = "Bu eşleşme yanlış. Doğru baloncuğu bul! −2 puan";
      if (!lives) { locked = true; pending = () => finish("Canlar bitti. Tekrar dene!"); delay = .75; }
    }
  }
  function tick(now) {
    if (!active || !game.frame.isConnected) return stop();
    const delta = Math.max(0, (now-last)/1000);
    const dt = Math.min(delta, .05); last = now;
    if (!paused) {
      if (pending) {
        delay -= dt;
        if (delay <= 0) { const action = pending; pending = null; action(); if (!active) return; }
      }
      remaining -= delta; elapsed += dt;
      if (remaining <= 0) return finish("Süre doldu!");
      clock.textContent = `${Math.floor(remaining/60)}:${String(Math.floor(remaining%60)).padStart(2,"0")}`;
      const w = field.clientWidth, h = field.clientHeight;
      nodes.forEach(n => {
        n.x = n.homeX + (reduced ? 0 : Math.sin(elapsed*.6+n.phase)*.045);
        n.y = n.homeY + (reduced ? 0 : Math.cos(elapsed*.7+n.phase)*.02);
        n.button.style.left = `${n.x*100}%`; n.button.style.top = `${n.y*100}%`;
      });
      cannon.style.transform = `translateX(-50%) rotate(${Math.atan2((aim.x-.5)*w, (.94-aim.y)*h)}rad)`;
      if (shot) {
        // Short physics steps prevent a fast projectile skipping a circle.
        const steps = Math.max(1, Math.ceil(dt*850/6));
        for (let j=0; j<steps && shot; j++) {
          shot.x += shot.dx*850*dt/steps; shot.y += shot.dy*850*dt/steps;
          const n = nodes.find(n => !n.popped && Math.hypot(shot.x-n.x*w, shot.y-n.y*h) <= n.button.offsetWidth/2);
          if (n) hit(n);
          else if (shot.x<0 || shot.x>w || shot.y<0 || shot.y>h) { shot=null; beam.style.opacity="0"; }
        }
        if (shot) { beam.style.left=`${shot.x}px`; beam.style.top=`${shot.y}px`; }
      }
      particles = particles.filter(p => {
        p.life -= dt; if(p.life<=0) { p.el.remove(); return false; }
        p.x += p.vx*dt; p.y += p.vy*dt; p.vy += 200*dt;
        p.el.style.transform=`translate(${p.x}px,${p.y}px)`; p.el.style.opacity=p.life/.65; return true;
      });
    }
    frame = requestAnimationFrame(tick);
  }
  next(); frame = requestAnimationFrame(tick);
}
