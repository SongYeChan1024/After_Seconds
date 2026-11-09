"""Smooth supported desktop runs and rounded rear service loops; retain actual plug endpoints."""
import sys,json,bpy
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));import common as m
m.manifest.update(json.loads((H/'models.json').read_text(encoding='utf8')))
bpy.ops.wm.open_mainfile(filepath=str(H/'LB_RecordWorkstation.blend'))
paths={
'Keyboard_USB':[(.035,.928,.305),(.035,.923,.265),(-.09,.9175,.214),(-.24,.9175,.08),(-.30,.9175,-.30),(-.325,.9175,-.535),(-.325,.88,-.57),(-.35,.81,-.60),(-.49,.785,-.67),(-.62,.79,-.725),(-.72,.86,-.725),(-.74,.95,-.68),(-.74,.978,-.626),(-.74,.978,-.616)],
'Mouse_USB':[(-.43,.937,.336),(-.43,.924,.28),(-.45,.9175,.20),(-.40,.9175,.08),(-.355,.9175,-.16),(-.335,.9175,-.54),(-.335,.88,-.57),(-.37,.80,-.61),(-.49,.775,-.69),(-.59,.79,-.745),(-.67,.86,-.735),(-.69,.95,-.68),(-.69,.978,-.626),(-.69,.978,-.616)],
'Display_Data':[(0,1.176,-.514),(0,1.154,-.548),(-.14,1.04,-.60),(-.35,.945,-.635),(-.52,.98,-.64),(-.60,1.039,-.626),(-.60,1.039,-.616)],
'Display_Power':[(-.086,1.176,-.514),(-.10,1.13,-.55),(-.17,.98,-.615),(-.235,.91,-.72),(-.235,.84,-.75),(-.23,.79,-.70),(-.22,.783,-.59),(-.22,.783,-.50)],
'PC_Power':[(-.54,1.039,-.616),(-.54,1.015,-.642),(-.48,.94,-.72),(-.41,.86,-.75),(-.37,.80,-.69),(-.36,.783,-.60),(-.36,.783,-.50)]}
dark=bpy.data.materials.get('B4O_Dark')
for name,pts in paths.items():
 for o in list(bpy.context.scene.objects):
  if o.name==name:bpy.data.objects.remove(o,do_unlink=True)
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=18;cu.bevel_depth=.0018 if 'USB' in name else .0025;cu.bevel_resolution=2;s=cu.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 coords=[Vector(m.b.xyz(*p)) for p in pts]
 for i,p in enumerate(s.bezier_points):
  p.co=coords[i];p.handle_left_type='FREE';p.handle_right_type='FREE';prev=coords[max(0,i-1)];nxt=coords[min(len(coords)-1,i+1)];t=(nxt-prev).normalized()
  # Surface runs stay tangent to the desktop; hanging sections preserve continuous tangency.
  if abs(pts[i][1]-.9175)<1e-5:t.z=0;t.normalize()
  p.handle_left=p.co-t*(p.co-prev).length*.24;p.handle_right=p.co+t*(nxt-p.co).length*.24
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(dark);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob=bpy.context.object
 for f in ob.data.polygons:f.use_smooth=True
m.save('LB_RecordWorkstation',False)
