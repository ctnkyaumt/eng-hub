/* No build: data coverage plus deterministic gameplay/lifecycle probes. */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const read = (p, fallback) => fs.existsSync(path.join(root,p)) ? JSON.parse(fs.readFileSync(path.join(root,p),"utf8")) : fallback;
const { rounds, start } = await import("../app/js/games/sharpshooter.js");
const catalog = read("app/data/catalog.json");
const seed = read("app/data/sharpshooter-words.json").units;
let units = 0;
for (const g of catalog.grades) for (const u of g.units) {
  const key = `${g.id}/${u.id}`;
  const bank = read(`content/${key}/games/bank.json`,{sets:[],words:[]});
  const slides = read(`content/${key}/presentation/slides.json`,{slides:[]});
  const words = new Map((bank.words||[]).map(w=>[w.en.toLowerCase(),w]));
  for (const s of slides.slides) for(const w of s.items||[]) if(w.en && w.tr) words.set(w.en.toLowerCase(),w);
  if(words.size<4) for(const w of seed[key]||[]) words.set(w.en.toLowerCase(),w);
  for(let run=0;run<10;run++) {
    const result = rounds({words:[...words.values()],questions:bank.sets.flatMap(s=>s.questions)});
    assert(result.length>=4,`${key}: insufficient shooter data`);
    for(const q of result) {
      assert.equal(q.a.filter(a=>a.c).length,1);
      assert(q.a.length>=2 && q.a.length<=4);
      assert.equal(new Set(q.a.map(a=>a.t)).size,q.a.length,`${key}: duplicate choices`);
    }
  }
  units++;
}
assert.equal(units,36);
assert.equal(catalog.grades.find(g=>g.id==="g6").units.length,8);

class Element {
  constructor(tag){this.tagName=tag;this.children=[];this.style={};this.attrs={};this.handlers={};this.nodeType=1;this.textContent="";this.className="";this.clientWidth=1000;this.clientHeight=400;this.offsetWidth=136;
    this.classList={add:(c)=>{this.className+=" "+c;},remove:(c)=>{this.className=this.className.replace(c,"");},toggle:()=>{}};
  }
  setAttribute(k,v){this.attrs[k]=v;}
  addEventListener(k,fn){this.handlers[k]=fn;}
  append(...xs){for(const x of xs){x.parentElement=this;this.children.push(x);}}
  replaceChildren(...xs){for(const x of this.children)x.parentElement=null;this.children=[];this.append(...xs);}
  remove(){if(this.parentElement){this.parentElement.children=this.parentElement.children.filter(x=>x!==this);this.parentElement=null;}}
  get isConnected(){return this===screen || !!this.parentElement?.isConnected;}
  click(){if(!this.disabled)this.handlers.click?.({stopPropagation(){}});}
  matches(){return false;}
}
const screen = new Element("main");
const handlers = new Map();
globalThis.window = {addEventListener:(k,f)=>handlers.set(k,f),removeEventListener:(k,f)=>{if(handlers.get(k)===f)handlers.delete(k);}};
globalThis.document={createElement:t=>new Element(t),createTextNode:t=>Object.assign(new Element("text"),{textContent:t}),addEventListener(){},removeEventListener(){},body:new Element("body")};
globalThis.matchMedia=()=>({matches:true});
let now=0,id=0;
const frames=new Map(),timeouts=new Map();
globalThis.performance={now:()=>now};
globalThis.requestAnimationFrame=f=>{frames.set(++id,f);return id;};
globalThis.cancelAnimationFrame=i=>frames.delete(i);
globalThis.setTimeout=(f,delay)=>{timeouts.set(++id,{f,at:now+delay});return id;};
globalThis.clearTimeout=i=>timeouts.delete(i);
const descendants=(n)=>[n,...n.children.flatMap(descendants)];
const find=(c)=>descendants(screen).find(e=>e.className.split(" ").includes(c));
const advance=(ms)=>{for(let t=0;t<ms;t+=20){now+=20;const batch=[...frames];frames.clear();batch.forEach(([,f])=>f(now));for(const [i,v]of timeouts)if(v.at<=now){timeouts.delete(i);v.f();}}};
const bank={words:seed["g6/u1"],questions:[],imgBase:"/"};
const ctx={screen,title:"probe",bank,backHash:"#/g6/u1/oyunlar"};ctx.restart=()=>start(ctx);
start(ctx);advance(20);
let prompt=find("shooter-prompt").children.at(-1).textContent;
let answer=bank.words.find(w=>w.tr===prompt).en;
let bubbles=()=>descendants(screen).filter(e=>e.className.split(" ").includes("shooter-bubble"));
let wrong=bubbles().find(b=>!b.attrs["aria-label"].endsWith(": "+answer));
// Aim directly at a lower circle so no other target lies in the ray.
wrong=bubbles().slice(2).find(b=>!b.attrs["aria-label"].endsWith(": "+answer))||wrong;
wrong.click();advance(800);
assert(wrong.className.includes("popped"));assert(wrong.disabled);
assert.equal(find("shooter-controls").children[0].textContent,"♥ 4 / 5");
wrong.click();advance(100);assert.equal(find("shooter-controls").children[0].textContent,"♥ 4 / 5");
const pause=find("shooter-controls").children[2];pause.click();
let before=find("shooter-controls").children[1].textContent;
advance(2000);assert.equal(find("shooter-controls").children[1].textContent,before);
assert(bubbles().every(b=>b.disabled));pause.click();
let correct=bubbles().find(b=>b.attrs["aria-label"].endsWith(": "+answer));
correct.click();advance(1000);
assert.equal(find("hud").children[0].children[1].textContent,7);
ctx.restart();advance(20);assert.equal(frames.size,1);assert.equal(timeouts.size,0);
assert.equal(find("hud").children[0].children[1].textContent,"0");
handlers.get("hashchange")();assert.equal(frames.size,0);assert.equal(timeouts.size,0);
start(ctx);advance(300100);assert(find("result"));assert.equal(frames.size,0);
console.log(`PASS: ${units} menus, randomized choices, projectile hits, popping, repeat-hit guard, pause, restart, timeout and exit cleanup.`);
