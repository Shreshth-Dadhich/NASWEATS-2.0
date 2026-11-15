import {compressedJSON} from './dataCache.js';
import {digest,boundsOf,coverageBounds,contains} from './acquisition.js';

export const GMI={"air_quality":{"collection":"instM_2d_bot_Nx","field":"pm25_bot","unit":"µg/m³","native_unit":"kg m-3","factor":1000000000,"offset":0,"label":"Reconstructed bottom-layer PM2.5"},"dust":{"collection":"tavgM_2d_aer_Nx","field":"duexttau","unit":"1","native_unit":"1","factor":1,"offset":0,"label":"Dust optical depth at 550 nm"},"cloud":{"collection":"tavgM_2d_rad_Nx","field":"cldlow","unit":"fraction","native_unit":"1","factor":1,"offset":0,"label":"Low-cloud fraction"},"ocean":{"collection":"tavgM_2d_rad_Nx","field":"ts","unit":"°C","native_unit":"K","factor":1,"offset":-273.15,"label":"Surface skin temperature (land + sea)"},"soil_root":{"collection":"tavgM_2d_lnd_Nx","field":"gwetroot","unit":"dimensionless","native_unit":"1","factor":1,"offset":0,"label":"Root-zone soil wetness","domain":"land","ready_presets":["gulf","california"]},"soil_top":{"collection":"tavgM_2d_lnd_Nx","field":"gwettop","unit":"dimensionless","native_unit":"1","factor":1,"offset":0,"label":"Topsoil wetness","land_mask":"gwetroot","domain":"land","ready_presets":["gulf","california"]},"precip_gmi":{"collection":"tavgM_2d_flx_Nx","field":"prectot","unit":"mm/day","native_unit":"kg m-2 s-1","factor":86400,"offset":0,"label":"Precipitation rate · PRECTOT","ready_presets":["gulf","california"]},"precip_corr_gmi":{"collection":"tavgM_2d_flx_Nx","field":"prectotcorr","unit":"mm/day","native_unit":"kg m-2 s-1","factor":86400,"offset":0,"label":"Precipitation rate · PRECTOTCORR","ready_presets":["gulf","california"]}};
const files=new Map();
async function load(url,signal){if(files.has(url))return files.get(url);const result=await compressedJSON(url,signal);files.set(url,result);if(files.size>16)files.delete(files.keys().next().value);return result;}

export function parseDAP(text){
  const blocks=text.split(/^([a-z][a-z0-9_]*), \[/m),result={};
  for(let i=1;i<blocks.length;i+=2){
    const [first,...lines]=blocks[i+1].split(/\r?\n/),shape=(first.match(/\d+/g)||[]).map(Number),values=[];
    for(let line of lines){if(!line.trim())continue;if(line.startsWith('['))line=line.slice(line.indexOf(',')+1);for(const value of line.split(','))if(value.trim()){const n=Number(value);if(!Number.isFinite(n))throw Error('NASA returned an invalid numerical array.');values.push(n);}}
    if(values.length!==shape.reduce((n,s)=>n*s,1))throw Error('NASA OPeNDAP array dimensions do not match the response.');
    result[blocks[i]]={shape,values};
  }
  return result;
}
function inside(lon,lat,geometry){const ring=geometry.coordinates[0];let hit=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>lat)!==(b[1]>lat)&&lon<(b[0]-a[0])*(lat-a[1])/(b[1]-a[1])+a[0])hit=!hit;}return hit;}
export async function lakeIndex(signal){return fetch('/data/lakes/index.json',{signal}).then(r=>{if(!r.ok)throw Error('The NASA lake catalogue could not load.');return r.json();});}

async function grace({geometry,variable,signal,onProgress}){
  const b=boundsOf(geometry),manifest=await fetch('/data/grace/'+variable+'/manifest.json',{signal}).then(r=>{if(!r.ok)throw Error('NASA GRACE archive is unavailable.');return r.json();});
  // Index by actual cell extents, so edge-crossing equal-area cells are retained.
  const keys=manifest.tiles.filter(t=>t.bounds[0]<b[2]&&t.bounds[2]>b[0]&&t.bounds[1]<b[3]&&t.bounds[3]>b[1]).map(t=>t.key);
  onProgress('Loading NASA GRACE mascons…');
  let first=null,cells=[];
  for(let i=0;i<keys.length;i++){const d=await load('/data/grace/'+variable+'/'+keys[i]+'.json.gz',signal);first??=d;cells.push(...d.cells.filter(c=>c.bounds[0]<b[2]&&c.bounds[2]>b[0]&&c.bounds[1]<b[3]&&c.bounds[3]>b[1]));}
  const domain=variable==='water'?'land':'ocean';
  return {...first,schema_version:2,source_mode:'public_starter',variable,parameter:'cmwe_'+(variable==='water'?'OBP':'SLA'),unit:'cm w.e.',domain,source:manifest.source,dates:manifest.dates,cells,bbox:b};
}

