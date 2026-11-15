# Verification fixture

`power-reference.json` is a real, unmodified NASA POWER response retrieved on 2026-11-14 for automated verification. It is not used by the website at runtime, deployed as a static asset, or used as a fallback.

Request: https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M,PRECTOTCORR,RH2M,WS10M,ALLSKY_SFC_SW_DWN&community=RE&longitude=55.27&latitude=25.2&format=JSON&start=2001&end=2024

Provider: NASA Langley Research Center, POWER Project. Monthly and Annual API v2.10.0 (version and sources recorded in the response header).

Citation guidance: https://power.larc.nasa.gov/docs/referencing/

Run `node verify.cjs` to verify numerical reference cases, missing-value behavior, all five source variable roundtrips, complete-year handling, and research archive creation. Test archives are written under the ignored `verification/` directory.
