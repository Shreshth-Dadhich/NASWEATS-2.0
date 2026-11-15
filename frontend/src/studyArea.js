// Operational study extent, not a political or administrative boundary.
export const MIDDLE_EAST=[24,12,64,42];
export const AREA_LABEL='24–64°E · 12–42°N';
export function inStudyArea(lon,lat,margin=0){const [w,s,e,n]=MIDDLE_EAST;return Number.isFinite(lon)&&Number.isFinite(lat)&&lon>=w+margin&&lon<=e-margin&&lat>=s+margin&&lat<=n-margin;}
const lakeCountries=new Set(['Egypt','Turkey','Iran','Iraq','Syria','Lebanon','Jordan','Israel','Palestine','Saudi Arabia','Yemen','Oman','United Arab Emirates','UAE','Kuwait','Qatar','Bahrain','Cyprus']);
export function regionalLake(lake){return inStudyArea(lake.lon,lake.lat,.1)&&lakeCountries.has(lake.name.split('·').at(-1).trim());}
export function assertStudyArea(geometry){
 const rings=geometry?.type==='Polygon'?geometry.coordinates:null;
 if(!rings?.length||!rings.every(r=>r.length>=4&&r.every(p=>inStudyArea(p[0],p[1]))))throw Error('Keep the entire selection inside the Middle East study extent: 24–64°E, 12–42°N.');
 return geometry;
}
