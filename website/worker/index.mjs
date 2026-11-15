// Public, allowlisted NASA relay. No arbitrary URLs or credentials are accepted.
const INDEX_HTML=`__EARTHSIGNAL_INDEX_HTML__`;
const DATA={air_quality:{collection:'instM_2d_bot_Nx',field:'pm25_bot',units:'kg m-3'},dust:{collection:'tavgM_2d_aer_Nx',field:'duexttau',units:'1'},cloud:{collection:'tavgM_2d_rad_Nx',field:'cldlow',units:'1'},ocean:{collection:'tavgM_2d_rad_Nx',field:'ts',units:'K'},"soil_root":{"collection":"tavgM_2d_lnd_Nx","field":"gwetroot","units":"1"},"soil_top":{"collection":"tavgM_2d_lnd_Nx","field":"gwettop","units":"1","mask":"gwetroot"},"precip_gmi":{"collection":"tavgM_2d_flx_Nx","field":"prectot","units":"kg m-2 s-1"},"precip_corr_gmi":{"collection":"tavgM_2d_flx_Nx","field":"prectotcorr","units":"kg m-2 s-1"}};
const metadata=new Map();
const json=(data,status=200)=>Response.json(data,{status,headers:{'Cache-Control':'no-store'}});
export function nasaRequest(url){
  const kind=url.searchParams.get('variable'),spec=Object.hasOwn(DATA,kind)?DATA[kind]:null,year=Number(url.searchParams.get('year')),span=Number(url.searchParams.get('span')||1),bbox=(url.searchParams.get('bbox')||'').split(',').map(Number);
  if(!spec||!Number.isInteger(year)||year<1980||year>2019||!Number.isInteger(span)||span<1||span>5||year+span-1>2019||bbox.length!==4||bbox.some(v=>!Number.isFinite(v)))throw Error('Choose a supported NASA measurement, a valid 1–5 year subset within 1980–2019 and a valid bounding box.');
  const [w,s,e,n]=bbox;
  if(w< -180||e>180||s< -85||n>85||e<=w||n<=s||e-w>12||n-s>12)throw Error('NASA study boxes must be within global coordinate limits and span at most 12° per axis.');
  const x0=Math.max(0,Math.floor((w+180-.3125)/.625)),x1=Math.min(575,Math.ceil((e+180+.3125)/.625)),y0=Math.max(0,Math.floor((s+90-.25)/.5)),y1=Math.min(360,Math.ceil((n+90+.25)/.5)),t0=(year-1980)*12;
  const root='https://opendap.nccs.nasa.gov/dods/merra2_gmi/'+spec.collection;
  const subset=field=>`${field}[${t0}:1:${t0+12*span-1}][${y0}:1:${y1}][${x0}:1:${x1}]`;
  return {...spec,year,span,key:[kind,year,span,x0,x1,y0,y1].join('/'),source:root+'.ascii?'+[spec.field,spec.mask].filter(Boolean).map(subset).join(','),metadata:root+'.das'};
}
async function validatedMetadata(spec){
  const metadataKey=spec.metadata+'#'+spec.field,ready=metadata.get(metadataKey);if(ready&&Date.now()-ready.time<86400000)return ready;
  const r=await fetch(spec.metadata,{signal:AbortSignal.timeout(30000)});if(!r.ok)throw Error('NASA source metadata unavailable.');
  const raw=await r.text(),match=raw.match(new RegExp('    '+spec.field+' \\{([\\s\\S]*?)\\n    \\}'));
  if(!match||!match[1].includes('String units "'+spec.units+'"'))throw Error('NASA field units differ from the validated source; acquisition stopped.');
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw))),b=>b.toString(16).padStart(2,'0')).join('');
  const value={time:Date.now(),hash,raw};metadata.set(metadataKey,value);return value;
}
export default {
  async fetch(request,env={},ctx={waitUntil:()=>{}}){
    const url=new URL(request.url);
    if(url.pathname==='/api/nasa/health')return json({status:'ok',provider:'NASA public datasets',has_asset_binding:!!env.ASSETS,credentials_required:false});
    if(url.pathname==='/api/nasa/gmi'){
      if(request.method!=='GET')return json({error:'Use GET for public NASA subsets.'},405);
      let spec;try{spec=nasaRequest(url);}catch(e){return json({error:e.message},400);}
      const key=new Request(url.origin+'/__nasa-source/'+spec.key);let cache=null;
      // Some dispatch hosts forbid Cache API access. It is an optional optimization.
      try{cache=globalThis.caches?.default;if(cache){const cached=await cache.match(key);if(cached)return cached;}}catch{cache=null;}
      try{
        const meta=await validatedMetadata(spec);
        const response=await fetch(spec.source,{signal:AbortSignal.timeout(60000)});
        if(!response.ok)return json({error:'NASA returned HTTP '+response.status+'. Retry later; no values were substituted.'},502);
        const body=await response.text();
        if(!body.includes(spec.field+', ['+(12*spec.span)+']'))return json({error:'NASA did not return the expected monthly numerical array.'},502);
        const result=new Response(body,{headers:{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'public, max-age=86400','X-NASA-Source':spec.source,'X-NASA-Metadata-SHA256':meta.hash,'X-NASA-Units':spec.units,'X-Content-Type-Options':'nosniff'}});
        if(cache)ctx.waitUntil(cache.put(key,result.clone()).catch(()=>{}));return result;
      }catch(e){return json({error:e.name==='TimeoutError'?'NASA subset service timed out. Retry later; completed local caches remain available.':e.message},502);}
    }
    if(url.pathname.startsWith('/api/'))return json({error:'This hosted API supports public NASA subsets. Direct authenticated granule decoding needs the separate Python service.'},501);
    if(url.pathname==='/'||url.pathname==='/index.html')return new Response(INDEX_HTML,{headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'}});
    if(env.ASSETS)return env.ASSETS.fetch(request);
    return new Response('Static asset binding unavailable.',{status:503});
  }
};
