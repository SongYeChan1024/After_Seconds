"""B1 human-scale interior plan. Author: 송예찬. Never executes old Apply tools."""
from pathlib import Path
import json, math, copy, hashlib, shutil
H=Path(__file__).resolve().parent; R=H.parents[1]
U=R/'Unity/After_Seconds_Build_V0.01'; A=U/'Assets/Afrer_Seconds'
O=R/'Docs/Review/2026-11-12_B1_Interior'; O.mkdir(parents=True,exist_ok=True)
original=json.loads((H.parent/'B1_StaffDataRevision/layout.json').read_text(encoding='utf8'))
p=copy.deepcopy(original); p['workspaces']=[]
rooms={r['id']:r for r in p['rooms']}; walls=[]; ceilings=[]; zones=[]; lights=[]
scene=A/'01.Scenes/Stage/Level_B1_Circular.unity'
if not (H/'before.unity').exists():shutil.copy2(scene,H/'before.unity')
if not (H/'protected_before.json').exists():
 protected={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ['01.Scenes','02.Scripts','07.Animator'] for f in (A/folder).rglob('*') if f.is_file() and f!=scene and not ('Level_B1_Circular' in str(f) and f.suffix=='.asset')}
 for f in (A/'05.Model/Props/B2').glob('VA_*'):
  if f.is_file():protected[str(f.relative_to(R))]=hashlib.sha256(f.read_bytes()).hexdigest()
 (H/'protected_before.json').write_text(json.dumps(protected,indent=2),encoding='utf8')
def selected(room,model):return [q for q in p['placements'] if q['room']==room and q['model']==model]
def rot(x,z,a):
 a=math.radians(a);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
def place(q,x,z,a=0):
 dx,dz=rot(q['center'][0],q['center'][2],a)
 q['position']=[x-dx,q['position'][1],z-dz];q['yaw']=a
def setall(room,model,coords):
 qs=selected(room,model);assert len(qs)==len(coords),(room,model,len(qs),len(coords))
 for q,co in zip(qs,coords):place(q,*co)
def add(room,model,x,z,a=0):
 src=next(q for q in original['placements'] if q['model']==model);q=copy.deepcopy(src)
 q.update(room=room,name=f'B1_{room}_Interior_{model}_{len(p["placements"])+1:03d}',template=src['name'],templateRoom=src['room'])
 place(q,x,z,a);p['placements'].append(q);return q
def deskset(room,coords):
 desks=selected(room,'BL_ResearchDesk');chairs=selected(room,'SF_TaskChair')
 # C01 has comparison chairs; other paired console chairs are handled below.
 if room=='C01':chairs=chairs[:6]
 if room=='S01':chairs=chairs[:1]
 if room=='C03':chairs=chairs[:2]
 assert len(desks)==len(coords)
 for i,(d,co) in enumerate(zip(desks,coords)):
  place(d,*co);dx,dz=rot(0,.91,co[2] if len(co)>2 else 0)
  place(chairs[i],co[0]+dx,co[1]+dz,(co[2] if len(co)>2 else 0)+180)
def wall(room,name,a,b,h=2.85,th=.14,mat='Coat'):
 walls.append(dict(room=room,name=name,a=a,b=b,h=h,th=th,mat=mat))
def line(room,name,a,b,gaps=(),h=2.85,mat='Coat'):
 # Horizontal/vertical; gaps in scalar coordinate, no overlapping corner surfaces.
 axis=0 if abs(a[0]-b[0])>.01 else 1; lo,hi=sorted([a[axis],b[axis]])
 intervals=[];cur=lo
 for g0,g1 in sorted(gaps):
  if g0>cur:intervals.append((cur,g0))
  cur=max(cur,g1)
 if cur<hi:intervals.append((cur,hi))
 for i,(v0,v1) in enumerate(intervals):
  aa=list(a);bb=list(b);aa[axis]=v0;bb[axis]=v1;wall(room,name+f'_{i+1:02}',aa,bb,h,mat=mat)
def suite(room,name,bounds,doors=None,h=2.85,ceiling=True):
 x0,z0,x1,z1=bounds;doors=doors or {}
 for side,a,b in [('S',[x0,z0],[x1,z0]),('N',[x0,z1],[x1,z1]),('W',[x0,z0+.08],[x0,z1-.08]),('E',[x1,z0+.08],[x1,z1-.08])]:line(room,name+'_'+side,a,b,doors.get(side,[]),h)
 zones.append(dict(room=room,name=name,bounds=bounds))
 if ceiling:canopy(room,name,[x0+.1,z0+.1,x1-.1,z1-.1],h+.14)
