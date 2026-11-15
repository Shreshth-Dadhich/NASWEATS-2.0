import {boundsOf} from './acquisition.js';

export function validateDrawnPolygon(geometry){
  boundsOf(geometry);
  const ring=geometry.coordinates[0],last=ring.at(-1);
  if(ring[0][0]!==last[0]||ring[0][1]!==last[1])throw Error('Close the polygon boundary.');
  const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  const on=(a,b,p)=>Math.abs(cross(a,b,p))<1e-12&&p[0]>=Math.min(a[0],b[0])-1e-12&&p[0]<=Math.max(a[0],b[0])+1e-12&&p[1]>=Math.min(a[1],b[1])-1e-12&&p[1]<=Math.max(a[1],b[1])+1e-12;
  const vertices=new Set(ring.slice(0,-1).map(p=>p[0]+','+p[1]));
  if(vertices.size!==ring.length-1)throw Error('Polygon vertices repeat. Draw a simple boundary.');
  let twiceArea=0;
  for(let i=0;i<ring.length-1;i++){
    twiceArea+=cross(ring[0],ring[i],ring[i+1]);
    for(let j=i+2;j<ring.length-1;j++){
      if(i===0&&j===ring.length-2)continue;
      const a=ring[i],b=ring[i+1],c=ring[j],d=ring[j+1];
      if((cross(a,b,c)*cross(a,b,d)<0&&cross(c,d,a)*cross(c,d,b)<0)||on(a,b,c)||on(a,b,d)||on(c,d,a)||on(c,d,b))throw Error('Polygon edges cross or touch. Draw a simple boundary.');
    }
  }
  if(Math.abs(twiceArea)<1e-14)throw Error('The polygon has no measurable area.');
  return geometry;
}
