/* Public game links and their publisher-provided previews. No remote players load here. */
import { el } from './ui.js';

export function gameLinkKey(link) {
  try { const u = new URL(link); u.hash = ''; u.pathname = u.pathname.replace(/\/+$/, ''); return u.href.replace(/\/$/, ''); }
  catch { return String(link || ''); }
}

export function mergeGameLinks(items, additions = [], thumbnails = {}) {
  const merged = new Map();
  for (const item of [...items, ...additions]) {
    const key = gameLinkKey(item.link);
    if (!/^https?:\/\//.test(key)) continue;
    const prior = merged.get(key) || {};
    const preview = thumbnails[key]?.coverImage;
    merged.set(key, { ...prior, ...item, coverImage: item.coverImage || prior.coverImage || preview });
  }
  return [...merged.values()];
}

export function sourceGameCard(item, offline = false) {
  const link = offline ? item.url : item.link;
  let publisher = '';
  try { publisher = new URL(item.link).hostname.replace(/^www\./, ''); } catch { /* local-only card */ }
  const preview = el('div', { class: 'game-preview' }, [
    el('span', { class: 'game-preview-fallback', 'aria-hidden': 'true', text: offline ? '🕹️' : '🎮' }),
    el('span', { class: 'game-resource-badge', text: offline ? 'Çevrimdışı' : 'Çevrimiçi' }),
  ]);
  const cover = item.coverImage;
  if (typeof cover === 'string' && /^(https?:\/\/|\/app\/|\/content\/)/.test(cover)) {
    const img = el('img', { src: cover, alt: '', loading: 'lazy', decoding: 'async', referrerpolicy: 'no-referrer' });
    img.addEventListener('load', () => preview.classList.add('has-image'));
    img.addEventListener('error', () => { img.remove(); preview.classList.remove('has-image'); });
    preview.prepend(img);
  }
  return el('a', { class: 'source-game-card', href: link, target: '_blank', rel: 'noopener noreferrer' }, [
    preview,
    el('div', { class: 'game-resource-copy' }, [
      el('h3', { text: item.title }),
      el('p', { text: item.by || publisher }),
      el('span', { class: 'game-resource-open', text: offline ? 'Oyunu aç ▶' : 'Kaynakta oyna ↗' }),
    ]),
  ]);
}

export function onlineGameGallery(items) {
  const grid = el('div', { class: 'source-game-grid' });
  const cards = items.map(item => ({ item, node: sourceGameCard(item) }));
  grid.append(...cards.map(c => c.node));
  const result = el('p', { class: 'game-search-result', role: 'status', 'aria-live': 'polite' });
  const input = el('input', { type: 'search', class: 'game-search', placeholder: 'Oyun veya hazırlayan ara…', 'aria-label': 'Çevrimiçi oyun ara' });
  input.addEventListener('input', () => {
    const query = input.value.trim().toLocaleLowerCase('tr'); let count = 0;
    for (const { item, node } of cards) {
      node.hidden = !`${item.title} ${item.by || ''} ${item.link}`.toLocaleLowerCase('tr').includes(query);
      if (!node.hidden) count++;
    }
    result.textContent = query ? `${count} oyun bulundu` : '';
  });
  return el('section', { class: 'online-game-gallery' }, [input, result, grid]);
}
