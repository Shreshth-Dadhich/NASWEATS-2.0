from __future__ import annotations
import io, json, os, uuid, csv, zipfile
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from . import nasa_fetcher as nasa
from .stats_engine import analyze

app=FastAPI(title="EarthSignal Global Science API",version="7.0.0")
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("ALLOWED_ORIGINS","http://localhost:4176,http://127.0.0.1:4176").split(","),allow_methods=["GET","POST"],allow_headers=["Content-Type"])
JOBS={}

class AnalysisRequest(BaseModel):
    records:list[dict]=Field(max_length=2000)
    start_year:int=Field(ge=1980,le=2026)
    end_year:int=Field(ge=1980,le=2026)
    season:str="ALL"
    anomaly:bool=False
    confidence:float=.95

class AcquisitionRequest(BaseModel):
    variable:str
    product:str
    geometry:dict
    start:str
    end:str

@app.get("/api/health")
def health():
    return {"status":"ok","earthdata_configured":bool(os.getenv("EARTHDATA_USERNAME") and os.getenv("EARTHDATA_PASSWORD")),"earth_engine_configured":bool(os.getenv("EE_PROJECT")),"native_products_require_pinned_versions":True}

@app.get("/api/catalog")
def catalog(): return nasa.CATALOG

@app.get("/api/discover/{variable}/{product}")
def discovery(variable:str,product:str):
    try:
        spec=nasa.specification(variable,product)
        return {"requested":spec,"collections":nasa.discover(spec["short_name"]),"warning":"Discovery confirms metadata, not data access or scientific suitability. Never silently substitute collection versions."}
    except (ValueError,nasa.DataUnavailable) as e: raise HTTPException(422,str(e))

@app.post("/api/analyze")
def statistics(request:AnalysisRequest):
    try:return analyze(**request.model_dump())
    except ValueError as e:raise HTTPException(422,str(e))

def acquire_job(job_id,request):
    try:
        result=nasa.acquire_earthdata(**request.model_dump(),progress=lambda text:JOBS[job_id].update(message=text))
        JOBS[job_id].update(status="complete",message="Native NASA grid acquired",result=result)
    except Exception as e:
        JOBS[job_id].update(status="failed",message=str(e))

@app.post("/api/acquire",status_code=202)
def acquisition(request:AcquisitionRequest,tasks:BackgroundTasks):
    try:nasa.validate_geometry(request.geometry);nasa.specification(request.variable,request.product)
    except ValueError as e:raise HTTPException(422,str(e))
    if not os.getenv("EARTHDATA_USERNAME") or not os.getenv("EARTHDATA_PASSWORD"):
        raise HTTPException(503,"NASA Earthdata credentials are not configured on this backend. No native product was substituted.")
    job_id=str(uuid.uuid4());JOBS[job_id]={"status":"queued","message":"Searching NASA CMR"}
    tasks.add_task(acquire_job,job_id,request)
    return {"job_id":job_id}

@app.get("/api/jobs/{job_id}")
def job(job_id:str):
    if job_id not in JOBS:raise HTTPException(404,"Unknown acquisition job")
    return JOBS[job_id]

@app.post("/api/export")
def export(request:AnalysisRequest):
    result=statistics(request)
    output=io.BytesIO()
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("analysis.json",json.dumps(result,indent=2,allow_nan=False))
        text=io.StringIO(newline="");writer=csv.DictWriter(text,fieldnames=["date","value"],extrasaction="ignore");writer.writeheader();writer.writerows(request.records)
        archive.writestr("monthly.csv",text.getvalue())
        archive.writestr("request.json",request.model_dump_json(indent=2))
        archive.writestr("README.txt","This API export contains supplied analysis inputs, not independently verified NASA provenance. Use the acquisition/source manifest with this archive. No source attribution is inferred from client-provided values.")
    output.seek(0)
    return StreamingResponse(output,media_type="application/zip",headers={"Content-Disposition":"attachment; filename=earthsignal-analysis.zip"})
