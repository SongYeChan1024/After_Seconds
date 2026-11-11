from pathlib import Path
import json,math,copy,sys
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01'
sys.path.insert(0,str(U/'Temp/ZFightingReview/deps'))
from PIL import Image,ImageDraw,ImageFont
p=json.loads((H/'layout.json').read_text(encoding='utf8'));models=json.loads((H/'models_props.json').read_text());rem=[q for q in p['placements'] if q['room']=='C05' and q['model'] in ['SF_BriefingTable','SF_TaskChair']]
assert len(rem)==5,'One-time conference extension'
removed={q['name'] for q in rem};p['placements']=[q for q in p['placements'] if q['name'] not in removed];p['workspaces']=[q for q in p['workspaces'] if q['name'] not in removed]
chair=next(q for q in p['placements'] if q['room']=='W01' and q['model']=='SF_TaskChair');new=[]
def add(model,x,z,yaw):
 q=copy.deepcopy(chair if model=='SF_TaskChair' else models[model]);q.update(room='C05',model=model,name='B1_C05_Conference_'+model.split('_',1)[1]+'_'+str(len(new)+1).zfill(2),yaw=yaw,role='Seating' if model=='SF_TaskChair' else 'Equipment',meshCollider=False)
 w,h,d=q['size'];cx,cy,cz=q['center'];a=math.radians(yaw);q['position']=[x-cx*math.cos(a)-cz*math.sin(a),-(cy-h/2),z+cx*math.sin(a)-cz*math.cos(a)];new.append(q);p['placements'].append(q)
 distance=-.69 if model=='SF_TaskChair' else d/2+.70
 p['workspaces'].append(dict(room='C05',name=q['name'],point=[x+math.sin(a)*distance,0,z+math.cos(a)*distance]))
add('BL_ConferenceTable',0,-.4,0);add('BL_PresentationBoard',0,3.5,180)
for x in [-1.4,0,1.4]:
 add('SF_TaskChair',x,-1.6,0);add('SF_TaskChair',x,.8,180)
add('SF_TaskChair',-2.55,-.4,90);add('SF_TaskChair',2.55,-.4,270)
for r in p['rooms']:
 if r['id']=='C05':r['name']='연구 보고·직원 회의장';r['conference_seats']=8
p['conference']='사용자 추가 요청: C05 8인용 회의 테이블·자료 발표 화면·발표 공간·기록 보관장'
for path,obj in [(H/'conference_plan.json',dict(remove=list(removed),add=new,template=chair['name'],templateRoom='W01')),(H/'layout.json',p)]:path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
im=Image.new('RGB',(1024,576),(19,30,36));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('C:/Windows/Fonts/consola.ttf',n)
d.rectangle((0,0,1024,92),fill=(36,62,67));d.text((42,23),'RESEARCH REPORT REVIEW',font=font(42),fill=(220,227,217));d.text((42,116),'B1 / STAFF MEETING   |   ARCHIVE COPY',font=font(25),fill=(154,188,181))
for k,(title,body) in enumerate([('01  RESULTS','B4 RECORDS / R06'),('02  REVIEW','ANALYSIS NOTES'),('03  HANDOVER','ACTION RECORD')]):
 x=42+k*324;d.rectangle((x,190,x+294,456),fill=(30,45,51),outline=(69,92,95),width=2);d.text((x+18,215),title,font=font(25),fill=(215,220,205));d.text((x+18,265),body,font=font(20),fill=(161,187,183))
 for j in range(4):d.line((x+20,330+j*24,x+265-(j%2)*45,330+j*24),fill=(97,126,129),width=3)
d.text((42,510),'RECORDED DATA / REVIEW DISCUSSION / STAFF USE',font=font(22),fill=(175,194,184));im.save(U/'Assets/Afrer_Seconds/05.Model/Props/B1/Textures/BL_Presentation.png')
print('Conference total placements:',len(p['placements']))
