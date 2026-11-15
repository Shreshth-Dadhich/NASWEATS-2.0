> Historical technical reference: paths and validation statements below describe an earlier layout. Use [current setup](../setup.md) and [repository layout](../repository_layout.md) for this edition.

# Portable packaging verification

This edition starts from the preserved EarthSignal Final commit recorded in
PROJECT_ORIGIN.json. Frontend UI/statistical modules and worker/index.mjs are
unchanged. Build, development, preview, deployment, Git configuration and setup
documentation are now independent of the original hosting workspace.

The final ZIP's integration-spec.md did not match its existing manifest checksum.
The original working project's specification was restored only after verifying
that its SHA-256 equals the unchanged manifest's expected value:
6b1e5aaea52f57c9fc0e51c0dfaa07f9baae112ea687c14473a7682babb3f962.
No scientific measurements or published statistical values were changed.
Git attributes preserve public asset bytes across operating systems.

Verified during packaging:
- Independent Vite production build.
- All ten original JavaScript scientific/integration check suites.
- Source checksums, all 36 scatterplot variable pairs in six scopes,
  15,210 annual/monthly map values and all 45 regional trend records.
- Cloudflare Wrangler dry-run bundle with 1,548 static assets and ASSETS binding.
- Standalone production preview: HTML, health endpoint, invalid NASA request
  rejection, private/missing paths and byte-identical JSON/specification/gzip assets.

Repeat checks from the repository root:

```sh
npm ci
npm run build
npm test
node tests/portable_preview.mjs
npm run deploy:check
```

Native authenticated mission acquisition is not enabled or validated by a
packaging build. It requires separately configured credentials and verified
product versions. No new hosting account or domain is created by these checks.
