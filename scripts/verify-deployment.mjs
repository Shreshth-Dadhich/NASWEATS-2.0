import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const origin=new URL(process.argv[2]||'https://earthsignal-nasweats-2-0.earthsignal-by-nasweats-2-0.workers.dev');
if(origin.protocol!=='https:'||origin.username||origin.password)throw Error('Use the deployed HTTPS origin without credentials.');
async function get(relative){const response=await fetch(new URL(relative,origin),{signal:AbortSignal.timeout(45000)});assert.ok(response.ok,`${relative}: HTTP ${response.status}`);return response;}
const html=await (await get('/')).text();assert.ok(html.includes('/assets/'));assert.ok(!html.includes('__EARTHSIGNAL_INDEX_HTML__'));
const health=await (await get('/api/nasa/health')).json();assert.equal(health.status,'ok');assert.equal(health.has_asset_binding,true);
assert.equal((await fetch(new URL('/api/nasa/gmi?variable=invalid',origin),{signal:AbortSignal.timeout(15000)})).status,400);
const assets=['studies/arabian-dust/data.json','studies/arabian-dust/manifest.json','studies/arabian-dust/integration-spec.md','studies/arabian-dust/datasets/regional_monthly_averages_land_weighted.csv','studies/arabian-dust/figures/05_wind_vs_dust.png'];
async function gzip(dir){for(const f of await fs.readdir(dir,{withFileTypes:true})){const p=path.join(dir,f.name);if(f.isDirectory()){const match=await gzip(p);if(match)return match;}else if(f.name.endsWith('.gz'))return p;}}
const assetRoot=path.join(root,'dist/client');
assets.push(path.relative(assetRoot,await gzip(assetRoot)).replaceAll('\\','/'));
const checks=await Promise.all(assets.map(async relative=>{const bytes=Buffer.from(await (await get('/'+relative)).arrayBuffer());assert.deepEqual(bytes,await fs.readFile(path.join(assetRoot,relative)),`Changed asset: ${relative}`);return {path:relative,sha256:createHash('sha256').update(bytes).digest('hex')};}));
const report={origin:origin.origin,checked_utc:new Date().toISOString(),health,asset_checks:checks};
await fs.mkdir(path.join(root,'verification'),{recursive:true});await fs.writeFile(path.join(root,'verification/cloudflare-deployment.json'),JSON.stringify(report,null,2)+'\n');
console.log(`PASS: ${origin.origin}: production HTML, API routing, invalid-request rejection and ${checks.length} byte-identical scientific assets.`);
