# Supplied-study workspace verification

2026-11-15. Source observations and original CSVs/PNGs were not edited.

- `node tests/study_workbench.mjs`: every raw scatter coordinate for all 36 unique variable pairs across 6 scopes matches the original monthly CSVs (312 observations per scope). All 34 supplied residual coefficients reproduce within 1e-12. All nine six-line annual comparisons match the original annual CSVs. All 45 directional verdicts use the supplied FDR flag and Sen direction. Reverse-pair handling preserves Pearson r.
- `node tests/arabian_study.mjs`: original hashes, annual aggregation, supplied methods, statistical scope and checksum-enforced research ZIPs pass.
- Independent ZIP inspection: 156 normalized annual comparison rows across six scopes, consistent 11-column schema, and 312 paired monthly raw/residual rows. Original source files remain included and hash-verified.
- `node tests/polygon_selection.mjs`: a real NASA triangular selection covers approximately half its bounding rectangle, changes monthly means and trend, clips source cells, and rejects self-intersections.
- Existing global spatial/export and Middle East guard tests pass. The original scientific Python suite passes 24 tests. Its local FastAPI test client required running outside the sandbox; no application behavior was changed to accommodate that test environment.
- Browser checks: full-page study with zero dialogs; six distinct comparison traces; monthly mode hides Compare; nine-row regional profiles; supplied and missing-test labels; arbitrary PRECTOTCORR/topsoil exploration; raw CSV mode; map zoom-out after Whole peninsula; visible vertices, undo and keyboard finish; responsive 390px/320px layouts without page overflow. A 25-source-cell polygon changed the live temperature trend from approximately +0.045 to +0.050 degrees C/year.

## Scientific scope

There are 9 published whole-peninsula and 25 published regional correlation tests, not 54 published tests. The regional correlation matrix shows all nine catalogue pairs for five regions, but the 20 missing regional tests are explicitly unreported. Their descriptive r values come from the actual transformed monthly CSVs. Additional X/Y pairs also have no supplied inferential verdict. Reported FDR families and thresholds are never enlarged or replaced silently.

Whole-peninsula raw scatter values use regional_monthly_averages_land_weighted.csv. Regional plots use regional_monthly_analysis.csv. Residuals remove calendar-month climatology then the full-record linear trend, reproducing figure 05 r=0.382, figure 06 r=-0.202 and figure 07 r=0.658 at their printed precision. These are transformed source observations, not invented replacement values. Monthly-pair exports include both original and residual coordinates.

Statistical tables remain fixed to 2000–2025. Time-window controls filter the displayed annual/monthly series; they do not recalculate or mislabel the published tests. Effect-size formatting retains five significant digits and small p/q values use scientific notation; exports preserve original numeric precision. Internal consistency checks do not independently establish upstream NASA extraction, whose raw granules and preprocessing scripts were absent from the supplied package.


## Study atlas and roomier interface

`node tests/study_maps.mjs` verifies all 15,210 regional annual/monthly observations against the original CSVs, all 45 Sen and OLS slopes, derived annual means, annual versus monthly precipitation units, fixed/full-frame legend ranges, 25 reported regional correlation tests and 20 explicitly unreported tests. Missing data remain null rather than zero; incomplete long-term means are not silently filled. Map export rows preserve original values and absent q-values.

Map values use regional_annual_analysis.csv or regional_monthly_analysis.csv. Averages mean the 26 supplied annual values; annual precipitation averages retain mm/year units. OLS values use regional_linear_trends.csv; Sen slopes/classifications use regional_mann_kendall_sen.csv and its FDR flag. Correlations use the previously verified full-record monthly residual transformation, plus the supplied regional correlation statistics where present. Additional pairs receive descriptive r but no invented inferential results. A 2025 Southwest PRECTOT annual value displays 344.78 mm/year; January 2025 displays 7.695 mm/month. Southwest wind has a supplied significant decreasing Sen trend; Southwest topsoil versus dust reproduces r=-0.299354 and q=5.645e-6 at displayed precision.

Browser QA covers all three map modes, annual/monthly switching, timeline playback/pause, source year/month controls, map-region mouse and keyboard selection, missing-test labels, opening a corresponding scatterplot, the map CSV download event, and 390px/320px layouts without page overflow. The map updates five existing paths rather than rebuilding layers on each frame. View selection does not alter the fixed 2000–2025 statistical scope. Broader map context is not presented as measurements outside the five supplied analytical regions.

Direct hash navigation was verified in an already-open document: Observatory → #study/map → #study/regions → #observatory. App and workspace listeners now handle hash/history events; opening a deep link no longer leaves the previous view visible. Scientific selections in the observatory remain mounted and preserved.
