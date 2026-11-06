"""Revision of delivered data. Never executes the other workspace's generators."""
import json,math,copy,hashlib,sys,shutil
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
HERE=Path(__file__).resolve().parent; REPO=HERE.parents[1]
OUT=REPO/'Docs/도면/원형공동'; OUT.mkdir(parents=True,exist_ok=True)
SOURCE=Path('C:/Users/503-26/Documents/Codex/2026-11-06/dl/outputs/after_seconds_multilevel')
d=json.loads((HERE/'source_design.json').read_text(encoding='utf-8'))
if (HERE/'validated_routes.json').exists():
 validated=json.loads((HERE/'validated_routes.json').read_text())
 for f in d['floors']:
  if f['id'] in validated:
   for k,points in validated[f['id']].items():
    f[k]=points;f['route_length' if k=='route' else 'alternate_length']=round(sum(math.dist(a,b) for a,b in zip(points,points[1:])),2)
audit=json.loads((HERE/'source_audit.json').read_text(encoding='utf-8'))
d.update(title='After Seconds 원형 공동 제작 설계 V0.03',version='V0.03',author='송예찬',status='사용자 논의 반영 / 상세 치수 제작 검수 중 / 원본 V0.02와 구분',source_revision=audit['source_hashes'])
styles={
'B5':dict(label='창백한 격리 생활',wall='#C5D3DE',floor='#606D79',metal='#4B5967',accent='#DFEDF5',light='#C2DDFF',ambient=.21,description='옅은 청색·흰색. 낮은 채도와 눈부심을 억제한 청백색.'),
'B4':dict(label='어두운 무채색 연구',wall='#62666B',floor='#35393E',metal='#252A30',accent='#A6ACB3',light='#E6EBF1',ambient=.12,description='시험 대상과 조작부의 국부 작업광. 색 강조를 줄인 회색·흑연색.'),
'B3':dict(label='소등된 보관 구역',wall='#727A82',floor='#424B54',metal='#434C55',accent='#B2BEC7',light='#D5E3EC',ambient=.06,description='보관부 기본 소등. 출입·계단 최소 안내광과 작업대 별도 회로.'),
'B2':dict(label='철색과 붉은 보조등',wall='#5C6268',floor='#363B40',metal='#717B85',accent='#AA3635',light='#FF4940',ambient=.13,description='붉은 상시 보조등. 계단·밸브에는 중성 작업광. 경보 표현은 별도.'),
'B1':dict(label='직원 생활과 관제',wall='#BEB8AA',floor='#676660',metal='#686A67',accent='#827160',light='#FFE6C9',ambient=.19,description='따뜻한 회색·아이보리. 생활부 온화한 빛과 실험부 중성광.'),
'1F':dict(label='폐공장과 외광',wall='#8D8D80',floor='#62635C',metal='#676C5E',accent='#855B43',light='#E3EAF1',ambient=.26,description='녹·먼지·낡은 녹색 도장. 외광과 최근 사용된 작업 구역.'),
}
d['floor_art_direction']=styles
d['authoring_scope']={'runtime_scripts':False,'door_animation':False,'light_switch_logic':False,'enemy_AI':False,'minimap':False,'first_scene':'Level_B5_Circular.unity','first_stage':'B5 핵심 공동 4개·코어 3개·터널 7개 / 건축·기존 소품 기반 첫 제작'}
d['wayfinding']={'codes':[
{'code':'R1','purpose':'직원 출입·교대 / 지상 출입 구역 연결','color':'#DEE6E9','pattern':'double-solid'},
{'code':'S1','purpose':'시료 이송·인계','color':'#5E9C9A','pattern':'single-solid-square'},
{'code':'M1','purpose':'설비 점검·정비','color':'#BC9B5A','pattern':'dashed'}],
'rule':'층별 색과 별개로 모든 층에서 같은 의미. 도면 예상 경로와 월드 업무 안내선을 구분한다. 게임 UI 경로 표시 없음.',
'records':[{'floor':'B5','room':'C02','text':'교대자는 R1 이중선을 따라 계단 A 인계 지점으로 이동. 관찰 공동 통과 전 근무자 확인.'}, {'floor':'B4','room':'C03','text':'측정 종료 후 시료는 S1 이송선으로 인계. 직원 퇴근 이동은 R1 계단 B 방향.'},{'floor':'B3','room':'C05','text':'야간 회수 시 해당 보관 구역의 작업등만 점등. 회수 후 소등, 시료 이송 설비 전원 유지.'},{'floor':'B1','room':'E02','text':'지상 출입 검문 인계는 R1 직원 동선을 따른다. 정비 노선 M1과 혼동하지 말 것.'}]}
d['guidance_routes']=[]
for f in d['floors']:
 for code,key in [('R1','route'),('S1','alternate')]:
  d['guidance_routes'].append({'floor':f['id'],'code':code,'points':f[key],'status':'경로 가안 / 실제 장비·문·계단 반영 후 표면 배치','source':'V0.02 검증 이동 경로 기반'})
 if f['id']=='B2':d['guidance_routes'].append({'floor':'B2','code':'M1','points':[[13,8.5],[12.8,2.9],[12.8,-3.5],[25.2,-3.5],[25.2,2.9],[25.2,8.5]],'status':'상하 경로는 B2 mezzanine의 height 참조'})
