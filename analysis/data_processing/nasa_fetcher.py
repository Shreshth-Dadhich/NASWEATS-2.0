"""NASA-only acquisition, exact collection discovery, spatial clipping and caching.

CMR is metadata discovery, not a substitute for data download. Earthdata access
is explicit and noninteractive. Native products never fall back to NASA POWER.
"""
from __future__ import annotations
import hashlib, json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path
import httpx
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import shape, box
from pyproj import Geod

CATALOG=json.loads((Path(__file__).parent/"catalog.json").read_text(encoding="utf-8"))
CACHE=Path(os.getenv("EARTHSIGNAL_CACHE",str(Path(__file__).parents[2]/"data/processed/cache")))
GEOD=Geod(ellps="WGS84")
CMR="https://cmr.earthdata.nasa.gov/search/collections.umm_json"

class DataUnavailable(RuntimeError):
    pass

def specification(variable, product):
    family=next((v for v in CATALOG if v["id"]==variable),None)
    if not family: raise ValueError("Unknown variable")
    spec=next((p for p in family["products"] if p["id"]==product),None)
    if not spec: raise ValueError("Unknown product")
    # Operator overrides are configuration, not arbitrary user-supplied URLs.
    overrides=json.loads(os.getenv("NASA_PRODUCT_CONFIG","{}"))
    return {**spec,**overrides.get(variable+":"+product,{})}

def discover(short_name):
    response=httpx.get(CMR,params={"short_name":short_name,"page_size":100},timeout=45)
    response.raise_for_status()
    out=[]
    for entry in response.json().get("items",[]):
        u=entry["umm"]
        if u.get("ShortName")!=short_name: continue
        out.append({"concept_id":entry["meta"]["concept-id"],"short_name":u["ShortName"],"version":u.get("Version"),"title":u.get("EntryTitle"),"doi":u.get("DOI",{}).get("DOI"),"temporal":u.get("TemporalExtents"),"url":"https://cmr.earthdata.nasa.gov/search/concepts/"+entry["meta"]["concept-id"]+".html"})
    return out

def validate_geometry(geometry):
    region=shape(geometry)
    if region.geom_type not in ("Polygon","MultiPolygon") or region.is_empty or not region.is_valid:
        raise ValueError("Provide a valid polygon or bounding-box polygon")
    west,south,east,north=region.bounds
    if west < -180 or east > 180 or south < -85 or north > 85:
        raise ValueError("Study geometry must use global WGS84 coordinates within ±180° longitude and ±85° latitude")
    if east-west > 12 or north-south > 12:
        raise ValueError("Choose a local study region up to 12° × 12° anywhere on Earth; split larger or dateline-crossing geometries")
    return region

def cell_weights(lons,lats,geometry):
    """Geodesic intersection areas of native rectilinear cells and user polygon."""
    region=validate_geometry(geometry)
    def edges(a):
        if len(a)<2: raise DataUnavailable("Need native coordinate bounds for a single-cell grid")
        return np.r_[a[0]-(a[1]-a[0])/2,(a[:-1]+a[1:])/2,a[-1]+(a[-1]-a[-2])/2]
    lon_edges,lat_edges=edges(np.asarray(lons)),edges(np.asarray(lats))
    w=np.zeros((len(lats),len(lons)))
    bounds=[]
    for j in range(len(lats)):
        for i in range(len(lons)):
            b=[lon_edges[i],lat_edges[j],lon_edges[i+1],lat_edges[j+1]]
            intersection=region.intersection(box(*b))
            if not intersection.is_empty: w[j,i]=abs(GEOD.geometry_area_perimeter(intersection)[0])
            bounds.append(b)
    return w,bounds

