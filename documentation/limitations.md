# Limitations

- **Reanalysis versus local measurements.** MERRA-2 combines modeling and
  assimilated observations. Its grid values are not direct readings from a
  selected ground station. A small drawn region does not create finer source
  resolution.
- **Monthly means versus individual events.** Monthly dust, wind and cloud
  values cannot by themselves identify or count individual storms or fog events.
- **Different physical quantities.** Fine mineral dust is not total atmospheric
  PM2.5. Relative soil wetness is not groundwater storage or lake level. GRACE
  terrestrial water storage, sea-level mass and altimetric water height are
  different measurements. The app labels the actual available metric.
- **Regional aggregates.** The supplied study contains five fixed analytical
  rectangles. Its regional CSVs cannot support arbitrary subregional polygon
  calculations. Observatory polygons operate on available NASA grids instead.
- **Provenance boundaries.** The supplied study's CSV consistency, statistical
  relationships and file hashes can be checked. Raw NASA granules are absent.
  The two contributed reference scripts contain original machine-specific paths
  and need additional inputs and review before their processing can be rerun.
  Older supplied manifest notes describe the earlier bundle before those scripts
  were added; the reference scripts are now included under `analysis/`.
- **Fixed published evidence.** The study's test tables always describe
  2000–2025, even when the chart window changes. The interactive observatory's
  recalculated inference is a separate workflow.
- **Significance versus effect size.** A statistically significant association
  can be weak. Read slope or Pearson r alongside the test result. Unreported
  regional relationship p/q values are not inferred from another scope.
- **Association versus cause.** Correlation does not establish causation.
  Shared meteorological drivers and model structure can create associations.
- **Autocorrelation and multiple tests.** Time-series dependence affects
  inference. The study uses its supplied modified tests, approximate effective
  sample sizes and FDR adjustment. Interactive tests retain their own documented
  assumptions; significance is not a guarantee about underlying physical causes.
- **Source availability.** Products have different date ranges, units,
  resolutions and access requirements. The public relay is bounded to validated
  MERRA2-GMI subsets within 1980–2019. Native mission products need separately
  verified acquisition configuration and appropriate access. Upstream outages
  do not authorize invented substitutes.
- **Numerical precision.** Source-reported zero p-values preserve the supplied
  numerical precision; they are not interpreted as a mathematical probability
  of exactly zero.

See [methodology](methodology.md), the [data dictionary](data_dictionary.md),
the source panels and the original supplied specification for context.
