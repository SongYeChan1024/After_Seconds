"""실험동 문 검수 산출물 정리. 작성자: 송예찬."""
from pathlib import Path
import json,hashlib,re
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[1];O=R/'Docs/검수/2026-11-07_C01_Doors'
baseline=json.loads((H/'baseline.json').read_text('utf-8'))
changed=[p for p,h in baseline['protected'].items() if not (R/p).is_file() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
def blocks(path):
 s=path.read_text('utf-8');return {key:body for key,body in re.findall(r'^--- !u!\d+ &(-?\d+)([^\n]*\n[\s\S]*?)(?=^--- !u!|\Z)',s,re.M)}
old=blocks(Path(baseline['backup'])/'Level_B5_Circular.unity');now=blocks(R/baseline['scene'])
diff=[]
for key,b in old.items():
 if now.get(key)!=b:diff.append(dict(id=key,type=b.splitlines()[1],oldFather=re.findall(r'm_Father:.*',b),newFather=re.findall(r'm_Father:.*',now.get(key,''))))
door_ids={'350186563','515884787','1090667923'}
def in_old_doors(key):
 seen=set()
 while key in old and key not in seen:
  if key in door_ids:return True
  seen.add(key);parent=re.search(r'm_(?:Father|TransformParent): \{fileID: (-?\d+)\}',old[key])
  if not parent:return False
  key=parent[1]
 return False
unexpected=[row['id'] for row in diff if not in_old_doors(row['id'])]
result=dict(protectedFiles=len(baseline['protected']),changedProtectedFiles=changed,oldSceneObjects=len(old),removedSceneObjects=[k for k in old if k not in now],changedOriginalSceneObjects=diff,unexpectedChangesOutsideThreeOriginalDoors=unexpected)
(O/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
rows=['Door_B5-T01_0','Door_B5-T03_4','Door_B5-T11_q'];out=Image.new('RGB',(1600,3*544),(22,28,34));d=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
for i,key in enumerate(rows):
 for j,prefix in enumerate(['Before','After']):
  im=Image.open(O/f'{prefix}_{key}_Room.png');im.thumbnail((800,500));out.paste(im,(800*j,i*544+44));d.text((800*j+18,i*544+10),f'{key}  |  '+('수정 전' if j==0 else '수정 후'),font=font,fill=(225,235,240))
out.save(O/'BeforeAfter.jpg',quality=93)
print(json.dumps(dict(protected=len(baseline['protected']),changed=changed,originalSceneBlocksChanged=len(diff),removed=len(result['removedSceneObjects']),unexpectedSceneChanges=unexpected),ensure_ascii=False))