for c in d['catalog']:
 if c['code']=='P38':c.update(asset='Assets/Afrer_Seconds/05.Model/Enemy/CCTV_SecurityCamera_Articulated.prefab',purpose='Fixed_Base → Pan_Yaw → Head_Tilt. 아트 분리 모델. 감지·회전 기능 미구현')
 if c['code']=='P23':c['preferred_variants']='Assets/Afrer_Seconds/05.Model/Props/Common/SW_Case_*'
 if c['code']=='P40':c['production_note']='2.4m 개구부용 문틀·포켓 재제작. 기존1.5m 문을 비균등 확대하지 않음. 열린 문짝은 벽 포켓에 수납.'
mezz={'floor':'B2','room':'C02','center':[19,1],'height':3.6,'cavern_radius':11,'status':'제작 치수 가안','deck_rects':[
{'name':'North','x':19,'v':-3.5,'w':14.6,'d':2.2},
{'name':'West','x':12.8,'v':-.3,'w':2.2,'d':6.4},
{'name':'East','x':25.2,'v':-.3,'w':2.2,'d':6.4}],
'stairs':[{'id':'West','x':12.8,'v_bottom':8.5,'v_top':2.9,'w':1.4,'steps':20,'tread':.28,'rise':.18},{'id':'East','x':25.2,'v_bottom':8.5,'v_top':2.9,'w':1.4,'steps':20,'tread':.28,'rise':.18}],
'solid_workpads':[{'x':12.8,'v':-2.3,'w':2.2,'d':1.6},{'x':25.2,'v':-2.3,'w':2.2,'d':1.6}],
'rules':['グレーチング'.replace('グレーチング','그레이팅')+'은 상하 시야가 통함','시야 차단은 장비·철판 작업대에서 확보','기둥·보·연결판·난간·발끝막이·계단참·베벨 포함','다른 층으로 연결되는 계단과 별개'],
'lower_props':[{'code':'P20','x':16.5,'v':1.0},{'code':'P20','x':21.5,'v':1.0},{'code':'P19','x':16,'v':4.5},{'code':'P19','x':22,'v':4.5}],
'route3d':[[12.8,0,8.5],[12.8,3.6,2.9],[12.8,3.6,-3.5],[25.2,3.6,-3.5],[25.2,3.6,2.9],[25.2,0,8.5]]}
d['mezzanines']=[mezz]
d['light_circuits']=[]
f3=next(f for f in d['floors'] if f['id']=='B3')
dark={'C01','C02','W01','W02','E03'}
for r in f3['rooms']:
 if r['kind']!='cavern':continue
 t=next(t for t in f3['tunnels'] if r['id'] in [t['a'],t['b']]);p=t['p'] if t['a']==r['id'] else t['q'];dx=r['x']-p[0];dv=r['v']-p[1];le=math.hypot(dx,dv)
 d['light_circuits'].append({'id':'B3-L-'+r['id'],'room':r['id'],'default_on':r['id'] not in dark,'control':'manual-zone','switch':[p[0]+dx/le*.9-dv/le*.8,1.25,p[1]+dv/le*.9+dx/le*.8],'emergency_guidance':'출입·계단 최소 안내광 별도 유지','cold_storage_power':'조명 회로와 분리 / 장비는 계속 가동','logic_status':'사용자 직접 구현 예정'})
