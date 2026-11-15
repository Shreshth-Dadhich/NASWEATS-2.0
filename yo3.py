from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(
    r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends"
)

MONTHLY = ROOT / "data" / "processed" / "monthly"

FRLAND_PATH = (
    ROOT
    / "data"
    / "processed"
    / "MERRA2_101.const_2d_asm_Nx.00000000.nc4"
)

OUTPUT = ROOT / "data" / "processed"

# --------------------------------------------------
# REGIONAL DEFINITIONS
# Boundaries are approximate analytical zones.
# Latitude: degrees North
# Longitude: degrees East
# --------------------------------------------------

REGIONS = {
    "Northwest": {
        "lat_min": 20, "lat_max": 32,
        "lon_min": 34, "lon_max": 43
    },
    "North_Central": {
        "lat_min": 20, "lat_max": 32,
        "lon_min": 43, "lon_max": 50
    },
    "Northeast": {
        "lat_min": 20, "lat_max": 32,
        "lon_min": 50, "lon_max": 60
    },
    "Southwest": {
        "lat_min": 12, "lat_max": 20,
        "lon_min": 34, "lon_max": 47
    },
    "Southeast": {
        "lat_min": 12, "lat_max": 20,
        "lon_min": 47, "lon_max": 60
    }
}

# --------------------------------------------------
# LOAD LAND FRACTION
# --------------------------------------------------

with xr.open_dataset(FRLAND_PATH) as ds_land:
    frland = ds_land["FRLAND"].squeeze(drop=True)
    frland = frland.sel(
        lat=slice(12, 32),
        lon=slice(34, 60)
    ).load()

frland = frland.fillna(0)

# Latitude correction for grid-cell area
latitude_weights = np.cos(
    np.deg2rad(frland.lat)
)

# --------------------------------------------------
# CHECK MONTHLY FILES
# --------------------------------------------------

files = sorted(
    MONTHLY.glob("ArabianPeninsula_*.nc")
)

print("Monthly files found:", len(files))

if len(files) != 312:
    raise ValueError("Expected exactly 312 monthly files.")

# --------------------------------------------------
# HUMIDITY CALCULATION
# --------------------------------------------------

def calculate_rh(temp_k, dewpoint_k):

    temp_c = temp_k - 273.15
    dew_c = dewpoint_k - 273.15

    es_temp = np.exp(
        17.625 * temp_c / (243.04 + temp_c)
    )

    es_dew = np.exp(
        17.625 * dew_c / (243.04 + dew_c)
    )

    return np.clip(
        100 * es_dew / es_temp,
        0,
        100
    )

# --------------------------------------------------
# PROCESS EACH REGION
# --------------------------------------------------

results = []

