// Empty template only. Never rebuild a populated tracker with this script.
import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const output = process.argv[2];
if (!output) throw new Error('Usage: node build_tracker.mjs OUTPUT.xlsx [QA_DIRECTORY] [CONFIG.json]');
try { await fs.access(output); throw new Error('Output exists. Choose a new file; populated workbooks must be edited in place.'); }
catch (e) { if (e.code !== 'ENOENT') throw e; }
const qaDir = process.argv[3];
const configPath=process.argv[4]||path.join(path.dirname(output),'config.json');
const config=JSON.parse(await fs.readFile(configPath,'utf8'));
if(config.onboarding_status&&config.onboarding_status!=='directions_confirmed') throw new Error('Confirm search directions before building the tracker');
const categories=config.categories;
if(!Array.isArray(categories)||!categories.length||categories.some(c=>typeof c!=='string'||!c.trim())||new Set(categories.map(c=>c.toLowerCase())).size!==categories.length) throw new Error('Unique confirmed category names required in config');
const categoryEnd=12+categories.length, priorityHeader=categoryEnd+3, priorityFirst=priorityHeader+1;
const monthHeader=priorityHeader+6, periodFirst=monthHeader+1, overviewLast=periodFirst+29;
const wb = Workbook.create();
const overview = wb.worksheets.add('Overview');
const search = wb.worksheets.add('Search');
const apps = wb.worksheets.add('Applications');
const statuses = ['Draft','Ready','Applied','Assessment','Interview','Offer','Rejected','Withdrawn','No response (inferred)','On hold'];
const headers = ['Application ID','Company','Job title','Category','Priority','Status','Applied date','Advert URL','Location','Next action','Due date','First progressed date','Updated date','Notes','Requisition ID','Search match'];
const first = 6, last = 1005;
const ref = col => `Applications!$${col}$${first}:$${col}$${last}`;
const dates = ref('G');
const cohort = `${dates},">="&$B$4,${dates},"<"&$D$4`;

