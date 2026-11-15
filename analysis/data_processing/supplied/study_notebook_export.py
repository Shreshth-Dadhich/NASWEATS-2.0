# %%
#wowowowowowoo python analysis by Marwan Khaled for Shreshth's website

import earthaccess
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("All libraries imported successfully!")

# %%
from dotenv import load_dotenv
import os

load_dotenv("yo2.env", override=True)

print("Token available:", bool(os.getenv("EARTHDATA_TOKEN")))

# %%
import earthaccess

auth = earthaccess.login(strategy="environment")

print("Authenticated:", auth.authenticated)

# %%
results = earthaccess.search_data(
    short_name="M2TMNXSLV",
    temporal=("2020-01-01", "2020-12-31")
)

print("Files found:", len(results))

# %%
from pathlib import Path

download_dir = Path("data/merra2_test")
download_dir.mkdir(parents=True, exist_ok=True)

files = earthaccess.download(
    results[:1],
    local_path=str(download_dir)
)

print("Downloaded files:", len(files))
print(files)

# %%
import xarray as xr

file_path = files[0]

ds = xr.open_dataset(file_path, engine="netcdf4")

print(ds)

# %%
for variable in ds.data_vars:
    print(
        variable,
        "| Units:", ds[variable].attrs.get("units", "Unknown"),
        "| Description:", ds[variable].attrs.get("long_name", "Unknown")
    )

# %%
target_variables = [
    "T2M",
    "T10M",
    "T2MDEW",
    "T2MWET",
    "U10M",
    "V10M",
    "PRECTOT",
    "PS",
    "SLP"
]

for var in target_variables:
    if var in ds:
        print(
            f"{var}: AVAILABLE | "
            f"{ds[var].attrs.get('units', 'Unknown')}"
        )
    else:
        print(f"{var}: NOT IN THIS COLLECTION")

# %%
arabia = ds.sel(
    lat=slice(12, 32),
    lon=slice(34, 60)
)

print(arabia)

# %%
temperature = arabia["T2M"]

mean_temp_kelvin = float(temperature.mean())
mean_temp_celsius = mean_temp_kelvin - 273.15

print("Regional mean temperature:")
print(round(mean_temp_celsius, 2), "°C")

# %%
import matplotlib.pyplot as plt

arabia["T2M"].isel(time=0).plot(
    cmap="inferno",
    cbar_kwargs={"label": "Temperature (K)"}
)

plt.title("Arabian Peninsula - January 2020")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

# %%
print("Regional dimensions:", arabia.sizes)
print("Temperature range:",
      float(arabia["T2M"].min()),
      "to",
      float(arabia["T2M"].max()), "K")

print("Regional mean:", mean_temp_celsius, "°C")

# %%
import numpy as np

arabia["WIND10M"] = np.sqrt(
    arabia["U10M"]**2 + arabia["V10M"]**2
)

mean_wind = float(arabia["WIND10M"].mean())

print("Mean 10m wind speed:", round(mean_wind, 2), "m/s")

# %%
import numpy as np

weights = np.cos(np.deg2rad(arabia.lat))

weighted_temp = arabia["T2M"].weighted(weights).mean(
    dim=("lat", "lon")
)

weighted_wind = arabia["WIND10M"].weighted(weights).mean(
    dim=("lat", "lon")
)

print("Weighted temperature:",
      round(float(weighted_temp.item()) - 273.15, 2), "°C")

print("Weighted wind speed:",
      round(float(weighted_wind.item()), 2), "m/s")

# %%
print("Time:", ds.time.values)
print("Latitude:", float(ds.lat.min()), "to", float(ds.lat.max()))
print("Longitude:", float(ds.lon.min()), "to", float(ds.lon.max()))
print("Dataset size:", ds.nbytes / (1024**2), "MB")

# %%
from pathlib import Path

BASE = Path("arabian_earth_trends")

RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

print("Project folders created.")
print("Raw data:", RAW)
print("Processed data:", PROCESSED)

# %%
START_YEAR = 2000
END_YEAR = 2025

MONTHS = [1, 7]

LAT_MIN, LAT_MAX = 12, 32
LON_MIN, LON_MAX = 34, 60

print("Period:", START_YEAR, "-", END_YEAR)
print("Months:", MONTHS)
print("Region:", LAT_MIN, "-", LAT_MAX, "N")
print("Region:", LON_MIN, "-", LON_MAX, "E")

# %%
import earthaccess

results = earthaccess.search_data(
    short_name="M2TMNXSLV",
    temporal=("2000-01-01", "2025-07-31")
)

print("Total granules found:", len(results))

# %%
selected = []

for granule in results:
    filename = granule["umm"]["RelatedUrls"][0]["URL"]
    if any(
        f".{year}{month:02d}.nc4" in filename
        for year in range(START_YEAR, END_YEAR + 1)
        for month in MONTHS
    ):
        selected.append(granule)

print("Selected granules:", len(selected))

# %%
import earthaccess

downloaded_files = earthaccess.download(
    selected,
    local_path=str(RAW)
)

print("Downloaded:", len(downloaded_files))

# %%
import earthaccess

collections = [
    "M2TMNXSLV",
    "M2TMNXFLX",
    "M2TMNXLND",
    "M2TMNXAER"
]

all_results = {}

for collection in collections:

    results = earthaccess.search_data(
        short_name=collection,
        temporal=("2000-01-01", "2025-12-31")
    )

    all_results[collection] = results

    print(collection, ":", len(results), "granules")

# %%
for collection, granules in all_results.items():
    print(f"\n{collection}: {len(granules)}")

    for g in granules[:3]:
        print(g["umm"]["RelatedUrls"][0]["URL"])

# %%
from pathlib import Path
import earthaccess

# RAW is your existing raw-data directory
RAW.mkdir(parents=True, exist_ok=True)

total_downloaded = 0

for collection, granules in all_results.items():

    output_dir = RAW / collection
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nDownloading {collection}")
    print(f"Granules to download: {len(granules)}")

    downloaded = earthaccess.download(
        granules,
        local_path=str(output_dir)
    )

# %%
from pathlib import Path

for collection in all_results:
    folder = RAW / collection
    files = list(folder.glob("*.nc4"))

    print(f"\n{collection}")
    print(f"Expected: 312")
    print(f"Found: {len(files)}")
    print(f"Complete: {len(files) == 312}")

# %%
import xarray as xr
from pathlib import Path

for collection in all_results:

    folder = RAW / collection
    sample_file = sorted(folder.glob("*.nc4"))[0]

    print("\n" + "=" * 65)
    print(f"COLLECTION: {collection}")
    print(f"SAMPLE: {sample_file.name}")
    print("=" * 65)

    with xr.open_dataset(sample_file, engine="netcdf4") as ds:

        print("Dimensions:", dict(ds.sizes))

        for variable in ds.data_vars:
            attrs = ds[variable].attrs

            description = attrs.get(
                "long_name",
                attrs.get("standard_name", "No description")
            )

            units = attrs.get("units", "Unknown units")

            print(f"{variable:20} | {units:15} | {description}")

# %%
LAT_MIN, LAT_MAX = 12, 32
LON_MIN, LON_MAX = 34, 60

# %%
from pathlib import Path
import calendar
import numpy as np
import pandas as pd
import xarray as xr

# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends")

RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed" / "monthly"

OUTPUT.mkdir(parents=True, exist_ok=True)

LAT_MIN, LAT_MAX = 12, 32
LON_MIN, LON_MAX = 34, 60

START_YEAR = 2000
END_YEAR = 2020

COLLECTIONS = {
    "SLV": "M2TMNXSLV",
    "FLX": "M2TMNXFLX",
    "LND": "M2TMNXLND",
    "AER": "M2TMNXAER"
}

# Variables needed from each collection
VARIABLES = {
    "SLV": [
        "T2M", "T2MDEW", "U10M", "V10M"
    ],
    "FLX": [
        "PRECTOT", "PRECTOTCORR", "EVAP"
    ],
    "LND": [
        "GWETROOT", "GWETTOP"
    ],
    "AER": [
        "DUSMASS", "DUSMASS25"
    ]
}


