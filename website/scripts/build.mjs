import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),dist=path.resolve(root,'dist');
if(JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8')).name!=='earthsignal-by-nasweats-2-0'||dist!==path.join(root,'dist'))throw Error('Unexpected build directory');
// Verified above: only this package's reproducible build directory is removed.
fs.rmSync(dist,{recursive:true,force:true});
const require=createRequire(path.join(root,'package.json'));
const vite=path.join(path.dirname(require.resolve('vite/package.json')),'bin/vite.js');
const result=spawnSync(process.execPath,[vite,'build'],{cwd:root,stdio:'inherit'});
if(result.error)throw result.error;if(result.status!==0)process.exit(result.status??1);
const html=fs.readFileSync(path.join(dist,'client/index.html'),'utf8'),source=fs.readFileSync(path.join(root,'worker/index.mjs'),'utf8');
if(!source.includes('`__EARTHSIGNAL_INDEX_HTML__`'))throw Error('Missing Worker HTML build placeholder');
fs.mkdirSync(path.join(dist,'server'),{recursive:true});
fs.writeFileSync(path.join(dist,'server/index.js'),source.replace('`__EARTHSIGNAL_INDEX_HTML__`',JSON.stringify(html)));
console.log('Built independent frontend + NASA relay. Deployment config: wrangler.jsonc');
