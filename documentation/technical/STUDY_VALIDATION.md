> Historical technical reference: paths and validation statements below describe an earlier layout. Use [current setup](../setup.md) and [repository layout](../repository_layout.md) for this edition.

# Arabian Peninsula study validation

Archive SHA-256: `df2595e5970fd1e6f86d77fcdfc3ce779797965a6929a030ee5ca9566620031e`

- Actual archive prefix is frontend_data/, not arabian_earth_trends/. Seven figure names have numeric prefixes; original filenames are preserved.
- Annual precipitation values are sums of monthly totals, displayed as mm/year although source column names end in _MM_MONTH. Other annual variables are arithmetic monthly means, not day-weighted means.
- The specification reports NASA MERRA-2 sources and cos(latitude) × FRLAND weights; raw granules, grid weights, exact product versions and preprocessing code are not supplied, so upstream NASA extraction and the claimed 1,384-cell spatial audit cannot be independently verified from this package.
- Supplied statistical CSVs remain authoritative, with fixed 2000–2025 coverage. Chart-window changes do not recompute these tests.
- Zero p-values are retained as reported numerical precision, not interpreted as proof of zero probability.

## Files

- datasets/annual_trends_land_weighted.csv: 26; SHA-256 78dc280ac795e34c2a53a3691fc9835d4acee443aa9afe36031983ad3320527a
- datasets/correlation_significance.csv: 9; SHA-256 b398f14358af0d28b9a2778307e4d762cdcacb92a507941c0f71c122822d5ecf
- datasets/regional_annual_analysis.csv: 130; SHA-256 27ba0d61e5155678e22f33687696ef25fe44e27dd1ce7f1bbad1fac86e25a100
- datasets/regional_correlation_analysis.csv: 25; SHA-256 fdaff6a80b5a4cc6f6965ce3ed4514195635906512366b4391fa48a013085fbf
- datasets/regional_linear_trends.csv: 45; SHA-256 8cba6cc89b18f2a96c9d74cbeb7a3823a6e271ca3e43a7f779a7822e68718d29
- datasets/regional_mann_kendall_sen.csv: 45; SHA-256 e353e1221842098f5be159fb0da9669cdc26bc483000199c9dd77941b885e99b
- datasets/regional_monthly_analysis.csv: 1560; SHA-256 0f55bbfdf4ced5e736792dedb01689bd902b979314dcee46c4fdd8b35e0bcbc6
- datasets/regional_monthly_averages_land_weighted.csv: 312; SHA-256 fd1dc4fd78c065a550a79c21452a294ee8bafcfd3fcb2ff95eb474db90db87f6
- figures/01_annual_temperature.png: 2970 × 1466; SHA-256 f653671cdcb1529365e430ee437362ff36fad561dbc8095cb57847d77e33fad2
- figures/02_annual_precipitation.png: 2970 × 1466; SHA-256 061b14c07f4bb1956763c471483f1bd8fc4a4f4e02964d88943a1e47a901c868
- figures/03_annual_soil_wetness.png: 2970 × 1466; SHA-256 3bf6bc088f760b7f247c4477332d981ec78a30a3088c42f8d6cffdb18f1da20b
- figures/04_annual_dust.png: 2970 × 2367; SHA-256 6fa7e74be6debb32a7aad207d1bb9d0613330e7d0de450902e1df7849c3a0168
- figures/05_wind_vs_dust.png: 2070 × 1765; SHA-256 be0d828f6d3e1a48b3b7fd5f23175c61ba3d36b0bd99781e6208f1c1967f2d14
- figures/06_soil_wetness_vs_dust.png: 2070 × 1765; SHA-256 d23cb6136ce9c45ecc1843651b8a1508a04ef18e4fca1c5546fe5129794efea0
- figures/07_precipitation_vs_soil_wetness.png: 2070 × 1765; SHA-256 68965c4e8335c70436340a89d1f6a0f6db44cfcb77ae2b43cbabf2e2babd9a0d
- figures/regional_correlation_heatmap.png: 3627 × 1765; SHA-256 ff98bc768959a4c404f8fbe6fec9888846d27c783014a0d38d05c5b59b4d541e

## Checks

{
  "core_coverage": "312 consecutive months, five regional panels, 130 region-years, no missing or duplicate keys; 2000\u20132025.",
  "annual_aggregation": "All nine variables reproduce supplied annual values: monthly sum for precipitation; arithmetic monthly mean otherwise.",
  "statistical_crosscheck": {
    "ols": 2.842170943040401e-14,
    "hamed_rao_p": 0.0,
    "sen_slope": 4.73232564246473e-15,
    "correlation_r": 7.771561172376096e-16
  },
  "fdr": "BH adjusted p-values reproduce all 45 trend tests, 25 regional relationships and 9 study-wide relationships; supplied boolean flags match q < 0.05.",
  "variable_ranges": {
    "TEMP_C": {
      "min": 11.156394844113228,
      "max": 37.92540615615131
    },
    "RH": {
      "min": 9.763713560991754,
      "max": 62.30429722117595
    },
    "WIND_SPEED": {
      "min": 0.7455325067053533,
      "max": 4.4711119652661155
    },
    "GWETROOT": {
      "min": 0.2642705911892936,
      "max": 0.5301977516408735
    },
    "GWETTOP": {
      "min": 0.0467546025258202,
      "max": 0.5128131428134861
    },
    "PRECTOT_MM_MONTH": {
      "min": 1.938474181549855e-05,
      "max": 236.1855194652709
    },
    "PRECTOTCORR_MM_MONTH": {
      "min": 3.551980669439908e-06,
      "max": 200.55900060545696
    },
    "DUST_UG_M3": {
      "min": 68.97075136704832,
      "max": 589.7568109562526
    },
    "FINE_DUST_UG_M3": {
      "min": 16.069205591399445,
      "max": 123.10427745270104
    }
  }
}
