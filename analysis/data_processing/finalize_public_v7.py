"""Attach exact NASA metadata bytes and make measurement scope explicit."""
from pathlib import Path
import gzip,hashlib,json,re
import requests
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/processed/nasa'
metadata={}
for name in ['tavgM_2d_aer_Nx','tavgM_2d_rad_Nx','instM_2d_bot_Nx']:
    url='https://opendap.nccs.nasa.gov/dods/merra2_gmi/'+name+'.das'
    r=requests.get(url,timeout=30);r.raise_for_status();raw=r.content
    target=OUT/'originals'/(name+'.das.gz');target.write_bytes(gzip.compress(raw,mtime=0))
    metadata[name]={'requested_url':url,'raw_url':'/data/originals/'+target.name,'raw_sha256':hashlib.sha256(raw).hexdigest()}
    text=raw.decode()
    for field,unit in {'pm25_bot':'kg m-3','duexttau':'1','cldlow':'1','ts':'K'}.items():
        match=re.search(r'    '+field+r' \{([\s\S]*?)\n    \}',text)
        if match and f'String units "{unit}"' not in match.group(1):raise ValueError('NASA metadata units changed for '+field)
for path in (OUT/'ready').glob('*.json.gz'):
    d=json.loads(gzip.decompress(path.read_bytes()))
    if d['source'].get('short_name') in metadata:d['source']['metadata']=metadata[d['source']['short_name']]
    if d['variable']=='ocean':d['source']['measurement_label']='Surface skin temperature (land + sea)'
    path.write_bytes(gzip.compress(json.dumps(d,separators=(',',':'),allow_nan=False).encode(),compresslevel=6,mtime=0))
for kind in ['water','sea_level']:
    directory=OUT/'grace'/kind
    manifest=json.loads((directory/'manifest.json').read_bytes())
    manifest['source']['native_unit']='cm equivalent water height'
    manifest['source']['measurement_label']='Total water-storage anomaly' if kind=='water' else 'Sea-level mass component'
    keep=[i for i,d in enumerate(manifest['dates']) if d>='2002-04-01']
    manifest['dates']=[manifest['dates'][i] for i in keep]
    for path in directory.glob('*.json.gz'):
        d=json.loads(gzip.decompress(path.read_bytes()));indices=[i for i,date in enumerate(d['dates']) if date>='2002-04-01'];d['source']=manifest['source'];d['unit']='cm w.e.';d['dates']=[d['dates'][i] for i in indices]
        for cell in d['cells']:cell['values']=[cell['values'][i] for i in indices]
        path.write_bytes(gzip.compress(json.dumps(d,separators=(',',':'),allow_nan=False).encode(),compresslevel=6,mtime=0))
    (directory/'manifest.json').write_text(json.dumps(manifest,separators=(',',':')))
for path in (OUT/'lakes').glob('*.json.gz'):
    d=json.loads(gzip.decompress(path.read_bytes()));d['bbox_role']='Display / selection extent around one ground-track observation point; not its physical footprint.'
    for cell in d['cells']:
        cell.pop('bounds',None);cell['geometry']={'type':'Point','coordinates':[cell['lon'],cell['lat']]}
    path.write_bytes(gzip.compress(json.dumps(d,separators=(',',':'),allow_nan=False).encode(),mtime=0))
print('Validated NASA metadata preserved; GRACE water-equivalent units explicit; lake records remain point features.',flush=True)
