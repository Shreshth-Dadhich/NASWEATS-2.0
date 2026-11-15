# EarthSignal by NASWEATS 2.0

Interactive NASA Earth science investigation and supplied Arabian Peninsula research study. This repository packages the approved **EarthSignal Final** application for independent installation and hosting. The original UI, charts, maps, scientific calculations and bundled measurements are preserved. See `PROJECT_ORIGIN.json` for the source snapshot and archive checksum.

## Start here: run from GitHub

Install **Node.js 24** (including npm) and **Git**. Use a current Chrome, Edge, Firefox or Safari browser. Internet access is needed to install dependencies, load external basemaps and request new NASA data.

Open PowerShell, Terminal or a VS Code terminal:

```powershell
git clone https://github.com/Shreshth-Dadhich/NASWEATS-2.0.git
cd NASWEATS-2.0
npm ci
npm run dev
```

Open **http://127.0.0.1:4176**. Keep the terminal running; press Ctrl+C to stop. The development command starts both Vite and the public NASA relay on port 8000. No Earthdata account is needed for the bundled supplied study, cached extracts or supported public NASA requests.

For the Desktop copy instead, start with:

```powershell
cd "$HOME\Desktop\EarthSignal by NASWEATS 2.0"
npm ci
npm run dev
```

Use the root folder containing this README and `package.json`. Do not open `index.html` directly or install only the frontend workspace. If you downloaded GitHub's ZIP, extract it first and run the same npm commands inside the extracted project root.

## Production build and local preview

```powershell
npm run build
npm start
```

Open http://127.0.0.1:4176. `npm start` serves the built site and NASA relay together. Build again after source or public-data changes. The original Desktop package includes a prebuilt `dist` for convenience; GitHub excludes generated output, so a clone must be built first.

```powershell
npm test
npm run deploy:check
```

The tests cover region selection, polygons, spatial weighting, exports, relationships, NASA relay contracts, supplied-study calculations and map modes. The deployment check builds and bundles the Cloudflare Worker without publishing it. `npm run preview:cloudflare` runs Cloudflare's local emulator after a build. Python tests are separate and optional; see below.

## What the application includes

- A Middle East observatory with interactive region selection, rectangle/polygon drawing, variable choices, time windows, seasonal/anomaly controls, time series, regression confidence bands, statistical evidence and research exports.
- A full-page supplied study with annual changes, regional comparisons, scatterplots, relationship evidence, region profiles, methodology, limitations and source downloads.
- Maps for variable values, annual/monthly history, long-term averages, trends and tested correlations, with clickable regional analysis and explicit missing-data labels.
- Supplied MERRA-2 study data covering **January 2000–December 2025**, five analytical regions and nine fields: air temperature, relative humidity, wind speed, root-zone wetness, topsoil wetness, PRECTOT, PRECTOTCORR, total dust and fine dust.
- Source CSV files, original figures, study metadata and source archives under `frontend/public/studies/arabian-dust/`. These are application assets and must remain in the repository.

The current observatory is constrained to **24–64°E, 12–42°N**. Individual new investigation requests are limited to 12° by 12°. The supplied study's five regions have their own documented bounding boxes; they are analytical subdivisions, not political borders. Historical module names containing “global” do not change the current geographic restriction.

## Data accuracy and availability

Scientific measurements come from NASA sources or the supplied NASA-attributed study extracts. The supplied study's internal CSV consistency and hashes are checked; its upstream NASA extraction and land weights cannot be independently verified without the original granules and preprocessing code, which were not supplied. Esri imagery provides geographical context only. NASA POWER, the public MERRA2-GMI OPeNDAP relay, stored verified extracts, NASA imagery services and optional native mission acquisition have different temporal coverage, resolution and availability. They are not interchangeable datasets. Dataset identifiers, coverage, provenance and caveats are exposed in the application's source panels and exports.

The public MERRA2-GMI relay supports the validated fields in `worker/index.mjs` within its **1980–2019** request contract. It validates source metadata/units and does not invent substitute measurements if NASA is unavailable. New requests can take time when upstream services are slow. Bundled study/caches remain usable independently of those requests. Do not describe fine mineral dust as total air-quality PM2.5, reanalysis as direct station measurements, or monthly means as individual storm counts. Groundwater, sea level and other native mission products require appropriate actual data and configured acquisition; packaging does not fabricate missing coverage.

