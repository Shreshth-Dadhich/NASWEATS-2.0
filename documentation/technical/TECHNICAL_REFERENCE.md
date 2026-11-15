> Historical technical reference: paths and validation statements below describe an earlier layout. Use [current setup](../setup.md) and [repository layout](../repository_layout.md) for this edition.

# EarthSignal — NASA Earth System Trends

## Current study workspace

The Map tab now provides labeled annual/monthly variable values with playback, full-record annual averages, published OLS slopes, FDR-classified Sen trend maps, and regional correlation maps. All nine variables and every relationship pair remain available. Color scales can be fixed across all years or explicitly rescaled to one frame; correlation uses a fixed [-1, 1] domain. Selected regions show the actual current value, annual/monthly history against the supplied whole-peninsula aggregate, full-record trend or correlation evidence, and links to the corresponding scatterplot. A dedicated map CSV records all five regional values, units, legend bounds, displayed time/aggregation, selected-region flag and available source statistics. Original CSV/PNG files are unchanged.

The interface uses larger spacing and layered 22/88-pixel background grids, with responsive map controls and mobile shortcuts between the map and its selected-region analysis. Timelines update local verified study data without fetching new NASA subsets or resetting the camera.

The supplied Arabian Peninsula study now opens as a full-page workspace at `#study`, with Annual changes, Relationships, Regions, Map, Methodology, Limitations and Sources tabs. The live observatory remains mounted underneath and retains its investigation when switching back. Annual changes offers all nine supplied variables, including both precipitation, soil-wetness and dust variants. Its Compare regions control is available only in annual mode and plots the five regions plus the supplied whole-peninsula aggregate.

Regional evidence includes all 45 original tests, directional FDR verdicts, Sen slopes, Kendall tau, adjusted q, OLS changes and R². Region profiles include the actual 2000/2025 annual endpoints, all nine variables, highlighted comparative time series, a 45-cell trend matrix and correlation evidence. No whole-peninsula MK test is fabricated.

Relationship plots default to figure-matched full-record monthly residuals, with a separate original-CSV view. All nine published whole-peninsula relationships and five published relationships per region retain their supplied test statistics. Every variable is also available through X/Y exploration. Additional pairs and the four unreported relationship tests in each region are descriptive calculations from original monthly values: missing p/q/effective-N/ACF results are labeled Not supplied, not inferred. Mathematical interpretations make no causal claims. Original figures 05–07 remain available unchanged alongside their matching relationships.

Both maps now zoom out beyond the whole peninsula. This necessarily shows surrounding basemap context; numerical selections remain restricted to the Middle East study extent. Whole peninsula and fit-selection controls are distinct. Polygon drawing shows vertex markers, supports Undo/Backspace/Ctrl+Z, Enter/Finish/double-click/first-point closure, and retains an invalid drawing for correction. Polygon-cell overlap weighting remains the scientific calculation; a triangular selection changes results relative to its bounding rectangle. Regions up to 12° × 12° remain the interactive acquisition limit.

Research ZIPs retain the original source files and now add full monthly raw/residual pairs plus normalized six-scope annual comparison CSVs. Source and original-file hashes are unchanged. See STUDY_WORKSPACE_VALIDATION.md for verification. V1 and V2 restore points remain preserved.


A global React observatory with real NASA measurements, drawn study regions, time-series analysis, statistical tests and reproducible research exports. Public data run without an Earthdata account. Exact protected mission products remain distinct optional acquisitions.

## Connected measurements

