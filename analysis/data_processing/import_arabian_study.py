from pathlib import Path
import json,zipfile,io,hashlib,struct,zlib
import pandas as pd,numpy as np
from scipy.stats import linregress,false_discovery_control,pearsonr
from scipy.signal import detrend
import pymannkendall as mk
ROOT=Path(__file__).resolve().parents[2];ARCHIVE=ROOT/'data/processed/study/frontend_data.zip';SPEC=ROOT/'data/processed/study/integration-spec.md';OUT=ROOT/'data/processed/study';OUT.mkdir(parents=True,exist_ok=True)
VARIABLES=[{'id':'TEMP_C','name':'Air temperature','unit':'°C','annual_unit':'°C','definition':'Two-meter air temperature, reported in Celsius.','source':'M2TMNXSLV'},{'id':'RH','name':'Relative humidity','unit':'%','annual_unit':'%','definition':'Relative humidity derived from temperature and dewpoint, according to the supplied study documentation.','source':'M2TMNXSLV'},{'id':'WIND_SPEED','name':'Wind speed','unit':'m/s','annual_unit':'m/s','definition':'Ten-meter wind-speed magnitude derived from U10M and V10M, according to the supplied documentation.','source':'M2TMNXSLV'},{'id':'GWETROOT','name':'Root-zone soil wetness','unit':'dimensionless','annual_unit':'dimensionless','definition':'Relative soil wetness in the root zone; not groundwater storage or absolute water depth.','source':'M2TMNXLND'},{'id':'GWETTOP','name':'Topsoil wetness','unit':'dimensionless','annual_unit':'dimensionless','definition':'Surface-layer relative soil wetness; not a water-level measurement.','source':'M2TMNXLND'},{'id':'PRECTOT_MM_MONTH','name':'Precipitation · PRECTOT','unit':'mm/month','annual_unit':'mm/year','definition':'PRECTOT-derived monthly precipitation total. Annual CSV values sum the twelve monthly totals.','source':'M2TMNXFLX'},{'id':'PRECTOTCORR_MM_MONTH','name':'Corrected precipitation · PRECTOTCORR','unit':'mm/month','annual_unit':'mm/year','definition':'PRECTOTCORR-derived monthly precipitation total, separate from PRECTOT and from POWER mean rates. Annual CSV values are yearly totals.','source':'M2TMNXFLX'},{'id':'DUST_UG_M3','name':'Total surface dust','unit':'µg/m³','annual_unit':'µg/m³','definition':'Dust surface mass concentration; not optical depth or a count of dust storms.','source':'M2TMNXAER'},{'id':'FINE_DUST_UG_M3','name':'Fine surface dust','unit':'µg/m³','annual_unit':'µg/m³','definition':'Fine dust mass concentration from DUSMASS25; not total atmospheric PM2.5 across all species.','source':'M2TMNXAER'}]
REGIONS=[{'id':'Northwest','name':'Northwest','bbox':[34,20,43,32]},{'id':'North_Central','name':'North Central','bbox':[43,20,50,32]},{'id':'Northeast','name':'Northeast','bbox':[50,20,60,32]},{'id':'Southwest','name':'Southwest','bbox':[34,12,47,20]},{'id':'Southeast','name':'Southeast','bbox':[47,12,60,20]}]
EXPECTED={'annual_trends_land_weighted':26,'correlation_significance':9,'regional_annual_analysis':130,'regional_correlation_analysis':25,'regional_linear_trends':45,'regional_mann_kendall_sen':45,'regional_monthly_analysis':1560,'regional_monthly_averages_land_weighted':312}
sha=lambda b:hashlib.sha256(b).hexdigest();rawzip=ARCHIVE.read_bytes();rawspec=SPEC.read_bytes();report={'archive_sha256':sha(rawzip),'specification_sha256':sha(rawspec),'files':[],'checks':{},'notes':['Actual archive prefix is frontend_data/, not arabian_earth_trends/. Seven figure names have numeric prefixes; original filenames are preserved.','Annual precipitation values are sums of monthly totals, displayed as mm/year although source column names end in _MM_MONTH. Other annual variables are arithmetic monthly means, not day-weighted means.','The specification reports NASA MERRA-2 sources and cos(latitude) × FRLAND weights; raw granules, grid weights, exact product versions and preprocessing code are not supplied, so upstream NASA extraction and the claimed 1,384-cell spatial audit cannot be independently verified from this package.','Supplied statistical CSVs remain authoritative, with fixed 2000–2025 coverage. Chart-window changes do not recompute these tests.','Zero p-values are retained as reported numerical precision, not interpreted as proof of zero probability.']};frames={};figures=[]
with zipfile.ZipFile(io.BytesIO(rawzip)) as z:
 assert z.testzip() is None
 for info in z.infolist():
  if info.is_dir():continue
  p=Path(info.filename);assert not p.is_absolute() and '..' not in p.parts and len(p.parts)==3 and p.parts[0]=='frontend_data'
  assert p.parts[1] in ['datasets','figures'] and info.file_size<2000000
  b=z.read(info);dest=(ROOT/'data/figures/arabian-dust'/p.name) if p.parts[1]=='figures' else OUT/Path(*p.parts[1:]);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
  entry={'path':Path(*p.parts[1:]).as_posix(),'bytes':len(b),'sha256':sha(b)}
  if p.suffix=='.csv':
   f=pd.read_csv(io.BytesIO(b),float_precision='round_trip');frames[p.stem]=f;assert len(f)==EXPECTED[p.stem];assert not f.isna().any().any();assert not f.duplicated().any()
   entry.update(rows=len(f),columns=list(f),types={c:str(t) for c,t in f.dtypes.items()},missing_values=int(f.isna().sum().sum()),duplicate_rows=int(f.duplicated().sum()))
  elif p.suffix=='.png':
   assert b[:8]==b'\x89PNG\r\n\x1a\n';pos=8;idat=b''
   while pos<len(b):
    n=struct.unpack('>I',b[pos:pos+4])[0];kind=b[pos+4:pos+8];part=b[pos+8:pos+8+n];crc=struct.unpack('>I',b[pos+8+n:pos+12+n])[0];assert zlib.crc32(kind+part)&0xffffffff==crc
    if kind==b'IHDR':entry.update(width=struct.unpack('>I',part[:4])[0],height=struct.unpack('>I',part[4:8])[0])
    if kind==b'IDAT':idat+=part
    pos+=12+n
   zlib.decompress(idat);entry['png_crc_and_decompression']='passed';figures.append(entry)
  else:raise ValueError('Unexpected archive file '+str(p))
  report['files'].append(entry)
