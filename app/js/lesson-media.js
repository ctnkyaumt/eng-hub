import { el } from "./ui.js";

export function mediaUrl(name, ctx) {
  return /^(https:\/\/|\/)/.test(name) ? name : (ctx?.base || "") + "img/" + name;
}

export function lessonImage(item, ctx, className, alt = "") {
  const img = el("img", {
    class: className, src: mediaUrl(item.img, ctx), alt,
    decoding: "async", referrerpolicy: "no-referrer",
    "data-fit": "contain",
  });
  img.addEventListener("error", () => {
    img.dispatchEvent(new CustomEvent("imageunavailable", { bubbles: true }));
    const retry = el("button", { type: "button", class: className + " image-unavailable", text: "Görsel yüklenemedi · Yeniden dene",
      onclick: () => retry.replaceWith(lessonImage(item, ctx, className, alt)),
    });
    img.replaceWith(retry);
  }, { once: true });
  img.addEventListener("load", () => img.dispatchEvent(new CustomEvent("imageready", { bubbles: true })), { once: true });
  return img;
}