# ============================================================
# FIND MONTHLY FILE
# ============================================================

def find_monthly_file(collection, yearmonth):

    folder = RAW / collection

    matches = [
        f for f in folder.rglob("*")
        if f.is_file()
        and yearmonth in f.name
        and f.suffix.lower() in [".nc4", ".nc"]
    ]

    if len(matches) != 1:
        raise FileNotFoundError(
            f"{collection} {yearmonth}: "
            f"Expected 1 file, found {len(matches)}"
        )

    return matches[0]


# ============================================================
# PROCESS ONE MONTH
# ============================================================

def process_month(year, month):

    yearmonth = f"{year}{month:02d}"

    print(f"Processing {yearmonth}...")

    datasets = []

    # Open each collection and crop it immediately
    for short_name, collection in COLLECTIONS.items():

        filepath = find_monthly_file(collection, yearmonth)

        ds = xr.open_dataset(filepath)

        # Check coordinates
        if "lat" not in ds.coords or "lon" not in ds.coords:
            ds.close()
            raise ValueError(
                f"Missing lat/lon coordinates in {filepath}"
            )

        # Select only required variables
        available = [
            v for v in VARIABLES[short_name]
            if v in ds.data_vars
        ]

        missing = [
            v for v in VARIABLES[short_name]
            if v not in ds.data_vars
        ]

        if missing:
            ds.close()
            raise ValueError(
                f"Missing variables in {collection}: {missing}"
            )

        ds = ds[available]

        # Crop to Arabian Peninsula
        selected_lat = ds.lat[
            (ds.lat >= LAT_MIN) & (ds.lat <= LAT_MAX)
        ]

        selected_lon = ds.lon[
            (ds.lon >= LON_MIN) & (ds.lon <= LON_MAX)
        ]

        ds = ds.sel(lat=selected_lat, lon=selected_lon)

        # Load cropped data into memory, then close source file
        ds.load()
        ds.close()

        datasets.append(ds)

    # Combine the four collections
    data = xr.merge(
        datasets,
        compat="no_conflicts",
        join="exact"
    )

    # ========================================================
    # DERIVED VARIABLES
    # ========================================================

    # Temperature: Kelvin to Celsius
    data["TEMP_C"] = data["T2M"] - 273.15
    data["TEMP_C"].attrs["units"] = "degC"

    # Relative humidity from temperature and dew point
    # Magnus approximation
    temperature = data["TEMP_C"]
    dewpoint = data["T2MDEW"] - 273.15

    def saturation_vapour_pressure(temp):
        return 6.112 * np.exp(
            (17.67 * temp) / (temp + 243.5)
        )

    rh = (
        100
        * saturation_vapour_pressure(dewpoint)
        / saturation_vapour_pressure(temperature)
    )

    data["RH"] = rh.clip(0, 100)
    data["RH"].attrs["units"] = "%"

    # Wind speed from U and V components
    data["WIND_SPEED"] = np.sqrt(
        data["U10M"]**2 + data["V10M"]**2
    )
    data["WIND_SPEED"].attrs["units"] = "m/s"

    # Precipitation: monthly mean flux to monthly accumulation
    seconds_in_month = (
        calendar.monthrange(year, month)[1] * 86400
    )

    for variable in ["PRECTOT", "PRECTOTCORR"]:

        if variable in data:
            output_name = variable + "_MM_MONTH"

            data[output_name] = (
                data[variable] * seconds_in_month
            )

            data[output_name].attrs["units"] = "mm/month"

    # Dust concentration: kg/m3 to micrograms/m3
    data["DUST_UG_M3"] = data["DUSMASS"] * 1e9
    data["DUST_UG_M3"].attrs["units"] = "ug/m3"

    data["FINE_DUST_UG_M3"] = data["DUSMASS25"] * 1e9
    data["FINE_DUST_UG_M3"].attrs["units"] = "ug/m3"

    # ========================================================
    # SAVE REGIONAL GRID
    # ========================================================

    output_file = OUTPUT / f"ArabianPeninsula_{yearmonth}.nc"

    data.to_netcdf(
        output_file,
        engine="netcdf4"
    )

    # ========================================================
    # CALCULATE AREA-WEIGHTED REGIONAL AVERAGES
    # ========================================================

    # Grid-cell area is approximately proportional to cos(latitude)
    weights = np.cos(np.deg2rad(data.lat))

    summary = {
        "year": year,
        "month": month,
        "yearmonth": yearmonth
    }

    summary_variables = [
        "TEMP_C",
        "RH",
        "WIND_SPEED",
        "GWETROOT",
        "GWETTOP",
        "PRECTOT_MM_MONTH",
        "PRECTOTCORR_MM_MONTH",
        "DUST_UG_M3",
        "FINE_DUST_UG_M3"
    ]

    for variable in summary_variables:

        if variable not in data:
            continue

        average = data[variable].weighted(weights).mean(
            dim=("lat", "lon"),
            skipna=True
        )

        summary[variable] = float(average.values.squeeze())

    data.close()

    return summary


# ============================================================
# MAIN LOOP: JANUARY 2000 TO DECEMBER 2025
# ============================================================

results = []

for year in range(START_YEAR, END_YEAR + 1):

    for month in range(1, 13):

        result = process_month(year, month)
        results.append(result)

        print(f"Finished {result['yearmonth']}")

# Save regional averages
df = pd.DataFrame(results)

csv_file = ROOT / "processed" / "regional_monthly_averages.csv"

csv_file.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(csv_file, index=False)

print("\n================================")
print("PROCESSING COMPLETE")
print("Months processed:", len(df))
print("Regional grids:", OUTPUT)
print("Regional averages:", csv_file)
print("================================")

# %%
from pathlib import Path
import calendar
import numpy as np
import pandas as pd
import xarray as xr

# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends")

RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed" / "monthly"

OUTPUT.mkdir(parents=True, exist_ok=True)

LAT_MIN, LAT_MAX = 12, 32
LON_MIN, LON_MAX = 34, 60

START_YEAR = 2021
END_YEAR = 2025

COLLECTIONS = {
    "SLV": "M2TMNXSLV",
    "FLX": "M2TMNXFLX",
    "LND": "M2TMNXLND",
    "AER": "M2TMNXAER"
}

# Variables needed from each collection
VARIABLES = {
    "SLV": [
        "T2M", "T2MDEW", "U10M", "V10M"
    ],
    "FLX": [
        "PRECTOT", "PRECTOTCORR", "EVAP"
    ],
    "LND": [
        "GWETROOT", "GWETTOP"
    ],
    "AER": [
        "DUSMASS", "DUSMASS25"
    ]
}


# ============================================================
# FIND MONTHLY FILE
# ============================================================

def find_monthly_file(collection, yearmonth):

    folder = RAW / collection

    matches = [
        f for f in folder.rglob("*")
        if f.is_file()
        and yearmonth in f.name
        and f.suffix.lower() in [".nc4", ".nc"]
    ]

    if len(matches) != 1:
        raise FileNotFoundError(
            f"{collection} {yearmonth}: "
            f"Expected 1 file, found {len(matches)}"
        )

    return matches[0]


# ============================================================
# PROCESS ONE MONTH
# ============================================================

