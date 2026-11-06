"""Precision clinical furniture for C01. Authoring only; original assets untouched."""
from pathlib import Path
import math,json,sys
H=Path(__file__).resolve().parent;R=H.parents[1]
lib=R/'SourceAssets/B5_Sector01/build_details.py';e={'__file__':str(lib),'__name__':'clinical_helpers'}
helper=lib.read_text('utf-8').split('# Structural ribs')[0].replace('  for p in o.data.polygons:\n   axes=', '  if o.get("display_uv"):continue\n  for p in o.data.polygons:\n   axes=')
exec(compile(helper,str(lib),'exec'),e)
e['H']=H;bpy=e['bpy'];box=e['box'];cyl=e['cyl'];tube=e['tube'];mesh=e['mesh'];reports={}
import bmesh
def tube(n,points,r=.015,mat='Steel',sides=8):
    ob=e['tube'](n,points,r,mat,sides);bm=bmesh.new();bm.from_mesh(ob.data)
    boundary=[edge for edge in bm.edges if edge.is_boundary]
    if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();return ob
palette={'Coat':(.60,.70,.73,1),'Steel':(.38,.46,.50,1),'Dark':(.026,.043,.05,1),'Blue':(.12,.27,.31,1),'Screen':(.012,.035,.044,1),'Trace':(.16,.58,.57,1),'Paper':(.75,.78,.74,1),'Amber':(.61,.29,.07,1),'Glass':(.57,.77,.80,.16),'Rubber':(.014,.023,.026,1)}
def reset():
    e['reset']();e['mats'].clear()
    for key,col in palette.items():
        m=bpy.data.materials.new('CP_'+key);m.diffuse_color=col;m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=col;p.inputs['Metallic'].default_value=.78 if key=='Steel' else .1;p.inputs['Roughness'].default_value=.38 if key=='Steel' else .58;e['mats'][key]=m
def export(name):
    if '--polish-only' in sys.argv and name not in {'CP_EmergencyCabinet','CP_PerimeterServiceRuns'}:return
    finish=runpy.run_path(str(R/'SourceAssets/C01_PropFinish/finish_geometry.py'))
    finish['finish'](e,name);finish['export'](e,name,props=True);reports[name]=e['manifest'][name]
def pull(x,y,z,w=.22):
    for a in [-w/2,w/2]:cyl('HandleMount',(x+a,y,z),(x+a,y,z+.035),.009,'Steel',10)
    cyl('PullGrip',(x-w/2,y,z+.035),(x+w/2,y,z+.035),.011,'Steel',10)
def base(w=1.24,doors=True,top=True):
    box('Recessed_Plinth',0,.07,-.035,w-.12,.14,.64,'Dark',.01)
    for x in [-w/2+.015,w/2-.015]:box('Base_Side',x,.50,-.015,.03,.74,.72,'Coat',.006)
    box('Base_Back',0,.50,-.36,w,.74,.03,'Coat',.006)
    box('Base_Floor',0,.15,-.015,w,.035,.72,'Coat',.004)
    if doors:
        for x in [-w*.245,w*.245]:box('Lower_SealedDoor',x,.50,.36,w*.47,.69,.035,'Blue',.006);pull(x,.76,.385,w*.22)
    else:
        for y in [.26,.49,.72]:box('Drawer',0,y,.36,w-.055,.21,.035,'Coat',.005);pull(0,y+.035,.386,.32)
    if top:box('Seamless_Worktop',0,.925,0,w+.025,.055,.80,'Steel',.012)
import runpy
display=runpy.run_path(str(R/'SourceAssets/C01_InstrumentDetail/display_geometry.py'))
def screen(x,y,z,w=.47,h=.28,kind='Assay'):return display['screen'](e,x,y,z,w,h,kind)
def label(x,y,z,w=.18,kind='Optics'):return display['nameplate'](e,x,y,z,w,kind)
def bottle(x,y,z,r=.025,h=.12):
    cyl('Specimen_Vial',(x,y,z),(x,y+h,z),r,'Paper',12);cyl('Vial_Cap',(x,y+h,z),(x,y+h+.018,z),r*1.08,'Blue',12)
    # C01_PropRepair replaces these construction guides with detailed bottles and conformal printed labels.
