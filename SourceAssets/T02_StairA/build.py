"""T02 corridor and VA circulation core. Author: 송예찬. Unity metres."""
import ast,bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1]
tree=ast.parse((R/'SourceAssets/CircularDressing/build_environment.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
export_source=ast.unparse(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='export'))
exec(export_source.replace('obj.name = name','obj.name = name\n    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)'))
OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B5';manifest={}
layout=json.loads((R/'Docs/도면/Decision/원형공동/facility_layout.json').read_text(encoding='utf-8'))
floor=layout['floors'][0];tunnel=next(t for t in floor['tunnels'] if t['id']=='B5-T02')
start=Vector((tunnel['p'][0],0,-tunnel['p'][1]));end=Vector((tunnel['q'][0],0,-tunnel['q'][1]));L=(end-start).length
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
    global mats;mats={}
    for n,c,metal,rough in [('Coat',(.58,.65,.67,1),.12,.55),('Floor',(.22,.27,.29,1),.02,.71),('Steel',(.35,.42,.46,1),.8,.38),('Dark',(.035,.045,.05,1),.06,.68),('Cable',(.045,.063,.068,1),.05,.48),('Accent',(.12,.27,.23,1),.25,.4),('Hazard',(.77,.62,.21,1),.05,.6),('Lamp',(.67,.83,.91,1),0,.25)]:
        m=bpy.data.materials.new('TA_'+n);m.use_nodes=True;m.diffuse_color=c;n0=m.node_tree.nodes['Principled BSDF'];n0.inputs['Base Color'].default_value=c;n0.inputs['Metallic'].default_value=metal;n0.inputs['Roughness'].default_value=rough;mats[n]=m
def curved(n,z0,z1,a0,a1,r=2.078,th=.014):
    vs=[];k=10
    for z in [z0,z1]:
        for rr in [r,r+th]:
            for i in range(k+1):
                a=a0+(a1-a0)*i/k;vs.append((rr*math.cos(a),1.3+rr*math.sin(a),z))
    m=k+1;fs=[]
    for i in range(k):fs.extend([(i,i+1,m+i+1,m+i),(2*m+i,3*m+i,3*m+i+1,2*m+i+1),(i,2*m+i,2*m+i+1,i+1),(m+i,m+i+1,3*m+i+1,3*m+i)])
    fs.extend([(0,m,3*m,2*m),(m-1,3*m-1,4*m-1,2*m-1)]);return mesh(n,vs,fs,'Coat',.002,True)
reset()
for i in range(math.ceil((L-1.2)/1.35)):
    n=math.ceil((L-1.2)/1.35);z0=.6+i*(L-1.2)/n+.008;z1=.6+(i+1)*(L-1.2)/n-.008
    for j in range(6):curved('ArchPanel',z0,z1,j*math.pi/6+.003,(j+1)*math.pi/6-.003)
    for side in [-1,1]:
        box('LowerPanel',side*2.062,.72,(z0+z1)/2,.036,1.12,z1-z0,'Coat',.005)
        box('Kick',side*2.035,.12,(z0+z1)/2,.044,.19,z1-z0,'Steel',.004)
        box('CartRail',side*1.98,.94,(z0+z1)/2,.12,.105,z1-z0-.035,'Steel',.012)
        box('RailRubber',side*1.915,.94,(z0+z1)/2,.018,.06,z1-z0-.09,'Dark',.006)
        for z in [z0+.10,z1-.10]:
            for y in [.26,1.16]:cyl('PanelScrew',(side*2.035,y,z),(side*2.025,y,z),.009,'Steel',8)
export('TA_T02_Lining')
reset();box('ResinFloor',0,.003,L*.5,4.04,.014,L-.6,'Floor',.002)
for side in [-1,1]:
    for i in range(math.ceil((L-1.3)/1.4)):
        z=.83+i*1.35
        if z+.64>L-.3:continue
        box('DrainBack',side*1.87,.012,z,.10,.008,1.27,'Dark',.001)
        for x in [side*1.87-.056,side*1.87+.056]:box('DrainLip',x,.015,z,.012,.014,1.30,'Steel',.002)
        for k in range(14):box('DrainSlat',side*1.87,.017,z-.6+k*.092,.10,.012,.031,'Steel',.002)
export('TA_T02_Floor')
reset()
for i in range(4):
    x=.70+i*.11;cyl('SignalCable',(x,3.10,1.35),(x,3.10,L-1.35),.026,'Cable',12)
for z in [1.45,L*.33,L*.66,L-1.45]:
    box('CableTray',.87,3.04,z,.55,.035,.10,'Steel',.005)
    for x in [.70,.81,.92,1.03]:box('CableTie',x,3.123,z,.065,.015,.025,'Dark',.003)
    for x in [.60,1.15]:cyl('TrayAnchor',(x,3.04,z),(x,1.3+math.sqrt(2.09**2-x*x),z),.012,'Steel',12)
for z in [1.35,L-1.35]:
    for x in [.70,.81,.92,1.03]:
        pts=[(x,3.10,z),(1.32,2.86,z),(1.72,2.45,z),(1.91,2.13,z)]
        for a,b in zip(pts,pts[1:]):cyl('CableReturn',a,b,.026,'Cable',12)
# One pressurization/door controller, with fittings attached to a backed enclosure.
z=L*.48
box('ControllerBack',1.94,1.54,z,.20,.82,.64,'Steel',.018);box('ControllerGasket',1.827,1.54,z,.02,.76,.58,'Dark',.007);box('ControllerDoor',1.808,1.54,z,.027,.73,.55,'Coat',.01)
for zz in [z-.22,z+.22]:
    for y in [1.24,1.84]:cyl('LidScrew',(1.789,y,zz),(1.780,y,zz),.012,'Steel',8)
box('HandleRecess',1.789,1.46,z-.17,.015,.15,.05,'Dark',.007);box('Latch',1.769,1.46,z-.17,.033,.10,.024,'Steel',.005)
for zz in [z-.07,z+.07]:cyl('Indicator',(1.788,1.76,zz),(1.776,1.76,zz),.020,'Accent',16)
for zz in [z-.18,z+.18]:
    cyl('Gland',(1.94,1.93,zz),(1.94,2.00,zz),.035,'Dark',16)
    pts=[(1.94,2.,zz),(1.72,2.45,zz),(1.32,2.86,zz),(.87,3.10,zz)]
    for a,b in zip(pts,pts[1:]):cyl('Conduit',a,b,.022,'Steel',12)
for z in [L*.24,L*.78]:
    x=-math.sqrt(2.08**2-.65**2)
    box('VentFrame',x+.055,1.95,z,.11,.42,.72,'Steel',.015);box('ClosedPlenum',x+.116,1.95,z,.018,.35,.65,'Dark',.004)
    for i in range(7):box('VentLouver',x+.139,1.81+i*.047,z,.045,.022,.60,'Coat',.006)
export('TA_T02_Services')

# An actual 16m stair shaft replaces only the VA shell, preserving the B5 footprint.
reset()
def cylinder_object(n,r,y0,y1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=r,depth=y1-y0,location=xyz(0,(y0+y1)/2,0));o=bpy.context.object;o.name=n;return o
shell=cylinder_object('VA_Shaft_Concrete',5.22,-.08,19.4);shell.data.materials.append(mats['Coat'])
inner=cylinder_object('cut',4.98,-.5,19.10)
def difference(obj,cut):
    bpy.context.view_layer.objects.active=obj;m=obj.modifiers.new('ArchitecturalOpening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
difference(shell,inner)
# Tunnel profile prisms in original world coordinates, then translate to this local core.
for t in floor['tunnels']:
    if 'VA' not in (t['a'],t['b']):continue
    other=next(r for r in floor['rooms'] if r['id']==(t['b'] if t['a']=='VA' else t['a']))
    f=Vector((other['x']+44,0,-other['v']-28)).normalized();right=Vector((f.z,0,-f.x));vs=[];prof=[(-t['w']/2,-.3),(t['w']/2,-.3)]
    prof += [(t['w']/2*math.cos(a),t['h']-t['w']/2+t['w']/2*math.sin(a)) for a in [i*math.pi/32 for i in range(33)]]
    for dist in [0,7]:
        for x,y in prof:vs.append(tuple(f*dist+right*x+Vector((0,y,0))))
    n=len(prof);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    cut=mesh('PortalCut',vs,fs,'Dark',0);difference(shell,cut)
be=shell.modifiers.new('OpeningBevel','BEVEL');be.width=.01;be.segments=3
export('TA_VA_Shaft')
reset()
# 8 flights x 12 steps = 16m. Paired flights share landings, giving 4m repeated headroom.
for flight in range(8):
    side=-1 if flight%2==0 else 1;x=side*.96;direction=1 if flight%2==0 else -1;z0=-1.68*direction;y0=flight*2
    for i in range(12):
        y=y0+(i+1)/6;z=z0+direction*(i+.5)*.28
        box('Tread',x,y-.052,z,1.50,.104,.28,'Steel',.004)
        box('ClosedRiser',x,y-.11,z-direction*.126,1.50,.13,.028,'Coat',.003)
        box('AntiSlipInset',x,y+.002,z-direction*.055,1.40,.005,.14,'Dark',.001)
        box('NoseStripe',x,y+.004,z-direction*.117,1.42,.007,.024,'Hazard',.001)
        for xx in [x-.66,x+.66]:cyl('TreadBolt',(xx,y+.004,z+.05),(xx,y+.009,z+.05),.009,'Steel',8)
    for xx in [x-.69,x+.69]:
        a=(xx,y0-.10,z0);b=(xx,y0+1.90,-z0);cyl('Stringer',a,b,.065,'Steel',12)
    topz=-z0+direction*.70;y=y0+2
    box('LandingDeck',0,y-.075,topz,3.44,.15,1.40,'Steel',.007)
    box('LandingGrip',0,y+.003,topz,3.31,.006,1.27,'Floor',.002)
export('TA_VA_Stairs')
reset()
for flight in range(8):
    side=-1 if flight%2==0 else 1;x=side*.96;direction=1 if flight%2==0 else -1;z0=-1.68*direction;y0=flight*2
    for xx in [x-.78,x+.78]:
        for i in [0,3,6,9,12]:
            z=z0+direction*i*.28;y=y0+i/6
            box('PostFoot',xx,y+.018,z,.13,.036,.13,'Steel',.005);cyl('RailingPost',(xx,y+.035,z),(xx,y+1.06,z),.024,'Steel',12)
            for dx in [-.04,.04]:cyl('AnchorBolt',(xx+dx,y+.035,z),(xx+dx,y+.048,z),.008,'Steel',8)
        cyl('TopHandrail',(xx,y0+1.06,z0-.12*direction),(xx,y0+3.06,-z0+.12*direction),.032,'Steel',20)
        cyl('GuardMidrail',(xx,y0+.55,z0),(xx,y0+2.55,-z0),.017,'Steel',12)
    y=y0+2;back=-z0+direction*1.38
    for xx in [-1.74,0,1.74]:cyl('LandingPost',(xx,y,back),(xx,y+1.08,back),.024,'Steel',12)
    for h,r in [(1.08,.032),(.54,.017)]:cyl('LandingBackRail',(-1.74,y+h,back),(1.74,y+h,back),r,'Steel',16)
    for xx in [-1.74,1.74]:
        for h,r in [(1.08,.032),(.54,.017)]:cyl('LandingSideRail',(xx,y+h,-z0),(xx,y+h,back),r,'Steel',16)
export('TA_VA_Railings')
reset()
# Vertical service spine and structural bands. The floor-level portal arcs remain clear.
for xx in [-1.76,1.76]:
    for zz in [-3.08,3.08]:
        box('StructuralColumn',xx,8,zz,.12,16,.12,'Steel',.006)
        box('ColumnBase',xx,.04,zz,.28,.08,.28,'Steel',.008)
        for dx in [-.09,.09]:
            for dz in [-.09,.09]:cyl('FoundationAnchor',(xx+dx,.08,zz+dz),(xx+dx,.10,zz+dz),.012,'Steel',8)
        for yy in range(2,17,2):box('LandingBracket',xx,yy-.12,zz,.24,.22,.22,'Steel',.006)
for x,z in [(-3.6,-2.8),(-3.6,2.8),(3.6,2.8)]:
    cyl('RiserPipe',(x,.18,z),(x,18.6,z),.065,'Steel',20)
    for y in [.5,2.9,6.9,10.9,14.9,18.2]:
        out=Vector((x,0,z)).normalized();p=Vector((x,y,z));cyl('WallSupport',p,Vector((out.x*4.99,y,out.z*4.99)),.036,'Steel',12)
        for off in [-.10,.10]:cyl('PipeCoupling',(x,y+off-.025,z),(x,y+off+.025,z),.083,'Steel',16)
for y in [3.65,7.65,11.65,15.65,18.6]:
    for j in range(96):
        a=j*2*math.pi/96;b=(j+1)*2*math.pi/96;cyl('ShaftRing',(4.93*math.cos(a),y,4.93*math.sin(a)),(4.93*math.cos(b),y,4.93*math.sin(b)),.035,'Steel',8)
# Wall lining strips form regular architectural joints, never freestanding blocks.
for j in range(48):
    a=j*2*math.pi/48
    cyl('VerticalJoint',(4.971*math.cos(a),3.55,4.971*math.sin(a)),(4.971*math.cos(a),18.7,4.971*math.sin(a)),.007,'Dark',6)
export('TA_VA_Services')
reset()
# Ground-level emergency equipment: closed-backed cabinet and communication recess.
x,z=-2.9,-3.72
box('CabinetBack',x,1.15,z,.82,1.40,.22,'Steel',.025);box('DoorSeal',x,1.15,z+.12,.76,1.33,.024,'Dark',.012);box('FireDoor',x,1.15,z+.143,.73,1.30,.028,'Coat',.014)
box('CabinetHandle',x+.26,1.15,z+.18,.045,.25,.04,'Steel',.008)
for yy in [.63,1.65]:box('CabinetHinge',x-.37,yy,z+.16,.06,.14,.04,'Steel',.007)
box('FirePanelBand',x,1.60,z+.165,.54,.13,.006,'Hazard',.002)
for xx in [x-.32,x+.32]:
    for yy in [.55,1.74]:cyl('WallStandoff',(xx,yy,z-.12),(xx,yy,z-.30),.035,'Steel',12)
center=Vector(xyz(x,0,z));rot=Matrix.Translation(center)@Matrix.Rotation(-math.atan2(-x,-z),4,'Z')@Matrix.Translation(-center)
for obj in list(bpy.context.scene.objects):obj.matrix_world=rot@obj.matrix_world
cabinet=set(bpy.context.scene.objects)
box('Intercom',2.75,1.50,-3.84,.28,.55,.12,'Steel',.016);box('IntercomInset',2.75,1.51,-3.772,.23,.48,.012,'Dark',.008)
for i in range(6):box('SpeakerSlot',2.75,1.60+i*.021,-3.762,.16,.008,.01,'Coat',.002)
cyl('CallButton',(2.75,1.33,-3.77),(2.75,1.33,-3.75),.038,'Accent',24)
box('IntercomMount',2.75,1.50,-3.98,.15,.43,.22,'Steel',.008)
center=Vector(xyz(2.75,0,-3.84));rot=Matrix.Translation(center)@Matrix.Rotation(-math.atan2(-2.75,3.84),4,'Z')@Matrix.Translation(-center)
for obj in set(bpy.context.scene.objects)-cabinet:obj.matrix_world=rot@obj.matrix_world
export('TA_VA_SafetyEquipment')
reset()
# Eight sealed luminaires on upper shaft walls; dedicated lights are placed at their diffuser.
fixtures=[]
for y in [5.2,9.2,13.2,17.2]:
    for side in [-1,1]:
        x=side*3.95;z=0
        box('LampBack',x,y,z,.14,.24,1.1,'Steel',.018);box('LampDiffuser',x-side*.08,y,z,.03,.17,.98,'Lamp',.012)
        cyl('LampBracket',(x,y,z),(side*4.99,y,z),.04,'Steel',16)
        fixtures.append(dict(position=[x-side*.13,y,z],direction=[-side,-.4,0]))
# Match the four existing B5 point-light positions without moving them.
for x,z in [(2.6,0),(0,-4.5),(-2.6,0),(0,4.5)]:
    box('LowerLampHousing',x,3.31,z,.82,.13,.24,'Steel',.012);box('LowerDiffuser',x,3.232,z,.72,.025,.17,'Lamp',.008)
    cyl('Suspension',(x,3.38,z),(x,3.65,z),.02,'Steel',12)
    out=Vector((x,0,z)).normalized();cyl('FixtureWallArm',(x,3.65,z),(out.x*4.99,3.65,out.z*4.99),.035,'Steel',12)
export('TA_VA_Lighting')
reset()
# B4 level 16m landing terminates at a closed access door; no false connection to an absent floor.
box('UpperBulkheadLeft',-.79,17.35,-3.06,1.90,2.70,.14,'Coat',.008)
box('UpperBulkheadRight',1.79,17.35,-3.06,.14,2.70,.14,'Coat',.008)
box('UpperBulkheadHeader',.96,18.70,-3.06,1.52,.20,.14,'Coat',.008)
box('UpperVestibuleFloor',0,15.92,-3.74,3.48,.16,1.32,'Steel',.008)
for xx in [-1.78,1.78]:box('UpperVestibuleSide',xx,17.4,-3.75,.12,2.8,1.46,'Coat',.01)
box('UpperDoorBack',.96,17.28,-3.02,1.48,2.56,.12,'Dark',.008)
for xx in [.19,1.73]:box('UpperDoorJamb',xx,17.3,-2.94,.12,2.6,.18,'Steel',.01)
box('UpperDoorHeader',.96,18.58,-2.94,1.66,.12,.18,'Steel',.012);box('UpperDoorLeaf',.96,17.27,-2.94,1.36,2.45,.09,'Coat',.018)
box('PushBar',.96,17.06,-2.866,1.12,.055,.07,'Steel',.009)
for xx in [.44,1.48]:box('BarSupport',xx,17.06,-2.90,.07,.11,.08,'Steel',.008)
export('TA_VA_UpperDoor')
reset();cylinder_object('CoreResinFloor',4.94,-.006,.010).data.materials.append(mats['Floor']);export('TA_VA_Floor')
(H/'model_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(H/'geometry.json').write_text(json.dumps(dict(corridor=dict(origin=list(start),direction=list((end-start).normalized()),length=L),core=dict(position=[-44,-82,28],height=16,flights=8,steps=96,width=1.5,rise=1/6,tread=.28),fixtures=fixtures),indent=2),encoding='utf-8')
print('COMPLETE T02 VA',L,flush=True)
