import {defineConfig} from 'vite';import react from '@vitejs/plugin-react';import tailwindcss from '@tailwindcss/vite';
import {prepareAssets} from './scripts/prepare-assets.mjs';
export default defineConfig(async()=>({publicDir:await prepareAssets(),plugins:[react(),tailwindcss()],build:{outDir:'dist/client',emptyOutDir:true},worker:{format:'es'},server:{proxy:{'/api':'http://127.0.0.1:8000'}}}));
