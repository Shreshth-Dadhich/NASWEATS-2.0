import {prepare} from './analytics.js';
export function pairedRelationship(xRecords,yRecords,{range,season='ALL',anomaly=false,frequency='annual',detrend=false}){
 const a=prepare(xRecords,...range,season,anomaly),b=prepare(yRecords,...range,season,anomaly),x=frequency==='monthly'?a.monthly:a.series,y=frequency==='monthly'?b.monthly:b.series,key=r=>frequency==='monthly'?r.date:String(r.year),lookup=new Map(y.filter(r=>Number.isFinite(r.value)).map(r=>[key(r),r]));
 const pairs=x.filter(r=>Number.isFinite(r.value)&&lookup.has(key(r))).map(r=>({date:r.date,analysis_year:r.analysisYear||r.year,x:r.value,y:lookup.get(key(r)).value,time:frequency==='monthly'?+r.date.slice(0,4)+(+r.date.slice(5,7)-.5)/12:r.year}));
 if(detrend&&pairs.length>=2)for(const axis of ['x','y']){const mt=pairs.reduce((s,p)=>s+p.time,0)/pairs.length,mv=pairs.reduce((s,p)=>s+p[axis],0)/pairs.length,tt=pairs.reduce((s,p)=>s+(p.time-mt)**2,0),slope=tt?pairs.reduce((s,p)=>s+(p.time-mt)*(p[axis]-mv),0)/tt:0;for(const p of pairs)p[axis]-=mv+slope*(p.time-mt);}
 const n=pairs.length;if(n<3)return {pairs,n,r:null,reason:'At least three paired observations are needed to describe a relationship.'};
 const mx=pairs.reduce((s,p)=>s+p.x,0)/n,my=pairs.reduce((s,p)=>s+p.y,0)/n,xx=pairs.reduce((s,p)=>s+(p.x-mx)**2,0),yy=pairs.reduce((s,p)=>s+(p.y-my)**2,0),xy=pairs.reduce((s,p)=>s+(p.x-mx)*(p.y-my),0);
 return {pairs,n,r:xx>1e-24&&yy>1e-24?Math.max(-1,Math.min(1,xy/Math.sqrt(xx*yy))):null,reason:xx<=1e-24||yy<=1e-24?'A selected series is constant.':null,start:pairs[0].date,end:pairs.at(-1).date};
}
