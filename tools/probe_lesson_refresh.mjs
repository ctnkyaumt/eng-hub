import assert from 'node:assert/strict';
import { taskNode } from '../app/js/exercises.js';
import { markedParts } from '../app/js/lesson-emphasis.js';

// DOM fixture deliberately exercises the real activity event handlers.
class Node {
  constructor(tag) {
    this.tagName=tag;this.nodeType=1;this.children=[];this.attrs={};this.events={};this.className='';this.ownText='';this.hidden=false;
    this.classList={add:(...cs)=>{this.className=[...new Set([...this.className.split(' '),...cs])].filter(Boolean).join(' ');},
      remove:(...cs)=>{this.className=this.className.split(' ').filter(c=>!cs.includes(c)).join(' ');},
      contains:c=>this.className.split(' ').includes(c),toggle:(c,on)=>{this.classList[on??!this.classList.contains(c)?'add':'remove'](c);}};
  }
  set textContent(t){this.ownText=String(t);this.children=[];}
  get textContent(){return this.ownText+this.children.map(c=>c.textContent).join('');}
  setAttribute(k,v){this.attrs[k]=v;if(k==='hidden')this.hidden=true;}
  addEventListener(k,f){(this.events[k]??=[]).push(f);}
  emit(k,e={}){for(const f of this.events[k]||[])f({currentTarget:this,preventDefault(){},...e});}
  click(){if(!this.disabled)this.emit('click');}
  append(...nodes){for(const n of nodes){n.remove();n.parent=this;this.children.push(n);}}
  prepend(n){n.remove();n.parent=this;this.children.unshift(n);}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(c=>c!==this);this.parent=null;}
  replaceChildren(...nodes){this.ownText='';this.children.forEach(n=>n.parent=null);this.children=[];this.append(...nodes);}
}
globalThis.document={createElement:t=>new Node(t),createTextNode:t=>{const n=new Node('#text');n.textContent=t;return n;}};
globalThis.window={};
const all=n=>[n,...n.children.flatMap(all)];
const css=(root,cls)=>all(root).filter(n=>n.classList.contains(cls));
const byText=(root,text)=>all(root).find(n=>n.tagName==='button'&&n.textContent===text);

let root=taskNode({kind:'wordpairs',pairs:[{a:'one',b:'bir'},{a:'two',b:'iki'},{a:'three',b:'üç'}]},{});
const card=text=>css(root,'pair-card').find(n=>css(n,'pair-front')[0].textContent.endsWith(text));
card('one').click();card('iki').click();assert.equal(css(root,'matched').length,0);
card('one').click(); // First open card cannot count twice.
assert.equal(css(root,'matched').length,0);
card('three').click();card('üç').click();
for(const [a,b] of [['one','bir'],['two','iki']]){card(a).click();card(b).click();}
assert.equal(css(root,'matched').length,6);assert(css(root,'activity-score')[0].textContent.startsWith('3 / 3'));
byText(root,'Play again').click();assert.equal(css(root,'matched').length,0);

root=taskNode({kind:'groupsort',groups:[{label:'Fruit',items:['apple','pear']},{label:'Colours',items:['red','blue']}]},{});
byText(root,'Fruit').click();assert(css(root,'verdict')[0].textContent.includes('first'));
byText(root,'apple').click();byText(root,'Colours').click();assert.equal(css(root,'sorted-word').length,0);
byText(root,'Fruit').click();assert.equal(css(root,'sorted-word').length,1);
const dt={setData(){},effectAllowed:''};byText(root,'pear').emit('dragstart',{dataTransfer:dt});css(root,'sort-bin')[0].emit('drop');
for(const word of ['red','blue']){byText(root,word).click();byText(root,'Colours').click();}
assert.equal(css(root,'sorted-word').length,4);byText(root,'Start again').click();assert.equal(css(root,'sorted-word').length,0);

root=taskNode({kind:'cloze',sentences:[{text:'I ___ happy.',answer:'am',tr:'Mutluyum.'},{text:'You ___ happy.',answer:'are',tr:'Mutlusun.'},{text:'They ___ happy.',answer:'are',tr:'Mutlular.'}]},{});
const gaps=()=>css(root,'cloze-gap'), words=()=>css(root,'cloze-word');
byText(root,'Check answers').click();assert(css(root,'verdict')[0].textContent.includes('every gap'));
words().find(n=>n.textContent==='are').click();gaps()[0].click();words().find(n=>n.textContent==='am').click();gaps()[1].click();words().find(n=>n.textContent==='are'&&!n.disabled).click();gaps()[2].click();
byText(root,'Check answers').click();assert.equal(css(root,'wrong').length,2);assert(css(root,'cloze-translation').every(n=>n.hidden));
gaps()[0].click();gaps()[1].click();words().find(n=>n.textContent==='am').click();gaps()[0].click();
words().find(n=>n.textContent==='are'&&!n.disabled).emit('dragstart',{dataTransfer:dt});gaps()[1].emit('drop');
byText(root,'Check answers').click();assert.equal(css(root,'right').length,3);assert(gaps().every(n=>n.disabled));
assert(css(root,'cloze-translation').every(n=>n.hidden));byText(root,'Show Turkish meanings').click();assert(css(root,'cloze-translation').every(n=>!n.hidden));
byText(root,'Start again').click();assert(words().every(n=>!n.disabled));assert(gaps().every(n=>n.textContent==='…'));

root=taskNode({kind:'quizbox',questions:[{q:'Say hello.',answer:'Hello!',tr:'Merhaba!'},{q:'Say goodbye.',answer:'Goodbye!'}]},{});
css(root,'question-box')[0].click();assert(css(root,'box-answer')[0].hidden);
byText(root,'Reveal model answer').click();assert(!css(root,'box-answer')[0].hidden);assert(css(root,'box-translation')[0].hidden);
byText(root,'Turkish meaning').click();assert(!css(root,'box-translation')[0].hidden);byText(root,'Practise again').click();
assert(css(root,'question-box')[0].classList.contains('review'));css(root,'question-box')[0].click();byText(root,'Reveal model answer').click();byText(root,'I got it').click();
css(root,'question-box')[1].click();byText(root,'Reveal model answer').click();byText(root,'I got it').click();
assert(css(root,'activity-score')[0].textContent.includes('2 / 2 answered · 2 correct'));
byText(root,'Play again').click();assert(css(root,'activity-score')[0].textContent.includes('0 / 2'));

assert.deepEqual(markedParts('She plays.',[{start:8,end:9,role:'ending'}]),[{text:'She play'},{text:'s',role:'ending'},{text:'.'}]);
assert.equal(markedParts('<b>safe</b>',[]).map(p=>p.text).join(''),'<b>safe</b>');
console.log('PASS: actual memory, sorting, cloze and question-box handlers; wrong/correct answers, duplicate word tiles, drag/tap, retries, hidden meanings, reset and rich-text suffixes.');