| Available metric | NASA source | Published record | Units |
| --- | --- | --- | --- |
| 2 m air temperature | POWER / MERRA-2, T2M | 1984–2024 | °C |
| Relative humidity | POWER / MERRA-2, RH2M | 1984–2024 | % |
| Mean 10 m wind speed | POWER / MERRA-2, WS10M | 1984–2024 | m/s |
| Corrected precipitation rate | POWER / MERRA-2, PRECTOTCORR | 1984–2024 | mm/day |
| Reconstructed bottom-layer PM2.5 | MERRA2-GMI, instM_2d_bot_Nx / pm25_bot | 1980–2019 | µg/m³ |
| Dust optical depth, 550 nm | MERRA2-GMI, tavgM_2d_aer_Nx / duexttau | 1980–2019 | unitless |
| Low-cloud fraction | MERRA2-GMI, tavgM_2d_rad_Nx / cldlow | 1980–2019 | fraction |
| Surface skin temperature, land and ocean | MERRA2-GMI, tavgM_2d_rad_Nx / ts | 1980–2019 | °C |
| Total land water-storage anomaly | GSFC GRACE / GRACE-FO OBP RL06v2.0, solution/cmwe | April 2002–June 2026 | cm water equivalent |
| Sea-level mass component | GSFC GRACE / GRACE-FO SLA RL06v2.0, ocean solution/cmwe | April 2002–June 2026 | cm water equivalent |
| Root-zone soil wetness | MERRA2-GMI, tavgM_2d_lnd_Nx / gwetroot | 1980–2019 | dimensionless |
| Topsoil wetness, land masked | MERRA2-GMI, tavgM_2d_lnd_Nx / gwettop | 1980–2019 | dimensionless |
| PRECTOT precipitation rate | MERRA2-GMI, tavgM_2d_flx_Nx / prectot | 1980–2019 | mm/day |
| PRECTOTCORR precipitation rate | MERRA2-GMI, tavgM_2d_flx_Nx / prectotcorr | 1980–2019 | mm/day |
| Lake/reservoir level anomaly | GSFC Global Water Measurements, GWM_HEIGHT_ANOMALY | Feature-specific, some starting 1992 | m |

The public layer contains **340 monitored lake records**, global native GRACE mascon tiles and verified regional extracts. The build warms all twelve geographic presets for the eight POWER/GMI gridded metrics. A same-origin NASA relay acquires new global MERRA2-GMI study regions; POWER requests use its public API directly. Original source URLs, units, processing, metadata and SHA-256 hashes accompany each measurement.

These metrics are deliberately distinguished. GRACE land storage is not groundwater alone or lake level. GRACE ocean mass is not total altimetric sea-surface height and excludes thermal expansion. Surface skin temperature includes land and ocean and does not measure currents; marine studies need offshore selections. Low-cloud fraction is not fog frequency. Monthly dust optical depth is not a storm count. Precipitation is a rate, not a monthly accumulation.

The old aerosol-collection `pm25` field showed suspect archive months in source checks. The application consistently uses the separate `pm25_bot` bottom-layer collection for the entire PM2.5 record, with its own provenance. No individual months are patched from another source. Native kg/m³ values are converted to µg/m³ by multiplying by 10^9.

## Using the observatory

1. Choose a measurement and a geographic preset, or draw a rectangle/polygon. Study areas may span up to 12° per axis, within ±85° latitude. Split dateline crossings.
2. For **Lake water levels**, choose a named monitored water body. The default record is Nasser, Egypt. Its marker represents one satellite observation location; the surrounding display box is not a measurement footprint or regional average.
3. Drag the year handles, choose a season or confidence level, and optionally remove the seasonal cycle. The chart, map and statistics update together. Monthly view shows the source record; inference uses complete annual/seasonal samples.
4. Inspect **Measurement scope & processing** and **View provenance & citation**. Review NASA's record-specific lake advisories.
5. Download a research ZIP containing source grids, monthly and annual/seasonal CSV, statistical results, selection geometry, source manifest, citation and SVG chart. Overpass counts and selected-domain coverage are included where relevant.

The map shows native source cells or monitored points, colored by period mean or fitted change per decade. Esri imagery is attributed visual context only, as authorized by the owner; NASA GIBS relief is available as an alternative. Imagery detail does not increase measurement resolution. POWER/GMI cells are approximately 0.5° × 0.625°; GRACE equal-area mascons are spatially correlated and require basin-scale interpretation.

## Responsiveness and caching

