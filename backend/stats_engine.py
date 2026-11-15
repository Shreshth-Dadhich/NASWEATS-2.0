"""Time-aware OLS, confidence bands, MK and seasonal anomaly engine.

No missing-value imputation; exact and approximate inference are labeled.
"""
from __future__ import annotations
from collections import Counter
from itertools import permutations
from math import factorial
import numpy as np
import pandas as pd
from scipy import stats
import pymannkendall as mk

SEASONS = {"ALL": list(range(1, 13)), "JJA": [6, 7, 8], "DJF": [12, 1, 2], "MAM": [3, 4, 5], "SON": [9, 10, 11]}

def prepare_series(records, start_year, end_year, season="ALL", anomaly=False):
    """Complete annual/seasonal means, weighted by days; DJF labeled by Jan year.

    Climatology is fixed to the full input record (not the slider window).
    Anomaly mode subtracts each calendar month's full-record mean before averaging.
    """
    if season not in SEASONS or start_year > end_year:
        raise ValueError("Invalid period or season")
    frame = pd.DataFrame(records)
    if frame.empty:
        raise ValueError("No source records")
    frame["date"] = pd.to_datetime(frame["date"], utc=True).dt.tz_convert(None)
    if frame.date.duplicated().any():
        raise ValueError("Duplicate timestamps must be resolved at acquisition")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    # Accept monthly data only: daily products must be aggregated by nasa_fetcher.
    if frame.date.dt.to_period("M").duplicated().any():
        raise ValueError("Expected one observation per month")
    frame["month"] = frame.date.dt.month
    climatology = frame.groupby("month").value.mean()
    if anomaly:
        frame["value"] -= frame.month.map(climatology)
    frame["analysis_year"] = frame.date.dt.year + ((frame.month == 12) & (season == "DJF")).astype(int)
    frame["days"] = frame.date.dt.days_in_month
    frame = frame[frame.month.isin(SEASONS[season]) & frame.analysis_year.between(start_year, end_year)]
    out = []
    for year, group in frame.groupby("analysis_year"):
        good = group[np.isfinite(group.value)]
        if set(good.month) != set(SEASONS[season]):
            continue
        out.append({"date": f"{year}-07-01", "year": int(year), "value": float(np.average(good.value, weights=good.days))})
    return out, {"months": SEASONS[season], "DJF_label": "January year; December is previous year", "climatology": {str(k): float(v) for k, v in climatology.items() if np.isfinite(v)}, "baseline": [str(pd.to_datetime(records[0]["date"]).date()), str(pd.to_datetime(records[-1]["date"]).date())]}

