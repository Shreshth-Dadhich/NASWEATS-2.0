# EarthSignal — NASWEATS 2.0

An interactive NASA Earth science investigation site and Arabian Peninsula research workspace for NASA Space Apps 2026.

**[Open the live website](https://earthsignal-nasweats-2-0.earthsignal-by-nasweats-2-0.workers.dev)** · [Setup and deployment](documentation/setup.md) · [Methodology](documentation/methodology.md) · [Data dictionary](documentation/data_dictionary.md) · [Limitations](documentation/limitations.md)

## Run locally

Install Node.js 24 with npm and Git, then:

```sh
git clone https://github.com/Shreshth-Dadhich/NASWEATS-2.0.git
cd NASWEATS-2.0/website
npm ci
npm run dev
```

Open **http://127.0.0.1:4176**. This starts the React/Vite app and its public NASA relay. No Earthdata credentials are needed for the supplied study or supported public datasets. The optional native-product Python API has separate configuration requirements.

## Repository layout

```text
EarthSignal/
├── README.md
├── website/                   React application, NASA relay and hosting
│   ├── src/                   UI, maps, charts and browser statistics
│   ├── public/                Icons, fonts and public runtime configuration
│   ├── worker/                Public NASA subset relay
│   ├── api/                   Optional Python FastAPI service
│   ├── scripts/               Build, preview, asset staging and verification
│   ├── package.json
│   ├── package-lock.json
│   └── wrangler.jsonc
├── analysis/
│   ├── data_processing/       Acquisition and preprocessing tools
│   │   └── supplied/          Original contributed analysis scripts
│   ├── statistical_analysis/ Python statistical engine
│   ├── validation/            JavaScript and Python scientific checks
│   └── requirements.txt
├── data/
│   ├── processed/             NASA extracts, supplied CSVs and metadata
│   └── figures/               Original supplied research figures
├── documentation/
│   ├── setup.md
│   ├── methodology.md
│   ├── data_dictionary.md
│   ├── limitations.md
│   ├── sources/               Supplied specifications and design references
│   └── technical/             Architecture, audits and historical notes
└── LICENSE
```

The GitHub repository name remains **NASWEATS-2.0**. `EarthSignal/` above represents its project root. Hidden Git/tool configuration and the agent guidance file support development.

## Build, verify and deploy

Run these commands **inside `website/`**:

```sh
npm run build
npm test
npm run test:preview
npm run deploy:check
npm start
```

`npm start` previews the built app at http://127.0.0.1:4176. To publish to your own Cloudflare account:

```sh
npx wrangler login
npm run deploy
```

For Cloudflare Git integration, set the build root to **`website`**, build command to **`npm ci && npm run build`**, and deploy command to **`npx wrangler deploy`**. The checkout must include the full repository because the website packages scientific assets from `../data/`. See [setup](documentation/setup.md) for custom domains and the optional Python API.

## Scientific data

The supplied study contains 312 monthly observations per scope for 2000–2025, five analytical regions, nine variables, 45 regional trend tests and 34 supplied relationship tests. The observatory supports Middle East investigation sectors within 24–64°E and 12–42°N. Coverage and methods differ between products; see the in-app source panels and [data dictionary](documentation/data_dictionary.md).

`data/` is the canonical home for scientific assets. Development and builds assemble an ignored `website/.generated/public/` directory while preserving existing `/data/`, `/cache/` and `/studies/arabian-dust/` URLs. CSVs, figures, provenance hashes and source archives retain their original bytes. Do not hand-edit generated assets or create substitute measurements.

## Rights and attribution

The contributors' original code and documentation are **all rights reserved**, as recorded in [LICENSE](LICENSE). NASA data, supplied third-party material, dependencies, basemap imagery and fonts retain their own terms and attribution. Keep their citations and licenses. NASA sourcing does not imply endorsement.

The approved Desktop V1, V2 and Final archives are preserved separately. [Source provenance](documentation/PROJECT_ORIGIN.json) identifies the original approved application snapshot.
