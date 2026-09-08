import assert from 'node:assert/strict';
import { earlierSetup, setupKey } from '../app/js/deck-steps.js';
import { mediaUrl, lessonImage } from '../app/js/lesson-media.js';

const slides = [
  {type:'grammar', rule:'Try *this* rule', chips:["Why don’t we"]},
  {type:'vocab'},
  {type:'grammar', rule:'A different rule', chips:["Why don't we", "Let's"]},
];
assert.equal(earlierSetup(slides, 0).size, 0);
const seen = earlierSetup(slides, 2);
assert(seen.has(setupKey('rule', 'Try this rule')));
assert(seen.has(setupKey('chip', "  WHY DON'T WE  ")));
assert(!seen.has(setupKey('rule', slides[2].rule)));
assert(!seen.has(setupKey('chip', "Let's")));
assert(!seen.has(setupKey('example', "Why don't we")));
assert.equal(mediaUrl('https://static.arasaac.org/a.png', {}), 'https://static.arasaac.org/a.png');
assert.equal(mediaUrl('/app/img/a.svg', {}), '/app/img/a.svg');
assert.equal(mediaUrl('a.png', {base:'/unit/'}), '/unit/img/a.png');

// Exercise the actual image failure/retry lifecycle without a network or build.
class Element extends EventTarget {
  constructor(tag) { super(); this.tag = tag; this.attrs = {}; }
  setAttribute(key, value) { this.attrs[key] = value; }
  replaceWith(node) { this.replacement = node; }
}
globalThis.document = {createElement: tag => new Element(tag)};
globalThis.CustomEvent ??= class extends Event {};
const img = lessonImage({img:'/app/img/a.svg'}, {}, 'picture');
assert.equal(img.attrs['data-fit'], 'contain');
let failed = false;
img.addEventListener('imageunavailable', () => { failed = true; });
img.dispatchEvent(new Event('error'));
assert(failed);
assert.equal(img.replacement.tag, 'button');
img.replacement.dispatchEvent(new Event('click'));
const retried = img.replacement.replacement;
assert.equal(retried.tag, 'img');
let ready = false;
retried.addEventListener('imageready', () => { ready = true; });
retried.dispatchEvent(new Event('load'));
assert(ready);
console.log('PASS: first, partial and nonadjacent setup; media paths; image retry lifecycle.');
