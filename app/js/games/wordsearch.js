/* Kelime Avı - drag across letters to find the unit's words ----------------- */
import { Game } from "./engine.js";
import { el, sample } from "../ui.js";

const SIZE = 12;
const DIRS = [[1, 0], [0, 1], [1, 1], [1, -1], [-1, 0], [0, -1], [-1, -1], [-1, 1]];
const ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

function place(grid, word) {
  for (let tries = 0; tries < 220; tries++) {
    const [dx, dy] = DIRS[Math.floor(Math.random() * DIRS.length)];
    const x = Math.floor(Math.random() * SIZE);
    const y = Math.floor(Math.random() * SIZE);
    const ex = x + dx * (word.length - 1);
    const ey = y + dy * (word.length - 1);
    if (ex < 0 || ey < 0 || ex >= SIZE || ey >= SIZE) continue;
    let ok = true;
    for (let i = 0; i < word.length; i++) {
      const c = grid[y + dy * i][x + dx * i];
      if (c && c !== word[i]) { ok = false; break; }
    }
    if (!ok) continue;
    const cells = [];
    for (let i = 0; i < word.length; i++) {
      grid[y + dy * i][x + dx * i] = word[i];
      cells.push((y + dy * i) * SIZE + (x + dx * i));
    }
    return cells;
  }
  return null;
}

export function start(ctx) {
  const candidates = ctx.bank.words
    .filter((w) => /^[a-zA-Z ]{3,11}$/.test(w.en))
    .map((w) => ({ ...w, key: w.en.replace(/\s+/g, "").toUpperCase() }));

  const grid = Array.from({ length: SIZE }, () => Array(SIZE).fill(""));
  const placed = [];
  for (const w of sample(candidates, 20)) {
    if (placed.length >= 8) break;
    if (placed.some((p) => p.key === w.key)) continue;
    const cells = place(grid, w.key);
    if (cells) placed.push({ ...w, cells: new Set(cells) });
  }
  for (let y = 0; y < SIZE; y++)
    for (let x = 0; x < SIZE; x++)
      if (!grid[y][x]) grid[y][x] = ALPHA[Math.floor(Math.random() * 26)];

  const game = new Game({
    screen: ctx.screen, title: ctx.title, total: placed.length,
    time: 180, backHash: ctx.backHash, onRestart: ctx.restart,
  });

  const cellNodes = [];
  const gridNode = el("div", {
    class: "ws-grid",
    style: `grid-template-columns:repeat(${SIZE},auto)`,
  });
  for (let i = 0; i < SIZE * SIZE; i++) {
    const n = el("div", { class: "ws-cell", text: grid[Math.floor(i / SIZE)][i % SIZE], "data-i": i });
    cellNodes.push(n);
    gridNode.append(n);
  }

  const wordNodes = new Map();
  const listNode = el("div", { class: "ws-words" }, placed.map((p) => {
    const n = el("div", {}, [el("b", { text: p.en }), el("small", { text: p.tr })]);
    wordNodes.set(p.key, n);
    return n;
  }));

  game.stage.replaceChildren(el("div", { class: "ws-wrap" }, [gridNode, listNode]));

  /* selection: pointer down -> move -> up, constrained to a straight line */
  let anchor = null, current = [];

  const clearSel = () => cellNodes.forEach((n) => n.classList.remove("sel"));

  function lineFrom(a, b) {
    const ax = a % SIZE, ay = Math.floor(a / SIZE);
    const bx = b % SIZE, by = Math.floor(b / SIZE);
    const dx = Math.sign(bx - ax), dy = Math.sign(by - ay);
    const len = Math.max(Math.abs(bx - ax), Math.abs(by - ay));
    if (dx && dy && Math.abs(bx - ax) !== Math.abs(by - ay)) return null;
    const out = [];
    for (let i = 0; i <= len; i++) out.push((ay + dy * i) * SIZE + (ax + dx * i));
    return out;
  }

  gridNode.addEventListener("pointerdown", (e) => {
    const t = e.target.closest(".ws-cell");
    if (!t) return;
    anchor = +t.dataset.i;
    current = [anchor];
    clearSel();
    t.classList.add("sel");
    gridNode.setPointerCapture(e.pointerId);
  });

  gridNode.addEventListener("pointermove", (e) => {
    if (anchor === null) return;
    const t = document.elementFromPoint(e.clientX, e.clientY)?.closest(".ws-cell");
    if (!t) return;
    const line = lineFrom(anchor, +t.dataset.i);
    if (!line) return;
    current = line;
    clearSel();
    for (const i of line) cellNodes[i].classList.add("sel");
  });

  const settle = () => {
    if (anchor === null) return;
    const word = current.map((i) => cellNodes[i].textContent).join("");
    const rev = [...word].reverse().join("");
    const hit = placed.find((p) => !p.found && (p.key === word || p.key === rev));
    if (hit) {
      hit.found = true;
      for (const i of current) cellNodes[i].classList.add("found");
      wordNodes.get(hit.key).classList.add("hit");
      game.hit(15);
      game.step();
      if (placed.every((p) => p.found)) game.finish("Bütün kelimeler bulundu!");
    } else if (current.length > 1) {
      game.miss();
    }
    clearSel();
    anchor = null;
    current = [];
  };

  gridNode.addEventListener("pointerup", settle);
  gridNode.addEventListener("pointercancel", settle);
}
