/* catalog + per-unit data loading, with a small cache -----------------------
   Layout on disk:
     app/data/catalog.json
     content/<gid>/<uid>/presentation/slides.json
     content/<gid>/<uid>/games/bank.json
     content/<gid>/<uid>/worksheets/manifest.json
--------------------------------------------------------------------------- */

import { mergeGameLinks, gameLinkKey } from './game-resources.js';

const cache = new Map();

const REQUIRED = Symbol("required");

/** `fallback` is returned for any failure; pass REQUIRED to let errors bubble. */
async function loadJSON(url, fallback = REQUIRED) {
  if (cache.has(url)) return cache.get(url);
  const p = fetch(url, { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.status))))
    .catch((err) => {
      if (fallback !== REQUIRED) return fallback;
      throw err;
    });
  cache.set(url, p);
  return p;
}

const EMPTY_CATALOG = { generated: null, grades: [] };

export async function getCatalog() {
  const cat = await loadJSON("/app/data/catalog.json", EMPTY_CATALOG);
  if (!cat.grades.length) {
    throw new Error("Katalog bulunamadı. tools/fetch_catalog.py çalıştırılmalı.");
  }
  return cat;
}

export function unitPath(gid, uid) {
  return `/content/${gid}/${uid}`;
}

export async function getUnit(gid, uid) {
  const cat = await getCatalog();
  const grade = cat.grades.find((g) => g.id === gid);
  if (!grade) throw new Error("Sınıf bulunamadı: " + gid);
  const unit = grade.units.find((u) => u.id === uid);
  if (!unit) throw new Error("Ünite bulunamadı: " + uid);
  return { catalog: cat, grade, unit };
}

export function getSlides(gid, uid) {
  return loadJSON(`${unitPath(gid, uid)}/presentation/slides.json`, null);
}

export async function getBank(gid, uid) {
  const [bank, sources] = await Promise.all([
    loadJSON(`${unitPath(gid, uid)}/games/bank.json`, { sets: [], words: [], online: [] }),
    loadJSON('/app/data/game-sources.json', { units: {}, thumbnails: {} }),
  ]);
  const sumeyye = (sources.units[`${gid}/${uid}`] || []).map((item) => {
    const key = gameLinkKey(item.link);
    return {
      ...item,
      coverImage: item.coverImage || sources.thumbnails[key]?.coverImage,
    };
  });
  const online = mergeGameLinks(bank.online || [], [], sources.thumbnails);
  return { ...bank, online, sumeyye };
}

export async function getStarterWords(gid, uid) {
  const data = await loadJSON("/app/data/sharpshooter-words.json", { units: {} });
  return data.units[`${gid}/${uid}`] || [];
}

export async function getWorksheets(gid, uid) {
  const [man, sources] = await Promise.all([
    loadJSON(`${unitPath(gid, uid)}/worksheets/manifest.json`, { items: [] }),
    loadJSON("/app/data/worksheet-sources.json", { units: {} }),
  ]);
  const all = sources.units[`${gid}/${uid}`] || [];
  const ingilizcecin = all.filter((item) => item.source === "ingilizcecin");
  const dersingilizce = all.filter((item) => item.source === "dersingilizce");
  const mebOdsgm = all.filter((item) => item.source === "meb-odsgm");
  return { ...man, ingilizcecin, dersingilizce, mebOdsgm };
}

/** Offline copies of the source's static activities (games + slide sites). */
export async function getSites(gid, uid, kind) {
  const man = await loadJSON(`${unitPath(gid, uid)}/sites/manifest.json`, { items: [] });
  const items = (man.items || []).filter((i) => i.path && (!kind || i.kind === kind));
  const sources = kind === 'game' ? await loadJSON('/app/data/game-sources.json', { thumbnails: {} }) : { thumbnails: {} };
  return items.map((i) => ({ ...i, coverImage: i.coverImage || sources.thumbnails[gameLinkKey(i.link)]?.coverImage,
    url: `${unitPath(gid, uid)}/sites/${i.path}` }));
}

/** LGS exam resources from ingilizceciyiz and dersingilizce */
export async function getLgsSources() {
  return loadJSON("/app/data/lgs-sources.json", { sources: [], counts: { total: 0 } });
}

/** Ask the local server to open a file with its associated desktop app. */
export async function openLocal(relPath) {
  const r = await fetch("/api/open?path=" + encodeURIComponent(relPath));
  const j = await r.json().catch(() => ({ ok: false }));
  if (!j.ok) throw new Error(j.error || "açılamadı");
  return true;
}
