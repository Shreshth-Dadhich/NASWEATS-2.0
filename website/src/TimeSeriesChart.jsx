import {chartTheme} from './visualTheme';
import React,{memo,useMemo,useCallback} from 'react';
import Plotly from 'plotly.js-basic-dist-min';
import createPlotlyComponent from 'react-plotly.js/factory';
const Plot=createPlotlyComponent(Plotly);
function series(a,label,line,fill,monthly,unit){
  if(!a?.series)return [];
  const p=monthly?a.monthly:a.series;
  const traces=[{x:p.map(p=>p.date),y:p.map(p=>p.value),type:'scatter',mode:monthly?'lines':'lines+markers',name:label,line:{color:line,width:1.8,shape:'linear'},marker:{size:4},connectgaps:false,hovertemplate:(monthly?'%{x|%Y-%m}':'%{x|%Y}')+': %{y:.6g} '+unit+'<extra>'+label+'</extra>'}];
  if(a.available){const x=a.bands.map(p=>`${p.year}-07-01`);traces.push({x,y:a.bands.map(p=>p.high),type:'scatter',mode:'lines',line:{width:0},showlegend:false,hoverinfo:'skip'},{x,y:a.bands.map(p=>p.low),type:'scatter',mode:'lines',line:{width:0},fill:'tonexty',fillcolor:fill,showlegend:false,hoverinfo:'skip'},{x,y:a.bands.map(p=>p.fit),type:'scatter',mode:'lines',name:label+' OLS',line:{color:line,width:2.5,dash:'dash'},hoverinfo:'skip'});}
  return traces;
}
export default memo(function TimeSeriesChart({analysis,analysisB,label,labelB,compare,monthly,unit,theme,identity,plotRef}){
  const c=chartTheme(theme);
  const traces=useMemo(()=>[...series(analysis,label,c.primary,c.fill,monthly,unit),...(compare?series(analysisB,labelB,c.secondary,c.secondaryFill,monthly,unit):[])],[analysis,analysisB,label,labelB,compare,monthly,unit,theme]);
  const layout=useMemo(()=>({autosize:true,height:285,paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{color:c.text,family:'IBM Plex Sans, system-ui',size:10},margin:{l:50,r:15,t:18,b:35},xaxis:{type:'date',gridcolor:c.grid,zeroline:false},yaxis:{title:{text:unit,font:{size:10}},gridcolor:c.grid,zeroline:false},legend:{orientation:'h',y:1.15,x:0,font:{size:9}},hovermode:'x unified',hoverlabel:{bgcolor:c.surface,bordercolor:c.grid,font:{family:'IBM Plex Mono, monospace',color:c.ink,size:11}},uirevision:identity+monthly}),[theme,unit,identity,monthly]);
  const config=useMemo(()=>({displaylogo:false,responsive:true,modeBarButtonsToRemove:['lasso2d','select2d'],toImageButtonOptions:{format:'svg',filename:'earthsignal-chart'}}),[]);
  const onGraph=useCallback((f,g)=>{plotRef.current=g;},[plotRef]);
  return <div className="time-series-plot" style={{height:285,minWidth:0,position:'relative'}}><Plot data={traces} layout={layout} config={config} useResizeHandler style={{width:'100%',height:'100%',position:'relative',display:'block'}} onInitialized={onGraph} onUpdate={onGraph}/></div>;
});
