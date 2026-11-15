import assert from 'node:assert/strict';import fs from 'node:fs';
import {annualComparison,trendRows,trendVerdict,relationshipModel,reportedRelationship} from '../frontend/src/studyWorkbench.js';
const base='frontend/public/studies/arabian-dust/',m=JSON.parse(fs.readFileSync(base+'manifest.json')),d=JSON.parse(fs.readFileSync(base+m.data.url));
const readCSV=name=>{const [header,...lines]=fs.readFileSync(base+'datasets/'+name,'utf8').trim().split(/\r?\n/),keys=header.split(',');return lines.map(line=>Object.fromEntries(line.split(',').map((v,i)=>[keys[i],v!==''&&Number.isFinite(+v)?+v:v])));};
const whole=readCSV('regional_monthly_averages_land_weighted.csv'),regional=readCSV('regional_monthly_analysis.csv'),annual=readCSV('regional_annual_analysis.csv'),wholeAnnual=readCSV('annual_trends_land_weighted.csv');
for(const region of ['all',...m.regions.map(r=>r.id)]){
 const rows=(region==='all'?whole:regional.filter(r=>r.region===region)).sort((a,b)=>a.yearmonth-b.yearmonth);assert.equal(rows.length,312);
 for(let i=0;i<m.variables.length;i++)for(let j=i+1;j<m.variables.length;j++){
  const x=m.variables[i].id,y=m.variables[j].id,id=x+' vs '+y,raw=relationshipModel(d,region,id,true),residual=relationshipModel(d,region,id);assert.equal(raw.points.length,312);
  raw.points.forEach((p,k)=>{assert.equal(p.x,rows[k][x]);assert.equal(p.y,rows[k][y]);});
  assert.ok(residual.fit.r>=-1&&residual.fit.r<=1);
  const reported=reportedRelationship(d,region,id);if(reported)assert.ok(Math.abs(reported.r-residual.fit.r)<1e-12);
  assert.ok(Math.abs(relationshipModel(d,region,y+' vs '+x).fit.r-residual.fit.r)<1e-12);
 }
}
for(const v of m.variables){const traces=annualComparison(m,d,v.id,[2000,2025]);assert.equal(traces.length,6);traces.forEach((trace,i)=>{const rows=i===5?wholeAnnual:annual.filter(r=>r.region===m.regions[i].id);assert.deepEqual(trace.y,rows.map(r=>r[v.id]));});const rows=trendRows(m,d,v.id);assert.equal(rows.length,5);for(const {mk}of rows)assert.equal(trendVerdict(mk),mk.FDR_significant?(mk.Sen_slope_per_decade>0?'Increase':'Decrease'):'No significant trend');}
assert.equal(reportedRelationship(d,'Northwest','TEMP_C vs RH'),null);
assert.equal(reportedRelationship(d,'all','PRECTOTCORR_MM_MONTH vs GWETROOT'),null);
for(const [id,r]of [['WIND_SPEED vs DUST_UG_M3',.382],['GWETTOP vs DUST_UG_M3',-.202],['PRECTOT_MM_MONTH vs GWETTOP',.658]])assert.ok(Math.abs(relationshipModel(d,'all',id).fit.r-r)<.0005);
console.log('PASS: every raw scatter coordinate for all 36 variable pairs × 6 scopes matches original CSVs; all 34 supplied coefficients reproduce; no invented FDR for missing tests; all 9 six-line annual comparisons match CSVs; all 45 directional verdicts use supplied q.');
