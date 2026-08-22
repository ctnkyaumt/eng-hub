/* Interactive practice tasks used by the "exercise" slide type ---------------
   kinds:  fill   - drop the right word into the gap
            order  - put the scrambled words in order
            choose - multiple choice
            match  - pair English with Turkish
            picture - identify an approved unit image
            truefalse - vote on a word or sentence claim
            flash  - think first, then reveal the answer
            dragmatch - drag picture cards onto word docks
            listenpicture - hear a word and identify its picture
            dragorder - drag words into complete unit sentences
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
    case "dragmatch": return dragMatchTask(t, ctx);
    case "listenpicture": return listenPictureTask(t, ctx);
    case "dragorder": return dragOrderTask(t);
    default: return fillTask(t);
  }
}

/** Speak only through an installed English system voice. We deliberately do
 * not fall back to a remote voice, so the USB lesson stays local and offline. */
export function speakEnglish(text) {
  const synth = window.speechSynthesis;
  if (!synth || !text) return false;
  const voice = synth.getVoices().find((v) => v.localService && /^en[-_]/i.test(v.lang));
  if (!voice) return false;
  synth.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.voice = voice;
  utterance.lang = voice.lang;
  utterance.rate = 0.82;
  utterance.pitch = 1;
  synth.speak(utterance);
  return true;
}

let spokenAudio = null;
async function playEnglish(item) {
  if (item.audio) {
    try {
      spokenAudio?.pause();
      spokenAudio = new Audio(item.audio);
      await spokenAudio.play();
      return true;
    } catch { /* fall through to an installed system voice */ }
  }
  return speakEnglish(item.en);
}

function mediaSrc(name, ctx) {
  return name.startsWith("/") ? name : (ctx?.base || "") + "img/" + name;
}

function visualNode(item, ctx, cls = "mission-picture") {
  if (item.img) return el("img", { class: cls, src: mediaSrc(item.img, ctx), alt: item.en || "" });
  if (item.num !== undefined) return el("span", { class: cls + " mission-number", text: item.num });
  return el("span", { class: cls + " mission-emoji", text: item.emoji || "🧩" });
}

/** Native drag for mouse plus a pointer ghost for touch screens. */
function makePictureDraggable(source, root, onDrop) {
  source.draggable = true;
  source.addEventListener("dragstart", (e) => {
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", source.dataset.key);
    source.classList.add("dragging");
  });
  source.addEventListener("dragend", () => source.classList.remove("dragging"));

  source.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "mouse" || source.disabled) return;
    e.preventDefault();
    const ghost = source.cloneNode(true);
    ghost.classList.add("drag-ghost");
    document.body.append(ghost);
    const move = (x, y) => {
      ghost.style.left = x + "px";
      ghost.style.top = y + "px";
    };
    move(e.clientX, e.clientY);
    const moving = (ev) => move(ev.clientX, ev.clientY);
    const up = (ev) => {
      document.removeEventListener("pointermove", moving);
      document.removeEventListener("pointerup", up);
      ghost.remove();
      const hit = document.elementFromPoint(ev.clientX, ev.clientY)?.closest(".drop-zone");
      if (hit && root.contains(hit)) onDrop(source.dataset.key, hit);
    };
    document.addEventListener("pointermove", moving);
    document.addEventListener("pointerup", up, { once: true });
  });
}

