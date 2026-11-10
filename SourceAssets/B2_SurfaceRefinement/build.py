"""B2 close-view machinery props. Metres; bevelled Blender source, no game code."""
import sys,json,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'SourceAssets/B2_FullFloor'))
from common import *
H=Path(__file__).resolve().parent;R=H.parents[1]
b.H=H;b.OUT=b.A/'Props/B2';b.manifest={}
def start():
 reset()
 for key in list(b.mats):b.mats[key].name='BR_'+key
def panel(n,x,y,z,w,h,key):
 ob=b.print_panel(n,x,y,z,w,h,key);return ob
def save(n):
 b.raw_export('BR_'+n)
 ob=bpy.context.object;mod=ob.modifiers.new('DistanceReduction','DECIMATE');mod.ratio=.40;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name);ob.name='BR_'+n+'_Far'
 bpy.ops.export_scene.fbx(filepath=str(b.OUT/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
 b.manifest[ob.name]={'triangles':len(ob.data.polygons),'distance_only':True}
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
start()
# A folded sheet enclosure, separate doors and recessed seals; no fused AI geometry.
box('RecessedPlinth',0,.08,0,1.28,.16,.77,'Dark',.008)
box('FoldedCabinet',0,.54,-.03,1.34,.91,.83,'Coat',.014)
for x in [-.325,.325]:
 box('DoorGasket',x,.53,.394,.635,.78,.023,'Rubber',.004)
 box('ServiceDoor',x,.53,.410,.613,.758,.018,'Coat',.005)
 for yy in [.27,.79]:
  box('HingeLeaf',x+(-.278 if x<0 else .278),yy,.431,.055,.10,.026,'Steel',.003)
  cyl('HingePin',(x+(-.278 if x<0 else .278),yy-.054,.45),(x+(-.278 if x<0 else .278),yy+.054,.45),.008,'Steel',12)
 hx=x+(.22 if x<0 else -.22)
 box('LatchRecess',hx,.64,.424,.055,.14,.014,'Dark',.004)
 box('RecessedLatch',hx,.64,.438,.025,.09,.018,'Steel',.004)
 for yy in [.19,.87]:
  for xx in [x-.23,x+.23]:bolt(xx,yy,.424)
box('WorktopLip',0,1.025,.02,1.39,.055,.94,'Steel',.01)
box('SlopedControlHousing',0,1.10,.18,1.35,.10,.54,'Coat',.009)
box('UpperDisplayHousing',0,1.30,-.14,1.35,.49,.20,'Coat',.012)
for i,x in enumerate([-.325,.325],1):
 box('DisplaySeal',x,1.35,-.026,.601,.338,.025,'Rubber',.006)
 box('MachinedDisplayBezel',x,1.35,-.006,.579,.316,.024,'Dark',.006)
 panel('ReadableProcessLCD',x,1.35,.008,.535,.270,i)
 for dx in [-.276,.276]:
  for dy in [-.140,.140]:bolt(x+dx,1.35+dy,.008)
 # Small hardware status lamps below the display.
 for j,key in enumerate(['Indicator','Indicator','Red']):cyl('StatusLens',(x-.07+j*.07,1.13,.456),(x-.07+j*.07,1.13,.466),.009,key,16)
box('ControlsFace',0,1.08,.455,1.28,.13,.018,'Dark',.004)
panel('EngravedControlLegends',0,1.083,.466,1.245,.107,3)
for i,x in enumerate([-.49,-.30,-.11,.14,.35]):
 cyl('ControlCollar',(x,1.083,.468),(x,1.083,.48),.031,'Steel',24)
 if i<2:cyl('StartStopButton',(x,1.083,.481),(x,1.083,.505),.024,'Indicator' if i==0 else 'Red',24)
 else:
  cyl('RotarySelector',(x,1.083,.481),(x,1.083,.509),.022,'Dark',20)
  box('SelectorGrip',x,1.083,.517,.013,.045,.016,'Steel',.003)
cyl('EmergencyStopCollar',(.535,1.06,.468),(.535,1.06,.487),.043,'Hazard',32)
cyl('MushroomStop',(.535,1.06,.486),(.535,1.06,.526),.033,'Red',32)
for side in [-1,1]:
 for y in [.26+i*.024 for i in range(10)]:box('SideCoolingLouvre',side*.675,y,-.07,.012,.009,.38,'Dark',.002)
 for z in [-.29,.23]:
  box('AnchorTab',side*.57,.027,z,.18,.054,.13,'Steel',.004)
  cyl('AnchorHead',(side*.57,.055,z),(side*.57,.068,z),.014,'Steel',6)
box('RearRemovablePlate',0,.59,-.46,1.05,.57,.018,'Coat',.004)
for x in [-.46,.46]:
 for y in [.36,.82]:
  cyl('RearFastener',(x,y,-.477),(x,y,-.466),.008,'Steel',6)
for x in [-.39,-.13,.13,.39]:
 cyl('CableGland',(x,.23,-.45),(x,.23,-.49),.028,'Steel',16)
 tube('ProtectedFloorCable',[(x,.23,-.49),(x,.11,-.55),(x,.055,-.52)],.016,'Rubber')
panel('AssetIdentification',.325,.84,.427,.25,.065,4)
save('PlantConsole')

start()
box('ContainmentBase',0,.07,0,1.38,.14,.90,'Dark',.01)
for x in [-.59,.59]:box('PalletRunner',x,.03,0,.13,.06,.96,'Steel',.005)
for z in [-.44,.44]:box('RetainingLip',0,.17,z,1.42,.20,.035,'Coat',.004)
for x in [-.695,.695]:box('RetainingLip',x,.17,0,.035,.20,.86,'Coat',.004)
for x in [-.33,.33]:
 box('VibrationPad',x,.162,0,.33,.045,.66,'Rubber',.003)
 for z in [-.34,.34]:cyl('TieDownEye',(x,.23,z),(x,.23,z+.018),.03,'Steel',16)
panel('SpareMotorTag',0,.155,.461,.40,.12,5)
save('PartsCradle')

start()
# Lubrication / seal servicing station for the empty east side of C01.
box('BundedServiceBase',0,.09,0,1.35,.18,.72,'Dark',.012)
for z in [-.35,.35]:box('SpillLip',0,.17,z,1.38,.18,.03,'Steel',.004)
for x in [-.66,.66]:box('SpillLip',x,.17,0,.03,.18,.70,'Steel',.004)
box('ServiceBackboard',0,1.10,-.31,1.30,1.6,.065,'Coat',.012)
for x in [-.57,.57]:box('FrameLeg',x,.98,-.34,.07,1.96,.075,'Steel',.004)
for x in [-.30,.30]:
 cyl('SealedOilReservoir',(x,.20,.02),(x,.91,.02),.22,'Coat',40)
 for yy in [.25,.73,.90]:cyl('DrumBead',(x,yy-.012,.02),(x,yy+.012,.02),.228,'Steel',40)
 cyl('ReservoirLid',(x,.91,.02),(x,.945,.02),.225,'Steel',40)
 cyl('PumpHead',(x,.95,.02),(x,1.13,.02),.045,'Steel',24)
 cyl('PumpHandle',(x-.13,1.14,.02),(x+.13,1.14,.02),.018,'Dark',16)
 points=[Vector(p) for p in [(x,1.08,.08),(x,1.26,.18),(x+.12,1.33,.22),(x+.18,1.15,.25),(x+.14,.65,.27),(x+.07,.47,.23)]];curve=[]
 for j in range(len(points)-1):
  a=points[max(0,j-1)];c=points[j];d=points[j+1];e=points[min(len(points)-1,j+2)]
  for k in range(8):
   t=k/8;curve.append(tuple(.5*((2*c)+(-a+d)*t+(2*a-5*c+4*d-e)*t*t+(-a+3*c-3*d+e)*t*t*t)))
 curve.append(tuple(points[-1]));tube('MeteredSupplyHose',curve,.015,'Rubber')
 gauge(x,1.52,-.245)
 tube('GaugeSenseLine',[(x,1.10,.02),(x,1.10,-.28),(x,1.32,-.28)],.009,'Steel')
 panel('LubricantContainerLabel',x,.59,.246,.28,.14,6)
box('MeterFace',0,1.75,-.26,1.1,.20,.03,'Dark',.005)
panel('LubricationStationIdentity',0,1.75,-.242,1.06,.16,7)
for x in [-.57,.57]:
 for y in [.39,1.74]:bolt(x,y,-.27)
save('LubricationStation')
print('B2 surface-refinement models ready',flush=True)
