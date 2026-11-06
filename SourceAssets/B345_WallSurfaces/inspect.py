import bpy,json
from pathlib import Path
from collections import Counter
r=Path(__file__).resolve().parents[2]
rows={}
for f in ('B5','B4','B3'):
 p=r/('SourceAssets/B345_Dressing/SD_B3_Architecture.blend' if f=='B3' else f'SourceAssets/LevelContinuation/LC_{f}_Architecture.blend')
 bpy.ops.wm.open_mainfile(filepath=str(p))
 mats={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  m=o.data.materials[0].name
  if any(k in m for k in ['Wall','Clinical','Staff','Service','Concrete','Panel']):
   z=mats.setdefault(m,{'count':0,'examples':[]});z['count']+=1
   if len(z['examples'])<4:z['examples'].append({'name':o.name,'dims':list(o.dimensions),'loc':list(o.location),'bevel':[(q.name,q.width) for q in o.modifiers if q.type=='BEVEL']})
 rows[f]=mats
(r/'SourceAssets/B345_WallSurfaces/source_inspection.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows),flush=True)
