import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.csv':'text/csv; charset=utf-8','.gz':'application/gzip','.zip':'application/zip','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml','.woff2':'font/woff2','.txt':'text/plain; charset=utf-8','.ico':'image/x-icon'};
export function createPreviewServer(worker,assetRoot){
  const base=assetRoot&&path.resolve(assetRoot);
  const env=base?{ASSETS:{async fetch(request){
    const pathname=decodeURIComponent(new URL(request.url).pathname);
    const file=path.resolve(base,'.'+pathname),relative=path.relative(base,file);
    if(relative.startsWith('..')||path.isAbsolute(relative)||relative.split(/[\\/]/).some(p=>p.startsWith('.')))return new Response('Not found',{status:404});
    try{const stat=await fs.stat(file);if(!stat.isFile())return new Response('Not found',{status:404});
      // Gzip data files are decompressed explicitly by the app.
      return new Response(await fs.readFile(file),{headers:{'Content-Type':mime[path.extname(file)]||'application/octet-stream','X-Content-Type-Options':'nosniff'}});
    }catch(e){if(e.code==='ENOENT')return new Response('Not found',{status:404});throw e;}
  }}}:{};
  return http.createServer(async(req,res)=>{
    try{
      if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end('Use GET or HEAD');return;}
      const response=await worker.fetch(new Request('http://localhost'+req.url,{method:req.method}),env,{waitUntil:p=>p.catch(()=>{})});
      res.writeHead(response.status,Object.fromEntries(response.headers));res.end(req.method==='HEAD'?undefined:Buffer.from(await response.arrayBuffer()));
    }catch(e){res.writeHead(500,{'Content-Type':'application/json'});res.end(JSON.stringify({error:e.message}));}
  });
}
