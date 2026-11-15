# Repository organization

The approved application's behavior, source data and public download URLs are
preserved while code and research material are grouped by purpose.

| Previous location | Current location |
| --- | --- |
| `frontend/src/` | `website/src/` |
| Frontend icons, fonts and runtime configuration | `website/public/` |
| `worker/` | `website/worker/` |
| Root build/dev/preview scripts | `website/scripts/` |
| Root npm workspace and frontend package | One package under `website/` |
| Root Wrangler configuration | `website/wrangler.jsonc` |
| `backend/main.py` | `website/api/main.py` |
| `backend/stats_engine.py` | `analysis/statistical_analysis/stats_engine.py` |
| Acquisition/catalog/processing Python tools | `analysis/data_processing/` |
| `tests/` | `analysis/validation/` |
| `yo3.py` | `analysis/data_processing/supplied/regional_land_weighting.py` |
| `main_data_analysis_jupyter_export.py` | `analysis/data_processing/supplied/study_notebook_export.py` |
| Public NASA/cache/study assets | `data/processed/` |
| Supplied study PNGs | `data/figures/arabian-dust/` |
| Source specifications and editorial reference | `documentation/sources/` |
| Architecture, audits and earlier technical notes | `documentation/technical/` |

The two contributed analysis scripts are preserved as received. Historical
technical notes refer to earlier layouts and capabilities; use the current root
README and setup/methodology/data-dictionary/limitations pages as entry points.

Builds stage scientific assets without changing `/data/`, `/cache/` or
`/studies/arabian-dust/` URLs. Reports, dependencies, generated assets and build
output are Git-ignored. Run npm commands in `website/`, and Python commands at
the repository root. The optional API Dockerfile uses that root as its context.

A local Git tag, `earthsignal-before-reorganization`, identifies the state before
these moves. The separately preserved Desktop V1, V2 and Final backups remain
outside this repository and were not modified.

## Reorganization checks

- Clean dependency install from `website/package-lock.json`.
- Production build and all ten JavaScript scientific/integration suites.
- All 24 Python validation tests, including browser/Python statistical parity.
- All 1,521 original public-file hashes match staging and production output.
- NASA Worker source is byte-identical; the sole frontend source edit changes
  the catalog import path to its new analysis location.
- Development HTTP checks, production preview and Cloudflare deployment dry run.

The live Cloudflare deployment remains reachable at its existing URL.
