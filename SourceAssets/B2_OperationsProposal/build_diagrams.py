"""Generate new technical proposal drawings; never edits Unity or source layouts."""
from pathlib import Path
from html import escape
import json, math, hashlib
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'Docs/도면/Decision/원형공동'
OUT = BASE / 'B2_운영동선_재설계'
SOURCE = BASE / 'facility_layout.json'
data = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
floor = next(f for f in data['floors'] if f['id'] == 'B2')
rooms = {r['id']: r for r in floor['rooms']}
BG = '#f4f1e9'
INK = '#20343d'
M = '#087f80'
G = '#b85b22'
BLUE = '#376c9b'
FONT = 'C:/Windows/Fonts/malgun.ttf'
BOLD = 'C:/Windows/Fonts/malgunbd.ttf'

class Sheet:
    def __init__(self, title, sub, width=1600, height=1160):
        self.w, self.h = width, height
        self.im = Image.new('RGB', (width,height), BG)
        self.d = ImageDraw.Draw(self.im)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',f'<rect width="100%" height="100%" fill="{BG}"/>']
        self.text((54,32),title,34,bold=True)
        self.text((56,86),sub,18,color='#5c696c')
        self.line([(54,124),(width-54,124)],'#aeb9b8',2)
    def line(self, pts, color=INK, width=2, dash=False):
        pts=[(float(x),float(y)) for x,y in pts]
        if dash:
            for a,b in zip(pts,pts[1:]):
                dist=math.dist(a,b)
                for start in range(0,int(dist),16):
                    end=min(start+9,dist)
                    self.d.line([(a[0]+(b[0]-a[0])*start/dist,a[1]+(b[1]-a[1])*start/dist),(a[0]+(b[0]-a[0])*end/dist,a[1]+(b[1]-a[1])*end/dist)],fill=color,width=max(1,round(width)))
        else: self.d.line(pts,fill=color,width=max(1,round(width)),joint='curve')
        self.svg.append(f'<polyline points="'+ ' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"'+(' stroke-dasharray="9 7"' if dash else '')+'/>')
    def rect(self, box, fill, outline=INK, width=2):
        x,y,x2,y2=box; self.d.rectangle(box,fill=fill,outline=outline,width=max(1,round(width)))
        self.svg.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" fill="{fill}" stroke="{outline}" stroke-width="{width}"/>')
    def ellipse(self, box, fill, outline=INK, width=2):
        x,y,x2,y2=box; self.d.ellipse(box,fill=fill,outline=outline,width=max(1,round(width)))
        self.svg.append(f'<ellipse cx="{(x+x2)/2}" cy="{(y+y2)/2}" rx="{(x2-x)/2}" ry="{(y2-y)/2}" fill="{fill}" stroke="{outline}" stroke-width="{width}"/>')
    def text(self, pos, text, size=20, color=INK, bold=False, anchor='left'):
        font=ImageFont.truetype(BOLD if bold else FONT,size)
        for i,line in enumerate(text.split('\n')):
            x,y=pos[0],pos[1]+i*round(size*1.5)
            length=self.d.textlength(line,font=font)
            if anchor=='middle': x-=length/2
            if anchor=='right': x-=length
            self.d.text((x,y),line,font=font,fill=color)
            self.svg.append(f'<text x="{x:.2f}" y="{y+size:.2f}" font-family="Malgun Gothic, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(line)}</text>')
    def arrow(self, a,b,color, size=12):
        angle=math.atan2(b[1]-a[1],b[0]-a[0]); x,y=b
        pts=[(x,y),(x-size*math.cos(angle-.48),y-size*math.sin(angle-.48)),(x-size*math.cos(angle+.48),y-size*math.sin(angle+.48))]
        self.d.polygon(pts,fill=color)
        self.svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="{color}"/>')
    def save(self,name):
        self.text((54,self.h-42),'After Seconds  |  B2 운영 동선 재설계 V0.01  |  송예찬  |  2026-11-10  |  Unity 적용 전 제안',15,color='#667476')
        self.im.save(OUT/f'{name}.png')
        (OUT/f'{name}.svg').write_text('\n'.join(self.svg+['</svg>']),encoding='utf-8')

