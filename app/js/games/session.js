/* One owned animation clock: pause, delayed feedback and navigation cleanup. */
let stopPrevious = () => {};

export function createSession(game, { tick = () => {}, key = () => {}, onPause = () => {} } = {}) {
  stopPrevious();
  let active = true, paused = false, frame = 0, pending = null;
  let last = performance.now();
  const session = {
    get active() { return active; },
    get paused() { return paused; },
    after(seconds, fn) { pending = { seconds, fn }; },
    togglePause() {
      if (!active) return;
      paused = !paused;
      game.frame.classList.toggle("game-paused", paused);
      last = performance.now();
      onPause(paused);
    },
    stop() {
      active = false;
      pending = null;
      cancelAnimationFrame(frame);
      window.removeEventListener("keydown", keyboard);
      window.removeEventListener("hashchange", session.stop);
      document.removeEventListener("visibilitychange", visibility);
    },
  };
  function keyboard(e) {
    if (e.repeat || e.ctrlKey || e.metaKey || e.altKey ||
        e.target?.closest?.("input, textarea, select, [contenteditable=true]")) return;
    if (e.key.toLowerCase() === "p") { e.preventDefault(); session.togglePause(); }
    else if (!paused) key(e);
  }
  function visibility() { if (document.hidden && !paused) session.togglePause(); }
  function loop(now) {
    if (!active) return;
    if (!game.frame.isConnected) return session.stop();
    const dt = Math.min(.25, Math.max(0, (now - last) / 1000));
    last = now;
    if (!paused) {
      if (pending) {
        pending.seconds -= dt;
        if (pending.seconds <= 0) { const fn = pending.fn; pending = null; fn(); }
      } else tick(dt);
    }
    if (active) frame = requestAnimationFrame(loop);
  }
  stopPrevious = session.stop;
  window.addEventListener("keydown", keyboard);
  window.addEventListener("hashchange", session.stop);
  document.addEventListener("visibilitychange", visibility);
  visibility();
  frame = requestAnimationFrame(loop);
  return session;
}