assert len(frames)==8 and len(figures)==8
keys={'regional_monthly_analysis':['region','yearmonth'],'regional_annual_analysis':['region','year'],'regional_monthly_averages_land_weighted':['yearmonth'],'annual_trends_land_weighted':['year'],'regional_linear_trends':['Region','Variable'],'regional_mann_kendall_sen':['Region','Variable'],'regional_correlation_analysis':['Region','Relationship'],'correlation_significance':['Relationship']}
for name,f in frames.items():
 assert not f.duplicated(keys[name]).any()
 if 'region' in f or 'Region' in f:assert set(f['region' if 'region' in f else 'Region'])=={r['id'] for r in REGIONS}
 for col in f.select_dtypes(include='number'):assert np.isfinite(f[col]).all()
for mname,aname in [('regional_monthly_analysis','regional_annual_analysis'),('regional_monthly_averages_land_weighted','annual_trends_land_weighted')]:
 m,a=frames[mname],frames[aname];group=['region','year'] if 'region' in m else ['year']
 for _,s in m.groupby('region') if 'region' in m else [('study',m)]:assert sorted(s.yearmonth)==[y*100+mo for y in range(2000,2026) for mo in range(1,13)]
 for v in VARIABLES:
  c=v['id'];g=m.groupby(group)[c].agg('sum' if c.startswith('PRECTOT') else 'mean');assert np.allclose(g,a.set_index(group)[c].reindex(g.index),rtol=1e-12,atol=1e-12)
report['checks']['core_coverage']='312 consecutive months, five regional panels, 130 region-years, no missing or duplicate keys; 2000–2025.'
report['checks']['annual_aggregation']='All nine variables reproduce supplied annual values: monthly sum for precipitation; arithmetic monthly mean otherwise.'
a=frames['regional_annual_analysis'];t=frames['regional_linear_trends'];k=frames['regional_mann_kendall_sen'];errors={'ols':0.,'hamed_rao_p':0.,'sen_slope':0.,'correlation_r':0.}
for _,r in t.iterrows():
 s=a[a.region==r.Region];q=linregress(s.year,s[r.Variable]);errors['ols']=max(errors['ols'],abs(q.slope*10-r.Change_per_decade));assert np.isclose(q.slope*10,r.Change_per_decade,atol=1e-12)
for _,r in k.iterrows():
 s=a[a.region==r.Region];q=mk.hamed_rao_modification_test(s[r.Variable]);errors['hamed_rao_p']=max(errors['hamed_rao_p'],abs(q.p-r.MK_p_value));errors['sen_slope']=max(errors['sen_slope'],abs(q.slope-r.Sen_slope_per_year));assert np.isclose(q.p,r.MK_p_value,atol=1e-12);assert np.isclose(q.slope,r.Sen_slope_per_year,atol=1e-12)
assert np.allclose(false_discovery_control(k.MK_p_value),k.FDR_p_value,atol=1e-12);assert np.array_equal(k.FDR_significant,k.FDR_p_value<.05)
for regional in [True,False]:
 m=frames['regional_monthly_analysis' if regional else 'regional_monthly_averages_land_weighted'];c=frames['regional_correlation_analysis' if regional else 'correlation_significance'];pc='FDR_p_value' if regional else 'Multiple-test p-value';p='Autocorrelation_adjusted_p' if regional else 'Adjusted p-value';assert np.allclose(false_discovery_control(c[p]),c[pc],atol=1e-12)
 if regional:assert np.array_equal(c.Significant,c[pc]<.05)
 for _,r in c.iterrows():
  x,y=r.Relationship.split(' vs ');s=(m[m.region==r.Region] if regional else m).sort_values('yearmonth');transform=lambda key:detrend((s[key]-s.groupby('month')[key].transform('mean')).to_numpy());rr=pearsonr(transform(x),transform(y)).statistic;errors['correlation_r']=max(errors['correlation_r'],abs(rr-r['Pearson_r' if regional else 'Pearson r']));assert np.isclose(rr,r['Pearson_r' if regional else 'Pearson r'],atol=1e-12)
