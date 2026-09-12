/* No build or browser dependencies. Exercise actual game modules with a clock/DOM fixture. */
import assert from "node:assert/strict";
import fs from "node:fs";
const root = new URL("../", import.meta.url);
const read = (p, fallback) => fs.existsSync(new URL(p, root)) ? JSON.parse(fs.readFileSync(new URL(p, root), "utf8")) : fallback;
const { rounds } = await import("../app/js/games/sharpshooter.js");
const { start: arcade } = await import("../app/js/games/arcade.js");
const { start: tower } = await import("../app/js/games/tower.js");
const seed = read("app/data/sharpshooter-words.json").units;
let units = 0;
for (const g of read("app/data/catalog.json").grades) for (const u of g.units) {
  const unit = `${g.id}/${u.id}`;
  const bank = read(`content/${unit}/games/bank.json`, {});
  const words = new Map((bank.words || []).map(w => [w.en.toLowerCase(), w]));
  for (const slide of read(`content/${unit}/presentation/slides.json`, {}).slides || []) {
    for (const w of slide.items || []) if (w.en && w.tr) words.set(w.en.toLowerCase(), w);
  }
  if (words.size < 4) for (const w of seed[unit] || []) words.set(w.en.toLowerCase(), w);
  for (let n = 0; n < 5; n++) {
    const questions = rounds({ words: [...words.values()], questions: (bank.sets || []).flatMap(s => s.questions) });
    assert(questions.length >= 4, unit);
    for (const q of questions) {
      assert.equal(q.a.filter(a => a.c).length, 1, unit);
      assert(q.a.length >= 2 && q.a.length <= 4, unit);
      assert.equal(new Set(q.a.map(a => a.t)).size, q.a.length, unit);
    }
  }
  units++;
}
assert.equal(units, 38);
// Bank fallback must retain pictures and exactly one answer.
assert.equal(rounds({ words: [], questions: [{ q: "Picture", img: "q.png", a: [
  { img: "yes.png", c: true }, { img: "no.png", c: false },
] }] })[0].img, "q.png");

