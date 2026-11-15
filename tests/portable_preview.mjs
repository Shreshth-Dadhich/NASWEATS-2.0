import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createPreviewServer} from '../scripts/server-core.mjs';
import worker from '../dist/server/index.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const server=createPreviewServer(worker,path.join(root,'dist/client'));
await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
try{
 const origin=`http://127.0.0.1:${server.address().port}`;
 const get=p=>fetch(origin+p,{signal:AbortSignal.timeout(5000)});
 const html=await (await get('/')).text();assert.ok(html.includes('/assets/'));assert.ok(!html.includes('__EARTHSIGNAL_INDEX_HTML__'));
 const health=await (await get('/api/nasa/health')).json();assert.equal(health.status,'ok');assert.equal(health.has_asset_binding,true);
 assert.equal((await get('/api/nasa/gmi?variable=invalid')).status,400);
 for(const p of ['/.env','/missing-data.json'])assert.equal((await get(p)).status,404);
 const assetRoot=path.join(root,'dist/client');
 async function findGzip(dir){for(const f of await fs.readdir(dir,{withFileTypes:true})){const p=path.join(dir,f.name);if(f.isDirectory()){const match=await findGzip(p);if(match)return match;}else if(f.name.endsWith('.gz'))return p;}}
 const gzip=await findGzip(assetRoot);assert.ok(gzip);
 for(const relative of ['studies/arabian-dust/data.json','studies/arabian-dust/integration-spec.md',path.relative(assetRoot,gzip).replaceAll('\\','/')]){
   const r=await get('/'+relative);assert.equal(r.status,200);assert.deepEqual(Buffer.from(await r.arrayBuffer()),await fs.readFile(path.join(assetRoot,relative)));
 }
 console.log('PASS: standalone preview HTML, health, request validation, private/missing paths and exact JSON/specification/gzip bytes.');
}finally{server.closeAllConnections();await new Promise(resolve=>server.close(resolve));}
