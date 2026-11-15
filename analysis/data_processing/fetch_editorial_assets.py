from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,re,hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'website/public/fonts';OUT.mkdir(parents=True,exist_ok=True)
url='https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&family=Instrument+Serif:ital@0;1&display=swap'
r=requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'},timeout=40);r.raise_for_status()
faces=re.findall(r'/\* latin \*/\s*(@font-face\s*\{[\s\S]*?\})',r.text);assert len(faces)==8
sources={};css=[];preloads={}
for face in faces:
 family=re.search("font-family: '([^']+)'",face)[1];weight=re.search(r'font-weight: (\d+)',face)[1];style=re.search(r'font-style: (\w+)',face)[1];source=re.search(r'url\((https://fonts.gstatic.com/[^)]+\.woff2)\)',face)[1]
 name=family.lower().replace(' ','-')+'-'+hashlib.sha256(source.encode()).hexdigest()[:10]+'.woff2';sources[source]=(name,family)
 css.append(face.replace(source,'/fonts/'+name))
 if style=='normal' and weight=='400':preloads[family]='/fonts/'+name
records=[]
def download(item):
 source,(name,family)=item;p=OUT/name
 if not p.exists():q=requests.get(source,timeout=30);q.raise_for_status();p.write_bytes(q.content)
 raw=p.read_bytes();assert raw[:4]==b'wOF2'
 return {'family':family,'file':name,'source':source,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
with ThreadPoolExecutor(4) as pool:records=list(pool.map(download,sources.items()))
for family,folder in [('IBM Plex Sans','ibmplexsans'),('IBM Plex Mono','ibmplexmono'),('Instrument Serif','instrumentserif')]:
 u='https://raw.githubusercontent.com/google/fonts/main/ofl/'+folder+'/OFL.txt';q=requests.get(u,timeout=30);q.raise_for_status();(OUT/(folder+'-OFL.txt')).write_bytes(q.content)
(ROOT/'website/src/editorial-fonts.css').write_text('/* Self-hosted Latin WOFF2 subsets from Google Fonts; licenses in /fonts. */\n'+'\n'.join(css)+'\n',encoding='utf-8')
(OUT/'manifest.json').write_text(json.dumps({'css_source':url,'fonts':records,'preloads':preloads},indent=2)+'\n')
p=ROOT/'website/index.html';html=p.read_text();html=html.replace('content="#182e3c"','content="#0a1220"');html=re.sub(r'<link\s+rel="preload"\s+href="/fonts/[^">]+"[^>]*>', '', html);html=html.replace('</head>',''.join(f'<link rel="preload" href="{preloads[f]}" as="font" type="font/woff2" crossorigin>' for f in ['IBM Plex Sans','Instrument Serif'])+'</head>');p.write_text(html)
print('Self-hosted',len(records),'font files;',sum(r['bytes'] for r in records),'bytes total; licensed OFL assets preserved.')