/* -------------------------------------------------- unit mission: pictures */
function dragMatchTask(t, ctx) {
  const root = el("div", { class: "task mission-task" });

  function renderBoard() {
    const items = (t.items || []).map((item, i) => ({ ...item, key: String(i) }));
    const v = verdict();
    const bank = el("div", { class: "drag-bank" });
    const docks = el("div", { class: "drop-docks" });
    let selected = null;
    let done = 0;

    function select(key) {
      selected = key;
      bank.querySelectorAll(".picture-drag").forEach((node) =>
        node.classList.toggle("selected", node.dataset.key === key)
      );
    }

    function attempt(key, dock) {
      const source = bank.querySelector(`[data-key="${CSS.escape(key)}"]`);
      if (!source || source.disabled || dock.classList.contains("right")) return;
      if (dock.dataset.key === key) {
        source.disabled = true;
        source.draggable = false;
        source.classList.remove("selected", "dragging");
        source.classList.add("used");
        dock.classList.add("right");
        dock.append(el("span", { class: "dock-check", text: "✓" }));
        selected = null;
        done++;
        say(v, true, done === items.length ? "✔ Mission complete — every picture is docked!" : "✔ Good match");
        if (done === items.length) beep("win");
      } else {
        dock.classList.add("wrong");
        source.classList.add("wrong");
        say(v, false, "✘ That picture belongs at a different word.");
        setTimeout(() => {
          dock.classList.remove("wrong");
          source.classList.remove("wrong");
        }, 550);
      }
    }

    shuffle(items).forEach((item) => {
      const card = el("button", {
        class: "picture-drag", type: "button", "data-key": item.key,
        title: "Drag this picture, or tap it and then tap a word.",
      }, [visualNode(item, ctx)]);
      card.onclick = () => select(item.key);
      makePictureDraggable(card, root, attempt);
      bank.append(card);
    });

    shuffle(items).forEach((item) => {
      const dock = el("button", {
        class: "drop-zone", type: "button", "data-key": item.key,
      }, [
        el("b", { text: item.en }),
        el("small", { text: item.tr || "" }),
      ]);
      dock.addEventListener("dragover", (e) => { e.preventDefault(); dock.classList.add("over"); });
      dock.addEventListener("dragleave", () => dock.classList.remove("over"));
      dock.addEventListener("drop", (e) => {
        e.preventDefault();
        dock.classList.remove("over");
        attempt(e.dataTransfer.getData("text/plain"), dock);
      });
      dock.onclick = () => {
        if (selected !== null) attempt(selected, dock);
        else say(v, false, "Choose a picture first, then choose its word.");
      };
      docks.append(dock);
    });

    root.replaceChildren(
      ...head(t, "Drag with a mouse or finger. You can also tap a picture, then tap its word."),
      el("div", { class: "mission-board" }, [bank, docks]),
      v,
      el("div", { class: "activity-actions reset-action" }, [
        el("button", { class: "opt", text: "Reset board", onclick: renderBoard }),
      ])
    );
  }

  renderBoard();
  return root;
}

/* ----------------------------------------------------- unit mission: sound */
function listenPictureTask(t, ctx) {
  const items = shuffle(t.items || []);
  const root = el("div", { class: "task mission-task listen-mission" });
  let round = 0;

  function renderRound() {
    const target = items[round];
    const v = verdict();
    const choices = el("div", { class: "listen-choices" });
    const fallback = el("div", { class: "listen-fallback" });
    const progress = el("div", { class: "mission-progress", text: `Round ${round + 1} / ${items.length}` });
    const listen = el("button", { class: "listen-button", text: "🔊 Listen" });
    listen.onclick = async () => {
      if (await playEnglish(target)) {
        fallback.textContent = "Listen again whenever you need.";
        fallback.classList.remove("show-word");
      } else {
        fallback.textContent = `No offline English voice is installed. Teacher reads: “${target.en}”.`;
        fallback.classList.add("show-word");
        beep("tick");
      }
    };

    shuffle(items).forEach((item) => {
      const b = el("button", { class: "listen-choice", type: "button", title: "Choose this picture" }, [
        visualNode(item, ctx),
        el("span", { class: "listen-label", text: item.en }),
      ]);
      b.onclick = () => {
        const ok = item.en === target.en;
        b.classList.add(ok ? "right" : "wrong");
        if (!ok) {
          say(v, false, "✘ Listen once more and try again.");
          setTimeout(() => b.classList.remove("wrong"), 550);
          return;
        }
        choices.querySelectorAll("button").forEach((node) => (node.disabled = true));
        choices.classList.add("reveal-labels");
        say(v, true, `✔ ${target.en}${target.tr ? " — " + target.tr : ""}`);
        if (round === items.length - 1) {
          v.textContent += "  Mission complete!";
          beep("win");
        } else {
          const next = el("button", { class: "opt", text: "Next sound →" });
          next.onclick = () => { round++; renderRound(); };
          actions.append(next);
        }
      };
      choices.append(b);
    });

    const actions = el("div", { class: "activity-actions mission-actions" }, [listen]);
    root.replaceChildren(
      ...head(t, "The word plays from a bundled offline recording."),
      el("div", { class: "listen-toolbar" }, [progress, actions]),
      fallback,
      choices,
      v
    );
  }

  renderRound();
  return root;
}