def canopy(room,name,bounds,y=3.05):ceilings.append(dict(room=room,name=name,bounds=bounds,y=y))
def light(room,x,z,y=2.75):lights.append(dict(room=room,point=[x,y,z]))

# C01: quiet reading south, comparison north; cross traffic stays around east/north.
deskset('C01',[(x,z,0) for x in [-4.7,-1.7,1.3] for z in [-5.4,-2.5]])
setall('C01','SF_ArchiveCaseRack',[(x,-7.25,0) for x in [-4.8,-2.3,.2,2.7]])
setall('C01','SF_BriefingTable',[(-3.2,5.2,0),(1.0,5.2,0)])
for q,co in zip(selected('C01','SF_TaskChair')[6:],[(-4.62,5.2,90),(-1.78,5.2,270),(-.42,5.2,90),(2.42,5.2,270)]):place(q,*co)
setall('C01','SF_SC_RecordArchive',[(-8.3,-1,90),(-8.3,2,90)])
setall('C01','BL_LoungeSofa',[(6.8,1.5,270)])
suite('C01','ReadingSuite',[-6.5,-8.0,3.9,-.4],{'N':[(-1.0,1.0)],'E':[(-4.6,-2.8)]},3.05)
suite('C01','ComparisonAlcove',[-5.4,3.0,3.6,7.7],{'S':[(-4.5,-2.7),(.2,2.0)]},1.25,False)
canopy('C01','ComparisonCanopy',[-5.4,3,3.6,7.7],3.3)
for x in [-3.8,1.0]:light('C01',x,-3.8,2.9)
light('C01',-1,5.3,3.05)

# C02: handover counter, processing office, and waiting separated from four-way transit.
deskset('C02',[(4.5,-.5,270),(4.5,2.0,270)])
setall('C02','SF_ArchiveCaseRack',[(-4.4,-2.2,90),(-4.4,-.1,90)])
setall('C02','SF_SC_RecordArchive',[(2.8,4.3,180)])
setall('C02','BL_LoungeSofa',[(-3.2,3.3,180)])
suite('C02','RecordsIntake',[2,-2.1,5.35,3.15],{'W':[(-.9,.9)]},2.75)
wall('C02','SortingScreen',[-2.7,-3.3],[-2.7,-1.0],1.3)
wall('C02','SortingBack',[-5.1,-3.3],[-2.78,-3.3],2.65)
canopy('C02','SortingCanopy',[-5.1,-3.3,-2.7,1.0],2.95)
for x,z in [(3.8,1),(-3.8,-1)]:light('C02',x,z,2.62)

# C03: compact archive aisles behind an intake threshold.
deskset('C03',[(-3.4,2.9,180),(3.3,2.9,180)])
setall('C03','SF_ArchiveCaseRack',[(-3.4,-3.9,0),(-1.15,-3.9,0),(1.1,-3.9,0),(3.35,-3.9,0),(-3.6,-1.8,90)])
setall('C03','BS_ArchiveUPS',[(4.7,1.9,270)])
setall('C03','SF_SC_IncidentReview',[(-4.8,1.1,90)])
place(selected('C03','SF_TaskChair')[2],-3.9,1.1,270)
suite('C03','ArchiveRoom',[-4.4,-4.5,4.4,-.6],{'N':[(-.9,.9)]},2.65)
for x,z in [(-2.4,-2.4),(2.4,-2.4),(0,2.5)]:light('C03',x,z,2.65 if z<0 else 3.2)

# C04: two screened consultation beds and a distinct public waiting side.
setall('C04','SF_MedicalBed',[(-2.0,-3.0,0),(2.0,-3.0,0)])
setall('C04','SF_VitalCart',[(-3.3,-1.6,90)])
setall('C04','SF_UltrasoundCart',[(3.3,-1.6,270)])
setall('C04','SF_PrivacyCurtain',[(0,-3.2,90)])
setall('C04','SF_MedicationCabinet',[(3.6,2.7,180)])
setall('C04','SF_MedicalGasStation',[(-1.5,4.5,180)])
setall('C04','SF_DoubleWashSink',[(.9,4.4,180)])
setall('C04','SF_PPEDispenser',[(4.7,.3,270)])
setall('C04','SF_ExaminationLight',[(2.8,1.1,270)])
suite('C04','StaffClinic',[-3.9,-4.9,3.9,-.7],{'N':[(-.9,.9)]},2.75)
add('C04','SF_WaitingBench',-2.6,2.4,90)
for x,z in [(-2,-2.6),(2,-2.6),(1.8,2.6)]:light('C04',x,z,2.7 if z<0 else 3.25)

