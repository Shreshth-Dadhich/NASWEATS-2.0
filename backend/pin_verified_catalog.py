"""Pin unambiguous CMR versions; explicitly retain rejected identifiers."""
import json
from pathlib import Path
path=Path('backend/catalog.json');catalog=json.loads(path.read_text(encoding='utf-8'))
verified=json.loads(Path('frontend/public/catalog-verification.json').read_text(encoding='utf-8'))['products']
for family in catalog:
    for p in family['products']:
        hits=verified.get(p['short_name'],{}).get('collections',[])
        if len(hits)==1:p['version']=hits[0]['version']
        if p['short_name']=='MODISA_L3m_SST_Monthly_4km_Daytime_V2019.0':
            p['rejected_identifier']=p['short_name'];p['short_name']='MODIS_AQUA_L3_SST_THERMAL_MONTHLY_4KM_DAYTIME_V2019.0';p['version']='2019.0'
            p['needs_selection']='Verified CMR short name corrected from an invalid adapter identifier. Validate SST quality mask and native field units before enabling acquisition.'
        if p['short_name']=='TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.1_V2':
            p['needs_selection']='Requested identifier has no exact NASA CMR match. Choose the explicitly labeled active RL06.3 V4 alternative; never silently replace versions.'
    if family['id']=='water':family['products'].insert(1,{'id':'grace_active','short_name':'TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4','version':'RL06.3Mv04','field':'lwe_thickness','unit':'cm','scale':1,'offset':0,'start':2002,'resolution':'mascons; output grid is not independent resolution','version_note':'Explicit active alternative to the unmatched requested RL06.1_V2 identifier. Reference baseline and corrections must be read from source attributes.'})
path.write_text(json.dumps(catalog,indent=2,ensure_ascii=False),encoding='utf-8')
