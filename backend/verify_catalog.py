"""Public NASA CMR metadata verification; does not claim download authorization."""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from backend.nasa_fetcher import CATALOG,discover

def lookup(name):
    try:return name,{"collections":discover(name)}
    except Exception as e:return name,{"error":str(e)}

if __name__=='__main__':
    names=sorted({p['short_name'] for v in CATALOG for p in v['products']})
    with ThreadPoolExecutor(max_workers=3) as pool:results=dict(pool.map(lookup,names))
    output={'retrieved_utc':datetime.now(timezone.utc).isoformat(),'endpoint':'https://cmr.earthdata.nasa.gov/search/collections.umm_json','meaning':'Exact short-name metadata matches only. No data authorization or variable-field validation is inferred.','products':results}
    dest=Path('frontend/public/catalog-verification.json');dest.write_text(json.dumps(output,indent=2),encoding='utf-8')
    for name,value in results.items():print(name, len(value.get('collections',[])), 'exact CMR matches',flush=True)
