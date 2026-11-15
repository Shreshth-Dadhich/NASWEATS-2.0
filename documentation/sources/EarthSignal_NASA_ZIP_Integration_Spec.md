# EarthSignal --- NASA ZIP Integration Specification

## Purpose

Integrate the supplied `arabian_earth_trends` ZIP into EarthSignal as a
separate, clearly identified research study. Preserve the existing
public measurement catalogue and its current data pipelines. Do not
merge the ZIP's values into existing measurements merely because their
names look similar.

The ZIP contains processed results from a specific Arabian Peninsula
investigation covering January 2000--December 2025. It is not a
replacement for the existing NASA POWER, MERRA2-GMI, GRACE/GRACE-FO or
lake-level sources.

## 1. Inspect and validate the ZIP

Expected contents:

**Eight CSV datasets** - `regional_monthly_averages_land_weighted.csv` -
`annual_trends_land_weighted.csv` - `regional_monthly_analysis.csv` -
`regional_annual_analysis.csv` - `regional_linear_trends.csv` -
`regional_mann_kendall_sen.csv` - `correlation_significance.csv` -
`regional_correlation_analysis.csv`

**Eight PNG figures** - `annual_temperature.png` -
`annual_precipitation.png` - `annual_soil_wetness.png` -
`annual_dust.png` - `wind_vs_dust.png` - `soil_wetness_vs_dust.png` -
`precipitation_vs_soil_wetness.png` - `regional_correlation_heatmap.png`

Before coding, list and inspect every file. Read actual CSV headers,
data types, units, row counts, missing values, duplicate keys and date
ranges. Verify that every image opens. Do not assume column names beyond
those found in the files. Produce a validation report. If the ZIP
differs from expectations, report the actual contents; never fabricate
or fill missing records.

Expected structural checks from the research pipeline: - 312 monthly
observations, January 2000--December 2025. - Five analytical regions. -
1,560 region-month records where the file contains the full region-month
panel. - 130 region-year records where the file contains five regions
across 26 years. - No missing values in the audited core monthly and
annual datasets.

## 2. Add a separate research-data mode

Add **Research Studies → Arabian Peninsula Dust and Climate Study**.

Keep the existing eleven connected public measurement options and their
workflows unchanged. The ZIP is a pre-processed, fixed-coverage research
dataset, not another globally available live measurement.

Suggested description:

"An independent analysis of NASA MERRA-2 monthly reanalysis data across
five analytical regions of the Arabian Peninsula, January 2000--December
2025. The study examines temperature, humidity, wind, precipitation,
soil wetness and dust-related variables, including regional trends and
statistical associations."

Clearly distinguish: 1. Existing live/on-demand EarthSignal
measurements. 2. This supplied, pre-processed Arabian Peninsula study.

Do not imply global coverage, daily observations, real-time data or
arbitrary-area calculations for this study.

## 3. Variables and definitions

Use exact CSV column names and units:

  ------------------------------------------------------------------------
  Variable                 Meaning                 Unit
  ------------------------ ----------------------- -----------------------
  `TEMP_C`                 2 m air temperature     °C

  `RH`                     Relative humidity       \%
                           derived from            
                           temperature and         
                           dewpoint                

  `WIND_SPEED`             10 m wind-speed         m/s
                           magnitude derived from  
                           U10M and V10M           

  `GWETROOT`               Root-zone soil wetness  dimensionless

  `GWETTOP`                Topsoil wetness         dimensionless

  `PRECTOT_MM_MONTH`       PRECTOT-derived monthly mm/month
                           precipitation total     

  `PRECTOTCORR_MM_MONTH`   PRECTOTCORR-derived     mm/month
                           monthly precipitation   
                           total                   

  `DUST_UG_M3`             Total dust surface mass µg/m³
                           concentration           

  `FINE_DUST_UG_M3`        Fine dust fraction      µg/m³
                           (DUSMASS25)             
  ------------------------------------------------------------------------

Critical distinctions: - PRECTOT and PRECTOTCORR are different
variables; keep them separate. - DUSMASS25 is the fine dust fraction,
not total atmospheric PM2.5. - DUST_UG_M3 is dust surface mass
concentration, not dust optical depth. - RH and WIND_SPEED are derived
variables; disclose this. - Do not equate these variables with similarly
named NASA POWER or MERRA2-GMI fields. Different source collections,
processing and periods mean they are not automatically interchangeable.

## 4. Provenance, processing and geography

Attribute this study to NASA MERRA-2 reanalysis. Source collections: -
`M2TMNXSLV` - `M2TMNXFLX` - `M2TMNXLND` - `M2TMNXAER`

Static land-fraction source: `M2C0NXASM`, field `FRLAND`.

The study uses monthly data from January 2000 to December 2025. Regional
values use land-focused area weights based on cosine latitude multiplied
by land fraction (`FRLAND`). Atmospheric variables originate as grid-box
means; land-fraction weighting creates a land-fraction-weighted regional
estimate, not direct land-only station observations.

Five provisional analytical rectangles: - Northwest: latitude 20--32°,
longitude 34--43°. - North Central: latitude 20--32°, longitude
43--50°. - Northeast: latitude 20--32°, longitude 50--60°. - Southwest:
latitude 12--20°, longitude 34--47°. - Southeast: latitude 12--20°,
longitude 47--60°.

These are analytical subdivisions, not official climate zones or
administrative boundaries. If drawing them on the map, use the exact
bounds and label them "analytical study regions".

