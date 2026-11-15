# Global source-quality audit

The added global choices use NASA NCCS MERRA2-GMI monthly grids, not the uploaded 2000–2025 regional averages. NASA metadata and exact subset responses were inspected before connecting fields.

Connected: `gwetroot`, `gwettop` (dimensionless), and `prectot`, `prectotcorr` (native kg/m²/s multiplied by 86,400 to give mm/day). These public records span 1980–2019. The Gulf and California subsets are cached; other bounded global selections use the same NASA relay. Topsoil wetness uses the native `gwetroot` missing-value validity to exclude ocean cells that otherwise report surface wetness 1. This is a model-cell mask, not an invented FRLAND weighting.

The audited PRECTOT and PRECTOTCORR replay records are identical in Gulf and California. Both native identifiers remain separate, and no numerical difference is manufactured. These rates are not the uploaded study's monthly totals or a substitute for a direct authenticated MERRA-2 bias-correction investigation.

Rejected: global `dusmass` and `dusmass25` from `tavgM_2d_aer_Nx`. Audited source maxima were 968,427.7 / 968,087.35 µg/m³ in the Gulf and 452,215.55 / 452,214.74 µg/m³ in California. These implausible monthly surface concentrations would distort trends. They were not capped, patched, silently interpolated, or published as connected global measurements. Original attempted responses remain in ignored `nasa-source/interactive` for audit. The source variable names remain documented in the supplied research study, whose independent regional tables are unchanged.

The existing V1 globally selectable dust-optical-depth field (`duexttau`) and independently checked bottom-layer PM2.5 (`pm25_bot`) are preserved. The supplied study's total/fine dust concentrations remain restricted to its five published regions. Neither is relabeled as another physical quantity.

Reference metadata:
- https://opendap.nccs.nasa.gov/dods/merra2_gmi/tavgM_2d_lnd_Nx.das
- https://opendap.nccs.nasa.gov/dods/merra2_gmi/tavgM_2d_flx_Nx.das
- https://opendap.nccs.nasa.gov/dods/merra2_gmi/tavgM_2d_aer_Nx.das
