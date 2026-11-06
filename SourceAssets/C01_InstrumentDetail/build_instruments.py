"""Distinct static bench instruments and storage modules for the accepted C01 layout. 송예찬."""
from pathlib import Path
import math,json
H=Path(__file__).resolve().parent;R=H.parents[1]
lib=R/'SourceAssets/C01_Perimeter/build_assets.py';c={'__file__':str(lib),'__name__':'detail_helpers'}
exec(compile(lib.read_text('utf-8').split('reset();base();')[0],str(lib),'exec'),c)
c['e']['H']=H;e=c['e'];box=c['box'];cyl=c['cyl'];tube=c['tube'];screen=c['screen'];label=c['label'];reset=c['reset'];export=c['export'];mesh=c['mesh'];bottle=c['bottle'];rack=c['rack'];pull=c['pull'];bpy=c['bpy']
def feet(w,d):
 for x in [-w*.39,w*.39]:
  for z in [-d*.37,d*.37]:cyl('Isolating_Foot',(x,0,z),(x,.035,z),.027,'Rubber',16)
def housing(w,h,d,kind='Prep'):
 feet(w,d);box('Instrument_Shell',0,h/2+.03,0,w,h,d,'Coat',.014)
 box('Removable_ServicePanel',0,h*.50,-d/2-.004,w*.87,h*.78,.012,'Blue',.005)
 for x in [-w*.42,w*.42]:
  for y in [.07,h-.015]:cyl('Captive_Screw',(x,y,d/2),(x,y,d/2+.005),.006,'Steel',6)
 for i in range(7):box('Vent_Louvre',w/2+.002,h*.5+i*.024-h*.07,-.03,.006,.009,d*.45,'Dark',.002)
 label(-w*.22,.10,d/2+.005,min(.22,w*.4),kind)
def circle_glass(n,x,y,z,r,mat='ID_DisplayGlass'):
 c['display']['mat'](e,mat,(.4,.6,.65,.045));vs=[(x,y,z)]+[(x+r*math.cos(a),y+r*math.sin(a),z) for a in [i*math.tau/64 for i in range(64)]];mesh(n,vs,[(0,i+2,i+1) for i in range(63)]+[(0,1,64)],mat,0)
def torus(n,x,y,z,major,minor,mat='Steel'):
 pts=[(x+major*math.cos(i*math.tau/64),y+major*math.sin(i*math.tau/64),z) for i in range(65)];tube(n,pts,minor,mat,12)