Trend significance, effect size and association are separate concepts. Supplied study significance uses its supplied FDR-adjusted tests. Additional descriptive relationships lacking supplied adjusted tests must retain that distinction. Relationships do not establish causation. Consult the in-app Methodology and Limitations tabs before interpreting results.

## Project structure and technology

```text
frontend/             React/Vite frontend and public datasets
  src/                JSX/JavaScript UI, map and statistics modules/workers
  public/             Scientific JSON/CSV/gzip extracts, figures and local fonts
backend/              Optional Python FastAPI native-data/statistics service
worker/index.mjs      Public NASA relay and production request handler
scripts/              Portable build, development, preview and test commands
tests/                JavaScript scientific checks and Python tests
docs/                 Additional technical reference and packaging verification
package.json          Root npm workspace commands
package-lock.json     Reproducible npm dependency lockfile
wrangler.jsonc        Independent Cloudflare Worker + static-assets deployment
PROJECT_ORIGIN.json   Approved-final source provenance
dist/                 Generated output; excluded from GitHub
```

Frontend: **JavaScript/JSX, React 19, Vite 6, CSS/Tailwind 4, Leaflet/react-leaflet, leaflet-draw, Turf, Plotly and rc-slider**. Browser Web Workers perform interactive analysis. Backend: **Python, FastAPI, NumPy, pandas, SciPy, pymannkendall, xarray and NASA acquisition libraries**. Hosting relay: **JavaScript on Cloudflare Workers**. This is a React/Vite application; it does not require Next.js or a database.

## Publish source on GitHub

Target public repository: **Shreshth-Dadhich/NASWEATS-2.0**. The repository includes source, scientific assets and the npm lockfile. Dependencies, build output, credentials and local caches stay excluded by `.gitignore`. The nested supplied-study ZIP is intentionally tracked; do not add a blanket `*.zip` ignore rule.

For an existing clone, publish changes with:

```powershell
git status
git add .
git commit -m "Update EarthSignal"
git push origin main
```

Sign in through GitHub's normal Git credential-manager or GitHub Desktop flow if prompted. Do not enter a GitHub account password into Git or put access tokens in source files. Set your own Git author name/email if Git asks for them. The public repository's commit history preserves earlier published states; do not force-push over other contributors' changes.

If starting with an unconnected folder, the simplest route is GitHub Desktop: clone the repository, copy the packaged source into that clone (excluding `node_modules`, `dist` and `.git`), review changes, commit, and push. Keep the repository's existing reference files. Official guide: https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github

## Put the site online using Cloudflare Workers

Use **Workers with Static Assets**, so the frontend and `/api/nasa/*` relay share an HTTPS origin. GitHub Pages alone serves static files and cannot run this NASA relay.

1. Create/sign into your own Cloudflare account.
2. From this project root run:

```powershell
npm ci
npx wrangler login
npm run deploy
```

3. Complete Cloudflare's browser login. Wrangler prints your deployed `https://earthsignal-nasweats-2-0.<your-account-subdomain>.workers.dev` address. Use the actual URL printed by your deployment; the placeholder above is not a live address.
4. Check the home page, open the supplied study, switch map modes and download a CSV. Visit `/api/nasa/health` on that same origin: it should return JSON with `status: "ok"` and an asset binding. Check a supported NASA-backed observatory request as well; upstream availability is separate from deployment success.

The root `wrangler.jsonc` includes the `ASSETS` binding and routes `/api/*` through the Worker before static SPA fallback. Keep both settings. No original Codex Sites project ID or hosting account is required. Do not deploy only `dist/client` when you need the relay.

### Automatically deploy GitHub changes

In Cloudflare's Workers dashboard connect/import **Shreshth-Dadhich/NASWEATS-2.0** using its Git integration. Choose the **main** production branch and repository root directory. Use Node 24, build command **`npm ci && npm run build`** and deploy command **`npx wrangler deploy`**. The Worker name must match `earthsignal-nasweats-2-0` in `wrangler.jsonc`. If the dashboard supplies its own install step, `npm run build` is sufficient as the build command after `npm ci`. Authorize only the intended repository. Subsequent main-branch pushes trigger deployment.

