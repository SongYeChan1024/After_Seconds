from pathlib import Path
import json,math
H=Path(__file__).resolve().parent
plan=json.loads((H/'plan.json').read_text(encoding='utf-8'));cat={a['name']:a for p in ['asset_catalog.json','new_catalog.json'] for a in json.loads((H/p).read_text())}
def item(n,x=0,z=0,yaw=0,label=None):return {'model':n,'x':x,'z':z,'yaw':yaw,'label':label or n}
def group(*entries):return list(entries)
def one(n,label=None):return group(item(n,label=label))
def desk(n='BF_ResearchDesk'):return group(item(n,label='연구작업석'),item('SF_TaskChair',0,1.02,180,label='작업의자'))
def bed():return group(item('SF_MedicalBed',label='검사침대'),item('SF_VitalCart',1.03,.2,label='생체신호기록기'),item('BF_GlazedDivider',-1.03,0,90,label='진료구획_가림'))
program={
'C02':[group(item('BF_DiagnosticChair',label='기초진단_센서의자'),item('SF_VitalCart',1.15,.2,label='진단모니터')),one('BF_AnalysisBench','검체준비_분석대'),one('SF_ColdStorage','밀폐시료냉장'),one('SF_MedicationCabinet','진단용품보관'),one('BO_SynchronizationCart','검사동기화카트'),one('SF_WaitingBench','이송대기석'),one('BF_GlazedDivider','검사구획')],
'C03':[one('BF_SensorWorkbench','센서교정작업대'),one('SF_MaintenanceBench','측정기정비대'),one('BO_SensorPreparationBench','검사준비대'),one('BO_SensorStorage','센서출납보관'),one('SF_ArchiveCaseRack','운반케이스보관'),desk('BO_ObservationConsole'),one('BF_GlazedDivider','교정구획')],
'C04':[one('BF_AnalysisBench','신호분석대'),one('BF_AnalysisBench','시료측정대'),one('SF_ColdStorage','분석시료냉장'),one('SF_MedicalSterilizer','용기세척멸균'),one('BO_AcquisitionRack','분석수집랙'),one('BF_SensorWorkbench','분석장비교정'),one('BF_GlazedDivider','분석구획')],
'C05':[one('BF_RecordRack','봉인기록보관_01'),one('BF_RecordRack','봉인기록보관_02'),one('BF_RecordRack','봉인기록보관_03'),one('BF_CustodyTransferHatch','기록인수인계'),one('SF_SC_NetworkRack','기록서버'),one('SF_SC_UPSRack','무정전전원'),desk()],
'W01':[one('BF_ThrowLane','투척지연_측정레인'),desk('BO_TrialControlConsole'),one('BO_SensorPreparationBench','투척물계측준비'),one('BO_SynchronizationCart','타임코드기록'),one('BO_SensorStorage','투척물보관'),one('BF_GlazedDivider','측정감독구획')],
'W02':[one('BF_TrajectoryGantry','3단광학_궤적게이트'),desk('BO_TrialControlConsole'),one('BF_SensorWorkbench','카메라교정대'),one('BO_CalibrationTarget','좌표보정타깃'),one('BO_AcquisitionRack','고속영상수집'),one('SF_ArchiveCaseRack','관측장비케이스'),one('BF_GlazedDivider','교정구획')],
'W03':[group(item('BF_ReactionBooth',label='자극응답부스_01'),item('SF_TaskChair',0,.72,180,label='피험체좌석')),group(item('BF_ReactionBooth',label='자극응답부스_02'),item('SF_TaskChair',0,.72,180,label='피험체좌석')),one('BO_SynchronizationCart','반응타임코드'),one('SF_MedicalBed','검사대기침대'),one('SF_VitalCart','생체기록'),one('BO_SensorStorage','자극장비보관')],
'E01':[one('BF_InterpretationWall','영상비교_대형판독벽'),desk(),desk(),one('BF_RecordRack','판독자료보관'),one('SF_SC_NetworkRack','영상워크스테이션'),one('BF_GlazedDivider','판독구획')],
'E02':[desk(),desk(),desk(),one('SF_BriefingTable','연구검토테이블'),one('BF_RecordRack','프로토콜보관'),one('SF_SC_GearLockers','연구원개인보관'),one('BF_SensorWorkbench','시제품계측'),one('BF_GlazedDivider','집중작업구획')],
'E03':[bed(),bed(),one('SF_MedicalGasStation','회복지원설비'),one('SF_MedicationCabinet','의료용품보관'),one('SF_TransferNurseDesk','이송상태기록'),one('SF_LinenRack','회복리넨보관'),one('SF_WaitingBench','감독대기석')],
'N01':[one('BF_IntegratedControlWall','통합관찰_6분할화면'),desk('BO_ObservationConsole'),desk('BO_ObservationConsole'),desk('BO_TrialControlConsole'),one('SF_SC_RadioDutyStation','관찰연락석'),one('BO_AcquisitionRack','관측데이터랙'),one('SF_SC_UPSRack','무정전전원'),one('BF_CustodyTransferHatch','기록인계'),one('BF_GlazedDivider','교대구획')],
'S01':[one('BF_ShieldTestCell','차폐하중_실험챔버'),desk('BO_TrialControlConsole'),one('BO_SynchronizationCart','차폐시험계측'),one('BO_SensorStorage','시험치구보관'),one('BF_AnalysisBench','시험후분석'),one('BO_AcquisitionRack','시험수집랙')]}
def turn(x,z,yaw):
 a=math.radians(yaw);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
