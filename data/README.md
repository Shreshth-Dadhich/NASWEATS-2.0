# Scientific assets

These files are the canonical scientific inputs used by the website. Keep their
bytes, source attribution and hashes intact.

| Directory | Contents | Public URL when packaged |
| --- | --- | --- |
| `processed/cache/` | Public starter grids and their raw response records | `/cache/` |
| `processed/nasa/` | NASA ready grids, original responses, lake/GRACE products and metadata | `/data/` |
| `processed/study/` | Supplied processed study tables, browser JSON, archive and manifest | `/studies/arabian-dust/` |
| `figures/arabian-dust/` | Eight supplied PNG figures | `/studies/arabian-dust/figures/` |
| `processed/source_archives/` | Separately contributed source archive from the original repository root | Not automatically published |

`processed/catalog-verification.json` is published as
`/catalog-verification.json`. `processed/power-reference.json` is retained for
independent statistical parity checks, not added to the public asset tree.

`website/scripts/prepare-assets.mjs` assembles the unchanged public paths in the
ignored `website/.generated/public/` tree. Only build output/staging is generated;
scientific values are not invented or altered by this step.

These are processed extracts and source-response records, not a complete
collection of original NASA NetCDF granules. See the study manifest, source
specification and [data dictionary](../documentation/data_dictionary.md) for
actual coverage, units, variable definitions and provenance boundaries.
