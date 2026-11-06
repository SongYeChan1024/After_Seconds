"""C01 manufactured geometry and normal-preserving export. 작성자: 송예찬."""
import math,json
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent

def finish(e,name):
    box,cyl,tube,mesh=e['box'],e['cyl'],e['tube'],e['mesh']
    import runpy
    display=runpy.run_path(str(H.parent/'C01_InstrumentDetail/display_geometry.py'))
    for key,col in [('PF_Glass',(.63,.82,.85,.14)),('PF_Liquid',(.13,.42,.48,1))]:display['mat'](e,key,col)
    def remove(prefix):
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)
    def find(prefix):return next(o for o in bpy.context.scene.objects if o.name.startswith(prefix))
    def coord(o):
        v=o.matrix_world@(sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices))
        return (-v.x,v.z,-v.y)
    def decal(key,x,y,z,w,h=None):
        key='PF_Decal_'+key;display['mat'](e,key,(.8,.85,.8,1))
        return display['make_quad'](e,key,x,y,z,w,h or w/3,key)
    def horizontal_decal(key,x,y,z,w,h):
        ob=decal(key,x,y,z,w,h);pivot=Vector(e['xyz'](x,y,z));ob.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(math.pi/2,4,'X')@Matrix.Translation(-pivot)@ob.matrix_world;return ob
    def lathe(n,x,y,z,profile,mat='Steel',segments=32):
        vs=[(x+r*math.cos(i*math.tau/segments),y+dy,z+r*math.sin(i*math.tau/segments)) for dy,r in profile for i in range(segments)]
        fs=[]
        for j in range(len(profile)-1):
            for i in range(segments):k=j*segments+i;ii=j*segments+(i+1)%segments;fs.append((k,ii,ii+segments,k+segments))
        fs.extend([tuple(range(segments-1,-1,-1)),tuple((len(profile)-1)*segments+i for i in range(segments))])
        ob=mesh(n,vs,fs,mat,0,True);ob['rounded_surface']=True;return ob
    def cup(n,x,y,z,r,h,mat='Steel',segments=24):
        t=min(.004,r*.18)
        return lathe(n,x,y,z,[(0,r*.92),(.002,r),(h-.002,r),(h,r-t/2),(h-.002,r-t),(.004,r-t)],mat,segments)
    def ring(n,x,y,z,r,t,mat='Steel'):
        return tube(n,[(x+r*math.cos(i*math.tau/48),y,z+r*math.sin(i*math.tau/48)) for i in range(49)],t,mat,10)
    def cut(obj,cutter):
        bpy.context.view_layer.objects.active=obj
        m=obj.modifiers.new('Machined_Recess','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
        bpy.ops.object.modifier_move_up(modifier=m.name)
        bpy.ops.object.modifier_move_up(modifier=m.name)
        bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)
    def knob(x,y,z,r=.025):
        cyl('Knurled_Encoder',(x,y,z),(x,y,z+.022),r,'Dark',32)
        for i in range(16):
            a=i*math.tau/16;cyl('Knurl',(x+(r-.001)*math.cos(a),y+(r-.001)*math.sin(a),z+.003),(x+(r-.001)*math.cos(a),y+(r-.001)*math.sin(a),z+.020),.0015,'Steel',6)
        box('Encoder_Index',x,y+r*.65,z+.023,.002,r*.42,.0015,'Paper',0)
    if name in {'CP_Centrifuge','ID_BinocularMicroscope','ID_ThermalCycler','ID_UltrasonicBath','ID_BenchAutoclave'}:
        remove('Recessed_Nameplate');remove('Manufactured_Label')
    # Shared bottle/contact repairs run below after all functional parts exist.
    if name=='CP_Centrifuge':
        remove('Sealed_Rotor_Cover');remove('HandleMount');remove('PullGrip')
        cutter=cyl('CUT',(0,.19,-.025),(0,.55,-.025),.211,'Dark',64);cutter.modifiers.clear();cut(find('Centrifuge_Housing'),cutter)
        cup('Rotor_Chamber',0,.205,-.025,.211,.217,'Steel',48)
        cyl('Rotor_Disc',(0,.24,-.025),(0,.29,-.025),.178,'Dark',48)
        for i in range(8):
            a=i*math.tau/8;x,z=.135*math.cos(a),-.025+.135*math.sin(a);cup('Rotor_TubeSocket',x,.286,z,.024,.047,'Blue');lathe('Rotor_SampleTube',x,.293,z,[(0,.013),(.04,.016),(.052,.016)],'Paper',16)
        cyl('Rotor_Lock',(0,.29,-.025),(0,.355,-.025),.035,'Steel',32)
        ring('Lid_Seal',0,.433,-.025,.216,.010,'Rubber');ring('Lid_Frame',0,.445,-.025,.226,.012,'Blue')
        cyl('Clear_Rotor_Lid',(0,.445,-.025),(0,.451,-.025),.211,'PF_Glass',64)
        box('Safety_Latch',0,.433,.223,.10,.04,.035,'Coat',.008)
        decal('Centrifuge',0,.09,.292,.21)
    elif name=='ID_ThermalCycler':
        remove('Heated_Lid');remove('PullGrip');remove('HandleMount');remove('Thermal_Block')
        box('Thermal_Block_Insulator',0,.28,-.06,.56,.12,.42,'Blue',.018)
        box('Aluminum_Block_Deck',0,.344,-.06,.50,.018,.36,'Steel',.006)
        for i in range(12):
            for j in range(8):cup('PCR_Reaction_Well',-.213+i*.0387,.35,-.203+j*.041,.015,.023,'Steel',12)
        lid=box('Hinged_Heated_Lid',0,.60,-.21,.57,.045,.43,'Coat',.018)
        gasket=box('Lid_Insulation_Gasket',0,.577,-.21,.51,.016,.37,'Rubber',.006)
        plate=box('Lid_Heater_Plate',0,.566,-.21,.46,.014,.32,'Steel',.005)
        # Rotate assembled lid around its own center; front rises, rear remains near hinge.
        pivot=Vector(e['xyz'](0,.60,-.21));rot=Matrix.Rotation(math.radians(-62),4,'X')
        for ob in [lid,gasket,plate]:ob.matrix_world=Matrix.Translation(pivot)@rot@Matrix.Translation(-pivot)@ob.matrix_world
        for x in [-.24,.24]:tube('Lid_Hinge_Link',[(x,.42,-.27),(x,.46,-.37),(x,.53,-.36)],.012,'Steel',12)
        decal('PCR',-.17,.26,.159,.20)
    elif name=='ID_UltrasonicBath':
        remove('Bath_Recess');remove('Basket_Wire');remove('HandleMount');remove('PullGrip')
        cutter=box('CUT',0,.35,0,.55,.30,.33,'Dark',0);cut(find('Instrument_Shell'),cutter)
        box('Bath_Deep_Bottom',0,.218,0,.55,.018,.33,'Steel',.006)
        for x in [-.273,.273]:box('Bath_Inner_Wall',x,.285,0,.012,.13,.34,'Steel',.005)
        for z in [-.162,.162]:box('Bath_Inner_Wall',0,.285,z,.55,.13,.012,'Steel',.005)
        for j in range(9):cyl('Basket_Base_Wire',(-.245,.25,-.14+j*.035),(.245,.25,-.14+j*.035),.003,'Steel',8)
        for x in [-.22,.22]:tube('Basket_Lifting_Handle',[(x,.25,-.12),(x,.40,-.12),(x,.40,.12),(x,.25,.12)],.005,'Steel',8)
        for x in [-.11,.06]:tube('Immersed_Forceps',[(x,.26,-.11),(x+.035,.27,.03),(x,.26,.12)],.008,'Steel',10)
        decal('Wash',-.20,.22,.263,.20)
    elif name=='ID_BinocularMicroscope':
        remove('Curved_Optical_Stand')
        profile=[(.10,-.20),(.10,-.06),(.25,-.08),(.43,-.12),(.51,-.08),(.55,-.03),(.61,-.08),(.61,-.19),(.54,-.27),(.36,-.28),(.17,-.24)]
        vs=[(x,y,z) for x in [-.064,.064] for y,z in profile];k=len(profile)
        mesh('Cast_Curved_Arm',vs,[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)],'Coat',.012)
        cyl('Revolving_Nosepiece',(0,.475,-.025),(0,.49,-.025),.083,'Dark',36)
        remove('Optical_Head')
        box('Binocular_Head_Housing',0,.555,-.06,.17,.115,.18,'Coat',.026)
        cyl('Optical_Head_Bearing',(0,.49,-.025),(0,.51,-.025),.049,'Steel',32)
        for x in [-.135,.135]:cyl('Fine_Focus',(x,.42,-.17),(x*1.17,.42,-.17),.024,'Steel',32)
        box('Stage_Travel_Rail',0,.28,.06,.31,.018,.018,'Steel',.003)
        decal('Microscope',0,.085,.255,.23)
    elif name=='ID_MicroplateHandler':
        old=[o for o in bpy.context.scene.objects if o.name.startswith('Microplate_Well')]
        for o in old:
            x,y,z=coord(o);bpy.data.objects.remove(o,do_unlink=True);cup('Open_Microplate_Well',x,.273,z,.012,.013,'Paper',12)
        for x in [-.31,.05]:cyl('Plate_Guide_Rail',(x,.225,-.21),(x,.225,.22),.008,'Steel',16)
        box('Vertical_Drive_Rail',.28,.48,-.064,.04,.45,.012,'Steel',.004)
        for y in [.32,.43,.54,.65]:box('Drive_Belt_Tooth',.28,y,-.054,.038,.007,.008,'Dark',.002)
    elif name=='ID_PipetteWorkstation':
        remove('Pipette_Tip')
        for x in [.17,.27,.37]:
            lathe('Tapered_Pipette_Tip',x,.105,-.06,[(0,.0015),(.07,.006),(.085,.009)],'Paper',16)
            box('Pipette_Finger_Rest',x,.405,-.07,.055,.018,.025,'Blue',.006)
            decal('Pipette',x,.33,-.040,.030,.075)
    elif name=='ID_DualMagneticStirrer':
        remove('Reagent_Flask');remove('Flask_Neck')
        for x in [-.19,.19]:
            lathe('Erlenmeyer_Glass',x,.214,0,[(0,.07),(.008,.082),(.025,.083),(.15,.032),(.21,.029),(.215,.032),(.219,.029),(.21,.025),(.15,.028),(.023,.078),(.008,.074)],'PF_Glass',40)
            lathe('Reagent_Liquid',x,.226,0,[(0,.071),(.014,.073),(.082,.049)],'PF_Liquid',40)
            ring('Flask_Lip',x,.432,0,.029,.003,'PF_Glass')
        knob(-.26,.12,.24,.019);knob(.26,.12,.24,.019)
    elif name=='ID_GlasswareDryingRack':
        remove('Inverted_Flask')
        for x in [-.32,0,.32]:
            for z in [-.14,.05]:lathe('Inverted_Drying_Flask',x,.10,z-.04,[(0,.024),(.065,.024),(.16,.063),(.175,.063),(.18,.056),(.175,.050),(.163,.059),(.068,.020),(.001,.020)],'PF_Glass',32)
        for z in [-.18,-.09,0,.09,.18]:box('Drain_Channel',0,.052,z,.83,.003,.006,'Dark',0)
    elif name=='ID_BenchAutoclave':
        remove('Door_Latch');knob(-.15,.32,.35,.045)
        for a in [0,math.tau/3,2*math.tau/3]:tube('Door_Locking_Spoke',[(-.15,.32,.38),(-.15+.10*math.cos(a),.32+.10*math.sin(a),.39)],.012,'Steel',12)
        cyl('Pressure_Gauge_Case',(.27,.14,.31),(.27,.14,.33),.052,'Steel',40)
        display['mat'](e,'PF_Decal_Gauge',(.8,.85,.8,1));r=.0455
        gauge=mesh('Circular_Gauge_Face',[(.27,.14,.334)]+[(.27+r*math.cos(i*math.tau/48),.14+r*math.sin(i*math.tau/48),.334) for i in range(48)],[(0,1+i,1+(i+1)%48) for i in range(48)],'PF_Decal_Gauge',0)
        uv=gauge.data.uv_layers.new(name='UVMap')
        for p in gauge.data.polygons:
            for li in p.loop_indices:
                v=gauge.data.vertices[gauge.data.loops[li].vertex_index].co;uv.data[li].uv=((v.x+.27)/(2*r)+.5,(v.z-.14)/(2*r)+.5)
        gauge['display_uv']=True;tube('Gauge_Needle',[(.27,.14,.336),(.247,.162,.336)],.0018,'Dark',8)
        decal('Sterilizer',-.12,.067,.315,.25)
    elif name=='ID_PrecisionBalance':
        for z in [-.18,.145]:box('Sliding_Glass_Track',0,.158,z,.49,.014,.017,'Dark',.003)
        cyl('Level_Vial_Recess',(.21,.17,.18),(.21,.178,.18),.026,'Dark',32)
        cyl('Level_Liquid',(.21,.179,.18),(.21,.183,.18),.022,'PF_Liquid',32)
        ring('Level_Target',.21,.185,.18,.010,.0015,'Paper')
        for x in [-.22,.22]:ring('Adjustable_Foot_Collar',x,.031,.185,.025,.004,'Steel')
    elif name=='ID_SlideScanner':
        for x in [-.32,-.03]:cyl('Precision_Travel_Rail',(x,.29,-.24),(x,.29,.22),.009,'Steel',20)
        box('Scanner_Linear_Carriage',-.12,.535,-.08,.16,.045,.15,'Blue',.007)
        cyl('Objective_Focus_Collar',(-.12,.43,-.08),(-.12,.465,-.08),.055,'Steel',32)
        for x in [-.30,-.22,-.14,-.06]:box('Slide_End_Clamp',x,.338,.145,.052,.008,.012,'Blue',.002)
    elif name=='ID_DualVortexMixer':
        remove('Vortex_Rubber_Cup')
        for x in [-.13,.13]:cup('Molded_Vortex_Cup',x,.22,0,.072,.044,'Rubber',32);ring('Cup_Isolation_Bellows',x,.218,0,.058,.007,'Dark')
    elif name=='ID_TubeRotator':
        for x in [-.27,.27]:cyl('Rotator_Bearing',(x-.014,.39,0),(x+.014,.39,0),.046,'Steel',32)
        for i in range(7):
            x=-.22+i*.073;cyl('Sample_Screw_Cap',(x,.435,.179),(x,.445,.205),.021,'Blue',20)
        box('Drive_Gearbox',.27,.24,-.08,.12,.16,.14,'Blue',.018)
    elif name=='ID_SterileSealer':
        box('Heated_Sealing_Strip',0,.221,-.025,.66,.018,.032,'Steel',.003)
        for i in range(3):
            x=-.20+i*.20
            for dx in [-.072,.072]:box('Pouch_Weld_Seam',x+dx,.180,.10,.004,.002,.21,'Blue',0)
            ob=decal('Sealer',x,.185,.10,.13,.07);pivot=Vector(e['xyz'](x,.185,.10));ob.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(math.pi/2,4,'X')@Matrix.Translation(-pivot)@ob.matrix_world
    elif name=='ID_LabelPrinter':
        remove('Hand_Scanner')
        cyl('Scanner_Handgrip',(.38,.12,.02),(.38,.25,.055),.026,'Blue',32)
        box('Scanner_Head',.38,.278,.095,.085,.065,.17,'Blue',.022)
        ob=decal('Barcode',0,.185,.26,.16,.10);pivot=Vector(e['xyz'](0,.185,.26));ob.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(math.pi/2,4,'X')@Matrix.Translation(-pivot)@ob.matrix_world
        box('Scanner_Optical_Window',.38,.29,.171,.055,.023,.009,'Dark',.004)
        box('Scan_Laser_Aperture',.38,.29,.177,.039,.006,.002,'Trace',.001)
        for x in [-.17,.17]:box('Output_Paper_Guide',x,.218,.24,.018,.018,.065,'Blue',.004)
    elif name=='ID_FlowCytometer':
        for x in [-.30,-.16]:
            cyl('Fluidic_Bulkhead',(x,.56,-.12),(x,.60,-.12),.019,'Steel',20)
        box('Loader_Travel_Rail',-.28,.16,.30,.29,.018,.25,'Steel',.004)
        knob(-.29,.43,.28,.025);decal('Vial',-.22,.10,.278,.20)
    elif name=='CP_OpticalAnalyzer':
        ring('Lens_Focus_Ring',-.23,.545,-.02,.047,.006,'Steel')
        for x in [.18,.27,.36]:decal('Vial',x,.39,.2452,.044,.06)
    elif name=='CP_PreparationKit':
        remove('Tablet_Glass');display['mat'](e,'ID_LCD_Printer')
        ob=display['make_quad'](e,'Sample_Record_Display',.31,.086,.15,.235,.15,'ID_LCD_Printer');pivot=Vector(e['xyz'](.31,.086,.15));ob.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(math.pi/2,4,'X')@Matrix.Translation(-pivot)@ob.matrix_world
        for x in [-.34,-.22,-.10]:horizontal_decal('Sealer',x,.076,.17,.08,.08)
    elif name=='CP_PPEStation':
        remove('Sanitizer_Bottle');lathe('Sanitizer_Molded_Bottle',.30,1.495,-.02,[(0,.05),(.007,.065),(.15,.065),(.19,.038),(.22,.027)],'Paper',32)
        decal('Wash',.30,1.60,.047,.089,.067)
        for x in [-.29,0,.29]:
            decal('Glove',x,1.29,.172,.21)
            for j in range(4):tube('Dispensed_Glove_Finger',[(x-.025+j*.016,1.18,.188),(x-.028+j*.017,1.13,.198)],.006,'Paper',8)
        decal('Mask',-.21,1.64,.043,.32)
        for z in [.065,.078,.091]:box('Mask_Pleat',-.21,1.625,z,.25,.004,.006,'Coat',.001)
        for x in [-.36,-.06]:tube('Mask_Earloop',[(x,1.55,.07),(x+(-.03 if x<-.2 else .03),1.55,.10),(x,1.57,.11)],.002,'Paper',8)
    elif name=='CP_WashBench':
        for i in range(8):
            a=i*math.tau/8;cyl('Drain_Strainer',(-.12+.021*math.cos(a),.791,.02+.021*math.sin(a)),(-.12+.021*math.cos(a),.793,.02+.021*math.sin(a)),.003,'Steel',8)
        decal('Wash',-.30,.78,.386,.18)
    elif name=='CP_ServicePanel':
        for x in [-.38,.38]:
            cyl('Gas_Quick_Coupler',(x,.70,.11),(x,.70,.14),.016,'Steel',20)
            cyl('Gas_Port_Recess',(x,.70,.14),(x,.70,.142),.009,'Dark',16)
    elif name=='ID_MixedSupplyShelf':
        for ob in list(bpy.context.scene.objects):
            if ob.name.startswith('Component_Bin'):
                x,y,z=coord(ob);cutter=box('CUT',x,y+.05,z,.187,.17,.214,'Dark',0);cut(ob,cutter)
                for j in range(3):box('Stored_Supply_Pack',x-.055+j*.055,y+.02,z-.02,.043,.075,.12,'Paper',.004)
    # Visible joints/hinges and exposed panel fasteners establish assembly scale.
    doors=[o for o in list(bpy.context.scene.objects) if any(o.name.startswith(p) for p in ['Upper_Door','LiftUp_Door','Insulated_Door','Cryo_Drawer','Supply_Door','Lower_SealedDoor']) and 'Gasket' not in o.name]
    for ob in doors:
        x,y,z=coord(ob);coords=[ob.matrix_world@v.co for v in ob.data.vertices];w=max(v.x for v in coords)-min(v.x for v in coords);h=max(v.z for v in coords)-min(v.z for v in coords)
        for yy in [y-h*.31,y+h*.31]:cyl('Recessed_Hinge_Pin',(x-w*.46,yy-.018,z+.022),(x-w*.46,yy+.018,z+.022),.007,'Steel',16)
    runpy.run_path(str(H.parent/'C01_PropRepair/refine_components.py'))['apply'](e,name)
    polish_normals(name)
    report={'asset':name,'parts':len([o for o in bpy.context.scene.objects if o.type=='MESH']),'bevelSegments':3,'flatDecalsPreserved':True,'detailPass':'manufacturing + functional geometry'}
    (H/(name+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')

def polish_normals(name):
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH' or ob.get('display_uv') or ob.name=='CP_VitalMonitor_Source':continue
        # Preserve flat caps, smoothly shade cylindrical walls and rounded bevels.
        for poly in ob.data.polygons:poly.use_smooth=not ob.get('knurl_surface',False)
        bm=bmesh.new();bm.from_mesh(ob.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        for edge in bm.edges:edge.smooth=not(edge.is_manifold and edge.calc_face_angle()>math.radians(48))
        bm.to_mesh(ob.data);bm.free()
        for mod in ob.modifiers:
            if mod.type=='BEVEL':
                mod.segments=3;mod.harden_normals=True;mod.use_clamp_overlap=True
                if 'Screw' not in ob.name and 'Key' not in ob.name:mod.width*=1.20
        if not ob.get('rounded_surface') and not any(m.type=='WEIGHTED_NORMAL' for m in ob.modifiers):
            wn=ob.modifiers.new('Manufactured_Weighted_Normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40

def export(e,name,props=False,collide=True):
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for o in objs:
        if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
        if o.get('display_uv'):continue
        for p in o.data.polygons:
            axes=[i for i in range(3) if i!=max(range(3),key=lambda j:abs(p.normal[j]))]
            for li in p.loop_indices:
                v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(v[axes[0]]*.7,v[axes[1]]*.7)
    bpy.ops.wm.save_as_mainfile(filepath=str(e['H']/(name+'.blend')))
    dg=bpy.context.evaluated_depsgraph_get();out=[]
    for o in objs:
        # Evaluated normals survive export: do not round-trip the finished mesh through BMesh.
        tri=o.modifiers.new('Export_Triangulation','TRIANGULATE');tri.quad_method='FIXED';tri.ngon_method='BEAUTY'
        if hasattr(tri,'keep_custom_normals'):tri.keep_custom_normals=True
        dg.update();me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg)
        # Remove sub-pixel zero-area Boolean slivers while retaining UVs and split normals.
        good=[p for p in me.polygons if p.area>=5e-9]
        if len(good)!=len(me.polygons):
            clean=bpy.data.meshes.new(me.name+'_Clean');clean.from_pydata([v.co for v in me.vertices],[],[tuple(p.vertices) for p in good]);clean.update()
            for mat in me.materials:clean.materials.append(mat)
            for dst,src in zip(clean.polygons,good):dst.material_index=src.material_index;dst.use_smooth=src.use_smooth
            for layer in me.uv_layers:
                uv=clean.uv_layers.new(name=layer.name);values=[layer.data[li].uv[:] for p in good for li in p.loop_indices]
                for dst,src in zip(uv.data,values):dst.uv=src
            clean.normals_split_custom_set([me.corner_normals[li].vector[:] for p in good for li in p.loop_indices]);me=clean
        n=bpy.data.objects.new(o.name,me);bpy.context.collection.objects.link(n);n.matrix_world=o.matrix_world.copy();out.append(n)
    bpy.ops.object.select_all(action='DESELECT')
    for o in out:o.select_set(True)
    bpy.context.view_layer.objects.active=out[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    folder=e['A']/('Props/B5' if props else 'Environment/B5')
    bpy.ops.export_scene.fbx(filepath=str(folder/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='OFF',use_custom_props=True)
    e['manifest'][name]=dict(parts=len(objs),beveled_parts=sum(any(m.type=='BEVEL' for m in ob.modifiers) for ob in objs),triangles=len(o.data.polygons),props=props,collide=collide,normalPreservingExport=True)
    print('FINISHED',name,len(o.data.polygons),flush=True)