# C05: a meeting pod inside a continuous external bypass; eight seats retained.
setall('C05','SF_SC_RecordArchive',[(-2.5,2.2,180),(2.5,2.2,180)])
setall('C05','BL_ConferenceTable',[(0,-.5,0)])
setall('C05','BL_PresentationBoard',[(0,2.1,180)])
setall('C05','SF_TaskChair',[(-1.4,-1.6,0),(-1.4,.6,180),(0,-1.6,0),(0,.6,180),(1.4,-1.6,0),(1.4,.6,180),(-2.5,-.5,90),(2.5,-.5,270)])
suite('C05','MeetingPod',[-3.65,-2.95,3.65,2.85],{'W':[(.2,1.8)],'E':[(.2,1.8)]},2.8)
for x in [-1.9,1.9]:light('C05',x,-.5,2.65)

# W01: six workstations within a work suite, with a separate shared reception passage.
deskset('W01',[(x,z,0) for z in [-.2,3.0] for x in [-3.8,0,3.8]])
setall('W01','SF_BriefingTable',[(-2.1,-4.8,0)])
setall('W01','SF_SC_RecordArchive',[(-5.3,1.6,90),(5.3,1.6,270)])
setall('W01','SF_WaitingBench',[(2.8,-4.8,0)])
suite('W01','StaffOffice',[-6.0,-1.5,6.0,5.4],{'S':[(-1,1)]},2.95)
for x in [-3.8,3.8]:
 for z in [.3,3.8]:light('W01',x,z,2.8)

# W02: clean preparation -> serving -> dining, dirty returns on kitchen east.
setall('W02','BL_DiningSet',[(-3.8,.4,0),(.0,.4,0),(-2.2,4.2,0)])
add('W02','BL_DiningSet',1.7,4.2,0)
setall('W02','BL_ServingCounter',[(-1.2,-3.4,0)])
setall('W02','SF_MealPreparation',[(-1.4,-6.8,0)])
setall('W02','SF_ColdStorage',[(-3.9,-6.8,0)])
setall('W02','SF_TrayDishwasher',[(.8,-6.8,0)])
setall('W02','SF_DoubleWashSink',[(2.6,-6.8,0)])
setall('W02','SF_SupplyRack',[(-5.4,-5.2,90)])
setall('W02','BL_LoungeSofa',[(-7.6,1.8,90)])
add('W02','BL_LoungeSofa',-4.6,6.8,180)
setall('W02','SF_LinenReturnCart',[(2.3,-3.8,270)])
suite('W02','Kitchen',[-6.1,-7.5,3.8,-2.8],{'N':[(-2.8,.4),(1.5,3.3)],'E':[(-5.9,-4.2)]},2.9)
wall('W02','LoungeScreen',[-6.2,-.7],[-6.2,3.8],1.2,mat='Warm')
canopy('W02','DiningCanopy',[-5.3,-1.3,3.3,5.7],3.35)
for x,z,y in [(-3,-5.3,2.75),(1.6,-5.3,2.75),(-3.6,.8,3.15),(1,3.8,3.15),(-6.8,2,3.15)]:light('W02',x,z,y)

# W03: two four-bunk sleeping rooms, outside public bypass, shared hygiene suite north.
setall('W03','BL_StaffBunk',[(x,z,0) for x in [-4.7,-2.2,1.6,4.1] for z in [-3.0,0]])
setall('W03','SF_PersonalLocker',[(x,-5.85,0) for x in [-5.1,-4.1,-3.1,-2.1,1.3,2.3,3.3,4.3]])
setall('W03','BL_SanitaryCubicle',[(-2.4,6.7,180),(-.8,6.7,180)])
setall('W03','BL_ShowerCubicle',[(.8,6.7,180),(2.4,6.7,180)])
setall('W03','BL_LaundryMachine',[(-5.8,3.9,90),(-5.8,5.0,90)])
setall('W03','SF_LinenRack',[(-7.4,-2.8,90)])
setall('W03','SF_BootDryingRack',[(-4.7,5.9,180)])
setall('W03','SF_LinenReturnCart',[(4.7,4.7,270)])
setall('W03','SF_SanitaryBasin',[(4.7,6.3,270)])
suite('W03','SleepWest',[-6,-6.35,-.2,2.0],{'N':[(-4.25,-2.65)]},2.9)
suite('W03','SleepEast',[.2,-6.35,6,2.0],{'N':[(2.05,3.65)]},2.9)
wall('W03','WestPrivacyReturn',[-4.7,3.3],[-2.2,3.3],2.45)
wall('W03','EastPrivacyReturn',[1.6,3.3],[4.0,3.3],2.45)
suite('W03','Hygiene',[-3.4,4.6,3.4,7.6],{'S':[(-.85,.85)]},2.75)
for x,z in [(-4,-2.8),(-2,.1),(2,-2.8),(4,.1),(0,5.4)]:light('W03',x,z,2.65)