def process_month(year, month):

    yearmonth = f"{year}{month:02d}"

    print(f"Processing {yearmonth}...")

    datasets = []

    # Open each collection and crop it immediately
    for short_name, collection in COLLECTIONS.items():

        filepath = find_monthly_file(collection, yearmonth)

        ds = xr.open_dataset(filepath)

        # Check coordinates
        if "lat" not in ds.coords or "lon" not in ds.coords:
            ds.close()
            raise ValueError(
                f"Missing lat/lon coordinates in {filepath}"
            )

        # Select only required variables
        available = [
            v for v in VARIABLES[short_name]
            if v in ds.data_vars
        ]

        missing = [
            v for v in VARIABLES[short_name]
            if v not in ds.data_vars
        ]

        if missing:
            ds.close()
            raise ValueError(
                f"Missing variables in {collection}: {missing}"
            )

        ds = ds[available]

        # Crop to Arabian Peninsula
        selected_lat = ds.lat[
            (ds.lat >= LAT_MIN) & (ds.lat <= LAT_MAX)
        ]

        selected_lon = ds.lon[
            (ds.lon >= LON_MIN) & (ds.lon <= LON_MAX)
        ]

        ds = ds.sel(lat=selected_lat, lon=selected_lon)

        # Load cropped data into memory, then close source file
        ds.load()
        ds.close()

        datasets.append(ds)

    # Combine the four collections
    data = xr.merge(
        datasets,
        compat="no_conflicts",
        join="exact"
    )

    # ========================================================
    # DERIVED VARIABLES
    # ========================================================

    # Temperature: Kelvin to Celsius
    data["TEMP_C"] = data["T2M"] - 273.15
    data["TEMP_C"].attrs["units"] = "degC"

    # Relative humidity from temperature and dew point
    # Magnus approximation
    temperature = data["TEMP_C"]
    dewpoint = data["T2MDEW"] - 273.15

    def saturation_vapour_pressure(temp):
        return 6.112 * np.exp(
            (17.67 * temp) / (temp + 243.5)
        )

    rh = (
        100
        * saturation_vapour_pressure(dewpoint)
        / saturation_vapour_pressure(temperature)
    )

    data["RH"] = rh.clip(0, 100)
    data["RH"].attrs["units"] = "%"

    # Wind speed from U and V components
    data["WIND_SPEED"] = np.sqrt(
        data["U10M"]**2 + data["V10M"]**2
    )
    data["WIND_SPEED"].attrs["units"] = "m/s"

    # Precipitation: monthly mean flux to monthly accumulation
    seconds_in_month = (
        calendar.monthrange(year, month)[1] * 86400
    )

    for variable in ["PRECTOT", "PRECTOTCORR"]:

        if variable in data:
            output_name = variable + "_MM_MONTH"

            data[output_name] = (
                data[variable] * seconds_in_month
            )

            data[output_name].attrs["units"] = "mm/month"

    # Dust concentration: kg/m3 to micrograms/m3
    data["DUST_UG_M3"] = data["DUSMASS"] * 1e9
    data["DUST_UG_M3"].attrs["units"] = "ug/m3"

    data["FINE_DUST_UG_M3"] = data["DUSMASS25"] * 1e9
    data["FINE_DUST_UG_M3"].attrs["units"] = "ug/m3"

    # ========================================================
    # SAVE REGIONAL GRID
    # ========================================================

    output_file = OUTPUT / f"ArabianPeninsula_{yearmonth}.nc"

    data.to_netcdf(
        output_file,
        engine="netcdf4"
    )

    # ========================================================
    # CALCULATE AREA-WEIGHTED REGIONAL AVERAGES
    # ========================================================

    # Grid-cell area is approximately proportional to cos(latitude)
    weights = np.cos(np.deg2rad(data.lat))

    summary = {
        "year": year,
        "month": month,
        "yearmonth": yearmonth
    }

    summary_variables = [
        "TEMP_C",
        "RH",
        "WIND_SPEED",
        "GWETROOT",
        "GWETTOP",
        "PRECTOT_MM_MONTH",
        "PRECTOTCORR_MM_MONTH",
        "DUST_UG_M3",
        "FINE_DUST_UG_M3"
    ]

    for variable in summary_variables:

        if variable not in data:
            continue

        average = data[variable].weighted(weights).mean(
            dim=("lat", "lon"),
            skipna=True
        )

        summary[variable] = float(average.values.squeeze())

    data.close()

    return summary


# ============================================================
# MAIN LOOP: JANUARY 2000 TO DECEMBER 2025
# ============================================================

results = []

for year in range(START_YEAR, END_YEAR + 1):

    for month in range(1, 13):

        result = process_month(year, month)
        results.append(result)

        print(f"Finished {result['yearmonth']}")

# Save regional averages
df = pd.DataFrame(results)

csv_file = ROOT / "processed" / "regional_monthly_averages.csv"

csv_file.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(csv_file, index=False)

print("\n================================")
print("PROCESSING COMPLETE")
print("Months processed:", len(df))
print("Regional grids:", OUTPUT)
print("Regional averages:", csv_file)
print("================================")

# %%
from pathlib import Path

folder = Path(
    r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends\data\processed\monthly"
)

files = sorted(folder.glob("ArabianPeninsula_*.nc"))

print("Total regional grids:", len(files))
print("First:", files[0].name)
print("Last:", files[-1].name)  

# %%
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(
    r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends"
)

GRID_DIR = ROOT / "data" / "processed" / "monthly"
OUTPUT = ROOT / "data" / "processed" / "regional_monthly_averages.csv"

files = sorted(GRID_DIR.glob("ArabianPeninsula_*.nc"))

assert len(files) == 312, f"Expected 312 files, found {len(files)}"

variables = [
    "TEMP_C",
    "RH",
    "WIND_SPEED",
    "GWETROOT",
    "GWETTOP",
    "PRECTOT_MM_MONTH",
    "PRECTOTCORR_MM_MONTH",
    "DUST_UG_M3",
    "FINE_DUST_UG_M3"
]

results = []

for i, filepath in enumerate(files, 1):

    print(f"[{i}/312] {filepath.name}")

    with xr.open_dataset(filepath) as ds:

        weights = np.cos(np.deg2rad(ds.lat))

        row = {
            "yearmonth": filepath.stem.split("_")[-1],
            "year": int(filepath.stem[-6:-2]),
            "month": int(filepath.stem[-2:])
        }

        for variable in variables:

            if variable not in ds:
                continue

            mean = ds[variable].weighted(weights).mean(
                dim=("lat", "lon"),
                skipna=True
            )

            row[variable] = float(mean.values.squeeze())

        results.append(row)

df = pd.DataFrame(results)

df.to_csv(OUTPUT, index=False)

print("\nCOMPLETE")
print("Rows:", len(df))
print("Saved:", OUTPUT)
print(df.head())
print(df.tail())


# %%
import pandas as pd

csv_path = r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends\data\processed\regional_monthly_averages.csv"

df = pd.read_csv(csv_path)

print("Rows:", len(df))
print("First month:", df["yearmonth"].iloc[0])
print("Last month:", df["yearmonth"].iloc[-1])
print("Duplicate months:", df["yearmonth"].duplicated().sum())
print("\nMissing values:")
print(df.isna().sum())
print("\nColumns:")
print(df.columns.tolist())

# %%
checks = {
    "TEMP_C": (-90, 65),
    "RH": (0, 100),
    "WIND_SPEED": (0, 100),
    "GWETROOT": (0, 1),
    "GWETTOP": (0, 1),
    "PRECTOT_MM_MONTH": (0, None),
    "PRECTOTCORR_MM_MONTH": (0, None),
    "DUST_UG_M3": (0, None),
    "FINE_DUST_UG_M3": (0, None)
}

for variable, (lower, upper) in checks.items():
    values = df[variable]
    invalid = pd.Series(False, index=values.index)

    if lower is not None:
        invalid |= values < lower
    if upper is not None:
        invalid |= values > upper

    print(
        f"{variable:25} "
        f"Min: {values.min():10.3f} | "
        f"Max: {values.max():10.3f} | "
        f"Invalid: {invalid.sum()}"
    )

print("\nSummary statistics:")
print(df[list(checks)].describe().round(3).T)

# %%
import matplotlib.pyplot as plt
import pandas as pd

# Sort chronologically
df = df.sort_values("yearmonth").copy()

# Annual aggregation
annual_df = df.groupby("year").agg({
    "TEMP_C": "mean",
    "RH": "mean",
    "WIND_SPEED": "mean",
    "GWETROOT": "mean",
    "GWETTOP": "mean",
    "PRECTOT_MM_MONTH": "sum",
    "PRECTOTCORR_MM_MONTH": "sum",
    "DUST_UG_M3": "mean",
    "FINE_DUST_UG_M3": "mean"
}).reset_index()

print(annual_df.to_string(index=False))

