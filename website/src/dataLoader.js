import {assertStudyArea,inStudyArea} from './studyArea.js';
import {acquirePublic as acquirePOWER,boundsOf,coverageBounds,contains} from './acquisition.js';
import {acquireExtra,GMI} from './extraSources.js';
import {readDataset,storeDataset,compressedJSON} from './dataCache.js';
export {boundsOf} from './acquisition.js';
const memory=[];
const extent=d=>d.domain?d.bbox:coverageBounds(d);
export async function acquirePublic(args){
  const {geometry,variable,signal,force=false,onProgress=()=>{}}=args,bounds=boundsOf(assertStudyArea(geometry));
  if(!force&&variable!=='water_level'){
    const cached=memory.find(d=>d.variable===variable&&contains(extent(d),bounds));if(cached)return cached;
    const saved=await readDataset(variable,bounds);if(signal.aborted)throw new DOMException('Cancelled','AbortError');
    if(saved){memory.unshift(saved);return saved;}
  }
  let result;
  if(!force&&!['water','sea_level','water_level'].includes(variable)&&args.preset&&(!GMI[variable]?.ready_presets||GMI[variable].ready_presets.includes(args.preset))){
    try{const ready=await compressedJSON('/data/ready/'+args.preset+'-'+variable+'.json.gz',signal);if(contains(extent(ready),bounds))result=ready;}catch(e){if(signal.aborted)throw e;}
  }
  if(!result&&!['temperature','humidity','wind'].includes(variable))result=await acquireExtra(args);
  if(!result)result=await acquirePOWER(args);
  if(signal.aborted)throw new DOMException('Cancelled','AbortError');
  if(result.feature_based&&!result.cells.every(c=>inStudyArea(c.lon,c.lat)))throw Error('This monitored water body is outside the Middle East study extent.');
  memory.unshift(result);if(memory.length>16)memory.length=16;
  storeDataset(result,extent(result)).catch(()=>{});
  onProgress('Verified NASA source ready');return result;
}
