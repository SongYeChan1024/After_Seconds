from pathlib import Path
import importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[1]
spec=importlib.util.spec_from_file_location('b3_inherited_geometry',R/'SourceAssets/B4_FullFloor/common.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
for k,v in base.__dict__.items():
 if not k.startswith('_') and k not in ['H','R','save']:globals()[k]=v
b.H=H;b.manifest=json.loads((H/'models.json').read_text()) if (H/'models.json').exists() else {}
def reset():
 base.reset()
 for i in range(1,24):
  n=f'B3_Display_{i:02}';m=bpy.data.materials.new(n);m.diffuse_color=(.12,.15,.18,1);b.mats[f'Display_{i:02}']=m
def save(name,category='Environment'):
 b.OUT=b.A/category/'B3';b.raw_export('BS_'+name);b.manifest['BS_'+name]['category']=category
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf-8')
