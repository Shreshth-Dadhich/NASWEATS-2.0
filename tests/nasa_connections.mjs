import assert from 'node:assert/strict';
import fs from 'node:fs';
import {acquirePublic,decodeNASA} from '../frontend/src/acquisition.js';
import {validateDrawnPolygon} from '../frontend/src/geometry.js';
import {rectangle} from '../frontend/src/spatial.js';
import {clampRange,validateComparison,getTheme,saveTheme} from '../frontend/src/selection.js';

const raw=fs.readFileSync('frontend/public/cache/raw/gulf-temperature.json','utf8');
const geometry=rectangle([48.2,24.2,48.3,24.3]);
const originalFetch=globalThis.fetch,urls=[];
try{
  globalThis.fetch=async url=>{urls.push(url);return new Response(raw,{status:200});};
  const signal=new AbortController().signal;
  const a=await acquirePublic({geometry,variable:'temperature',signal,force:true});
  assert.equal(urls.length,1);
  assert.equal(new URL(urls[0]).hostname,'power.larc.nasa.gov');
  assert.equal(a.originals[0].raw,raw);
  assert.equal(a.parameter,'T2M');
  globalThis.fetch=async()=>{throw Error('offline');};
  assert.equal(await acquirePublic({geometry,variable:'temperature',signal}),a);
  await assert.rejects(acquirePublic({geometry,variable:'temperature',signal,force:true}),/No values were substituted|no values were substituted/);
  let siblingAborted=false;
  globalThis.fetch=async(url,options)=>{
    if(new URL(url).searchParams.get('longitude-min')==='47.687500')return new Response('{}',{status:400});
    return new Promise((resolve,reject)=>options.signal.addEventListener('abort',()=>{siblingAborted=true;reject(new DOMException('Cancelled','AbortError'));},{once:true}));
  };
  await assert.rejects(acquirePublic({geometry:rectangle([48,24,54,28]),variable:'temperature',signal,force:true}),/HTTP 400/);
  assert.equal(siblingAborted,true);
}finally{globalThis.fetch=originalFetch;}
const malformed=JSON.parse(raw);malformed.parameters.T2M.units='F';
assert.throws(()=>decodeNASA(JSON.stringify(malformed),'T2M','url','hash'),/unexpected measurement units/);
malformed.parameters.T2M.units='C';malformed.features[0].geometry.coordinates[0]=null;
assert.throws(()=>decodeNASA(JSON.stringify(malformed),'T2M','url','hash'),/invalid grid coordinate/);
const polygon=coordinates=>({type:'Polygon',coordinates:[coordinates]});
validateDrawnPolygon(rectangle([10,20,11,21]));
assert.throws(()=>validateDrawnPolygon(polygon([[0,0],[1,1],[2,2],[0,0]])),/no measurable area/);
assert.throws(()=>validateDrawnPolygon(polygon([[0,0],[2,2],[0,2],[2,0],[0,0]])),/cross or touch/);
assert.throws(()=>validateDrawnPolygon(polygon([[0,0],[2,0],[1,1],[2,0],[0,2],[0,0]])),/vertices repeat/);
assert.deepEqual(clampRange([2023,2024],1984,2024),[2020,2024]);
assert.deepEqual(clampRange([1980,2026],2000,2002),[2000,2002]);
validateComparison({unit:'C',parameter:'T2M'},{unit:'C',parameter:'T2M'});
assert.throws(()=>validateComparison({unit:'C',parameter:'T2M'},{unit:'m/s',parameter:'WS10M'}),/different measurements or units/);
assert.throws(()=>validateComparison({unit:'C',parameter:'T2M',source:{api:{version:'v1'}}},{unit:'C',parameter:'T2M',source:{api:{version:'v2'}}}),/different source versions/);
assert.equal(getTheme(),'atlas');saveTheme('midnight');
console.log('PASS: NASA-only request URL; live refresh bypasses cache; API errors never return cached substitutes; sibling requests abort; units/coordinates reject invalid responses; polygon degeneracy and intersections; valid slider ranges; compatible comparisons; blocked browser storage.');
