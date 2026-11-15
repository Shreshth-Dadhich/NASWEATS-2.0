"""Fetch real NASA POWER regional starters. Never relabel these as native products.
Run from project root. These are explicitly labeled supplemental MERRA-2-derived
public products; they do not replace IMERG, GRACE, MODIS, or native M2TMNXSLV.
"""
import json, hashlib, time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor

REGIONS = {"gulf": [48,24,52,28], "empty": [48,19,52,23], "tigris": [42,32,46,36], "redsea": [36,20,40,24], "nile": [29,29,33,33]}
PARAMETERS = {"temperature": "T2M", "humidity": "RH2M", "wind": "WS10M"}
OUT = Path(__file__).resolve().parents[1]/"frontend/public/cache"

def acquire(task):
    region, variable = task
    destination = OUT/f"{region}-{variable}.json"
    if destination.exists():
        return
    west,south,east,north=REGIONS[region]
    query={"parameters":PARAMETERS[variable],"community":"RE","longitude-min":west,"longitude-max":east,"latitude-min":south,"latitude-max":north,"format":"JSON","start":1984,"end":2024}
    url="https://power.larc.nasa.gov/api/temporal/monthly/regional?"+urlencode(query)
    for attempt in range(3):
        try:
            with urlopen(url,timeout=120) as response: raw=response.read()
            break
        except Exception:
            if attempt==2: raise
            time.sleep(2)
    data=json.loads(raw)
    if not data.get("features"):
        raise ValueError("NASA returned no regional features")
    dates=[f"{y}-{m:02d}-01" for y in range(1984,2025) for m in range(1,13)]
    parameter=PARAMETERS[variable]
    cells=[]
    for feature in data["features"]:
        lon,lat,*_=feature["geometry"]["coordinates"]
        series=feature["properties"]["parameter"][parameter]
        values=[series.get(d[:4]+d[5:7]) for d in dates]
        values=[v if isinstance(v,(int,float)) and v!=data["header"]["fill_value"] else None for v in values]
        cells.append({"lon":lon,"lat":lat,"bounds":[lon-.3125,lat-.25,lon+.3125,lat+.25],"values":values})
    (OUT/"raw").mkdir(parents=True,exist_ok=True)
    raw_path=OUT/"raw"/f"{region}-{variable}.json"
    raw_path.write_bytes(raw)
    result={"schema_version":1,"source_mode":"public_starter","variable":variable,"region":region,"bbox":[west,south,east,north],"dates":dates,"cells":cells,"unit":data["parameters"][parameter]["units"],"parameter":parameter,"source":{"label":"NASA POWER / MERRA-2 regional product","api":data["header"]["api"],"sources":data["header"]["sources"],"time_standard":data["header"]["time_standard"],"requested_url":url,"retrieved_utc":datetime.now(timezone.utc).isoformat(),"raw_sha256":hashlib.sha256(raw).hexdigest(),"raw_url":f"/cache/raw/{region}-{variable}.json","citation_url":"https://power.larc.nasa.gov/docs/referencing/","resolution":"0.5° latitude × 0.625° longitude","not_native_product":"This is a NASA POWER regional extract, not a direct M2TMNXSLV granule. No requested satellite product is silently substituted."}}
    destination.write_text(json.dumps(result,separators=(",",":")),encoding="utf-8")
    print(region,variable,len(cells),"cells",flush=True)

if __name__=="__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(acquire,[(r,v) for r in REGIONS for v in PARAMETERS]))