def rack(x,y,z,count=5):
    box('VialRack',x,y+.025,z,count*.065+.04,.05,.15,'Blue',.004)
    for i in range(count):bottle(x+(i-(count-1)/2)*.065,y+.05,z,.021,.105)
def boxes(x,y,z,n=3):
    for i in range(n):
        box('Sealed_ReagentPack',x+i*.16,y+.085,z,.14,.17,.17,'Paper',.005)
        box('Pack_Band',x+i*.16,y+.085,z+.087,.13,.025,.002,'Blue',0)

reset();base();export('CP_LabBench')
reset();base(doors=False);export('CP_DrawerBench')

reset()
box('Sealed_UpperCase',0,.36,0,1.21,.72,.34,'Coat',.01)
for x in [-.30,.30]:box('Upper_Door',x,.36,.182,.576,.676,.025,'Coat',.007);pull(x,.12,.2,.18)
box('UnderCabinet_Light',0,-.022,.08,1.08,.028,.095,'Paper',.004)
export('CP_UpperCabinet')

reset()
for y in [0,.36,.72]:box('Shelf_Tray',0,y,.04,1.20,.025,.34,'Steel',.005)
for x in [-.56,.56]:box('Shelf_Upright',x,.36,-.115,.03,.80,.045,'Steel',.003)
boxes(-.47,.013,.02,4);rack(.18,.373,.02,6);boxes(-.46,.373,.02,2)
for x in [-.43,-.26,-.09]:bottle(x,.733,.02,.045,.22)
boxes(.13,.733,.02,3);export('CP_ReagentShelf')

reset()
box('Service_Backboard',0,.65,-.025,1.24,1.3,.08,'Coat',.006)
for y in [.12,.67,1.15]:box('Utility_Rail',0,y,.032,1.20,.045,.04,'Steel',.003)
for x in [-.43,-.27,.27,.43]:
    box('Sealed_Outlet',x,.14,.061,.09,.11,.035,'Dark',.004)
    for dx in [-.018,.018]:box('Outlet_Recess',x+dx,.14,.082,.009,.024,.003,'Steel',0)
for x in [-.38,.38]:
    cyl('Gas_Tap',(x,.70,.04),(x,.70,.11),.022,'Steel',12);box('Tap_Lever',x,.73,.112,.08,.018,.025,'Blue',.003)
export('CP_ServicePanel')

reset();base(top=False)
for x,w in [(-.54125,.1825),(.42125,.4225)]:box('Sink_Worktop_Side',x,.925,0,w,.055,.80,'Steel',.006)
for z,d in [(-.315,.17),(.33,.14)]:box('Sink_Worktop_End',-.12,.925,z,.66,.055,d,'Steel',.006)
box('Basin_Bottom',-.12,.77,.015,.66,.025,.49,'Steel',.004)
for x in [-.45,.21]:box('Basin_Side',x,.85,.015,.018,.17,.49,'Steel',.004)
for z in [-.23,.26]:box('Basin_End',-.12,.85,z,.66,.17,.018,'Steel',.004)
cyl('Drain',(-.12,.784,.02),(-.12,.790,.02),.032,'Dark',16)
tube('Gooseneck_Faucet',[(-.18,.96,-.30),(-.18,1.22,-.30),(-.18,1.28,-.23),(-.18,1.28,-.02),(-.18,1.22,.035)],.018,'Steel',12)
for x in [-.34,.01]:cyl('Tap_Stem',(x,.95,-.29),(x,1.01,-.29),.025,'Steel',12);box('Tap_Lever',x,1.025,-.27,.10,.018,.04,'Blue',.004)
box('Drying_Tray',.43,.975,.04,.25,.04,.47,'Blue',.005)
for z in [-.14,-.04,.06,.16]:cyl('Drying_Peg',(.43,.98,z),(.43,1.10,z),.008,'Steel',8)
export('CP_WashBench')

