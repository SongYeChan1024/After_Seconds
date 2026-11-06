from pathlib import Path
import json,openpyxl,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1]
src=Path(json.loads((H/'workbook_source.json').read_text('utf-8'))['source'])
out=R/'Docs/도면/원형공동/AfterSeconds_프랍환경_제작목록.xlsx'
a=openpyxl.load_workbook(src,data_only=False);b=openpyxl.load_workbook(out,data_only=False);cache=openpyxl.load_workbook(out,data_only=True)
assert b.sheetnames[:7]==a.sheetnames
diff=[]
for sa in a:
 sb=b[sa.title]
 for row in sa:
  for ca in row:
   cb=sb[ca.coordinate];av=ca.value;bv=cb.value
   if av==bv:continue
   if ca.coordinate=='A1':continue
   if isinstance(av,str) and av.startswith('=') and av.replace('3269','3311')==bv:continue
   if sa.title=='설계안내' and (ca.coordinate in ['A2','B7','B14','B20','B23'] or ca.row>=43):continue
   if sa.title=='프랍제작목록' and (ca.coordinate=='A2' or ca.row in [43,133] and ca.column in [5,9,10,11,13]):continue
   if sa.title=='배치구성목록' and (ca.column==10 and bv=='배치 완료' or ca.row==5 and ca.column in [19,20,21]):continue
   diff.append((sa.title,ca.coordinate,av,bv))
 assert sa.freeze_panes==sb.freeze_panes,(sa.title,'freeze',sa.freeze_panes,sb.freeze_panes)
 assert set(sa.tables)==set(sb.tables),(sa.title,'table names')
assert not diff,diff[:20]
cat=b['프랍제작목록'];codes=[cat.cell(r,1).value for r in range(6,cat.max_row+1)];assert len(codes)==179 and len(set(codes))==179
assert b['배치구성목록'].max_row==3311
v=cache['프랍제작목록'];expected={'P146':(1,1,0),'P147':(1,1,0),'P128':(4,1,3),'E03':(4,4,0),'E04':(12,12,0),'E26':(5,5,0)}
for code,wanted in expected.items():
 row=codes.index(code)+6;actual=tuple(v.cell(row,c).value for c in [6,7,8]);assert actual==wanted,(code,actual,wanted)
errors=[]
for s in cache:
 for row in s:
  for c in row:
   if c.data_type=='e':errors.append((s.title,c.coordinate,c.value))
assert not errors,errors[:10]
record={'sheets':b.sheetnames,'catalog':179,'environment':32,'placementRows':3306,'newPlacements':42,'originalDataUnexpectedChanges':diff,'formulaErrors':errors,'nativeTables':[list(s.tables) for s in b],'expectedTotals':expected,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
(R/'Docs/검수/2026-11-06_CircularDressing/workbook_validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf-8');print(json.dumps(record,ensure_ascii=False))