function base(sheet, range) {
  sheet.showGridLines = false;
  sheet.getRange(range).format.font = {name:'Arial',size:11,color:'#243044'};
  sheet.getRange(range).format.rowHeight = 24;
  sheet.getRange(range).format.verticalAlignment = 'center';
}
function title(sheet,text) {
  sheet.getRange('A2').values = [[text]];
  sheet.getRange('A2').format.font = {name:'Arial',size:16,bold:true,color:'#243044'};
  sheet.getRange('A2:H2').format.rowHeight = 30;
  sheet.getRange('A3:H3').format.borders = {bottom:{style:'thin',color:'#CBD5E1'}};
}
function head(sheet,range) {
  sheet.getRange(range).format.fill = '#263D60';
  sheet.getRange(range).format.font = {name:'Arial',size:11,bold:true,color:'#FFFFFF'};
  sheet.getRange(range).format.wrapText = true;
  sheet.getRange(range).format.horizontalAlignment = 'center';
  sheet.getRange(range).format.rowHeight = 34;
}
base(overview,`A1:H${overviewLast}`); base(search,'A1:H21'); base(apps,`A1:P${last}`);
overview.tabColor = '#263D60';
title(overview,'Application overview'); title(search,'Find an application'); title(apps,'Applications');
overview.getRange('A4').values = [['From']]; overview.getRange('C4').values = [['Until (exclusive)']];
overview.getRange('B4').values = [[new Date('2026-10-01T00:00:00Z')]];
overview.getRange('D4').values = [[new Date('2026-11-01T00:00:00Z')]];
overview.getRange('B4').setNumberFormat('dd mmm yyyy'); overview.getRange('D4').setNumberFormat('dd mmm yyyy');
overview.getRange('B4').format.fill = '#FFF2CC'; overview.getRange('D4').format.fill = '#FFF2CC';
overview.getRange('F4').values = [['Edit yellow dates to choose the application cohort.']];
overview.getRange('A6:H6').values = [['Applications','Progressed','Conversion','Rejected','Rejection rate','Offers','No response (inferred)','Drafts / ready']];
head(overview,'A6:H6');
overview.getRange('A7:H7').formulas = [[
  `=COUNTIFS(${cohort})`, `=COUNTIFS(${cohort},${ref('L')},">0")`,
  '=IF(A7=0,"n.a.",B7/A7)',`=COUNTIFS(${cohort},${ref('F')},"Rejected")`,
  '=IF(A7=0,"n.a.",D7/A7)',`=COUNTIFS(${cohort},${ref('F')},"Offer")`,
  `=COUNTIFS(${cohort},${ref('F')},"No response (inferred)")`,
  `=COUNTIF(${ref('F')},"Draft")+COUNTIF(${ref('F')},"Ready")`
]];
overview.getRange('C7').setNumberFormat('0.0%'); overview.getRange('E7').setNumberFormat('0.0%');
overview.getRange('A7:H7').format.rowHeight = 30;
overview.getRange('A7:H7').format.horizontalAlignment = 'right';
overview.getRange('A9').values = [['Conversion counts the first assessment, interview or offer, including later rejections.']];
overview.getRange('A10').values = [['Drafts / ready shows all current drafts. Other results use applied dates in the selected cohort.']];
overview.getRange('A9:H10').format.font.italic = true;
overview.getRange('A12:F12').values = [['Category','Applications','Progressed','Conversion','Rejected','Rejection rate']]; head(overview,'A12:F12');
for (let i=0;i<categories.length;i++) {
  const r=13+i; overview.getRange(`A${r}`).values=[[categories[i]]];
  overview.getRange(`B${r}:F${r}`).formulas=[[
    `=COUNTIFS(${cohort},${ref('D')},A${r})`,
    `=COUNTIFS(${cohort},${ref('D')},A${r},${ref('L')},">0")`,
    `=IF(B${r}=0,"n.a.",C${r}/B${r})`,
    `=COUNTIFS(${cohort},${ref('D')},A${r},${ref('F')},"Rejected")`,
    `=IF(B${r}=0,"n.a.",E${r}/B${r})`
  ]];
}
overview.getRange(`D13:D${categoryEnd}`).setNumberFormat('0.0%'); overview.getRange(`F13:F${categoryEnd}`).setNumberFormat('0.0%');
overview.getRange(`B13:F${categoryEnd}`).format.horizontalAlignment='right';
overview.getRange(`A13:A${categoryEnd}`).format.wrapText=true;
overview.getRange(`A${priorityHeader}:F${priorityHeader}`).values=[['Priority','Applications','Progressed','Conversion','Rejected','Rejection rate']];head(overview,`A${priorityHeader}:F${priorityHeader}`);
for (let r=priorityFirst;r<=priorityFirst+2;r++) {
  overview.getRange(`A${r}`).values=[[r-priorityFirst+3]];
  overview.getRange(`B${r}:F${r}`).formulas=[[
    `=COUNTIFS(${cohort},${ref('E')},A${r})`,
    `=COUNTIFS(${cohort},${ref('E')},A${r},${ref('L')},">0")`,
    `=IF(B${r}=0,"n.a.",C${r}/B${r})`,
    `=COUNTIFS(${cohort},${ref('E')},A${r},${ref('F')},"Rejected")`,
    `=IF(B${r}=0,"n.a.",E${r}/B${r})`]];
}
overview.getRange(`D${priorityFirst}:D${priorityFirst+2}`).setNumberFormat('0.0%'); overview.getRange(`F${priorityFirst}:F${priorityFirst+2}`).setNumberFormat('0.0%');
overview.getRange(`B${priorityFirst}:F${priorityFirst+2}`).format.horizontalAlignment='right';
overview.getRange(`A${monthHeader}:C${monthHeader}`).values=[['Month','Until (exclusive)','Applications']];head(overview,`A${monthHeader}:C${monthHeader}`);
overview.getRange(`E${monthHeader}:G${monthHeader}`).values=[['Semiweekly from','Until (exclusive)','Applications']];head(overview,`E${monthHeader}:G${monthHeader}`);
overview.getRange(`E${monthHeader-1}`).values=[['Monday–Wednesday and Thursday–Sunday']];
for (let i=0;i<12;i++) {
  const r=periodFirst+i;
  overview.getRange(`A${r}`).values=[[new Date(Date.UTC(2026,9+i,1))]];
  overview.getRange(`B${r}`).values=[[new Date(Date.UTC(2026,10+i,1))]];
  overview.getRange(`C${r}`).formulas=[[`=COUNTIFS(${dates},">="&A${r},${dates},"<"&B${r})`]];
}
const startDate = new Date('2026-10-05T00:00:00Z');
for (let i=0;i<24;i++) {
  const r=periodFirst+i, offset=Math.floor(i/2)*7+(i%2?3:0), length=i%2?4:3;
  overview.getRange(`E${r}:F${r}`).values=[[
    new Date(startDate.getTime()+offset*86400000),new Date(startDate.getTime()+(offset+length)*86400000)]];
  overview.getRange(`G${r}`).formulas=[[`=COUNTIFS(${dates},">="&E${r},${dates},"<"&F${r})`]];
}
overview.getRange(`A${periodFirst}:B${periodFirst+11}`).setNumberFormat('mmm yyyy'); overview.getRange(`E${periodFirst}:F${periodFirst+23}`).setNumberFormat('dd mmm yyyy');
overview.getRange(`A${periodFirst+26}`).values=[['Monthly and semiweekly tables show application volumes. Extend date rows for later periods.']];
overview.getRange(`A${periodFirst+27}`).values=[['Recent cohorts are incomplete. No response is separate from confirmed rejection.']];
overview.getRange(`A${overviewLast}`).values=[['Applications and calculations are prepared for 1,000 records. Extend ranges together before adding more.']];
overview.getRange(`A1:A${overviewLast}`).format.columnWidth=Math.max(38,Math.min(58,Math.max(...categories.map(c=>c.length))+2));
overview.getRange(`A13:F${categoryEnd}`).format.autofitRows();
overview.getRange(`B1:G${overviewLast}`).format.columnWidth=18;
overview.getRange(`H1:H${overviewLast}`).format.columnWidth=20;

