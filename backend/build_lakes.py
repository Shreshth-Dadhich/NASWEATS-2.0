"""NASA GWM feature observations -> monthly means; missing observations stay missing."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from collections import defaultdict
import gzip,hashlib,json,math,xml.etree.ElementTree as ET
import openpyxl,requests
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'nasa-source';OUT=ROOT/'frontend/public/data/lakes';OUT.mkdir(parents=True,exist_ok=True)
RAW.mkdir(exist_ok=True)
for filename,url in [('gwm-index.xml','https://nasa-power.s3.amazonaws.com/?list-type=2&prefix=gwm/&max-keys=1000'),('gwm-10day.xlsx','https://earth.gsfc.nasa.gov/gwm/html/WATER-MONITOR.LakesReservoirs.10day.xlsx'),('gwm-35day.xlsx','https://earth.gsfc.nasa.gov/gwm/html/WATER-MONITOR.LakesReservoirs.35day.xlsx')]:
    if not (RAW/filename).exists():
        response=requests.get(url,timeout=60);response.raise_for_status();(RAW/filename).write_bytes(response.content)
ns={'s':'http://s3.amazonaws.com/doc/2006-03-01/'}
keys=[x.text for x in ET.parse(RAW/'gwm-index.xml').getroot().findall('s:Contents/s:Key',ns) if x.text!='gwm/empty.json']
names={}
for version in ['10day','35day']:
    book=openpyxl.load_workbook(RAW/f'gwm-{version}.xlsx',read_only=True,data_only=True)
    for row in book.active.values:
        if isinstance(row[0],str) and row[0].isdigit() and len(row[0])==6:names.setdefault(row[0],{'name':row[1],'country':row[4],'advisories':[str(x) for x in row[11:] if x is not None]})

def process(key):
    filename=key.split('/')[-1];ident=filename.removesuffix('.json');url='https://nasa-power.s3.amazonaws.com/'+key
    path=RAW/'gwm'/filename;path.parent.mkdir(exist_ok=True)
    if path.exists():raw=path.read_bytes()
    else:
        r=requests.get(url,timeout=(15,60));r.raise_for_status();raw=r.content;path.write_bytes(raw)
    data=json.loads(raw);lon=float(data['coords']['lon']['data'][0]);lat=float(data['coords']['lat']['data'][0])
    if abs(lat)>85:return None
    parameter='GWM_HEIGHT_ANOMALY';field=data['data_vars'].get(parameter)
    if not field or field.get('attrs',{}).get('units')!='m':return None
    times=data['coords']['time']['data'];values=field['data'][0][0]
    months=defaultdict(list)
    for date,value in zip(times,values):
        if isinstance(value,(int,float)) and math.isfinite(value) and abs(value)<10000:months[date[:7]].append(value)
    if not months:return None
    start=min(months);end=max(months);dates=[f'{y}-{m:02d}-01' for y in range(int(start[:4]),int(end[:4])+1) for m in range(1,13) if start<=f'{y}-{m:02d}'<=end]
    info=names.get(ident[4:10],{'name':'NASA lake '+ident[4:10],'country':'','advisories':[]});name=str(info['name'])+' · '+str(info['country'])
    source={'label':'NASA GSFC Global Water Measurements · '+name,'short_name':ident,'version':ident.split('.')[-1],'field':parameter,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'requested_url':url,'original_file_sha256':hashlib.sha256(raw).hexdigest(),'citation_url':'https://earth.gsfc.nasa.gov/gwm/lake/Index','resolution':'Satellite ground-track lake observation; not a gridded field','feature_name':name,'measurement_label':'Lake level anomaly','advisories':info['advisories'],'processing':'Mean of actual valid GWM_HEIGHT_ANOMALY overpasses in each calendar month, in meters. Missing days are not filled. Months require at least one observation; per-month overpass counts are exported. Annual/seasonal analysis still requires every month. This single monitored feature does not represent the mean of a drawn region.'}
    dataset={'schema_version':2,'source_mode':'public_starter','variable':'water_level','parameter':parameter,'unit':'m','feature_based':True,'domain':'feature','dates':dates,'bbox':[lon-.05,lat-.05,lon+.05,lat+.05],'cells':[{'id':ident,'lon':lon,'lat':lat,'bounds':[lon-.05,lat-.05,lon+.05,lat+.05],'values':[sum(months[d[:7]])/len(months[d[:7]]) if months[d[:7]] else None for d in dates],'observation_counts':[len(months[d[:7]]) for d in dates]}],'source':source}
    (OUT/(ident+'.json.gz')).write_bytes(gzip.compress(json.dumps(dataset,separators=(',',':'),allow_nan=False).encode(),mtime=0))
    print(ident,name,len(months),'months',flush=True)
    return {'id':ident,'name':name,'lon':lon,'lat':lat,'start':start,'end':end,'valid_months':sum(bool(x) for x in months.values())}

with ThreadPoolExecutor(4) as pool:entries=[x for x in pool.map(process,keys) if x]
entries.sort(key=lambda x:x['name']);(OUT/'index.json').write_text(json.dumps(entries,separators=(',',':')))
print('NASA GWM ready:',len(entries),'monitored records',flush=True)
