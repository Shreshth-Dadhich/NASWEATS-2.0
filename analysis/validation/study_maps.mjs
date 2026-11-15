import assert from 'node:assert/strict';import fs from 'node:fs';
import {studyMapModel,mapExportRows} from '../../website/src/studyMapModel.js';
const root='website/.generated/public/studies/arabian-dust/',m=JSON.parse(fs.readFileSync(root+'manifest.json')),d=JSON.parse(fs.readFileSync(root+m.data.url));
function csv(name){const [first,...rows]=fs.readFileSync(root+'datasets/'+name,'utf8').trim().split(/\r?\n/),keys=first.split(',');return rows.map(row=>Object.fromEntries(row.split(',').map((v,i)=>[keys[i],Number.isFinite(+v)?+v:v])));}
const annual=csv('regional_annual_analysis.csv'),monthly=csv('regional_monthly_analysis.csv'),mk=csv('regional_mann_kendall_sen.csv'),ols=csv('regional_linear_trends.csv'),corr=csv('regional_correlation_analysis.csv');
let observations=0;
for(const variable of m.variables.map(v=>v.id)){
 for(const aggregation of ['annual','monthly']){const source=aggregation==='annual'?annual:monthly,all=source.map(r=>r[variable]),expected=[Math.min(...all),Math.max(...all)],n=aggregation==='annual'?26:312;
  for(let frame=0;frame<n;frame++){const year=2000+(aggregation==='annual'?frame:Math.floor(frame/12)),month=frame%12+1,model=studyMapModel(m,d,{variable,aggregation,year,month});assert.deepEqual(model.extent,expected);for(const region of model.rows){const raw=source.find(r=>r.region===region.id&&r.year===year&&(aggregation!=='monthly'||r.month===month));assert.equal(region.value,raw[variable]);observations++;}if(variable.startsWith('PRECTOT'))assert.equal(model.unit,aggregation==='annual'?'mm/year':'mm/month');}
 }
 const trend=studyMapModel(m,d,{variable,mode:'trend'}),linear=studyMapModel(m,d,{variable,aggregation:'ols'}),average=studyMapModel(m,d,{variable,aggregation:'average'});
 for(const row of trend.rows){const raw=mk.find(r=>r.Region===row.id&&r.Variable===variable);assert.equal(row.value,raw.Sen_slope_per_decade);assert.equal(row.classification,raw.FDR_p_value<.05?raw.Sen_slope_per_decade>0?'increase':'decrease':'nonsignificant');}
 for(const row of linear.rows)assert.equal(row.value,ols.find(r=>r.Region===row.id&&r.Variable===variable).Change_per_decade);
 for(const row of average.rows){const source=annual.filter(r=>r.region===row.id);assert.equal(row.value,source.reduce((s,r)=>s+r[variable],0)/source.length);}
 const frame=studyMapModel(m,d,{variable,scale:'frame',year:2025});assert.deepEqual(frame.extent,[Math.min(...frame.rows.map(r=>r.value)),Math.max(...frame.rows.map(r=>r.value))]);
}
let reported=0,missing=0;
for(const relationship of d.study_correlations.map(r=>r.Relationship)){const model=studyMapModel(m,d,{mode:'correlation',relationship});assert.deepEqual(model.extent,[-1,1]);for(const region of model.rows){const source=corr.find(r=>r.Region===region.id&&r.Relationship===relationship);if(source){assert.equal(region.value,source.Pearson_r);assert.equal(region.reported.q,source.FDR_p_value);assert.equal(region.classification,source.FDR_p_value<.05?source.Pearson_r>=0?'increase':'decrease':'nonsignificant');reported++;}else{assert.equal(region.classification,'unreported');assert.equal(region.reported,null);assert.ok(Number.isFinite(region.value));missing++;}}}
const exported=mapExportRows(studyMapModel(m,d,{mode:'correlation',relationship:'TEMP_C vs RH'}));assert.equal(exported.length,5);assert.ok(exported.every(r=>r.fdr_q===null&&r.classification==='unreported'&&Number.isFinite(r.value)));assert.equal(mapExportRows(studyMapModel(m,d,{variable:'PRECTOT_MM_MONTH'})).find(r=>r.region==='Southwest').value,annual.find(r=>r.region==='Southwest'&&r.year===2025).PRECTOT_MM_MONTH);
assert.equal(reported,25);assert.equal(missing,20);
const changed=structuredClone(d),target=changed.annual.find(r=>r.region==='Southwest'&&r.year===2025);target.TEMP_C=0;assert.equal(studyMapModel(m,changed).rows.find(r=>r.id==='Southwest').value,0);target.TEMP_C=null;const absent=studyMapModel(m,changed).rows.find(r=>r.id==='Southwest');assert.equal(absent.value,null);assert.equal(absent.classification,'missing');assert.equal(studyMapModel(m,changed,{aggregation:'average'}).rows.find(r=>r.id==='Southwest').value,null);
console.log(`PASS: ${observations} annual/monthly map values match original CSVs; all 45 Sen and OLS slopes, means, units, fixed/frame scales, 25 regional correlation tests and 20 unreported tests are correct; missing values stay distinct from zero.`);