# E01: access-security operations to the north, public passage/vestibule to the south.
setall('E01','SF_SC_VideoWall',[(0,4.5,180)])
setall('E01','SF_SC_OperatorDesk_A',[(-1.5,1.4,180)])
setall('E01','SF_SC_OperatorDesk_B',[(1.5,1.4,180)])
setall('E01','SF_TaskChair',[(-1.5,.4,0),(1.5,.4,0)])
setall('E01','SF_SC_RadioDutyStation',[(4.2,3.4,270)])
setall('E01','SF_SC_NetworkRack',[(-3.6,4.4,180)])
setall('E01','SF_SC_UPSRack',[(3.3,4.4,180)])
setall('E01','SF_SC_RecordArchive',[(-4.4,2.3,90)])
suite('E01','AccessOperations',[-5.3,-1.3,5.3,5.5],{'S':[(-1,1)]},3.5)
wall('E01','VestibuleScreen',[-2.1,-3.2],[-2.1,-1.6],2.4)
add('E01','SF_WaitingBench',-3.8,-5.4,0)
for x in [-2.8,2.8]:light('E01',x,2,3.2)

# E02: restricted records behind a staggered vestibule; through traffic west.
setall('E02','SF_ArchiveCaseRack',[(1.6,-2.7,90),(1.6,.2,90),(4.6,-2.7,270),(4.6,.2,270)])
deskset('E02',[(1.1,3.9,180)])
setall('E02','SF_SC_NetworkRack',[(4.6,3.9,180)])
setall('E02','SF_SR_EvidenceCabinet',[(0,-4.6,0)])
setall('E02','BL_LoungeSofa',[(-5.6,.3,90)])
suite('E02','RestrictedArchive',[-2.3,-5.6,5.6,5.1],{'W':[(.2,1.8)]},2.95)
wall('E02','ArchiveVestibule',[.0,-1.6],[.0,1.9],2.75)
for x,z in [(3,-2.8),(3,.1),(1.5,3.6)]:light('E02',x,z,2.78)

# E03: private sleeping south-west, washing south-east, shift handover north.
setall('E03','BL_StaffBunk',[(x,z,0) for x in [-4.7,-2.2] for z in [-3.0,0]])
setall('E03','SF_PersonalLocker',[(x,-5.7,0) for x in [-5.1,-4.1,-3.1,-2.1]])
setall('E03','BL_SanitaryCubicle',[(3.0,-4.6,0)])
setall('E03','BL_ShowerCubicle',[(5,-4.6,0)])
setall('E03','BL_LaundryMachine',[(5.7,-1.4,270)])
setall('E03','SF_SanitaryBasin',[(3.2,-1,180)])
setall('E03','SF_SC_GearLockers',[(.6,5.6,180)])
setall('E03','SF_SR_ShiftEquipment',[(3.6,5.4,180)])
setall('E03','SF_SC_RadioDutyStation',[(-3.0,5.6,180)])
setall('E03','BL_LoungeSofa',[(-5.7,3.7,90)])
setall('E03','SF_BootDryingRack',[(5.7,1.2,270)])
suite('E03','GuardRest',[-6,-6.2,-.2,2.0],{'N':[(-4.25,-2.65)]},2.9)
wall('E03','RestPrivacyReturn',[-4.7,3.3],[-2.2,3.3],2.45)
suite('E03','GuardHygiene',[1.9,-5.6,6.7,.4],{'W':[(-1.8,-.2)]},2.8)
wall('E03','HandoverBack',[-1.5,6.8],[4.7,6.8],2.75)
canopy('E03','HandoverCanopy',[-1.5,3.9,4.7,6.8],3.05)
for x,z in [(-3.8,-3),(-2,.3),(4,-2.8),(2,5)]:light('E03',x,z,2.7)

