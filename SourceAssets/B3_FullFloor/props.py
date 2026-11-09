import sys,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *

def init():
 reset()
 for i,c in enumerate([(.22,.26,.28,1),(.34,.36,.34,1),(.19,.22,.24,1),(.46,.48,.44,1),(.30,.32,.34,1),(.38,.39,.36,1)]):
  m=bpy.data.materials.new(f'B3_Case_{i}');m.diffuse_color=c;b.mats[f'Case{i}']=m
 m=bpy.data.materials.new('B3_Labels');m.diffuse_color=(.78,.80,.75,1);b.mats['Labels']=m

def label(x,y,z,w=.18,h=.07,idx=0):
 o=mesh('Inventory_Label',[(x-w/2,y-h/2,z),(x+w/2,y-h/2,z),(x+w/2,y+h/2,z),(x-w/2,y+h/2,z)],[(0,3,2,1)],'Labels',0)
 if o.data.polygons[0].normal.y>0:o.data.flip_normals()
 uv=o.data.uv_layers.new(name='UVMap');u=(idx%4)/4;v=1-(idx//4+1)/8
 coords=[(u+.25,v),(u,v),(u,v+.125),(u+.25,v+.125)]
 for p in o.data.polygons:
  for li in p.loop_indices:uv.data[li].uv=coords[o.data.loops[li].vertex_index]
 o['display_uv']=True

def crate(x,y,z,w=.46,h=.29,d=.40,k=0):
 mat=f'Case{k%6}';box('Insulated_Case',x,y+h/2,z,w,h,d,mat,.014);box('Lid_Gasket',x,y+h-.035,z,w+.008,.014,d+.008,'Rubber',.005);box('Clamped_Lid',x,y+h-.010,z,w+.014,.033,d+.014,mat,.012)
 for xx in [-1,1]:
  for zz in [-1,1]:box('Corner_Guard',x+xx*(w/2-.015),y+h/2,z+zz*(d/2-.012),.039,h-.035,.035,'Steel',.006)
 for xx in [-w*.31,w*.31]:
  box('Over_Centre_Latch',x+xx,y+h-.065,z+d/2+.012,.045,.08,.025,'Steel',.005);cyl('Latch_Pin',(x+xx-.019,y+h-.037,z+d/2+.026),(x+xx+.019,y+h-.037,z+d/2+.026),.004,'Steel',8)
 box('Handle_Recess',x,y+h*.48,z+d/2+.005,.15,.06,.008,'Dark',.006);cyl('Inset_Handle',(x-.055,y+h*.48,z+d/2+.017),(x+.055,y+h*.48,z+d/2+.017),.008,'Steel',12);label(x,y+h*.77,z+d/2+.018,min(w*.35,.19),.047,k%12)

for variant in range(3):
 init();rng=random.Random(330+variant);w=2.65;d=.90;h=2.55
 for x in [-w/2,0,w/2]:
  for z in [-d/2,d/2]:
   box('Rolled_Upright',x,h/2,z,.048,h,.048,'Steel',.005);box('Anchored_Foot',x,.018,z,.12,.036,.12,'Steel',.006)
   for yy in [.4,1.05,1.7,2.35]:bolt(x,yy,z+.028)
 for y in [.18,.77,1.36,1.95,2.54]:
  box('Folded_Load_Shelf',0,y,0,w,.040,d,'Coat',.006);box('Front_Label_Channel',0,y+.018,d/2+.014,w,.055,.020,'Steel',.004);label(0,y+.02,d/2+.026,.34,.055,12+variant)
 for x in [-w/2+.02,w/2-.02]:tube('Rear_Cross_Brace',[(x,.2,-d/2),(0,1.3,-d/2),(x,2.5,-d/2)],.010,'Steel')
 for row,y in enumerate([.205,.795,1.385,1.975]):
  for col,x in enumerate([-.98,-.36,.36,.98]):
   if rng.random()<.13:continue
   crate(x+rng.uniform(-.035,.035),y,rng.uniform(-.10,.07),.49,rng.choice([.26,.31,.36]),.50,rng.randrange(6))
   if row<3 and rng.random()<.28:crate(x,y+.36,.02,.40,.16,.36,rng.randrange(6))
 save('SampleRack_'+str(variant+1),'Props')

for typ in ['DeepFreezer','ColdCabinet']:
 init();w=1.05;d=.88;h=2.12;feet(w,d);box('Insulated_Cabinet',0,1.11,0,w,2.0,d,'Coat',.026);box('Compressor_Base',0,.22,.02,w+.03,.3,d+.04,'Steel',.01);vent(0,.24,d/2+.03,.82,.19)
 box('Magnetic_Door_Seal',0,1.23,d/2+.017,.95,1.67,.045,'Rubber',.017);box('Insulated_Door',0,1.23,d/2+.055,.91,1.63,.075,'Case3' if typ=='DeepFreezer' else 'Case1',.024)
 for y in [.60,1.76]:box('Heavy_Hinge',-.47,y,d/2+.1,.065,.17,.07,'Steel',.007)
 for y in [1.05,1.45]:cyl('Latch_Bracket',(.34,y,d/2+.1),(.34,y,d/2+.18),.020,'Steel',16)
 cyl('Pull_Lever',(.34,1.04,d/2+.18),(.34,1.46,d/2+.18),.024,'Dark',20);display(-.10,1.91,d/2+.11,.38,.13,1 if typ=='DeepFreezer' else 2);label(-.07,1.52,d/2+.096,.35,.15,15 if typ=='DeepFreezer' else 16)
 for x in [-.38,.38]:tube('Compressor_Service_Loop',[(x,.3,-.46),(x,.8,-.49),(x*.7,1.0,-.49)],.016,'Steel')
 save(typ,'Props')

for variant in [1,2]:
 init();w=.78;d=1.04;h=2.25
 for x in [-w/2,w/2]:
  for z in [-d/2,d/2]:box('Rack_Frame',x,h/2,z,.055,h,.055,'Steel',.005)
 for y in [.08,2.2]:box('Rack_End',0,y,0,w+.06,.10,d+.06,'Dark',.009)
 for x in [-w/2,w/2]:box('Rack_Side',x,1.13,0,.028,2.10,d-.06,'Case2',.005)
 for i in range(9):
  y=.30+i*.205;box('Server_Blade',0,y,.06,.69,.17,.87,'Case2' if i%3 else 'Case0',.007);box('Blade_Faceplate',0,y,.52,.70,.16,.018,'Steel',.003)
  for x in [-.30,.30]:tube('Rack_Handle',[(x,y-.047,.532),(x,y-.047,.566),(x,y+.047,.566),(x,y+.047,.532)],.006,'Steel')
  for j in range(8):box('Airflow_Slot',-.18+j*.037,y,.533,.018,.065,.004,'Dark',.001)
  for j in range(3):box('Drive_Status',.18+j*.024,y+.038,.537,.009,.008,.005,'Indicator' if (i+j)%4 else 'Hazard',.001)
  label(.20,y-.035,.536,.12,.028,(17+i)%32)
 for i in range(6):
  x=-.25+i*.10;tube('Rear_Patch_Lead',[(x,1.9,-.55),(x+.02,1.7,-.62),(.30,1.5-i*.11,-.62),(.30,.2,-.58)],.005,'Teal' if i%2 else 'Dark')
 display(0,2.11,.56,.32,.10,3+variant);save('ServerRack_'+str(variant),'Props')

init();cabinet(1.22,1.90,.66,'doors','Case2');display(0,1.65,.40,.34,.17,6);label(0,1.20,.374,.40,.16,23);save('ArchiveUPS','Props')

if True:
 init();w=2.2;d=1.1
 for x in [-.96,.96]:
  for z in [-.43,.43]:box('Bench_Leg',x,.48,z,.065,.96,.065,'Steel',.006);box('Levelling_Pad',x,.035,z,.1,.07,.1,'Rubber',.009)
 box('Lower_Service_Tray',0,.23,0,2.06,.035,.85,'Steel',.006);box('Worktop_Substrate',0,.95,0,w,.065,d,'Coat',.012);box('Stainless_Worktop',0,.987,0,w+.025,.014,d+.025,'Steel',.006)
 box('Balance_Antivibration_Base',-.60,1.025,.04,.59,.055,.48,'Dark',.009);box('Sample_Balance',-.60,1.09,.04,.48,.09,.39,'Coat',.012);cyl('Balance_Pan',(-.60,1.135,.02),(-.60,1.15,.02),.16,'Steel',48);display(-.60,1.09,.26,.22,.065,7)
 box('Scanner_Dock',.56,1.015,.18,.16,.025,.18,'Dark',.010);tube('Handheld_Scanner',[(.56,1.03,.18),(.56,1.16,.12),(.56,1.20,.01)],.035,'Case2');tube('Scanner_Coil',[(.56,1.05,.15),(.62,1.03,-.1),(.70,1.02,-.39),(.70,.86,-.49)],.004,'Dark')
 for i in range(3):crate(-.18+i*.39,1.0,-.18,.28,.15,.29,i+1)
 display(.53,1.40,-.40,.55,.32,8);monitor_stand(.53,1.40,-.40,.55,.32,top=.995);label(-.10,.93,.566,.33,.10,25);save('AccessionBench','Props')

if True:
 init();cabinet(1.9,.90,.75,'drawers');box('Packing_Top',0,.93,0,2.0,.05,.9,'Steel',.009)
 box('Heat_Sealer_Base',-.48,.995,.06,.70,.08,.30,'Case1',.012);box('Heat_Seal_Arm',-.48,1.075,.03,.68,.06,.075,'Coat',.012);cyl('Sealer_Hinge',(-.81,1.04,-.05),(-.81,1.04,.16),.035,'Steel',20);display(-.48,1.0,.22,.22,.055,9)
 for i in range(4):box('Folded_Sterile_Pouch',.33+i*.055,.969+i*.002,.09,.34,.002,.25,'Paper',.001)
 crate(.56,.96,-.20,.36,.18,.29,3);label(.60,.85,.392,.36,.12,26);save('PackingBench','Props')

if True:
 init();w=2.45;h=2.40
 box('Filter_Cabinet',0,h/2,0,w,h,.52,'Coat',.018)
 for x in [-.79,0,.79]:
  for y in [.62,1.76]:
   box('Filter_Frame',x,y,.28,.71,1.03,.07,'Steel',.012);box('Filter_Media',x,y,.325,.62,.93,.012,'Case1',.002)
   for j in range(15):box('Pleated_Filter_Rib',x-.29+j*.041,y,.34,.007,.89,.013,'Dark',.001)
   for yy in [y-.43,y+.43]:bolt(x-.28,yy,.35);bolt(x+.28,yy,.35)
 display(0,2.32,.34,.46,.10,10);save('FilterBank','Props')

if True:
 init();box('Zone_Isolator_Housing',0,.18,0,.34,.36,.12,'Coat',.014);box('Switch_Backplate',0,.18,.066,.28,.29,.012,'Dark',.008)
 for x in [-.065,.065]:box('Rocker_Switch',x,.16,.083,.065,.10,.035,'Case3',.006)
 label(0,.285,.075,.24,.065,27);box('Power_Status',.085,.235,.086,.012,.012,.01,'Indicator',.002);save('ZoneLightingPanel','Props')

if True:
 init();box('Containment_Platform',0,.035,0,2.5,.07,1.4,'Steel',.01)
 for x in [-.84,0,.84]:
  box('Waste_Receptacle',x,.59,0,.70,1.05,.72,'Case1',.022);box('Containment_Lid',x,1.14,0,.73,.09,.75,'Coat',.024);box('Seal_Band',x,1.095,0,.72,.016,.74,'Rubber',.005)
  label(x,.86,.371,.38,.18,28 if x<0 else 29);tube('Lid_Handle',[(x-.13,1.19,0),(x-.13,1.24,0),(x+.13,1.24,0),(x+.13,1.19,0)],.015,'Steel')
 save('SealedWasteStation','Props')
print('B3_PROPS_DONE',flush=True)
