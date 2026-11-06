import bpy,bmesh,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/B5_Sector01/S1_VitalMonitor.blend'))
out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 out.append(dict(name=o.name,vertices=len(bm.verts),faces=len(bm.faces),boundary=sum(e.is_boundary for e in bm.edges),nonmanifold=sum(not e.is_manifold for e in bm.edges),wire=sum(e.is_wire for e in bm.edges),dimensions=list(o.dimensions),location=list(o.location),rotation=list(o.rotation_euler),materials=[m.name for m in o.data.materials],modifiers=[(m.name,m.type) for m in o.modifiers],bounds=[list(v) for v in o.bound_box]));bm.free()
(H/'vital_source_inventory.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
