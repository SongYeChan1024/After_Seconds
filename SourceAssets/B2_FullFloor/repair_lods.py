from pathlib import Path
import json
H=Path(__file__).resolve().parent
old=json.loads((H/'lod_models.json').read_text());cat=json.loads((H/'lod_catalog.json').read_text());names={r['name'].rsplit('_LOD',1)[0] for r in cat if r['inverted']>r['tri']*.02}
s=(H/'lods.py').read_text();s=s.replace('for p in plan:',f'plan=[p for p in plan if p["name"] in {names!r}]\nfor p in plan:');s=s.replace("  bpy.ops.export_scene.fbx(","  ob.data.normals_split_custom_set([(0,0,0)]*len(ob.data.loops))\n  for poly in ob.data.polygons:poly.use_smooth=False\n  bpy.ops.export_scene.fbx(")
exec(compile(s,str(H/'lods.py'),'exec'),{'__file__':str(H/'lods.py')})
new={r['name']:r for r in json.loads((H/'lod_models.json').read_text())};merged=[new.get(r['name'],r) for r in old];(H/'lod_models.json').write_text(json.dumps(merged,indent=2))