def point(x,z): return (530+x*36,566-z*36)
def title_room(room,title,sub):
    s=Sheet(title,sub)
    r=rooms[room]['r']; cx,cy=point(0,0)
    s.ellipse((cx-r*36,cy-r*36,cx+r*36,cy+r*36),'#e6e5de','#35464d',6)
    s.line([point(-r,0),point(r,0)],'#c8ceca',1,True)
    s.line([point(0,-r),point(0,r)],'#c8ceca',1,True)
    s.text((72,146),'북 / Unity +Z ↑',17,bold=True)
    s.text((72,174),f'공동 반지름 {r}m · 내부는 제안 배치',16)
    s.line([(1080,144),(1080,1022)],'#c2cac5',2)
    return s

def portals(s, room, upper=False):
    for d in rooms[room]['doors']:
        t=next(t for t in floor['tunnels'] if t['id']==d['id']); other=t['b'] if t['a']==room else t['a']
        x,z=d['x'],d['z']; a=math.atan2(z,x); r=rooms[room]['r']
        p=point(x,z); col=BLUE if upper else INK
        if not upper or d['id']=='B2-T01':
            tangent=(-math.sin(a),math.cos(a)); q=(r*math.cos(a),r*math.sin(a))
            s.line([point(q[0]-1.6*tangent[0],q[1]-1.6*tangent[1]),point(q[0]+1.6*tangent[0],q[1]+1.6*tangent[1])],BG,9)
            s.ellipse((p[0]-7,p[1]-7,p[0]+7,p[1]+7),BG,col,3)
        label=point((r+1.0)*math.cos(a),(r+1.0)*math.sin(a))
        s.text((label[0],label[1]-13),d['id'].replace('B2-','')+' → '+other,16,col,True,'middle')

def block(s,b,muted=False):
    x,z,w,h=b['x'],b['z'],b['w'],b['d']; x1,y1=point(x-w/2,z+h/2); x2,y2=point(x+w/2,z-h/2)
    fill=b.get('fill','#8ea5ac') if not muted else '#dddcd5'
    if b.get('shape')=='circle': s.ellipse((x1,y1,x2,y2),fill,'#51616a',2)
    else: s.rect((x1,y1,x2,y2),fill,'#51616a',2)
    if b.get('stairs'):
        for i in range(1,12):
            yy=y1+(y2-y1)*i/12; s.line([(x1,yy),(x2,yy)],'#60757c',1)
        s.arrow((x1+w*18,y2-12),(x1+w*18,y1+14),INK)
    s.text(point(x,z),b['id'],19 if len(b['id'])<3 else 15,INK,True,'middle')

def route(s,pts,color,width=5,dash=False):
    xy=[point(*p) for p in pts]; s.line(xy,color,width,dash)
    for i in range(0,len(xy)-1,2):
        a,b=xy[i],xy[i+1]; t=.65; q=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t); s.arrow(a,q,color,11)

def mark(s,p,label,color):
    x,y=point(*p); s.ellipse((x-14,y-14,x+14,y+14),BG,color,3); s.text((x,y-12),label,15,color,True,'middle')

def notes(s, groups):
    y=155
    for title,lines,color in groups:
        s.text((1110,y),title,24,color,True); y+=45
        for line in lines:
            s.text((1110,y),line,18); y+=31
        y+=28