reset()
box('ColdStore_Plinth',0,.08,0,.94,.16,.61,'Dark',.01);box('ColdStore_Housing',0,1.17,0,1.02,2.10,.68,'Coat',.014)
for y,h in [(.75,1.05),(1.79,.85)]:
    box('Door_Gasket',0,y,.35,.95,h,.028,'Dark',.007);box('Insulated_Door',0,y,.372,.90,h-.045,.035,'Blue',.008)
    cyl('Vertical_Pull',(-.35,y-.20,.41),(-.35,y+.20,.41),.015,'Steel',12)
screen(.14,2.08,.367,.28,.13,'Cold');label(-.19,1.11,.40,.25,'Storage')
for i in range(10):box('Condenser_Vent',-.36+i*.08,.18,.36,.035,.08,.018,'Dark',.002)
export('CP_ColdStorage')

reset()
# Deck instrument: visible sample carousel, optical head and vertical cartridge magazine.
box('Instrument_Plinth',0,.045,0,1.0,.09,.61,'Dark',.012)
box('Optical_Analyzer_Base',0,.18,0,.97,.24,.59,'Coat',.018)
box('Reader_Tower',.30,.43,-.11,.30,.50,.32,'Coat',.015)
box('Optical_Arm',-.02,.64,-.08,.72,.10,.22,'Coat',.012)
cyl('Optical_Lens',(-.23,.54,-.02),(-.23,.59,-.02),.045,'Dark',20)
cyl('Sample_Carousel',(-.22,.31,.045),(-.22,.36,.045),.19,'Blue',24)
for i in range(8):
    a=i*math.tau/8;bottle(-.22+.13*math.cos(a),.36,.045+.13*math.sin(a),.018,.08)
for i in range(3):
    box('Cartridge_Slot',.18+i*.09,.329,.17,.065,.018,.18,'Dark',.002)
    box('Inserted_Cartridge',.18+i*.09,.38,.17,.054,.095,.15,'Paper',.004)
screen(.30,.55,.069,.21,.14)
cyl('Emergency_Button',(.42,.26,.30),(.42,.26,.32),.023,'Amber',12)
label(-.25,.18,.302,.22,'Optics')
for x in [-.40,.40]:
    for z in [-.23,.23]:cyl('Vibration_Isolator',(x,-.002,z),(x,.03,z),.035,'Rubber',16)
for x in [-.43,.43]:
    for y in [.11,.25]:cyl('Captive_Panel_Screw',(x,y,.30),(x,y,.304),.005,'Steel',6)
export('CP_OpticalAnalyzer')

reset()
box('Centrifuge_Base',0,.06,0,.67,.12,.57,'Dark',.014)
box('Centrifuge_Housing',0,.25,0,.64,.34,.54,'Coat',.018)
cyl('Sealed_Rotor_Cover',(0,.42,-.025),(0,.46,-.025),.235,'Blue',32)
pull(0,.455,.13,.20);screen(0,.25,.28,.33,.13,'Centrifuge');label(-.17,.105,.292,.18,'Thermal')
export('CP_Centrifuge')

reset()
box('Preparation_Mat',0,.008,0,1.02,.016,.54,'Blue',.004);rack(-.29,.018,-.05,5)
boxes(.20,.02,-.11,2)
box('Specimen_Tray',-.1,.04,.17,.46,.045,.16,'Steel',.004)
for x in [-.29,.09]:box('Tray_Rim',x,.07,.17,.018,.04,.15,'Steel',.003)
box('Sample_Record_Tablet',.31,.055,.15,.27,.055,.18,'Dark',.01);box('Tablet_Glass',.31,.086,.15,.235,.005,.15,'Screen',.002)
for x in [-.34,-.22,-.10]:box('Sealed_Specimen_Pouch',x,.069,.17,.095,.012,.115,'Paper',.002)
export('CP_PreparationKit')

