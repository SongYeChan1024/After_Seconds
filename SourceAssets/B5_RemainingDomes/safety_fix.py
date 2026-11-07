import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import *
import build
build.manifest.update(json.loads((H/'models.json').read_text(encoding='utf-8')))
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/T02_StairA/TA_VA_SafetyEquipment.blend'))
for o in list(bpy.context.scene.objects):
 inter=any(k in o.name for k in ['Intercom','Speaker','CallButton']);old=(2.75,-3.84) if inter else(-2.9,-3.72);new=(-4.70,0) if inter else(0,4.68);oldyaw=math.atan2(-old[0],-old[1]);newyaw=math.atan2(-new[0],-new[1]);rot=Matrix.Translation(Vector(xyz(new[0],0,new[1])))@Matrix.Rotation(-(newyaw-oldyaw),4,'Z')@Matrix.Translation(-Vector(xyz(old[0],0,old[1])));o.matrix_world=rot@o.matrix_world
for m in bpy.data.materials:
 if m.name.startswith('TA_'):m.name=m.name.replace('TA_','RD_',1)
export('VB_SafetyEquipment',True)