c02_blocks=[
 {'id':'P1','x':-2.5,'z':-.5,'w':2.8,'d':5,'fill':'#98acb2'},
 {'id':'P2','x':2.3,'z':0,'w':2.8,'d':4,'fill':'#98acb2'},
 {'id':'H','x':0,'z':5,'w':3.4,'d':2.2,'fill':'#78919b'},
 {'id':'R','x':4.8,'z':4.3,'w':2.5,'d':2.5,'shape':'circle','fill':'#9bada3'},
 {'id':'D','x':7.4,'z':0,'w':1,'d':4,'fill':'#a7b4c6'},
 {'id':'B','x':-5.7,'z':-4.4,'w':1.8,'d':.8,'fill':'#b5afa0'},
 {'id':'L','x':1,'z':-5.5,'w':3,'d':1.6,'fill':'#e0ce9c','reserved':True},
 {'id':'S1','x':-5.4,'z':0,'w':1.6,'d':5.4,'stairs':True,'fill':'#c8ceca'},
 {'id':'S2','x':5.4,'z':-4,'w':1.6,'d':5.4,'stairs':True,'fill':'#c8ceca'},
]
c02_m=[[-2,-10],[-3,-8],[-2.3,-5.5],[-.1,-3.8],[-.1,2.9],[1.8,2.9],[5,2.5],[6,1.5],[6,2.7],[8.5,2.7],[8.5,-2],[7.4,-6],[7.1,-6.8],[5.4,-7.5]]
c02_g=[[-2,-10],[-3,-8],[-6.7,-7],[-8.7,-3],[-8.5,.3],[-8,3.9],[-7.69,6.7],[-4.5,8.4],[0,9.2],[4.6,8.4],[6.66,7.73],[8.3,4],[8.7,0],[8.7,-2.8],[7.4,-5.5],[7.1,-6.8],[4.8,-7.8],[-3,-8]]

def c02_lower():
    s=title_room('C02','C02 냉각·펌프 공동  |  하부 운영 평면','운전면 → 정비면 → 상부 점검으로 이어지는 작업장. 출입구 위치는 현행 도면 기준.')
    for b in c02_blocks: block(s,b)
    # Pipe arrows describe a proposed circuit, not a personnel route.
    s.line([point(-2.5,2),point(-2.5,5),point(-1.7,5)],'#6c858b',7)
    s.line([point(2.3,2),point(2.3,5),point(1.7,5)],'#6c858b',7)
    s.line([point(1.7,5),point(4.8,5)],'#6c858b',7)
    route(s,c02_g,G,4,True); route(s,c02_m,M,5)
    for p,lab in [((-2.3,-5.5),'1'),((-.1,.4),'2'),((0,2.9),'3'),((5,2.5),'4'),((6,1.5),'5'),((5.4,-7.5),'6')]: mark(s,p,lab,M)
    for p in [(-8.5,.3),(-7.69,6.7),(6.66,7.73),(8.7,0),(-3,-8)]: mark(s,p,'G',G)
    portals(s,'C02')
    notes(s,[('점검자가 도는 순서',['1 인계·교체품 확인','2 P1/P2 운전면과 계기','3 H 공용 헤더·열교환','4 R 탱크와 연결부','5 D 제어반 상태 대조','6 S2 계단으로 상부 점검'],M),('경비가 보는 것',['G 출입구·계단·제어반','외곽 순환 중 안쪽을 번갈아 확인','문 앞 정지 대신 옆쪽 정지 홈','설비 뒤는 이동해야 확인 가능'],G),('구조와 남겨 둘 공간',['P1/P2 병렬 펌프 열','H 큰 불투명 설비로 시선 분절','B 공구대 / L 부품 인계 자리','S1/S2 서로 다른 접근 계단','운반 통로는 외곽 남·동쪽 확보','최종 폭·충돌은 Unity 검수'],INK)])
    s.text((80,1030),'실선: 점검 동선    점선: 순찰 예시    회색: 설비 / 계단    황토색: 일시 인계 공간',18)
    s.save('C02_lower')

