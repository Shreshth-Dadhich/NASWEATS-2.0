import assert from 'node:assert/strict';import fs from 'node:fs';import {webcrypto} from 'node:crypto';
import {boundsOf,planRequests,decodeNASA,coverageBounds,contains} from '../../website/src/acquisition.js';import {rectangle,weightedCells,regionalRecords,mapValues,mergeMapCells} from '../../website/src/spatial.js';import {analyze} from '../../website/src/analytics.js';
const globalRegions=[[-123,36,-119,40],[-62,-5,-58,-1],[149,-35,153,-31],[137,34,141,38],[12,76,16,80]];
for(const box of globalRegions){const tiles=planRequests(rectangle(box));assert.ok(tiles.length>0&&tiles.length<=16);for(const [w,s,e,n]of tiles){assert.ok(e-w<=5.0000001&&n-s<=5.0000001);assert.ok(w>=-180&&e<=180&&s>=-90&&n<=90);}}
assert.throws(()=>boundsOf(rectangle([-170,0,170,2])),/12°/);assert.throws(()=>boundsOf(rectangle([181,0,182,2])),/coordinates/);
const d=JSON.parse(fs.readFileSync('website/.generated/public/cache/gulf-temperature.json','utf8'));
function tiny(cell){return rectangle([cell.lon-.08,cell.lat-.06,cell.lon+.08,cell.lat+.06]);}
const cellA=d.cells[0],cellB=d.cells.at(-1),a=tiny(cellA),b=tiny(cellB),wa=weightedCells(d,a),wb=weightedCells(d,b);assert.equal(wa.length,1);assert.equal(wb.length,1);
const ra=regionalRecords(d,wa,a),rb=regionalRecords(d,wb,b);assert.ok(ra.every((r,i)=>Math.abs(r.value-cellA.values[i])<1e-10));assert.ok(rb.every((r,i)=>Math.abs(r.value-cellB.values[i])<1e-10));assert.notEqual(analyze(ra,2001,2024).slope,analyze(rb,2001,2024).slope);
const full=rectangle([48,24,52,28]),wc=weightedCells(d,full),m=mapValues(d,wc,[2001,2024],'ALL',false,'trend'),mShort=mapValues(d,wc,[2010,2024],'ALL',false,'trend');assert.ok(m.some((c,i)=>Math.abs(c.mapValue-mShort[i].mapValue)>1e-7));assert.ok(contains(coverageBounds(d),[48,24,52,28]));
const raw=fs.readFileSync('website/.generated/public/cache/raw/gulf-temperature.json','utf8'),digest=Buffer.from(await webcrypto.subtle.digest('SHA-256',new TextEncoder().encode(raw))).toString('hex'),parsed=decodeNASA(raw,'T2M','https://power.larc.nasa.gov/api/temporal/monthly/regional',digest);assert.equal(parsed.cells.length,d.cells.length);assert.equal(parsed.unit,d.unit);assert.deepEqual(parsed.cells[0].values,d.cells[0].values);assert.equal(parsed.original.raw,raw);
const merged=mergeMapCells([...m,...m]);assert.equal(merged.length,m.length);
assert.ok(merged.every(c=>c.clipped.type==='MultiPolygon'&&c.clipped.coordinates.length===2));
assert.deepEqual(merged.map(c=>c.mapValue),m.map(c=>c.mapValue));
console.log('PASS: five global hemispheres; native-sized tile planning; selection limits; two independently selected real NASA cells produce distinct trends; tiny polygons preserve source values; window changes alter trend-map values; raw regional decoding preserves source data; overlapping comparison cells render once.');