# %%
variables = [
    ("TEMP_C", "Temperature (°C)"),
    ("RH", "Relative Humidity (%)"),
    ("WIND_SPEED", "Wind Speed (m/s)"),
    ("GWETROOT", "Root-Zone Soil Wetness"),
    ("GWETTOP", "Top-Layer Soil Wetness"),
    ("PRECTOT_MM_MONTH", "Annual Precipitation (mm)"),
    ("PRECTOTCORR_MM_MONTH", "Annual Corrected Precipitation (mm)"),
    ("DUST_UG_M3", "Dust Concentration (µg/m³)"),
    ("FINE_DUST_UG_M3", "Fine Dust Concentration (µg/m³)")
]

fig, axes = plt.subplots(3, 3, figsize=(16, 12))
axes = axes.flatten()

for ax, (column, label) in zip(axes, variables):
    ax.plot(annual_df["year"], annual_df[column], marker="o")
    ax.set_title(label)
    ax.set_xlabel("Year")
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# %%
from scipy.stats import linregress
import pandas as pd

trend_variables = {
    "TEMP_C": "Temperature (°C)",
    "RH": "Relative humidity (%)",
    "WIND_SPEED": "Wind speed (m/s)",
    "GWETROOT": "Root-zone soil wetness",
    "GWETTOP": "Top-layer soil wetness",
    "PRECTOT_MM_MONTH": "Precipitation (mm/year)",
    "PRECTOTCORR_MM_MONTH": "Corrected precipitation (mm/year)",
    "DUST_UG_M3": "Dust concentration (µg/m³)",
    "FINE_DUST_UG_M3": "Fine dust concentration (µg/m³)"
}

results = []

for column, label in trend_variables.items():
    result = linregress(annual_df["year"], annual_df[column])

    results.append({
        "Variable": label,
        "Slope per year": result.slope,
        "Change per decade": result.slope * 10,
        "P-value": result.pvalue,
        "R-squared": result.rvalue ** 2,
        "2000 value": annual_df[column].iloc[0],
        "2025 value": annual_df[column].iloc[-1],
        "Endpoint difference": (
            annual_df[column].iloc[-1] - annual_df[column].iloc[0]
        )
    })

trend_df = pd.DataFrame(results)

print(trend_df.round(4).to_string(index=False))

# %%
from scipy.stats import pearsonr, spearmanr, linregress
import pandas as pd

# Remove each calendar month's long-term average
monthly_anomalies = df.copy()

variables = [
    "RH", "GWETROOT", "GWETTOP",
    "WIND_SPEED", "DUST_UG_M3", "FINE_DUST_UG_M3"
]

for col in variables:
    monthly_anomalies[col] = (
        df[col] - df.groupby("month")[col].transform("mean")
    )

# Also remove each variable's linear long-term trend
time = range(len(monthly_anomalies))

for col in variables:
    fit = linregress(time, monthly_anomalies[col])
    monthly_anomalies[col] = (
        monthly_anomalies[col] -
        (fit.intercept + fit.slope * pd.Series(time, index=df.index))
    )

# Test relationships
pairs = [
    ("RH", "GWETROOT"),
    ("RH", "GWETTOP"),
    ("WIND_SPEED", "DUST_UG_M3"),
    ("WIND_SPEED", "FINE_DUST_UG_M3"),
    ("GWETROOT", "DUST_UG_M3"),
    ("GWETTOP", "DUST_UG_M3")
]

for x, y in pairs:
    r, p = pearsonr(monthly_anomalies[x], monthly_anomalies[y])
    rho, p_s = spearmanr(monthly_anomalies[x], monthly_anomalies[y])

    print(f"\n{x} vs {y}")
    print(f"Pearson r:  {r:.4f} | p-value: {p:.6g}")
    print(f"Spearman ρ: {rho:.4f} | p-value: {p_s:.6g}")

# %%
import numpy as np
from scipy.stats import t as t_dist
from statsmodels.tsa.stattools import acf

pairs = [
    ("RH", "GWETROOT"),
    ("RH", "GWETTOP"),
    ("WIND_SPEED", "DUST_UG_M3"),
    ("WIND_SPEED", "FINE_DUST_UG_M3"),
    ("GWETROOT", "DUST_UG_M3"),
    ("GWETTOP", "DUST_UG_M3")
]

for x, y in pairs:
    a = monthly_anomalies[x].to_numpy()
    b = monthly_anomalies[y].to_numpy()

    r = np.corrcoef(a, b)[0, 1]

    # Lag-1 autocorrelation
    rx = acf(a, nlags=1, fft=False)[1]
    ry = acf(b, nlags=1, fft=False)[1]

    # Approximate effective sample size
    n = len(a)
    n_eff = n * (1 - rx * ry) / (1 + rx * ry)
    n_eff = np.clip(n_eff, 3, n)

    # Approximate autocorrelation-adjusted p-value
    t_stat = r * np.sqrt((n_eff - 2) / (1 - r**2))
    p_adjusted = 2 * t_dist.sf(abs(t_stat), df=n_eff - 2)

    print(f"\n{x} vs {y}")
    print(f"Correlation: {r:.4f}")
    print(f"Lag-1 autocorrelation: {rx:.3f}, {ry:.3f}")
    print(f"Effective sample size: {n_eff:.1f}")
    print(f"Approx. adjusted p-value: {p_adjusted:.6g}")

# %%
df["PRECIP_DIFFERENCE"] = (
    df["PRECTOTCORR_MM_MONTH"] - df["PRECTOT_MM_MONTH"]
)

print("Mean PRECTOT:", df["PRECTOT_MM_MONTH"].mean())
print("Mean PRECTOTCORR:", df["PRECTOTCORR_MM_MONTH"].mean())

print("\nMean monthly difference:",
      df["PRECIP_DIFFERENCE"].mean())

print("\nDifference statistics:")
print(df["PRECIP_DIFFERENCE"].describe())

# Annual comparison
precip_annual = df.groupby("year").agg({
    "PRECTOT_MM_MONTH": "sum",
    "PRECTOTCORR_MM_MONTH": "sum"
})

precip_annual.plot(
    figsize=(12, 5),
    title="Annual Precipitation: Original vs Corrected"
)

plt.ylabel("Precipitation (mm/year)")
plt.grid(True, alpha=0.3)
plt.show()

# %%
import xarray as xr

grid_path = (
    r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends"
    r"\data\processed\monthly\ArabianPeninsula_200001.nc"
)

with xr.open_dataset(grid_path) as ds:
    print("Variables:")
    print(list(ds.data_vars))

    print("\nCoordinates:")
    print(list(ds.coords))

    for var in ["PRECTOT_MM_MONTH", "PRECTOTCORR_MM_MONTH"]:
        if var in ds:
            print(f"\n{var} metadata:")
            print(ds[var].attrs)

# %%
import earthaccess

results = earthaccess.search_data(
    short_name="M2C0NXASM",
    count=5
)

print("Granules found:", len(results))

for item in results:
    print(item)

# %%
from pathlib import Path
import earthaccess

output_folder = Path(
    r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends\data\processed"
)

output_folder.mkdir(parents=True, exist_ok=True)

downloaded = earthaccess.download(
    results,
    local_path=str(output_folder)
)

print(downloaded)

# %%
import xarray as xr

frland_path = r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends\data\processed\MERRA2_101.const_2d_asm_Nx.00000000.nc4"

ds_land = xr.open_dataset(frland_path)

print(ds_land)
print("\nVariables:")
print(list(ds_land.data_vars))

# %%
import numpy as np
import xarray as xr

# Load one of our existing regional monthly files
monthly_path = r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends\data\processed\monthly\ArabianPeninsula_200001.nc"

ds_month = xr.open_dataset(monthly_path)

# Extract the land fraction and the Arabian Peninsula region
frland = ds_land["FRLAND"].squeeze(drop=True)
frland = frland.sel(
    lat=slice(12, 32),
    lon=slice(34, 60)
)

# Compare coordinates
print("Land fraction shape:", frland.shape)
print("Monthly grid shape:", ds_month["T2M"].shape)

print(
    "Latitude matches:",
    np.array_equal(frland.lat.values, ds_month.lat.values)
)

