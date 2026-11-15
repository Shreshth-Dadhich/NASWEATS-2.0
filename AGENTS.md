# EarthSignal by NASWEATS 2.0

Independent portable edition of the approved EarthSignal Final snapshot.
Preserve scientific data, citations, missing-data semantics and statistical labels.
Run npm ci, npm run build and npm test inside website/.
Deploy using website/wrangler.jsonc; no Codex Sites project identity is required.
Scientific files are canonical in data/; website/.generated/public is disposable
staging assembled by website/scripts/prepare-assets.mjs. Preserve public URLs.
Python imports use analysis.data_processing, analysis.statistical_analysis and
website.api. Run Python commands from the repository root.
Do not modify the separate original earthsignal workspace or V1/V2/Final archives.
Never commit NASA credentials, Earthdata tokens, .env files or installed dependencies.
