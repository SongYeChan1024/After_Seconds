"""Purposeful floor soiling and close-view industrial readouts. No repeated decals."""
from pathlib import Path
import json,math,hashlib,os
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model';T=A/'Environment/B2/Textures';P=A/'Props/B2/Textures'
T.mkdir(exist_ok=True,parents=True);P.mkdir(exist_ok=True,parents=True)
plan=json.loads((R/'SourceAssets/B2_OperationsRebuild/plan.json').read_text(encoding='utf8'))
for p in plan['placements']:
 if p['name']=='B2_C02_Ops_PartsStaging_13':p['position']=[-4.0,.185,-5.3]
 if p['name']=='B2_C02_Ops_PartsStaging_14':p['position']=[-6.55,0,-5.9];p['yaw']=180
plan['placements'].append(dict(name='B2_C01_LubricationStation',room='C01',group='SealService',model='BR_LubricationStation',position=[7.9,0,2.8],yaw=270,size=[1.4,1.96,.8],center=[0,.98,0]))
plan['placements'].append(dict(name='B2_C02_PartsCradle',room='C02',group='PartsStaging',model='BR_PartsCradle',position=[-4,0,-5.3],yaw=0,size=[1.42,.27,.96],center=[0,.135,0]))
(H/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
protected=H/'protected_before.json'
if not protected.exists():
 root=R/'Unity/After_Seconds_Build_V0.01'
 files=[p for p in (root/'Assets').rglob('*') if p.is_file() and (p.suffix in {'.cs','.controller','.inputactions'} or (p.suffix=='.unity' and p.name!='Level_B2_Circular.unity'))]
 protected.write_text(json.dumps({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2),encoding='utf8')
def noise(n,grid,rng):
 a=rng.integers(0,256,(grid,grid),dtype=np.uint8)
 return np.asarray(Image.fromarray(a).resize((n,n),Image.Resampling.BICUBIC),dtype=np.float32)/255
def write_pbr(stem,col,height,metal,smooth,folder=T):
 col=np.clip(col,0,255).astype(np.uint8);Image.fromarray(col).save(folder/(stem+'_Base.png'))
 n=len(col);ms=np.zeros((n,n,4),np.uint8);ms[:,:,:3]=np.clip(metal*255,0,255).astype(np.uint8)[...,None] if isinstance(metal,np.ndarray) else int(metal*255);ms[:,:,3]=np.clip(smooth*255,0,255);Image.fromarray(ms).resize((1024,1024),Image.Resampling.LANCZOS).save(folder/(stem+'_MS.png'))
 h=np.asarray(Image.fromarray(height.astype(np.float32)).resize((1024,1024),Image.Resampling.BILINEAR));dy,dx=np.gradient(h);normal=np.stack([-dx,-dy,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);Image.fromarray(np.clip((normal*.5+.5)*255,0,255).astype(np.uint8)).save(folder/(stem+'_Normal.png'))
rows=json.loads((H/'before.json').read_text(encoding='utf8'))
floors=[q for q in rows if q['active'] and q['name'].endswith('_Floor') and q['mesh']]
manifest=[]
for index,q in enumerate(floors):
 if os.environ.get('BR_ONLY_TILES'):continue
 n=2048;rng=np.random.default_rng(8521+index*171);w=q['bounds']['size'][0];d=q['bounds']['size'][2];room=q['name'].split('_')[1]
 # Image row zero maps to the largest world Z, like a normal UV surface.
 X,Z=np.meshgrid(np.linspace(-w/2,w/2,n),np.linspace(d/2,-d/2,n));fine=noise(n,768,rng);mid=noise(n,96,rng);cloud=noise(n,13,rng);broad=noise(n,5,rng)
 grain=(fine-.5)*15+(mid-.5)*13+(cloud-.5)*16
 col=np.empty((n,n,3),np.float32);col[:]=[101,104,103];col+=grain[...,None]
 pores=np.clip((fine-.69)*5,0,1)
 col-=pores[...,None]*23
 h=(fine-.5)*1.0+(mid-.5)*.28-pores*.65
 radius=min(w,d)/2;edge=np.clip((np.sqrt(X*X+Z*Z)-(radius-1.15))/1.2,0,1)*(cloud*.7+.3)
 dust=edge*.45+np.clip((broad-.56)*1.3,0,.32)
 col=col*(1-dust[...,None])+np.array([116,106,87])*dust[...,None]
 # Concrete saw joints, a few millimetres deep; these are material seams, not route stripes.
 joint=np.zeros((n,n),np.float32)
 for axis in [X,Z]:
  for v in np.arange(-radius+1.4,radius,3.8):joint=np.maximum(joint,np.exp(-((axis-v)/.013)**2))
 col-=joint[...,None]*28;h-=joint*1.6
 oil=np.zeros((n,n),np.float32)
 for p in [p for p in plan['placements'] if p['room']==room]:
  if any(k in p['model'] for k in ['Pump','Generator','Centrifuge','Heat','Motor','Lubrication','Tank']):
   x,_,z=p['position'];sx=.45+p['size'][0]*.32;sz=.35+p['size'][2]*.3
   x+=rng.uniform(-.5,.5);z+=rng.uniform(-.5,.5)
   shape=((X-x)/sx)**2+((Z-z)/sz)**2+(cloud-.5)*1.4+(mid-.5)*.3
   blob=np.clip((1-shape)*6,0,1)*(.72+mid*.28)
   oil=np.maximum(oil,blob*rng.uniform(.35,.8))
 # Small old spill patches spread irregularly, with dragged boot/hand-cart smears.
 for _ in range(5):
  x,z=rng.uniform(-radius*.7,radius*.7,2);sx,sz=rng.uniform(.15,.6,2)
  shape=((X-x)/sx)**2+((Z-z)/sz)**2+(cloud-.5)*1.8
  oil=np.maximum(oil,np.clip((1-shape)*7,0,1)*(.18+mid*.2))
 col=col*(1-oil[...,None]*.68)+np.array([26,23,18])*oil[...,None]*.68
 marks=Image.new('L',(n,n));draw=ImageDraw.Draw(marks)
 def uv(x,z):return ((x/w+.5)*n,(.5-z/d)*n)
 for k in range(4):
  z0=rng.uniform(-radius*.65,radius*.65);x0=rng.uniform(-radius*.65,radius*.65);ang=rng.uniform(0,math.tau)
  for j in range(rng.integers(4,10)):
   x=x0+math.cos(ang)*j*.39+math.sin(ang)*(.10 if j%2 else -.10);z=z0+math.sin(ang)*j*.39
   px,py=uv(x,z);rx=.095/w*n;ry=.16/d*n
   draw.ellipse((px-rx,py-ry,px+rx,py+ry),fill=int(rng.integers(12,40)))
   for step in range(4):draw.line((px-rx,py-ry+step*ry/2,px+rx,py-ry+step*ry/2),fill=0,width=2)
 mark=np.asarray(marks.filter(ImageFilter.GaussianBlur(.7)),np.float32)/255;col-=mark[...,None]*65
 smooth=np.clip(.12+oil*.30+(mid-.5)*.08,.07,.47)
 stem='BR_Floor_'+room;write_pbr(stem,col,h,0,smooth);manifest.append(dict(name=q['name'],stem=stem,center=q['bounds']['center'],size=q['bounds']['size']))
 print('Floor',room,flush=True)
# Tileable metal / concrete: mirrored sampling avoids sharp texture boundaries.
for kind in ['Steel','Coat','Concrete','Grip']:
 n=1024;rng=np.random.default_rng({'Steel':342,'Coat':475,'Concrete':236,'Grip':823}[kind]);fine=noise(n,512,rng);mid=noise(n,80,rng);cloud=noise(n,12,rng)
 col=np.empty((n,n,3),np.float32);base={'Steel':[101,107,107],'Coat':[70,79,77],'Concrete':[102,105,103],'Grip':[44,46,44]}[kind];col[:]=base;col+=((fine-.5)*3+(mid-.5)*4+(cloud-.5)*(4 if kind=='Coat' else 9))[...,None]
 dirt=np.clip((cloud-.70)*3,0,.40);col=col*(1-dirt[...,None]*.40)+np.array([70,47,29])*dirt[...,None]*.40
 scratches=Image.new('L',(n,n));dr=ImageDraw.Draw(scratches)
 for _ in range(200 if kind!='Concrete' else 50):
  x,y=rng.integers(0,n,2);ln=rng.integers(3,70);dr.line((x,y,x+ln,y+rng.integers(-4,5)),fill=int(rng.integers(20,110)),width=1)
 scr=np.asarray(scratches,np.float32)/255;col+=scr[...,None]*(20 if kind=='Coat' else 50)
 h=(fine-.5)*.07+(mid-.5)*.045-scr*.04
 smooth=np.clip((.29 if kind=='Steel' else .16)+(mid-.5)*.18-dirt*.16+scr*.25,.04,.65)
 metal=np.clip((.78 if kind=='Steel' else .15)*(1-dirt),0,1)
 write_pbr('BR_'+kind,col,h,metal,smooth)
if manifest:(H/'floors.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')

font=lambda s:ImageFont.truetype('C:/Windows/Fonts/consola.ttf',s)
for number in [1,2]:
 im=Image.new('RGB',(1024,512),(10,20,21));dr=ImageDraw.Draw(im)
 dr.rectangle((0,0,1024,62),fill=(30,55,57));dr.text((26,13),'PLANT / PROCESS' if number==1 else 'PUMP / TREND',font=font(30),fill=(177,205,194))
 dr.text((750,22),'LOCAL  AUTO',font=font(21),fill=(112,177,145))
 if number==1:
  for x,label,val in [(170,'TRAIN A','1460 rpm'),(475,'TRAIN B','1458 rpm'),(800,'RETURN','3.82 bar')]:
   dr.rounded_rectangle((x-93,150,x+93,300),radius=18,outline=(121,153,148),width=5);dr.text((x-77,172),label,font=font(25),fill=(177,195,185));dr.text((x-77,225),val,font=font(24),fill=(99,174,147))
  dr.line([(40,225),(75,225),(75,370),(935,370),(935,225),(893,225)],fill=(98,145,143),width=6)
  for x in [290,598]:dr.line((x,225,x+90,225),fill=(98,145,143),width=6);dr.polygon([(x+35,216),(x+50,225),(x+35,234)],fill=(178,192,177))
  dr.text((80,405),'FEED  42.6 C    FLOW  128 m3/h',font=font(29),fill=(176,196,187))
 else:
  for x in range(110,970,107):dr.line((x,112,x,360),fill=(34,53,54),width=1)
  for y in range(112,361,62):dr.line((110,y,970,y),fill=(34,53,54),width=1)
  for j,color in enumerate([(92,174,150),(190,147,82)]):
   points=[(110+i*4,220+j*48+math.sin(i*.15+j)*8+math.sin(i*.027)*19) for i in range(215)];dr.line(points,fill=color,width=3)
  dr.text((25,91),'bar',font=font(20),fill=(127,146,142));dr.text((110,377),'INLET 4.18     OUTLET 3.82',font=font(29),fill=(176,196,187));dr.text((110,424),'VIB  2.4 mm/s    MOTOR 64 C',font=font(27),fill=(144,175,161))
 dr.line((0,474,1024,474),fill=(50,73,72),width=2);dr.text((24,484),'B2 / MECHANICAL    |    NO ACTIVE TRIP',font=font(18),fill=(108,145,129));im.save(P/f'BR_Display_{number:02}.png')
labels={3:('RUN    STOP    MODE    SPEED    RESET       E-STOP',(1024,128)),4:('B2 / PLC-201   IP54',(512,128)),5:('P-202 SPARE / INSPECTED',(1024,256)),6:('ISO VG 46\nSEALED OIL',(512,256)),7:('LUBRICATION / SEAL SERVICE',(1024,160))}
for i,(txt,size) in labels.items():
 im=Image.new('RGB',size,(55,61,59));dr=ImageDraw.Draw(im);dr.rectangle((3,3,size[0]-4,size[1]-4),outline=(119,123,111),width=3)
 if i==3:
  for x,label in [(.535,'E-STOP'),(.35,'RESET'),(.14,'SPEED'),(-.11,'MODE'),(-.30,'STOP'),(-.49,'RUN')]:dr.text(((.6225-x)/1.245*1024,9),label,anchor='mt',font=font(22),fill=(189,192,172))
 else:dr.multiline_text((16,14),txt,font=font(30),fill=(189,192,172),spacing=14)
 im.save(P/f'BR_Display_{i:02}.png')
print('Floor maps, PBR tiles and readable control screens ready')
