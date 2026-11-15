import intersect from '@turf/intersect';import area from '@turf/area';
import {prepare} from './analytics.js';
export function rectangle(b){const [w,s,e,n]=b;return {type:'Polygon',coordinates:[[[w,s],[e,s],[e,n],[w,n],[w,s]]]};}
export function feature(geometry){return {type:'Feature',properties:{},geometry};}
// A single SVG path fills overlapping parts once. Orient rings consistently and
// use the nonzero fill rule so comparison regions cannot double the overlay alpha.
export function mergeMapCells(cells){
  const groups=new Map(),points=[];
  for(const cell of cells){
    if(cell.clipped.type==='Point'){points.push(cell);continue;}
    const key=cell.lon+','+cell.lat;
    if(!groups.has(key)){groups.set(key,{...cell,parts:[]});}
    const group=groups.get(key);
    const polygons=cell.clipped.type==='MultiPolygon'?cell.clipped.coordinates:[cell.clipped.coordinates];
    for(const polygon of polygons)group.parts.push(polygon.map((ring,index)=>{
      const area=ring.slice(1).reduce((sum,p,i)=>sum+ring[i][0]*p[1]-p[0]*ring[i][1],0);
      return (area>0)===(index===0)?ring:[...ring].reverse();
    }));
  }
  return [...groups.values()].map(({parts,...cell})=>({...cell,clipped:{type:'MultiPolygon',coordinates:parts}})).concat(points);
}
function containsPoint(lon,lat,geometry){const ring=geometry.coordinates[0];let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>lat)!==(b[1]>lat)&&lon<(b[0]-a[0])*(lat-a[1])/(b[1]-a[1])+a[0])inside=!inside;}return inside;}
export function weightedCells(dataset,geometry){if(!dataset)return [];if(dataset.feature_based)return dataset.cells.filter(c=>containsPoint(c.lon,c.lat,geometry)).map(c=>({...c,area:1,clipped:{type:'Point',coordinates:[c.lon,c.lat]}}));return dataset.cells.map(cell=>{try{const clipped=intersect({type:'FeatureCollection',features:[feature(rectangle(cell.bounds)),feature(geometry)]});if(!clipped)return null;return {...cell,clipped:clipped.geometry,area:area(clipped)};}catch{return null;}}).filter(c=>c&&c.area>0);}
export function regionalRecords(dataset,cells,geometry){if(!dataset||!cells.length)return [];const selected=cells.reduce((s,c)=>s+c.area,0),full=geometry?area(feature(geometry)):selected,total=dataset.domain?selected:full;return dataset.dates.map((date,i)=>{let sum=0,validArea=0,count=0;for(const c of cells){const v=c.values[i];if(Number.isFinite(v)){sum+=v*c.area;validArea+=c.area;count+=c.observation_counts?.[i]||0;}}const coverage=Math.min(1,validArea/total);return {date,value:coverage>=.8&&validArea>0?sum/validArea:null,coverage,...(dataset.domain?{domain_fraction:dataset.feature_based?null:Math.min(1,selected/full)}:{}),...(dataset.feature_based?{observation_count:count}:{})};});}
export function mapValues(dataset,cells,range,season,anomaly,mode='mean'){if(!dataset)return [];return cells.map(cell=>{const records=dataset.dates.map((date,i)=>({date,value:cell.values[i]})),p=prepare(records,...range,season,anomaly),good=p.series.filter(p=>Number.isFinite(p.value));let value=null;if(mode==='trend'&&good.length>=5){const mx=good.reduce((s,p)=>s+p.year,0)/good.length,my=good.reduce((s,p)=>s+p.value,0)/good.length;value=10*good.reduce((s,p)=>s+(p.year-mx)*(p.value-my),0)/good.reduce((s,p)=>s+(p.year-mx)**2,0);}else if(mode!=='trend'&&good.length)value=good.reduce((s,p)=>s+p.value,0)/good.length;return {...cell,mapValue:value,years:good.length};});}
export function fullDomain(dataset,cells,season,anomaly){if(!dataset)return [];const range=[+dataset.dates[0].slice(0,4),+dataset.dates.at(-1).slice(0,4)];return cells.flatMap(cell=>prepare(dataset.dates.map((date,i)=>({date,value:cell.values[i]})),...range,season,anomaly).series.map(p=>p.value)).filter(Number.isFinite);}
export const palettes={temperature:['#3965b6','#58bec2','#e8d387','#e48e57','#bd4d59'],humidity:['#d6bd78','#8fbbaa','#4bbbc5','#3978bc','#5550a6'],wind:['#b8e3d8','#69c5be','#47a1bf','#566cac','#955eaf'],default:['#80c5d2','#6686ba','#8e6bab','#c77d9c','#e9b286']};
export function color(value,min,max,palette){if(value===null)return '#8b9baa';const t=Math.max(0,Math.min(1,(value-min)/(max-min||1)))*(palette.length-1),i=Math.min(palette.length-2,Math.floor(t)),f=t-i;const rgb=h=>h.match(/[\da-f]{2}/gi).map(x=>parseInt(x,16));const a=rgb(palette[i]),b=rgb(palette[i+1]);return '#'+a.map((x,j)=>Math.round(x+(b[j]-x)*f).toString(16).padStart(2,'0')).join('');}