print(
    "Longitude matches:",
    np.array_equal(frland.lon.values, ds_month.lon.values)
)

print("Land fraction range:", float(frland.min()), float(frland.max()))

# %%
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends")
MONTHLY = ROOT / "data" / "processed" / "monthly"

# Remove the single time dimension from the static land-fraction data
frland = ds_land["FRLAND"].squeeze(drop=True)

# Calculate area weights: latitude area correction × fraction of land
weights = np.cos(np.deg2rad(frland.lat)) * frland

def weighted_mean(data):
    data = data.squeeze(drop=True)
    return float(data.weighted(weights).mean(
        dim=("lat", "lon"),
        skipna=True
    ).values)

# Magnus approximation for relative humidity
def calculate_rh(temp_k, dewpoint_k):
    temp_c = temp_k - 273.15
    dew_c = dewpoint_k - 273.15

    es_temp = np.exp(
        (17.625 * temp_c) / (243.04 + temp_c)
    )
    es_dew = np.exp(
        (17.625 * dew_c) / (243.04 + dew_c)
    )

    return np.clip(100 * es_dew / es_temp, 0, 100)

files = sorted(MONTHLY.glob("ArabianPeninsula_*.nc"))

print("Monthly files found:", len(files))

if len(files) != 312:
    raise ValueError("Expected 312 monthly files. Check the folder.")

results = []

for i, file in enumerate(files, start=1):
    ds = xr.open_dataset(file)

    try:
        # Check spatial alignment for every file
        if not np.array_equal(ds.lat.values, frland.lat.values):
            raise ValueError(f"Latitude mismatch: {file.name}")

        if not np.array_equal(ds.lon.values, frland.lon.values):
            raise ValueError(f"Longitude mismatch: {file.name}")

        timestamp = pd.Timestamp(ds.time.values[0])
        seconds_in_month = timestamp.days_in_month * 86400

        temp = ds["T2M"]
        dew = ds["T2MDEW"]

        wind = np.sqrt(ds["U10M"]**2 + ds["V10M"]**2)

        rh = calculate_rh(temp, dew)

        row = {
            "yearmonth": timestamp.strftime("%Y%m"),
            "year": timestamp.year,
            "month": timestamp.month,

            "TEMP_C": weighted_mean(temp - 273.15),
            "RH": weighted_mean(rh),
            "WIND_SPEED": weighted_mean(wind),

            "GWETROOT": weighted_mean(ds["GWETROOT"]),
            "GWETTOP": weighted_mean(ds["GWETTOP"]),

            "PRECTOT_MM_MONTH": (
                weighted_mean(ds["PRECTOT"]) * seconds_in_month
            ),

            "PRECTOTCORR_MM_MONTH": (
                weighted_mean(ds["PRECTOTCORR"]) * seconds_in_month
            ),

            "DUST_UG_M3": (
                weighted_mean(ds["DUSMASS"]) * 1e9
            ),

            "FINE_DUST_UG_M3": (
                weighted_mean(ds["DUSMASS25"]) * 1e9
            )
        }

        results.append(row)

    finally:
        ds.close()

    if i % 25 == 0 or i == len(files):
        print(f"Processed {i}/{len(files)}")

# Save separately so the original remains untouched
df_corrected = pd.DataFrame(results)

output_path = (
    ROOT / "data" / "processed" /
    "regional_monthly_averages_land_weighted.csv"
)

df_corrected.to_csv(output_path, index=False)

print("\nFinished!")
print("Rows:", len(df_corrected))
print("First month:", df_corrected.iloc[0]["yearmonth"])
print("Last month:", df_corrected.iloc[-1]["yearmonth"])
print("Missing values:")
print(df_corrected.isna().sum())
print("\nSaved to:", output_path)

# %%
print("Land latitude:", frland.lat.values[:5])
print("Monthly latitude:", ds_month.lat.values[:5])

print("Land longitude:", frland.lon.values[:5])
print("Monthly longitude:", ds_month.lon.values[:5])

# %%
frland = ds_land["FRLAND"].squeeze(drop=True)

frland = frland.sel(
    lat=slice(12, 32),
    lon=slice(34, 60)
)

print("Land latitude:", frland.lat.values[:5])
print("Monthly latitude:", ds_month.lat.values[:5])

print("Land longitude:", frland.lon.values[:5])
print("Monthly longitude:", ds_month.lon.values[:5])

print(
    "Latitude matches:",
    np.array_equal(frland.lat.values, ds_month.lat.values)
)

print(
    "Longitude matches:",
    np.array_equal(frland.lon.values, ds_month.lon.values)
)

# %%
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends")
MONTHLY = ROOT / "data" / "processed" / "monthly"

weights = np.cos(np.deg2rad(frland.lat)) * frland

def weighted_mean(data):
    return float(
        data.squeeze(drop=True)
        .weighted(weights)
        .mean(dim=("lat", "lon"), skipna=True)
        .values
    )

def calculate_rh(temp_k, dewpoint_k):
    temp_c = temp_k - 273.15
    dew_c = dewpoint_k - 273.15

    es_temp = np.exp(17.625 * temp_c / (243.04 + temp_c))
    es_dew = np.exp(17.625 * dew_c / (243.04 + dew_c))

    return np.clip(100 * es_dew / es_temp, 0, 100)

files = sorted(MONTHLY.glob("ArabianPeninsula_*.nc"))

print("Monthly files found:", len(files))

if len(files) != 312:
    raise ValueError("Expected 312 monthly files.")

results = []

for i, file in enumerate(files, start=1):

    with xr.open_dataset(file) as ds:

        if not np.array_equal(ds.lat.values, frland.lat.values):
            raise ValueError(f"Latitude mismatch: {file.name}")

        if not np.array_equal(ds.lon.values, frland.lon.values):
            raise ValueError(f"Longitude mismatch: {file.name}")

        timestamp = pd.Timestamp(ds.time.values[0])
        seconds_in_month = timestamp.days_in_month * 86400

        temp = ds["T2M"]
        dew = ds["T2MDEW"]

        wind = np.sqrt(ds["U10M"]**2 + ds["V10M"]**2)
        rh = calculate_rh(temp, dew)

        row = {
            "yearmonth": timestamp.strftime("%Y%m"),
            "year": timestamp.year,
            "month": timestamp.month,

            "TEMP_C": weighted_mean(temp - 273.15),
            "RH": weighted_mean(rh),
            "WIND_SPEED": weighted_mean(wind),

            "GWETROOT": weighted_mean(ds["GWETROOT"]),
            "GWETTOP": weighted_mean(ds["GWETTOP"]),

            "PRECTOT_MM_MONTH": (
                weighted_mean(ds["PRECTOT"]) * seconds_in_month
            ),

            "PRECTOTCORR_MM_MONTH": (
                weighted_mean(ds["PRECTOTCORR"]) * seconds_in_month
            ),

            "DUST_UG_M3": weighted_mean(ds["DUSMASS"]) * 1e9,
            "FINE_DUST_UG_M3": weighted_mean(ds["DUSMASS25"]) * 1e9
        }

        results.append(row)

    if i % 25 == 0 or i == len(files):
        print(f"Processed {i}/{len(files)}")

df_corrected = pd.DataFrame(results)

output_path = (
    ROOT / "data" / "processed" /
    "regional_monthly_averages_land_weighted.csv"
)

df_corrected.to_csv(output_path, index=False)

print("\nFinished!")
print("Rows:", len(df_corrected))
print("First month:", df_corrected.iloc[0]["yearmonth"])
print("Last month:", df_corrected.iloc[-1]["yearmonth"])
print("\nMissing values:")
print(df_corrected.isna().sum())
print("\nSaved to:", output_path)

# %%
import pandas as pd

old_path = ROOT / "data" / "processed" / "regional_monthly_averages.csv"
new_path = ROOT / "data" / "processed" / "regional_monthly_averages_land_weighted.csv"

old = pd.read_csv(old_path)
new = pd.read_csv(new_path)

columns = [
    "TEMP_C", "RH", "WIND_SPEED",
    "GWETROOT", "GWETTOP",
    "PRECTOT_MM_MONTH", "PRECTOTCORR_MM_MONTH",
    "DUST_UG_M3", "FINE_DUST_UG_M3"
]

