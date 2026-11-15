import assert from 'node:assert/strict';
import fs from 'node:fs';
import {assertStudyArea,inStudyArea,regionalLake} from '../../website/src/studyArea.js';
import {REGIONS} from '../../website/src/regions.js';
import {rectangle} from '../../website/src/spatial.js';
import {acquirePublic} from '../../website/src/dataLoader.js';
for(const region of Object.values(REGIONS))assertStudyArea(rectangle(region.bbox));
assert.equal(Object.keys(REGIONS).length,5);
assertStudyArea(rectangle([24,12,25,13]));
for(const box of [[23.99,20,25,21],[40,11.99,41,13],[63,20,64.01,21],[40,41,41,42.01],[-123,36,-119,40]])assert.throws(()=>assertStudyArea(rectangle(box)),/Middle East/);
// Rejection must precede caches and NASA requests, even for an existing preset or forced reload.
let requests=0;const original=globalThis.fetch;
globalThis.fetch=async()=>{requests++;throw Error('Unexpected external request');};
try{for(const force of [false,true])await assert.rejects(acquirePublic({geometry:rectangle([-123,36,-119,40]),variable:'temperature',preset:'gulf',force,signal:new AbortController().signal}),/Middle East/);}finally{globalThis.fetch=original;}
assert.equal(requests,0);
const lakes=JSON.parse(fs.readFileSync('website/.generated/public/data/lakes/index.json')).filter(regionalLake);
assert.ok(lakes.length>0&&lakes.length<340);assert.ok(lakes.some(l=>l.name.includes('Nasser')));assert.ok(lakes.every(l=>inStudyArea(l.lon,l.lat,.1)));assert.ok(!lakes.some(l=>/Sudan|Ethiopia|Azerbaijan/.test(l.name)));
console.log(`PASS: five Middle East presets, boundary-crossing rejection before any request/cache, and ${lakes.length} eligible NASA lake records.`);
