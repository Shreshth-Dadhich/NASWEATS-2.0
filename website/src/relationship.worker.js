import {weightedCells,regionalRecords} from './spatial.js';
import {pairedRelationship} from './globalRelationship.js';
let yA=[],yB=[];
self.onmessage=({data:m})=>{try{if(m.type==='init'){yA=regionalRecords(m.a,weightedCells(m.a,m.geometry),m.geometry);yB=m.b?regionalRecords(m.b,weightedCells(m.b,m.geometryB),m.geometryB):[];return;}self.postMessage({id:m.id,result:{a:pairedRelationship(m.xA,yA,m.options),b:m.xB?.length?pairedRelationship(m.xB,yB,m.options):null,options:m.options}});}catch(e){self.postMessage({id:m.id,error:e.message});}};
