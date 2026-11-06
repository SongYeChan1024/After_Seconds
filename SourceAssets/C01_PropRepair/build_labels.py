"""병 표면에 밀착할 인쇄 라벨. 작성자: 송예찬."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5/Textures'
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',n)
for key,title,code,band in [('SpecimenA','SPECIMEN','04218-A',(35,93,104)),('SpecimenB','SPECIMEN','04219-B',(95,113,82)),('Reagent','REAGENT','R-061107',(134,104,54))]:
 im=Image.new('RGB',(768,512),(225,231,218));d=ImageDraw.Draw(im);d.rectangle((0,0,768,92),fill=band);d.text((24,19),title,font=font(46),fill=(242,246,236));d.text((26,120),code,font=font(60),fill=(30,53,58));d.text((28,208),'LOT 061107  /  LAB A',font=font(32),fill=(38,59,61));d.text((28,264),'DATE  07.11  /  QC',font=font(28),fill=(52,70,70))
 for j in range(57):
  if j%5!=3:d.rectangle((28+j*8,335,30+j*8+j%3,445),fill=(27,45,48))
 d.text((28,463),'ASE  /  TRACEABLE SAMPLE',font=font(22),fill=(42,64,65))
 for j in range(6):
  y=152+j*57;d.line((628,y,688 if j%2==0 else 665,y),fill=(40,62,64),width=4)
  if j%2==0:d.text((695,y-14),str(5-j),font=font(23),fill=(40,62,64))
 im.save(O/f'PR_Label_{key}.png')
im=Image.new('RGB',(384,512),(220,229,213));d=ImageDraw.Draw(im)
for pad in [9,15]:d.rounded_rectangle((pad,pad,383-pad,511-pad),radius=4,outline=(107,140,134),width=2)
d.rectangle((25,32,359,86),fill=(43,81,88));d.text((43,43),'STERILE PACK',font=font(30),fill=(236,243,230))
d.text((30,112),'SEALED / SINGLE USE',font=font(24),fill=(36,64,66));d.text((30,157),'LOT 061107\nQC  PASSED\nLAB A',font=font(27),fill=(42,63,64),spacing=10)
for i in range(37):
 if i%5!=3:d.rectangle((31+i*8,320,33+i*8+i%2,417),fill=(33,57,61))
d.text((32,444),'ASE / 07.11',font=font(24),fill=(45,68,67));im.save(O/'PR_Label_Pouch.png')
print('3 curved-label textures and 1 sterile-pouch print created')