for p in d['placements']:
 if p['floor']=='B3' and p['code']=='P39':p.update(light_control='수정본 light_circuits 우선',default_on=p['room'] not in dark)
 if p['code']=='P38':p['review_status']='기존 일괄 배치 가안 / security_plan의 후보 구역 우선'
d['security_plan']={'roles':{'guard':'추격','cctv':'경비 호출','researcher':'도주하며 주변 알림','director':'엔딩'},'candidate_rooms':{'B5':['C02','C03'],'B4':['C01','C04'],'B3':['C04','C05'],'B2':['C01','C02'],'B1':['C01','C05'],'1F':['C03']},'B3':'보관 공동 상주 인원 최소화. 작업·인계 구역 중심. 소등이 감지 면역을 뜻하지 않음.','state':'가안 / AI·정확한 인원·시야각 미구현'}
d['manufacturing']={'bevel':'모든 새 예각, 부품 크기에 맞는 폭','walls':'원형 바닥 반구 / 터널은 연속 반원 단면','wear':'불규칙한 먼지·손때·닦임·카트 접촉. 장식 문양 금지','doors':'개방시 양쪽 포켓 수납','validation_pending':['전체 실내 칸막이·문 정합','실제 경비 감지','전체층 계단·승강기 기능','장비 전체 3264명세의 실제 배치·중복 해소']}
# Explicitly record crossings: they must be shared junctions, not intersecting solid walls.
d['tunnel_junctions']=[]
def intersect(a,b,c,e):
 dx,dy=b[0]-a[0],b[1]-a[1];ex,ey=e[0]-c[0],e[1]-c[1];den=dx*ey-dy*ex
 if abs(den)<1e-8:return None
 t=((c[0]-a[0])*ey-(c[1]-a[1])*ex)/den;u=((c[0]-a[0])*dy-(c[1]-a[1])*dx)/den
 return [a[0]+t*dx,a[1]+t*dy] if .02<t<.98 and .02<u<.98 else None
for f in d['floors']:
 for i,a in enumerate(f['tunnels']):
  for b in f['tunnels'][i+1:]:
   p=intersect(a['p'],a['q'],b['p'],b['q'])
   if p:d['tunnel_junctions'].append({'floor':f['id'],'tunnels':[a['id'],b['id']],'point':p,'treatment':'개방 교차부 / 벽·천장 합집합으로 제작; 원본 연결 그래프의 추가 연결 검토'})
(OUT/'facility_layout.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
pdfmetrics.registerFont(TTFont('Malgun','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunB','C:/Windows/Fonts/malgunbd.ttf'))
W,H=1191,842; c=canvas.Canvas(str(OUT/'AfterSeconds_원형공동_제작설계.pdf'),pagesize=(W,H));c.setTitle(d['title']);c.setAuthor('송예찬')
page_names=[];INK='#243542';MUT='#607383'
def txt(x,y,s,size=11,color=INK,bold=False):
 c.setFillColor(HexColor(color));c.setFont('MalgunB' if bold else 'Malgun',size);c.drawString(x,H-y,str(s))
def line(x1,y1,x2,y2,col=INK,width=1):c.setStrokeColor(HexColor(col));c.setLineWidth(width);c.line(x1,H-y1,x2,H-y2)
def rect(x,y,w,h,col,stroke=None):
 c.setFillColor(HexColor(col));c.setStrokeColor(HexColor(stroke or col));c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))
def wrap(x,y,s,width,size=11,leading=19):
 buf=''
 for ch in s:
  if pdfmetrics.stringWidth(buf+ch,'Malgun',size)>width:txt(x,y,buf,size);y+=leading;buf=''
  buf+=ch
 if buf:txt(x,y,buf,size)
 return y+leading
def header(title,sub,name):
 c.setFillColor(HexColor('#FAFCFD'));c.rect(0,0,W,H,fill=1,stroke=0)
 txt(42,36,'AFTER SECONDS / 제작 설계 V0.03',10,MUT,True);txt(42,76,title,24,INK,True);txt(42,105,sub,10,MUT)
 line(42,121,1149,121,'#C6D0D8');page_names.append(name)
