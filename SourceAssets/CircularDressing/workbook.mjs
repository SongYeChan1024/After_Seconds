import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const here=path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/,'$1'));
const source=JSON.parse(await fs.readFile(path.join(here,'workbook_source.json'),'utf8'));
const delivery='C:/Users/503-26/Documents/Codex/2026-11-06/dl/outputs/after_seconds_reviewed/AfterSeconds_프랍환경_제작목록.xlsx';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(process.argv.includes('--polish')||process.argv.includes('--test')?delivery:source.source));
if(process.argv.includes('--test')){
 const p=wb.worksheets.getItem('배치구성목록'),c=wb.worksheets.getItem('프랍제작목록');
 const before=c.getRange('F155:H155').values;p.getRange('J3270').values=[['미배치']];wb.recalculate();const changed=c.getRange('F155:H155').values;
 p.getRange('J3270').values=[['배치 완료']];wb.recalculate();const restored=c.getRange('F155:H155').values;
 if(JSON.stringify(changed)!=='[[4,3,1]]'||JSON.stringify(restored)!=='[[4,4,0]]')throw new Error(JSON.stringify({before,changed,restored}));
 await fs.writeFile(path.join(here,'status_recalculation.json'),JSON.stringify({before,changed,restored,exported:false},null,2));console.log({before,changed,restored});process.exit(0);
}
function polish(){
 const guide=wb.worksheets.getItem('설계안내');guide.getRange('B43:F48').unmerge();guide.getRange('B43:F48').merge(true);guide.getRange('B43:F48').format.wrapText=true;guide.getRange('A43:F48').format.rowHeight=48;
 const cat=wb.worksheets.getItem('프랍제작목록');cat.getRange('A151:U184').format.rowHeight=60;cat.getRange('A151:U184').format.verticalAlignment='center';
 const pl=wb.worksheets.getItem('배치구성목록');pl.getRange('A3270:U3311').format.verticalAlignment='center';pl.getRange('A3270:U3311').format.rowHeight=42;
 const art=wb.worksheets.getItem('층별연출');art.getRange('A14:F15').unmerge();art.getRange('A14:F15').values=[['공통 원칙',null,'R1 흰 이중선 / S1 청록 사각 / M1 황토 점선',null,null,null],['제작 품질',null,'예각 베벨, 맞닿는 접합부, 금속·도장의 거칠기 분리, 불규칙 사용 흔적',null,null,null]];art.getRange('A14:B15').merge(true);art.getRange('C14:F15').merge(true);
 const space=wb.worksheets.getItem('공간프로그램');space.getRange('A92:O92').format.rowHeight=60;space.getRange('A92:O92').format.verticalAlignment='center';
 const con=wb.worksheets.getItem('연결계획');con.getRange('A126:Q127').format.rowHeight=48;con.getRange('A126:Q127').format.verticalAlignment='center';
}
if(process.argv.includes('--polish')){
 polish();wb.recalculate();
 for(const [name,sheet,range] of [['guide','설계안내','A43:F48'],['catalog_progress','프랍제작목록','P151:U158'],['placements_added','배치구성목록','A3270:J3279'],['floor_art','층별연출','A1:F15'],['space_added','공간프로그램','A88:O92'],['connections_added','연결계획','A123:Q127']]){const b=await wb.render({sheetName:sheet,range,scale:1.1});await fs.writeFile(path.join(here,name+'.png'),new Uint8Array(await b.arrayBuffer()));}
 const x=await SpreadsheetFile.exportXlsx(wb);await x.save(delivery);await fs.copyFile(delivery,path.resolve(here,'../../Docs/도면/원형공동/AfterSeconds_프랍환경_제작목록.xlsx'));console.log('polished export');process.exit(0);
}
console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:1500})).ndjson);
const blob=await wb.render({sheetName:'프랍제작목록',range:'A1:H10',scale:1.3});
await fs.writeFile(path.join(here,'source_preview.png'),new Uint8Array(await blob.arrayBuffer()));
if(!process.argv.includes('--edit')) process.exit(0);
// Temporarily remove calculation cells while writing source rows; restore exact
// formula groups after all data edits to avoid recalculating every intermediate.
const restoreGroups=[];
for(const s of source.sheets){const sh=wb.worksheets.getItem(s.name);for(let col=0;col<s.cols;col++){
 let start=-1,formulas=[];const flush=()=>{if(start>=0){restoreGroups.push({sheet:s.name,row:start,col,formulas});sh.getRangeByIndexes(start,col,formulas.length,1).clear({applyTo:'contents'});start=-1;formulas=[];}};
 for(let row=0;row<s.values.length;row++){const val=s.values[row][col];if(typeof val==='string'&&val.startsWith('=')){if(start<0)start=row;formulas.push([val]);}else flush();}flush();
}}
console.log('calculation cells staged');
const repo=path.resolve(here,'../..');
const plan=JSON.parse(await fs.readFile(path.join(here,'production_plan.json'),'utf8'));
const audit=path.join(repo,'Docs/검수/2026-11-06_CircularDressing');
const placed=JSON.parse(await fs.readFile(path.join(audit,'placements.json'),'utf8'));
const placedIds=new Set(placed.map(p=>p.id));
const oldPlaced=JSON.parse(await fs.readFile(path.join(repo,'Docs/검수/2026-11-06_CircularFacility/B5_placement.json'),'utf8'));
const data=JSON.parse(await fs.readFile(path.join(repo,'Docs/도면/원형공동/facility_layout.json'),'utf8'));
const cat=wb.worksheets.getItem('프랍제작목록'),pl=wb.worksheets.getItem('배치구성목록'),guide=wb.worksheets.getItem('설계안내');
const newItems=[...plan.newprops,...plan.environment];
const lookup=new Map([...data.catalog,...newItems].map(x=>[x.code,x]));
const latest=JSON.parse(await fs.readFile(path.join(here,'LinenHamper_manifest.json'),'utf8'));
const emergency=JSON.parse(await fs.readFile(path.join(here,'EmergencyCabinet_manifest.json'),'utf8'));
lookup.get('P128').w=latest.dimensions[0];lookup.get('P128').d=latest.dimensions[2];lookup.get('P128').h=latest.dimensions[1];
lookup.get('P147').w=emergency.dimensions[0];lookup.get('P147').d=emergency.dimensions[2];
const lastPlacement=3269+plan.placements.length;
for(const s of source.sheets)wb.worksheets.getItem(s.name).getRange('A1').values=[[String(s.values[0][0]).replace('V0.02','V0.03')]];
console.log('expanded source formula ranges');
guide.getRange('A1').values=[['시설 프랍·환경 제작 관리 V0.03']];
guide.getRange('B7').values=[['프랍제작목록에서 품목·제작단계를 확인하고, 배치구성목록에서 설치 수량을 관리합니다. 층별연출은 재질·조명 기준입니다.']];
guide.getRange('A2').values=[['작성자 송예찬 · 2026.11.06 · 원형 공동 제작 설계 V0.03 반영']];
guide.getRange('B14').values=[['B5 핵심 구역과 B2 메자닌 초안이 있습니다. 이번 제작은 B5 C01·T01 기준 구간입니다. 전체층 배치 완료나 게임 기능 완성을 뜻하지 않습니다.']];
guide.getRange('B20').values=[['AfterSeconds_원형공동_제작설계.pdf와 facility_layout.json을 함께 사용합니다. 본 엑셀의 신규 환경 항목은 기준 구간에서 먼저 제작합니다.']];
guide.getRange('B23').values=[['배치구성목록의 행을 추가하면 집계 수식의 마지막 행을 함께 늘립니다. 환경 품목의 명세 수량 빈칸은 전층 수량 미산정입니다.']];
guide.getRange('A43:B48').values=[['제작 범위','B5 C01 방과 T01 터널 기준 구간. 전층 환경 품목은 단계적으로 제작'],['수량 구분','기존 프랍 명세는 전층 계획, 신규 환경 명세는 1차 기준 구간만 집계. 공통 모듈·구성 부품을 합쳐 장비 대수로 해석하지 않음'],['에셋과 배치','제작단계는 모델 준비 상태. 처리 완료 수량은 배치구성목록의 배치 완료·기존 포함만 집계'],['제작 규칙','VARCO 우선 프랍 생성, 부족하면 Blender. 건축 치수·접합부는 Blender. 베벨·PBR·LOD·충돌 검사'],['현재 씬','Level_B5_Circular / Level_B2_MezzaninePreview. 구버전은 Stage/Old 보관'],['출처','시설생활 프랍배치 V0.02, 원형 공동 제작 설계 V0.03, 2026-11-06 사용자 요청']];
guide.getRange('A43:B48').format.font={name:'맑은 고딕',size:11};guide.getRange('B43:B48').format.wrapText=true;guide.getRange('A43:B48').format.rowHeight=44;

