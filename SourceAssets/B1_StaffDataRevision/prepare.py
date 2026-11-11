"""B1 staff/data correction. No scene rebuild; clone validated furniture in Editor."""
from pathlib import Path
import json, math, sys, copy, hashlib, shutil
H=Path(__file__).resolve().parent; R=H.parents[1]; OLD=R/'SourceAssets/B1_FullFloor'
PROJECT=R/'Unity/After_Seconds_Build_V0.01'; O=R/'Docs/Review/2026-11-11_B1_StaffData'
O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(PROJECT/'Temp/ZFightingReview/deps'))
from shapely.geometry import Polygon,Point,LineString
from shapely.affinity import rotate,translate
from PIL import Image,ImageDraw,ImageFont
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if (H/'before_layout.json').exists():raise RuntimeError('One-time preparation already run')
old=json.loads((OLD/'layout.json').read_text(encoding='utf8'));write(H/'before_layout.json',old)
tmp=PROJECT/'Temp/B1_StaffData';tmp.mkdir(parents=True,exist_ok=True)
shutil.copy2(PROJECT/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B1_Circular.unity',tmp/'Before.unity')
protected=json.loads((OLD/'protected_before.json').read_text(encoding='utf8'))
write(H/'protected_before.json',protected)
names={'C01':('연구 자료 열람·대조','RESEARCH DATA LIBRARY'),'C02':('연구 기록 인계·정리','RECORDS INTAKE'),'C03':('연구 기록 보관','RESEARCH ARCHIVE'),'C04':('직원 의무실','STAFF CLINIC'),'C05':('직원 회의·보고','STAFF MEETING'),'W01':('연구원 사무실','RESEARCH OFFICES'),'W02':('직원 식당·휴게·조리','STAFF DINING'),'W03':('연구원·지원인력 생활','STAFF QUARTERS'),'E01':('출입 보안 업무','ACCESS SECURITY'),'E02':('책임자·기밀 기록','RESTRICTED ARCHIVE'),'E03':('경비 숙소·교대 대기','GUARD QUARTERS'),'N01':('연구 데이터 분석','RESEARCH DATA ANALYSIS'),'S01':('백업 서버·기록 대조','BACKUP SERVERS')}
changed={'C01','C02','C05','N01'}
plan=copy.deepcopy(old);plan['name']='연구 데이터·직원 생활층';plan['full_role']='연구 자료 분석·보관·업무와 직원 생활';plan['theme']='실험체 없는 상층 직원 공간. 자료 인계·열람·분석·보관과 숙소·식당·위생 시설.'
plan['subject_access_rule']='실험체의 정상 활동 범위는 B5/B4. B4→B3 상행 경계부터 진입 금지. 플레이어 탈출은 경계 침범이며 B1 현장 실험은 없음.'
for r in plan['rooms']:
 if r['id'] in names:r['name']=names[r['id']][0]
plan['placements']=[p for p in old['placements'] if p['room'] not in changed]
plan['workspaces']=[p for p in old['workspaces'] if p['room'] not in changed]
templates={p['model']:p for p in old['placements'] if p['room'] not in changed}
blocks={c:[] for c in changed}; serial={c:0 for c in changed}; created=[]
def turn(x,z,a):a=math.radians(a);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
def rect(w,d,x,z,a):return translate(rotate(Polygon([(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]),-a,origin=(0,0)),xoff=x,yoff=z)
def add(room,model,x,z,yaw=0,seat=False,record=False):
 t=templates[model];p=copy.deepcopy(t);serial[room]+=1;p.update(room=room,name=f'B1_{room}_Data_{model.split("_",1)[1]}_{serial[room]:02}',yaw=yaw,template=t['name'],templateRoom=t['room']);w,h,d=p['size'];cx,cy,cz=p['center'];ox,oz=turn(cx,cz,yaw);p['position']=[x-ox,-(cy-h/2),z-oz];p['role']='Seating' if seat else 'Equipment';created.append(p);plan['placements'].append(p);blocks[room].append(rect(w,d,x,z,yaw).buffer(.12))
 if not seat:
  dx,dz=turn(0,d/2+.67,yaw);plan['workspaces'].append(dict(room=room,name=p['name'],point=[x+dx,0,z+dz]));blocks[room].append(rect(w,1.1,x+turn(0,d/2+.55,yaw)[0],z+turn(0,d/2+.55,yaw)[1],yaw))
 if model=='BL_ResearchDesk':
  dx,dz=turn(0,d/2+.46,yaw);add(room,'SF_TaskChair',x+dx,z+dz,(yaw+180)%360,seat=True);side=turn(.78,d/2+.46,yaw);plan['workspaces'][-1]['point']=[x+side[0],0,z+side[1]]
 return p
# Library desks face the shared aisle; archive shelves belong to the same work area.
for x in [-5.2,-2.5,.2]:
 for z in [-6.0,-2.8]:add('C01','BL_ResearchDesk',x,z)
for x in [-5.2,-2.4,.4,3.2]:add('C01','SF_ArchiveCaseRack',x,-9.0)
for x in [-2.8,1.2]:
 add('C01','SF_BriefingTable',x,5.0)
 for dx in [-1.42,1.42]:add('C01','SF_TaskChair',x+dx,5,90 if dx<0 else 270,seat=True)
for z in [.0,3.0]:add('C01','SF_SC_RecordArchive',-9,z,90)
add('C01','BL_LoungeSofa',5.7,-1.5,270)
for x in [-3.2,0,3.2]:
 for z in [-.5,2.8]:add('N01','BL_ResearchDesk',x,z)
for x in [-3.2,0,3.2]:add('N01','SF_ArchiveCaseRack',x,6.6)
add('N01','SF_SC_RecordArchive',-7.3,.3,90);add('N01','SF_SC_RecordArchive',7.3,.3,270)
add('C05','SF_BriefingTable',0,0)
for x in [-1.4,1.4]:
 for z in [-.45,.45]:add('C05','SF_TaskChair',x,z,90 if x<0 else 270,seat=True)
# Small record intake / meeting storage uses vacant wall sectors outside door approaches.
for room,models in {'C02':['BL_ResearchDesk','BL_ResearchDesk','SF_ArchiveCaseRack','SF_ArchiveCaseRack','SF_SC_RecordArchive','BL_LoungeSofa'],'C05':['SF_SC_RecordArchive','SF_SC_RecordArchive']}.items():
 r=next(r for r in plan['rooms'] if r['id']==room);rad=r['r'];paths=[LineString([(0,0),(d['x'],d['z'])]).buffer(.9,cap_style=2) for d in r['doors']]
 for model in models:
  w,h,d=templates[model]['size'];limit=math.sqrt(rad*rad-h*h)-.35;found=None
  for step in range(32):
   rr=limit-d/2-.25-step*.15
   if rr<.5:break
   for angle in range(0,360,2):
    a=math.radians(angle);x,z=rr*math.cos(a),rr*math.sin(a);yaw=270-angle;poly=rect(w,d,x,z,yaw);dx,dz=turn(0,d/2+.75,yaw);ap=rect(w+(.4 if model=='BL_ResearchDesk' else 0),1.5,x+dx,z+dz,yaw)
    if not Point(0,0).buffer(limit).covers(poly) or any(poly.intersects(q) for q in paths):continue
    if any(poly.buffer(.18).intersects(q) or ap.intersects(q) for q in blocks[room]):continue
    found=(x,z,yaw);break
   if found:break
  if not found:raise RuntimeError(f'No room for {room} {model}')
  add(room,model,*found)
# Desks contain built-in papers, keyboards, monitors; clone clean furniture, no new mesh assets.
plan['refinement']='2026-11-11 사용자 정정: B5/B4 실험체 구역, B3 이상 출입 금지. B1 연구 데이터/직원 생활. 네 공동 시험설비 교체.'
write(H/'layout.json',plan);write(H/'changes.json',dict(replaceRooms=sorted(changed),remove=[p for p in old['placements'] if p['room'] in changed],add=created,roomNames=names))
print(json.dumps(dict(removed=sum(p['room'] in changed for p in old['placements']),added=len(created),total=len(plan['placements'])),ensure_ascii=False))
# Dedicated sign/display text is generated from source, retaining existing B1 texture GUIDs.
out=PROJECT/'Assets/Afrer_Seconds/05.Model/Environment/B1/Textures'; props=PROJECT/'Assets/Afrer_Seconds/05.Model/Props/B1/Textures'
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/consola.ttf',n)
for code,(kr,en) in names.items():
 im=Image.new('RGB',(512,128),(36,47,48));d=ImageDraw.Draw(im);d.rectangle((4,4,507,123),outline=(139,157,150),width=2);d.text((20,12),'B1 / '+code,font=font(47),fill=(225,227,209));d.text((20,80),en,font=font(22),fill=(182,198,188));im.save(out/f'BL_Sign_{code}.png')
for filename,title,lines in [('BL_Display_01.png','RESEARCH / RECORD INDEX',['REPORT     REVISION    STATUS','S03-042    R06         FILED','S03-043    R02         REVIEW','S03-044    R01         RECEIVED']),('BL_DataReview.png','RESEARCH / REPORT REVIEW',['DATA SOURCE     B4 LAB ARCHIVE','DOCUMENT        S03-043 / R02','MEETING NOTES   ANALYSIS TEAM','REVIEW COPY     LOCAL / READ ONLY']),('BL_AccessSecurity.png','ACCESS / B4 UPPER BOUNDARY',['ZONE       B4 -> B3 / STAFF ONLY','STAIR A    ACCESS LOG AVAILABLE','STAIR B    ACCESS LOG AVAILABLE','CARGO      STAFF TRANSFER RECORD'])]:
 im=Image.new('RGB',(512,256),(17,28,33));d=ImageDraw.Draw(im);d.rectangle((0,0,512,38),fill=(38,66,73));d.text((14,10),title,font=font(21),fill=(216,225,216))
 for i,line in enumerate(lines):d.text((16,63+i*36),line,font=font(17),fill=(182,201,193));d.line((16,90+i*36,494,90+i*36),fill=(49,67,70))
 d.text((16,233),'FACILITY RECORD / STATIC ART DISPLAY',font=font(13),fill=(118,143,144));im.save(props/filename)