def finish():
 line(42,793,1149,793,'#C6D0D8');txt(42,816,'송예찬 | 2026-11-06 | 게임 제작용 가안 · 런타임 코드 미구현',9,MUT);txt(1090,816,f'{len(page_names):02}',10,MUT);c.showPage()
header('완성본 대조와 수정 기준','원본의 생활·시설 구성을 보존하고 최근 사용자 합의와 연결한다.','00_대조결과')
items=[('유지','독립 원형 공동·연속 터널 / 6층 / 86공간 / 113동층 연결 / 5주요 층간 연결'),('유지','145품목·3,264명세·27생활 활동. 구성 부품을 독립 장비 대수로 합산하지 않음.'),('추가','B2 냉각·펌프 C02: 그레이팅 메자닌 + 두 계단 + 상하 관찰·차폐'),('추가','R1 직원·S1 시료·M1 정비 안내선 및 인수인계 문구와 도면 경로'),('수정','B5 창백한 청백색 / B4 어두운 무채색 / B2 철색·붉은 보조등 / B1 유지'),('추가','B3 저인원 보관부 기본 소등. 수동 구역 조명·스위치 위치·별도 안내광'),('수정','CCTV 회전 분리 모델을 우선 후보로 변경. 일괄 방별 배치를 감시 구역별 재검토'),('제작','B5 핵심 공동 4개 + 코어 3개 + 터널 7개부터 새 씬에 제작 시작'),('남음','내부 칸막이, 전체 소품 정합, 모든 층의 문·계단·승강기 상세와 실제 AI 검증')]
yy=167
for a,b in items:txt(52,yy,a,13,'#29636D',True);yy=wrap(135,yy,b,970,13,22)+25
finish()
header('층별 분위기와 색감','사용자 수정안 우선. 색은 재질 바탕과 작업광에 나누고 안내선 의미는 공통으로 유지한다.','01_층별분위기')
for i,(fid,s) in enumerate(styles.items()):
 y=154+i*102;txt(50,y+20,fid+'  '+s['label'],16,INK,True)
 for j,k in enumerate(['wall','floor','metal','accent','light']):rect(53+j*58,y+38,48,28,s[k])
 wrap(395,y+28,s['description'],710,13,23)
