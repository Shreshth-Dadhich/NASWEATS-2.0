import {analyze} from './analytics.js';
import {weightedCells,regionalRecords,mapValues,fullDomain,mergeMapCells} from './spatial.js';
let input=null,domainCache=new Map();
self.onmessage=({data:message})=>{
  const started=performance.now();
  try{
    if(message.type==='init'){
      input=message.input;domainCache=new Map();
      input.cells=weightedCells(input.a,input.geometry);
      input.cellsB=weightedCells(input.b,input.geometryB);
      input.records=regionalRecords(input.a,input.cells,input.geometry);
      input.recordsB=regionalRecords(input.b,input.cellsB,input.geometryB);
    }
    if(!input||message.version!==input.version)return;
    const o=message.options,{a,b,cells,cellsB,records,recordsB}=input;
    const analysis=analyze(records,...o.range,o.season,o.anomaly,o.confidence);
    const analysisB=analyze(recordsB,...o.range,o.season,o.anomaly,o.confidence);
    const mapped=mergeMapCells([...mapValues(a,cells,o.range,o.season,o.anomaly,o.mapMode),...mapValues(b,cellsB,o.range,o.season,o.anomaly,o.mapMode)]).map(({values,observation_counts,...cell})=>cell);
    let domain;
    if(o.mapMode==='trend'){
      const limit=mapped.reduce((m,c)=>Number.isFinite(c.mapValue)?Math.max(m,Math.abs(c.mapValue)):m,1e-12);domain=[-limit,limit];
    }else{
      const key=o.season+':'+o.anomaly;
      if(!domainCache.has(key)){
        const values=[...fullDomain(a,cells,o.season,o.anomaly),...fullDomain(b,cellsB,o.season,o.anomaly)];
        domainCache.set(key,values.length?values.reduce(([lo,hi],v)=>[Math.min(lo,v),Math.max(hi,v)],[Infinity,-Infinity]):[0,1]);
      }
      domain=domainCache.get(key);
    }
    self.postMessage({version:message.version,id:message.id,options:o,result:{analysis,analysisB,records,recordsB,mapped,domain,cellsCount:cells.length,cellsBCount:cellsB.length,milliseconds:performance.now()-started}});
  }catch(e){self.postMessage({version:message.version,id:message.id,error:e.message});}
};
