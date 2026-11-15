import {observations,trendEvidence} from './studyData.js';
import {relationshipModel} from './studyWorkbench.js';
export const VALUE_VIEWS=[['annual','Annual values'],['monthly','Monthly values'],['average','Long-term average'],['ols','Linear trend / decade']];
export function valueAt(data,region,variable,aggregation,year=2025,month=12){
 if(!VALUE_VIEWS.some(([id])=>id===aggregation))throw Error('Unknown map aggregation.');
 if(aggregation==='ols')return trendEvidence(data,region,variable).linear?.Change_per_decade??null;
 const rows=observations(data,region,aggregation==='monthly'?'monthly':'annual');
 if(aggregation==='average')return rows.length&&rows.every(r=>Number.isFinite(r[variable]))?rows.reduce((s,r)=>s+r[variable],0)/rows.length:null;
 const row=rows.find(r=>r.year===year&&(aggregation!=='monthly'||r.month===month));return Number.isFinite(row?.[variable])?row[variable]:null;
}
export function studyMapModel(manifest,data,{mode='values',variable='TEMP_C',aggregation='annual',year=2025,month=12,scale='all',relationship='WIND_SPEED vs DUST_UG_M3'}={}){
 const spec=manifest.variables.find(v=>v.id===variable);if(!spec)throw Error('Unknown supplied map variable.');
 const unit=mode==='correlation'?'Pearson r':mode==='trend'||aggregation==='ols'?spec.annual_unit+' / decade':aggregation==='monthly'?spec.unit:spec.annual_unit;
 const rows=manifest.regions.map(region=>{
  const evidence=trendEvidence(data,region.id,variable);let value,reported=null,classification='value';
  if(mode==='correlation'){
   const model=relationshipModel(data,region.id,relationship);reported=model.reported;value=reported?.r??model.fit.r;
   classification=!reported?'unreported':reported.significant?(value>=0?'increase':'decrease'):'nonsignificant';
  }else if(mode==='trend'){
   value=evidence.mk?.Sen_slope_per_decade??null;
   classification=!evidence.mk?'missing':!evidence.mk.FDR_significant?'nonsignificant':value>0?'increase':value<0?'decrease':'nonsignificant';
  }else value=valueAt(data,region.id,variable,aggregation,year,month);
  if(!Number.isFinite(value))classification='missing';
  return {...region,value:Number.isFinite(value)?value:null,classification,reported,...evidence};
 });
 let extent;
 if(mode==='correlation')extent=[-1,1];
 else if(mode==='trend'||aggregation==='ols'){const magnitude=Math.max(...rows.map(r=>Math.abs(r.value??0)),1e-12);extent=[-magnitude,magnitude];}
 else{
  const values=scale==='all'&&['annual','monthly','average'].includes(aggregation)?data[aggregation==='monthly'?'monthly':'annual'].map(r=>r[variable]):rows.map(r=>r.value);
  const finite=values.filter(Number.isFinite);extent=finite.length?[Math.min(...finite),Math.max(...finite)]:[0,1];
 }
 return {rows,unit,extent,spec,mode,aggregation,year,month,scale,relationship,source:mode==='trend'?'regional_mann_kendall_sen.csv':mode==='correlation'?'regional_monthly_analysis.csv / regional_correlation_analysis.csv':aggregation==='ols'?'regional_linear_trends.csv':aggregation==='monthly'?'regional_monthly_analysis.csv':'regional_annual_analysis.csv'};
}
export function mapExportRows(model){return model.rows.map(r=>({region:r.id,west:r.bbox[0],south:r.bbox[1],east:r.bbox[2],north:r.bbox[3],mode:model.mode,variable:model.mode==='correlation'?model.relationship:model.spec.id,aggregation:model.mode==='trend'?'sen_slope':model.mode==='correlation'?'monthly_residuals':model.aggregation,year:model.mode==='values'&&['annual','monthly'].includes(model.aggregation)?model.year:null,month:model.mode==='values'&&model.aggregation==='monthly'?model.month:null,value:r.value,unit:model.unit,legend_min:model.extent[0],legend_max:model.extent[1],scale:model.mode==='correlation'?'fixed_r_-1_to_1':model.mode==='trend'||model.aggregation==='ols'?'symmetric_full_record':model.scale,classification:model.mode==='correlation'&&r.classification==='increase'?'fdr_significant_positive_association':model.mode==='correlation'&&r.classification==='decrease'?'fdr_significant_negative_association':r.classification,sen_per_decade:model.mode==='correlation'?null:r.mk?.Sen_slope_per_decade??null,mk_tau:model.mode==='correlation'?null:r.mk?.MK_tau??null,mk_z:model.mode==='correlation'?null:r.mk?.MK_z??null,mk_p:model.mode==='correlation'?null:r.mk?.MK_p_value??null,fdr_q:model.mode==='correlation'?r.reported?.q??null:r.mk?.FDR_p_value??null,ols_per_decade:model.mode==='correlation'?null:r.linear?.Change_per_decade??null,ols_r2:model.mode==='correlation'?null:r.linear?.R_squared??null,ols_p:model.mode==='correlation'?null:r.linear?.P_value??null,correlation_adjusted_p:r.reported?.p??null,effective_n:r.reported?.n??null,lag1_acf_x:r.reported?.acfX??null,lag1_acf_y:r.reported?.acfY??null,statistical_years:'2000-2025',source_files:model.source}));}
