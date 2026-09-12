/* All worksheets and tests open online or require internet. */
import { getUnit, getWorksheets, unitPath } from "./store.js";
import { el, setCrumbs } from "./ui.js";

export async function worksheetList(gid, uid, screen) {
  const { grade, unit } = await getUnit(gid, uid);
  const unitLabel = unit.no ? `${unit.label || "Ünite"} ${unit.no}` : (unit.label || "Revizyon");
  const man = await getWorksheets(gid, uid);
  setCrumbs([
    { label: "Ana Menü", hash: "#/" },
    { label: grade.title, hash: `#/${gid}` },
    { label: unitLabel, hash: `#/${gid}/${uid}` },
    { label: "Çalışma Kâğıtları ve Testler" },
  ]);

  const items = man.items || [];

  const hero = el("div", { class: "hero" }, [
    el("span", { class: "kicker", text: `${grade.title} · ${unitLabel} · ${unit.title}` }),
    el("h1", { text: "Çalışma Kâğıtları ve Testler" }),
    el("p", { text: "Tüm çalışma kâğıtları ve testler için internet bağlantısı gerekir." }),
  ]);

  const parts = [hero];

  if (!items.length) {
    parts.push(el("div", { class: "empty" }, [
      el("span", { class: "emoji", text: "📭" }),
      el("p", { text: "Bu ünite için çalışma kâğıdı veya test bulunamadı." }),
    ]));
  } else {
    const isQuiz = (it) => it.type === "quiz" || (!it.type && /\b(test|quiz|deneme)\b/i.test(it.title || ""));
    const quizzes = items.filter(isQuiz);
    const worksheets = items.filter((it) => !isQuiz(it));

    const openResource = (it) => {
      if (it.link) {
        window.open(it.link, "_blank", "noopener");
      } else if (it.file) {
        window.open(`${unitPath(gid, uid)}/worksheets/${encodeURIComponent(it.file)}`, "_blank", "noopener");
      }
    };

    const renderList = (title, list, icon) => {
      if (!list.length) return;
      parts.push(el("h2", { class: "section-title", text: `${title} · İnternet gerekli (${list.length})` }));
      parts.push(el("div", { class: "list" }, list.map((it) =>
        el("button", { class: "row", onclick: () => openResource(it) }, [
          el("span", { class: "ic", text: icon }),
          el("div", { class: "txt" }, [
            el("b", { text: it.title }),
            el("small", { text: [it.desc, it.by ? (it.by.startsWith("Hazırlayan:") ? it.by : "Hazırlayan: " + it.by) : null].filter(Boolean).join(" · ") }),
          ]),
          el("span", { class: "go", text: "↗" }),
        ])
      )));
    };

    renderList("Çalışma Kâğıtları", worksheets, "📄");
    renderList("Testler ve Quizler", quizzes, "📝");
  }

  screen.replaceChildren(...parts);
}
