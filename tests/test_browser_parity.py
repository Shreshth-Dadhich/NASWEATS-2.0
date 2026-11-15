import json
from pathlib import Path
import pytest
from backend.stats_engine import analyze

def test_browser_matches_python_nasa_data():
    path=Path('verification/browser-statistics.json')
    assert path.exists(), 'Run node tests/browser_reference.mjs first'
    payload=json.loads(path.read_text())
    for case in payload['results']:
        js=case['result'];py=analyze(payload['records'],2001,2024,case['season'],case['anomaly'],case['confidence'])
        assert js['slope']==pytest.approx(py['slope'],abs=1e-10)
        assert js['ci']==pytest.approx(py['slope_ci'],abs=1e-9)
        assert js['t_p']==pytest.approx(py['t_p'],abs=1e-9)
        assert js['mk']['p']==pytest.approx(py['mann_kendall']['p'],abs=1e-12)
        assert js['mk']['tau']==pytest.approx(py['mann_kendall']['tau'],abs=1e-12)
        assert js['sen_slope']==pytest.approx(py['sen_slope'],abs=1e-10)
        assert len(js['series'])==py['n']
