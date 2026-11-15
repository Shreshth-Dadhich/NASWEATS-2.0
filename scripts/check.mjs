import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
for(const test of ['middle_east','polygon_selection','global_spatial','global_export','global_relationship','nasa_connections','relay_v7','arabian_study','study_workbench','study_maps']){
  const r=spawnSync(process.execPath,[`tests/${test}.mjs`],{cwd:root,stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)process.exit(r.status??1);
}