The regional coverage audit found 1,384 land-containing cells, zero
uncovered cells and zero overlapping cells. This describes the study's
regional partition, not global coverage.

## 5. Statistical methods and interpretation

Use the supplied statistical CSVs as the authoritative results. Do not
silently recompute or replace them with different methods.

The study includes: - Annual linear regression. - Regional Mann--Kendall
tests with Hamed--Rao autocorrelation modification. - Sen's slope
estimates. - Pearson correlations after removing calendar-month
climatology and linear trend. - Approximate lag-1 autocorrelation
adjustment to effective sample size for correlations. -
Benjamini--Hochberg false-discovery-rate (FDR) correction.

For regional trend claims, use the supplied FDR-adjusted significance
field (`FDR_significant` or its verified equivalent), not unadjusted
p-values alone. For correlation claims, use the supplied FDR-adjusted
results.

Distinguish trend direction, statistical significance and effect size.
Correlation is association, not causation. Describe autocorrelation and
effective-sample-size adjustments as approximate.

## 6. Required study interface

**Overview** - Research question, period, geographic scope and MERRA-2
source. - Key findings drawn from actual results. - State that this is
historical research, not forecasting.

**Regional selector and map** - Five selectable regions and their exact
bounds. - Do not imply arbitrary polygons or coordinate selections are
supported by these pre-aggregated data. - If the global map remains,
visually distinguish the five study regions from globally selectable
areas.

**Trend explorer** - Annual charts for temperature, precipitation, soil
wetness and dust. - Region filtering where supported by the CSVs. -
Correct units, labels, tooltips and source notes. - Keep total/fine dust
and PRECTOT/PRECTOTCORR separate.

**Relationship explorer** - Wind speed versus total/fine dust. -
Root-zone and topsoil wetness versus dust. - Precipitation versus soil
wetness. - Show actual correlation coefficients and FDR-adjusted
significance. - State that correlation does not demonstrate causation.

**Regional evidence** - Regional correlation heatmap. - Trend table with
Mann--Kendall direction, Kendall tau, FDR-adjusted p-value and Sen's
slope. - Explain statistics in plain language. - Never label a result
significant unless the supplied FDR result supports it.

**Figures** Use supplied PNGs as reference or downloadable figures.
Prefer interactive charts recreated from CSVs when the underlying data
supports them. Preserve access to the original figures for comparison.

**Methodology and limitations** Explain MERRA-2 reanalysis,
land-fraction weighting, derived variables and statistical tests.
Monthly averages do not count individual dust storms. The analysis
cannot establish causation.

## 7. Changes required for coherence with existing EarthSignal

1.  **Do not merge dust products.** Existing `pm25_bot` is MERRA2-GMI
    reconstructed bottom-layer PM2.5 (1980--2019). ZIP `DUST_UG_M3` and
    `FINE_DUST_UG_M3` are different MERRA-2 dust variables (2000--2025).
    They are not interchangeable.
2.  **Do not merge dust concentration with `duexttau`.** Dust optical
    depth is unitless column optical information; surface dust
    concentration is mass per volume.
3.  **Do not silently merge temperature records.** ZIP `TEMP_C` and
    existing POWER `T2M` are related concepts but differ in source,
    processing, aggregation and coverage.
4.  **Do not merge precipitation records.** ZIP PRECTOT/PRECTOTCORR are
    monthly totals in mm/month. Existing POWER PRECTOTCORR is a monthly
    mean rate in mm/day. Any conversion or comparison must be explicit
    and validated.
5.  **Do not present regional aggregates as arbitrary-area queries.**
    The ZIP does not contain the original gridded data needed to
    calculate a new user-drawn polygon. Arbitrary geometry support
    requires underlying gridded monthly data or verified cell-level
    extracts.
6.  **Keep the period honest.** This study ends December 2025. Do not
    extend it to 2026 or fill years using another product.
7.  **Keep statistical methods study-specific.** Do not apply generic
    EarthSignal settings or significance badges unless they reproduce
    the supplied methods and thresholds.
8.  **Preserve the existing application.** This is an additional
    research workspace, not a rewrite of the existing catalogue, global
    map, lake selector, GRACE workflow, NASA relay or export pipeline.

## 8. Research export

Add a study-specific export containing the selected region and bounds,
selected variables and period, relevant source CSV rows, statistical
results, collection identifiers, variable definitions,
processing/weighting notes, methods, limitations and relevant figures.

Do not claim the ZIP contains raw NASA granules. It contains processed
regional datasets and figures, not the original NetCDF archive.

## 9. Implementation order and acceptance tests

Implement in this order: 1. Inspect and validate the ZIP. 2. Create a
study data manifest and typed data-loading layer. 3. Add the study
workspace without changing existing sources. 4. Add regional selection,
trend charts and relationship charts. 5. Add statistical evidence,
methodology and limitations. 6. Add study-specific exports. 7. Test all
five regions, nine variables, date ranges, missing-value handling,
units, significance labels and responsive layouts.

Integration is complete only when all expected files are validated,
every displayed value comes from supplied data or a documented
calculation, incompatible products are never silently combined, regional
bounds and the 2000--2025 period are correct, the study is clearly
distinct from live/global measurements, existing features still work,
and exports preserve provenance.

**Priority: scientific coherence and data integrity first; visual polish
second. If the supplied regional aggregates cannot support a feature,
explain the limitation rather than pretending it works.**
