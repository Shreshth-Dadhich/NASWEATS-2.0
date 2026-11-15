let database;
export function covers(outer,inner){return outer&&inner&&outer[0]<=inner[0]+1e-8&&outer[1]<=inner[1]+1e-8&&outer[2]>=inner[2]-1e-8&&outer[3]>=inner[3]-1e-8;}
async function open(){
  if(typeof indexedDB==='undefined')return null;
  if(!database)database=new Promise(resolve=>{
    try{const r=indexedDB.open('earthsignal-nasa-v7.2',1);r.onupgradeneeded=()=>{const s=r.result.createObjectStore('datasets',{keyPath:'key'});s.createIndex('variable','variable');};r.onsuccess=()=>resolve(r.result);r.onerror=()=>resolve(null);}catch{resolve(null);}
  });return database;
}
export async function readDataset(variable,bounds){
  const db=await open();if(!db)return null;
  return new Promise(resolve=>{try{const r=db.transaction('datasets').objectStore('datasets').index('variable').getAll(variable);r.onsuccess=()=>resolve(r.result.filter(x=>Date.now()-x.saved<30*86400000&&covers(x.bounds,bounds)).sort((a,b)=>b.saved-a.saved)[0]?.dataset||null);r.onerror=()=>resolve(null);}catch{resolve(null);}});
}
export async function storeDataset(dataset,bounds){
  const db=await open();if(!db)return;
  try{
    const transaction=db.transaction('datasets','readwrite'),store=transaction.objectStore('datasets');
    store.put({key:dataset.variable+':'+dataset.parameter+':'+bounds.join(','),variable:dataset.variable,bounds,saved:Date.now(),dataset});
    transaction.oncomplete=()=>{const t=db.transaction('datasets','readwrite'),s=t.objectStore('datasets'),r=s.getAll();r.onsuccess=()=>{const rows=r.result.sort((a,b)=>b.saved-a.saved);for(const row of rows.slice(20))s.delete(row.key);};};
  }catch{/* Storage quotas never prevent NASA data acquisition. */}
}
export async function compressedJSON(url,signal){
  const r=await fetch(url,{signal});if(!r.ok)throw Error('NASA cache file unavailable ('+r.status+').');
  const bytes=new Uint8Array(await r.arrayBuffer());
  // CDNs may serve .gz as content-encoding, or as a gzip file. Handle both.
  const text=bytes[0]===31&&bytes[1]===139?await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text():new TextDecoder().decode(bytes);
  return JSON.parse(text);
}
