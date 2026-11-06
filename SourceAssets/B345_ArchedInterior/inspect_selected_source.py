import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(r/'SourceAssets/B345_WallSurfaces/WS_B5_Walls.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.data.materials[0].name!='WS_Steel':continue
 u=24-o.location.x;v=16-o.location.y
 if int(max(0,min(47.9,u))//8)==4 and int(max(0,min(31.9,v))//8)==1:rows.append({'name':o.name,'position':[u-24,o.location.z,v-16],'dimensions':list(o.dimensions),'sourceBatch':o.get('source_batch')})
print('SELECTED_SOURCES',json.dumps(rows),flush=True)
