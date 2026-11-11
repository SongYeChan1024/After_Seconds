from pathlib import Path
import json,shutil,hashlib,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2];H=Path(__file__).parent;P=ROOT/'Unity/After_Seconds_Build_V0.01'
backup=Path.home()/'Documents/Codex/Backups/AfterSeconds_ZFighting_20261111'
backup.mkdir(parents=True,exist_ok=True)
protected={}
for p in (P/'Assets/Afrer_Seconds').rglob('*'):
 if p.is_file() and (p.suffix in ('.cs','.unity','.controller','.inputactions','.asmdef') or '07.Animator' in str(p) or p.suffix=='.prefab'):
  rel=p.relative_to(P).as_posix();protected[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
  if p.suffix=='.unity':
   dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   if not dst.exists():shutil.copy2(p,dst)
if not (H/'protected_before.json').exists():(H/'protected_before.json').write_text(json.dumps(protected,indent=2))
shots=[]
for name in ['Level_B2_Circular','Level_B3_Circular','Level_B4_Circular','Level_B5_Circular']:
 p=H/'results'/f'{name}.json'
 if not p.exists():continue
 d=json.loads(p.read_text());rows=d['rows'];selected=[]
 for typ in ['VerticalStairs','StairsToB1','DeckStructure','Floor','Shell']:
  a=next((a for a in d['overlaps'] if typ in rows[a['a']]['path'] and a['maxArea']>.05),None)
  if a and a not in selected:selected.append(a)
 for i,a in enumerate(selected):
  at=np.array(a['point']);n=np.array(a['normal']);p=at+n*2.0+np.array([.5,.6,.2]);
  if abs(n[1])>.9:p=at+n*1.6+np.array([.8,0,1.2])
  shots.append(dict(scene=d['scene'],name=f'{name}_{i}',position=p.tolist(),target=at.tolist(),candidate=a))
shots.append(dict(scene='Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity',name='B4_VA_user_view',position=[-44.53,-64.49,25.70],target=[-44.76,-66.2,28.70]))
(H/'shots.json').write_text(json.dumps(shots,indent=2))
print('Protected',len(protected),'shots',len(shots),'backup',backup)
