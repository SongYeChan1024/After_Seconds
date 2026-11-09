import sys,json,bpy
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
import common as m
m.manifest.update(json.loads((H/'models.json').read_text(encoding='utf8')))
src=(H/'build.py').read_text(encoding='utf8');part=src[src.index("bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/B4_LayoutPolish/BP_BenchKit_3.blend'))"):]
exec(part,m.__dict__)
