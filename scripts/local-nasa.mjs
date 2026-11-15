import http from 'node:http';import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';import worker from '../worker/index.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
http.createServer(async(req,res)=>{
  try{
    const request=new Request('http://127.0.0.1:8000'+req.url,{method:req.method});
    const reply=await worker.fetch(request,{}, {waitUntil:p=>p.catch(()=>{})});
    res.writeHead(reply.status,Object.fromEntries(reply.headers));res.end(Buffer.from(await reply.arrayBuffer()));
  }catch(e){res.writeHead(500,{'Content-Type':'application/json'});res.end(JSON.stringify({error:e.message}));}
}).listen(8000,'127.0.0.1',()=>console.log('NASA subset relay: http://127.0.0.1:8000'));