print("CORRECTED DATA SUMMARY")
print(new[columns].describe().round(3))

print("\nCHANGE FROM ORIGINAL AVERAGES")
comparison = pd.DataFrame({
    "Original mean": old[columns].mean(),
    "Land-weighted mean": new[columns].mean()
})

comparison["Difference"] = (
    comparison["Land-weighted mean"] - comparison["Original mean"]
)

print(comparison.round(3))

# %%
import pandas as pd
from scipy.stats import linregress

df = pd.read_csv(new_path)

annual = df.groupby("year").agg({
    "TEMP_C": "mean",
    "RH": "mean",
    "WIND_SPEED": "mean",
    "GWETROOT": "mean",
    "GWETTOP": "mean",
    "PRECTOT_MM_MONTH": "sum",
    "PRECTOTCORR_MM_MONTH": "sum",
    "DUST_UG_M3": "mean",
    "FINE_DUST_UG_M3": "mean"
}).reset_index()

variables = [
    "TEMP_C", "RH", "WIND_SPEED",
    "GWETROOT", "GWETTOP",
    "PRECTOT_MM_MONTH", "PRECTOTCORR_MM_MONTH",
    "DUST_UG_M3", "FINE_DUST_UG_M3"
]

for variable in variables:
    result = linregress(annual["year"], annual[variable])

    print(f"\n{variable}")
    print(f"Change per decade: {result.slope * 10:.4f}")
    print(f"R²: {result.rvalue**2:.4f}")
    print(f"P-value: {result.pvalue:.6g}")
    print(f"2000: {annual[variable].iloc[0]:.4f}")
    print(f"2025: {annual[variable].iloc[-1]:.4f}")

annual.to_csv(
    ROOT / "data" / "processed" / "annual_trends_land_weighted.csv",
    index=False
)

print("\nAnnual analysis saved.")

# %%
import xarray as xr
import numpy as np

test_file = MONTHLY / "ArabianPeninsula_200001.nc"

with xr.open_dataset(test_file) as ds:

    top = ds["GWETTOP"].squeeze(drop=True)

    print("GWETTOP original simple mean:")
    print(float(top.mean().values))

    print("\nGWETTOP land-weighted mean:")
    print(float(top.weighted(weights).mean().values))

    print("\nFRLAND statistics:")
    print(frland.to_series().describe())

    print("\nGWETTOP statistics:")
    print(top.to_series().describe())

# %%
import pandas as pd

diagnostic = xr.Dataset({
    "GWETTOP": top,
    "FRLAND": frland
}).to_dataframe().dropna()

diagnostic["land_category"] = pd.cut(
    diagnostic["FRLAND"],
    bins=[-0.01, 0.25, 0.75, 1.01],
    labels=["Mostly water", "Mixed", "Mostly land"]
)

print(
    diagnostic.groupby("land_category", observed=False)
    [["GWETTOP", "FRLAND"]]
    .mean()
    .round(4)
)

# %%
import pandas as pd
import numpy as np

from scipy.stats import pearsonr, spearmanr
from scipy.signal import detrend

df = pd.read_csv(new_path)

variables = [
    "TEMP_C",
    "RH",
    "WIND_SPEED",
    "GWETROOT",
    "GWETTOP",
    "PRECTOT_MM_MONTH",
    "DUST_UG_M3",
    "FINE_DUST_UG_M3"
]

# Remove the average seasonal cycle
anomalies = pd.DataFrame(index=df.index)

for variable in variables:
    monthly_climatology = df.groupby("month")[variable].transform("mean")
    anomalies[variable] = df[variable] - monthly_climatology

# Remove the long-term linear trend
for variable in variables:
    anomalies[variable] = detrend(anomalies[variable].values)

# Environmental relationships to investigate
pairs = [
    ("WIND_SPEED", "DUST_UG_M3"),
    ("WIND_SPEED", "FINE_DUST_UG_M3"),
    ("GWETROOT", "DUST_UG_M3"),
    ("GWETTOP", "DUST_UG_M3"),
    ("PRECTOT_MM_MONTH", "GWETROOT"),
    ("PRECTOT_MM_MONTH", "GWETTOP"),
    ("RH", "GWETROOT"),
    ("RH", "GWETTOP"),
    ("TEMP_C", "RH")
]

print("CORRELATION RESULTS")
print("Seasonal cycle and linear trends removed")

for x, y in pairs:
    r, p = pearsonr(anomalies[x], anomalies[y])
    rho, sp = spearmanr(anomalies[x], anomalies[y])

    print(f"\n{x} vs {y}")
    print(f"Pearson r: {r:.4f}")
    print(f"Pearson p-value: {p:.6g}")
    print(f"Spearman rho: {rho:.4f}")
    print(f"Spearman p-value: {sp:.6g}")

print("\nCorrelation analysis complete.")


# %%
from statsmodels.tsa.stattools import acf
from scipy.stats import t
from statsmodels.stats.multitest import multipletests
import numpy as np
import pandas as pd

results = []

n = len(anomalies)

for x, y in pairs:

    r = anomalies[x].corr(anomalies[y])

    # Lag-1 autocorrelation of each variable
    rho_x = acf(anomalies[x], nlags=1, fft=False)[1]
    rho_y = acf(anomalies[y], nlags=1, fft=False)[1]

    # Approximate effective sample size
    n_eff = n * (1 - rho_x * rho_y) / (1 + rho_x * rho_y)
    n_eff = np.clip(n_eff, 3, n)

    # Approximate autocorrelation-adjusted p-value
    t_stat = r * np.sqrt((n_eff - 2) / (1 - r**2))
    p_adjusted = 2 * t.sf(abs(t_stat), df=n_eff - 2)

    results.append({
        "Relationship": f"{x} vs {y}",
        "Pearson r": r,
        "Lag-1 ACF X": rho_x,
        "Lag-1 ACF Y": rho_y,
        "Effective sample size": n_eff,
        "Adjusted p-value": p_adjusted
    })

results_df = pd.DataFrame(results)

# Correct for testing nine relationships
results_df["Multiple-test p-value"] = multipletests(
    results_df["Adjusted p-value"],
    method="fdr_bh"
)[1]

print(results_df.round(5).to_string(index=False))

results_df.to_csv(
    ROOT / "data" / "processed" / "correlation_significance.csv",
    index=False
)

print("\nAdjusted correlation analysis saved.")

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import detrend
from scipy.stats import linregress


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(
    r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends"
)

DATA = ROOT / "data" / "processed"
CSV_PATH = DATA / "regional_monthly_averages_land_weighted.csv"

FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV_PATH)

if len(df) != 312:
    raise ValueError(f"Expected 312 rows, found {len(df)}")

print("Loaded:", len(df), "monthly records")


# --------------------------------------------------
# ANNUAL DATA
# --------------------------------------------------

annual = df.groupby("year").agg({
    "TEMP_C": "mean",
    "GWETROOT": "mean",
    "GWETTOP": "mean",
    "PRECTOT_MM_MONTH": "sum",
    "PRECTOTCORR_MM_MONTH": "sum",
    "DUST_UG_M3": "mean",
    "FINE_DUST_UG_M3": "mean"
}).reset_index()


def plot_annual_series(
    filename,
    title,
    ylabel,
    series
):
    fig, ax = plt.subplots(figsize=(10, 5))

    years = annual["year"].values

    for column, label in series:

        values = annual[column].values

        ax.plot(
            years,
            values,
            marker="o",
            markersize=3,
            label=label
        )

        result = linregress(years, values)

        fitted = (
            result.slope * years
            + result.intercept
        )

        ax.plot(
            years,
            fitted,
            linestyle="--",
            label=f"{label} trend"
        )

        print(
            f"{label}: "
            f"{result.slope * 10:.4f} per decade | "
            f"R²={result.rvalue**2:.4f} | "
            f"p={result.pvalue:.6g}"
        )

    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()

    fig.savefig(
        FIGURES / filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)


# 1. TEMPERATURE