finish()
def draw_plan(f,core=False,lights=False):
 rooms=[r for r in f['rooms'] if not core or not r.get('wing')]; ids={r['id'] for r in rooms}
 ts=[t for t in f['tunnels'] if t['a'] in ids and t['b'] in ids]
 minx=min(r['x']-r['r'] for r in rooms)-4;maxx=max(r['x']+r['r'] for r in rooms)+4
 minv=min(r['v']-r['r'] for r in rooms)-4;maxv=max(r['v']+r['r'] for r in rooms)+4
 scale=min(810/(maxx-minx),590/(maxv-minv)); X=lambda x:48+(x-minx)*scale;Y=lambda v:155+(v-minv)*scale
 for t in ts:line(X(t['p'][0]),Y(t['p'][1]),X(t['q'][0]),Y(t['q'][1]),'#D9E1E7',t['w']*scale+2);line(X(t['p'][0]),Y(t['p'][1]),X(t['q'][0]),Y(t['q'][1]),'#EEF2F5',t['w']*scale)
 for r in rooms:
  color='#D9E0E6' if lights and r['id'] in dark else '#EFF4F7'
  c.setFillColor(HexColor(color));c.setStrokeColor(HexColor('#748C9C'));c.setLineWidth(1.2)
  c.circle(X(r['x']),H-Y(r['v']),r['r']*scale,fill=1,stroke=1)
  txt(X(r['x'])-13,Y(r['v'])+4,r['id'],9 if core else 8,INK,True)
 if core:
  for p in d['placements']:
   if p['floor']==f['id'] and p['room'] in ids and p.get('role')=='독립 배치' and p['code'] not in ['P38','P39','P40','P41']:
    c.saveState();c.translate(X(p['x']),H-Y(p['v']));c.rotate(-p['yaw']);c.setFillColor(HexColor('#ABB8C3'));c.rect(-p['w']*scale/2,-p['d']*scale/2,p['w']*scale,p['d']*scale,stroke=0,fill=1);c.restoreState()
 for key,col,dash in [('route','#197B81',False),('alternate','#BE8C46',True)]:
  pts=f[key];c.setDash(5,3) if dash else c.setDash()
  for a,b in zip(pts,pts[1:]):line(X(a[0]),Y(a[1]),X(b[0]),Y(b[1]),col,1.9 if core else 1.3)
  c.setDash()
 if f['id']=='B2':
  for r in mezz['deck_rects']:rect(X(r['x']-r['w']/2),Y(r['v']-r['d']/2),r['w']*scale,r['d']*scale,'#8C9AA5','#405463')
 if lights:
  for q in d['light_circuits']:
   if q['room'] not in ids:continue
   x,h,v=q['switch'];rect(X(x)-3,Y(v)-3,6,6,'#E6B96C')
 # Draw identifiers last so equipment and route lines cannot obscure them.
 for r in rooms:
  rect(X(r['x'])-15,Y(r['v'])-8,30,17,'#FAFCFD');txt(X(r['x'])-11,Y(r['v'])+4,r['id'],9 if core else 8,INK,True)
  if core:txt(X(r['x'])-15,Y(r['v'])+19,f"D {r['r']*2}m",7,MUT)
 yy=162
 for r in rooms:yy=wrap(898,yy,r['id']+'  '+r['name'],245,10,16)+9
 yy=max(yy+8,580);txt(898,yy,'실선: 예상 주 경로',10,'#197B81');txt(898,yy+20,'점선: 예상 우회 경로',10,'#BE8C46')
 wrap(898,yy+50,'경로는 도면에만 표시. 실제 바닥 안내선은 R1/S1/M1 업무 코드로 제작한다.',240,10,18)
 if lights:wrap(898,yy+110,'회청색 공동: 기본 소등 보관부. 노란 사각: 수동 구역 스위치 후보.',240,10,18)
 txt(55,766,f"층 기준 Y={f['z']}m / X 동쪽 · v 남쪽 · Unity Z=-v / 터널 폭4.2m·높이3.4m / 문 유효폭2.4m (가안)",10,MUT)
for f in d['floors']:
 header(f['id']+'  '+f['name']+' 전체 시설',f.get('full_role',f['theme'])+' / 외곽 생활·운영 공동까지 보존',f"02_{f['id']}_전체")
 draw_plan(f);finish()
for f in d['floors']:
 header(f['id']+' 핵심 구역과 예상 이동',styles[f['id']]['label']+' / 배치 명세는 큰 설비만 표시, 세부 소품은 후속 정합',f"03_{f['id']}_핵심")
 draw_plan(f,True,f['id']=='B3');finish()
header('B2 냉각·펌프 공동: 상하 잠입','부분 그레이팅 메자닌 / 계단 두 곳 / 지지 구조와 상하 시야를 함께 제작','04_B2_메자닌')
cx,cy,S=310,420,20
c.setStrokeColor(HexColor('#708696'));c.circle(cx,H-cy,11*S,fill=0)
for r in mezz['deck_rects']:
 x=cx+(r['x']-19-r['w']/2)*S;y=cy+(r['v']-1-r['d']/2)*S;rect(x,y,r['w']*S,r['d']*S,'#C1CBD2','#5F7685')
 for i in range(int(r['w']*S/7)):line(x+i*7,y,x+i*7,y+r['d']*S,'#7A8C97',.5)
for s in mezz['stairs']:
 x=cx+(s['x']-19-s['w']/2)*S;y=cy+(s['v_top']-1)*S;rect(x,y,s['w']*S,(s['v_bottom']-s['v_top'])*S,'#E7EBEE','#5F7685')
 for i in range(21):line(x,y+i*.28*S,x+s['w']*S,y+i*.28*S,'#647E8E',.5)
for r in mezz['solid_workpads']:rect(cx+(r['x']-19-r['w']/2)*S,cy+(r['v']-1-r['d']/2)*S,r['w']*S,r['d']*S,'#566975')
txt(94,694,'평면: 중앙 설비와 상하 시야를 열어 둔다',12,INK,True)
# Section through deck and floor, left/right stairs shown schematically.
ox,oy,ss=875,450,18
c.setStrokeColor(HexColor('#637B8B'));p=c.beginPath()
for i in range(61):
 a=math.pi*i/60;x=ox+11*ss*math.cos(a);y=oy-11*ss*math.sin(a)
 p.moveTo(x,H-y) if i==0 else p.lineTo(x,H-y)
