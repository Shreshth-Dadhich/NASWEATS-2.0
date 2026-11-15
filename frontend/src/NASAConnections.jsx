import React,{useEffect,useState} from 'react';

export default function NASAConnections({product,dataset,onSources}) {
  const [lookup,setLookup]=useState({state:'idle'}),[attempt,setAttempt]=useState(0);
  const short=product.short_name;
  useEffect(()=>{
    const controller=new AbortController();
    setLookup({state:'loading'});
    const query=new URLSearchParams({short_name:short,page_size:'20'});
    fetch('https://cmr.earthdata.nasa.gov/search/collections.json?'+query,{signal:AbortSignal.any([controller.signal,AbortSignal.timeout(30000)])})
      .then(async r=>{if(!r.ok)throw Error('NASA CMR returned HTTP '+r.status);return r.json();})
      .then(json=>{
        if(!Array.isArray(json.feed?.entry))throw Error('NASA CMR returned an unreadable response.');
        const entries=json.feed.entry.filter(e=>e.short_name===short);
        setLookup({state:'ready',entries,checked:new Date().toISOString()});
      }).catch(e=>{if(!controller.signal.aborted)setLookup({state:'error',message:e.message});});
    return()=>controller.abort();
  },[short,attempt]);
  return <div className="nasa-connections">
    <p className="connection-intro">Measurements come from NASA. Imagery is a separate visual layer. EarthSignal is an independent project.</p>
    <article className="connection-row"><span className="connection-dot connected"/><div><h3>NASA POWER</h3><p>Monthly air temperature (T2M), relative humidity (RH2M), mean wind speed (WS10M) and corrected precipitation rate (PRECTOTCORR), derived from MERRA-2. Published record: 1984–2024.</p><span className="connection-status">Public API and verified caches · no API key required</span><a href="https://power.larc.nasa.gov/docs/services/api/temporal/monthly/" target="_blank" rel="noopener">Read the API documentation ↗</a></div></article>
    <article className="connection-row"><span className="connection-dot connected"/><div><h3>NASA MERRA2-GMI</h3><p>Native monthly chemistry-replay grids: reconstructed surface PM2.5, dust optical depth, low-cloud fraction, surface skin temperature, root-zone/topsoil wetness and PRECTOT/PRECTOTCORR precipitation rates. The public archive spans 1980–2019; it is distinct from direct MERRA-2 products. Skin temperature includes land and sea and is not ocean current velocity. Soil wetness uses modeled land-cell validity. Precipitation is mm/day, not the supplied study’s monthly totals. Surface-dust concentrations were not enabled globally because their archive failed the source audit.</p><a href="https://opendap.nccs.nasa.gov/dods/merra2_gmi" target="_blank" rel="noopener">Inspect the NASA monthly archive ↗</a></div></article>
    <article className="connection-row"><span className="connection-dot connected"/><div><h3>NASA GSFC GRACE / GRACE-FO</h3><p>Global equal-area land mascons provide total water-storage anomalies; ocean mascons from the SLA product provide the mass component of sea-level change. Published record: April 2002–June 2026. Mission gaps stay missing. Ocean mass excludes thermal expansion; land storage is not groundwater alone.</p><a href="https://earth.gsfc.nasa.gov/geo/data/grace-mascons" target="_blank" rel="noopener">Inspect the original NASA HDF5 files ↗</a></div></article>
    <article className="connection-row"><span className="connection-dot connected"/><div><h3>NASA Global Water Measurements</h3><p>340 monitored lake and reservoir records, with feature-specific dates. Monthly height anomalies average actual valid satellite overpasses. This is lake-level observation, separate from GRACE water storage.</p><a href="https://earth.gsfc.nasa.gov/gwm/lake/Index" target="_blank" rel="noopener">Inspect NASA’s monitored water bodies ↗</a></div></article>
    <article className="connection-row"><span className={'connection-dot '+(lookup.state==='ready'?'connected':'')}/><div><h3>NASA Earthdata CMR</h3><p>Live collection discovery for <code>{short}</code>. A catalogue match confirms metadata, not access to numerical granules.</p><div role="status">{lookup.state==='loading'?'Querying NASA’s catalogue…':lookup.state==='error'?lookup.message:lookup.state==='ready'?lookup.entries.length+' exact collection matches · checked '+lookup.checked.slice(0,10):''}</div>{lookup.state==='error'&&<button className="quiet-button" onClick={()=>setAttempt(x=>x+1)}>Retry catalogue query</button>}{lookup.entries?.map(entry=><div className="collection-entry" key={entry.id}><strong>{entry.title}</strong><span>Version {entry.version_id} · {entry.id}</span><span>{entry.time_start?.slice(0,10)} — {entry.time_end?.slice(0,10)||'ongoing'}</span></div>)}<a href={'https://cmr.earthdata.nasa.gov/search/collections.json?short_name='+encodeURIComponent(short)} target="_blank" rel="noopener">Open the exact CMR request ↗</a></div></article>
    <article className="connection-row"><span className="connection-dot"/><div><h3>Other native mission products</h3><p>Direct MODIS, GPM, AIRS, OMI, GLDAS, OSCAR currents and Jason / SWOT altimetric height require the configured Python acquisition service, authorized access and validated product decoding. Their exact metrics are not silently replaced by the public alternatives above.</p><span className="connection-status">An Earthdata account alone does not configure the server connection. Tokens stay server-side.</span><a href="https://urs.earthdata.nasa.gov/" target="_blank" rel="noopener">Create or manage Earthdata access ↗</a></div></article>
    <article className="connection-row"><span className="connection-dot connected"/><div><h3>NASA GIBS</h3><p>NASA Blue Marble relief is available in the basemap menu. Esri provides the optional high-detail imagery. Neither basemap supplies the plotted measurements.</p><a href="https://nasa-gibs.github.io/gibs-api-docs/" target="_blank" rel="noopener">Read about NASA GIBS ↗</a></div></article>
    {dataset&&<button className="button-primary" onClick={onSources}>Inspect the measurement source ↗</button>}
  </div>;
}
