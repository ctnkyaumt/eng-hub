/* tiny DOM helpers shared by every screen ---------------------------------- */

export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "text") node.textContent = v;
    else if (k === "html") node.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);
    else if (k === "class") node.className = v;
    else node.setAttribute(k, v);
  }
  for (const c of [].concat(children)) {
    if (c === null || c === undefined || c === false) continue;
    node.append(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return node;
}

/** replaceChildren() turns a null argument into the text "null" - drop them. */
export function mount(node, ...kids) {
  node.replaceChildren(...kids.filter((k) => k !== null && k !== undefined && k !== false));
}

let toastTimer;
export function toast(msg, bad = false) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.toggle("bad", !!bad);
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 2600);
}

export function setCrumbs(items) {
  const nav = document.getElementById("crumbs");
  nav.replaceChildren();
  items.forEach((it, i) => {
    if (i) nav.append(el("span", { class: "sep", text: "›" }));
    nav.append(
      it.hash ? el("a", { href: it.hash, text: it.label }) : el("span", { class: "now", text: it.label })
    );
  });
}

/* Fisher-Yates - used everywhere in the games */
export function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function sample(arr, n) {
  return shuffle(arr).slice(0, n);
}

/* WebAudio blips: no asset files, works offline, never blocks the UI */
let ac;
export function beep(kind = "ok") {
  try {
    ac = ac || new (window.AudioContext || window.webkitAudioContext)();
    const spec = {
      ok:   [[660, 0], [990, 0.09]],
      bad:  [[220, 0], [160, 0.12]],
      tick: [[880, 0]],
      win:  [[523, 0], [659, 0.1], [784, 0.2], [1047, 0.3]],
    }[kind] || [[660, 0]];
    for (const [freq, at] of spec) {
      const o = ac.createOscillator(), g = ac.createGain();
      o.type = kind === "bad" ? "sawtooth" : "triangle";
      o.frequency.value = freq;
      g.gain.setValueAtTime(0.0001, ac.currentTime + at);
      g.gain.exponentialRampToValueAtTime(0.16, ac.currentTime + at + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, ac.currentTime + at + 0.22);
      o.connect(g).connect(ac.destination);
      o.start(ac.currentTime + at);
      o.stop(ac.currentTime + at + 0.24);
    }
  } catch { /* audio is a bonus, never a requirement */ }
}

export function confetti(host, n = 90) {
  const wrap = el("div", { class: "confetti" });
  const colors = ["#ffd166", "#4ade80", "#38bdf8", "#fb7185", "#c084fc", "#fff"];
  for (let i = 0; i < n; i++) {
    wrap.append(el("i", {
      style: `left:${Math.random() * 100}%;background:${colors[i % colors.length]};
              animation-delay:${Math.random() * 0.6}s;
              animation-duration:${1.6 + Math.random() * 1.4}s;
              transform:rotate(${Math.random() * 360}deg)`,
    }));
  }
  host.append(wrap);
  setTimeout(() => wrap.remove(), 3600);
}
