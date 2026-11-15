import React,{useEffect} from 'react';
export default function ScrollMotion(){
 useEffect(()=>{
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');let frame=0;
  const seen=new WeakSet();
  const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('is-revealed');observer.unobserve(e.target);}}),{threshold:.06});
  function scan(){if(reduced.matches)return;document.querySelectorAll('.panel,.case-card,.guide-card,.guide-step,.guide-heading').forEach(el=>{if(seen.has(el))return;seen.add(el);if(el.getBoundingClientRect().top>innerHeight){el.classList.add('scroll-reveal');observer.observe(el);}});}
  function update(){frame=0;const height=document.documentElement.scrollHeight-innerHeight,scroll=document.documentElement.scrollTop;document.documentElement.style.setProperty('--reading-progress',height>0?Math.min(1,scroll/height):0);document.documentElement.style.setProperty('--hero-shift',reduced.matches?'0px':`${Math.min(scroll*.12,70)}px`);}
  function onScroll(){if(!frame)frame=requestAnimationFrame(update);}
  const mutations=new MutationObserver(scan);mutations.observe(document.getElementById('root'),{childList:true,subtree:true});scan();update();window.addEventListener('scroll',onScroll,{passive:true});window.addEventListener('resize',onScroll,{passive:true});
  return()=>{observer.disconnect();mutations.disconnect();cancelAnimationFrame(frame);window.removeEventListener('scroll',onScroll);window.removeEventListener('resize',onScroll);};
 },[]);
 return <div className="reading-progress" aria-hidden="true"/>;
}