c.drawPath(p);line(ox-11*ss,oy,ox+11*ss,oy,'#637B8B',2)
for sign in [-1,1]:
 rect(ox+(sign*6.2-1.1)*ss,oy-3.6*ss,2.2*ss,.2*ss,'#637785');line(ox+sign*6.2*ss,oy,ox+sign*6.2*ss,oy-3.6*ss,'#637785',3)
txt(690,490,'데크 +3.6m / 20단 × 0.18m / 디딤판 0.28m',10)
y=535
for s in ['계단·데크 치수는 게임 제작 가안이며 실제 통행 검수 후 조정한다.','그레이팅 아래에서는 위의 이동을, 위에서는 하부 통로를 관찰한다.','철판 작업대·제어반·탱크·굵은 배관이 시야를 끊는다.','기둥·주보·보조보·체결부·난간·발끝막이까지 제작한다.','철색 재질 + 붉은 보조등. 계단·밸브는 중성 작업등으로 읽힌다.']:y=wrap(655,y,s,480,11,20)+12
finish()
header('바닥 안내선과 인수인계 기록','도면상의 예상 이동과 게임 안의 업무용 안내선은 구분한다.','05_안내선_기록')
y=166
for r in d['wayfinding']['codes']:
 rect(55,y,160,36,'#3E4852')
 if r['pattern']=='dashed':c.setDash(12,7)
 line(65,y+13,205,y+13,r['color'],3);c.setDash()
 if r['pattern']=='single-solid-square':rect(125,y+7,12,12,r['color'])
 if r['pattern']=='double-solid':line(65,y+24,205,y+24,r['color'],3)
 txt(245,y+24,r['code']+'  '+r['purpose'],15,INK,True);y+=78
y+=10
for r in d['wayfinding']['records']:
 txt(55,y,r['floor']+'-'+r['room']+'  기록 문구 가안',12,'#29636D',True);y=wrap(55,y+24,r['text'],1060,13,22)+28
wrap(55,730,'갈림길·문·계단에서는 표식 가독성을 유지. 안내선 위에도 감시가 있으므로 우회 후 재합류한다.',1080,11,19);finish()
header('층간 연결과 제작 순서','각 층 루트의 높이를 유지하고, 내부 메자닌 높이는 해당 층 로컬 높이로 다룬다.','06_층간_제작순서')
y=165
for v in d['vertical']:
 txt(55,y,f"{v['lower']} → {v['upper']}   {v['core']}   높이차 {v['rise']}m",16,INK,True)
 y=wrap(55,y+26,'승강기 동작은 사용자 구현 예정. 초기 제작에서는 도착 위치와 승강로를 보존한다.' if v['core']=='VL' else f"계단 {v['steps']}단·{v['flights']}개 구간 가안. 실제 계단실·참·문 정합은 층간 제작 때 검사한다.",1050,12,21)+32
for s in ['1. B5 핵심 공동·터널을 새 씬에 제작하고 기존 이동 캐릭터로 통행을 확인한다.','2. B5 시야·프랍 밀도·청백색 밝기를 검수한 뒤 B4로 연결한다.','3. B3 소등 회로·B2 메자닌을 각 층 구조와 함께 제작한다.','4. 외곽 생활 공간과 작은 소품은 핵심 통행을 보존하며 확장한다.']:
 y=wrap(55,y,s,1060,12,22)+10
finish();c.save()
sys.path.insert(0,'C:/Users/503-26/Documents/Codex/2026-11-06/dl/work/dome_pythonlibs')
import pymupdf
pdf=pymupdf.open(OUT/'AfterSeconds_원형공동_제작설계.pdf')
draw=OUT/'도면';draw.mkdir(exist_ok=True)
for i,p in enumerate(pdf):(draw/(f'{i+1:02}_'+page_names[i]+'.svg')).write_text(p.get_svg_image(),encoding='utf-8')
(OUT/'page_index.json').write_text(json.dumps(page_names,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(pdf),'junctions':len(d['tunnel_junctions']),'output':str(OUT),'B3_circuits':len(d['light_circuits'])},ensure_ascii=False))