Cloudflare build configuration: https://developers.cloudflare.com/workers/ci-cd/builds/configuration/
Static assets and API routing: https://developers.cloudflare.com/workers/static-assets/binding/

### Connect a real custom domain

1. Register a domain you own, or use an existing one. Domain registration is separate from GitHub and hosting.
2. Add that domain to Cloudflare and finish the nameserver/DNS activation steps at your registrar. Preserve existing mail and other DNS records.
3. Open your deployed Worker, then **Settings → Domains & Routes → Add → Custom Domain**. Enter your chosen hostname, for example `earthsignal.yourdomain.com`. Use a hostname you control; the example is not a reserved or purchased domain.
4. Complete the dashboard flow. Cloudflare configures the corresponding DNS record and certificate for a valid active zone. Wait until HTTPS/certificate status is active, then test the site and `/api/nasa/health` on the new hostname.
5. If desired, add the new URL to this README and your GitHub repository's About/Website field. Recheck any optional Python backend CORS settings against the new origin.

Official custom-domain steps: https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
Usage limits and pricing depend on your Cloudflare account/plan; review them before broad public use.

## Optional Python backend / authenticated NASA products

The public deployment above does not need Python. The included FastAPI service is for advanced native-granule acquisition and Python statistical analysis. Earthdata authentication and explicitly pinned/verified product configurations are required for supported native products; a username alone is not enough. Google Earth Engine additionally requires an approved project and its own authentication.

Windows example, in another terminal:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r backend/requirements.txt
$env:ALLOWED_ORIGINS="http://127.0.0.1:4176,http://localhost:4176"
.\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

API documentation: http://127.0.0.1:8001/docs . Copy only the relevant variable names from `backend/.env.example` into your server environment. Uvicorn does not load that file automatically with the command above. Configure `NASA_PRODUCT_CONFIG` and any `EE_COLLECTIONS` according to `backend/nasa_fetcher.py` and verified collection metadata. Keep passwords/tokens on the server; never put them in frontend JSON, GitHub, screenshots or exports.

Set `apiBase` in `frontend/public/config.json` to `http://127.0.0.1:8001` for this optional local API, then rebuild/restart. For production use an HTTPS Python service, configure `ALLOWED_ORIGINS` to the precise frontend HTTPS origin, and set `apiBase` to that service's HTTPS base URL. The included backend Dockerfile is a starting point for a separate container deployment; it is not executed by Cloudflare Workers. See `backend/requirements.txt` for portable dependencies and the preserved lockfile for the original Python environment record.

Python verification (after installing its dependencies):

```powershell
node tests/browser_reference.mjs
node tests/global_relationship_reference.mjs
.\.venv\Scripts\python -m pytest tests
```

## Troubleshooting

- **npm not recognized:** install Node 24 with npm and reopen the terminal.
- **Port in use:** stop an earlier dev/preview terminal. Default frontend port is 4176; development relay is 8000. Run the optional Python backend on 8001.
- **Missing build:** run `npm run build` before `npm start`.
- **Map/data request failed:** check internet access and the source error displayed by the app. Bundled data are not evidence that a live NASA service is currently available.
- **API returns HTML in production:** use the root Worker configuration with `run_worker_first: ["/api/*"]`; static-only hosting is insufficient.
- **A variable is unavailable:** inspect its actual coverage/source requirements. Do not substitute fabricated values or infer unsupported mission coverage.
- **Cloudflare CLI cannot authenticate:** run `npx wrangler login` in your own terminal. Never commit Cloudflare tokens.

## Attribution and preservation

Keep NASA dataset citations, supplied-study metadata, figure attribution and bundled font licenses with the app. NASA sourcing does not imply NASA endorsement. No new license for the team's original application code is selected by this packaging step. The approved Desktop V1, V2 and Final backups remain separate and unchanged. `docs/TECHNICAL_REFERENCE.md` preserves the earlier technical README for development history; this README is the portable setup/deployment entry point.