for region_name, bounds in REGIONS.items():

    print(f"\nPreparing region: {region_name}")

    region_mask = (
        (frland.lat >= bounds["lat_min"])
        & (
             (frland.lat < bounds["lat_max"])
             if bounds["lat_max"] == 20
             else (frland.lat <= bounds["lat_max"])
          )
        & (frland.lon >= bounds["lon_min"])
        & (
              (frland.lon <= bounds["lon_max"])
             if bounds["lon_max"] == 60
             else (frland.lon < bounds["lon_max"])
          )
    ) 

    region_land = frland.where(region_mask, 0)

    weights = latitude_weights * region_land

    land_cells = int(
        ((region_land > 0.05).sum()).values
    )

    total_weight = float(weights.sum().values)

    print("Land-containing grid cells:", land_cells)
    print("Total area weight:", round(total_weight, 3))

    if land_cells == 0 or total_weight == 0:
        raise ValueError(
            f"No usable land cells in {region_name}"
        )

    def weighted_mean(data):

        result = (
            data.squeeze(drop=True)
            .weighted(weights)
            .mean(
                dim=("lat", "lon"),
                skipna=True
            )
        )

        return float(result.values.squeeze())

    # ----------------------------------------------
    # PROCESS ALL 312 MONTHS
    # ----------------------------------------------

    for i, file in enumerate(files, start=1):

        with xr.open_dataset(file) as ds:

            if not np.array_equal(
                ds.lat.values,
                frland.lat.values
            ):
                raise ValueError(
                    f"Latitude mismatch: {file.name}"
                )

            if not np.array_equal(
                ds.lon.values,
                frland.lon.values
            ):
                raise ValueError(
                    f"Longitude mismatch: {file.name}"
                )

            timestamp = pd.Timestamp(
                ds.time.values[0]
            )

            seconds_in_month = (
                timestamp.days_in_month * 86400
            )

            temp = ds["T2M"]
            dew = ds["T2MDEW"]

            wind = np.sqrt(
                ds["U10M"]**2 + ds["V10M"]**2
            )

            rh = calculate_rh(temp, dew)

            row = {
                "region": region_name,
                "yearmonth": timestamp.strftime("%Y%m"),
                "year": timestamp.year,
                "month": timestamp.month,

                "TEMP_C": weighted_mean(
                    temp - 273.15
                ),

                "RH": weighted_mean(rh),

                "WIND_SPEED": weighted_mean(wind),

                "GWETROOT": weighted_mean(
                    ds["GWETROOT"]
                ),

                "GWETTOP": weighted_mean(
                    ds["GWETTOP"]
                ),

                "PRECTOT_MM_MONTH": (
                    weighted_mean(ds["PRECTOT"])
                    * seconds_in_month
                ),

                "PRECTOTCORR_MM_MONTH": (
                    weighted_mean(ds["PRECTOTCORR"])
                    * seconds_in_month
                ),

                "DUST_UG_M3": (
                    weighted_mean(ds["DUSMASS"])
                    * 1e9
                ),

                "FINE_DUST_UG_M3": (
                    weighted_mean(ds["DUSMASS25"])
                    * 1e9
                )
            }

            results.append(row)

        if i % 50 == 0 or i == len(files):
            print(
                f"{region_name}: "
                f"{i}/{len(files)} months processed"
            )

# --------------------------------------------------
# SAVE REGIONAL MONTHLY DATA
# --------------------------------------------------

regional_df = pd.DataFrame(results)

monthly_output = (
    OUTPUT / "regional_monthly_analysis.csv"
)

regional_df.to_csv(
    monthly_output,
    index=False
)

print("\nRegional monthly dataset saved:")
print(monthly_output)

# --------------------------------------------------
# CREATE ANNUAL SUMMARIES
# --------------------------------------------------

annual_results = []

mean_variables = [
    "TEMP_C",
    "RH",
    "WIND_SPEED",
    "GWETROOT",
    "GWETTOP",
    "DUST_UG_M3",
    "FINE_DUST_UG_M3"
]

for region_name, group in regional_df.groupby("region"):

    annual = (
        group.groupby("year")[mean_variables]
        .mean()
        .reset_index()
    )

    precipitation = (
        group.groupby("year")[
            [
                "PRECTOT_MM_MONTH",
                "PRECTOTCORR_MM_MONTH"
            ]
        ]
        .sum()
        .reset_index()
    )

    annual = annual.merge(
        precipitation,
        on="year"
    )

    annual.insert(
        0,
        "region",
        region_name
    )

    annual_results.append(annual)

annual_df = pd.concat(
    annual_results,
    ignore_index=True
)

annual_output = (
    OUTPUT / "regional_annual_analysis.csv"
)

annual_df.to_csv(
    annual_output,
    index=False
)

# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

print("\nREGIONAL DATA VALIDATION")

for region_name, group in regional_df.groupby("region"):

    print(
        region_name,
        "| Months:", len(group),
        "| Years:", group["year"].nunique(),
        "| Missing values:", group.isna().sum().sum()
    )

print("\nRegional analysis complete.")