def _load_grid(path,spec):
    options={"mask_and_scale":True,"decode_times":True}
    if spec.get("group"): options["group"]=spec["group"]
    try: ds=xr.open_dataset(path,**options)
    except Exception as exc:
        raise DataUnavailable("Cannot decode native granule with xarray/NetCDF. HDF4 and SWOT swaths require a verified product-specific decoder; no values were guessed.") from exc
    rename={}
    for axis,aliases in {"lat":["latitude","Latitude","YDim"],"lon":["longitude","Longitude","XDim"],"time":["Time"]}.items():
        if axis not in ds.coords:
            found=next((a for a in aliases if a in ds.coords),None)
            if found: rename[found]=axis
    ds=ds.rename(rename)
    if not all(a in ds.coords for a in ("lat","lon","time")):
        raise DataUnavailable("Native coordinate or time metadata missing; refusing guessed axes")
    if ds.lat.ndim!=1 or ds.lon.ndim!=1:
        raise DataUnavailable("Swath/curvilinear data require an explicit regridding adapter, not rectilinear assumptions")
    required=spec.get("fields") or [spec["field"]]
    if any(k not in ds for k in required):
        raise DataUnavailable("Configured field is absent. Available data variables: "+", ".join(list(ds.data_vars)[:35]))
    if spec.get("fields"):
        u,v=(ds[k] for k in required)
        if u.attrs.get("units")!=v.attrs.get("units"): raise DataUnavailable("Vector component units differ")
        field=np.hypot(u,v);field.attrs=dict(u.attrs)
    else: field=ds[spec["field"]]
    if not field.attrs.get("units"):
        raise DataUnavailable("Missing source units; configure a verified decoder")
    for dimension,index in spec.get("selectors",{}).items(): field=field.isel({dimension:index})
    extras=set(field.dims)-{"time","lat","lon"}
    if extras: raise DataUnavailable("Select explicit levels before acquisition: "+str(extras))
    if spec.get("qa_field"):
        if spec["qa_field"] not in ds: raise DataUnavailable("Required QA field missing")
        qa=ds[spec["qa_field"]].astype("uint32")
        field=field.where((qa & spec["qa_mask"])==spec["qa_value"])
    native_unit=field.attrs["units"]
    if spec.get("native_unit") and native_unit!=spec["native_unit"]:
        raise DataUnavailable(f"Expected native units {spec['native_unit']}, received {native_unit}")
    aliases={"°C":{"K","kelvin","C","degC","degree_Celsius","degrees_Celsius"},"kg/kg":{"kg/kg","kg kg-1","kg kg^-1","1"},"kg/m²":{"kg/m2","kg m-2","kg m^-2","kg/m^2"},"m/s":{"m/s","m s-1","m s^-1","m sec-1"},"m":{"m","meter","meters"},"cm":{"cm","centimeter","centimeters"},"mm/hour":{"mm/hr","mm/hour","mm h-1","mm hr-1"},"1":{"1","unitless","dimensionless","None"},"fraction":{"1","fraction","unitless"},"molecules/cm²":{"molec/cm2","molecules/cm2","molecules/cm^2","molecules cm-2"}}
    if spec["unit"] not in aliases or native_unit not in aliases[spec["unit"]]:
        raise DataUnavailable(f"Source units {native_unit!r} do not match the verified output conversion {spec['unit']!r}. Configure and test the product decoder before proceeding.")
    # CF mask/scale is applied by xarray once. Products with packed non-CF
    # encodings must supply a decoder; never apply a second hardcoded scale.
    if "scale_factor" in field.encoding or "add_offset" in field.encoding:
        scale=1.
    else: scale=spec.get("scale",1.)
    offset=spec.get("offset",0.)
    if spec["unit"]=="°C" and native_unit not in {"K","kelvin"}:
        offset=0.;scale=1.
    field=field*scale+offset
    if float(ds.lon.max())>180: field=field.assign_coords(lon=((ds.lon+180)%360)-180)
    return field.sortby("lat").sortby("lon"),native_unit

