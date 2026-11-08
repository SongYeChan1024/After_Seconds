from pathlib import Path
import re,json,collections
H=Path(__file__).resolve().parent;data=json.loads((H/'scene_names.json').read_text(encoding='utf8'));ko=re.compile('[\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]')
words={'능력측정발달강화층':'ResearchFloor','실험운용설비':'ExperimentEquipment','전체확장':'FloorLayout','가림계산영역':'OcclusionAreas','복도전용안내':'CorridorGuides','연결복도':'Corridors','실험운용':'Equipment','관측설비':'ObservationEquipment','관찰 지원 공동':'CalibrationLab','중앙 관찰 공동':'MainLab','진단 공동':'SensorPrep','분석 공동':'SignalAnalysis','기록 공동':'SessionRecords','투척 지연 측정실':'ThrowLab','궤적 추적실':'TrackingLab','반응시간 측정실':'ReactionLab','영상 판독실':'ImageReview','연구원 작업실':'ResearchOffice','진단·회복 공동':'Recovery','통합 관찰 관제':'ControlRoom','차폐 실험 공동':'ShieldLab','화물 승강기':'FreightLift','계단 A':'StairA','계단 B':'StairB','집중작업구획':'WorkBay','검토회의석':'ReviewDesk','관제구획_가림':'ControlPartition','목적지안내':'Wayfinding','복도안내선':'GuideLine','안내선':'GuideLine','바닥표기':'FloorLabel','접근복도':'Approach','건축':'Architecture','출입구':'Entrances','운용설비':'Equipment','조명_서스펜션':'LightRig','등기구_실제광원':'Light','복도조명_보강':'CorridorLights','천장등_보강':'CeilingLight','천장조명':'CeilingLights','보강조명':'Lights','천장등':'CeilingLight','조명':'Lights','광원':'Light'}
def plain(s):
 for a,b in sorted(words.items(),key=lambda p:-len(p[0])):s=s.replace(a,b)
 s=re.sub(r'([A-Z]\d\d|V[ABL])행',r'To_\1',s)
 return s
def propose(q):
 row=q['row'];name=row['name']
 if not row['prefabRoot']:return plain(name)
 if '작업의자' in name:return 'TaskChair_'+name.rsplit('_',1)[-1]
 # Keep function-specific distinctions for chairs, lights and connected portals.
 special={'관측석작업등':'ConsoleLight','데크하부등':'DeckLight','상부관측의자':'ObserverChair','시험제어의자':'OperatorChair','천장등_보강':'CeilingLight','천장등':'CeilingLight','아치문틀':'Portal','닫힌문':'ClosedDoor'}
 for a,b in special.items():
  if a in name:
   n=name.replace(a,b).replace('_B4-T','_T');n=plain(n)
   if not ko.search(n):return n
 model=Path(row['prefabAsset']).stem;model=re.sub(r'^(?:BF|BO|BX|SF|CFD|CL)_','',model)
 m=re.match(r'^(B\d_)?([CWENS]\d\d|V[ABL]|T\d\d)_',name)
 prefix=m.group(0) if m else ''
 if m:model=re.sub('^'+m.group(2)+'_','',model)
 index=re.search(r'_(\d+(?:_\d+)*)$',name)
 return prefix+model+('_'+index.group(1) if index else '')
by_scene=collections.defaultdict(list)
for q in data:by_scene[q['scene']].append(q)
plan=[];changed_names={};collisions=[]
for scene,rows in by_scene.items():
 allrows=json.loads((H/(Path(scene).stem+'_before.json')).read_text(encoding='utf8'));mapping={q['row']['id']:propose(q) for q in rows};siblings=collections.defaultdict(set)
 # Preserve already-English siblings, then resolve new conflicts with simple suffixes.
 for r in allrows:
  if r['id'] not in mapping:siblings[r['parent']].add(r['name'])
 for q in rows:
  r=q['row'];base=mapping[r['id']];assert not ko.search(base),base
  name=base;i=2
  while name in siblings[r['parent']]:name=base+f'_{i:02}';i+=1
  if name!=base:collisions.append({'old':r['name'],'base':base,'new':name})
  siblings[r['parent']].add(name);plan.append({'scene':scene,'id':r['id'],'old':r['name'],'new':name})
  changed_names.setdefault(r['name'],set()).add(name)
(H/'rename_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(H/'name_map.json').write_text(json.dumps({k:sorted(v) for k,v in changed_names.items()},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'renames':len(plan),'uniqueOldNames':len(changed_names),'ambiguousNames':{k:sorted(v) for k,v in changed_names.items() if len(v)>1},'resolvedCollisions':collisions[:25]},ensure_ascii=False,indent=2))