def corners(w,d,cx=0,cz=0,yaw=0):return [(cx+turn(x,z,yaw)[0],cz+turn(x,z,yaw)[1]) for x,z in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
def sat(a,b,margin=.25):
 for poly in [a,b]:
  for i in range(4):
   x,z=poly[(i+1)%4][0]-poly[i][0],poly[(i+1)%4][1]-poly[i][1];l=math.hypot(x,z);nx,nz=-z/l,x/l;aa=[x*nx+z*nz for x,z in a];bb=[x*nx+z*nz for x,z in b]
   if max(aa)+margin<min(bb) or max(bb)+margin<min(aa):return False
 return True
placements=[];zones=[];skipped=[]
for r in plan['rooms']:
 code=r['id']
 if code not in program:continue
 blocks=[];paths=[]
 for door in r['doors']:
  length=math.hypot(door['x'],door['z']);yaw=math.degrees(math.atan2(door['x'],door['z']));paths.append(corners(1.8,length,door['x']/2,door['z']/2,yaw))
 for gi,cluster in enumerate(program[code]):
  pts=[];height=0
  for it in cluster:
   c=cat[it['model']];w,h,d=c['size'];cx,cy,cz=c['center'];ox,oz=turn(cx,cz,it['yaw']);pts+=corners(w,d,it['x']+ox,it['z']+oz,it['yaw']);height=max(height,cy+h/2)
  minx,maxx=min(x for x,z in pts),max(x for x,z in pts);minz,maxz=min(z for x,z in pts),max(z for x,z in pts);w,d=maxx-minx,maxz-minz;cx,cz=(maxx+minx)/2,(maxz+minz)/2
  found=None;limit=math.sqrt(r['r']**2-min(height,3.5)**2)-.22
  for depthstep in range(10):
   radius=r['r']-d/2-.65-depthstep*.25
   if radius<2.2:continue
   candidates=[]
   for ai in range(120):
    angle=(90+ai*3+(gi%2)*1.5)%360;a=math.radians(angle);x,z=radius*math.cos(a),radius*math.sin(a);yaw=270-angle;poly=corners(w,d,x,z,yaw)
    if max(math.hypot(px,pz) for px,pz in poly)>limit:continue
    if sat(poly,corners(2.4,2.4),.15) or any(sat(poly,p,.18) for p in paths) or any(sat(poly,p,.45) for p in blocks):continue
    # Prefer broad wall bays and separate neighboring activities.
    score=min(abs((angle-q['angle']+180)%360-180) for q in r['doors'])+radius*.1;candidates.append((score,angle,x,z,yaw,poly))
   if candidates:found=max(candidates);break
  if found is None:skipped.append({'room':code,'models':[i['model'] for i in cluster]});continue
  _,angle,x,z,yaw,poly=found;blocks.append(poly);zones.append({'room':code,'group':gi,'center':[x,z],'size':[w,d],'yaw':yaw,'polygon':poly})
  for it in cluster:
   c=cat[it['model']];dx,dz=turn(it['x']-cx,it['z']-cz,yaw);label=it['label'] if not it['label'].startswith(('BF_','BO_','SF_')) else '설비'
   placements.append({'room':code,'name':f'B4_{code}_{label}_{sum(p["room"]==code for p in placements)+1:02}','asset':c['asset'],'position':[x+dx,0,z+dz],'yaw':(yaw+it['yaw'])%360,'size':c['size'],'center':c['center'],'meshCollider':it['model'] in ['BF_ThrowLane','BF_TrajectoryGantry','BF_ReactionBooth','BF_DiagnosticChair','BF_ShieldTestCell','BF_GlazedDivider']})
plan['placements']=placements;plan['zones']=zones;plan['skippedOptional']=skipped
(H/'layout.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'placements':len(placements),'perRoom':{r['id']:sum(p['room']==r['id'] for p in placements) for r in plan['rooms'] if r['id'] in program},'skipped':skipped},ensure_ascii=False))
