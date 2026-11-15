import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createPreviewServer} from './server-core.mjs';
import worker from '../dist/server/index.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),port=Number(process.env.PORT||4176);
createPreviewServer(worker,path.join(root,'dist/client')).listen(port,'127.0.0.1',()=>console.log(`EarthSignal preview: http://127.0.0.1:${port}`));
