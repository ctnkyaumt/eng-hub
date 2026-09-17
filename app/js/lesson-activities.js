/* Local classroom activities: mouse, touch and native button keyboard support. */
import { el, shuffle, beep } from "./ui.js";

const button = (text, onclick, cls = "opt") => el("button", { type: "button", class: cls, text, onclick });
const feedback = () => el("div", { class: "verdict", role: "status", "aria-live": "polite" });
function tell(node, ok, text) {
  node.className = `verdict ${ok ? "ok" : "no"}`; node.textContent = text; beep(ok ? "ok" : "bad");
}
function shell(t, cls, hint) {
  return el("div", { class: `task local-activity ${cls}` }, [
    el("div", { class: "prompt", text: t.q }), el("p", { class: "hint", text: hint }),
  ]);
}
function draggable(node, id, choose) {
  node.draggable = true;
  node.addEventListener("dragstart", e => {
    if (node.disabled) { e.preventDefault(); return; }
    choose(); e.dataTransfer.setData("text/plain", String(id)); e.dataTransfer.effectAllowed = "move";
  });
}
function droppable(node, accept) {
  node.addEventListener("dragover", e => { e.preventDefault(); });
  node.addEventListener("drop", e => { e.preventDefault(); accept(); });
}

export function wordPairsTask(t) {
  const root = shell(t, "wordpairs-task", "Turn over two cards. Find all the pairs. You can also use Tab and Enter.");
  const board = el("div", { class: "pairs-board" }), info = feedback();
  const progress = el("div", { class: "activity-score", role: "status" });
  const pairs = (t.pairs || []).slice(0, 6);
  let open = [], found = 0, tries = 0;
  function reset() {
    open = []; found = 0; tries = 0; info.textContent = "";
    const update = () => { progress.textContent = `${found} / ${pairs.length} pairs · ${tries} turns`; };
    board.replaceChildren(...shuffle(pairs.flatMap((p, id) => [
      { id, text: p.a, lang: "EN" }, { id, text: p.b, lang: "TR" },
    ])).map((card, index) => {
      const tile = button("", () => {
        if (tile.disabled || open.some(c => c.tile === tile)) return;
        if (open.length === 2) { open.forEach(c => { c.tile.classList.remove("flipped"); c.tile.setAttribute("aria-label", `Card ${c.index + 1}`); }); open = []; }
        tile.classList.add("flipped"); tile.setAttribute("aria-label", `${card.lang}: ${card.text}`);
        open.push({ ...card, tile, index });
        if (open.length === 2) {
          tries++;
          if (open[0].id === open[1].id) {
            found++; open.forEach(c => { c.tile.disabled = true; c.tile.classList.add("matched"); }); open = [];
            tell(info, true, found === pairs.length ? "All pairs found! Play again to practise." : "A match! Find the next pair.");
          } else tell(info, false, "Remember these cards. Turn over another card to try again.");
          update();
        }
      }, "pair-card");
      tile.setAttribute("aria-label", `Card ${index + 1}`);
      tile.append(el("span", { class: "pair-back", "aria-hidden": "true", text: index + 1 }),
        el("span", { class: "pair-front", "aria-hidden": "true" }, [el("small", { text: card.lang }), el("b", { text: card.text })]));
      return tile;
    })); update();
  }
  root.append(progress, board, info, button("Play again", reset, "opt reset-action")); reset(); return root;
}

