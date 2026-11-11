from pathlib import Path
import json,math,sys
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'))
from PIL import Image,ImageDraw,ImageFont
p=json.loads((H/'layout.json').read_text(encoding='utf8'));cat={q['name']:q for q in json.loads((H/'catalog.json').read_text())}
names={'C01':'CENTRAL TRIAL CHAMBER','C02':'EXPERIMENT PREPARATION','C03':'RESEARCH RECORDS','C04':'MEDICAL SUPPORT','C05':'OBSERVATION','W01':'RESEARCH OFFICES','W02':'STAFF DINING','W03':'STAFF QUARTERS','E01':'SECURITY CONTROL','E02':'RESTRICTED ARCHIVE','E03':'GUARD QUARTERS','N01':'PREDICTIVE RESEARCH','S01':'BACKUP SERVERS','VA':'STAIR A  /  1F','VB':'STAIR B  /  1F','VL':'CARGO LIFT  /  1F'}
out=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B1/Textures';out.mkdir(exist_ok=True,parents=True)
for code,name in names.items():
 im=Image.new('RGB',(512,128),(36,47,48));d=ImageDraw.Draw(im);d.rectangle((4,4,507,123),outline=(139,157,150),width=2);d.text((20,12),'B1 / '+code,font=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',47),fill=(225,227,209));d.text((20,80),name,font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22),fill=(182,198,188));im.save(out/f'BL_Sign_{code}.png')
# Chairs belong to their workstations, not separate arbitrary wall bays.
oldchairs=[q for q in p['placements'] if q['model']=='SF_TaskChair'];p['placements']=[q for q in p['placements'] if q not in oldchairs];p['workspaces']=[q for q in p['workspaces'] if q['name'] not in {q['name'] for q in oldchairs}]
for room in ['W01','C03','C05','E01','E02','S01']:
 desks=[q for q in p['placements'] if q['room']==room and q['model'] in ['BL_ResearchDesk','SF_SC_OperatorDesk_A','SF_SC_OperatorDesk_B','SF_SC_IncidentReview','BO_ObservationConsole']]
 for i,desk in enumerate(desks):
  c=cat['SF_TaskChair'];yaw=desk['yaw'];a=math.radians(yaw);offset=desk['center'][2]+desk['size'][2]/2+.43;dx,dz=math.sin(a)*offset,math.cos(a)*offset
  pos=[desk['position'][0]+dx,0,desk['position'][2]+dz];p['placements'].append(dict(room=room,name=f'B1_{room}_PairedChair_{i+1:02}',model='SF_TaskChair',asset=c['asset'],position=pos,yaw=(yaw+180)%360,size=c['size'],center=c['center'],role='Seating',meshCollider=False))
  # Access is beside the seat, preserving approach to the desk controls.
  ws=next((w for w in p['workspaces'] if w['name']==desk['name']),None)
  if ws:ws['point']=[pos[0]+math.cos(a)*.68,0,pos[2]-math.sin(a)*.68]
p['refinement']='Chairs paired with desks; opaque mounted signs; R1 double solid circulation marks.'
(H/'layout.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8');print('placements',len(p['placements']),'signs',len(names),'chairs',sum(q['role']=='Seating' for q in p['placements']))
