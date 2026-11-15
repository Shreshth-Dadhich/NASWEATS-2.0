import React, {useEffect, useRef} from 'react';

export default function Dialog({children, onClose, label, className=''}) {
  const ref=useRef(null);
  const close=useRef(onClose);close.current=onClose;
  useEffect(()=>{
    const previous=document.activeElement, overflow=document.body.style.overflow;
    document.body.style.overflow='hidden';
    ref.current?.querySelector('button')?.focus();
    function key(e) {
      if(e.key==='Escape'){e.preventDefault();close.current();}
      if(e.key!=='Tab')return;
      const items=[...ref.current.querySelectorAll('button,a[href],input,select,[tabindex="0"]')].filter(e=>!e.disabled&&e.getClientRects().length);
      if(!items.length){e.preventDefault();return;}
      const first=items[0],last=items.at(-1);
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
      else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
    }
    document.addEventListener('keydown',key);
    return()=>{document.body.style.overflow=overflow;document.removeEventListener('keydown',key);previous?.focus();};
  },[]);
  return <div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)onClose();}}><section ref={ref} className={'modal '+className} role="dialog" aria-modal="true" aria-label={label}>{children}</section></div>;
}