export function groupSortTask(t) {
  const root = shell(t, "groupsort-task", "Tap a word, then a group. You can also drag words into their groups.");
  const bank = el("div", { class: "sort-bank" }), bins = el("div", { class: "sort-groups" }), info = feedback();
  const progress = el("div", { class: "activity-score" });
  let selected = null, solved = 0, tiles = [];
  function reset() {
    selected = null; solved = 0; info.textContent = ""; bins.replaceChildren();
    const rows = (t.groups || []).flatMap((g, group) => g.items.map(text => ({ text, group })));
    const update = () => { progress.textContent = `${solved} / ${rows.length} sorted`; };
    tiles = shuffle(rows).map((item, id) => {
      const choose = () => {
        if (node.disabled) return;
        selected = { item, node }; tiles.forEach(n => { n.classList.toggle("selected", n === node); n.setAttribute("aria-pressed", String(n === node)); });
        info.textContent = `“${item.text}” selected. Choose a group.`;
      };
      const node = button(item.text, choose, "opt sort-word"); node.setAttribute("aria-pressed", "false");
      draggable(node, id, choose); return node;
    });
    bank.replaceChildren(...tiles);
    (t.groups || []).forEach((g, group) => {
      const placed = el("div", { class: "sorted-words" });
      const accept = () => {
        if (!selected) { info.textContent = "Choose a word first."; return; }
        if (selected.item.group !== group) { tell(info, false, "Try another group. The word stays selected."); return; }
        placed.append(el("span", { class: "sorted-word", text: selected.item.text }));
        selected.node.disabled = true; selected.node.classList.remove("selected"); selected.node.classList.add("used");
        selected.node.setAttribute("aria-pressed", "false"); selected = null; solved++; update();
        tell(info, true, solved === rows.length ? "Every word is in the right group!" : "Correct group!");
      };
      const target = button(g.label, accept, "sort-group-title");
      const bin = el("section", { class: "sort-bin", "aria-label": g.label }, [target, placed]);
      droppable(bin, accept); bins.append(bin);
    }); update();
  }
  root.append(progress, bank, bins, info, button("Start again", reset, "opt reset-action")); reset(); return root;
}

export function clozeTask(t) {
  const root = shell(t, "cloze-task", "Tap a word, then a gap, or drag it. Tap a filled gap to return its word.");
  const sentences = (t.sentences || []).slice(0, 5);
  const lines = el("div", { class: "cloze-lines" }), bank = el("div", { class: "cloze-bank" }), info = feedback();
  const actions = el("div", { class: "activity-actions" });
  let selected = null, assigned = [], tiles = [], blanks = [], translations = [], complete = false;
  function reset() {
    selected = null; assigned = sentences.map(() => null); complete = false; info.textContent = "";
    translations = []; blanks = []; lines.replaceChildren(); actions.replaceChildren();
    const rows = sentences.map((s, id) => ({ text: s.answer, id }));
    tiles = rows.map(item => {
      const choose = () => {
        if (node.disabled || complete) return;
        selected = item.id; tiles.forEach((n, id) => { n.classList.toggle("selected", id === selected); n.setAttribute("aria-pressed", String(id === selected)); });
        info.textContent = `“${item.text}” selected. Choose a gap.`;
      };
      const node = button(item.text, choose, "opt cloze-word"); node.setAttribute("aria-pressed", "false");
      draggable(node, item.id, choose); return node;
    });
    bank.replaceChildren(...shuffle(tiles));
    sentences.forEach((sentence, index) => {
      const place = () => {
        if (complete) return;
        const old = assigned[index];
        if (old !== null) { tiles[old].disabled = false; tiles[old].classList.remove("used"); }
        assigned[index] = selected;
        if (selected !== null) { tiles[selected].disabled = true; tiles[selected].classList.add("used"); }
        gap.textContent = selected === null ? "…" : rows[selected].text;
        gap.setAttribute("aria-label", `Gap ${index + 1}: ${gap.textContent}`);
        gap.classList.remove("wrong", "right"); gap.classList.toggle("filled", selected !== null);
        selected = null; tiles.forEach(n => { n.classList.remove("selected"); n.setAttribute("aria-pressed", "false"); });
      };
      const gap = button("…", place, "cloze-gap"); gap.setAttribute("aria-label", `Gap ${index + 1}`); droppable(gap, place); blanks.push(gap);
      const [before, ...after] = sentence.text.split("___");
      const tr = el("p", { class: "cloze-translation", text: sentence.tr || "", hidden: "hidden" }); translations.push(tr);
      lines.append(el("div", { class: "cloze-row" }, [el("small", { text: index + 1 }), el("div", {}, [
        el("div", { class: "cloze-sentence" }, [before, gap, after.join("___")]), tr,
      ])]));
    });
    const check = button("Check answers", () => {
      if (assigned.some(id => id === null)) { tell(info, false, "Fill every gap before checking."); return; }
      let correct = 0;
      blanks.forEach((gap, index) => {
        const ok = rows[assigned[index]].text === sentences[index].answer;
        gap.classList.toggle("right", ok); gap.classList.toggle("wrong", !ok); if (ok) correct++;
      });
      complete = correct === sentences.length;
      tell(info, complete, complete ? "All correct! Read the complete sentences aloud." : `${correct} / ${sentences.length} correct. Tap a gap to change its word.`);
      if (complete) {
        check.disabled = true; blanks.forEach(n => { n.disabled = true; });
        if (sentences.some(s => s.tr)) actions.append(button("Show Turkish meanings", e => {
          translations.forEach(n => { n.hidden = false; }); e.currentTarget.disabled = true;
        }));
      }
    });
    actions.append(check, button("Start again", reset));
  }
  root.append(lines, bank, actions, info); reset(); return root;
}

