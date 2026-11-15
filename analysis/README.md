# Analysis and validation

Run Python commands from the **repository root** so `analysis` and `website.api`
can be imported. On Windows, install dependencies with:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r analysis/requirements.txt
```

For later `python` commands, activate `.venv` first or invoke its Python
executable explicitly. On Windows, that executable is `.venv\Scripts\python.exe`.
On Linux/macOS, use `.venv/bin/python` after creating a Python 3.12 environment.

- `data_processing/`: NASA acquisition, native-product catalog and preprocessing
  scripts. These are operator tools; some request external data or write outputs.
  Run a selected module explicitly, for example
  `python -m analysis.data_processing.verify_catalog`.
- `statistical_analysis/stats_engine.py`: the optional FastAPI service's Python
  OLS, confidence-interval, seasonal-anomaly and Mann–Kendall engine.
- `validation/`: original JavaScript scientific tests and Python reference/parity
  checks. Validation reports are generated in `validation/reports/` and ignored
  by Git.
- `data_processing/supplied/regional_land_weighting.py`: the original `yo3.py`.
- `data_processing/supplied/study_notebook_export.py`: the original
  `main_data_analysis_jupyter_export.py`.

Both supplied scripts are preserved without changing their contents. They contain
original machine-specific paths and require raw NASA inputs that are not bundled.
The notebook export also includes acquisition and output-writing cells; do not
treat it as a one-command reproducible pipeline for the current processed study.
Review paths, credentials and inputs before adapting those references.

Prepare browser assets and reference outputs before the Python parity tests:

```sh
cd website
npm ci
npm run assets
npm test
cd ..
node analysis/validation/browser_reference.mjs
node analysis/validation/global_relationship_reference.mjs
python -m pytest analysis/validation
```

Optional API:

```sh
python -m uvicorn website.api.main:app --host 127.0.0.1 --port 8001
```

Configure credentials only in the server environment using
`website/api/.env.example` as a variable-name reference. See the setup guide for
pinned product configurations, CORS and `website/public/config.json`.