report['checks']['statistical_crosscheck']=errors;report['checks']['fdr']='BH adjusted p-values reproduce all 45 trend tests, 25 regional relationships and 9 study-wide relationships; supplied boolean flags match q < 0.05.'
report['checks']['variable_ranges']={v['id']:{'min':float(frames['regional_monthly_analysis'][v['id']].min()),'max':float(frames['regional_monthly_analysis'][v['id']].max())} for v in VARIABLES}
manifest={'schema_version':1,'id':'arabian-dust-climate','title':'Arabian Peninsula Dust and Climate Study','period':{'start':'2000-01','end':'2025-12','years':[2000,2025]},'scope':'Supplied pre-processed regional study; fixed analytical regions only, no arbitrary-area queries.','provenance_status':'NASA MERRA-2 attribution and spatial processing are reported in the accompanying specification; original granules and upstream processing code are not included. Internal table consistency has been independently checked.','collections':[{'id':c,'url':'https://cmr.earthdata.nasa.gov/search/collections.json?short_name='+c} for c in ['M2TMNXSLV','M2TMNXFLX','M2TMNXLND','M2TMNXAER','M2C0NXASM']],'static_land_fraction':'M2C0NXASM / FRLAND','weighting':'cos(latitude) × FRLAND, as reported by the supplied specification; not recomputed from raw grids.','annual_aggregation':'Arithmetic mean of 12 monthly values, except PRECTOT and PRECTOTCORR annual totals sum 12 monthly totals.','statistics_scope':'Supplied 2000–2025 statistical results; not recomputed by chart-window controls.','methods':['Annual ordinary least-squares regression','Hamed–Rao modified Mann–Kendall and Sen slope','Monthly calendar-climatology removal then OLS detrending for correlations','Approximate lag-1 effective-sample-size adjustment','Benjamini–Hochberg FDR correction; significance q < 0.05'],'alpha':.05,'variables':VARIABLES,'regions':REGIONS,'files':report['files'],'archive':{'name':ARCHIVE.name,'url':'frontend_data.zip','sha256':sha(rawzip)},'specification':{'name':SPEC.name,'url':'integration-spec.md','sha256':sha(rawspec)},'references':[{'title':'NASA MERRA-2 citation guidance','url':'https://gmao.gsfc.nasa.gov/gmao-products/merra-2/citing-merra-2-data_merra-2/'},{'title':'NASA MERRA-2 FAQ and variable interpretation','url':'https://gmao.gsfc.nasa.gov/gmao-products/merra-2/faq_merra-2/'}],'limitations':report['notes']}
def records(f):return json.loads(f.to_json(orient='records',double_precision=15))
data={'schema_version':1,'monthly':records(frames['regional_monthly_analysis']),'annual':records(frames['regional_annual_analysis']),'study_monthly':records(frames['regional_monthly_averages_land_weighted']),'study_annual':records(frames['annual_trends_land_weighted']),'linear':records(t),'mk':records(k),'correlations':records(frames['regional_correlation_analysis']),'study_correlations':records(frames['correlation_significance'])}
# pandas float JSON formatting rounds digits; use Python's round-trip serializer instead.
for key,name in [('monthly','regional_monthly_analysis'),('annual','regional_annual_analysis'),('study_monthly','regional_monthly_averages_land_weighted'),('study_annual','annual_trends_land_weighted'),('linear','regional_linear_trends'),('mk','regional_mann_kendall_sen'),('correlations','regional_correlation_analysis'),('study_correlations','correlation_significance')]:data[key]=frames[name].to_dict(orient='records')
data_bytes=json.dumps(data,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8');manifest['data']={'url':'data.json','sha256':sha(data_bytes)}
for name,value in [('manifest.json',manifest),('data.json',data),('validation-report.json',report)]: (OUT/name).write_text(json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')),encoding='utf-8')
(OUT/'frontend_data.zip').write_bytes(rawzip);(OUT/'integration-spec.md').write_bytes(rawspec)
lines=['# Arabian Peninsula study validation','',f'Archive SHA-256: `{sha(rawzip)}`','',*['- '+n for n in report['notes']],'','## Files','',*['- '+x['path']+': '+str(x.get('rows',str(x.get('width'))+' × '+str(x.get('height'))))+'; SHA-256 '+x['sha256'] for x in report['files']],'','## Checks','',json.dumps(report['checks'],indent=2)]
(ROOT/'STUDY_VALIDATION.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('Validated and imported',len(report['files']),'files;',len(data['monthly']),'region-month records; errors',errors)
