import {useEffect,useRef} from 'react';
import {useMap} from 'react-leaflet';
import L from 'leaflet';
import {color} from './spatial';import {number} from './numbers';

export default function GridLayer({cells,domain,palette,unit,variable,range,opacity,tool}){
  const map=useMap(),group=useRef(null),current=useRef(null);
  current.current={cells:new Map(cells.map(c=>[c.lon+','+c.lat,c])),domain,palette,unit,variable,range,opacity,tool};
  const shapeKey=JSON.stringify(cells.map(c=>[c.lon,c.lat,c.clipped]));
  function style(feature){const s=current.current,c=s.cells.get(feature.properties.key);return {fillRule:'nonzero',color:'#f4ead8',weight:.55,opacity:.35,fillColor:color(c.mapValue,...s.domain,s.palette),fillOpacity:c.mapValue===null?0:s.opacity,interactive:!s.tool};}
  useEffect(()=>{
    const renderer=L.canvas({padding:.25});
    group.current=L.geoJSON({type:'FeatureCollection',features:cells.map(c=>({type:'Feature',properties:{key:c.lon+','+c.lat},geometry:c.clipped}))},{renderer,style,pointToLayer:(feature,latlng)=>L.circleMarker(latlng,{radius:7,renderer}),onEachFeature:(feature,layer)=>{
      layer.bindTooltip(()=>{
        const s=current.current,c=s.cells.get(feature.properties.key),node=document.createElement('div');node.style.whiteSpace='pre-line';
        node.textContent=`${s.variable}: ${c.mapValue===null?'insufficient complete data':number(c.mapValue,4)+' '+s.unit}\n${c.years} complete annual/seasonal samples · ${s.range[0]}–${s.range[1]}\n${c.clipped.type==='Point'?'Monitored feature; not a regional grid.':'NASA source cell; no spatial interpolation.'}`;return node;
      });
    }}).addTo(map);
    return()=>{group.current?.remove();renderer.remove();group.current=null;};
  },[map,shapeKey]);
  useEffect(()=>{group.current?.setStyle(style);group.current?.eachLayer(layer=>{layer.options.interactive=!tool;});},[cells,domain,palette,opacity,tool]);
  return null;
}