class Element {
  constructor(tag) {
    this.tagName = tag; this.children = []; this.attrs = {}; this.events = {};
    this.style = { setProperty(k, v) { this[k] = v; } }; this.nodeType = 1; this.className = ""; this.textContent = "";
    this.classList = {
      add: (...classes) => { this.className = [...new Set([...this.className.split(" "), ...classes])].filter(Boolean).join(" "); },
      remove: (...classes) => { this.className = this.className.split(" ").filter(c => !classes.includes(c)).join(" "); },
      toggle: (c, on) => { const value = on ?? !this.className.split(" ").includes(c); this.classList[value ? "add" : "remove"](c); },
    };
  }
  setAttribute(k, v) { if (k === "class") this.className = v; else this.attrs[k] = v; }
  addEventListener(k, f) { (this.events[k] ||= new Set()).add(f); }
  removeEventListener(k, f) { this.events[k]?.delete(f); }
  emit(k, event = {}) { for (const f of [...this.events[k] || []]) f(event); }
  append(...nodes) { for (const n of nodes) { n.remove(); n.parentElement = this; this.children.push(n); } }
  prepend(n) { n.remove(); n.parentElement = this; this.children.unshift(n); }
  replaceChildren(...nodes) { this.children.forEach(n => { n.parentElement = null; }); this.children = []; this.append(...nodes); }
  remove() { if (this.parentElement) this.parentElement.children = this.parentElement.children.filter(n => n !== this); this.parentElement = null; }
  cloneNode(deep) { const copy = new Element(this.tagName); copy.className = this.className; copy.textContent = this.textContent; if (deep) copy.append(...this.children.map(c => c.cloneNode(true))); return copy; }
  get isConnected() { return this === screen || !!this.parentElement?.isConnected; }
  get firstElementChild() { return this.children[0]; }
  click() { if (!this.disabled) this.emit("click"); }
}
const screen = new Element("main"), doc = new Element("document"), win = new Element("window");
doc.createElement = t => new Element(t);
doc.createTextNode = t => Object.assign(new Element("text"), { textContent: String(t) });
doc.body = new Element("body");
globalThis.document = doc; globalThis.window = win;
let reduced = false;
globalThis.matchMedia = () => ({ matches: reduced });
let now = 0, nextId = 0;
const frames = new Map(), timers = new Map();
globalThis.performance = { now: () => now };
globalThis.requestAnimationFrame = f => { frames.set(++nextId, f); return nextId; };
globalThis.cancelAnimationFrame = id => frames.delete(id);
globalThis.setTimeout = (f, ms) => { timers.set(++nextId, { f, at: now + ms }); return nextId; };
globalThis.clearTimeout = id => timers.delete(id);
function advance(ms) {
  for (let n = 0; n < ms; n += 20) {
    now += 20;
    const batch = [...frames.values()]; frames.clear(); batch.forEach(f => f(now));
    for (const [id, t] of timers) if (t.at <= now) { timers.delete(id); t.f(); }
  }
}
const all = n => [n, ...n.children.flatMap(all)];
const findAll = c => all(screen).filter(n => n.className.split(" ").includes(c));
const find = c => findAll(c)[0];
const text = n => [n.textContent, ...n.children.map(text)].join(" ");
const key = k => win.emit("keydown", { key: k, preventDefault() {} });
const words = [
  { en: "apple", tr: "elma" }, { en: "pear", tr: "armut" },
  { en: "orange", tr: "portakal" }, { en: "cherry", tr: "kiraz" },
  { en: "melon", tr: "kavun" }, { en: "plum", tr: "erik" },
];
function startGame(mode, start = arcade, bank = { words, questions: [], imgBase: "/" }) {
  const ctx = { screen, mode, bank, title: "probe", backHash: "#/" };
  ctx.restart = () => start(ctx); start(ctx); return ctx;
}
function choice(correct = true) {
  const translation = find("arcade-prompt").children.at(-1).textContent;
  const answer = words.find(w => w.tr === translation).en;
  return findAll("arcade-target").findIndex(b => b.attrs["aria-label"].endsWith(`: ${answer}`) === correct);
}
const score = () => Number(find("hud").children[0].children[1].textContent);
for (const mode of ["balon-patlat", "kostebek-avi", "uzay-kosusu"]) {
  for (const motion of [false, true]) {
    reduced = motion;
    const ctx = startGame(mode);
    assert.equal(findAll("arcade-target").length, 4);
    key(String(choice() + 1));
    if (mode === "uzay-kosusu") { assert.equal(score(), 0); advance(14020); }
    assert.equal(score(), 14, `${mode} correct score`);
    const before = score(); key("1"); assert.equal(score(), before, "double answer locked");
    key("p"); advance(3000);
    assert(findAll("arcade-target").every(b => b.disabled));
    assert.equal(find("hud").children[2].children[1].textContent, "1/6", "feedback paused");
    key("p"); advance(1100);
    key(String(choice(false) + 1));
    if (mode === "uzay-kosusu") advance(14020);
    assert.equal(find("arcade-lives").textContent, "♥ 4 / 5");
    assert(text(find("arcade-status")).includes("Doğru cevap:"));
    ctx.restart(); assert.equal(frames.size, 1, "restart owns only one clock");
    const clock = find("arcade-clock").textContent;
    doc.hidden = true; doc.emit("visibilitychange"); advance(20000);
    assert.equal(find("arcade-clock").textContent, clock, "hidden page paused");
    doc.hidden = false; key("p");
    advance(110000); assert(find("result"), "unanswered rounds reach game over");
    assert.equal(frames.size, 0, "game over stops clock");
    ctx.restart(); win.emit("hashchange"); assert.equal(frames.size, 0);
    assert.equal(win.events.keydown.size, 0, "exit removes keyboard listener");
    assert.equal(doc.events.visibilitychange.size, 0, "exit removes visibility listener");
  }
  reduced = true;
  startGame(mode);
  for (let i = 0; i < words.length; i++) {
    key(String(choice() + 1));
    advance(mode === "uzay-kosusu" ? 15100 : 1100);
  }
  assert(find("result"), `${mode} all correct completes`);
  assert(text(find("result")).includes("6/6 doğru"));
  assert.equal(frames.size, 0);
}
// Image-only question/answer fallback is also playable in every arcade mode.
for (const mode of ["balon-patlat", "kostebek-avi", "uzay-kosusu"]) {
  startGame(mode, arcade, { words: [], imgBase: "/", questions: [{ q: "Pick", img: "q.png", a: [
    { img: "yes.png", c: true }, { img: "no.png", c: false },
  ] }] });
  assert.equal(find("arcade-prompt").children[0].attrs.src, "/q.png");
  const n = findAll("arcade-target").findIndex(b => b.children.some(c => c.attrs.src === "/yes.png"));
  key(String(n + 1)); advance(mode === "uzay-kosusu" ? 15100 : 1100);
  assert(text(find("result")).includes("1/1 doğru"));
}
const towerBank = { words: [], imgBase: "/", questions: Array.from({ length: 15 }, (_, n) => ({
  q: `Question ${n}`, a: [{ t: "yes", c: true }, { t: "no", c: false }],
})) };
const chooseTower = correct => findAll("ans").find(b => b.attrs["aria-label"].endsWith(correct ? ": yes" : ": no")).click();
const ctx = startGame("kule", tower, towerBank);
chooseTower(true); advance(1100); chooseTower(true); advance(1100);
assert.equal(findAll("tower-floor").length, 2);
assert.equal(find("tower-stack").children[0].children[0].textContent, "2", "new floor on top");
chooseTower(false);
assert.equal(findAll("tower-floor").length, 1);
assert.equal(find("tower-scene").attrs["aria-label"], "Kule: 1 kat. En yüksek: 2 kat.");
key("p"); advance(5000); assert(findAll("ans").every(b => b.disabled));
key("p"); advance(2200); chooseTower(false); advance(2200); chooseTower(false); advance(2200);
assert(find("result")); assert(text(find("result")).includes("Canlar bitti. Kulen: 0 kat · En yüksek: 2 kat"));
assert.equal(findAll("tower-floor").length, 0);
assert.equal(frames.size, 0);
ctx.restart();
for (let n = 0; n < 15; n++) { chooseTower(true); advance(1100); }
assert.equal(findAll("tower-floor").length, 15);
assert(text(find("result")).includes("Kulen: 15 kat · En yüksek: 15 kat"));
assert(find("tower-summit")); assert.equal(frames.size, 0);
ctx.restart(); chooseTower(true); ctx.restart(); advance(1100);
assert.equal(findAll("tower-floor").length, 0, "old delayed answer cannot alter restarted tower");
assert.equal(frames.size, 1); win.emit("hashchange"); assert.equal(frames.size, 0);
assert.equal(win.events.keydown.size, 0);
console.log(`PASS: ${units} units; three arcade modes, both motion settings, scores/lives, pause, visibility, timeout, victory, picture fallback, restart/exit; tower order, damage, height, defeat and 15-floor victory.`);
