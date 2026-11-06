"""V0.01: correct upper Stair B lens face and synchronize final B3 lighting/plan."""
import bpy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
exec(compile((HERE/'build_sections.py').read_text(encoding='utf-8').split("for floor in ('B5','B4'):")[0],str(HERE/'build_sections.py'),'exec'))
for floor in ('B4','B3'):
 SRC=HERE if floor=='B4' else REPO/'SourceAssets/B3_StealthLayout'
 data=json.loads((SRC/(floor+'_sections.json')).read_text(encoding='utf-8'))
 colliders[:]=data['colliders'];lightdefs[:]=data['lights']
 if floor=='B3':
  for row in lightdefs:
   if row['name'].startswith('Ceiling_'):row['intensity']=24 if row['position'][1]>4.2 else 18
   elif row['name']=='LiftInterior':row['intensity']=14
 bpy.ops.wm.open_mainfile(filepath=str(SRC/('LC_'+floor+'_Architecture.blend')))
 fixed=0
 for ob in bpy.context.scene.objects:
  if ob.name.startswith('LC_StepLightLens') and abs((24-ob.location.x)-43.676)<.005:
   ob.location.x-=.108;fixed+=1
 if fixed!=1:raise RuntimeError(f'Expected one inward-facing lens, found {fixed}')
 export(floor,[None]*data['removedSourceObjects'])
 if floor=='B3':
  plan=next(p for p in json.loads((REPO/'Docs/도면/잠입_탐색/layout.json').read_text(encoding='utf-8-sig'))['floors'] if p['floor']=='B3')
  (SRC/'plan_snapshot.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
 print('FINAL_MODEL',floor,fixed,flush=True)