export function quizBoxTask(t) {
  const root = shell(t, "quizbox-task", "Answer aloud before revealing the model. Mark your answer, then choose another box.");
  const boxes = el("div", { class: "question-boxes" }), panel = el("div", { class: "question-panel" });
  const progress = el("div", { class: "activity-score", role: "status" });
  const questions = (t.questions || []).slice(0, 8); let results = [];
  function reset() {
    results = questions.map(() => null); panel.replaceChildren();
    const update = () => {
      const count = results.filter(r => r !== null).length, correct = results.filter(r => r === true).length;
      progress.textContent = `${count} / ${questions.length} answered · ${correct} correct${count === questions.length ? " · Reopen a review box or play again." : ""}`;
    };
    boxes.replaceChildren(...questions.map((q, index) => {
      const box = button(String(index + 1), () => {
        [...boxes.children].forEach(n => { n.classList.remove("selected"); n.setAttribute("aria-pressed", "false"); });
        box.classList.add("selected"); box.setAttribute("aria-pressed", "true");
        const model = el("div", { class: "box-answer", hidden: "hidden", text: q.answer });
        const tr = el("div", { class: "box-translation", hidden: "hidden", text: q.tr || "" });
        const mark = el("div", { class: "activity-actions", hidden: "hidden" });
        const record = correct => {
          results[index] = correct; box.classList.toggle("answered", correct); box.classList.toggle("review", !correct);
          box.textContent = `${index + 1} ${correct ? "✓" : "↻"}`;
          box.setAttribute("aria-label", `Question ${index + 1}: ${correct ? "correct" : "review"}`);
          panel.replaceChildren(el("p", { text: correct ? "Good work. Choose another box." : "Read the model again, then reopen this box to practise." }), el("div", { class: "box-answer", text: q.answer })); update();
        };
        mark.append(button("I got it", () => record(true)), button("Practise again", () => record(false)));
        const reveal = button("Reveal model answer", e => {
          model.hidden = false; mark.hidden = false; e.currentTarget.disabled = true; beep("ok");
          if (q.tr) mark.prepend(button("Turkish meaning", e => { tr.hidden = false; e.currentTarget.disabled = true; }));
        });
        panel.replaceChildren(el("small", { text: `QUESTION ${index + 1}` }), el("p", { class: "box-question", text: q.q }), reveal, model, tr, mark);
      }, "question-box");
      box.setAttribute("aria-label", `Question ${index + 1}`); box.setAttribute("aria-pressed", "false"); return box;
    })); update();
  }
  root.append(progress, boxes, panel, button("Play again", reset, "opt reset-action")); reset(); return root;
}
