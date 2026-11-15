from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import gzip,json,math,re
import numpy as np
from build_public_v7 import fetch,parse_ascii,write_gz,OUT,RAW,GMI,sha,now
METRICS={'soil_root': ('tavgM_2d_lnd_Nx', 'gwetroot', '1', 1.0, 'dimensionless', 'Root-zone soil wetness', 'land'),
 'soil_top': ('tavgM_2d_lnd_Nx', 'gwettop', '1', 1.0, 'dimensionless', 'Topsoil wetness', 'land'),
 'precip_gmi': ('tavgM_2d_flx_Nx', 'prectot', 'kg m-2 s-1', 86400.0, 'mm/day', 'Precipitation rate · PRECTOT', None),
 'precip_corr_gmi': ('tavgM_2d_flx_Nx', 'prectotcorr', 'kg m-2 s-1', 86400.0, 'mm/day', 'Precipitation rate · PRECTOTCORR', None)}
REGIONS={'gulf':[48,24,52,28],'california':[-123,36,-119,40]}
GROUPS={'tavgM_2d_lnd_Nx':['gwetroot','gwettop'],'tavgM_2d_flx_Nx':['prectot','prectotcorr']}
def build():
 metadata={}
 for c,fields in GROUPS.items():
  raw=fetch(GMI+c+'.das',RAW/'interactive'/f'{c}.das');text=raw.decode();name='interactive-'+c+'.das.gz';(OUT/'originals'/name).write_bytes(gzip.compress(raw,mtime=0))
  for variable,(collection,field,unit,*_) in METRICS.items():
   if collection!=c:continue
   m=re.search(r'    '+field+r' \{([\s\S]*?)\n    \}',text);assert m and 'String units "'+unit+'"' in m.group(1)
  metadata[c]={'requested_url':GMI+c+'.das','raw_url':'/data/originals/'+name,'raw_sha256':sha(raw)}
 def acquire(task):
  region,c,start=task;b=REGIONS[region];x0=max(0,math.floor((b[0]+180-.3125)/.625));x1=min(575,math.ceil((b[2]+180+.3125)/.625));y0=max(0,math.floor((b[1]+90-.25)/.5));y1=min(360,math.ceil((b[3]+90+.25)/.5));t=(start-1980)*12
  url=GMI+c+'.ascii?'+','.join(f'{f}[{t}:1:{t+59}][{y0}:1:{y1}][{x0}:1:{x1}]' for f in GROUPS[c]);raw=fetch(url,RAW/'interactive'/f'{region}-{c}-{start}.txt');parsed=parse_ascii(raw);name=f'interactive-{region}-{c}-{start}.txt.gz';(OUT/'originals'/name).write_bytes(gzip.compress(raw,mtime=0));print('NASA subset',region,c,start,flush=True)
  return region,c,start,parsed,{'requested_url':url,'raw_url':'/data/originals/'+name,'raw_sha256':sha(raw)}
 with ThreadPoolExecutor(2) as pool:blocks=list(pool.map(acquire,[(r,c,y) for r in REGIONS for c in GROUPS for y in range(1980,2020,5)]))
 for region,bbox in REGIONS.items():
  for variable,(c,field,native,factor,unit,label,domain) in METRICS.items():
   parts=sorted([b for b in blocks if b[0]==region and b[1]==c],key=lambda b:b[2]);array=np.concatenate([b[3][field] for b in parts]);lat,lon=parts[0][3]['lat'],parts[0][3]['lon'];cells=[]
   for j,y in enumerate(lat):
    for i,x in enumerate(lon):
     bounds=[float(x-.3125),float(y-.25),float(x+.3125),float(y+.25)]
     if bounds[2]<=bbox[0] or bounds[0]>=bbox[2] or bounds[3]<=bbox[1] or bounds[1]>=bbox[3]:continue
     mask=np.concatenate([p[3]['gwetroot'] for p in parts])[:,j,i] if domain else np.zeros(len(array))
     values=[float(v*factor) if abs(v)<1e14 and abs(mask[k])<1e14 else None for k,v in enumerate(array[:,j,i])]
     if domain and not any(v is not None for v in values):continue
     cells.append({'lon':float(x),'lat':float(y),'bounds':bounds,'values':values})
   source={'label':'NASA MERRA2-GMI monthly replay · '+label,'measurement_label':label,'short_name':c,'field':field,'version':'NCCS monthly 1980–2019 archive','native_unit':native,'retrieved_utc':now(),'requested_url':GMI+c+'.info','source_files':[p[4] for p in parts],'metadata':metadata[c],'citation_url':'https://opendap.nccs.nasa.gov/dods/merra2_gmi','resolution':'0.5° latitude × 0.625° longitude','processing':f'Native monthly {field}; multiply by {factor:g} to obtain {unit}. Annual/seasonal views use day-weighted means, not sums. This NASA chemistry replay is distinct from the supplied 2000–2025 MERRA-2 regional study. Global surface-dust concentrations are not enabled because their archive failed the source-quality audit. Topsoil uses gwetroot missing-value validity as the land mask. PRECTOT and PRECTOTCORR are identical in the audited Gulf/California replay records; no difference is invented. Soil wetness is not groundwater. Precipitation here is mean rate, not monthly total. Missing values stay missing.'}
   d={'schema_version':2,'source_mode':'public_starter','variable':variable,'parameter':field,'unit':unit,'bbox':bbox,'dates':[f'{y}-{m:02d}-01' for y in range(1980,2020) for m in range(1,13)],'cells':cells,'source':source}
   if domain:d['domain']=domain
   write_gz(OUT/'ready'/f'{region}-{variable}.json.gz',d);v=[v for cell in cells for v in cell['values'] if v is not None];print('READY',region,variable,len(cells),'range',min(v) if v else None,max(v) if v else None,flush=True)
if __name__=='__main__':build()