plot_annual_series(
    "01_annual_temperature.png",
    "Annual Mean Temperature — Arabian Peninsula",
    "Temperature (°C)",
    [
        ("TEMP_C", "Mean temperature")
    ]
)


# 2. PRECIPITATION

plot_annual_series(
    "02_annual_precipitation.png",
    "Annual Precipitation — Arabian Peninsula",
    "Precipitation (mm/year)",
    [
        ("PRECTOT_MM_MONTH", "PRECTOT"),
        ("PRECTOTCORR_MM_MONTH", "PRECTOTCORR")
    ]
)


# 3. SOIL WETNESS

plot_annual_series(
    "03_annual_soil_wetness.png",
    "Annual Mean Soil Wetness — Arabian Peninsula",
    "Soil wetness (dimensionless)",
    [
        ("GWETROOT", "Root-zone wetness"),
        ("GWETTOP", "Topsoil wetness")
    ]
)


# 4. DUST — SEPARATE PANELS

fig, axes = plt.subplots(
    2,
    1,
    figsize=(10, 8),
    sharex=True
)

dust_series = [
    ("DUST_UG_M3", "Total dust", axes[0]),
    ("FINE_DUST_UG_M3", "Fine dust (DUSMASS25)", axes[1])
]

years = annual["year"].values

for column, label, ax in dust_series:

    values = annual[column].values

    ax.plot(
        years,
        values,
        marker="o",
        markersize=3,
        label=label
    )

    result = linregress(years, values)

    fitted = (
        result.slope * years
        + result.intercept
    )

    ax.plot(
        years,
        fitted,
        linestyle="--",
        label="Linear trend"
    )

    ax.set_ylabel("Concentration (µg/m³)")
    ax.set_title(label)
    ax.grid(True, alpha=0.3)
    ax.legend()

    print(
        f"{label}: "
        f"{result.slope * 10:.4f} µg/m³ per decade | "
        f"R²={result.rvalue**2:.4f} | "
        f"p={result.pvalue:.6g}"
    )

axes[1].set_xlabel("Year")

fig.suptitle(
    "Annual Mean Dust Concentration — Arabian Peninsula"
)

fig.tight_layout()

fig.savefig(
    FIGURES / "04_annual_dust.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close(fig)

print("\nImproved annual figures saved.")


# --------------------------------------------------
# MONTHLY ANOMALIES
# --------------------------------------------------

variables = [
    "WIND_SPEED",
    "DUST_UG_M3",
    "GWETTOP",
    "PRECTOT_MM_MONTH"
]

anomalies = pd.DataFrame(index=df.index)

for variable in variables:
    monthly_climatology = (
        df.groupby("month")[variable]
        .transform("mean")
    )

    anomalies[variable] = (
        df[variable] - monthly_climatology
    )

    anomalies[variable] = detrend(
        anomalies[variable].values
    )


# --------------------------------------------------
# SCATTER PLOTS
# --------------------------------------------------

def make_scatter(x_name, y_name, filename, title, xlabel, ylabel):

    x = anomalies[x_name].values
    y = anomalies[y_name].values

    result = linregress(x, y)

    fig, ax = plt.subplots(figsize=(7, 6))

    ax.scatter(
        x,
        y,
        alpha=0.55,
        s=22,
        label="Monthly anomalies"
    )

    line_x = np.linspace(x.min(), x.max(), 100)
    line_y = result.slope * line_x + result.intercept

    ax.plot(
        line_x,
        line_y,
        linestyle="--",
        label="Linear fit"
    )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)

    ax.text(
        0.04,
        0.96,
        f"Pearson r = {result.rvalue:.3f}\n"
        f"R² = {result.rvalue**2:.3f}",
        transform=ax.transAxes,
        verticalalignment="top"
    )

    ax.legend()
    fig.tight_layout()

    fig.savefig(
        FIGURES / filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)


# 5. Wind and dust

make_scatter(
    "WIND_SPEED",
    "DUST_UG_M3",
    "05_wind_vs_dust.png",
    "Wind Speed vs Dust Concentration",
    "Wind speed anomaly (m/s)",
    "Dust concentration anomaly (µg/m³)"
)


# 6. Topsoil wetness and dust

make_scatter(
    "GWETTOP",
    "DUST_UG_M3",
    "06_soil_wetness_vs_dust.png",
    "Topsoil Wetness vs Dust Concentration",
    "Topsoil wetness anomaly",
    "Dust concentration anomaly (µg/m³)"
)


# 7. Precipitation and topsoil wetness

make_scatter(
    "PRECTOT_MM_MONTH",
    "GWETTOP",
    "07_precipitation_vs_soil_wetness.png",
    "Precipitation vs Topsoil Wetness",
    "Precipitation anomaly (mm/month)",
    "Topsoil wetness anomaly"
)


print("\nAll figures generated successfully.")
print("Saved to:", FIGURES)


# %%

from pathlib import Path
import numpy as np
import xarray as xr

ROOT = Path(
    r"C:\Users\HP\Desktop\nasa 2026\arabian_earth_trends"
)

FRLAND_PATH = (
    ROOT / "data" / "processed"
    / "MERRA2_101.const_2d_asm_Nx.00000000.nc4"
)

REGIONS = {
    "Northwest": (20, 32, 34, 43),
    "North_Central": (20, 32, 43, 50),
    "Northeast": (20, 32, 50, 60),
    "Southwest": (12, 20, 34, 47),
    "Southeast": (12, 20, 47, 60)
}

with xr.open_dataset(FRLAND_PATH) as ds:
    land = ds["FRLAND"].squeeze(drop=True)
    land = land.sel(
        lat=slice(12, 32),
        lon=slice(34, 60)
    ).load()

land = land.fillna(0)

domain = land > 0.05

assignment_count = xr.zeros_like(
    land, dtype=np.int32
)

for name, (lat_min, lat_max, lon_min, lon_max) in REGIONS.items():

    mask = (
        (land.lat >= lat_min)
        & (
            (land.lat < lat_max)
            if lat_max == 20
            else (land.lat <= lat_max)
        )
        & (land.lon >= lon_min)
        & (
            (land.lon <= lon_max)
            if lon_max == 60
            else (land.lon < lon_max)
        )
    )

    assignment_count += mask.astype(np.int32)

uncovered = domain & (assignment_count == 0)
overlapping = domain & (assignment_count > 1)

print("LAND COVERAGE AUDIT")
print("Total land-containing cells:", int(domain.sum()))
print("Uncovered land cells:", int(uncovered.sum()))
print("Overlapping land cells:", int(overlapping.sum()))

print(
    "Uncovered land area weight:",
    float(
        (
            np.cos(np.deg2rad(land.lat))
            * land.where(uncovered, 0)
        ).sum()
    )
)

print(
    "Overlapping land area weight:",
    float(
        (
            np.cos(np.deg2rad(land.lat))
            * land.where(overlapping, 0)
        ).sum()
    )
)
uncovered_locations = land.where(uncovered).stack(
    cell=("lat", "lon")
).dropna("cell")

print("\nUNCOVERED CELL LOCATIONS")

for lat, lon, fraction in zip(
    uncovered_locations.lat.values,
    uncovered_locations.lon.values,
    uncovered_locations.values
):
    print(
        f"Latitude: {lat:.3f}, "
        f"Longitude: {lon:.3f}, "
        f"Land fraction: {fraction:.3f}"
    )

# %%
OUTPUT = ROOT / "data" / "processed"

annual_path = OUTPUT / "regional_annual_analysis.csv"

annual_df = pd.read_csv(annual_path)

print("ANNUAL DATA VALIDATION")
print("Total rows:", len(annual_df))
print("Regions:", annual_df["region"].nunique())
print("Years:", annual_df["year"].nunique())
print("Missing values:", annual_df.isna().sum().sum())

print(
    "Duplicate region-year records:",
    annual_df.duplicated(["region", "year"]).sum()
)

for region, group in annual_df.groupby("region"):
    print(
        region,
        "| Years:", len(group),
        "| First:", group["year"].min(),
        "| Last:", group["year"].max()
    )

# %%
from scipy.stats import linregress
import pandas as pd