reset()
box('Console_Recessed_Base',0,.065,-.07,1.48,.13,.70,'Dark',.012)
box('Console_Pedestal',0,.45,-.10,1.53,.73,.68,'Coat',.016)
for x in [-.38,.38]:box('Console_ServiceDoor',x,.44,.25,.71,.60,.028,'Blue',.008);pull(x,.67,.27,.26)
box('Console_Worktop',0,.88,0,1.68,.07,.90,'Steel',.012)
# Continuous sealed trapezoidal display pod.
mesh('Sloped_Instrument_Pod',[(-.79,.92,-.35),(.79,.92,-.35),(.79,.92,.06),(-.79,.92,.06),(-.79,1.49,-.35),(.79,1.49,-.35),(.79,1.40,.06),(-.79,1.40,.06)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Coat',.015)
for x in [-.38,.38]:screen(x,1.18,.079,.64,.35,'ObservationA' if x>0 else 'ObservationB')
label(.48,.78,.27,.24,'Prep')
box('Flush_Control_Deck',0,.926,.25,1.41,.026,.27,'Dark',.006)
for row in range(3):
    for i in range(12):box('Sealed_Key',-.48+i*.067,.946,.17+row*.055,.052,.013,.038,'Coat',.003)
for x in [-.65,.65]:cyl('Encoder',(x,.94,.28),(x,.969,.28),.028,'Steel',16)
box('Status_Light',0,1.46,.071,.31,.015,.012,'Trace',.002)
for x in [-.70,.70]:
    for y in [.20,.65,1.39]:cyl('Captive_Fastener',(x,y,.077 if y>1 else .27),(x,y,.084 if y>1 else .28),.007,'Steel',6)
export('CP_ObservationConsole')

reset()
box('PPE_Plinth',0,.06,0,.84,.12,.39,'Dark',.008)
box('Clean_Supply_Cabinet',0,.55,-.02,.92,.95,.43,'Coat',.012)
for x in [-.22,.22]:box('Supply_Door',x,.55,.205,.42,.88,.025,'Blue',.006);pull(x,.88,.23,.18)
box('PPE_BackPanel',0,1.36,-.17,.92,.76,.07,'Coat',.008)
for x in [-.29,0,.29]:
    box('Glove_Box',x,1.26,.02,.25,.24,.30,'Paper',.006)
    box('Dispensing_Slot',x,1.19,.18,.13,.035,.008,'Dark',.005)
    box('Glove_Edge',x,1.18,.185,.07,.018,.008,'Paper',.003)
box('Mask_Dispenser',-.21,1.61,-.065,.44,.20,.21,'Blue',.008)
box('Mask_Opening',-.21,1.53,.048,.33,.04,.015,'Dark',.004)
for i in range(4):box('Folded_Mask',-.21,1.54+i*.023,.055,.27,.018,.06,'Paper',.004)
box('Sanitizer_Bottle',.30,1.61,-.02,.13,.23,.14,'Paper',.006)
tube('Sanitizer_Pump',[(.30,1.72,-.02),(.30,1.79,-.02),(.30,1.79,.08)],.012,'Steel')
export('CP_PPEStation')

reset()
# True open-front carcass with inward-visible closed surfaces.
w=.80;depth=.48
box('Cabinet_Base',0,.055,0,.77,.11,.46,'Dark',.008)
for x in [-.385,.385]:box('Cabinet_Side',x,.76,0,.03,1.30,depth,'Coat',.006)
box('Opaque_Back',0,.76,-.225,.75,1.30,.03,'Coat',.004)
box('Cabinet_Top',0,1.405,0,.80,.035,depth,'Coat',.006)
for y in [.16,.38,.62,.85,1.08,1.30]:box('Interior_Shelf',0,y,-.006,.75,.025,.425,'Steel',.003)
for y in [.24,.46]:box('Lower_Drawer',0,y,.24,.73,.19,.025,'Coat',.005);pull(0,y+.02,.26,.24)
for y,h in [(.115,.055),(.35,.025),(.59,.065)]:box('Drawer_Frame_Rail',0,y,.238,.75,h,.03,'Coat',.003)
for x in [-.198,.198]:
    # Frame pieces leave a genuine rectangular clear window, with a gasket all round.
    for xx in [x-.178,x+.178]:box('Door_Stile',xx,1.00,.247,.035,.76,.034,'Coat',.004)
    for yy in [.645,1.355]:box('Door_Rail',x,yy,.247,.36,.05,.034,'Coat',.005)
    for xx in [x-.15,x+.15]:box('Window_Gasket',xx,1.0,.267,.012,.64,.014,'Dark',.003)
    for yy in [.685,1.315]:box('Window_Gasket',x,yy,.267,.30,.012,.014,'Dark',.003)
    cyl('Door_Handle',(x+(.12 if x<0 else -.12),.80,.285),(x+(.12 if x<0 else -.12),.97,.285),.010,'Steel',12)
    for y in [.72,1.27]:box('Hinge',x+(-.18 if x<0 else .18),y,.266,.024,.07,.025,'Steel',.003)
for y in [.633,.863,1.093]:
    for x in [-.25,-.10]:bottle(x,y,-.07,.036,.14)
    boxes(.09,y,-.06,1);box('Dressing_Pack',.24,y+.055,.04,.10,.11,.14,'Paper',.005)
export('CP_EmergencyCabinet')
reset()
for x in [-.198,.198]:box('Clear_Glass',x,1.0,.263,.29,.619,.006,'Glass',.002)
export('CP_EmergencyGlass')

reset()
for lo,hi in [(27,82),(126,170),(214,344)]:
    for rad,y in [(8.97,3.10),(9.02,3.25)]:
        pts=[(rad*math.cos(math.radians(a)),y,rad*math.sin(math.radians(a))) for a in range(lo,hi+1,2)]
        if (hi-lo)%2:pts.append((rad*math.cos(math.radians(hi)),y,rad*math.sin(math.radians(hi))))
        tube('Continuous_ServicePipe',pts,.035,'Steel',10)
    for a in range(lo+2,hi,8):
        rad=math.radians(a);x,z=8.99*math.cos(rad),8.99*math.sin(rad)
        tube('Pipe_Mount',[(x,3.06,z),(x,3.34,z),(9.26*math.cos(rad),3.34,9.26*math.sin(rad))],.018,'Dark',8)
for a in [52,150,232,280,328]:
    rad=math.radians(a);x,z=9.02*math.cos(rad),9.02*math.sin(rad)
    tube('Station_UtilityDrop',[(x,3.25,z),(x,2.75,z),(9.13*math.cos(rad),2.58,9.13*math.sin(rad)),(9.13*math.cos(rad),1.05,9.13*math.sin(rad))],.026,'Steel',8)
# Infill wedges close the rear triangular joints of the curved worktop bank.
angles=[40,48,56,64,72,80,128,136,144,152,160,216,224,232,240,248,272,280,288,296,304,312,336,344]
def at(a,x,y,z):
    a=math.radians(a);return ((8.8-z)*math.cos(a)-x*math.sin(a),y,(8.8-z)*math.sin(a)+x*math.cos(a))
for a in angles:
    if a+8 not in angles:continue
    pts=[at(a,.5819,y,z) for y in [.9175,.9505] for z in [.4,-.4]]+[at(a+8,-.5819,y,z) for y in [.9175,.9505] for z in [.4,-.4]]
    mesh('Worktop_Junction',pts,[(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6),(0,4,6,2),(1,3,7,5)],'Steel',.001)
for angle,console in [(136.6,(-5.4,5.1)),(317.8,(5.4,-4.9))]:
    a=math.radians(angle);rx,rz=math.cos(a),math.sin(a);tx,tz=-rz,rx
    for j in [-1,0,1]:
        x,z=console[0]+rx*.36+tx*j*.055,console[1]+rz*.36+tz*j*.055
        tube('Console_ServiceCable',[(x,.35,z),(x+rx*.08,.14,z+rz*.08),(x+rx*.22,.055,z+rz*.22),(rx*8.75+tx*j*.055,.055,rz*8.75+tz*j*.055),(rx*8.75+tx*j*.055,.22,rz*8.75+tz*j*.055)],.014,'Rubber',8)
export('CP_PerimeterServiceRuns')
if '--polish-only' in sys.argv:
    prior=json.loads((H/'assets_manifest.json').read_text('utf-8'));prior.update(reports);reports=prior
(H/'assets_manifest.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
