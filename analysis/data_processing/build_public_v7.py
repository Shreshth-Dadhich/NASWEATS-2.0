"""Reproducible, anonymous NASA caches. No generated environmental values.

Run --grace for GSFC native equal-area mascons, --power for precipitation,
--gmi for monthly chemistry-replay subsets. Original responses are retained.
"""
from pathlib import Path
import argparse,calendar,concurrent.futures,gzip,hashlib,json,math,re,time
from datetime import datetime,timedelta,timezone
import numpy as np
import requests

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'nasa-source'
OUT=ROOT/'data/processed/nasa'
REGIONS={'gulf':[48,24,52,28],'empty':[48,19,52,23],'tigris':[42,32,46,36],'redsea':[36,20,40,24],'nile':[29,29,33,33]}
GMI='https://opendap.nccs.nasa.gov/dods/merra2_gmi/'
GRACE='https://earth.gsfc.nasa.gov/sites/default/files/geo/GSFC.glb_.200204_202606_RL06v2.0_'

def compact(value):return json.dumps(value,separators=(',',':'),allow_nan=False).encode()
def write_gz(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress(compact(value),compresslevel=6,mtime=0))
def now():return datetime.now(timezone.utc).isoformat()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def fetch(url,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():return path.read_bytes()
    for attempt in range(3):
        try:
            r=requests.get(url,timeout=(20,150));r.raise_for_status()
            if r.content.startswith(b'<html'):raise ValueError('NASA returned HTML instead of numerical data')
            path.write_bytes(r.content);return r.content
        except Exception:
            if attempt==2:raise
            time.sleep(2*(attempt+1))

def build_grace(kind):
    import h5py
    name='OBP' if kind=='water' else 'SLA'
    path=RAW/('grace-obp.h5' if kind=='water' else 'grace-sla.h5')
    url=GRACE+name+'-ICE6GD.h5'
    if path.exists() and path.stat().st_size<174165410:path.unlink()
    if not path.exists():fetch(url,path)
    digest=sha(path.read_bytes())
    with h5py.File(path) as f:
        lat=f['mascon/lat_center'][0];lon=f['mascon/lon_center'][0]
        lon=np.where(lon>180,lon-360,lon)
        h=f['mascon/lat_span'][0];w=f['mascon/lon_span'][0]
        flags=f['mascon/location'][0]
        middle=f['time/ref_days_middle'][0]
        dates=[(datetime(2001,12,31)+timedelta(days=float(d))).strftime('%Y-%m-01') for d in middle]
        all_dates=[f'{y}-{m:02d}-01' for y in range(2002,2027) for m in range(1,13) if f'{y}-{m:02d}'<='2026-06']
        groups={date:[i for i,d in enumerate(dates) if d==date] for date in all_dates}
        values=f['solution/cmwe'][:]
        source={'label':f'NASA GSFC GRACE/GRACE-FO {name} RL06v2.0','short_name':f'GSFC.glb.200204_202606_RL06v2.0_{name}-ICE6GD','version':'RL06v2.0','field':'solution/cmwe','retrieved_utc':now(),'requested_url':url,'original_file_sha256':digest,'citation_url':'https://earth.gsfc.nasa.gov/geo/data/grace-mascons','resolution':'1° equal-area mascons; neighboring cells are correlated','processing':'Exact GSFC solution/cmwe values in cm equivalent water height. Each solution is assigned to its published midpoint calendar month; multiple solutions in a month are averaged. Missing months and the mission gap remain null. Means use only selected land mascons.' if kind=='water' else 'Ocean mascons from GSFC SLA product: mass component of sea-level anomaly in cm equivalent water height. Thermal expansion and tidal analysis are not included. Missing months remain null. Means use only selected ocean mascons.','reference_baseline':'2004.0–2010.0','uncertainty_note':'Source noise/leakage uncertainty is available in the original HDF5; it is not included in regression confidence intervals.'}
        tiles={}
        for i in range(len(lat)):
            if (kind=='water' and flags[i]!=80) or (kind!='water' and flags[i]!=90):continue
            if abs(lat[i])>85.5:continue
            cell={'id':int(i),'lon':float(lon[i]),'lat':float(lat[i]),'bounds':[max(-180,float(lon[i]-w[i]/2)),float(lat[i]-h[i]/2),min(180,float(lon[i]+w[i]/2)),float(lat[i]+h[i]/2)],'values':[float(np.mean(values[i,groups[d]])) if groups[d] else None for d in all_dates]}
            key=f'{math.floor((lon[i]+180)/10)}-{math.floor((lat[i]+90)/10)}'
            tiles.setdefault(key,[]).append(cell)
        directory=OUT/'grace'/kind;directory.mkdir(parents=True,exist_ok=True)
        for old in directory.glob('*.json.gz'):old.unlink()
        tile_index=[]
        for key,cells in tiles.items():
            write_gz(directory/(key+'.json.gz'),{'schema_version':2,'source_mode':'public_starter','variable':kind,'parameter':'cmwe_'+name,'unit':'cm','domain':'land' if kind=='water' else 'ocean','dates':all_dates,'cells':cells,'source':source})
            tile_index.append({'key':key,'bounds':[min(c['bounds'][0] for c in cells),min(c['bounds'][1] for c in cells),max(c['bounds'][2] for c in cells),max(c['bounds'][3] for c in cells)]})
        (directory/'manifest.json').write_bytes(compact({'source':source,'dates':all_dates,'keys':list(tiles),'tiles':tile_index,'n_cells':sum(map(len,tiles.values()))}))
        print(kind,len(tiles),'tiles',sum(map(len,tiles.values())),'mascons',flush=True)

def parse_ascii(raw):
    text=raw.decode();parts=re.split(r'(?m)^([a-z][a-z0-9_]*), \[',text)
    result={}
    for i in range(1,len(parts),2):
        name,body=parts[i],parts[i+1]
        first,*lines=body.splitlines();shape=[int(x) for x in re.findall(r'\d+',first)]
        vals=[]
        for line in lines:
            if not line.strip():continue
            if line.startswith('['):line=line.split(',',1)[1]
            vals.extend(float(v) for v in line.split(',') if v.strip())
        if len(vals)!=math.prod(shape):raise ValueError(f'{name}: expected {shape}, got {len(vals)}')
        result[name]=np.array(vals).reshape(shape)
    if not result:raise ValueError('No numerical OPeNDAP arrays returned')
    return result

def gmi_request(year,collection,variables):
    # A single source rectangle covers the original five Middle East sectors.
    a,b=(year-1980)*12,(year-1980)*12+11
    lat0,lat1=215,253;lon0,lon1=333,373
    query=','.join(f'{v}[{a}:1:{b}][{lat0}:1:{lat1}][{lon0}:1:{lon1}]' for v in variables)
    url=GMI+collection+'.ascii?'+query
    path=RAW/'gmi'/f'{collection}-{year}.txt'
    raw=fetch(url,path);data=parse_ascii(raw)
    for v in variables:
        if v not in data or not np.any(data[v]<1e14):raise ValueError(f'NASA {v} has no valid values')
    target=OUT/'originals'/f'{collection}-{year}.txt.gz';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(gzip.compress(raw,mtime=0))
    print(collection,year,len(raw),'bytes',flush=True)
    return year,data,{'requested_url':url,'raw_url':'/data/originals/'+target.name,'raw_sha256':sha(raw)}

def build_gmi(air_only=False):
    config=[('instM_2d_bot_Nx',['pm25_bot'])] if air_only else [('tavgM_2d_aer_Nx',['pm25','duexttau']),('tavgM_2d_rad_Nx',['cldlow','ts']),('instM_2d_bot_Nx',['pm25_bot'])]
    for collection,variables in config:
        jobs=[(year,collection,variables) for year in range(1980,2020)]
        with concurrent.futures.ThreadPoolExecutor(2) as pool:results=list(pool.map(lambda a:gmi_request(*a),jobs))
        results.sort(key=lambda x:x[0]);lats=results[0][1]['lat'];lons=results[0][1]['lon'];dates=[f'{y}-{m:02d}-01' for y in range(1980,2020) for m in range(1,13)]
        for field in variables:
            if field=='pm25':continue # Audited source has suspect archive months; use the separate bottom-layer collection throughout.
            variable={'pm25_bot':'air_quality','duexttau':'dust','cldlow':'cloud','ts':'ocean'}[field]
            unit={'pm25_bot':'µg/m³','duexttau':'1','cldlow':'fraction','ts':'°C'}[field]
            label={'pm25_bot':'Reconstructed bottom-layer PM2.5','duexttau':'Dust optical depth at 550 nm','cldlow':'Low-cloud fraction','ts':'Surface skin temperature'}[field]
            arrays=np.concatenate([d[field] for _,d,_ in results],axis=0)
            if field=='pm25_bot':arrays=arrays*1e9
            if field=='ts':arrays=arrays-273.15
            for region,box in REGIONS.items():
                cells=[]
                for j,lat in enumerate(lats):
                    for i,lon in enumerate(lons):
                        bounds=[float(lon-.3125),float(lat-.25),float(lon+.3125),float(lat+.25)]
                        if bounds[2]<=box[0] or bounds[0]>=box[2] or bounds[3]<=box[1] or bounds[1]>=box[3]:continue
                        cells.append({'lon':float(lon),'lat':float(lat),'bounds':bounds,'values':[float(v) if abs(v)<1e12 else None for v in arrays[:,j,i]]})
                source={'label':'NASA MERRA2-GMI monthly replay · '+label,'short_name':collection,'version':'NCCS monthly 1980–2019 archive','field':field,'native_unit':'kg m-3' if field=='pm25_bot' else 'K' if field=='ts' else '1','retrieved_utc':now(),'requested_url':GMI+collection+'.info','citation_url':'https://opendap.nccs.nasa.gov/dods/merra2_gmi','resolution':'0.5° latitude × 0.625° longitude','source_files':[s for _,_,s in results],'processing':('Source pm25_bot in kg/m³ multiplied by 10^9 to µg/m³. This is the separate monthly bottom-layer product, not the aerosol-collection pm25 field.' if field=='pm25_bot' else 'Source ts in kelvin minus 273.15.' if field=='ts' else 'Native monthly values, unchanged.')+' NASA chemistry replay, distinct from direct MERRA-2 mission products. Archive ends December 2019; later observations are not fabricated.','measurement_label':label,'not_native_product':'Explicit NASA MERRA2-GMI replay alternative. Not a direct native mission granule.'}
                write_gz(OUT/'ready'/f'{region}-{variable}.json.gz',{'schema_version':2,'source_mode':'public_starter','variable':variable,'parameter':field,'unit':unit,'bbox':box,'dates':dates,'cells':cells,'source':source})
                print(region,variable,len(cells),'cells',flush=True)

def build_power():
    for region,box in REGIONS.items():
        url='https://power.larc.nasa.gov/api/temporal/monthly/regional?'+requests.compat.urlencode({'parameters':'PRECTOTCORR','community':'RE','start':1984,'end':2024,'format':'JSON','longitude-min':box[0],'longitude-max':box[2],'latitude-min':box[1],'latitude-max':box[3]})
        raw=fetch(url,RAW/f'{region}-precipitation.json');j=json.loads(raw)
        if j.get('parameters',{}).get('PRECTOTCORR',{}).get('units')!='mm/day':raise ValueError('Unexpected precipitation units')
        dates=[f'{y}-{m:02d}-01' for y in range(1984,2025) for m in range(1,13)]
        cells=[]
        for f in j['features']:
            lon,lat=f['geometry']['coordinates'][:2];v=f['properties']['parameter']['PRECTOTCORR']
            cells.append({'lon':lon,'lat':lat,'bounds':[lon-.3125,lat-.25,lon+.3125,lat+.25],'values':[v.get(d[:4]+d[5:7]) if v.get(d[:4]+d[5:7],-999)!=-999 else None for d in dates]})
        if not any(v is not None for c in cells for v in c['values']):raise ValueError('NASA returned all missing precipitation')
        target=OUT/'originals'/f'{region}-precipitation.json.gz';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(gzip.compress(raw,mtime=0))
        write_gz(OUT/'ready'/f'{region}-precipitation.json.gz',{'schema_version':2,'source_mode':'public_starter','variable':'precipitation','parameter':'PRECTOTCORR','unit':'mm/day','bbox':box,'dates':dates,'cells':cells,'source':{'label':'NASA POWER / MERRA-2 corrected precipitation','api':j['header']['api'],'field':'PRECTOTCORR','retrieved_utc':now(),'requested_url':url,'source_files':[{'requested_url':url,'raw_url':'/data/originals/'+target.name,'raw_sha256':sha(raw)}],'citation_url':'https://power.larc.nasa.gov/docs/referencing/','resolution':'0.5° latitude × 0.625° longitude','processing':'NASA PRECTOTCORR monthly mean precipitation rate in mm/day. Not monthly accumulation and not a GPM IMERG granule.','measurement_label':'Corrected precipitation rate'}})
        print(region,'precipitation',len(cells),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--grace',action='store_true');parser.add_argument('--gmi',action='store_true');parser.add_argument('--power',action='store_true');parser.add_argument('--airquality',action='store_true');args=parser.parse_args()
    if args.grace:
        build_grace('water');build_grace('sea_level')
    if args.power:build_power()
    if args.gmi:build_gmi()
    if args.airquality:build_gmi(air_only=True)
