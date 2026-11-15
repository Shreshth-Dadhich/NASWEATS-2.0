from itertools import permutations
import math
import numpy as np
import pytest
from scipy import stats
from backend.stats_engine import analyze,mann_kendall,prepare_series

def records(years=20):
    return [{"date":f"{y}-{m:02d}-01","value":float(2*(y-2000)+10)} for y in range(2000,2000+years) for m in range(1,13)]

@pytest.mark.parametrize("values",[[1,1,2,3,4],[1,1,2,2,3],[2,1,3,2,4,1],[1,2,3,4,5]])
def test_exact_mk_against_enumeration(values):
    n=len(values)
    def score(v):return sum(np.sign(v[j]-v[i]) for i in range(n-1) for j in range(i+1,n))
    permutations_=set(permutations(values));s=score(values)
    exact=sum(abs(score(v))>=abs(s) for v in permutations_)/len(permutations_)
    result=mann_kendall(values)
    assert result["p"]==pytest.approx(exact,abs=1e-14)
    assert result["S"]==s

def test_tie_free_exact_matches_scipy():
    y=[4,2,7,1,8,9,3,6,5]
    result=mann_kendall(y)
    assert result["p"]==pytest.approx(stats.kendalltau(range(len(y)),y,method="exact").pvalue)

def test_known_slope_and_full_confidence_levels():
    for c in [.90,.95,.99]:
        result=analyze(records(),2000,2019,confidence=c)
        assert result["slope"]==pytest.approx(2,abs=1e-12)
        assert result["net_change"]==pytest.approx(38)
        assert result["t_p"]<1e-20
        assert result["slope_ci"][0]==pytest.approx(2,abs=1e-12)

def test_constant_no_false_trend():
    r=records()
    for p in r:p["value"]=4
    result=analyze(r,2000,2019)
    assert result["mann_kendall"]["p"]==1
    assert result["t_p"]==1

def test_djf_correct_year_and_completeness():
    series,_=prepare_series(records(),2000,2002,season="DJF")
    assert [p["year"] for p in series]==[2001,2002]
    expected=(10*31+12*31+12*28)/90
    assert series[0]["value"]==pytest.approx(expected)

def test_missing_month_not_interpolated():
    data=records();data=[p for p in data if p["date"]!="2004-07-01"]
    annual,_=prepare_series(data,2000,2019)
    assert len(annual)==19
    assert 2004 not in [p["year"] for p in annual]

def test_anomaly_baseline_does_not_follow_slider():
    data=records()
    a,meta_a=prepare_series(data,2000,2019,anomaly=True)
    b,meta_b=prepare_series(data,2010,2019,anomaly=True)
    assert meta_a["climatology"]==meta_b["climatology"]
    assert a[-1]["value"]==b[-1]["value"]

def test_irregular_years_sen_uses_actual_time():
    data=[p for p in records() if int(p["date"][:4]) not in (2005,2006)]
    result=analyze(data,2000,2019)
    assert result["sen_slope"]==pytest.approx(2)
    assert result["slope"]==pytest.approx(2)
