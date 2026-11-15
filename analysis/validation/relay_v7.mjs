import assert from 'node:assert/strict';import fs from 'node:fs';import {gunzipSync} from 'node:zlib';
import worker,{nasaRequest} from '../../website/worker/index.mjs';import {parseDAP} from '../../website/src/extraSources.js';import {number,signed} from '../../website/src/numbers.js';
const url=new URL('https://earthsignal.example/api/nasa/gmi?variable=air_quality&year=2019&bbox=48,24,52,28');
const query=nasaRequest(url);assert.ok(query.source.startsWith('https://opendap.nccs.nasa.gov/dods/merra2_gmi/instM_2d_bot_Nx.ascii?pm25_bot['));
assert.throws(()=>nasaRequest(new URL('https://x/api?variable=constructor&year=2019&bbox=48,24,52,28')));
assert.throws(()=>nasaRequest(new URL('https://x/api?variable=air_quality&year=2019&span=5&bbox=48,24,52,28')));
assert.throws(()=>nasaRequest(new URL('https://x/api?variable=air_quality&year=2019&bbox=-180,-85,180,85')));
const source=gunzipSync(fs.readFileSync('website/.generated/public/data/originals/instM_2d_bot_Nx-2019.txt.gz')).toString(),meta=gunzipSync(fs.readFileSync('website/.generated/public/data/originals/instM_2d_bot_Nx.das.gz')).toString();
const parsed=parseDAP(source);assert.deepEqual(parsed.pm25_bot.shape,[12,39,41]);assert.equal(parsed.time.values.length,12);
assert.throws(()=>parseDAP('pm25_bot, [12][1][1]\n[0][0], 1\n'),/dimensions/);
const originalFetch=globalThis.fetch,requests=[];
try{
 globalThis.fetch=async u=>{requests.push(u);return new Response(u.endsWith('.das')?meta:source);};
 const response=await worker.fetch(new Request(url));assert.equal(response.status,200);assert.equal(await response.text(),source);assert.equal(response.headers.get('X-NASA-Source'),query.source);assert.equal(response.headers.get('X-NASA-Units'),'kg m-3');assert.match(response.headers.get('X-NASA-Metadata-SHA256'),/^[a-f0-9]{64}$/);
 assert.equal(requests.length,2);
 const cacheDescriptor=Object.getOwnPropertyDescriptor(globalThis,'caches');
 try{
  Object.defineProperty(globalThis,'caches',{configurable:true,get(){throw Error('Cache API unavailable on dispatch host');}});
  const withoutCache=await worker.fetch(new Request(url));assert.equal(withoutCache.status,200);assert.equal(await withoutCache.text(),source);
 }finally{if(cacheDescriptor)Object.defineProperty(globalThis,'caches',cacheDescriptor);else delete globalThis.caches;}
 const count=requests.length,invalid=await worker.fetch(new Request('https://x/api/nasa/gmi?variable=https://example.com'));assert.equal(invalid.status,400);assert.equal(requests.length,count);
}finally{globalThis.fetch=originalFetch;}
assert.equal(number(.00000045),'4.50e-7');assert.equal(signed(-.00000045),'−4.50e-7');
console.log('PASS: NASA-only relay allowlist, bounded subsets, exact response passthrough, original-source headers, units/hash validation, multi-month DAP shape parsing and small scientific-number precision.');
