from pathlib import Path
import json
H=Path(__file__).resolve().parent;s=(H/'build.py').read_text(encoding='utf-8')
exec(compile(s[:s.index('\nreset()\nfor i in range')],str(H/'build.py'),'exec'))
manifest=json.loads((H/'model_manifest.json').read_text(encoding='utf-8'))
a=s.index('\nreset()\n# Eight');b=s.index('\nreset()\n# B4 level')
exec(compile(s[a:b],str(H/'build.py'),'exec'))
reset();bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=4.94,depth=.016,location=xyz(0,.002,0));bpy.context.object.data.materials.append(mats['Floor']);export('TA_VA_Floor')
(H/'model_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
