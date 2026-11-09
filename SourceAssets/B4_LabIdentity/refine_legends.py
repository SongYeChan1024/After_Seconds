import sys,json,bpy
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));import common as m
m.manifest.update(json.loads((H/'models.json').read_text(encoding='utf8')))
bpy.ops.wm.open_mainfile(filepath=str(H/'LB_RecordWorkstation.blend'))
fixed=0;total=0
for o in bpy.context.scene.objects:
 if not o.name.startswith('Key_Legend'):continue
 total+=1
 if o.data.polygons[0].normal.z<0:o.data.flip_normals();fixed+=1
print('KEY_NORMALS',fixed,'flipped of',total,flush=True)
m.save('LB_RecordWorkstation',False)
