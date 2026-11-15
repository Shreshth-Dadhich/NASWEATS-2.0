import React,{useState,useEffect,lazy,Suspense} from 'react';
import ScrollMotion from './ScrollMotion';import Dashboard from './Dashboard';
const ResearchStudy=lazy(()=>import('./ResearchStudy'));
export default function App(){
 const [study,setStudy]=useState(()=>location.hash.startsWith('#study')||location.hash.startsWith('#research-stud')?{}:null);
 useEffect(()=>{function route(){const hash=location.hash;if(hash.startsWith('#study')||hash.startsWith('#research-stud'))setStudy(previous=>previous||{});else if(hash==='#observatory'||hash==='')setStudy(null);}window.addEventListener('hashchange',route);window.addEventListener('popstate',route);return()=>{window.removeEventListener('hashchange',route);window.removeEventListener('popstate',route);};},[]);
 function open(variable){history.replaceState(null,'','#study');setStudy({variable});window.scrollTo({top:0,behavior:'instant'});}
 function back(){history.replaceState(null,'','#observatory');setStudy(null);requestAnimationFrame(()=>document.getElementById('observatory')?.scrollIntoView({block:'start',behavior:'instant'}));}
 return <><ScrollMotion/><div style={{display:study?'none':undefined}}><Dashboard initialVariable="temperature" onOpenStudy={open}/></div>{study&&<Suspense fallback={<p className="study-page-loading" role="status">Loading verified supplied study…</p>}><ResearchStudy initialVariable={study.variable} onBack={back}/></Suspense>}</>;
}
