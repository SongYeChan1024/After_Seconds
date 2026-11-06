from pathlib import Path
import json,hashlib,re
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-07_C01_Lighting';b=json.loads((H/'baseline.json').read_text('utf-8'))
changed=[p for p,h in b['protected'].items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
def blocks(p):return {k:v for k,v in re.findall(r'^--- !u!\d+ &(-?\d+)([^\n]*\n[\s\S]*?)(?=^--- !u!|\Z)',p.read_text('utf-8'),re.M)}
old=blocks(Path(b['backup'])/'Level_B5_Circular.unity');now=blocks(R/b['scene']);delta=[dict(id=k,type=v.splitlines()[1],before=v,after=now.get(k)) for k,v in old.items() if now.get(k)!=v]
result=dict(protectedFiles=len(b['protected']),changedProtectedFiles=changed,removedOriginalSceneObjects=[k for k in old if k not in now],changedOriginalSceneObjects=delta)
(O/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
out=Image.new('RGB',(1600,1088),(22,28,34));d=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
for i,key in enumerate(['S1_WallTaskLight_03','WorkArea']):
 for j,pre in enumerate(['Before','After']):
  im=Image.open(O/f'{pre}_{key}.png');im.thumbnail((800,500));out.paste(im,(j*800,i*544+44));d.text((j*800+18,i*544+10),('조명 보수 전' if j==0 else '등기구와 광원 연결 후'),font=font,fill=(225,235,240))
out.save(O/'BeforeAfter.jpg',quality=93)
print(json.dumps(dict(protected=len(b['protected']),changed=changed,sceneChanges=len(delta),removed=len(result['removedOriginalSceneObjects'])),ensure_ascii=False))