reset()
feet(.55,.52);box('Microscope_Foot',0,.06,0,.55,.075,.50,'Coat',.02)
mesh('Curved_Optical_Stand',[(-.08,.1,-.16),(.08,.1,-.16),(.08,.1,-.04),(-.08,.1,-.04),(-.08,.54,-.22),(.08,.54,-.22),(.08,.58,-.10),(-.08,.58,-.10)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Coat',.02)
box('Mechanical_Stage',0,.30,.02,.38,.035,.30,'Dark',.007);box('Specimen_Slide',0,.323,.04,.13,.006,.045,'Paper',.001)
for x in [-.09,.09]:box('Slide_Clip',x,.328,.045,.018,.008,.11,'Steel',.002)
cyl('Illuminator',(0,.105,.04),(0,.16,.04),.055,'Steel',24);cyl('Condenser',(0,.245,.04),(0,.28,.04),.038,'Dark',24)
cyl('Optical_Head',(0,.48,-.10),(0,.64,-.10),.065,'Coat',24)
for x in [-.042,.042]:cyl('Binocular_Tube',(x,.62,-.08),(x,.72,.035),.025,'Dark',20);cyl('Eyecup',(x,.714,.03),(x,.738,.055),.033,'Rubber',20)
for i in range(3):
 a=i*math.tau/3;x,z=.05*math.cos(a),-.025+.05*math.sin(a);cyl('Objective', (x,.405,z),(x,.47,z),.018,'Steel',20)
for x in [-.105,.105]:cyl('Coarse_Focus',(x,.42,-.17),(x*1.30,.42,-.17),.042,'Dark',24)
label(0,.084,.254,.20,'Optics');export('ID_BinocularMicroscope')

reset();housing(.70,.19,.56,'Thermal');box('Thermal_Block',0,.32,-.06,.56,.21,.42,'Blue',.014)
box('Heated_Lid',0,.446,-.06,.57,.045,.43,'Coat',.012);pull(0,.42,.165,.25)
for i in range(3):box('Lid_Hinge',-.19+i*.19,.42,-.282,.07,.055,.03,'Steel',.005)
screen(.08,.16,.288,.33,.14,'PCR');cyl('Start_Key',(-.26,.17,.285),(-.26,.17,.298),.025,'Blue',20);export('ID_ThermalCycler')

reset()
box('Pipetting_Deck',0,.025,0,.99,.05,.52,'Steel',.01)
for x in [-.39,-.12]:
 box('Tip_Box',x,.10,-.04,.20,.10,.24,'Blue',.006)
 for i in range(5):
  for j in range(6):cyl('Sterile_Tip',(x+(i-2)*.032,.15,-.12+j*.031),(x+(i-2)*.032,.17,-.12+j*.031),.006,'Paper',8)
box('Pipette_Stand_Base',.27,.06,-.12,.30,.035,.20,'Dark',.006)
for x in [.18,.36]:cyl('Stand_Upright',(x,.08,-.17),(x,.41,-.17),.01,'Steel',12)
box('Pipette_Hanger',.27,.42,-.13,.31,.025,.12,'Coat',.004)
for x in [.17,.27,.37]:cyl('Pipette_Body',(x,.19,-.06),(x,.45,-.06),.018,'Paper',16);cyl('Plunger',(x,.45,-.06),(x,.48,-.06),.023,'Blue',16);cyl('Pipette_Tip',(x,.12,-.06),(x,.19,-.06),.006,'Steel',10)
rack(.24,.05,.12,5);label(-.28,.061,.267,.22,'Prep');export('ID_PipetteWorkstation')

reset();housing(.94,.56,.55,'Fluidics')
box('Sample_Loader',-.28,.21,.34,.28,.14,.20,'Blue',.01);rack(-.28,.28,.34,3)
screen(.21,.37,.284,.30,.22,'Plate')
for x in [-.30,-.16]:bottle(x,.5905,-.12,.052,.20)
for x in [-.30,-.16]:tube('Fluidics_Line',[(x,.8055,-.12),(x,.88,-.10),(x+.06,.88,.06),(x+.06,.58,.12)],.008,'Rubber',8)
export('ID_FlowCytometer')

reset();housing(.58,.13,.50,'Optics')
screen(0,.13,.255,.34,.095,'Balance')
for x in [-.24,.24]:
 for z in [-.19,.15]:box('DraftShield_Post',x,.36,z,.018,.44,.018,'Steel',.003)
box('DraftShield_Top',0,.585,-.02,.51,.024,.39,'Coat',.006)
c['display']['mat'](e,'ID_DisplayGlass',(.4,.6,.65,.045))
for z in [-.19,.15]:c['display']['make_quad'](e,'DraftShield_Window',0,.36,z,.47,.41,'ID_DisplayGlass')
for x in [-.24,.24]:mesh('DraftShield_Side',[(x,.155,-.19),(x,.565,-.19),(x,.565,.15),(x,.155,.15)],[(0,1,2,3)],'ID_DisplayGlass',0)
cyl('Weighing_Pan',(0,.18,-.02),(0,.202,-.02),.17,'Steel',48);cyl('Calibration_Weight',(0,.203,-.02),(0,.25,-.02),.03,'Steel',24)
pull(.19,.37,.158,.035);export('ID_PrecisionBalance')

reset();housing(.71,.16,.46,'Prep')
for x in [-.19,.19]:
 cyl('Ceramic_Hotplate',(x,.19,0),(x,.21,0),.14,'Paper',32);cyl('Reagent_Flask',(x,.21,0),(x,.37,0),.082,'Blue',32);cyl('Flask_Neck',(x,.37,0),(x,.45,0),.031,'Paper',24)
screen(0,.13,.239,.25,.09,'Bath');export('ID_DualMagneticStirrer')

reset();feet(.70,.58)
for i in range(3):
 y=.16+i*.215;box('Chromatography_Module',0,y,0,.63,.19,.52,'Coat',.008);box('Module_Seam',0,y+.096,0,.61,.012,.50,'Dark',.002)
 screen(.10,y,.268,.29,.105,'Chromatography')
 for x in [-.25,-.18]:cyl('Fluid_Port',(x,y,.265),(x,y,.285),.018,'Steel',16)
 for j,x in enumerate([-.25,-.18]):
  bx=(i-1)*.21+(j-.5)*.02;top=.98+i*.017
  tube('PEEK_Line',[(x,y,.29),(x-.025,y+.05,.31),(-.38-j*.018,y+.09,.23),(-.40-j*.018,top-.03,-.02),(-.38-j*.018,top,-.06),(bx,top,-.06),(bx,.9275,-.06)],.005,'Amber',8)
for x in [-.21,0,.21]:bottle(x,.6925,-.06,.066,.22)
label(0,.055,.27,.24,'Fluidics');export('ID_ChromatographyStack')

reset();housing(.74,.32,.51,'Wash')
for x in [-.31,.31]:box('Bath_Rim',x,.36,0,.045,.025,.45,'Steel',.005)
for z in [-.20,.20]:box('Bath_Rim',0,.36,z,.59,.025,.045,'Steel',.005)
box('Bath_Recess',0,.34,0,.57,.018,.34,'Dark',.003)
for i in range(9):cyl('Basket_Wire',(-.25,.357,-.16+i*.04),(.25,.357,-.16+i*.04),.003,'Steel',8)
screen(.07,.21,.264,.30,.14,'Bath');pull(0,.38,.03,.36);export('ID_UltrasonicBath')

reset();box('Drainboard',0,.025,0,.95,.05,.50,'Steel',.008)
for x in [-.32,0,.32]:
 for z in [-.14,.05]:
  tube('Drying_Peg',[(x,.05,z),(x,.28,z-.04),(x,.33,z-.08)],.012,'Steel',12)
  cyl('Inverted_Flask',(x,.14,z-.02),(x,.30,z-.05),.06,'Paper',20)
box('Disassembly_Tray',.28,.07,.16,.28,.045,.11,'Blue',.004)
for i in range(4):cyl('Forceps',(-.39+i*.09,.066,.12),(-.39+i*.09,.066,.23),.006,'Steel',8)
export('ID_GlasswareDryingRack')

reset();housing(.82,.55,.61,'Thermal')
torus('Pressure_Door_Rim',-.15,.32,.315,.21,.023,'Steel');circle_glass('Door_Porthole',-.15,.32,.318,.18)
cyl('Inner_Door',(-.15,.32,.296),(-.15,.32,.308),.185,'Blue',64)
for y in [.19,.43]:box('Door_Hinge',-.355,y,.321,.045,.07,.045,'Steel',.006)
box('Door_Latch',.06,.32,.355,.05,.18,.06,'Dark',.008);screen(.27,.37,.314,.17,.19,'Sterilizer');export('ID_BenchAutoclave')

reset();housing(.96,.25,.58,'Optics')
box('Scanner_Bridge',0,.57,-.16,.77,.12,.22,'Coat',.014)
for x in [-.35,.35]:box('Bridge_Column',x,.40,-.16,.07,.24,.12,'Steel',.007)
box('Slide_Carrier',-.18,.31,.04,.39,.035,.32,'Dark',.004)
for i in range(4):box('Mounted_Slide',-.30+i*.08,.332,.04,.055,.004,.22,'Paper',.001)
cyl('Scanner_Optics',(-.12,.45,-.08),(-.12,.52,-.08),.05,'Dark',24);screen(.27,.23,.298,.29,.15,'Assay');export('ID_SlideScanner')

reset();housing(.51,.19,.44,'Prep')
for x in [-.13,.13]:cyl('Vortex_Rubber_Cup',(x,.22,0),(x,.26,0),.072,'Rubber',32);bottle(x,.225,0,.021,.14)
screen(0,.15,.228,.24,.10,'Centrifuge');export('ID_DualVortexMixer')

reset();housing(.88,.17,.55,'Prep')
box('Plate_Docking_Tray',-.16,.24,.04,.48,.06,.36,'Blue',.008)
for j in range(8):
 for i in range(12):cyl('Microplate_Well',(-.36+i*.037,.273,-.10+j*.04),(-.36+i*.037,.280,-.10+j*.04),.012,'Paper',10)
box('LiquidHandler_Mast',.28,.48,-.16,.15,.60,.17,'Coat',.012);box('Pipetting_Arm',-.06,.75,-.12,.72,.10,.18,'Coat',.012)
for i in range(8):cyl('Dispensing_Needle',(-.26+i*.039,.51,-.08),(-.26+i*.039,.70,-.08),.004,'Steel',8)
screen(.24,.17,.283,.27,.13,'Plate');export('ID_MicroplateHandler')

reset();housing(.71,.13,.48,'Prep')
for x in [-.27,.27]:box('Rotator_Support',x,.28,-.01,.04,.30,.12,'Coat',.006)
cyl('Rotation_Axle',(-.28,.39,0),(.28,.39,0),.018,'Steel',20)
for i in range(7):
 x=-.22+i*.073;cyl('Tube_Clamp',(x,.36,-.12),(x,.42,.12),.025,'Blue',16);cyl('Rotating_Sample',(x,.345,-.19),(x,.44,.19),.018,'Paper',16)
screen(0,.105,.249,.24,.08,'Centrifuge');export('ID_TubeRotator')

reset();housing(.84,.13,.46,'Prep');box('Heat_Sealing_Jaw',0,.28,-.08,.72,.10,.11,'Coat',.01)
for x in [-.34,.34]:box('Jaw_Hinge',x,.21,-.11,.045,.16,.06,'Steel',.005)
pull(0,.34,-.01,.29)
for i in range(3):box('Sterile_Pouch',-.20+i*.20,.176,.10,.16,.006,.24,'Paper',.001);box('Pouch_Seal',-.20+i*.20,.18,.20,.15,.002,.018,'Blue',0)
screen(.24,.115,.239,.19,.08,'Sterilizer');export('ID_SterileSealer')

reset();housing(.52,.40,.42,'Prep');box('Label_RollCover',0,.43,-.05,.48,.17,.30,'Blue',.016)
box('Label_OutputSlot',0,.23,.218,.30,.035,.02,'Dark',.003);box('Printed_Label_Strip',0,.18,.26,.18,.006,.12,'Paper',.001)
screen(0,.36,.219,.27,.12,'Printer');label(0,.09,.219,.22,'Prep')
box('Scanner_Cradle',.38,.065,.02,.18,.10,.25,'Dark',.01);tube('Hand_Scanner',[(.38,.12,.02),(.38,.26,.04),(.38,.29,.14)],.035,'Blue',16)
tube('Scanner_Cord',[(.36,.12,-.03),(.27,.045,-.16),(.14,.04,-.25),(.06,.15,-.22)],.008,'Rubber',8);export('ID_LabelPrinter')

# Storage alternatives keep the accepted footprint but vary door rhythm and silhouette.
reset();box('Freezer_Base',0,.08,0,.94,.16,.61,'Dark',.01);box('Freezer_Case',0,1.17,0,1.02,2.10,.68,'Coat',.013)
for y in [.37,.69,1.01,1.33,1.65]:
 box('Cryo_Drawer_Gasket',0,y,.35,.94,.29,.018,'Dark',.004);box('Cryo_Drawer',0,y,.368,.89,.25,.025,'Blue',.007);pull(0,y,.39,.41);label(.29,y,.39,.14,'Storage')
screen(0,2.03,.35,.43,.19,'Cold');export('ID_CryoDrawerBank')

reset();box('SpecimenCabinet_Base',0,.08,0,.94,.16,.61,'Dark',.01)
for x in [-.49,.49]:box('Cabinet_Side',x,1.17,0,.035,2.10,.68,'Coat',.01)
box('Cabinet_Back',0,1.17,-.32,.98,2.10,.035,'Coat',.006);box('Cabinet_Top',0,2.21,0,1.02,.04,.68,'Coat',.008)
for y in [.22,.61,1.0,1.39,1.78]:
 box('SpecimenShelf',0,y,0,.96,.027,.62,'Steel',.004)
 for i in range(3):box('Specimen_Box',-.31+i*.31,y+.134,.02,.27,.24,.43,'Paper',.008);label(-.31+i*.31,y+.15,.239,.16,'Storage')
for x in [-.47,0,.47]:box('Cabinet_Stile',x,1.17,.35,.04,2.05,.04,'Blue',.004)
for y in [.17,2.18]:box('Cabinet_Rail',0,y,.35,.98,.04,.04,'Blue',.004)
c['display']['mat'](e,'ID_DisplayGlass',(.4,.6,.65,.045))
for x in [-.235,.235]:c['display']['make_quad'](e,'Specimen_Glass',x,1.17,.351,.42,1.96,'ID_DisplayGlass');cyl('Vertical_Pull',(x*.18,.95,.39),(x*.18,1.31,.39),.012,'Steel',16)
export('ID_GlassSpecimenCabinet')

reset()
for x in [-.56,.56]:box('Shelf_Upright',x,.37,-.13,.028,.81,.04,'Steel',.003)
for y in [0,.36,.72]:box('Supply_Shelf',0,y,0,1.18,.025,.32,'Steel',.004)
for row in range(3):
 y=.013+row*.36
 if row==0:
  for x in [-.42,-.15,.17,.42]:box('Component_Bin',x,y+.08,0,.22,.16,.25,'Blue',.008);label(x,y+.09,.13,.14,'Prep')
 elif row==1:
  for x in [-.41,-.12,.23]:bottle(x,y,0,.065,.24)
 else:
  for i in range(4):box('Sterile_Kit',-.40+i*.27,y+.06,0,.23,.12,.25,'Paper',.006)
export('ID_MixedSupplyShelf')

reset();box('Upper_StorageCase',0,.36,0,1.21,.72,.34,'Coat',.01)
for y in [.19,.53]:
 box('LiftUp_Door',0,y,.18,1.16,.305,.025,'Blue',.008);pull(0,y-.10,.20,.34)
label(.41,.53,.197,.18,'Storage');export('ID_LiftUpUpperCabinet')

reset();c['base'](doors=False)
for y in [.26,.49,.72]:label(.40,y,.381,.15,'Prep')
box('Side_TowelRail',-.50,.80,.44,.018,.055,.10,'Steel',.004)
export('ID_IndexedDrawerBench')
(H/'assets_manifest.json').write_text(json.dumps(c['reports'],indent=2),encoding='utf-8')
print('INSTRUMENT VARIANTS',len(c['reports']))
