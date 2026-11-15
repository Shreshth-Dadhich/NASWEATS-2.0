import hashlib,json
from pathlib import Path
import numpy as np
import pytest
import xarray as xr
from fastapi.testclient import TestClient
from website.api.main import app
from analysis.data_processing.nasa_fetcher import _load_grid,validate_geometry,DataUnavailable

def test_all_15_public_caches_equal_original_nasa_responses():
    root=Path('website/.generated/public/cache')
    files=list(root.glob('*.json'));assert len(files)==15
    for path in files:
        cached=json.loads(path.read_text())
        raw=(root/'raw'/path.name).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==cached['source']['raw_sha256']
        original=json.loads(raw)
        indexed={tuple(f['geometry']['coordinates'][:2]):f for f in original['features']}
        assert len(cached['dates'])==492
        assert cached['source_mode']=='public_starter'
        assert cached['unit']==original['parameters'][cached['parameter']]['units']
        for cell in cached['cells']:
            series=indexed[(cell['lon'],cell['lat'])]['properties']['parameter'][cached['parameter']]
            for date,value in zip(cached['dates'],cell['values']):
                raw_value=series.get(date[:4]+date[5:7])
                expected=None if raw_value is None or raw_value==original['header']['fill_value'] else raw_value
                assert value==expected

def test_decode_cf_temperature_without_double_scaling(tmp_path):
    data=xr.Dataset({'T2M':(('time','lat','lon'),np.full((1,2,2),300.))},coords={'time':np.array(['2001-01-01'],dtype='datetime64[ns]'),'lat':[24.,24.5],'lon':[48.,48.625]})
    data.T2M.attrs['units']='K';path=tmp_path/'test.nc';data.to_netcdf(path)
    field,unit=_load_grid(path,{'field':'T2M','unit':'°C','native_unit':'K','offset':-273.15,'scale':1})
    assert float(field.mean())==pytest.approx(26.85)

def test_invalid_unit_refused(tmp_path):
    data=xr.Dataset({'T2M':(('time','lat','lon'),np.ones((1,2,2)))},coords={'time':np.array(['2001-01-01'],dtype='datetime64[ns]'),'lat':[24.,24.5],'lon':[48.,48.625]})
    data.T2M.attrs['units']='bananas';path=tmp_path/'test.nc';data.to_netcdf(path)
    with pytest.raises(DataUnavailable):_load_grid(path,{'field':'T2M','unit':'°C','offset':-273.15})

def test_native_credentials_are_explicitly_required(monkeypatch):
    monkeypatch.delenv('EARTHDATA_USERNAME',raising=False);monkeypatch.delenv('EARTHDATA_PASSWORD',raising=False)
    client=TestClient(app)
    response=client.post('/api/acquire',json={'variable':'temperature','product':'air','geometry':{'type':'Polygon','coordinates':[[[48,24],[52,24],[52,28],[48,28],[48,24]]]},'start':'2001-01-01','end':'2024-12-31'})
    assert response.status_code==503
    assert 'not configured' in response.json()['detail']

def test_global_coordinates_validated():
    assert validate_geometry({'type':'Polygon','coordinates':[[[-123,36],[-121,36],[-121,38],[-123,38],[-123,36]]]}).is_valid
    with pytest.raises(ValueError):validate_geometry({'type':'Polygon','coordinates':[[[200,0],[202,0],[202,2],[200,2],[200,0]]]})
