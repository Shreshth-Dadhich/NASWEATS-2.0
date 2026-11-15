import {useEffect,useRef,useState} from 'react';
const numerical=d=>d?{dates:d.dates,cells:d.cells,unit:d.unit,domain:d.domain,feature_based:d.feature_based}:null;
const EMPTY={analysis:{available:false,series:[],monthly:[],reason:'Load NASA measurements to calculate a trend.'},analysisB:{available:false,series:[],monthly:[]},records:[],recordsB:[],mapped:[],domain:[0,1],cellsCount:0,cellsBCount:0};

export default function useAnalysis({data,dataB,geometry,geometryB,options}){
  const worker=useRef(null),version=useRef(0),serial=useRef(0),latest=useRef(options),timer=useRef(null),running=useRef(false),queued=useRef(false),lastKey=useRef('');
  const [state,setState]=useState({result:EMPTY,processing:false,error:null});
  latest.current=options;
  function run(){
    if(!worker.current||!data)return;
    if(running.current){queued.current=true;return;}
    const key=JSON.stringify(latest.current);
    if(key===lastKey.current){setState(s=>({...s,processing:false}));return;}
    running.current=true;queued.current=false;lastKey.current=key;
    worker.current.postMessage({type:'compute',version:version.current,id:++serial.current,options:latest.current});
  }
  const runRef=useRef(run);runRef.current=run;
  useEffect(()=>{
    const w=new Worker(new URL('./analysis.worker.js',import.meta.url),{type:'module'});worker.current=w;
    w.onmessage=({data:m})=>{
      if(m.version!==version.current)return;
      running.current=false;
      if(m.error)setState(s=>({...s,processing:false,error:m.error}));
      else setState({result:{...m.result,options:m.options},processing:JSON.stringify(m.options)!==JSON.stringify(latest.current),error:null});
      if(queued.current||JSON.stringify(m.options)!==JSON.stringify(latest.current))runRef.current();
    };
    w.onerror=()=>setState(s=>({...s,processing:false,error:'The analysis worker could not load. Reload the page to retry.'}));
    return()=>{clearTimeout(timer.current);w.terminate();};
  },[]);
  useEffect(()=>{
    clearTimeout(timer.current);timer.current=null;version.current++;lastKey.current=JSON.stringify(latest.current);running.current=!!data;queued.current=false;
    setState({result:EMPTY,processing:!!data,error:null});
    worker.current?.postMessage({type:'init',version:version.current,id:++serial.current,input:{version:version.current,a:numerical(data),b:numerical(dataB),geometry,geometryB},options:latest.current});
  },[data,dataB,geometry,geometryB]);
  useEffect(()=>{
    if(!data)return;
    setState(s=>({...s,processing:true}));queued.current=true;
    if(!timer.current)timer.current=setTimeout(()=>{timer.current=null;runRef.current();},70);
  },[options.range[0],options.range[1],options.season,options.anomaly,options.confidence,options.mapMode]);
  return {...state,...state.result};
}