search.getRange('A4').values=[['Search text']]; search.getRange('B4').values=[['']];search.getRange('B4:D4').format.fill='#FFF2CC';
search.getRange('A6').values=[['Matching applications']];search.getRange('B6').formulas=[[`=SUM(${ref('P')})`]];
search.getRange('A8').values=[['First match row']];search.getRange('B8').formulas=[[`=IF(B6=0,"",MATCH(1,${ref('P')},0))`]];
const detail=[['Application ID','A'],['Company','B'],['Job title','C'],['Status','F'],['Advert URL','H'],['Next action','J']];
for(let i=0;i<detail.length;i++) {
  const r=10+i;search.getRange(`A${r}`).values=[[detail[i][0]]];
  search.getRange(`B${r}`).formulas=[[`=IF($B$6=0,"",INDEX(${ref(detail[i][1])},$B$8))`]];
}
search.getRange('A18').values=[['For all results, open Applications and filter Search match to 1.']];
search.getRange('A19').values=[['Use Category filters for Operations or another role family.']];
search.getRange('A20').values=[['Blank search includes all records. Excel Find also searches this workbook.']];
search.getRange('A1:A21').format.columnWidth=30; search.getRange('B1:B21').format.columnWidth=68;
search.getRange('C1:H21').format.columnWidth=12;
search.getRange('B10:B15').format.wrapText=true;search.getRange('A10:B15').format.rowHeight=38;
apps.getRange('A4').values=[['Enter one row per role. Applied date stays blank until submission. Filter using the header buttons.']];
apps.getRange('A5:P5').values=[headers];head(apps,'A5:P5');
const table=apps.tables.add(`A5:P${last}`,true,'ApplicationsTable');table.showFilterButton=true;table.showBandedColumns=false;
apps.getRange(`D${first}:D${last}`).dataValidation={rule:{type:'list',formula1:`INDIRECT("'Overview'!$A$13:$A$${categoryEnd}")`}};
apps.getRange(`F${first}:F${last}`).dataValidation={rule:{type:'list',values:statuses}};
apps.dataValidations.add({range:`E${first}:E${last}`,rule:{type:'whole',operator:'between',formula1:3,formula2:5}});
for(const c of ['G','K','L','M']) apps.getRange(`${c}${first}:${c}${last}`).setNumberFormat('dd mmm yyyy');
apps.getRange(`P${first}`).formulas=[[`=IF(A${first}="",0,IF(Search!$B$4="",1,IF(ISNUMBER(SEARCH(Search!$B$4,B${first}&" "&C${first}&" "&D${first}&" "&N${first}&" "&O${first})),1,0)))`]];
apps.getRange(`P${first}:P${last}`).fillDown();
apps.getRange(`E${first}:E${last}`).conditionalFormats.add('cellIs',{operator:'greaterThanOrEqual',formula:4,format:{fill:'#E4EDF8'}});
apps.getRange(`F${first}:F${last}`).conditionalFormats.add('containsText',{text:'Rejected',format:{fill:'#FCE8E6',font:{color:'#9A2B28'}}});
apps.getRange(`K${first}:K${last}`).conditionalFormats.addCustom(`AND(ISNUMBER(K${first}),K${first}<TODAY(),$A${first}<>"",$F${first}<>"Rejected",$F${first}<>"Withdrawn",$F${first}<>"Offer")`,{fill:'#FFF2CC'});
const widths=[20,26,38,37,10,25,18,45,25,42,18,22,18,50,22,17];
for(let i=0;i<widths.length;i++) apps.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}${last}`).format.columnWidth=widths[i];
apps.freezePanes.freezeRows(5);apps.freezePanes.freezeColumns(2);

// Representative input changes in memory; no fictional applications are delivered.
apps.getRange('A6:O8').values=[
 ['TEST-1','Example A','Example role',categories[0],4,'Rejected',new Date('2026-10-02'),'https://example.com/jobs/1','London','','',new Date('2026-10-05'),'','','R1'],
 ['TEST-2','Example B','Other role',categories.at(-1),3,'Applied',new Date('2026-10-03'),'https://example.com/jobs/2','London','','','','','','R2'],
 ['TEST-3','Example C','Draft role',categories[0],5,'Draft','','https://example.com/jobs/3','London','','','','','','R3']
];
search.getRange('B4').values=[['Example A']];wb.recalculate();
const metrics=overview.getRange('A7:H7').values[0];
if(metrics[0]!==2||metrics[1]!==1||metrics[2]!==0.5||metrics[3]!==1||metrics[4]!==0.5||metrics[7]!==1) throw new Error('Cohort metrics failed '+JSON.stringify(metrics));
if(search.getRange('B6').values[0][0]!==1||search.getRange('B10').values[0][0]!=='TEST-1') throw new Error('Search failed');
search.getRange('B4').values=[['no match at all']];wb.recalculate();
if(search.getRange('B6').values[0][0]!==0||search.getRange('B10').values[0][0]!=='') throw new Error('No-match search failed');
apps.getRange('A6:O8').clear({applyTo:'contents'});search.getRange('B4').values=[['']];wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Overview!A6:H7',include:'values,formulas',tableMaxRows:2,tableMaxCols:8,maxChars:1600})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
if(qaDir) {
  await fs.mkdir(qaDir,{recursive:true});
  for(const [sheet,range] of [['Overview',`A1:H${priorityFirst+2}`],['Overview',`A${monthHeader-1}:H${overviewLast}`],['Search','A1:D21'],['Applications','A1:G10'],['Applications','H4:P10']]) {
    const preview=await wb.render({sheetName:sheet,range,scale:1.4,format:'png'});
    await fs.writeFile(path.join(qaDir,`${sheet}-${range.replace(':','-')}.png`),new Uint8Array(await preview.arrayBuffer()));
  }
}
await fs.mkdir(path.dirname(output),{recursive:true});
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
console.log('Exported '+output+'; input-change checks passed; no sample records retained.');