def acquire_earthdata(variable,product,geometry,start,end,progress=lambda message:None):
    spec=specification(variable,product)
    if spec.get("needs_selection"):
        raise DataUnavailable(spec["needs_selection"]+" Configure NASA_PRODUCT_CONFIG after checking source documentation.")
    versions=discover(spec["short_name"])
    pinned=spec.get("version")
    if not pinned:
        raise DataUnavailable("Pin a verified collection version in NASA_PRODUCT_CONFIG. Discovered versions: "+", ".join(str(v["version"]) for v in versions))
    selected=next((v for v in versions if v["version"]==pinned),None)
    if not selected: raise DataUnavailable("Configured collection version not found in NASA CMR")
    import earthaccess
    auth=earthaccess.login(strategy="environment")
    if not auth.authenticated:
        raise DataUnavailable("Earthdata authentication is not configured. Set EARTHDATA_USERNAME and EARTHDATA_PASSWORD on the server only.")
    region=validate_geometry(geometry)
    granules=earthaccess.search_data(short_name=spec["short_name"],version=pinned,temporal=(start,end),bounding_box=region.bounds,count=int(os.getenv("MAX_GRANULES","600"))+1)
    if not granules: raise DataUnavailable("No NASA granules found for this product, area and period")
    if len(granules)>int(os.getenv("MAX_GRANULES","600")):
        raise DataUnavailable("Acquisition exceeds granule limit. Stage a smaller interval or prebuild a regional cache.")
    progress(f"Downloading {len(granules)} original NASA granules")
    arrays=[];provenance=[]
    with tempfile.TemporaryDirectory(prefix="earthsignal-") as temp:
        for index,granule in enumerate(granules):
            paths=earthaccess.download([granule],local_path=temp,threads=1)
            if not paths: raise DataUnavailable("A granule download failed; refusing incomplete unmarked results")
            path=Path(paths[0]);field,native_unit=_load_grid(path,spec)
            # Include a one-degree halo to retain intersecting edge cells.
            west,south,east,north=region.bounds
            field=field.sel(lat=slice(south-1,north+1),lon=slice(west-1,east+1))
            arrays.append(field.load())
            provenance.append({"granule":granule.get("meta",{}),"links":granule.data_links(),"filename":path.name,"sha256":hashlib.file_digest(path.open("rb"),"sha256").hexdigest()})
            progress(f"Decoded {index+1}/{len(granules)} granules")
            path.unlink(missing_ok=True)
    data=xr.concat(arrays,dim="time").sortby("time")
    if pd.Index(data.time.values).duplicated().any(): raise DataUnavailable("Duplicate granule timestamps; resolve source overlap explicitly")
    # Monthly/daily products have regular nominal sampling. Daily aggregation
    # requires all daily samples in the calendar month; no silent averaging gaps.
    if "daily" in product or spec.get("cadence")=="daily":
        counts=data.notnull().resample(time="MS").sum()
        monthly=data.resample(time="MS").mean()
        expected=xr.DataArray(pd.DatetimeIndex(monthly.time.values).days_in_month,dims="time",coords={"time":monthly.time})
        data=monthly.where(counts==expected)
    w,bounds=cell_weights(data.lon.values,data.lat.values,geometry)
    dates=pd.DatetimeIndex(data.time.values).strftime("%Y-%m-01").tolist()
    if len(set(dates))!=len(dates): raise DataUnavailable("Monthly aggregation is not configured for this source cadence")
    cells=[]
    for j,lat in enumerate(data.lat.values):
        for i,lon in enumerate(data.lon.values):
            if w[j,i]<=0: continue
            vals=data.isel(lat=j,lon=i).values
            cells.append({"lat":float(lat),"lon":float(lon),"bounds":[float(v) for v in bounds[j*len(data.lon)+i]],"values":[float(v) if np.isfinite(v) else None for v in vals],"intersection_area_m2":float(w[j,i])})
    result={"schema_version":1,"source_mode":"native","variable":variable,"product":product,"geometry":geometry,"dates":dates,"cells":cells,"unit":spec["unit"],"source":{"label":selected["title"],"short_name":spec["short_name"],"version":pinned,"collection":selected,"native_units":native_unit,"field":spec.get("field"),"fields":spec.get("fields"),"retrieved_utc":datetime.now(timezone.utc).isoformat(),"granules":provenance,"resolution":spec.get("resolution"),"processing":"CF mask and scale; explicit unit conversion; geodesic polygon-cell intersection weights; no spatial interpolation"}}
    CACHE.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(json.dumps({"variable":variable,"product":product,"geometry":geometry,"start":start,"end":end},sort_keys=True).encode()).hexdigest()
    (CACHE/(digest+".json")).write_text(json.dumps(result,separators=(",",":")),encoding="utf-8")
    return result