const lastCat=150+newItems.length;
cat.getRange(`A151:O${lastCat}`).copyFrom(cat.getRange('A150:O150'),'all');
for(let i=0;i<newItems.length;i++){
 const x=newItems[i],r=151+i,has=plan.placements.some(p=>p.code===x.code);
 cat.getRange(`A${r}:O${r}`).values=[[x.code,x.name,x.category,x.priority,x.model?'모델 준비':'신규 제작',null,0,null,x.w,x.d,x.h,x.notes,'','','2026-11-06 제작 가안. 환경 수량은 기준 구간만 집계']];
 if(has)cat.getRange(`F${r}:H${r}`).formulas=[[`=SUMIFS('배치구성목록'!$I$6:$I$${lastPlacement},'배치구성목록'!$E$6:$E$${lastPlacement},A${r})`,`=SUMIFS('배치구성목록'!$I$6:$I$${lastPlacement},'배치구성목록'!$E$6:$E$${lastPlacement},A${r},'배치구성목록'!$J$6:$J$${lastPlacement},"배치 완료")`,`=F${r}-G${r}`]];
}
cat.getRange('P5:U5').copyFrom(cat.getRange('A5:F5'),'all');cat.getRange('P5:U5').values=[['제작 방식','적용 층','제작 단계','재질·사용 흔적','검수 기준','제작 비고']];
cat.getRange(`P6:U${lastCat}`).format.font={name:'맑은 고딕',size:11};cat.getRange(`P6:U${lastCat}`).format.wrapText=true;cat.getRange(`P6:U${lastCat}`).format.verticalAlignment='center';
for(const [col,width] of [['P',20],['Q',18],['R',22],['S',42],['T',48],['U',48]])cat.getRange(`${col}5:${col}${lastCat}`).format.columnWidth=width;
const catCodes=[...data.catalog.map(x=>x.code),...newItems.map(x=>x.code)];
for(let i=0;i<catCodes.length;i++){
 const code=catCodes[i],x=lookup.get(code),row=i+6,build=placed.some(p=>p.code===code),old=oldPlaced.some(p=>p.code===code);
 const floors=x.floors||[...new Set(data.placements.filter(p=>p.code===code).map(p=>p.floor))].join(',');
 const method=x.method||(x.asset?'기존 에셋 검수·보수':'VARCO 후 Blender');
 const stage=build?'모델·기준구간 배치':old?'기존 배치·보수 검토':x.stage||'후속 제작';
 cat.getRange(`P${row}:U${row}`).values=[[method,floors,stage,'층별연출 기준. 먼지·닦임·손때를 사용 위치에 불규칙 적용','실척·바닥 피벗·예각 베벨·재질·메시 무게·통행 간섭',x.notes||(x.asset?'기존 후보 경로는 최종 품질 판정이 아님':'조립세트 포함 여부 확인 후 중복 제작 방지')]];
 if(code==='P128'||code==='P146'||code==='P147'){
  const name=code==='P128'?'CFD_LinenHamper':code==='P146'?'CFD_TransferCabinet':'CFD_EmergencyCabinet';cat.getRange(`M${row}`).values=[['Assets/Afrer_Seconds/05.Model/Props/Common/'+name+'.prefab']];cat.getRange(`E${row}`).values=[['모델 준비']];cat.getRange(`I${row}:K${row}`).values=[[x.w,x.d,x.h]];cat.getRange(`P${row}`).values=[[code==='P146'?'VARCO 실패 → Blender':'VARCO·리메시·Blender']];
 }
 if(code.startsWith('E')&&build){const p=plan.placements.find(p=>p.code===code);cat.getRange(`M${row}`).values=[['Assets/Afrer_Seconds/05.Model/Environment/Common/'+p.model+'.prefab']];}
}
const p38row=catCodes.indexOf('P38')+6;cat.getRange(`M${p38row}`).values=[['Assets/Afrer_Seconds/05.Model/Enemy/CCTV_SecurityCamera_Articulated.prefab']];
cat.getRange('A1').values=[['프랍·장비·환경 모듈 제작목록 V0.03']];cat.getRange('A2').values=[['프랍 147종과 환경 32종. 환경의 명세 수량은 B5 기준 구간이며 빈칸은 미산정입니다. 제작 단계와 배치 수량을 구분합니다.']];
const oldTable=cat.tables.items[0],style=oldTable.style;oldTable.delete();const table=cat.tables.add(`A5:U${lastCat}`,true,'PropCatalog');table.style=style;
console.log('catalog extended');
cat.getRange(`E6:E${lastCat}`).dataValidation={rule:{type:'list',values:['기존 에셋 검토','신규 제작','모델 준비','보수 필요']}};
cat.getRange(`R6:R${lastCat}`).dataValidation={rule:{type:'list',values:['후속 제작','기존 구조 재사용','기존 포함','기존 배치·보수 검토','모델·기준구간 배치','보수 필요']}};

