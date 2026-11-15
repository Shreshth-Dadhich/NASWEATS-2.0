import {chartTheme} from './visualTheme';
import React,{memo,useMemo} from 'react';
import Plotly from 'plotly.js-basic-dist-min';
import createPlotlyComponent from 'react-plotly.js/factory';
const Plot=createPlotlyComponent(Plotly);
export default memo(function StudyChart({traces,xTitle,yTitle,identity,theme,options={},height=360}){
 const c=chartTheme(theme);
 const colored=useMemo(()=>traces.map((t,i)=>({...t,hovertemplate:t.hovertemplate?.replaceAll(':.5g',':.7g'),...(t.line?{line:{...t.line,color:t.line.color||(i%2?c.secondary:c.primary),shape:'linear'}}:{}),...(t.marker?{marker:{...t.marker,color:t.marker.color||(i%2?c.secondary:c.primary)}}:{})})),[traces,theme]);
 const layout=useMemo(()=>({autosize:true,height:320,paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{family:'IBM Plex Sans, system-ui',size:11,color:c.text},margin:{l:68,r:24,t:36,b:55},xaxis:{title:{text:xTitle},gridcolor:c.grid,zeroline:false},yaxis:{title:{text:yTitle},gridcolor:c.grid,zeroline:false},legend:{orientation:'h',y:1.13},uirevision:identity,hovermode:'closest',hoverlabel:{bgcolor:c.surface,bordercolor:c.grid,font:{family:'IBM Plex Mono, monospace',color:c.ink,size:11}} }),[xTitle,yTitle,identity,theme]);
 const config=useMemo(()=>({responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d'],toImageButtonOptions:{format:'svg',filename:'earthsignal-arabian-study'}}),[]);
 return <div className="study-chart-canvas" style={{height}}><Plot data={colored} layout={{...layout,height,...options}} config={config} useResizeHandler style={{width:'100%',height:'100%',position:'relative',display:'block'}}/></div>;
});