upper_path=[[-5.4,2.7],[-5.4,5.2],[-2.4,7.4],[2,7.4],[6.6,6.4],[8,2.5],[5.4,-1.3]]
def c02_upper():
    s=title_room('C02','C02 냉각·펌프 공동  |  상부 정비 평면','하부 기준 +3.60m의 부분 데크. T01 상부 +2.42m와는 별도 높이 전환이 필요하다.')
    for b in c02_blocks: block(s,b,True)
    s.text(point(0,-3.5),'하부를 보는 열린 공간',19,anchor='middle')
    xy=[point(*p) for p in upper_path]
    s.line(xy,'#425c66',72); s.line(xy,'#bccbcb',62)
    branch=[[6.6,6.4],[6.66,7.73]]
    s.line([point(*p) for p in branch],BLUE,56); s.line([point(*p) for p in branch],'#cbd9e3',44)
    route(s,upper_path,M,5)
    for p,lab in [((-5.4,4),'S1'),((-2.4,7.4),'V1'),((2,7.4),'V2'),((6.6,6.4),'V3'),((5.4,-1.3),'S2')]: mark(s,p,lab,M)
    s.text(point(-1,9.3),'밸브·플랜지·지지 구조 점검면',18,anchor='middle')
    s.text(point(0,-7.5),'하부의 사람과 시선이 교차하는 그레이팅',18,anchor='middle')
    portals(s,'C02',True)
    notes(s,[('올라오는 이유',['V1 공급 헤더의 밸브','V2 회수 헤더·계측 연결','V3 배관 지지·접속부','S1/S2 작업 후 다른 쪽으로 하강'],M),('점검면을 잇는 부분 데크',['실제 점검 대상의 배치를 따라감','중앙은 하부 설비가 보이게 개방','손잡이 앞에는 서 있을 자리 확보','상부의 통행과 작업 자리 분리'],INK),('T01 연결 단면 확인',['공동 데크 +3.60m','터널 데크 +2.42m','차이 1.18m는 접속 계단으로 처리','기존 출입 위치 유지 방향','터널은 앉아서 점검하는 공간','카트 운반·경비 일상 순찰은 하부'],BLUE)])
    s.text((80,1030),'이 도면은 높이가 다른 경로의 연결 의도다. 계단 길이·난간·머리 공간은 단면 검수 대상.',18)
    s.save('C02_upper')

e02_blocks=[
 {'id':'F','x':2,'z':0,'w':3.2,'d':8,'fill':'#8ea5ac'},
 {'id':'H','x':2,'z':5.6,'w':3.6,'d':1.6,'fill':'#78919b'},
 {'id':'D','x':5.8,'z':0,'w':1.2,'d':3.6,'fill':'#a7b4c6'},
 {'id':'N','x':-2.3,'z':5.2,'w':2,'d':1.2,'fill':'#b8d3c4','reserved':True},
 {'id':'U','x':-2.4,'z':-4.4,'w':2,'d':1.2,'fill':'#d5b494','reserved':True},
 {'id':'I','x':-3.5,'z':0,'w':1.1,'d':1.6,'fill':'#a7b4c6'},
]
e02_m=[[-6.04,5.54],[-4.2,3.8],[-.9,3.8],[-.9,-3],[-.9,-5.7],[-3.8,-5.8],[-5.16,-6.37]]
e02_g=[[-6.04,5.54],[-6.8,2.5],[-6.8,-2],[-5.16,-6.37]]
e02_rear=[[0,7.3],[4.4,7],[4.8,5.5],[4.5,3.5],[4.5,-4.8],[0,-6.3]]
def e02():
    s=title_room('E02','E02 공조 필터 공동  |  교체와 회수의 흐름','필터 열의 앞은 교체 작업면, 뒤는 구동부 점검면. 작업 순서가 두 출입구를 잇는다.')
    for b in e02_blocks: block(s,b)
    for z in [-2.7,-1.35,0,1.35,2.7]: s.line([point(.4,z),point(3.6,z)],'#536f79',2)
    route(s,e02_m,M,5); route(s,e02_g,G,4,True)
    route(s,e02_rear,BLUE,4,True)
    for p,lab in [((-4.2,3.8),'1'),((-.9,1.8),'2'),((-.9,-2.7),'3'),((-3.8,-5.8),'4')]: mark(s,p,lab,M)
    portals(s,'E02')
    notes(s,[('정비 작업 순서',['1 N 새 필터·공구 인계','2 I 상태계 확인 / F 교체면 접근','3 필터를 꺼낼 전면 공간','4 U 사용 필터 밀폐 회수','물품 흐름은 출입문 잠금 규칙 아님'],M),('구조를 다르게 만드는 것',['F 긴 필터 열이 전면·후면 분리','D 구동부는 후면 통로에서 점검','H 상부 덕트와 댐퍼로 연결','두 열의 끝에서 다시 합류','상부 T15/T16 접속은 유지'],BLUE),('순찰과 잠입',['경비는 서측 출입 통로 확인','작업자는 필터 교체면에 정지','큰 설비 뒤는 돌아가야 보임','열 끝을 지날 때 시선이 다시 교차','최종 부품 인출 폭은 모델로 검수'],G)])
    s.text((80,1030),'실선: 필터 교체 흐름    주황 점선: 순찰 예시    파랑 점선: 후면 점검 접근',18)
    s.save('E02_filter')