const rows=plan.placements.map(p=>{const x=lookup.get(p.code);return[p.id,p.floor,p.room,p.room==='T01'?'격리–모니터링 터널':'피험체 격리 공동',p.code,x.name,p.code.startsWith('E')?'환경 모듈':'독립 배치',null,1,placedIds.has(p.id)?'배치 완료':'미배치',p.x,p.v,p.y,p.yaw,x.w,x.d,x.h,'B5 기준 구간 1차. 전층 배치 계획과 구분',null,null,null];});
pl.getRange(`A3270:U${lastPlacement}`).values=rows;
pl.getRange(`S3270:U${lastPlacement}`).formulas=rows.map((_,i)=>{const r=3270+i;return[`=K${r}`,`=M${r}`,`=-L${r}`];});
const placementStyle=pl.tables.items[0].style;pl.tables.items[0].delete();pl.tables.add(`A5:U${lastPlacement}`,true,'PlacementRows').style=placementStyle;
console.log('placement rows appended');
pl.getRange(`A3270:U${lastPlacement}`).format.rowHeight=60;pl.getRange(`A3270:U${lastPlacement}`).format.wrapText=true;pl.getRange(`K3270:Q${lastPlacement}`).setNumberFormat('0.00');
const originalPlacements=source.sheets.find(s=>s.name==='배치구성목록').values;
const oldIds=new Set(oldPlaced.map(p=>p.id));pl.getRange('J6:J3269').values=originalPlacements.slice(5).map(row=>[oldIds.has(row[0])?'배치 완료':row[9]]);
pl.getRange('S5:U5').values=[['Unity 로컬 X','Unity 로컬 Y','Unity 로컬 Z']];
console.log('existing placement statuses reconciled');
const space=wb.worksheets.getItem('공간프로그램');space.getRange('A92:O92').copyFrom(space.getRange('A91:O91'),'all');space.getRange('A92:O92').values=[['B2-C02U','B2','C02U','냉각 공동 상부 정비 데크','부분 메자닌','그레이팅 순환 통로 / 불투명 정비 발판',19,1,11,7.4,-30.4,null,null,'검토 씬 제작','하부 C02 바닥에서 +3.6m. 실제 그레이팅과 계단2개. 방 천장은 하부 공동 공유']];space.getRange('M92').formulas=[[`=COUNTIFS('배치구성목록'!$B$6:$B$${lastPlacement},B92,'배치구성목록'!$C$6:$C$${lastPlacement},C92,'배치구성목록'!$G$6:$G$${lastPlacement},"독립 배치")`]];let st=space.tables.items[0].style;space.tables.items[0].delete();space.tables.add('A5:O92',true,'SpaceProgram').style=st;
const con=wb.worksheets.getItem('연결계획');con.getRange('A126:Q127').copyFrom(con.getRange('A125:Q125'),'all');con.getRange('A126:Q127').values=[['B2-MZ-W','메자닌 계단','B2-C02','B2-C02U',5.6,3.6,1.4,null,20,.18,1,12.8,8.5,12.8,2.9,'검토 씬 제작','상하 순환 서측 계단'],['B2-MZ-E','메자닌 계단','B2-C02','B2-C02U',5.6,3.6,1.4,null,20,.18,1,25.2,8.5,25.2,2.9,'검토 씬 제작','상하 순환 동측 계단']];st=con.tables.items[0].style;con.tables.items[0].delete();con.tables.add('A5:Q127',true,'Connections').style=st;

