> Historical technical reference: paths and validation statements below describe an earlier layout. Use [current setup](../setup.md) and [repository layout](../repository_layout.md) for this edition.

# EarthSignal 7 review

The established Atlas, Midnight and Dune appearances remain. This update prioritizes missing measurements and responsiveness. Names expose the actual NASA quantities. Dust loading, low clouds, sea-level mass, land-and-sea skin temperature, land storage and lake heights are distinguished. Source periods vary by measurement. A monitored lake renders as a point rather than an invented resolution grid.

The analysis worker removes geometry and statistics from the UI thread. Canvas overlays retain geometry between slider changes. Lazy Plotly loading reduced the validation build's initial compressed JavaScript from approximately 525 KB to 145 KB. Browser checks observed cached measurement changes around 0.3–0.5 seconds on the development machine; uncached NASA latency remains variable.

Validation covers SciPy/browser statistics parity, relay allowlists and bounds, exact NASA passthrough, units and hashes, bottom-layer PM2.5 conversion, native GRACE masks/values/gaps, actual lake overpass means/counts, polygons and research exports. See README for commands. Browser checks use the host CUA tools. No separate taste skill headless-browser gate pass is claimed.

Scientific limits accompany measurements and manifests. GMI ends in 2019; no extension is fabricated. Neighboring GRACE mascons are correlated and require broad regional interpretation. Lake coverage is limited to monitored water bodies. Current vectors and full altimetric sea level require further exact product integration.

## V1-centered interactive update

The observatory is again the primary surface, including when entering through older research-study URLs. The supplied study opens in a dialog while the dashboard remains mounted, preserving its filters, polygon and camera. The new global relationship panel adds selectable Y measurements, annual/monthly pairing, optional detrending, two-region traces and paired-data exports without replacing the original line chart or its statistical controls.

Verification includes a newly acquired custom Alpine NASA soil-wetness region, real rectangle and polygon drawing with distinct resulting trends, two-region scatterplots, monthly/detrended pairing, all four new metric variants, mobile widths and dialog state preservation. An actual paired-data ZIP contained 456 selected monthly observations across two regions; independent SciPy coefficients reproduced both exported r values. The full Python suite passed 24 tests, including independent source conversion/masking and correlation checks; JavaScript regressions passed for the original observatory, supplied study, relay, geography and exports.

The public source audit rejected two implausible surface-dust fields rather than publishing distorted trends. Those quantities remain available only in the supplied regional study. Soil wetness and precipitation rates remain explicitly labeled global NASA replay fields with their actual 1980–2019 period and physical units. See GLOBAL_SOURCE_AUDIT.md.

## Editorial research interface (2026-11-15)

Applied the user-supplied EarthSystem Editorial Research UI brief to the existing V1-centered interface. The default Editorial appearance combines navy surfaces, sand accents and cyan measurement traces. Deep Space and light Dune remain selectable. Instrument Serif headings, IBM Plex Sans controls and IBM Plex Mono quantities are self-hosted as licensed Latin WOFF2 subsets (118,424 bytes total); source URLs, hashes and OFL licenses are included under frontend/public/fonts. The orbital mark is native SVG.

The sticky glass header and mobile navigation sheet preserve investigation state. Cards use restrained gradients, borders and a faint technical grid. Charts retain straight observation segments, OLS lines and confidence bands; quantity-specific map ramps replace generic measurement colors. The new Esri dark context map sits alongside high-detail Esri imagery and NASA relief. None is presented as scientific measurement data.

The brief's request for FDR wording is limited to the supplied study: global V1 significance remains explicitly unadjusted Mann–Kendall. Scientific data, source masks, geometry, statistical engines and exports are unchanged. V1 restore points remain intact.

Browser QA checked desktop and 390/320px widths without horizontal overflow, all appearances, basemap switching, time-window updates, both interactive charts, the supplied-study dialog, and mobile navigation to science notes. Font loading was verified in-browser. A chart styling scope error found during QA was corrected before publication.

## Middle East motion and research guide

Implemented scroll reveals, scroll-linked orbital decoration, reading progress and restrained card hover motion with reduced-motion support. Added a main Limitations view and supplied-study Methodology and Limitations tabs, using the supplied screenshots as layout references. Explanations preserve the distinction between unadjusted live MK tests and fixed supplied Hamed–Rao/BH evidence. Reported NASA extraction is clearly distinguished from verified internal consistency.

The observatory now exposes five Middle East sectors, constrained maps, guarded coordinates/polygons/rectangles and 32 eligible NASA lake records. The operational extent is explicitly 24–64°E, 12–42°N, not a political border. Valid tiny rectangular and triangular selections retained real source-cell values and produced updated trends in browser checks. Returning from guides preserves the investigation. Desktop, 390px and 320px checks covered overflow, wrapped study navigation, keyboard tabs, source charts and reduced-width dialogs.


## Expanded study atlas and spacing

Added larger gutters, card padding, control spacing and table rows, plus two-scale background linework across all appearances. The study atlas separates variable values, Sen/FDR trends and residual correlations, with a readable selected-region analysis and labeled map regions. Actual CSV-derived value ramps are separate from categorical FDR styling. Desktop uses a spacious map/analysis split; narrow screens stack the panels and provide direct navigation between them. Source-derived playback keeps legend bounds fixed by default and does not reload basemap tiles or reset the camera. CSV exports capture actual frame metadata and full available evidence; no reference-image numbers are hard-coded.
