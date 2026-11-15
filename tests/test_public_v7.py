import gzip,hashlib,json,re
from pathlib import Path
import numpy as np
import pytest
from backend.build_public_v7 import parse_ascii

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'frontend/public/data'
def load(path):return json.loads(gzip.decompress(path.read_bytes()))

def test_bottom_layer_pm25_has_exact_source_conversion_and_metadata():
    for region in ['gulf','empty','tigris','redsea','nile']:
        d=load(DATA/'ready'/f'{region}-air_quality.json.gz')
        assert d['parameter']=='pm25_bot'
        assert d['unit']=='µg/m³'
        assert d['source']['short_name']=='instM_2d_bot_Nx'
        assert d['dates'][0]=='1980-01-01' and d['dates'][-1]=='2019-12-01'
        for item in d['source']['source_files']:
            raw=gzip.decompress((ROOT/'frontend/public'/item['raw_url'].lstrip('/')).read_bytes())
            assert hashlib.sha256(raw).hexdigest()==item['raw_sha256']
        june2015=d['dates'].index('2015-06-01')
        assert max(v for c in d['cells'] for v in c['values'] if v is not None)<1000
        if region=='gulf':
            cell=next(c for c in d['cells'] if c['lat']==25 and c['lon']==50)
            # Independently checked at the NASA endpoint, 2015-06, 25 N / 50 E.
            assert cell['values'][june2015]==pytest.approx(2.0544559e-7*1e9,rel=1e-12)

def test_all_ready_metrics_have_consistent_dimensions_and_known_units():
    expected={'temperature':('T2M','C'),'humidity':('RH2M','%'),'wind':('WS10M','m/s'),'precipitation':('PRECTOTCORR','mm/day'),'air_quality':('pm25_bot','µg/m³'),'dust':('duexttau','1'),'cloud':('cldlow','fraction'),'ocean':('ts','°C'),'soil_root':('gwetroot','dimensionless'),'soil_top':('gwettop','dimensionless'),'precip_gmi':('prectot','mm/day'),'precip_corr_gmi':('prectotcorr','mm/day')}
    for path in (DATA/'ready').glob('*.json.gz'):
        d=load(path);assert (d['parameter'],d['unit'])==expected[d['variable']]
        assert d['cells'] and all(len(c['values'])==len(d['dates']) for c in d['cells'])
        assert any(v is not None for c in d['cells'] for v in c['values'])
        assert d['source']['requested_url'].startswith('https://')
        if 'metadata' in d['source']:
            meta=d['source']['metadata'];raw=gzip.decompress((ROOT/'frontend/public'/meta['raw_url'].lstrip('/')).read_bytes())
            assert hashlib.sha256(raw).hexdigest()==meta['raw_sha256']
            field=re.search(r'    '+d['parameter']+r' \{([\s\S]*?)\n    \}',raw.decode())
            assert field and f'String units "{d["source"]["native_unit"]}"' in field.group(1)

def test_global_presets_preserve_nasa_chemistry_values():
    expected={'air_quality':('instM_2d_bot_Nx','pm25_bot',1e9,0),'dust':('tavgM_2d_aer_Nx','duexttau',1,0),'cloud':('tavgM_2d_rad_Nx','cldlow',1,0),'ocean':('tavgM_2d_rad_Nx','ts',1,-273.15)}
    for region in ['amazon','california','alps','japan','australia','cape','arctic']:
        for variable,(collection,field,factor,offset) in expected.items():
            path=DATA/'ready'/f'{region}-{variable}.json.gz'
            if not path.exists():continue # Optional warm-cache assets may not be built locally.
            d=load(path)
            for start in [1980,2015]:
                raw_path=ROOT/'nasa-source/warm'/f'{region}-{collection}-{start}.txt'
                if not raw_path.exists():continue
                raw=raw_path.read_bytes();source=d['source']['source_files'][(start-1980)//5]
                assert hashlib.sha256(raw).hexdigest()==source['raw_sha256']
                native=parse_ascii(raw)
                for c in [d['cells'][0],d['cells'][-1]]:
                    j=list(native['lat']).index(c['lat']);i=list(native['lon']).index(c['lon'])
                    for month in [0,59]:
                        assert c['values'][(start-1980)*12+month]==pytest.approx(float(native[field][month,j,i]*factor+offset),rel=1e-12,abs=1e-12)

def test_grace_snapshot_preserves_native_values_masks_and_missing_months():
    import h5py
    for kind,filename,flag in [('water','grace-obp.h5',80),('sea_level','grace-sla.h5',90)]:
        manifest=json.loads((DATA/'grace'/kind/'manifest.json').read_bytes())
        assert manifest['dates'][0]=='2002-04-01' and manifest['dates'][-1]=='2026-06-01'
        assert len(manifest['tiles'])==len(manifest['keys'])
        native=ROOT/'nasa-source'/filename
        if not native.exists():continue # Native 174 MB files are linked by hash, not bundled.
        assert hashlib.sha256(native.read_bytes()).hexdigest()==manifest['source']['original_file_sha256']
        with h5py.File(native) as f:
            for key in manifest['keys'][::max(1,len(manifest['keys'])//5)]:
                d=load(DATA/'grace'/kind/(key+'.json.gz'));assert d['unit']=='cm w.e.'
                for cell in d['cells'][::max(1,len(d['cells'])//3)]:
                    assert f['mascon/location'][0,cell['id']]==flag
                    assert cell['values'][0]==pytest.approx(float(f['solution/cmwe'][cell['id'],0]))
                    assert cell['values'][-1]==pytest.approx(float(f['solution/cmwe'][cell['id'],-1]))
                    gap=[v for date,v in zip(d['dates'],cell['values']) if '2017-08'<=date[:7]<='2018-05']
                    assert all(v is None for v in gap)

def test_nasser_levels_match_actual_overpasses_and_are_not_a_fake_grid():
    index=json.loads((DATA/'lakes/index.json').read_bytes());assert len(index)==340
    entry=next(x for x in index if x['id']=='lake000331.10d.2')
    d=load(DATA/'lakes'/(entry['id']+'.json.gz'))
    assert d['feature_based'] and d['domain']=='feature' and d['unit']=='m'
    assert d['cells'][0]['geometry']['type']=='Point' and 'bounds' not in d['cells'][0]
    native=ROOT/'nasa-source/gwm'/(entry['id']+'.json')
    if not native.exists():return
    raw=native.read_bytes();assert hashlib.sha256(raw).hexdigest()==d['source']['original_file_sha256']
    source=json.loads(raw);month='2015-06'
    values=[v for t,v in zip(source['coords']['time']['data'],source['data_vars']['GWM_HEIGHT_ANOMALY']['data'][0][0]) if t.startswith(month) and isinstance(v,(int,float))]
    i=d['dates'].index(month+'-01')
    assert d['cells'][0]['values'][i]==pytest.approx(sum(values)/len(values))
    assert d['cells'][0]['observation_counts'][i]==len(values)
