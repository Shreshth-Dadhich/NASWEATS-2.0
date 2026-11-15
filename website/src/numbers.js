export function number(value,decimals=3){
  if(!Number.isFinite(value))return '—';
  return value!==0&&Math.abs(value)<10**(-decimals)?value.toExponential(2):value.toFixed(decimals);
}
export function signed(value){return Number.isFinite(value)?(value>=0?'+':'−')+number(Math.abs(value)):'—';}