annual_path = OUTPUT / "regional_annual_analysis.csv"
annual_df = pd.read_csv(annual_path)

variables = [
    "TEMP_C",
    "RH",
    "WIND_SPEED",
    "GWETROOT",
    "GWETTOP",
    "PRECTOT_MM_MONTH",
    "PRECTOTCORR_MM_MONTH",
    "DUST_UG_M3",
    "FINE_DUST_UG_M3"
]

results = []

for region, group in annual_df.groupby("region"):

    group = group.sort_values("year")

    for variable in variables:

        result = linregress(
            group["year"],
            group[variable]
        )

        results.append({
            "Region": region,
            "Variable": variable,
            "Change_per_decade": result.slope * 10,
            "R_squared": result.rvalue ** 2,
            "P_value": result.pvalue,
            "Value_2000": group.iloc[0][variable],
            "Value_2025": group.iloc[-1][variable]
        })

trend_df = pd.DataFrame(results)

trend_path = OUTPUT / "regional_linear_trends.csv"
trend_df.to_csv(trend_path, index=False)

print("REGIONAL LINEAR TRENDS")
print(trend_df.round(5).to_string(index=False))
print("\nSaved:", trend_path)

# %%
import pymannkendall as mk
import pandas as pd
import numpy as np
from statsmodels.stats.multitest import multipletests

# Load annual regional data
annual_path = OUTPUT / "regional_annual_analysis.csv"
annual_df = pd.read_csv(annual_path)

variables = [
    "TEMP_C",
    "RH",
    "WIND_SPEED",
    "GWETROOT",
    "GWETTOP",
    "PRECTOT_MM_MONTH",
    "PRECTOTCORR_MM_MONTH",
    "DUST_UG_M3",
    "FINE_DUST_UG_M3"
]

results = []

for region, group in annual_df.groupby("region"):

    group = group.sort_values("year")

    for variable in variables:

        values = group[variable].to_numpy(dtype=float)

        # Hamed-Rao modified Mann-Kendall test
        test = mk.hamed_rao_modification_test(
            values,
            alpha=0.05
        )

        # Sen's slope
        sen = mk.sens_slope(values)

        results.append({
            "Region": region,
            "Variable": variable,
            "MK_trend": test.trend,
            "MK_tau": test.Tau,
            "MK_p_value": test.p,
            "MK_z": test.z,
            "Sen_slope_per_year": sen.slope,
            "Sen_slope_per_decade": sen.slope * 10
        })

results_df = pd.DataFrame(results)

# Correct for 45 simultaneous statistical tests
results_df["FDR_p_value"] = multipletests(
    results_df["MK_p_value"],
    method="fdr_bh"
)[1]

results_df["FDR_significant"] = (
    results_df["FDR_p_value"] < 0.05
)

# Save results
output_path = OUTPUT / "regional_mann_kendall_sen.csv"

results_df.to_csv(output_path, index=False)

print("REGIONAL MANN-KENDALL AND SEN'S SLOPE")
print(results_df.round(5).to_string(index=False))

print("\nSaved:", output_path)

# %%
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, t
from scipy.signal import detrend
from statsmodels.tsa.stattools import acf
from statsmodels.stats.multitest import multipletests

# Load regional monthly data
monthly_path = OUTPUT / "regional_monthly_analysis.csv"
df = pd.read_csv(monthly_path)

# Five relationships to investigate
pairs = [
    ("WIND_SPEED", "DUST_UG_M3"),
    ("WIND_SPEED", "FINE_DUST_UG_M3"),
    ("GWETROOT", "DUST_UG_M3"),
    ("GWETTOP", "DUST_UG_M3"),
    ("PRECTOT_MM_MONTH", "GWETROOT")
]

results = []

for region, group in df.groupby("region"):

    group = group.sort_values("yearmonth").copy()

    # Remove monthly seasonality and linear trend
    anomalies = pd.DataFrame(index=group.index)

    variables = set()
    for x, y in pairs:
        variables.add(x)
        variables.add(y)

    for variable in variables:
        seasonal = (
            group.groupby("month")[variable]
            .transform("mean")
        )

        anomaly = group[variable] - seasonal

        anomalies[variable] = detrend(
            anomaly.to_numpy()
        )

    n = len(group)

    for x, y in pairs:

        xv = anomalies[x].to_numpy()
        yv = anomalies[y].to_numpy()

        r, _ = pearsonr(xv, yv)

        rho_x = acf(xv, nlags=1, fft=False)[1]
        rho_y = acf(yv, nlags=1, fft=False)[1]

        # Approximate effective sample size
        denominator = 1 + rho_x * rho_y

        if denominator <= 0:
            n_eff = n
        else:
            n_eff = n * (1 - rho_x * rho_y) / denominator

        n_eff = float(np.clip(n_eff, 3, n))

        t_stat = r * np.sqrt(
            (n_eff - 2) / (1 - r**2)
        )

        p_adjusted = 2 * t.sf(
            abs(t_stat),
            df=n_eff - 2
        )

        results.append({
            "Region": region,
            "Relationship": f"{x} vs {y}",
            "Pearson_r": r,
            "Lag1_ACF_X": rho_x,
            "Lag1_ACF_Y": rho_y,
            "Effective_sample_size": n_eff,
            "Autocorrelation_adjusted_p": p_adjusted
        })

correlation_df = pd.DataFrame(results)

# FDR correction across all 25 tests
correlation_df["FDR_p_value"] = multipletests(
    correlation_df["Autocorrelation_adjusted_p"],
    method="fdr_bh"
)[1]

correlation_df["Significant"] = (
    correlation_df["FDR_p_value"] < 0.05
)

# Save
correlation_path = OUTPUT / "regional_correlation_analysis.csv"

correlation_df.to_csv(
    correlation_path,
    index=False
)

print("REGIONAL CORRELATION ANALYSIS")
print(correlation_df.round(5).to_string(index=False))

print("\nSaved:", correlation_path)

# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = OUTPUT / "regional_correlation_analysis.csv"
data = pd.read_csv(path)

region_order = [
    "Northwest",
    "North_Central",
    "Northeast",
    "Southwest",
    "Southeast"
]

relationship_order = [
    "WIND_SPEED vs DUST_UG_M3",
    "WIND_SPEED vs FINE_DUST_UG_M3",
    "GWETROOT vs DUST_UG_M3",
    "GWETTOP vs DUST_UG_M3",
    "PRECTOT_MM_MONTH vs GWETROOT"
]

pivot = data.pivot(
    index="Region",
    columns="Relationship",
    values="Pearson_r"
).reindex(index=region_order, columns=relationship_order)

significance = data.pivot(
    index="Region",
    columns="Relationship",
    values="Significant"
).reindex(index=region_order, columns=relationship_order)

fig, ax = plt.subplots(figsize=(13, 6))

image = ax.imshow(
    pivot.values,
    cmap="RdBu_r",
    vmin=-1,
    vmax=1,
    aspect="auto"
)

ax.set_xticks(range(len(relationship_order)))
ax.set_xticklabels(
    [
        "Wind–Total dust",
        "Wind–Fine dust",
        "Root wetness–Dust",
        "Topsoil wetness–Dust",
        "Precipitation–Root wetness"
    ],
    rotation=25,
    ha="right"
)

ax.set_yticks(range(len(region_order)))
ax.set_yticklabels(region_order)

for i in range(len(region_order)):
    for j in range(len(relationship_order)):
        value = pivot.iloc[i, j]
        star = "*" if significance.iloc[i, j] else ""

        ax.text(
            j, i,
            f"{value:.2f}{star}",
            ha="center",
            va="center",
            color="black"
        )

colorbar = fig.colorbar(image, ax=ax)
colorbar.set_label("Pearson correlation coefficient (r)")

ax.set_title(
    "Regional Environmental Relationships Across the Arabian Peninsula"
)

fig.tight_layout()

output = OUTPUT / "regional_correlation_heatmap.png"
fig.savefig(output, dpi=300, bbox_inches="tight")
plt.show()

print("Saved:", output)

#that was a lot of code and thats a nice heatmap (Marwan Khaled)