- Trend calculations and polygon reductions run in `analysis.worker.js`, outside the UI thread. Slider changes are coalesced, obsolete calculations are discarded, and exports are disabled until the selected result is complete.
- Leaflet retains one canvas-based quantitative layer and updates its style. It does not destroy/recreate a React component per cell for every slider movement.
- Plotly is loaded separately. The initial JavaScript bundle decreased from about **525 KB to 145 KB compressed** in the validation build; the larger chart code loads afterward.
- Published snapshots are gzip-compressed and loaded by region. The browser does not download the entire global GRACE archive.
- Memory and IndexedDB caches reuse acquired data. Browser caches expire after 30 days; the hosted relay caches fixed-archive NASA responses for 24 hours where the host permits Cache API access; this dispatch host disables that optional edge cache. A manual refresh affects that request, not all future selections.
- POWER requests pad by half a native cell and use bounded 5° tiles. Many 4° presets need one request instead of four. New GMI regions use bounded five-year source batches, with two concurrent client requests.

Cached source changes tested at approximately 0.3–0.5 seconds on this development machine. Cold acquisitions outside cached regions still depend on NASA service latency. The interface reports progress rather than substituting fabricated data.

## Local development

Node 22+ and a modern browser are recommended. From the project root:

```powershell
node scripts/local-nasa.mjs
```

In a second terminal:

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

Open `http://127.0.0.1:4176`. Vite sends `/api` to the local NASA relay on port 8000. Existing source snapshots work without credentials; new global regions need network access to NASA.

For the deployment build:

```powershell
node scripts/build-v7.mjs
```

This produces `dist/client` assets and a Worker ESM entry at `dist/server/index.js`, with the `ASSETS` binding declared in `dist/server/wrangler.json`. The existing Site ID and audience are preserved. The hosted worker relays only allowlisted public NASA subsets; it is not a general-purpose URL proxy.

## Rebuilding NASA snapshots

Python is used for ingestion and independent statistical validation, not for the hosted public runtime:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe backend/build_public_v7.py --grace --power --gmi
.\.venv\Scripts\python.exe backend/build_lakes.py
.\.venv\Scripts\python.exe backend/finalize_public_v7.py
.\.venv\Scripts\python.exe backend/warm_global_v7.py
```

Original large HDF5 files and intermediate downloads are kept in ignored `nasa-source/`. Published snapshots reference the large originals by exact URL and SHA-256 rather than copying 174 MB granules into every researcher download. Cached original POWER/GMI responses and native metadata are retained where indicated in the source manifest. NASA access errors stop acquisition; no other source is silently used.

## Statistics and scientific limits

OLS uses calendar-year spacing and reports slope, fitted net change, Student t statistic/p-value, selected slope confidence interval, fitted-mean confidence band and Sen slope. Mann–Kendall reports S, Kendall tau-b and an exact conditional permutation p-value for up to 100 annual samples, including ties; longer records use an explicitly labeled approximation.

Annual/seasonal aggregation requires all relevant months. December in DJF belongs to the following January year. GRACE mission gaps remain missing. The monthly anomaly climatology is fixed over the full loaded source record. Regional means use polygon-cell intersection weights; at least 80% of the selected source domain must be valid in a month. Masked GRACE means refer only to land or ocean mascons inside the selection. Lake months require at least one actual overpass and export their observation counts; lake records are not spatially averaged across unrelated features.

At least five complete annual/seasonal samples are required for inference. Independence is assumed; no serial-correlation or multiple-testing correction is applied. Source measurement/model uncertainty is not propagated into regression confidence intervals. Statistical significance is not causation. Short or incomplete records can correctly return an inconclusive result.

## Optional exact mission acquisitions

The original MODIS, GPM, AIRS, OMI, GLDAS, Tellus, OSCAR, Jason and SWOT specifications remain in `backend/catalog.json`. Choosing **Requested native mission product** keeps those separate from the public alternatives above. Exact field/version selection, QA decoding and an authenticated Python service are required. OSCAR current vectors and full Jason/SWOT sea-surface height are not claimed as connected public measurements.

An Earthdata account alone does not configure this service. Keep credentials only in the backend environment. Configure `EARTHDATA_USERNAME` / `EARTHDATA_PASSWORD`, verified `NASA_PRODUCT_CONFIG`, `ALLOWED_ORIGINS`, and an HTTPS `apiBase` in `frontend/public/config.json`. Do not place secrets in browser code, public files or Git. Earth Engine additionally requires its own project and authentication. Unsupported decoders or ambiguous fields are rejected.

Run the optional Python service on a separate port, for example:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

## Verification

```powershell
node tests/global_spatial.mjs
node tests/global_export.mjs
node tests/nasa_connections.mjs
node tests/relay_v7.mjs
.\.venv\Scripts\python.exe -m pytest tests -q
```

The suite checks SciPy/browser parity, original NASA response hashes, unit conversions, PM2.5 source choice, native GRACE values/masks/gaps, actual Nasser overpasses, polygon geometry, source compatibility, export contents, small-number precision and the public relay's source allowlist and subset bounds. Native 174 MB-file checks run when those downloaded originals are present. Browser verification also covers rendered results and live downloads.

## Supplied Arabian Peninsula research study

Open **Supplied study** in the observatory to explore the separate supplied 2000–2025 MERRA-2 study in a dialog. The V1 observatory stays mounted, preserving its region, date filters and camera. Old `#research-studies` links return to the global observatory. Related measurement cards link directly to a compatible study variable. This addition leaves the existing global public measurements and their original acquisition/analysis pipelines separate.

