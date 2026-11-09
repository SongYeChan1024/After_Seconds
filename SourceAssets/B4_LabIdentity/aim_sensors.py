"""Orient optical heads toward the measured subject/lane/fixture, not out of the rig."""
import sys,json,bpy
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));import common as m
m.manifest.update(json.loads((H/'models.json').read_text(encoding='utf8')))
prefixes=('Sensor_Housing','Lens_Barrel','Optical_Coating','Captive_Screw','Screw_Slot')
for name in ['LB_PrecisionPlatform','LB_TrajectoryGantry','LB_MetrologyIsland','LB_OpticalCalibrationBench','LB_SignalAnalysisBench']:
 bpy.ops.wm.open_mainfile(filepath=str(H/(name+'.blend')))
 heads=[o for o in bpy.context.scene.objects if o.name.startswith('Sensor_Housing')]
 def center(o):return sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
 for head in heads:
  if head.get('sensor_aimed'):continue
  p=center(head);x,y,z=-p.x,p.z,-p.y
  if name=='LB_PrecisionPlatform':target=Vector(m.b.xyz(0,y,0))
  elif name=='LB_TrajectoryGantry':target=Vector(m.b.xyz(0,y,z))
  else:target=Vector(m.b.xyz(x,1.105,0))
  rot=Vector((0,-1,0)).rotation_difference((target-p).normalized()).to_matrix().to_4x4();M=Matrix.Translation(p)@rot@Matrix.Translation(-p)
  parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(prefixes) and (center(o)-p).length<.19]
  for o in parts:o.matrix_world=M@o.matrix_world
  head['sensor_aimed']=True
 print('AIMED',name,len(heads),flush=True);m.save(name)
