"""Original procedural PBR surfaces: peeled plaster, oxidised steel, cracked paving, soils."""
from pathlib import Path
import sys,json,math
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';sys.path.insert(0,str(U/'Temp/ZFightingReview/deps'))
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
O=U/'Assets/Afrer_Seconds/05.Model/Environment/1F/Textures';O.mkdir(parents=True,exist_ok=True)
N=1024;rng=np.random.default_rng(1728)
def noise(cells):
 a=rng.random((cells,cells)).astype(np.float32);a=np.pad(a,((0,1),(0,1)),mode='wrap');x=np.arange(N)/N*cells;i=x.astype(int);f=x-i;f=f*f*(3-2*f);v=(1-f)[None,:]*a[:,i]+f[None,:]*a[:,i+1];return (1-f)[:,None]*v[i,:]+f[:,None]*v[i+1,:]
def fractal():return noise(4)*.38+noise(9)*.28+noise(21)*.19+noise(65)*.1+noise(180)*.05
def blend(a,b,t):return np.array(a)[None,None,:]*(1-t[:,:,None])+np.array(b)[None,None,:]*t[:,:,None]
def save(name,rgb,height,metal=0,smooth=.15):
 rgb=np.uint8(np.clip(rgb,0,255));Image.fromarray(rgb).save(O/f'AE_{name}_Albedo.png')
 dx=(np.roll(height,-1,1)-np.roll(height,1,1))*8;dy=(np.roll(height,-1,0)-np.roll(height,1,0))*8;v=np.stack((-dx,dy,np.ones_like(dx)),axis=2);v/=np.linalg.norm(v,axis=2,keepdims=True);Image.fromarray(np.uint8(np.clip((v*.5+.5)*255,0,255))).save(O/f'AE_{name}_Normal.png')
 m=np.empty((N,N,4),dtype=np.uint8);m[:,:,0]=int(metal*255);m[:,:,1:3]=0;m[:,:,3]=np.uint8(np.clip((smooth+(height-height.mean())*.1)*255,0,255));Image.fromarray(m).save(O/f'AE_{name}_Mask.png')

f=fractal();detail=noise(200);yy,xx=np.mgrid[:N,:N];rows=yy//43;brickx=(xx+(rows%2)*62)//124;brickseed=rng.uniform(.65,1.15,(25,10));shade=brickseed[np.minimum(rows,24),np.minimum(brickx,9)];mortar=((yy%43)<4)|(((xx+(rows%2)*62)%124)<5)
brick=np.stack((118*shade,83*shade,61*shade),2)+(detail[:,:,None]-.5)*17;brick[mortar]=[81,81,71]
plaster=blend((103,105,90),(173,168,141),np.clip(f*1.35-.10,0,1));peel=np.clip((f-.46)*25,0,1);rgb=brick*(1-peel[:,:,None])+plaster*peel[:,:,None]
# Hairline fissures and damp islands are albedo variation, not a uniform noise coating.
rgb*=np.clip(.68+noise(7)*.55,.60,1.08)[:,:,None];height=peel*.2+np.where(mortar,0,.05)+detail*.014;save('Plaster',rgb,height,0,.11)
f=fractal();rust=np.clip((f-.40)*8,0,1);rgb=blend((57,72,63),(132,75,36),rust);rgb*= (.72+noise(85)*.5)[:,:,None];bare=(noise(35)>.77);rgb[bare]*=.7;save('Corrosion',rgb,rust*.045+noise(150)*.015,.35,.19)
f=fractal();rgb=blend((76,78,67),(139,134,113),f);im=Image.fromarray(np.uint8(rgb));d=ImageDraw.Draw(im);height=noise(180)*.012+f*.025
for i in range(24):
 x,y=rng.uniform(0,N,2);pts=[(int(x),int(y))]
 for j in range(int(rng.integers(5,13))):x+=rng.uniform(-38,38);y+=rng.uniform(13,45);pts.append((int(x)%N,int(y)%N))
 for a,b in zip(pts,pts[1:]):
  if abs(a[0]-b[0])+abs(a[1]-b[1])<150:d.line([a,b],fill=(41,44,37),width=int(rng.integers(1,4)))
 for j in range(0,len(pts)-1,3):
  x,y=pts[j];d.line([(x,y),(x+int(rng.uniform(-50,50)),y+int(rng.uniform(15,70)))],fill=(57,60,48),width=1)
save('Concrete',np.array(im),height,0,.15)
for name,a,b in [('Earth',(49,44,32),(103,88,61)),('Gravel',(63,61,49),(133,126,101)),('Moss',(36,43,23),(79,88,47))]:
 f=fractal();rgb=blend(a,b,f);fine=noise(240);rgb*= (.86+fine*.28)[:,:,None]
 if name=='Gravel':rgb+=np.clip((fine-.6)*80,0,18)[:,:,None]
 save(name,rgb,f*.04+fine*.035,0,.08)

# Overcast panoramic sky, seamless around the azimuth. No source photograph is modified.
W,HH=2048,1024;sky=np.zeros((HH,W,3));oldN=N;N=W;cloud=fractal();N=oldN
for y in range(HH):
 lat=y/(HH-1);base=np.array([61,70,75])*(1-lat)+np.array([142,146,136])*lat;layer=cloud[min(y*2,W-1),:];sky[y]=base+(layer[:,None]-.5)*58*(1-min(1,abs(lat-.38)*1.6))
sky[HH//2:]=np.array([98,102,93]);Image.fromarray(np.uint8(np.clip(sky,0,255))).save(O/'AE_OvercastSky.png')

# An original faded graffiti atlas; used sparingly on exterior wall planes.
im=Image.new('RGBA',(1024,1024));dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',105)
for i,word in enumerate(['ECHO','NO WAY','VOID','RUST']):
 y=i*256;box=dr.textbbox((0,0),word,font=font,stroke_width=8);x=(1024-(box[2]-box[0]))/2;dr.text((x,y+45),word,font=font,fill=(174,181,151,165),stroke_width=8,stroke_fill=(48,53,46,185))
 for j in range(15):
  x=int(rng.integers(250,800));dr.line((x,y+165,x+int(rng.integers(-6,6)),y+int(rng.integers(180,240))),fill=(114,131,106,100),width=int(rng.integers(2,6)))
im.save(O/'AE_Graffiti.png')
print('Generated 6 PBR surfaces, overcast panorama and original tags',flush=True)