The user supplied `frontend_data.zip` and `EarthSignal_NASA_ZIP_Integration_Spec.md`. The import script validates and preserves all eight CSVs and eight PNGs, copies the original archive and document, and creates a hashed manifest, typed loader data and validation report under `frontend/public/studies/arabian-dust`. See `STUDY_VALIDATION.md` for the audit. Original granules, exact source versions and upstream processing code were not supplied; the NASA attribution and cos(latitude) × FRLAND weighting are reported by the accompanying document, not independently revalidated from raw data.

Nine measurements cover temperature, derived relative humidity/wind magnitude, two soil-wetness fields, distinct PRECTOT/PRECTOTCORR precipitation totals and total/fine dust surface mass. Fine dust is not all-species PM2.5; concentration is not AOD. Five exact analytical rectangles are selectable; custom polygons are unsupported by these pre-aggregated records. Original study-wide aggregate series are provided separately, never reconstructed by averaging the five regions.

Annual precipitation columns retain their original `_MM_MONTH` identifiers, but their annual values are verified sums and are labeled **mm/year**. Other annual values are arithmetic monthly means, unlike the original observatory's day-weighted annual analysis.

The Trends year slider filters the chart and map means, while published OLS/MK/Sen/FDR evidence remains explicitly fixed to **2000–2025**. The workspace uses supplied Hamed–Rao modified MK, Sen slopes and BH FDR results. The significance verdict uses the supplied adjusted q < 0.05 flags. Zero p-values retain a source-precision note. No unsupplied confidence intervals are manufactured.

Relationship scatters remove calendar-month climatology and an OLS linear trend over all 312 months. These transforms reproduce all 34 supplied Pearson coefficients. Correlation effective-sample-size adjustments are approximate, and association is not causation. The five-region heatmap preserves the supplied regional FDR results.

Study exports include selected CSV rows, full-period published evidence, selection bounds, manifest, documentation, validation report, all original CSVs/PNGs and the exact original ZIP. SHA-256 checks stop exports when source bytes differ. The original figures remain individually downloadable. No archive is described as raw NASA NetCDF data.

Rebuild and test:

```powershell
.\.venv\Scripts\python.exe backend/import_arabian_study.py
node tests/arabian_study.mjs
```

The import script expects the two original supplied files beside the repository. It performs no NASA network acquisitions. The preserved EarthSignal V1 baseline is documented in AGENTS.md; its tag and external backup are not changed by this addition.