const art=wb.worksheets.add('층별연출');art.showGridLines=false;art.getRange('A2').values=[['층별 재질·조명·생활 흔적 V0.03']];art.getRange('A2').format.font={name:'맑은 고딕',size:16,bold:true};
art.getRange('A5:F11').values=[['층','공간 역할','기본 색·재질','조명','생활 흔적','주의할 점'],['B5','격리·생활','창백한 청백색 도장, 부분 스테인리스','차가운 간접광과 낮은 작업등','침상·배식·위생 설비의 손때와 닦임','생활 흔적은 유지하되 따뜻한 주거 분위기는 절제'],['B4','측정·관찰','짙은 회색·무채색, 검사 장비','관찰창·검사대 중심의 국소 조명','장비 접촉부 마모, 정리된 케이블','전체를 검게 만들지 않고 시선이 모이는 대상을 밝힘'],['B3','시료·창고','어두운 중성 회색, 랙·냉장 설비','보관5구역 기본 소등, 구역별 점등','랙 하부 먼지, 운반차 접촉, 적재 흔적','비상 이동등·냉장 전원과 일반 조명 회로 분리'],['B2','기계·정비','철색·흑철·배관 금속','낮은 붉은 보조등 + 중성 작업등','유분·열변색·먼지, 정비 부분의 닦임','경보와 상시 적색 구분. 계단·밸브는 읽히게'],['B1','연구·통제','기존 웜그레이·아이보리 유지','통제 데스크와 작업면 중심','잘 관리된 표면, 빈번한 조작부에 약한 마모','지하 공통 문·안내선 코드 유지'],['1F','폐공장·검문','풍화 콘크리트·바랜 도장·철재','외광과 검문 작업등 대비','누수·녹·방치 흔적, 사용 동선만 닦임','지상은 평지붕. 지하 반구 공동과 구분']];
art.getRange('A5:F5').format={fill:'#203A4B',font:{name:'맑은 고딕',size:11,bold:true,color:'#FFFFFF'},rowHeight:30};art.getRange('A6:F11').format={font:{name:'맑은 고딕',size:11},wrapText:true,verticalAlignment:'center',rowHeight:64};
for(const [c,w] of [['A',8],['B',18],['C',32],['D',38],['E',40],['F',48]])art.getRange(`${c}5:${c}11`).format.columnWidth=w;
art.getRange('A14:F15').values=[['공통 원칙','R1 흰 이중선 / S1 청록 사각 / M1 황토 점선',null,null,null,null],['제작 품질','예각 베벨, 맞닿는 접합부, 금속·도장의 거칠기 분리, 불규칙 사용 흔적',null,null,null,null]];art.getRange('B14:F15').merge(true);art.getRange('A14:F15').format.rowHeight=30;art.getRange('A14:F15').format.font={name:'맑은 고딕',size:11};
polish();
for(const group of restoreGroups)wb.worksheets.getItem(group.sheet).getRangeByIndexes(group.row,group.col,group.formulas.length,1).formulas=group.formulas.map(row=>[row[0].replaceAll('3269',String(lastPlacement))]);
console.log('original formulas restored');
wb.recalculate();
console.log('recalculated');
console.log((await wb.inspect({kind:'table',range:`프랍제작목록!A151:K157`,include:'values,formulas',tableMaxRows:7,tableMaxCols:11,maxChars:3000})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'final formula error scan',maxChars:1500})).ndjson);
for(const [name,sheet,range] of [['catalog_added','프랍제작목록','A151:K160'],['catalog_progress','프랍제작목록','P149:U158'],['placements_added','배치구성목록','A3270:J3279'],['guide','설계안내','A43:F48'],['floor_art','층별연출','A1:F15']]){
 const im=await wb.render({sheetName:sheet,range,scale:1.1});await fs.writeFile(path.join(here,name+'.png'),new Uint8Array(await im.arrayBuffer()));
}
const outDir=path.join('C:/Users/503-26/Documents/Codex/2026-11-06/dl/outputs/after_seconds_reviewed');
await fs.mkdir(outDir,{recursive:true});const dest=path.join(outDir,'AfterSeconds_프랍환경_제작목록.xlsx');const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(dest);
await fs.copyFile(dest,path.join(repo,'Docs/도면/원형공동/AfterSeconds_프랍환경_제작목록.xlsx'));
console.log(JSON.stringify({output:dest,catalogItems:catCodes.length,originalItems:145,environment:32,placementsAdded:rows.length,placed:placed.length}));