# N01: paired analysis banks facing inward; central discussion and south arrival space.
deskset('N01',[(-4.0,z,90) for z in [-.1,2.5,5.1]]+[(4.0,z,270) for z in [-.1,2.5,5.1]])
setall('N01','SF_ArchiveCaseRack',[(x,6.55,180) for x in [-2.6,0,2.6]])
setall('N01','SF_SC_RecordArchive',[(-6.0,-3.6,90),(6.0,-3.6,270)])
add('N01','SF_BriefingTable',0,2.5,90)
suite('N01','AnalysisSuite',[-5.8,-1.7,5.8,7.2],{'S':[(-4.7,-2.9),(2.9,4.7)]},2.95,False)
canopy('N01','WestAnalysis',[-6,-1.6,-2.4,6.4],3.1)
canopy('N01','EastAnalysis',[2.4,-1.6,6,6.4],3.1)
wall('N01','ArrivalScreen',[-1.7,-3.4],[1.7,-3.4],1.2)
for x in [-3.5,3.5]:
 for z in [.4,4.5]:light('N01',x,z,2.85)

# S01: two orderly rack rows, aisle/service clearance, separate backup operator bay.
servers=[q for q in p['placements'] if q['room']=='S01' and q['model'].startswith('BS_ServerRack')]
for q,(x,z) in zip(servers,[(x,z) for z in [-3.8,.3] for x in [-3.6,-1.2,1.2,3.6]]):place(q,x,z,0)
setall('S01','BS_ArchiveUPS',[(-6.7,-2,90),(6.7,-2,270)])
deskset('S01',[(-3,5.3,180)])
setall('S01','SF_SC_IncidentReview',[(3,5.3,180)])
place(selected('S01','SF_TaskChair')[1],3,4.35,0)
setall('S01','BS_FilterBank',[(0,-7.3,0)])
setall('S01','SF_ArchiveCaseRack',[(-6.4,3.8,90)])
suite('S01','BackupServerRoom',[-5.6,-5.6,5.6,2.6],{'N':[(-1,1)],'W':[(-2.5,-.8)],'E':[(-2.5,-.8)]},3.15)
for x,z in [(-3.4,-2),(3.4,-2),(-3.4,1.4),(3.4,1.4)]:light('S01',x,z,2.95)

# Move desk-top recorders with their original support desk; do not leave floating props.
for q in p['placements']:
 if q['model']!='BL_HandheldRecorder':continue
 old=next(x for x in original['placements'] if x['name']==q['name'])
 desks=[x for x in original['placements'] if x['room']==q['room'] and x['model']=='BL_ResearchDesk']
 d=min(desks,key=lambda x:sum((x['position'][i]-old['position'][i])**2 for i in [0,2]))
 new=next(x for x in p['placements'] if x['name']==d['name'])
 ox,oz=rot(old['position'][0]-d['position'][0],old['position'][2]-d['position'][2],-d['yaw'])
 dx,dz=rot(ox,oz,new['yaw']);q['position']=[new['position'][0]+dx,old['position'][1],new['position'][2]+dz];q['yaw']=new['yaw']

# Deliberate destinations; detailed reachable approach points resolved against real Unity colliders.
for q in p['placements']:
 if q['model']=='BL_HandheldRecorder':continue
 x,z=rot(q['center'][0],q['center'][2],q['yaw']);x+=q['position'][0];z+=q['position'][2]
 local=(0,q['size'][2]/2+.66)
 if q['model']=='SF_TaskChair':local=(0,-q['size'][2]/2-.40)
 if q['model']=='BL_StaffBunk':local=(q['size'][0]/2+.52,.65)
 if q['model']=='SF_ExaminationLight':local=(0,1.0)
 dx,dz=rot(*local,q['yaw'])
 if q['model'] in ['BL_ResearchDesk','SF_SC_OperatorDesk_A','SF_SC_OperatorDesk_B','SF_SC_IncidentReview']:
  candidates=[c for c in p['placements'] if c['room']==q['room'] and c['model']=='SF_TaskChair']
  if candidates:
   chair=min(candidates,key=lambda c:sum((c['position'][i]-q['position'][i])**2 for i in [0,2]))
   if math.hypot(chair['position'][0]-x,chair['position'][2]-z)<1.5:
    ox,oz=rot(0,-chair['size'][2]/2-.40,chair['yaw']);x=chair['position'][0]+ox;z=chair['position'][2]+oz;dx=dz=0
 p['workspaces'].append(dict(room=q['room'],name=q['name'],point=[x+dx,0,z+dz],model=q['model']))
for w in walls:
 if w['room'] in ['C01','C05','W01','N01','E01'] and '_S_' in w['name'] and w['h']>2.6:w['glazed']=True
p['interior']={'version':'V0.01','date':'2026-11-12','author':'송예찬','walls':walls,'ceilings':ceilings,'zones':zones,'lights':lights,'purpose':'Research data workflow and staff living; no subject experiments or staff control.'}
(H/'layout.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(placements=len(p['placements']),walls=len(walls),ceilings=len(ceilings),relocatedLights=len(lights),zones=len(zones))))
