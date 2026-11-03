# [의사코드] 저장된 배치·반입 명세를 따라 모델/시각 배치와 검수 결과를 재현한다.
# [코딩]
"""의사코드: 기존 모델 검수 렌더를 이름과 함께 한 장에 배열한다."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];paths=sorted((R/'prepared').glob('*/preview.png'))
cols=4;tile=370;label=42;rows=math.ceil(len(paths)/cols)
sheet=Image.new('RGB',(cols*tile,rows*(tile+label)),(35,35,35));draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for index,path in enumerate(paths):
    image=Image.open(path).convert('RGB');image.thumbnail((tile,tile));x=(index%cols)*tile;y=(index//cols)*(tile+label)
    sheet.paste(image,(x+(tile-image.width)//2,y));draw.text((x+8,y+tile+8),path.parent.name,fill='white',font=font)
sheet.save(R/'prepared'/'asset_contact_sheet.png');print('SHEET',len(paths),flush=True)

# [주석] 검수 자료의 작업 순서와 최신 경로표를 확인한 뒤 사용한다.
