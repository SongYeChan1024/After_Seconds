from pathlib import Path
import json,math,copy
H=Path(__file__).resolve().parent;R=H.parents[1]
plan=json.loads((H/'base_layout.json').read_text(encoding='utf8'));rooms={r['id']:r for r in plan['rooms']}
cat={a['name']:a for p in [H/'catalog.json',R/'SourceAssets/B4_FullFloor/asset_catalog.json',R/'SourceAssets/B4_FullFloor/new_catalog.json'] for a in json.loads(p.read_text(encoding='utf8'))}
existing=json.loads((H/'existing_assets.json').read_text(encoding='utf8'))
def turn(x,z,a):
 a=math.radians(a);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
def rect(x,z,w,d,yaw=0):return [(x+turn(a,b,yaw)[0],z+turn(a,b,yaw)[1]) for a,b in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
def sat(a,b,margin=.18):
 for poly in [a,b]:
  for i in range(4):
   x,z=poly[(i+1)%4][0]-poly[i][0],poly[(i+1)%4][1]-poly[i][1];n=math.hypot(x,z);nx,nz=-z/n,x/n;aa=[x*nx+z*nz for x,z in a];bb=[x*nx+z*nz for x,z in b]
   if max(aa)+margin<min(bb) or max(bb)+margin<min(aa):return False
 return True
def geom(model,x,z,yaw):
 c=cat[model];w,h,d=c['size'];cx,cy,cz=c['center'];dx,dz=turn(cx,cz,yaw);return rect(x+dx,z+dz,w,d,yaw)
old={k:[] for k in rooms}
for a in existing:
 if not a['active'] or '/Props/' not in a['asset'] or a['position'][1]>-64.8:continue
 code=next((k for k in rooms if a['name'].startswith('B4_'+k+'_')),None)
 if not code:continue
 r=rooms[code];model=Path(a['asset']).stem;x=a['position'][0]-r['x'];z=a['position'][2]+r['v'];yaw=a['rotation'][1]
 poly=geom(model,x,z,yaw) if model in cat else rect(a['boundsCenter'][0]-r['x'],a['boundsCenter'][2]+r['v'],max(.05,a['boundsSize'][0]),max(.05,a['boundsSize'][2]))
 old[code].append({'name':a['name'],'poly':poly})
# A desired work area with a real operator / subject approach. Coordinates may shift
# to clear existing furniture and the first 2.8m of every doorway.
primary={
'C01':[('PrecisionPlatform','종합계측_정밀플랫폼',0,0,0),('ObservationBooth','연구원_보호관측부스',-5.6,-5.6,225),('AdaptiveTargetArray','반복시험_가변표적',2,-5.2,0)],
'C02':[('SubjectCheckIn','실험체_접수확인',-2.4,2.0,180),('ElectrodePrepBench','센서부착_준비대',2.6,-1.6,270),('SensorFittingStand','실험체_센서착용',0,-2.4,0)],
'C03':[('InstrumentServiceBay','광학계측기_분해교정',2.0,-2.8,0),('UtilityServiceSpine','교정설비_접속반',3.6,1.7,270)],
'C04':[('OperatorIsland','정밀신호_분석작업섬',-2.2,2.3,180),('DualReviewStation','기준값_반복측정비교',2.2,-2.3,0)],
'C05':[('ProtocolTable','실험회차_기록대조',0,1.3,180),('SubjectCheckIn','기록인수_검증대',-2,-1.5,90)],
'W01':[('ObservationBooth','투척시험_보호관측부스',3.8,2.5,90),('AdaptiveTargetArray','투척조건_가변표적',-2.5,-3.4,0)],
'W02':[('ObservationBooth','궤적시험_보호관측부스',-1.5,-4.4,180),('PursuitTrack','추적발달_가변궤도',2.4,3.0,180)],
'W03':[('StimulusWall','전신반응_자극벽',0,3.6,180),('PrecisionPlatform','반응훈련_압력계측',-.7,-2.4,0)],
'E01':[('DualReviewStation','동일조건_영상비교석',-3.1,-2.7,0),('ProtocolTable','측정회차_공동판독',2.7,-2.0,0)],
'E02':[('ProtocolTable','발달계획_검토테이블',-1.5,-2.8,0),('InstrumentServiceBay','시험설정_장비준비',2.9,-4.9,0)],
'E03':[('RecoveryRecliner','시험후_집중회복석',3.2,1.3,270),('ElectrodePrepBench','센서제거_상태검사',-3,1.3,90)],
'N01':[('ProtocolTable','진행도_합동검토',0,-2.2,0),('GuardControlPost','경비_이송상태감시',-4.5,.5,90),('DualReviewStation','개체별_진행비교석',4.5,-2.6,315)],
'S01':[('LoadResistanceRig','부하발달_반복시험',-3.7,-2.4,30),('ObservationBooth','고부하시험_보호관측',4.2,1.1,50)]}
program={
'C01':['SubjectCheckIn','EscortBench','GuardControlPost','SensorFittingStand','ElectrodePrepBench','TimingReferenceTower','MobileAcquisitionCart','EquipmentCaseRack','TargetRecoveryTrolley','TrialInterlock','UtilityServiceSpine','SafetyEquipment','SmallSupplyCart','RollingCableReel'],
'C02':['EscortBench','GuardControlPost','CleanReturnCabinet','ConsumableWall','EmergencyCart','MobileAcquisitionCart','EquipmentWashStation','SmallSupplyCart','TrialInterlock','EquipmentCaseRack'],
'C03':['CalibrationRack','CalibrationRack','EquipmentCaseRack','EquipmentCaseRack','CleanReturnCabinet','EquipmentWashStation','RollingCableReel','TargetRecoveryTrolley','ConsumableWall','MobileAcquisitionCart','SafetyEquipment'],
'C04':['CalibrationRack','TimingReferenceTower','EquipmentCaseRack','ConsumableWall','UtilityServiceSpine','MobileAcquisitionCart','SmallSupplyCart','CleanReturnCabinet','TargetRecoveryTrolley','SafetyEquipment'],
'C05':['EquipmentCaseRack','EquipmentCaseRack','CleanReturnCabinet','ConsumableWall','GuardControlPost','MobileAcquisitionCart','SmallSupplyCart','SafetyEquipment'],
'W01':['ProjectileCabinet','ProjectileCabinet','TargetRecoveryTrolley','TargetRecoveryTrolley','TimingReferenceTower','CalibrationRack','SensorFittingStand','EscortBench','GuardControlPost','TrialInterlock','UtilityServiceSpine','SafetyEquipment','RollingCableReel'],
'W02':['CalibrationRack','TimingReferenceTower','EquipmentCaseRack','SensorFittingStand','MobileAcquisitionCart','TargetRecoveryTrolley','EscortBench','GuardControlPost','TrialInterlock','UtilityServiceSpine','SafetyEquipment','RollingCableReel'],
'W03':['AcousticPartition','SensorFittingStand','MobileAcquisitionCart','TimingReferenceTower','EscortBench','GuardControlPost','TrialInterlock','EmergencyCart','ConsumableWall','CleanReturnCabinet','SmallSupplyCart'],
'E01':['EquipmentCaseRack','CleanReturnCabinet','MobileAcquisitionCart','TimingReferenceTower','ConsumableWall','GuardControlPost','SmallSupplyCart','SafetyEquipment'],
'E02':['ConsumableWall','CleanReturnCabinet','EquipmentCaseRack','MobileAcquisitionCart','TimingReferenceTower','EquipmentWashStation','SmallSupplyCart','UtilityServiceSpine','SafetyEquipment'],
'E03':['RecoveryRecliner','EmergencyCart','EmergencyCart','ConsumableWall','CleanReturnCabinet','EquipmentWashStation','EscortBench','SubjectCheckIn','GuardControlPost','SmallSupplyCart','SafetyEquipment'],
'N01':['CalibrationRack','TimingReferenceTower','EquipmentCaseRack','ConsumableWall','SubjectCheckIn','EscortBench','MobileAcquisitionCart','UtilityServiceSpine','SafetyEquipment','SmallSupplyCart'],
'S01':['ShieldPowerPack','ShieldPowerPack','TimingReferenceTower','MobileAcquisitionCart','EquipmentCaseRack','TargetRecoveryTrolley','EscortBench','GuardControlPost','TrialInterlock','EmergencyCart','UtilityServiceSpine','SafetyEquipment'],
'VA':['GuardControlPost','SafetyEquipment'], 'VB':['GuardControlPost','SafetyEquipment'], 'VL':['SubjectCheckIn','EquipmentCaseRack','TargetRecoveryTrolley','SafetyEquipment']}
labels={'SubjectCheckIn':'실험체_인계확인대','EscortBench':'호송대기_고정좌석','GuardControlPost':'경비_현장통제석','SensorFittingStand':'측정센서_착용대','ElectrodePrepBench':'센서부착_준비대','TimingReferenceTower':'시험시간_동기화기','MobileAcquisitionCart':'측정데이터_수집카트','EquipmentCaseRack':'전용장비_케이스보관','TargetRecoveryTrolley':'시험물_회수카트','TrialInterlock':'시험구획_현장통제','UtilityServiceSpine':'장비전원_신호접속반','SafetyEquipment':'현장_비상대응설비','SmallSupplyCart':'소모품_운반카트','RollingCableReel':'계측케이블_릴','CleanReturnCabinet':'세척완료_장비보관','ConsumableWall':'실험소모품_보관대','EmergencyCart':'시험후_응급지원카트','EquipmentWashStation':'재사용기구_세척대','CalibrationRack':'정밀신호_교정랙','ProjectileCabinet':'규격시험물_보관장','AcousticPartition':'자극시험_차음구획','RecoveryRecliner':'회복관찰_리클라이너','ShieldPowerPack':'차폐시험_전원제어'}
placements=[];workspaces=[];failed=[];meshmodels={'ObservationBooth','ScreenedEntry','PrecisionPlatform','LoadResistanceRig','AdaptiveTargetArray','PursuitTrack','RecoveryRecliner','EscortBench','AcousticPartition'}
for code,r in rooms.items():
 blocks=copy.deepcopy(old[code]);spaces=[];doorpolys=[]
 for d in r['doors']:
  u,v=d['x'],d['z'];length=math.hypot(u,v);u/=length;v/=length;doorpolys.append(rect(u*(r['r']-1.10),v*(r['r']-1.10),2.2,2.8,math.degrees(math.atan2(u,v))))
 if code in ['VA','VB']:blocks.append({'name':'stair_footprint','poly':rect(0,0,3.8,6.6)})
 if code=='VL':blocks.append({'name':'cargo_cabin','poly':rect(0,-1.3,4.0,3.7)})
 if code=='C01':blocks.extend([{'name':'upper_stairs_area','poly':rect(0,7.0,13.4,8.0)}])
 def add(model,label,preferred=None,primary=False):
  mn='BX_'+model;c=cat[mn];w,h,d=c['size'];cx,cy,cz=c['center'];limit=math.sqrt(max(0,r['r']**2-(cy+h/2)**2))-.20 if r['kind']!='core' else r['r']-.2
  candidates=[]
  if preferred:
   px,pz,pa=preferred
   for radius in [0,.4,.8,1.2,1.8,2.4,3.2]:
    for ai in (range(1) if radius==0 else range(16)):
     x=px+radius*math.cos(ai*math.tau/16);z=pz+radius*math.sin(ai*math.tau/16)
     for da in [0,-15,15,-30,30]:candidates.append((x,z,(pa+da)%360,radius*10+abs(da)*.03))
  for rad in [r['r']-d/2-.6,r['r']-d/2-1.3,r['r']*.60,r['r']*.40,r['r']*.25]:
   for a in range(0,360,6):
    x=rad*math.cos(math.radians(a));z=rad*math.sin(math.radians(a));yaw=270-a
    candidates.append((x,z,yaw,100+(r['r']-rad)*3))
  for x,z,yaw,score in sorted(candidates,key=lambda a:a[3]):
   poly=geom(mn,x,z,yaw)
   if max(math.hypot(a,b) for a,b in poly)>limit:continue
   if any(sat(poly,b['poly'],.18) for b in blocks) or any(sat(poly,q,.08) for q in doorpolys) or any(sat(poly,q,.10) for q in spaces):continue
   # Keep the operator/subject side available; appliances with a deep test floor
   # remain mesh-collided, so their actual working interior is traversable.
   ww=min(w,1.8);dz=cz+d/2+.57;dx,zz=turn(cx,dz,yaw);access=rect(x+dx,z+zz,ww,.90,yaw)
   if max(math.hypot(a,b) for a,b in access)>r['r']-.2:continue
   if any(sat(access,b['poly'],.07) for b in blocks):continue
   n=f'B4_{code}_{label}_{sum(a["room"]==code for a in placements)+1:02}'
   p={'room':code,'name':n,'asset':c['asset'],'model':mn,'position':[x,0,z],'yaw':yaw%360,'size':c['size'],'center':c['center'],'meshCollider':model in meshmodels,'access':[x+dx,0,z+zz],'primary':primary}
   placements.append(p);blocks.append({'name':n,'poly':poly});spaces.append(access);workspaces.append({'name':n,'room':code,'point':p['access'],'polygon':access});return True
  failed.append({'room':code,'model':model,'primary':primary});return False
 for model,label,x,z,yaw in primary.get(code,[]):add(model,label,(x,z,yaw),True)
 for model in program.get(code,[]):add(model,labels[model])
 if r['kind']!='core':
  for p in [p for p in list(placements) if p['room']==code and p['primary'] and p['model']!='BX_ObservationBooth']:
   dx,dz=turn(-p['size'][0]/2-.70,-.15,p['yaw']);add('TaskLightPole','시험설비_작업등',(p['position'][0]+dx,p['position'][2]+dz,p['yaw']))
  add('TaskLightPole','장비준비_작업등')
plan['newPlacements']=placements;plan['workspaces']=workspaces;plan['unplaced']=failed;plan['newModelCount']=len(json.loads((H/'models.json').read_text()));plan['author']='송예찬'
(H/'layout.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'placed':len(placements),'perRoom':{k:sum(p['room']==k for p in placements) for k in rooms},'unplaced':failed},ensure_ascii=False))
# Flat review map: position and working-side clearance, never imported into the game.
colors={'old':'#58616a','new':'#8aa99e','access':'#b8b99b'}
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1440" viewBox="0 0 1440 1440"><rect width="1440" height="1440" fill="#172029"/>']
for i,(code,r) in enumerate(rooms.items()):
 ox=180+(i%4)*360;oy=180+(i//4)*360;scale=145/(r['r']+1)
 parts.append(f'<circle cx="{ox}" cy="{oy}" r="{r["r"]*scale}" fill="#26313b" stroke="#b8c4cb"/><text x="{ox-145}" y="{oy-154}" fill="white" font-size="18">{code}</text>')
 for d in r['doors']:parts.append(f'<circle cx="{ox+d["x"]*scale}" cy="{oy-d["z"]*scale}" r="9" fill="#cfad7b"/>')
 for b in old[code]:parts.append('<polygon points="'+' '.join(f'{ox+x*scale},{oy-z*scale}' for x,z in b['poly'])+'" fill="#59656e"/>')
 for p in [q for q in placements if q['room']==code]:
  poly=geom(p['model'],p['position'][0],p['position'][2],p['yaw']);parts.append('<polygon points="'+' '.join(f'{ox+x*scale},{oy-z*scale}' for x,z in poly)+'" fill="#91b5a6" stroke="#172029"/>');x,_,z=p['access'];parts.append(f'<circle cx="{ox+x*scale}" cy="{oy-z*scale}" r="3" fill="#f0dc9e"/>')
parts.append('</svg>');(H/'placement_plan.svg').write_text(''.join(parts),encoding='utf8')
