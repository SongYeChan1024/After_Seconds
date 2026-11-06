"""Physically separated clinical surface maps; authored locally. 송예찬."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures'
N=1024;rng=np.random.default_rng(71107)
families={'Coat':((205,215,216),0,.38),'Blue':((93,132,139),0,.40),'Steel':((179,186,190),.96,.30),'Dark':((32,42,49),0,.47),'Rubber':((20,25,29),0,.75),'Paper':((219,220,209),0,.78)}
def noise(scale):
 n=rng.integers(50,205,(scale,scale),dtype=np.uint8);im=Image.fromarray(n).resize((N,N),Image.Resampling.BICUBIC);return (np.asarray(im,dtype=np.float32)-127.5)/127.5
report={}
for name,(rgb,metal,rough) in families.items():
 fine=noise(512);broad=noise(32);soft=noise(8)
 if name=='Steel':
  # Directional brushing, with subtle polishing variation rather than painted scratches.
  row=rng.normal(0,.24,(N,1));height=row+fine*.055;variation=row*2+soft*2;roughmap=np.clip(rough+row*.06+broad*.035,.05,.95)
 elif name=='Rubber':height=fine*.35+broad*.1;variation=fine*2;roughmap=np.clip(rough+broad*.05,.1,.95)
 elif name=='Paper':height=fine*.12;variation=fine*1.3+broad*1.2;roughmap=np.clip(rough+fine*.025,.1,.95)
 else:height=fine*.12+broad*.025;variation=fine*1.0+soft*1.8;roughmap=np.clip(rough+broad*.035+soft*.02,.1,.95)
 albedo=np.clip(np.array(rgb)[None,None,:]+variation[:,:,None],0,255).astype(np.uint8)
 # Periodic gradients: tangent-space OpenGL normal, with deliberately restrained amplitude.
 dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.32;dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.32
 normal=np.dstack((-dx,dy,np.ones_like(dx)));normal/=np.linalg.norm(normal,axis=2)[:,:,None];normal=np.clip((normal*.5+.5)*255,0,255).astype(np.uint8)
 mask=np.zeros((N,N,4),dtype=np.uint8);mask[:,:,0]=int(metal*255);mask[:,:,1]=255;mask[:,:,2]=0;mask[:,:,3]=((1-roughmap)*255).astype(np.uint8)
 Image.fromarray(albedo).save(O/f'PF_{name}_Base.png');Image.fromarray(normal).save(O/f'PF_{name}_Normal.png');Image.fromarray(mask).save(O/f'PF_{name}_MOS.png')
 Image.fromarray((roughmap*255).astype(np.uint8)).save(H/f'PF_{name}_Roughness.png')
 report[name]={'baseColor':rgb,'metallic':metal,'roughnessMean':float(roughmap.mean()),'packed':'R=metallic,G=1 (no fabricated AO),B=unused,A=1-roughness','normal':'tangent-space +Y','resolution':N}
# Manufacturing legends and graduations complement actual geometry, not game instructions.
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',n)
for key,title,sub in [('Microscope','OPTICAL SYSTEM','40x / 0.65  •  FINE FOCUS'),('PCR','THERMAL CYCLER','96 WELL BLOCK  /  HOT SURFACE'),('Centrifuge','CENTRIFUGE','BALANCE ROTOR  /  LID LOCK'),('Wash','ULTRASONIC BATH','40 kHz  /  MAX FILL'),('Sterilizer','STEAM STERILIZER','121 °C  /  PRESSURE VESSEL'),('Pipette','MICROPIPETTE','100 – 1000 µL'),('Vial','SPECIMEN','LOT 061107  /  STERILE'),('Glove','NITRILE GLOVES','POWDER FREE   •   M'),('Mask','PROTECTIVE MASK','SINGLE USE  /  SEALED'),('Sealer','STERILE PACK','LOT 061107  /  QC PASSED'),('Barcode','SAMPLE 004218','ID 004218-07  /  LAB A')]:
 im=Image.new('RGB',(768,256),(212,219,213));d=ImageDraw.Draw(im);d.rectangle((0,0,768,55),fill=(35,74,82));d.text((23,10),title,font=font(29),fill=(230,239,237));d.text((23,80),sub,font=font(25),fill=(36,60,65))
 for i in range(53):d.rectangle((24+i*8,145,26+i*8+(i%3),220),fill=(34,53,59))
 d.text((495,150),'ASE\n0611 / 07',font=font(27),fill=(42,66,72));im.save(O/f'PF_Decal_{key}.png')
im=Image.new('RGB',(512,512),(216,226,220));d=ImageDraw.Draw(im);d.ellipse((8,8,504,504),fill=(221,230,224),outline=(40,58,63),width=9)
for i in range(31):
 a=np.deg2rad(135+i*9);r=208;rr=180 if i%5==0 else 193;d.line((256+r*np.cos(a),256+r*np.sin(a),256+rr*np.cos(a),256+rr*np.sin(a)),fill=(30,48,56),width=3)
d.text((192,325),'bar',font=font(44),fill=(35,65,70));d.text((140,390),'0 — 3.0',font=font(30),fill=(45,68,73));im.save(O/'PF_Decal_Gauge.png')
(H/'pbr_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('18 PBR runtime maps + 12 manufactured decals; roughness originals kept in SourceAssets')
