// Run through the Codex spreadsheet workflow. Input is a private JSON patch list.
import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const [file, patchFile, qaDir, suppliedConfig] = process.argv.slice(2);
if(!file||!patchFile) throw new Error('Usage: node update_tracker.mjs WORKBOOK PATCHES.json [QA_DIRECTORY]');
const patches=JSON.parse(await fs.readFile(patchFile,'utf8'));
if(!Array.isArray(patches)||patches.length===0) throw new Error('Nonempty patch list required');
const original=await fs.readFile(file);
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(file));
const apps=wb.worksheets.getItem('Applications');
const headers=apps.getRange('A5:O5').values[0];
const expected=['Application ID','Company','Job title','Category','Priority','Status','Applied date','Advert URL','Location','Next action','Due date','First progressed date','Updated date','Notes','Requisition ID'];
if(JSON.stringify(headers)!==JSON.stringify(expected)) throw new Error('Template columns changed; adapt and verify the updater before use');
const config=JSON.parse(await fs.readFile(suppliedConfig||path.join(path.dirname(file),'config.json'),'utf8'));
if(config.onboarding_status&&config.onboarding_status!=='directions_confirmed') throw new Error('Confirm search directions before writing applications');
const categories=config.categories;
if(!Array.isArray(categories)||!categories.length) throw new Error('Confirmed categories required');
const workbookCategories=wb.worksheets.getItem('Overview').getRange(`A13:A${12+categories.length}`).values.map(r=>r[0]);
if(JSON.stringify(workbookCategories)!==JSON.stringify(categories)) throw new Error('Config categories and workbook differ; review category migration first');
const statuses=['Draft','Ready','Applied','Assessment','Interview','Offer','Rejected','Withdrawn','No response (inferred)','On hold'];
const existing=apps.getRange('A6:O1005').values;
const used=new Map();
for(let i=0;i<existing.length;i++) if(existing[i][0]) {
  if(used.has(existing[i][0])) throw new Error('Duplicate Application ID in workbook');
  used.set(existing[i][0],i);
}
function asDate(value) {
  if(value===''||value===null||value===undefined) return '';
  if(typeof value==='number') return new Date(Date.UTC(1899,11,30)+value*86400000);
  if(value instanceof Date) return value;
  if(!/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error('Dates must be ISO YYYY-MM-DD');
  const d=new Date(value+'T00:00:00Z');
  if(Number.isNaN(d.getTime())||d.toISOString().slice(0,10)!==value) throw new Error('Invalid calendar date');
  return d;
}
const touched=[];
for(const p of patches) {
  if(!/^APP-[A-Z0-9]{10}$/.test(p.application_id)||!p.source||!p.fields||typeof p.fields!=='object') throw new Error('Patch requires stable ID, source and fields');
  if(Object.hasOwn(p.fields,'Application ID')) throw new Error('ID is immutable');
  let idx=used.get(p.application_id);
  if(idx===undefined) {
    idx=existing.findIndex(r=>!r[0]);
    if(idx<0) throw new Error('1,000-row capacity reached. Extend formulas and validation first.');
    used.set(p.application_id,idx);existing[idx]=Array(15).fill('');existing[idx][0]=p.application_id;
  }
  const row=[...existing[idx]], beforeProgress=asDate(row[11]);
  for(const [key,val] of Object.entries(p.fields)) {
    const col=headers.indexOf(key);
    if(col<1) throw new Error('Unknown editable field: '+key);
    row[col]=[6,10,11,12].includes(col)?asDate(val):val;
    if(typeof row[col]==='string'&&/^[=+@]/.test(row[col])) row[col]="'"+row[col];
  }
  for(const c of [6,10,11,12]) row[c]=asDate(row[c]);
  if(!row[1]||!row[2]||!categories.includes(row[3])||![3,4,5].includes(row[4])||!statuses.includes(row[5])) throw new Error('Company, title, configured category, integer priority 3–5 and valid status required');
  if(['Applied','Assessment','Interview','Offer','Rejected','Withdrawn','No response (inferred)'].includes(row[5])&&!row[6]) throw new Error('Submitted outcomes require a confirmed Applied date');
  if(['Draft','Ready'].includes(row[5])&&row[6]) throw new Error('Draft/Ready cannot have an Applied date');
  if(['Assessment','Interview','Offer'].includes(row[5])&&!row[11]) throw new Error('Progressed status requires first progression date');
  if(row[11]&&(!row[6]||row[11]<row[6])) throw new Error('Progression requires an application date on/before progression');
  if(beforeProgress&&(!row[11]||row[11]>beforeProgress)) throw new Error('Do not erase or move first progression later');
  existing[idx]=row;apps.getRange(`A${idx+6}:O${idx+6}`).values=[row];
  touched.push({id:p.application_id,row:idx+6,source:p.source});
}
wb.recalculate();
const check=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:10},maxChars:1500});
console.log(check.ndjson);
if(qaDir) {
  await fs.mkdir(qaDir,{recursive:true});
  const preview=await wb.render({sheetName:'Applications',range:`A${touched[0].row}:G${touched[0].row}`,scale:1.4,format:'png'});
  await fs.writeFile(path.join(qaDir,'updated-row.png'),new Uint8Array(await preview.arrayBuffer()));
}
// Detect changes made in Excel while this operation was running.
if(!(await fs.readFile(file)).equals(original)) throw new Error('Workbook changed during edit; re-read and retry. No overwrite performed.');
const backupDir=path.join(path.dirname(file),'backups');await fs.mkdir(backupDir,{recursive:true});
const stamp=new Date().toISOString().replace(/[:.]/g,'-');
await fs.writeFile(path.join(backupDir,`Applications-${stamp}.xlsx`),original,{flag:'wx'});
const temp=file+'.'+stamp+'.tmp.xlsx';await(await SpreadsheetFile.exportXlsx(wb)).save(temp);
// Export can take time. Recheck immediately before replacement as well.
if(!(await fs.readFile(file)).equals(original)) {await fs.unlink(temp);throw new Error('Workbook changed during export; preserved current file and backup.');}
await fs.rename(temp,file);
const logDir=path.join(path.dirname(file),'updates');await fs.mkdir(logDir,{recursive:true});
await fs.writeFile(path.join(logDir,stamp+'.json'),JSON.stringify(touched,null,2));
console.log(JSON.stringify({updated:touched,backup_created:true}));
