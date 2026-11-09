from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1]
for n in ['LodExport.cs','LodImport.cs','LodApply.cs','lods.py']:
 s=(R/'SourceAssets/B3_FullFloor'/n).read_text(encoding='utf8').replace('B3_FullFloor','B2_Cooling').replace('B3Lod','B2Lod').replace('Level_B3_Circular','Level_B2_Circular').replace('/B3/','/B2/').replace("/'B3'","/'B2'").replace('AssetDatabase.SaveAssets();','')
 (H/n).write_text(s,encoding='utf8')
im=Image.new('RGB',(1024,512),(220,218,200));d=ImageDraw.Draw(im);font='C:/Windows/Fonts/consolab.ttf'
d.rectangle((16,16,1008,496),outline=(160,31,27),width=14)
for p,t,s in [((60,48),'FIRE EQUIPMENT',77),((60,180),'HOSE / EXTINGUISHER',48),((60,290),'KEEP ACCESS CLEAR',48),((60,400),'CHECK SEAL BEFORE USE',35)]:d.text(p,t,font=ImageFont.truetype(font,s),fill=(130,24,19))
im.save(R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B2/Textures/BC_Display_10.png')
