"""Deterministic T01 manufacture. Author: 송예찬. Geometry in corridor metres."""
import ast,bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[1]
# Reuse established export/axis and bevel helpers without executing the old asset builder.
tree=ast.parse((R/'SourceAssets/CircularDressing/build_environment.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
export_source=ast.unparse(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='export'))
exec(export_source.replace('obj.name = name','obj.name = name\n    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)'))
OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B5';manifest={}
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
    global mats;mats={}
    for n,c,met,rough in [('Coat',(.58,.65,.67,1),.12,.55),('Floor',(.22,.27,.29,1),.02,.71),('Steel',(.35,.42,.46,1),.8,.38),('Dark',(.035,.045,.05,1),.06,.68),('Cable',(.045,.063,.068,1),.05,.48),('Teal',(.10,.28,.29,1),.35,.4),('Lens',(.025,.07,.095,1),.72,.12)]:
        m=bpy.data.materials.new('TC_'+n);m.use_nodes=True;m.diffuse_color=c;nd=m.node_tree.nodes['Principled BSDF'];nd.inputs['Base Color'].default_value=c;nd.inputs['Metallic'].default_value=met;nd.inputs['Roughness'].default_value=rough;mats[n]=m
def curved(name,z0,z1,a0,a1,r=2.083,th=.010,mat='Coat'):
    steps=10;vs=[]
    for z in [z0,z1]:
        for rr in [r,r+th]:
            for i in range(steps+1):
                a=a0+(a1-a0)*i/steps;vs.append((rr*math.cos(a),1.3+rr*math.sin(a),z))
    s=steps+1;fs=[]
    for i in range(steps):fs.extend([(i,i+1,s+i+1,s+i),(2*s+i,3*s+i,3*s+i+1,2*s+i+1),(i,2*s+i,2*s+i+1,i+1),(s+i,s+i+1,3*s+i+1,3*s+i)])
    fs.extend([(0,s,3*s,2*s),(s-1,3*s-1,4*s-1,2*s-1)])
    return mesh(name,vs,fs,mat,.0018,True)
L=13.4617394; bays=[(.62,2.16),(2.44,5.11),(5.39,8.06),(8.34,11.01),(11.29,L-.62)]
reset()
for b,(start,end) in enumerate(bays):
    count=math.ceil((end-start)/1.38)
    for k in range(count):
        z0=start+(end-start)*k/count+.008;z1=start+(end-start)*(k+1)/count-.008;z=(z0+z1)/2
        for a in range(6):curved('Formed_ArchPanel',z0,z1,a*math.pi/6+.003,(a+1)*math.pi/6-.003)
        for side in [-1,1]:
            box('Lower_Lining',side*2.065,.725,z,.034,1.12,z1-z0,'Coat',.005)
            box('Kick',side*2.045,.12,z,.042,.19,z1-z0,'Steel',.004)
            box('Cart_Rail',side*1.986,.94,z,.12,.105,z1-z0-.04,'Steel',.012)
            box('Rail_Rubber',side*1.922,.942,z,.018,.060,z1-z0-.105,'Dark',.008)
            for zz in [z0+.11,z1-.11]:
                for y in [.28,1.18]:cyl('Panel_Screw',(side*2.039,y,zz),(side*2.032,y,zz),.009,'Steel',8)
export('TC_T01_Lining')
reset()
box('Epoxy_Floor',0,.003,.5*L,4.04,.014,L-.6,'Floor',.002)
for side in [-1,1]:
    for i in range(9):
        z=.8+i*(L-1.6)/8
        box('Drain_Backing',side*1.875,.012,z,.085,.008,1.28,'Dark',.001)
        for x in [side*1.875-.052,side*1.875+.052]:box('Drain_Edge',x,.015,z,.016,.014,1.3,'Steel',.002)
        for j in range(14):box('Drain_Bridge',side*1.875,.016,z-.60+j*.092,.087,.011,.033,'Steel',.002)
export('TC_T01_Floor')
reset()
for i in range(4):
    x=.78+i*.105;y=3.115
    cyl('Main_Cable',(x,y,2.12),(x,y,12.08),.027,'Cable',12)
    for z in [2.2,4.18,6.18,8.18,10.18,12.02]:box('Cable_Tie',x,y+.021,z,.066,.017,.021,'Dark',.004)
    # End feed returns into the curved wall with continuous swept transitions.
    for z in [2.12,12.08]:
        pts=[(x,y,z),(x,3.11,z+(.18 if z>7 else -.18)),(1.32,2.85,z+(.40 if z>7 else -.40)),(1.70,2.48,z+(.40 if z>7 else -.40)),(1.86,2.23,z+(.40 if z>7 else -.40))]
        for a,b in zip(pts,pts[1:]):cyl('Wall_Return',a,b,.026,'Cable',12)
for z in [6.46,6.84]:
    points=[(1.09,3.115,z),(1.32,2.85,z),(1.70,2.40,z),(1.93,2.06,z),(1.93,1.82,z)]
    for a,b in zip(points,points[1:]):cyl('Power_Conduit',a,b,.022,'Steel',12)
    for y in [2.05,2.42]:
        x=math.sqrt(2.083**2-(y-1.3)**2)
        cyl('Wall_Anchor',(x-.07,y,z),(x+.005,y,z),.048,'Steel',12)
export('TC_T01_CableHarness')
reset()
# A single sealed door power cabinet; all fittings face into the corridor (-X).
box('PSU_Enclosure',1.933,1.43,6.65,.20,.76,.74,'Steel',.018)
box('PSU_Gasket',1.823,1.43,6.65,.017,.704,.684,'Dark',.008)
box('PSU_Door',1.805,1.43,6.65,.025,.68,.66,'Coat',.011)
for z in [6.39,6.91]:
    for y in [1.15,1.71]:cyl('PSU_Fastener',(1.789,y,z),(1.780,y,z),.014,'Steel',8)
for y in [1.26,1.57]:box('Door_Hinge',1.778,y,6.95,.045,.11,.025,'Steel',.006)
box('Recess_Handle',1.784,1.40,6.43,.015,.15,.055,'Dark',.012)
box('Latch',1.766,1.40,6.43,.028,.10,.025,'Steel',.006)
box('Power_Indicator_Recess',1.784,1.62,6.68,.018,.07,.22,'Dark',.006)
for z in [6.62,6.69,6.76]:cyl('Passive_StatusLens',(1.773,1.62,z),(1.766,1.62,z),.015,'Teal',16)
for z in [6.46,6.84]:cyl('Cable_Gland',(1.93,1.79,z),(1.93,1.86,z),.034,'Dark',12)
for j in range(7):box('Breather_Recess',1.788,1.20,6.51+j*.042,.014,.035,.024,'Dark',.003)
# Two passive louvers with closed black backing (never transparent through wall).
for z in [3.75,9.62]:
    x=-math.sqrt(2.083**2-(1.95-1.3)**2)
    box('Vent_Frame',x+.055,1.95,z,.11,.40,.70,'Steel',.017)
    box('Vent_ClosedPlenum',x+.116,1.95,z,.015,.34,.64,'Dark',.004)
    for j in range(7):box('Vent_Louver',x+.136,1.81+j*.047,z,.045,.023,.59,'Coat',.007)
    for zz in [z-.30,z+.30]:
        for y in [1.80,2.10]:cyl('Vent_Screw',(x+.115,y,zz),(x+.124,y,zz),.011,'Steel',8)
export('TC_T01_ServiceEquipment')
reset()
# Static CCTV exterior. The user will implement motion/AI later.
box('Camera_WallMount',-1.71,2.44,11.87,.10,.24,.22,'Steel',.018)
cyl('Camera_Arm',(-1.67,2.44,11.87),(-1.42,2.44,11.87),.035,'Steel',16)
cyl('Camera_Swivel',(-1.42,2.36,11.87),(-1.42,2.48,11.87),.060,'Dark',20)
box('Camera_WeatherHousing',-1.42,2.34,11.73,.30,.19,.48,'Coat',.035)
box('Camera_FaceGasket',-1.42,2.34,11.483,.245,.135,.018,'Dark',.024)
cyl('Camera_LensBarrel',(-1.42,2.34,11.48),(-1.42,2.34,11.443),.049,'Steel',24)
cyl('Camera_OpticalGlass',(-1.42,2.34,11.442),(-1.42,2.34,11.436),.037,'Lens',24)
box('Camera_Visor',-1.42,2.448,11.69,.328,.025,.59,'Steel',.008)
for x in [-1.51,-1.33]:cyl('Camera_IRLens',(x,2.34,11.474),(x,2.34,11.464),.015,'Lens',16)
export('TC_T01_SecurityCamera')
(H/'model_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
