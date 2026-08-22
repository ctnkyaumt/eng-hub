/* Interactive practice tasks used by the "exercise" slide type ---------------
   kinds:  fill   - drop the right word into the gap
            order  - put the scrambled words in order
            choose - multiple choice
            match  - pair English with Turkish
            picture - identify an approved unit image
            truefalse - vote on a word or sentence claim
            flash  - think first, then reveal the answer
--------------------------------------------------------------------------- */
import { el, shuffle, beep } from "./ui.js";

export function taskNode(t, ctx) {
  switch (t.kind) {
    case "order": return orderTask(t);
    case "choose": return chooseTask(t);
    case "match": return matchTask(t);
    case "picture": return pictureTask(t, ctx);
    case "truefalse": return trueFalseTask(t);
    case "flash": return flashTask(t, ctx);
    default: return fillTask(t);
  }
}

/* ------------------------------------------------------- guess and reveal */
function flashTask(t, ctx) {
  const answer = el("div", { class: "flash-answer", text: t.answer || "" });
  const reveal = el("button", { class: "opt", text: "Reveal answer" });
  reveal.onclick = () => {
    answer.classList.add("open");
    reveal.disabled = true;
    beep("ok");
  };
  const picture = t.img
    ? el("img", {
        class: "task-pic",
        src: t.img.startsWith("/") ? t.img : (ctx?.base || "") + "img/" + t.img,
        alt: "",
      })
    : null;
  return el("div", { class: "task" }, [
    ...head(t, "Say your answer before you reveal it."),
    picture,
    t.clue ? el("div", { class: "tf-statement", text: t.clue }) : null,
    el("div", { class: "activity-actions" }, [reveal]),
    answer,
  ]);
}

/* ---------------------------------------------------------- true or false */
function trueFalseTask(t) {
  const v = verdict();
  const actions = el("div", { class: "activity-actions" });
  [[true, "True"], [false, "False"]].forEach(([value, label]) => {
    const b = el("button", { class: "opt", text: label });
    b.onclick = () => {
      const ok = value === Boolean(t.answer);
      [...actions.children].forEach((c) => (c.disabled = true));
      b.classList.add(ok ? "right" : "wrong");
      const correct = actions.children[Boolean(t.answer) ? 0 : 1];
      correct?.classList.add("right");
      say(v, ok, (ok ? "✔ Correct!" : "✘ Not quite.") + (t.explain ? "  " + t.explain : ""));
    };
    actions.append(b);
  });
  return el("div", { class: "task" }, [
    ...head(t, "Decide together, then choose."),
    el("div", { class: "tf-statement", text: t.statement || t.q || "" }),
    actions,
    v,
  ]);
}

/* ------------------------------------------------------- picture -> word */
function pictureTask(t, ctx) {
  const src = t.img.startsWith("/") ? t.img : (ctx?.base || "") + "img/" + t.img;
  const v = verdict();
  const opts = el("div", { class: "opts" });
  shuffle(t.options || []).forEach((o) => {
    const b = el("button", { class: "opt", text: o });
    b.onclick = () => {
      const ok = o === t.answer;
      b.classList.add(ok ? "right" : "wrong");
      if (ok) {
        [...opts.children].forEach((c) => (c.disabled = true));
        say(v, true, "✔ " + t.answer + (t.tr ? "  (" + t.tr + ")" : ""));
      } else {
        say(v, false, "✘ Try again");
        setTimeout(() => b.classList.remove("wrong"), 500);
      }
    };
    opts.append(b);
  });
  return el("div", { class: "task" }, [
    ...head(t, "Which word matches the picture?"),
    el("img", { class: "task-pic", src, alt: "" }),
    opts, v,
  ]);
}

function head(t, hint) {
  return [
    t.q ? el("div", { class: "prompt", text: t.q }) : null,
    el("div", { class: "hint", text: t.tr || hint }),
  ].filter(Boolean);
}

function verdict() {
  return el("div", { class: "verdict" });
}

function say(v, ok, msg) {
  v.textContent = msg;
  v.className = "verdict " + (ok ? "ok" : "no");
  beep(ok ? "ok" : "bad");
}

