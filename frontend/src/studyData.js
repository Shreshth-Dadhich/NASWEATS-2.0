/** @typedef {{region?:string,year:number,yearmonth?:number,month?:number,[key:string]:number|string}} Observation
 * @typedef {{Region:string,Variable:string,FDR_p_value:number,FDR_significant:boolean,Sen_slope_per_decade:number,MK_tau:number,MK_trend:string}} Trend
 * @typedef {{Region?:string,Relationship:string,Pearson_r?:number,FDR_p_value?:number,Significant?:boolean,[key:string]:number|string|boolean}} Relationship
 * @typedef {{id:string,name:string,unit:string,annual_unit:string,definition:string,source:string}} StudyVariable
 * @typedef {{id:string,name:string,bbox:number[]}} StudyRegion
 */
export const STUDY_BASE='/studies/arabian-dust/';
export const sha256=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
async function response(url,signal){const r=await fetch(url,{signal});if(!r.ok)throw Error('Study file unavailable: '+url+' ('+r.status+').');return r;}
export function validateStudy(manifest,data){
 if(manifest.schema_version!==1||data.schema_version!==1||manifest.variables.length!==9||manifest.regions.length!==5)throw Error('Unsupported study schema.');
 const ids=new Set(manifest.regions.map(r=>r.id));
 for(const [name,n]of Object.entries({monthly:1560,annual:130,study_monthly:312,study_annual:26,linear:45,mk:45,correlations:25,study_correlations:9})){
  if(!Array.isArray(data[name])||data[name].length!==n)throw Error('Study table dimensions differ: '+name);
  for(const r of data[name]){if((r.region&&!ids.has(r.region))||(r.Region&&!ids.has(r.Region)))throw Error('Unknown study region.');for(const v of Object.values(r))if(typeof v==='number'&&!Number.isFinite(v))throw Error('Non-finite study value.');}
 }
 for(const name of ['monthly','annual','study_monthly','study_annual']){
  const keys=new Set();for(const r of data[name]){const key=(r.region||'all')+':'+(r.yearmonth||r.year);if(keys.has(key)||r.year<2000||r.year>2025)throw Error('Duplicate or out-of-range study observation.');keys.add(key);for(const v of manifest.variables)if(!Number.isFinite(r[v.id]))throw Error('Missing study measurement: '+v.id);}
 }
 for(const r of data.mk)if(typeof r.FDR_significant!=='boolean'||r.FDR_significant!==(r.FDR_p_value<.05))throw Error('Study trend significance is inconsistent.');
 for(const r of data.correlations)if(typeof r.Significant!=='boolean'||r.Significant!==(r.FDR_p_value<.05))throw Error('Study relationship significance is inconsistent.');
 return {manifest,data};
}
export async function loadStudy(signal){const manifest=await (await response(STUDY_BASE+'manifest.json',signal)).json(),raw=await (await response(STUDY_BASE+manifest.data.url,signal)).arrayBuffer();if(await sha256(raw)!==manifest.data.sha256)throw Error('Study dataset checksum mismatch.');return validateStudy(manifest,JSON.parse(new TextDecoder().decode(raw)));}
/** @returns {Observation[]} */
export function observations(data,region,frequency='annual',range=[2000,2025]){const source=region==='all'?data[frequency==='annual'?'study_annual':'study_monthly']:data[frequency];return source.filter(r=>(region==='all'||r.region===region)&&r.year>=range[0]&&r.year<=range[1]).sort((a,b)=>(a.yearmonth||a.year)-(b.yearmonth||b.year));}
export function trendEvidence(data,region,variable){return {mk:data.mk.find(r=>r.Region===region&&r.Variable===variable),linear:data.linear.find(r=>r.Region===region&&r.Variable===variable)};}
export function relationships(data,region){return (region==='all'?data.study_correlations:data.correlations.filter(r=>r.Region===region)).map(r=>({...r,r:r.Pearson_r??r['Pearson r'],q:r.FDR_p_value??r['Multiple-test p-value'],p:r.Autocorrelation_adjusted_p??r['Adjusted p-value'],n:r.Effective_sample_size??r['Effective sample size'],significant:r.Significant??r['Multiple-test p-value']<.05}));}
export function residuals(rows,key){const sum=new Array(12).fill(0),n=new Array(12).fill(0);for(const r of rows){sum[r.month-1]+=r[key];n[r.month-1]++;}const y=rows.map(r=>r[key]-sum[r.month-1]/n[r.month-1]),mx=(y.length-1)/2,my=y.reduce((a,b)=>a+b,0)/y.length,xx=y.reduce((s,_,i)=>s+(i-mx)**2,0),slope=y.reduce((s,v,i)=>s+(i-mx)*(v-my),0)/xx;return y.map((v,i)=>v-my-slope*(i-mx));}
export function relationshipPoints(data,region,relationship){const [x,y]=relationship.split(' vs '),rows=observations(data,region,'monthly'),xs=residuals(rows,x),ys=residuals(rows,y);return rows.map((r,i)=>({x:xs[i],y:ys[i],date:String(r.yearmonth).slice(0,4)+'-'+String(r.yearmonth).slice(4)}));}
export function annualMean(data,region,variable,range){const rows=observations(data,region,'annual',range);return rows.length?rows.reduce((s,r)=>s+r[variable],0)/rows.length:null;}
export function pValue(p){return p===0?'0 (source precision)':p<.001?p.toExponential(3):p.toFixed(4);}