/* -------------------------------------------------- unit mission: sentence */
function dragOrderTask(t) {
  const rounds = t.sentences || [];
  const root = el("div", { class: "task mission-task sentence-mission" });
  let round = 0;

  function renderSentence() {
    const current = rounds[round] || { answer: "", tr: "" };
    const target = current.answer.trim();
    const words = target.split(/\s+/).map((word, i) => ({ word, key: `${round}-${i}` }));
    const pool = el("div", { class: "word-pool word-drop-area" });
    const lane = el("div", { class: "word-lane word-drop-area" });
    const v = verdict();
    const progress = el("div", { class: "mission-progress", text: `Sentence ${round + 1} / ${rounds.length}` });

    function moveToken(token, destination, before = null) {
      if (before && before !== token) destination.insertBefore(token, before);
      else destination.append(token);
      lane.classList.remove("wrong");
      v.textContent = "";
      v.className = "verdict";
    }

    function wireDrop(area) {
      area.addEventListener("dragover", (e) => { e.preventDefault(); area.classList.add("over"); });
      area.addEventListener("dragleave", () => area.classList.remove("over"));
      area.addEventListener("drop", (e) => {
        e.preventDefault();
        area.classList.remove("over");
        const token = root.querySelector(`[data-token="${CSS.escape(e.dataTransfer.getData("text/plain"))}"]`);
        const before = e.target.closest(".drag-token");
        if (token) moveToken(token, area, before);
      });
    }

    wireDrop(pool);
    wireDrop(lane);
    shuffle(words).forEach(({ word, key }) => {
      const token = el("button", {
        class: "drag-token", type: "button", draggable: "true",
        "data-token": key, text: word,
        title: "Drag this word, or tap it to move it.",
      });
      token.addEventListener("dragstart", (e) => {
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", key);
        token.classList.add("dragging");
      });
      token.addEventListener("dragend", () => token.classList.remove("dragging"));
      token.onclick = () => moveToken(token, token.parentElement === pool ? lane : pool);
      pool.append(token);
    });

    const actions = el("div", { class: "activity-actions mission-actions" });
    const check = el("button", { class: "opt primary-action", text: "Check sentence" });
    check.onclick = () => {
      const answer = [...lane.querySelectorAll(".drag-token")].map((node) => node.textContent).join(" ");
      const ok = answer === target;
      if (!ok) {
        lane.classList.add("wrong");
        say(v, false, pool.children.length ? "Move every word into the sentence lane." : "The words are not in the right order yet.");
        return;
      }
      lane.classList.add("right");
      pool.querySelectorAll("button").forEach((node) => (node.disabled = true));
      lane.querySelectorAll("button").forEach((node) => (node.disabled = true));
      check.disabled = true;
      say(v, true, "✔ Correct!" + (current.tr ? "  " + current.tr : ""));
      if (round === rounds.length - 1) {
        v.textContent += "  Mission complete!";
        beep("win");
      } else {
        const next = el("button", { class: "opt", text: "Next sentence →" });
        next.onclick = () => { round++; renderSentence(); };
        actions.append(next);
      }
    };
    const reset = el("button", { class: "opt", text: "Shuffle again", onclick: renderSentence });
    actions.append(check, reset);

    root.replaceChildren(
      ...head(t, "Drag words into the lane. On touch screens, tap a word to move it."),
      progress,
      el("div", { class: "sentence-lane-label", text: "YOUR SENTENCE" }),
      lane,
      el("div", { class: "sentence-lane-label", text: "WORD BANK" }),
      pool,
      actions,
      v
    );
  }

  renderSentence();
  return root;
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