def earth_engine_query(collection,band,geometry,start,end,scale,offset=0.,factor=1.,qa_band=None,qa_mask=None,qa_value=0):
    """Explicit EE query, never a guessed substitute for an Earthdata collection.

    Only verified catalog IDs configured by the operator are accepted. Use this
    for MOD08_M3 or a registered collection; not an invented MOD11C3 asset ID.
    """
    import ee
    project=os.getenv("EE_PROJECT")
    if not project: raise DataUnavailable("EE_PROJECT is not configured")
    allowed=json.loads(os.getenv("EE_COLLECTIONS","[]"))
    if collection not in allowed: raise DataUnavailable("Earth Engine collection not verified in EE_COLLECTIONS")
    validate_geometry(geometry)
    ee.Initialize(project=project)
    region=ee.Geometry(geometry)
    images=ee.ImageCollection(collection).filterDate(start,end).filterBounds(region)
    if images.size().getInfo()==0: raise DataUnavailable("Earth Engine returned no images")
    first=ee.Image(images.first())
    if band not in first.bandNames().getInfo(): raise DataUnavailable("Band absent in verified EE collection")
    def transform(image):
        value=image.select(band).multiply(factor).add(offset)
        if qa_band:
            value=value.updateMask(image.select(qa_band).bitwiseAnd(qa_mask).eq(qa_value))
        return value.copyProperties(image,["system:time_start"])
    # Pixel-area weighting (not an unweighted geographic-pixel mean).
    def reduce_image(image):
        area=ee.Image.pixelArea().updateMask(image.mask())
        sums=image.multiply(area).rename("weighted").addBands(area.rename("area")).reduceRegion(reducer=ee.Reducer.sum(),geometry=region,scale=scale,maxPixels=100000000)
        total=ee.Number(sums.get("area"))
        return ee.Feature(None,{"date":image.date().format("YYYY-MM-dd"),"value":ee.Algorithms.If(total.gt(0),ee.Number(sums.get("weighted")).divide(total),None),"valid_area_m2":total})
    transformed=images.map(transform)
    records=ee.FeatureCollection(transformed.toList(transformed.size()).map(lambda item: reduce_image(ee.Image(item)))).getInfo()["features"]
    return {"records":[f["properties"] for f in records],"source":{"provider":"NASA via Google Earth Engine","collection":collection,"band":band,"scale_m":scale,"region":geometry,"start":start,"end":end,"retrieved_utc":datetime.now(timezone.utc).isoformat()},"map_query":"Request tiles separately for the same filtered collection; do not use unrelated imagery."}

def earth_engine_tiles(collection,band,geometry,start,end,months,minimum,maximum,palette,scale=1.,offset=0.):
    import ee
    if collection not in json.loads(os.getenv("EE_COLLECTIONS","[]")): raise DataUnavailable("Unverified EE collection")
    if not os.getenv("EE_PROJECT"): raise DataUnavailable("EE_PROJECT is not configured")
    validate_geometry(geometry);ee.Initialize(project=os.environ["EE_PROJECT"])
    images=ee.ImageCollection(collection).filterDate(start,end)
    images=images.map(lambda i:i.set("calendar_month",i.date().get("month"))).filter(ee.Filter.inList("calendar_month",months))
    layer=images.select(band).mean().multiply(scale).add(offset).clip(ee.Geometry(geometry))
    token=layer.getMapId({"min":minimum,"max":maximum,"palette":palette})
    return {"tile_url":token["tile_fetcher"].url_format,"aggregation":"mean of selected source images","start":start,"end":end,"months":months,"collection":collection,"band":band}
