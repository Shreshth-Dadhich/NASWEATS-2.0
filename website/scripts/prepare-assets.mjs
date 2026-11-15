import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const website=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const repository=path.resolve(website,'..');
// Public URLs are a compatibility contract. Scientific assets live in data/,
// while this ignored staging directory combines them with website/public/.
export const assetMounts=[
 ['data/processed/cache','cache'],
 ['data/processed/nasa','data'],
 ['data/processed/study','studies/arabian-dust'],
 ['data/figures/arabian-dust','studies/arabian-dust/figures'],
 ['data/processed/catalog-verification.json','catalog-verification.json']
];
export async function prepareAssets(){
 const output=path.resolve(website,'.generated/public');
 if(output!==path.join(website,'.generated','public')||JSON.parse(await fs.readFile(path.join(website,'package.json'),'utf8')).name!=='earthsignal-by-nasweats-2-0')throw Error('Unexpected public asset staging path');
 // Only the verified generated asset staging directory is removed.
 await fs.rm(output,{recursive:true,force:true});
 await fs.mkdir(output,{recursive:true});
 await fs.cp(path.join(website,'public'),output,{recursive:true});
 for(const [source,destination] of assetMounts){
   const target=path.join(output,destination);await fs.mkdir(path.dirname(target),{recursive:true});
   await fs.cp(path.join(repository,source),target,{recursive:true});
 }
 return output;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 console.log('Prepared public assets:',await prepareAssets());
}