route_defs=[
 {'id':'central','name':'중앙 운전 점검','rooms':['C04','C02','C03','C01','C04'],'tunnels':['T04','T09','T06','T05'],'color':BLUE},
 {'id':'west','name':'서측 전력·부품 순찰','rooms':['C04','C01','W03','W02','W01','VA','C01','C04'],'tunnels':['T05','T13','T12','T11','T10','T03','T05'],'color':G},
 {'id':'east','name':'동측 물·공조 순찰','rooms':['C04','C02','VL','E01','E02','E03','VB','C04'],'tunnels':['T04','T01','T14','T15','T16','T17','T08'],'color':M},
 {'id':'north','name':'북측 환기 점검','rooms':['C01','VA','N01','VL','C03','C01'],'tunnels':['T03','T18','T19','T07','T06'],'color':'#857f67'},
 {'id':'south','name':'남측 정비 인계','rooms':['C04','VB','S01','W03','C01','C04'],'tunnels':['T08','T20','T21','T13','T05'],'color':'#857f67'},
]

def overall():
    s=Sheet('B2 기계층  |  작업과 순찰이 이어지는 구조','공동 12개 · 이동 코어 3개 · 통로 21개 유지. 중앙과 외곽 업무를 나눠 짧은 순환으로 돌아본다.',1600,1200)
    def p(x,v): return 800+x*4.5,575+v*4.5
    ts={t['id'].replace('B2-',''):t for t in floor['tunnels']}
    for t in floor['tunnels']:
        xy=[p(*q) for q in t.get('path',[t['p'],t['q']])]; s.line(xy,'#b1bab7',12)
    for route_i,r in enumerate(route_defs[:3]):
        for tid in set(r['tunnels']):
            t=ts[tid]; xy=[p(*q) for q in t.get('path',[t['p'],t['q']])]
            if route_i==0: xy=[(x+3,y+3) for x,y in xy]
            s.line(xy,r['color'],4,route_i==1)
    for tid,t in ts.items():
        path=t.get('path',[t['p'],t['q']]); mid=path[len(path)//2] if len(path)>2 else [(t['p'][i]+t['q'][i])/2 for i in (0,1)]
        x,y=p(*mid); s.rect((x-20,y-11,x+20,y+11),BG,BG,1); s.text((x,y-10),tid,13,anchor='middle')
    labels={'C01':'원심분리','C02':'냉각·펌프','C03':'배전','C04':'관제','W01':'주 전력','W02':'예비 전력','W03':'부품·정비','E01':'급수','E02':'필터','E03':'폐수','N01':'환기','S01':'감시·정비','VA':'계단 A','VB':'계단 B','VL':'화물'}
    for rid,r in rooms.items():
        x,y=p(r['x'],r['v']); rr=r['r']*4.5
        s.ellipse((x-rr,y-rr,x+rr,y+rr),'#d6dfdb' if r['kind']=='cavern' else '#e6d4b5',INK,3)
        core=r['kind']=='core'
        s.text((x,y-18 if core else y-23),rid,16 if core else 19,bold=True,anchor='middle'); s.text((x,y+3 if core else y+5),labels[rid],11 if core else 13,anchor='middle')
    s.text((60,150),'북 ↑  /  Unity Z = -v',18,bold=True)
    s.text((60,180),'출입구·통로 좌표: 현행 Decision',16)
    s.text((60,211),'내부 작업 구획: 이번 재설계 제안',16)
    for i,r in enumerate(route_defs[:3]):
        x=65+i*510; s.line([(x,1040),(x+60,1040)],r['color'],5,i==1); s.text((x+75,1025),r['name'],22,r['color'],True)
    s.text((65,1085),'북측: VA–N01–VL 환기 점검    /    남측: VB–S01–W03 정비 인계    /    코어 이용은 자유 선택 유지',19)
    s.save('B2_routes')

def validation():
    ts={t['id'].replace('B2-',''):t for t in floor['tunnels']}
    checked=[]
    for r in route_defs:
        assert len(r['tunnels'])==len(r['rooms'])-1
        for a,b,tid in zip(r['rooms'],r['rooms'][1:],r['tunnels']):
            assert {a,b}=={ts[tid]['a'],ts[tid]['b']},(r['id'],a,b,tid)
            checked.append([r['id'],a,b,tid])
    for room,bs in [('C02',c02_blocks),('E02',e02_blocks)]:
        for b in bs:
            for sx in [-1,1]:
                for sz in [-1,1]:
                    assert math.hypot(b['x']+sx*b['w']/2,b['z']+sz*b['d']/2)<rooms[room]['r'],b
    clearances=[]
    for room,paths,blocks in [('C02',[('technician',c02_m),('guard',c02_g)],c02_blocks),('E02',[('technician',e02_m),('guard',e02_g),('rear',e02_rear)],e02_blocks)]:
        for name,path in paths:
            minimum=100
            for a,b in zip(path,path[1:]):
                steps=max(1,math.ceil(math.dist(a,b)/.025))
                for i in range(steps+1):
                    x,z=[a[k]+(b[k]-a[k])*i/steps for k in [0,1]]
                    minimum=min(minimum,rooms[room]['r']-math.hypot(x,z))
                    for block in blocks:
                        if block.get('shape')=='circle': distance=math.hypot(x-block['x'],z-block['z'])-block['w']/2
                        else: distance=math.hypot(max(abs(x-block['x'])-block['w']/2,0),max(abs(z-block['z'])-block['d']/2,0))
                        minimum=min(minimum,distance)
            assert minimum>=.4,(room,name,minimum)
            clearances.append({'room':room,'route':name,'minimum_centerline_distance_to_2d_blocks_or_wall_m':round(minimum,3),'sample_spacing_m':.025,'test_radius_m':.4})
    report={'version':'0.01','scope':'proposal drawings only; not Unity clearance or NavMesh validation','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'existing_rooms':len(rooms),'caverns':sum(r['kind']=='cavern' for r in rooms.values()),'existing_tunnels':len(floor['tunnels']),'routes_checked':len(route_defs),'adjacency_checks':len(checked),'all_route_edges_exist':True,'equipment_footprints_inside_room_circle':True,'route_edges':checked,'lower_plan_centerline_sampling':clearances,'not_validated':['3D overlap','stair section','cart swept clearance','NavMesh','visibility','runtime AI']}
    (OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    proposal={'version':'0.01','author':'송예찬','date':'2026-11-10','status':'proposal; not applied to Unity','scope':'B2','coordinate':'Room local x east, z north; floor plan v=-Unity Z','source':str(SOURCE.relative_to(ROOT)).replace('\\','/'),'rooms':[{'id':r['id'],'name':r['name'],'r':r['r'],'doors':r['doors']} for r in rooms.values()],'C02':{'lower_blocks':c02_blocks,'technician_route':c02_m,'guard_route':c02_g,'upper_walk':upper_path,'upper_elevation':3.60,'T01_upper_elevation':2.42},'E02':{'lower_blocks':e02_blocks,'technician_route':e02_m,'guard_route':e02_g,'rear_service_route':e02_rear},'floor_routes':route_defs}
    (OUT/'proposal.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    c02_lower(); c02_upper(); e02(); overall(); validation()
    print('Generated 4 PNG, 4 SVG, proposal.json and validation.json in',OUT)

if __name__=='__main__': main()
