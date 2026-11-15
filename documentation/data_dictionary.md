# Data dictionary

## Supplied study variables

Source identifiers and units below come from the unchanged supplied manifest. Annual precipitation units differ from monthly units.

| CSV column | Measurement | Monthly unit | Annual unit | NASA-attributed collection |
| --- | --- | --- | --- | --- |
| TEMP_C | Air temperature | Â°C | Â°C | M2TMNXSLV |
| RH | Relative humidity | % | % | M2TMNXSLV |
| WIND_SPEED | Wind speed | m/s | m/s | M2TMNXSLV |
| GWETROOT | Root-zone soil wetness | dimensionless | dimensionless | M2TMNXLND |
| GWETTOP | Topsoil wetness | dimensionless | dimensionless | M2TMNXLND |
| PRECTOT_MM_MONTH | Precipitation Â· PRECTOT | mm/month | mm/year | M2TMNXFLX |
| PRECTOTCORR_MM_MONTH | Corrected precipitation Â· PRECTOTCORR | mm/month | mm/year | M2TMNXFLX |
| DUST_UG_M3 | Total surface dust | Âµg/mÂ³ | Âµg/mÂ³ | M2TMNXAER |
| FINE_DUST_UG_M3 | Fine surface dust | Âµg/mÂ³ | Âµg/mÂ³ | M2TMNXAER |

## Definitions

- **TEMP_C**: Two-meter air temperature, reported in Celsius.
- **RH**: Relative humidity derived from temperature and dewpoint, according to the supplied study documentation.
- **WIND_SPEED**: Ten-meter wind-speed magnitude derived from U10M and V10M, according to the supplied documentation.
- **GWETROOT**: Relative soil wetness in the root zone; not groundwater storage or absolute water depth.
- **GWETTOP**: Surface-layer relative soil wetness; not a water-level measurement.
- **PRECTOT_MM_MONTH**: PRECTOT-derived monthly precipitation total. Annual CSV values sum the twelve monthly totals.
- **PRECTOTCORR_MM_MONTH**: PRECTOTCORR-derived monthly precipitation total, separate from PRECTOT and from POWER mean rates. Annual CSV values are yearly totals.
- **DUST_UG_M3**: Dust surface mass concentration; not optical depth or a count of dust storms.
- **FINE_DUST_UG_M3**: Fine dust mass concentration from DUSMASS25; not total atmospheric PM2.5 across all species.

## Files and locations

- data/processed/study/datasets/: eight original supplied CSV tables.
- data/processed/study/data.json: browser-ready representation checked against those tables.
- data/processed/study/manifest.json: variables, region bounds, coverage and hashes.
- data/processed/study/frontend_data.zip: unchanged archive used by research exports.
- data/figures/arabian-dust/: eight original PNG research figures.
- data/processed/cache/: NASA public starter grids and preserved raw responses.
- data/processed/nasa/: compressed ready grids, source responses, GRACE/lake products and metadata.
- data/processed/source_archives/: the separately contributed repository-root archive, preserved.

## Table keys and statistical columns

yearmonth identifies a monthly YYYYMM observation; year identifies an annual observation. Regional measurement tables use their supplied region field; test tables use Region and Variable or Relationship. Read each original CSV header because capitalization varies by supplied table.

Trend evidence exposes Sen slope per year/decade, Kendall tau, Mann-Kendall z and p, FDR-adjusted p, and OLS change per decade and R-squared. Relationships expose Pearson r, lag-1 autocorrelation, effective sample size, adjusted p and FDR results where supplied. Missing tests are not zero-valued tests.

The observatory catalog is broader than these nine study variables. Its exact product IDs, native units, derivations, access requirements and caveats are defined in nalysis/data_processing/catalog.json, website/src/extraSources.js and the in-app source panels. POWER corrected precipitation is a rate in mm/day, while study precipitation CSVs contain monthly totals in mm/month. Never merge them as one metric.

## Geographic scope

The observatory selection extent is 24-64 degrees E and 12-42 degrees N, with individual requests limited to 12 degrees per axis. The supplied study region bounds are separately defined in its manifest. Analytical regions are not political boundaries.