def mann_kendall(values):
    y = np.asarray(values, dtype=float)
    n = len(y)
    s = int(sum(np.sign(y[j] - y[i]) for i in range(n - 1) for j in range(i + 1, n)))
    counts = Counter(y)
    tie_pairs = sum(t * (t - 1) // 2 for t in counts.values())
    tau_a = s / (n * (n - 1) / 2)
    tau_b = s / np.sqrt((n * (n - 1) / 2) * (n * (n - 1) / 2 - tie_pairs)) if tie_pairs < n*(n-1)/2 else 0.
    if len(counts) == 1:
        return {"S": 0, "tau": 0., "tau_a": 0., "p": 1., "p_method": "exact constant-series null", "z": 0.}
    original = mk.original_test(y)
    if len(counts) == n:
        p = float(stats.kendalltau(np.arange(n), y, method="exact").pvalue)
        method = "exact permutation distribution (no ties)"
    elif n <= 100:
        # q-multinomial inversion distribution: [n]_q! / product([tie_count]_q!).
        # Integer polynomial arithmetic gives the exact conditional distribution
        # without enumerating n! permutations. S = unequal_pairs - 2*inversions.
        distribution = [1]
        for size in range(2,n+1):
            next_distribution=[]; window=0
            for k in range(len(distribution)+size-1):
                if k<len(distribution):window+=distribution[k]
                if 0<=k-size<len(distribution):window-=distribution[k-size]
                next_distribution.append(window)
            distribution=next_distribution
        for count in counts.values():
            for size in range(2,count+1):
                quotient=[];window=0
                for k in range(len(distribution)-size+1):
                    value=distribution[k]-window;quotient.append(value)
                    window+=value
                    if k>=size-1:window-=quotient[k-(size-1)]
                distribution=quotient
        unequal=n*(n-1)//2-tie_pairs
        p=sum(count for k,count in enumerate(distribution) if abs(unequal-2*k)>=abs(s))/sum(distribution)
        method="exact conditional multiset inversion distribution (ties)"
    else:
        p = float(original.p)
        method = "tie-corrected normal approximation with continuity correction"
    return {"S": s, "tau": float(tau_b), "tau_a": float(tau_a), "p": p, "p_method": method, "z": float(original.z)}

def analyze(records, start_year, end_year, season="ALL", anomaly=False, confidence=.95):
    if confidence not in (.9, .95, .99):
        raise ValueError("Confidence must be 0.90, 0.95 or 0.99")
    series, transform = prepare_series(records, start_year, end_year, season, anomaly)
    if len(series) < 5:
        return {"available": False, "reason": "At least 5 complete annual/seasonal samples are required", "series": series, "transform": transform}
    x, y = np.array([r["year"] for r in series], float), np.array([r["value"] for r in series], float)
    n, alpha = len(y), 1-confidence
    fit = stats.linregress(x, y)
    slope, se = float(fit.slope), float(fit.stderr)
    t_value = slope/se if se > 0 else None
    t_p = float(2*stats.t.sf(abs(t_value), n-2)) if t_value is not None else (1. if slope == 0 else 0.)
    critical = float(stats.t.ppf(1-alpha/2, n-2))
    prediction = fit.intercept+fit.slope*x
    residual = y-prediction
    sigma = np.sqrt(np.sum(residual**2)/(n-2))
    band = critical*sigma*np.sqrt(1/n+(x-x.mean())**2/np.sum((x-x.mean())**2))
    # Scientific slope uses actual year spacing, including gaps.
    sen = stats.theilslopes(y, x, alpha=confidence)
    mk_result = mann_kendall(y)
    consecutive = np.diff(x) == 1
    r1 = float(np.corrcoef(residual[:-1][consecutive], residual[1:][consecutive])[0,1]) if consecutive.sum() >= 3 and np.std(residual) > 1e-12 else None
    warnings = ["Unadjusted tests assume independent annual/seasonal samples; autocorrelation can inflate significance.", "No correction for multiple comparisons; CI excludes source measurement/model uncertainty."]
    if n < 10:
        warnings.append("Short record: fewer than 10 complete annual/seasonal samples.")
    if r1 is not None and abs(r1) > .3:
        warnings.append("Substantial residual lag-1 correlation; treat unadjusted significance cautiously.")
    return {"available": True, "n": n, "slope": slope, "slope_per_decade": slope*10, "net_change": slope*(end_year-start_year), "net_change_definition": "fitted slope times requested end-year minus start-year; not endpoint observations", "intercept": float(fit.intercept), "slope_stderr": se, "slope_ci": [slope-critical*se, slope+critical*se], "confidence": confidence, "alpha": alpha, "t_stat": t_value, "t_stat_degenerate": se == 0, "t_p": t_p, "r_squared": float(fit.rvalue**2) if np.isfinite(fit.rvalue) else None, "mann_kendall": mk_result, "sen_slope": float(sen.slope), "sen_ci": [float(sen.low_slope), float(sen.high_slope)], "residual_lag1": r1, "series": series, "bands": [{"year": int(year), "fit": float(v), "low": float(v-b), "high": float(v+b)} for year,v,b in zip(x,prediction,band)], "transform": transform, "verdict": ("Rising" if slope > 0 else "Falling")+" trend meets unadjusted MK threshold" if mk_result["p"] < alpha else "Inconclusive at selected confidence; consider a longer record", "warnings": warnings}
