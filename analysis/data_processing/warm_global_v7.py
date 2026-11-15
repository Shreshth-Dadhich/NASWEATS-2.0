"""Warm every global UI preset with verified NASA values before publication."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import gzip,json,re,time,hashlib
import requests,numpy as np
from .build_public_v7 import parse_ascii,fetch,write_gz,OUT,RAW,REGIONS,GMI,now,sha
regions={**REGIONS,'amazon':[-62,-5,-58,-1],'california':[-123,36,-119,40],'alps':[7,44,11,48],'japan':[137,34,141,38],'australia':[149,-35,153,-31],'cape':[16,-35,20,-31],'arctic':[12,76,16,80]}
met={'temperature':('T2M','C'),'humidity':('RH2M','%'),'wind':('WS10M','m/s'),'precipitation':('PRECTOTCORR','mm/day')}
def power(task):
    region,variable=task;box=regions[region];parameter,unit=met[variable]
    q={'parameters':parameter,'community':'RE','start':1984,'end':2024,'format':'JSON','longitude-min':box[0]-.3125,'longitude-max':box[2]+.3125,'latitude-min':box[1]-.25,'latitude-max':box[3]+.25}
    url='https://power.larc.nasa.gov/api/temporal/monthly/regional?'+requests.compat.urlencode(q)
    raw=fetch(url,RAW/'warm'/f'{region}-{variable}.json');j=json.loads(raw)
    if j.get('parameters',{}).get(parameter,{}).get('units')!=unit:raise ValueError('NASA units mismatch: '+region+variable)
    dates=[f'{y}-{m:02d}-01' for y in range(1984,2025) for m in range(1,13)];cells=[]
    for f in j['features']:
        lon,lat=f['geometry']['coordinates'][:2];p=f['properties']['parameter'][parameter]
        cells.append({'lon':lon,'lat':lat,'bounds':[lon-.3125,lat-.25,lon+.3125,lat+.25],'values':[p.get(d[:4]+d[5:7]) if p.get(d[:4]+d[5:7],-999)!=-999 else None for d in dates]})
    original=OUT/'originals'/f'{region}-{variable}-padded.json.gz';original.write_bytes(gzip.compress(raw,mtime=0))
    source={'label':'NASA POWER / MERRA-2 · '+parameter,'api':j['header']['api'],'field':parameter,'retrieved_utc':now(),'requested_url':url,'source_files':[{'requested_url':url,'raw_url':'/data/originals/'+original.name,'raw_sha256':sha(raw)}],'citation_url':'https://power.larc.nasa.gov/docs/referencing/','resolution':'0.5° latitude × 0.625° longitude','processing':'NASA monthly native-grid values, unchanged. PRECTOTCORR is mean rate in mm/day, not monthly accumulation or direct GPM IMERG.' if variable=='precipitation' else 'NASA POWER monthly native-grid values, unchanged. This is a POWER MERRA-2-derived product, not a direct native mission granule.'}
    if variable=='precipitation':source['measurement_label']='Corrected precipitation rate'
    write_gz(OUT/'ready'/f'{region}-{variable}.json.gz',{'schema_version':2,'source_mode':'public_starter','variable':variable,'parameter':parameter,'unit':unit,'bbox':box,'dates':dates,'cells':cells,'source':source})
    print('POWER ready',region,variable,len(cells),flush=True)

def chemistry(task):
    region,collection,fields,start=task;box=regions[region]
    x0=max(0,int(np.floor((box[0]+180-.3125)/.625)));x1=min(575,int(np.ceil((box[2]+180+.3125)/.625)))
    y0=max(0,int(np.floor((box[1]+90-.25)/.5)));y1=min(360,int(np.ceil((box[3]+90+.25)/.5)));t0=(start-1980)*12
    url=GMI+collection+'.ascii?'+','.join(f'{v}[{t0}:1:{t0+59}][{y0}:1:{y1}][{x0}:1:{x1}]' for v in fields)
    raw=fetch(url,RAW/'warm'/f'{region}-{collection}-{start}.txt');parsed=parse_ascii(raw)
    print('GMI warm',region,collection,start,flush=True)
    return region,collection,start,parsed,{'requested_url':url,'raw_sha256':sha(raw)}

if __name__=='__main__':
    with ThreadPoolExecutor(2) as pool:list(pool.map(power,[(r,v) for r in regions for v in met]))
    jobs=[(r,c,f,y) for r in regions if r not in REGIONS for c,f in [('instM_2d_bot_Nx',['pm25_bot']),('tavgM_2d_aer_Nx',['duexttau']),('tavgM_2d_rad_Nx',['cldlow','ts'])] for y in range(1980,2020,5)]
    results=[]
    with ThreadPoolExecutor(2) as pool:
        for result in pool.map(chemistry,jobs):results.append(result)
    for region in regions:
        if region in REGIONS:continue
        for field,variable,factor,offset in [('pm25_bot','air_quality',1e9,0),('duexttau','dust',1,0),('cldlow','cloud',1,0),('ts','ocean',1,-273.15)]:
            blocks=sorted([x for x in results if x[0]==region and field in x[3]],key=lambda x:x[2]);base=json.loads(gzip.decompress((OUT/'ready'/f'gulf-{variable}.json.gz').read_bytes()))
            base['bbox']=regions[region];base['cells']=[];base['source']['source_files']=[x[4] for x in blocks];base['source']['retrieved_utc']=now()
            lats,lons=blocks[0][3]['lat'],blocks[0][3]['lon'];array=np.concatenate([x[3][field] for x in blocks],axis=0)
            for j,lat in enumerate(lats):
                for i,lon in enumerate(lons):
                    bounds=[float(lon-.3125),float(lat-.25),float(lon+.3125),float(lat+.25)];b=regions[region]
                    if bounds[2]<=b[0] or bounds[0]>=b[2] or bounds[3]<=b[1] or bounds[1]>=b[3]:continue
                    base['cells'].append({'lon':float(lon),'lat':float(lat),'bounds':bounds,'values':[float(v*factor+offset) if abs(v)<1e14 else None for v in array[:,j,i]]})
            write_gz(OUT/'ready'/f'{region}-{variable}.json.gz',base);print('READY',region,variable,flush=True)
