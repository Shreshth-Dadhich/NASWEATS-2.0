import json,gzip,hashlib,subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scipy.stats import pearsonr
from backend.stats_engine import prepare_series
from backend.build_public_v7 import parse_ascii

ROOT=Path(__file__).resolve().parents[1]
def test_new_global_source_values_and_land_mask():
    for region in ['gulf','california']:
        for variable,collection,field,factor in [('soil_root','tavgM_2d_lnd_Nx','gwetroot',1),('soil_top','tavgM_2d_lnd_Nx','gwettop',1),('precip_gmi','tavgM_2d_flx_Nx','prectot',86400),('precip_corr_gmi','tavgM_2d_flx_Nx','prectotcorr',86400)]:
            d=json.loads(gzip.decompress((ROOT/'frontend/public/data/ready'/f'{region}-{variable}.json.gz').read_bytes()))
            assert len(d['dates'])==480 and d['dates'][0]=='1980-01-01' and d['dates'][-1]=='2019-12-01'
            for start in [1980,2015]:
                f=d['source']['source_files'][(start-1980)//5]
                raw=gzip.decompress((ROOT/'frontend/public'/f['raw_url'].lstrip('/')).read_bytes())
                assert hashlib.sha256(raw).hexdigest()==f['raw_sha256'];native=parse_ascii(raw)
                for cell in d['cells'][::max(1,len(d['cells'])//5)]:
                    y=list(native['lat']).index(cell['lat']);x=list(native['lon']).index(cell['lon'])
                    for m in [0,59]:
                        original=native[field][m,y,x]
                        if variable.startswith('soil'):assert abs(native['gwetroot'][m,y,x])<1e14
                        assert cell['values'][(start-1980)*12+m]==pytest.approx(float(original*factor),rel=1e-12)
            if variable.startswith('soil'):assert all(0<=v<=1 for c in d['cells'] for v in c['values'] if v is not None)
    catalogue=json.loads((ROOT/'backend/catalog.json').read_bytes())
    assert not {'dust_mass','fine_dust'}&{v['id'] for v in catalogue}

def test_global_scatter_matches_independent_scipy_reference():
    payload=json.loads(subprocess.check_output(['node','tests/global_relationship_reference.mjs'],cwd=ROOT,text=True))
    for case in payload['cases']:
        options=case['options'];result=case['result']
        if options['frequency']=='annual':
            def prepared(records):
                rows,_=prepare_series(records,*options['range'],options['season'],options['anomaly'])
                return {r['date']:r['value'] for r in rows}
        else:
            def prepared(records):
                frame=pd.DataFrame(records);frame['date']=pd.to_datetime(frame.date);frame['month']=frame.date.dt.month
                if options['anomaly']:frame['value']-=frame.groupby('month').value.transform('mean')
                months={'ALL':range(1,13),'JJA':[6,7,8],'DJF':[12,1,2]}[options['season']]
                ay=frame.date.dt.year+((frame.month==12)&(options['season']=='DJF')).astype(int)
                frame=frame[frame.month.isin(months)&ay.between(*options['range'])]
                return {r.date.strftime('%Y-%m-%d'):r.value for r in frame.itertuples() if np.isfinite(r.value)}
        a,b=prepared(payload['x']),prepared(payload['y']);dates=sorted(set(a)&set(b));assert len(dates)==result['n']
        x=np.array([a[d] for d in dates]);y=np.array([b[d] for d in dates])
        if options['detrend']:
            t=np.array([int(d[:4])+(int(d[5:7])-.5)/12 for d in dates]) if options['frequency']=='monthly' else np.array([int(d[:4]) for d in dates])
            design=np.column_stack([np.ones(len(t)),t-t.mean()]);x-=design@np.linalg.lstsq(design,x,rcond=None)[0];y-=design@np.linalg.lstsq(design,y,rcond=None)[0]
        assert np.array([p['x'] for p in result['pairs']])==pytest.approx(x,abs=1e-11)
        assert np.array([p['y'] for p in result['pairs']])==pytest.approx(y,abs=1e-11)
        assert result['r']==pytest.approx(pearsonr(x,y).statistic,abs=1e-12)