## V1-centered interactive observatory

The observatory remains the primary interface, including for legacy study URLs. It now offers 15 public metrics grouped into 12 measurement buttons. Soil wetness and precipitation have explicit metric selectors. The four new globally queryable fields are NASA NCCS MERRA2-GMI `gwetroot`, land-masked `gwettop`, `prectot` and `prectotcorr`. Their archive is 1980–2019. The Gulf and California new-field subsets are cached; other selected areas use the same bounded NASA OPeNDAP relay. Precipitation is converted by ×86,400 from kg/m²/s to mm/day and remains distinct from the supplied study's mm/month totals. PRECTOT and PRECTOTCORR are identical in the two audited replay presets; no difference is invented.

The new global relationship panel follows the main polygon, years, season, fixed-climatology anomaly setting and optional regional comparison. Users can change the Y measurement, use monthly or complete annual/seasonal pairs, and optionally remove linear trends over paired selected dates. Only matching valid timestamps are paired. The panel shows actual pair count/coverage and descriptive Pearson r, without a significance, FDR or causal claim. Computation uses a separate Web Worker and ignores obsolete results. Paired CSV, selection/method metadata and source grids are downloadable. Source periods, model resolution and spatial domains can differ between axes; overlapping dates do not imply identical sensor footprints.

The supplied study remains accessible in a modal dialog, preserving its original 2000–2025 results, all figures and exports. It does not replace the main V1 controls or reset the current investigation. Its published Hamed–Rao/FDR tables are distinct from the main dynamically recalculated V1 tests and the exploratory global scatterplots.

Global surface-dust concentration fields were tested and rejected because their public archive contained implausible monthly values. They are not connected or substituted with AOD. See GLOBAL_SOURCE_AUDIT.md. Supplied total/fine dust remain restricted to the five supplied study regions; the V1 dust-optical-depth layer remains globally queryable. Global coverage still respects native source domains and V1's 12° study-box / ±85° latitude limits; a monitored lake record cannot be invented outside its catalogue.

Additional verification:

```powershell
.\.venv\Scripts\python.exe backend/build_interactive_global.py
node tests/global_relationship.mjs
.\.venv\Scripts\python.exe -m pytest tests -q
```

## Middle East focus and research guide (2026-11-15)

The current interface restricts selections to the operational Middle East extent, 24–64°E and 12–42°N. This rectangular study extent is not a political boundary. Five regional presets remain, drawn regions are still limited to 12° × 12°, and coordinate/drawing/acquisition guards reject selections outside that extent before data retrieval or cache lookup. Both maps constrain panning and minimum zoom to the extent. The lake menu filters NASA catalogue coordinates and country labels, exposing 32 monitored records in the Middle East instead of the global catalogue. Underlying NASA source responses and native grid-cell values remain unchanged; source cells can straddle a study boundary and their clipped intersections supply the regional weighting.

Limitations is available from the main navigation and the supplied study. The supplied study also has a dedicated Methodology tab explaining reported acquisition, transformations, land weighting, annual aggregation, modified MK, Sen slope, residual Pearson r, approximate effective sample size and the actual BH test families. It distinguishes reported upstream processing from independently validated table consistency. The live observatory continues to use its own dynamically recalculated unadjusted MK test; the study uses fixed 2000–2025 published evidence and FDR-adjusted q-values. No statistical labels or source values have been changed to match a visual reference.

Motion uses IntersectionObserver reveals, scroll-linked decorative orbits and a reading-progress bar, plus modest card hover transitions. Reduced-motion preferences disable these effects. Limits and study tabs preserve investigation state; study tabs support arrow/Home/End keyboard navigation.

Additional verification: `node tests/middle_east.mjs` checks all presets, boundary-crossing rejection before network/cache access, and the regional lake catalogue. The earlier global-engine tests still exercise the reusable low-level acquisition math; global selections are no longer exposed through the current UI. EarthSignal-V1 and EarthSignal-V2 restore points remain preserved.