async function gmi({geometry,variable,signal,onProgress}){
  const b=boundsOf(geometry),spec=GMI[variable],years=Array.from({length:8},(_,i)=>1980+5*i),blocks=new Array(8),originals=new Array(8),task=new AbortController(),taskSignal=AbortSignal.any([signal,task.signal]);let next=0,done=0;
  onProgress('Loading NASA monthly '+spec.label+'…');
  async function worker(){while(next<years.length){const i=next++,year=years[i],q=new URLSearchParams({variable,year:String(year),span:'5',bbox:b.join(',')});const r=await fetch('/api/nasa/gmi?'+q,{signal:taskSignal});if(!r.ok){const error=await r.json().catch(()=>({}));throw Error(error.error||'NASA monthly request failed ('+r.status+').');}const text=await r.text(),parsed=parseDAP(text),array=parsed[spec.field];if(!array||array.shape[0]!==60)throw Error('NASA did not return sixty monthly source grids.');blocks[i]=parsed;originals[i]={raw:text,url:r.headers.get('X-NASA-Source'),sha256:await digest(text)};done+=5;onProgress(`NASA monthly archive: ${done}/40 years`);}}
  try{await Promise.all([worker(),worker()]);}catch(e){task.abort();throw e;}
  for(const block of blocks)if(JSON.stringify(block.lat.values)!==JSON.stringify(blocks[0].lat.values)||JSON.stringify(block.lon.values)!==JSON.stringify(blocks[0].lon.values))throw Error('NASA coordinate grids differ across years.');
  const lats=blocks[0].lat.values,lons=blocks[0].lon.values,dates=Array.from({length:40},(_,i)=>1980+i).flatMap(y=>Array.from({length:12},(_,m)=>`${y}-${String(m+1).padStart(2,'0')}-01`)),cells=[];
  for(let j=0;j<lats.length;j++)for(let i=0;i<lons.length;i++){
    const lat=lats[j],lon=lons[i],values=[];
    for(const block of blocks){for(let m=0;m<block[spec.field].shape[0];m++){const offset=(m*lats.length+j)*lons.length+i,v=block[spec.field].values[offset],mask=spec.land_mask?block[spec.land_mask]?.values[offset]:0;values.push(Math.abs(v)<1e14&&Number.isFinite(mask)&&Math.abs(mask)<1e14?v*spec.factor+spec.offset:null);}}
    cells.push({lon,lat,bounds:[lon-.3125,lat-.25,lon+.3125,lat+.25],values});
  }
  return {schema_version:2,source_mode:'public_starter',variable,parameter:spec.field,unit:spec.unit,bbox:b,dates,domain:spec.domain,cells:spec.domain?cells.filter(c=>c.values.some(Number.isFinite)):cells,originals,source:{label:'NASA MERRA2-GMI monthly replay · '+spec.label,short_name:spec.collection,field:spec.field,version:'NCCS monthly 1980–2019 archive',native_unit:spec.native_unit,retrieved_utc:new Date().toISOString(),requested_url:originals[0].url,requested_urls:originals.map(o=>o.url),raw_sha256_tiles:originals.map(({url,sha256})=>({url,sha256})),citation_url:'https://opendap.nccs.nasa.gov/dods/merra2_gmi',resolution:'0.5° latitude × 0.625° longitude',measurement_label:spec.label,processing:`Native monthly ${spec.field} · factor ${spec.factor}, offset ${spec.offset}. Annual and seasonal views use day-weighted means. Precipitation is a rate, not monthly accumulation; fine dust is not all-species PM2.5; soil wetness is not groundwater. This global chemistry replay is distinct from the supplied regional MERRA-2 study. No temporal extension beyond the archive and no invented values.`,not_native_product:'NASA MERRA2-GMI chemistry replay; distinct from the directly requested native mission products.'}};
}

export async function acquireExtra(args){
  const {variable,geometry,preset,signal,force,onProgress,lakeId}=args,b=boundsOf(geometry);
  if(variable==='water'||variable==='sea_level')return grace(args);
  if(variable==='water_level'){
    const entries=await lakeIndex(signal),available=entries.filter(l=>inside(l.lon,l.lat,geometry));
    if(!available.length)throw Error('No NASA-monitored lake observation lies inside this boundary. Choose a lake from the monitored-water-body selector.');
    available.sort((a,b)=>b.valid_months-a.valid_months);
    const chosen=available.find(l=>l.id===lakeId)||available[0];
    return load('/data/lakes/'+chosen.id+'.json.gz',signal);
  }
  if(!force&&['gulf','empty','tigris','redsea','nile'].includes(preset)&&(!GMI[variable]?.ready_presets||GMI[variable].ready_presets.includes(preset))){
    try{const d=await load('/data/ready/'+preset+'-'+variable+'.json.gz',signal);if(contains(d.domain?d.bbox:coverageBounds(d),b))return d;}catch(e){if(signal.aborted)throw e;}
  }
  if(GMI[variable])return gmi(args);
  return null;
}
