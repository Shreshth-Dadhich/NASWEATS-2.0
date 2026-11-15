import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createServer} from 'vite';
import worker from '../worker/index.mjs';
import {createPreviewServer} from './server-core.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),relay=createPreviewServer(worker);
await new Promise((resolve,reject)=>{relay.once('error',reject);relay.listen(8000,'127.0.0.1',resolve);});
let vite;
try{vite=await createServer({root,configFile:path.join(root,'vite.config.js'),server:{host:'127.0.0.1',port:4176,strictPort:true}});await vite.listen();vite.printUrls();}catch(e){relay.close();throw e;}
let closing=false;
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,async()=>{if(closing)return;closing=true;await vite.close();relay.close(()=>process.exit(0));relay.closeAllConnections();});
