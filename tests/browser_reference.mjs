import fs from 'node:fs';import {analyze,mannKendall} from '../frontend/src/analytics.js';
const source=JSON.parse(fs.readFileSync('power-reference.json','utf8'));
const records=Object.entries(source.properties.parameter.T2M).filter(([k])=>+k.slice(4)<=12).map(([k,v])=>({date:k.slice(0,4)+'-'+k.slice(4)+'-01',value:v}));
const results=[];for(const confidence of [.9,.95,.99])for(const season of ['ALL','JJA','DJF'])for(const anomaly of [false,true])results.push({confidence,season,anomaly,result:analyze(records,2001,2024,season,anomaly,confidence)});
fs.mkdirSync('verification',{recursive:true});fs.writeFileSync('verification/browser-statistics.json',JSON.stringify({records,results}));
if(Math.abs(mannKendall([1,1,2,3,4]).p-1/30)>1e-12)throw Error('Exact tied MK reference failed');
console.log('Wrote 18 actual NASA-data statistical reference cases.');
