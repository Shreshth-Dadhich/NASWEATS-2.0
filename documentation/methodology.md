# Methodology

EarthSignal contains two related workflows with different statistical contracts.
Do not combine their products, time windows or significance labels.

## Interactive observatory

The observatory acquires supported, explicitly identified NASA public products
for a selected Middle East region. It clips source-grid cells to the selected
geometry, weights the included cell areas and excludes missing measurements.
Changing the investigation window, season or anomaly setting recalculates the
interactive result. Source resolution and coverage remain those of the selected
dataset; a detailed basemap does not increase measurement resolution.

The browser engine is in `website/src/analytics.js`; the corresponding optional
Python implementation is in `analysis/statistical_analysis/stats_engine.py`.
Complete annual/seasonal means use day weighting. DJF is labeled by the January
year. Anomalies remove the fixed full-input-record calendar-month climatology.
The analysis includes OLS slope, net fitted change, regression-slope t testing,
confidence intervals/bands, Mann–Kendall evidence and Sen's slope. Exact versus
approximate inference and autocorrelation limitations are labeled by the app.
Inspect the in-app methodology and exported metadata for each result.

## Supplied Arabian Peninsula study

The supplied CSVs describe January 2000–December 2025: 312 months per scope,
five analytical regions, nine variables, 45 regional trend tests, 25 supplied
regional relationship tests and nine whole-study relationship tests.

The accompanying specification attributes extraction to MERRA-2 and regional
weighting to cosine of latitude multiplied by FRLAND. These are supplied
processing claims. Raw input granules and an independently reproducible,
version-pinned execution environment are not bundled.

Annual precipitation is the sum of twelve monthly totals, in mm/year. Other
annual study variables are arithmetic monthly means; they are not the
observatory's day-weighted annual series. PRECTOT and PRECTOTCORR remain distinct.
The whole-peninsula series comes from its supplied aggregate CSV, not an
unweighted average of the five regional series.

Regional trend tables use the supplied annual OLS regression, Hamed–Rao modified
Mann–Kendall tests and Sen's slopes. Significance labels use the supplied
Benjamini–Hochberg FDR-adjusted Mann–Kendall q < 0.05. Slopes determine increase
or decrease. OLS slopes and R² are descriptive comparisons; their supplied
unadjusted p-values are not used as FDR significance verdicts. No whole-study
trend test is invented where one was not supplied.

Reported relationships remove calendar-month climatology and then linear trend
from the full monthly series. Their evidence includes Pearson r, lag-1
autocorrelation, approximate effective sample size, adjusted p and supplied FDR q.
The regional and whole-study relationship tables are separate testing families.
Additional variable pairs can be plotted descriptively; absent supplied p/q
values remain absent.

Study timeline controls change observations displayed on charts/maps; they do
not recalculate published full-record 2000–2025 tests. Variable-value maps show
regional aggregates, trend maps show supplied slopes and FDR classifications,
and correlation maps show paired residual associations.

## Verification and traceability

Original CSV/PNG files and their manifest hashes are kept under `data/processed/`
and `data/figures/`. JavaScript checks and independent Python comparisons live
in `analysis/validation/`. Supplied reference code is in
`analysis/data_processing/supplied/`; it is preserved as contributed and requires
path/input review before execution. Research exports retain source identities,
coverage, processing notes, selections and original supplied files.

Sources: [supplied integration specification](sources/EarthSignal_NASA_ZIP_Integration_Spec.md),
[study manifest](../data/processed/study/manifest.json),
[validation report](../data/processed/study/validation-report.json).