/* ---------------------------------------------------------------- fill gap */
function fillTask(t) {
  const parts = (t.text || "___").split("___");
  const blank = el("span", { class: "blank", text: "?" });
  const sentence = el("div", { class: "sentence" }, [
    parts[0] || "",
    blank,
    parts.slice(1).join("___") || "",
  ]);
  const v = verdict();
  const opts = el("div", { class: "opts" });

  shuffle(t.options || [t.answer]).forEach((o) => {
    const b = el("button", { class: "opt", text: o });
    b.onclick = () => {
      blank.textContent = o;
      blank.classList.add("filled");
      const ok = o === t.answer;
      b.classList.add(ok ? "right" : "wrong");
      if (ok) {
        [...opts.children].forEach((c) => (c.disabled = true));
        say(v, true, "✔ Correct!" + (t.tr ? "  " + t.tr : ""));
      } else {
        say(v, false, "✘ Try again");
        setTimeout(() => b.classList.remove("wrong"), 500);
      }
    };
    opts.append(b);
  });

  return el("div", { class: "task" }, [...head(t, "Choose the correct word for the gap."), sentence, opts, v]);
}

/* ------------------------------------------------------------ word ordering */
function orderTask(t) {
  const target = (t.answer || "").trim();
  const words = target.split(/\s+/);
  const line = el("div", { class: "sentence" });
  const pool = el("div", { class: "opts" });
  const v = verdict();
  const picked = [];

  const redraw = () => {
    line.replaceChildren(...picked.map((w, i) =>
      el("span", { class: "blank filled", text: w, style: "cursor:pointer",
                   onclick: () => { picked.splice(i, 1); redraw(); check(); } })
    ));
    if (!picked.length) line.append(el("span", { class: "blank", text: " " }));
  };

  function check() {
    if (picked.length < words.length) { v.textContent = ""; v.className = "verdict"; return; }
    const ok = picked.join(" ") === target;
    say(v, ok, ok ? "✔ Correct!" + (t.tr ? "  " + t.tr : "") : "✘ Wrong order — tap a word to take it back");
  }

  shuffle(words).forEach((w) => {
    const b = el("button", { class: "opt", text: w });
    b.onclick = () => { picked.push(w); b.classList.add("used"); redraw(); check(); };
    pool.append(b);
  });

  redraw();
  return el("div", { class: "task" },
    [...head(t, "Put the words in the correct order."), line, pool, v]);
}

/* ------------------------------------------------------------ multiple choice */
function chooseTask(t) {
  const v = verdict();
  const opts = el("div", { class: "opts" });
  shuffle(t.options || []).forEach((o) => {
    const b = el("button", { class: "opt", text: o });
    b.onclick = () => {
      const ok = o === t.answer;
      b.classList.add(ok ? "right" : "wrong");
      if (ok) {
        [...opts.children].forEach((c) => (c.disabled = true));
        say(v, true, "✔ Correct!" + (t.tr ? "  " + t.tr : ""));
      } else {
        say(v, false, "✘ Try again");
        setTimeout(() => b.classList.remove("wrong"), 500);
      }
    };
    opts.append(b);
  });
  return el("div", { class: "task" }, [...head(t, "Choose the correct option."), opts, v]);
}

/* ------------------------------------------------------------------- match */
function matchTask(t) {
  const pairs = (t.pairs || []).slice(0, 6);
  const v = verdict();
  const left = el("div", { class: "opts", style: "flex-direction:column" });
  const right = el("div", { class: "opts", style: "flex-direction:column" });
  let sel = null;
  let done = 0;

  shuffle(pairs).forEach((p) => {
    const b = el("button", { class: "opt", text: p.a, "data-k": p.a });
    b.onclick = () => {
      left.querySelectorAll(".opt").forEach((x) => x.classList.remove("selected"));
      sel = p.a;
      b.classList.add("selected");
    };
    left.append(b);
  });

  shuffle(pairs).forEach((p) => {
    const b = el("button", { class: "opt", text: p.b });
    b.onclick = () => {
      if (!sel) { say(v, false, "Pick a word on the left first"); return; }
      if (sel === p.a) {
        const lb = left.querySelector(`[data-k="${CSS.escape(sel)}"]`);
        lb.classList.remove("selected");
        lb.classList.add("used");
        b.classList.add("used");
        sel = null;
        done++;
        say(v, true, done >= pairs.length ? "✔ All matched!" : "✔ Good match");
      } else {
        b.classList.add("wrong");
        setTimeout(() => b.classList.remove("wrong"), 500);
        say(v, false, "✘ Not this one");
      }
    };
    right.append(b);
  });

  return el("div", { class: "task" }, [
    ...head(t, "Tap a word on the left, then its meaning on the right."),
    el("div", { class: "match-cols" }, [left, right]),
    v,
  ]);
}
