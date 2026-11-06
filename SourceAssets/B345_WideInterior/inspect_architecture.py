import bpy,json
from pathlib import Path
S=Path(__file__).resolve().parent
for f in ('B5','B4','B3'):
 bpy.ops.wm.open_mainfile(filepath=str(S/f'WC_{f}_Architecture.blend'))
 rows=[dict(name=o.name,material=o.data.materials[0].name,pos=[24-o.location.x,o.location.z,16-o.location.y],dims=list(o.dimensions)) for o in bpy.context.scene.objects if o.type=='MESH' and ('Ceiling' in o.name or 'Screen' in o.name)]
 (S/f'{f}_architecture_parts.json').write_text(json.dumps(rows,indent=2));print(f,len(rows),[r['name'] for r in rows][:20],flush=True)
