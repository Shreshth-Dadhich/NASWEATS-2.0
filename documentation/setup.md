# Setup, GitHub and deployment

## Prerequisites

Install Node.js 24 with npm and Git. Python 3.12 is optional and only needed for
the separate Python API, processing tools and Python validation. Use a current
browser. Installation, external basemaps and new NASA requests need internet.

## Clone and run

```sh
git clone https://github.com/Shreshth-Dadhich/NASWEATS-2.0.git
cd NASWEATS-2.0/website
npm ci
npm run dev
```

Open http://127.0.0.1:4176 and keep the terminal running. Ctrl+C stops the app and
its public NASA relay. The relay listens on 8000 during development. For the
Desktop copy, open `EarthSignal by NASWEATS 2.0/website` instead of the clone.

Use the full checkout: the website reads canonical scientific assets from
`../data/`. Copying only `website/` is not sufficient. Avoid opening index.html
directly. All npm commands below run **inside `website/`**.

## Production build and checks

```sh
npm run build
npm test
npm run test:preview
npm run deploy:check
npm start
```

Open http://127.0.0.1:4176 to preview the built application and relay together.
`npm test` prepares assets and runs all ten scientific/integration check suites.
The preview check verifies production HTML, API routing and original data bytes.
The deploy check bundles for Cloudflare without publishing. For Cloudflare's
local emulator, run `npm run preview:cloudflare`.

`npm run assets` combines icons/fonts/configuration from `website/public/` with
the canonical `data/` assets in ignored `website/.generated/public/`. Vite invokes
this preparation during development and builds as well. After changing source
data, regenerate assets and restart development or rebuild. Never hand-edit the
staging tree or commit generated assets, node_modules, credentials or dist.

## Publish changes to GitHub

From the repository root, review and publish your changes:

```sh
git status
git add .
git commit -m "Describe your change"
git push origin main
```

Use GitHub's normal credential-manager or GitHub Desktop sign-in. Do not paste
access tokens or passwords into project files. Check and integrate newer remote
commits before pushing; do not force-push over another contributor's work.

Current repository: https://github.com/Shreshth-Dadhich/NASWEATS-2.0

## Deploy to Cloudflare

The existing project uses **Cloudflare Workers with Static Assets**. The browser
app and public NASA relay share an HTTPS origin. Static-only GitHub Pages hosting
does not run that relay.

From `website/`:

```sh
npx wrangler login
npm run deploy
```

Complete Cloudflare's browser authorization. Wrangler prints the deployed URL.
The configured Worker is `earthsignal-nasweats-2-0`; use another name in your own
configuration if deploying an independent copy. Do not deploy to somebody else's
account or overwrite an unrelated Worker.

The existing deployment is:
https://earthsignal-nasweats-2-0.earthsignal-by-nasweats-2-0.workers.dev

Verify the deployed page, supplied study, map modes, timeline and exports. Visit
`/api/nasa/health` on the same origin to check the relay binding. You can also run:

```sh
npm run verify:deployment
```

That command compares production scientific assets with the local build. Pass a
different HTTPS origin after `--` to verify an independent deployment. Reports
are written to `analysis/validation/reports/`. Live NASA service availability is
separate from deployment success.

Keep `assets.binding: "ASSETS"` and `run_worker_first: ["/api/*"]` in
`website/wrangler.jsonc`. They ensure API calls reach the Worker before SPA
fallback. See [Cloudflare asset routing](https://developers.cloudflare.com/workers/static-assets/binding/).

### GitHub automatic deployment settings

In Cloudflare's Git integration select the full NASWEATS-2.0 repository, main
production branch and **`website` build root**. Use Node 24, build command
`npm ci && npm run build`, and deploy command `npx wrangler deploy`. If the service
already performs `npm ci`, the build command can be `npm run build`. The checkout
must include sibling `data/` files. The Worker name must match wrangler.jsonc.

For a repository-root CI runner, the equivalent commands are
`npm --prefix website ci`, `npm --prefix website run build`, and
`npm --prefix website run deploy` after configuring deployment authentication.
Never place an API token directly in the repository or workflow text.

Official [Workers build configuration](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/).

### Custom domain

Use a domain you own, add and activate its zone in Cloudflare, and preserve
existing mail/other DNS records when updating nameservers. Open the deployed
Worker's **Settings → Domains & Routes → Add → Custom Domain**, enter the hostname
you control and complete the flow. Test the site and API health over HTTPS after
the domain/certificate becomes active. Registering a custom domain is separate
from the free workers.dev subdomain and hosting plan.

Official [custom-domain instructions](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/).

## Optional Python service

From the **repository root**, Windows PowerShell example:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r analysis/requirements.txt
$env:ALLOWED_ORIGINS="http://127.0.0.1:4176,http://localhost:4176"
.\.venv\Scripts\python -m uvicorn website.api.main:app --host 127.0.0.1 --port 8001
```

Documentation is available at http://127.0.0.1:8001/docs . Run it on 8001 to avoid
the development NASA relay's port 8000. Set `apiBase` in
`website/public/config.json` to `http://127.0.0.1:8001` and restart/rebuild the app.

Native acquisition needs real Earthdata credentials **and pinned, verified
product configurations**, configured only in the server environment. The
`website/api/.env.example` file documents variable names; Uvicorn does not load
it automatically with the command above. Earth Engine additionally requires
its own approved project and authentication. Do not put secrets in public JSON.

In production, deploy the Python service separately with HTTPS, set its precise
frontend CORS origin, and configure `apiBase` to that HTTPS service. The Worker
does not run Python. The optional container builds from the repository root:

```sh
docker build -f website/api/Dockerfile -t earthsignal-api .
```

Python validation instructions and the contributed reference scripts' input/path
limitations are documented in [analysis/README.md](../analysis/README.md).

## Troubleshooting

- **npm is missing:** install Node 24 with npm and reopen your terminal.
- **Missing data during build:** clone the full repository and retain `data/`.
- **Wrong working directory:** package.json and wrangler.jsonc now live in
  `website/`; earlier root-level npm commands must be run there.
- **Port occupied:** stop an older preview/dev process; use 8001 for Python.
- **Missing build:** run `npm run build` before `npm start`.
- **API returns HTML:** preserve the Worker-first `/api/*` routing configuration.
- **Unavailable mission variable:** inspect actual product coverage and access;
  do not replace it with fabricated data or another physical quantity.
- **Stale scientific assets:** rerun asset preparation and restart/rebuild.

See [methodology](methodology.md), [data dictionary](data_dictionary.md) and
[limitations](limitations.md) when interpreting results. The rights-reserved
[LICENSE](../LICENSE) covers original work; third-party sources retain their terms.
