from pathlib import Path
import re,json,hashlib
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-07_C01_PortalTiles'
b=json.loads((H/'baseline.json').read_text('utf-8'));changed=[p for p,h in b['protected'].items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
def blocks(p):return {k:v for k,v in re.findall(r'^--- !u!\d+ &(-?\d+)([^\n]*\n[\s\S]*?)(?=^--- !u!|\Z)',p.read_text('utf-8'),re.M)}
old=blocks(Path(b.get('effectiveSceneBackup',str(Path(b['backup'])/'Level_B5_Circular.unity'))))
lighting=R/'SourceAssets/C01_Lighting/baseline.json'
end=Path(json.loads(lighting.read_text('utf-8'))['backup'])/'Level_B5_Circular.unity' if lighting.exists() else R/b['scene']
now=blocks(end);delta=[dict(id=k,type=v.splitlines()[1],before=v,after=now.get(k)) for k,v in old.items() if now.get(k)!=v]
result=dict(protectedFiles=len(b['protected']),changedProtectedFiles=changed,userPendingEditsPreserved=b.get('userPendingEditsPreserved',False),baseline=b.get('effectiveSceneBackup'),removedOriginalSceneObjects=[k for k in old if k not in now],changedOriginalSceneObjects=delta)
(O/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
out=Image.new('RGB',(1600,3*544),(22,28,34));d=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
for i,key in enumerate(['Door_B5-T01_0','Door_B5-T03_4','Door_B5-T11_q']):
 for j,pre in enumerate(['Before','After']):
  im=Image.open(O/f'{pre}_{key}_Room.png');im.thumbnail((800,500));out.paste(im,(j*800,i*544+44));d.text((j*800+18,i*544+10),key+' | '+('타일 보수 전' if j==0 else '타일 연결 후'),font=font,fill=(225,235,240))
out.save(O/'BeforeAfter.jpg',quality=93)
print(json.dumps(dict(protected=len(b['protected']),changed=changed,removed=len(result['removedOriginalSceneObjects']),sceneChanges=[dict(id=r['id'],type=r['type']) for r in delta],userPendingEditsPreserved=result['userPendingEditsPreserved']),ensure_ascii=False))
