"""B5/B4 laboratory art polish V0.01 · 송예찬.
External Blender asset authoring. Keep originals, bevel sources, explicit triangles,
separate sliding leaves, physical keypad, and portable PBR. No game behaviour.
"""
import bpy,math,json,sys,numpy as np,bmesh
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
SRC=Path(__file__).resolve().parent;REPO=SRC.parents[1]
MODELS=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model'
DEST=MODELS/'Props/Common';TEX=MODELS/'Environment/Common/Textures'
DEST.mkdir(parents=True,exist_ok=True);TEX.mkdir(parents=True,exist_ok=True)
reports=[]

def textures():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 n=512;y,x=np.mgrid[:n,:n];rng=np.random.default_rng(1106)
 grain=rng.normal(0,1,(n,n)).astype(np.float32)
 for family in ('Coating','Stainless','Concrete'):
  if family=='Stainless':
   h=.0025*np.sin(y*math.tau/4)+.0012*grain;shade=.74+.014*np.sin(y*math.tau/4)+.004*grain;metal=.94;smooth=.48+.035*np.sin(y*math.tau/11)
  elif family=='Concrete':
   h=.007*grain+.002*np.sin(x*math.tau/64)*np.sin(y*math.tau/64);shade=.78+.013*grain+.004*np.cos(x*math.tau/128);metal=0;smooth=.18+.01*grain
  else:
   h=.001*grain;shade=.82+.003*grain;metal=0;smooth=.30+.01*grain
  dx=np.roll(h,-1,axis=1)-np.roll(h,1,axis=1);dy=np.roll(h,-1,axis=0)-np.roll(h,1,axis=0)
  for kind in ('Base','Normal','MetallicSmoothness'):
   a=np.ones((n,n,4),dtype=np.float32)
   if kind=='Base':a[:,:,:3]=shade[:,:,None]
   elif kind=='Normal':a[:,:,0]=.5-dx;a[:,:,1]=.5-dy;a[:,:,2]=1
   else:a[:,:,:3]=metal;a[:,:,3]=smooth
   name=f'LP_{family}_{kind}';im=bpy.data.images.new(name,width=n,height=n,alpha=True)
   im.colorspace_settings.name='sRGB' if kind=='Base' else 'Non-Color';im.pixels.foreach_set(np.clip(a,0,1).ravel());im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save()

palette={'Coating':(.52,.58,.57,1),'Stainless':(.57,.60,.62,1),'Graphite':(.055,.07,.075,1),'Teal':(.05,.25,.24,1),'Rubber':(.014,.018,.019,1),'Screen':(.06,.23,.21,1),'Indicator':(.16,.65,.49,1),'Amber':(.72,.33,.055,1),'Legend':(.68,.73,.70,1),'Glass':(.10,.30,.33,1)}
def reset():
 global mats,groups
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';mats={};groups=defaultdict(list)
 for key,color in palette.items():
  m=bpy.data.materials.new('LP_'+key);m.diffuse_color=color;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Metallic'].default_value=.94 if key=='Stainless' else 0;bs.inputs['Roughness'].default_value=.50 if key=='Stainless' else .65
  if key in ('Screen','Indicator','Amber'):bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=.4
  mats[key]=m
def world(x,y,z):return (-x,-z,y)
def box(name,x,y,z,w,h,d,mat='Coating',bevel=.004,group='Body'):
 vs=[(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]
 fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mats[mat]);me.update();uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis];p.use_smooth=True
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.location=world(x,y,z)
 if bevel:
  m=ob.modifiers.new('Manufactured_edge_bevel','BEVEL');m.width=min(bevel,min(w,h,d)*.22);m.segments=2 if bevel>.003 else 1;m.limit_method='ANGLE';m.harden_normals=True
  no=ob.modifiers.new('Weighted_normals','WEIGHTED_NORMAL');no.keep_sharp=True
 ob['bevel_width_m']=min(bevel,min(w,h,d)*.22);groups[group].append(ob);return ob
def cyl(name,x,y,z,r,depth,mat='Stainless',group='Body',axis='Y',vertices=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=world(x,y,z));o=bpy.context.object;o.name=name
 if axis=='Z':o.rotation_euler[0]=math.pi/2
 if axis=='X':o.rotation_euler[1]=math.pi/2
 o.data.materials.append(mats[mat]);m=o.modifiers.new('Edge_bevel','BEVEL');m.width=min(.002,depth*.15);m.segments=1;m.harden_normals=True;no=o.modifiers.new('Weighted_normals','WEIGHTED_NORMAL');no.keep_sharp=True
 for p in o.data.polygons:p.use_smooth=True
 o['bevel_width_m']=m.width;groups[group].append(o);return o
def glyph(digit,x,y,z,size,group):
 # Printed seven-segment markings, flat faces rather than expensive text meshes.
 segments={0:'abcedf',1:'bc',2:'abged',3:'abgcd',4:'fgbc',5:'afgcd',6:'afgecd',7:'abc',8:'abcdefg',9:'abfgcd'}[digit]
 defs={'a':(0,.5,.50,.08),'g':(0,0,.5,.08),'d':(0,-.5,.5,.08),'b':(.25,.25,.08,.44),'c':(.25,-.25,.08,.44),'f':(-.25,.25,.08,.44),'e':(-.25,-.25,.08,.44)}
 for s in segments:
  dx,dy,w,h=defs[s];box('Printed_digit',x-dx*size,y+dy*size,z,w*size,h*size,.0003,'Legend',0,group)
def save_export(name,pivots=None):
 src=SRC/(name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(src));deps=bpy.context.evaluated_depsgraph_get();exports=[]
 col=bpy.data.collections.new('Export_triangles');bpy.context.scene.collection.children.link(col)
 for key,obs in groups.items():
  baked=[]
  for ob in obs:
   me=bpy.data.meshes.new_from_object(ob.evaluated_get(deps),depsgraph=deps);n=bpy.data.objects.new('ExportPart',me);n.matrix_world=ob.matrix_world.copy();col.objects.link(n);baked.append(n)
  bpy.ops.object.select_all(action='DESELECT')
  for o in baked:o.select_set(True)
  bpy.context.view_layer.objects.active=baked[0];bpy.ops.object.join();o=bpy.context.object;o.name=key
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  bpy.context.scene.cursor.location=world(*(pivots or {}).get(key,(0,0,0)));bpy.ops.object.origin_set(type='ORIGIN_CURSOR');exports.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in exports:o.select_set(True)
 bpy.context.view_layer.objects.active=exports[0]
 path=DEST/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,add_leaf_bones=False,bake_anim=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_custom_props=True,path_mode='AUTO')
 reports.append(dict(asset=name,triangles=sum(len(o.data.polygons) for o in exports),parts=[o.name for o in exports],source=str(src.relative_to(REPO)),fbx=str(path.relative_to(REPO))))

def door():
 reset()
 for side in (-1,1):
  box('Jamb',side*.79,1.4,0,.08,2.8,.34,'Graphite',.008,'Fixed_Frame')
  for z in (-.175,.175):box('Pocket_cover',side*1.17,1.38,z,.68,2.76,.026,'Coating',.003,'Fixed_Frame')
 box('Track_motor_cover',0,2.91,0,2.96,.22,.39,'Graphite',.012,'Fixed_Frame')
 for z in (-.201,.201):
  box('Header_face',0,2.91,z,2.84,.14,.018,'Coating',.003,'Fixed_Frame');box('Status_lens',0,2.91,z*1.05,.15,.025,.012,'Indicator',.002,'Fixed_Frame')
 for side,group in ((-1,'Leaf_L'),(1,'Leaf_R')):
  x=side*.376
  box('Leaf_shell',x,1.37,0,.746,2.72,.085,'Coating',.008,group)
  box('Meeting_seal',side*.006,1.37,0,.010,2.70,.094,'Rubber',.001,group)
  for z in (-.047,.047):
   box('Kick_plate',x,.25,z,.69,.42,.010,'Stainless',.002,group)
   box('Inset_upper',x,1.93,z,.53,.53,.008,'Graphite',.003,group)
   box('Window_inset',x,1.93,z*1.11,.47,.47,.007,'Glass',.003,group)
   box('Leaf_accent',x,1.17,z,.67,.025,.008,'Teal',.001,group)
   box('Emergency_pull',x+side*.20,1.4,z*1.26,.035,.20,.02,'Stainless',.004,group)
 save_export('LP_DoubleSlidingDoor',{'Leaf_L':(-.376,0,0),'Leaf_R':(.376,0,0)})
def keypad():
 reset();g='Keypad'
 box('Mount_gasket',0,0,-.012,.155,.285,.025,'Rubber',.008,g);box('Keypad_housing',0,0,.012,.15,.28,.050,'Graphite',.010,g)
 box('Front_plate',0,0,.041,.136,.265,.009,'Stainless',.004,g);box('Readout',0,.080,.048,.109,.056,.009,'Screen',.003,g)
 box('Status_bar',0,.116,.049,.086,.007,.007,'Indicator',.001,g)
 for row in range(4):
  for col in range(3):
   x=(1-col)*.038;y=.018-row*.038;box('Key',x,y,.050,.031,.029,.010,'Graphite',.002,g)
   if row<3:glyph(row*3+col+1,x,y,.0553,.016,g)
   elif col==1:glyph(0,x,y,.0553,.016,g)
   else:box('Control_mark',x,y,.0553,.011,.003,.0003,'Amber' if col==0 else 'Indicator',0,g)
 for x in (-.056,.056):
  for y in (-.119,.119):cyl('Fixing_screw',x,y,.050,.0035,.003,'Graphite',g,'Z',8)
 save_export('LP_Keypad')
def trolley():
 reset()
 for y in (.22,.83):
  box('Tray',0,y,0,.80,.035,.50,'Stainless',.006)
  for x in (-.39,.39):box('Tray_lip',x,y+.04,0,.018,.07,.49,'Stainless',.003)
  for z in (-.24,.24):box('Tray_lip',0,y+.04,z,.77,.07,.018,'Stainless',.003)
 for x in (-.34,.34):
  for z in (-.20,.20):
   cyl('Leg',x,.53,z,.018,.68);box('Caster_fork',x,.12,z,.07,.10,.06,'Graphite',.004);cyl('Rubber_wheel',x,.065,z,.06,.04,'Rubber',axis='X');cyl('Wheel_hub',x,.065,z,.021,.045,'Stainless',axis='X')
 for z in (-.20,.20):cyl('Handle_upright',.43,.89,z,.014,.24)
 cyl('Handle_grip',.43,1.0,0,.016,.4,'Rubber',axis='Z')
 box('Sealed_case',-.12,.96,0,.40,.20,.29,'Teal',.018);box('Case_lid',-.12,1.064,0,.41,.025,.30,'Graphite',.006)
 for x in (-.22,-.02):box('Case_clasp',x,1.02,.155,.045,.055,.018,'Stainless',.003)
 for i in range(3):cyl('Sample_canister',.20,.96,(i-1)*.13,.040,.18,'Coating');cyl('Canister_cap',.20,1.06,(i-1)*.13,.045,.025,'Teal')
 box('Lower_tray_bin',0,.38,0,.56,.26,.37,'Coating',.012)
 save_export('LP_SampleTrolley')
def cabinet():
 reset()
 box('Sealed_fridge_body',0,.96,0,.72,1.86,.68,'Coating',.018)
 box('Base',0,.07,0,.66,.12,.62,'Graphite',.006)
 box('Door_gasket',0,1.04,.348,.66,1.57,.025,'Rubber',.006)
 box('Insulated_door',0,1.04,.374,.64,1.55,.047,'Coating',.012)
 box('Inset_panel',0,1.11,.401,.48,1.17,.014,'Teal',.005)
 box('Vertical_handle',-.245,1.15,.442,.028,.52,.052,'Stainless',.008)
 box('Controller',0,1.81,.36,.28,.15,.028,'Graphite',.006);box('Controller_display',-.04,1.81,.38,.14,.075,.012,'Screen',.002)
 for i in range(3):cyl('Control_key',.075+i*.026,1.81,.38,.008,.012,'Legend',axis='Z',vertices=12)
 for i in range(9):box('Compressor_vent',-.25+i*.062,.20,.35,.027,.14,.018,'Graphite',.002)
 for y in (.46,1.62):box('Door_hinge',.34,y,.36,.040,.10,.07,'Stainless',.004)
 save_export('LP_SampleColdCabinet')
def analyzer():
 reset()
 box('Pedestal',0,.46,0,1.0,.89,.64,'Coating',.016);box('Top_work_surface',0,.92,0,1.06,.045,.70,'Stainless',.006)
 for x in (-.24,.24):
  box('Cabinet_inset',x,.5,.326,.43,.65,.018,'Teal',.006);box('Recessed_pull',x,.69,.343,.17,.025,.025,'Graphite',.004)
 box('Analyzer_body',-.10,1.17,0,.69,.46,.47,'Coating',.020);box('Top_lid',-.10,1.405,0,.66,.026,.44,'Graphite',.008)
 box('Instrument_front',-.10,1.18,.245,.62,.30,.025,'Graphite',.006);box('Readout',-.19,1.21,.263,.28,.14,.014,'Screen',.004)
 cyl('Encoder',.12,1.16,.28,.028,.024,'Stainless',axis='Z')
 for i in range(5):box('Vent',-.36+i*.055,1.05,-.245,.025,.11,.015,'Graphite',.001)
 for x in (-.43,.43):
  for z in (-.24,.24):cyl('Adjustable_foot',x,.025,z,.035,.05,'Graphite')
 save_export('LP_BenchAnalyzer')

def worklight():
 reset()
 box('Instrument_mount_post',0,-.45,-.22,.025,.90,.025,'Stainless',.003)
 box('Instrument_mount_foot',0,-.89,-.20,.10,.025,.10,'Graphite',.003)
 box('Wall_bracket',0,.06,-.18,.18,.18,.04,'Graphite',.006)
 for x in (-.07,.07):box('Stand_off',x,0,-.10,.025,.025,.17,'Stainless',.004)
 box('Shielded_lamp_body',0,0,0,.70,.075,.18,'Graphite',.008)
 box('Diffuser',0,-.040,0,.61,.012,.12,'Legend',.002)
 for x in (-.28,-.14,0,.14,.28):box('Glare_louver',x,-.054,0,.012,.025,.14,'Graphite',.002)
 save_export('LP_WorkLight')

def architecture(floor):
 # Load authored bevel sources, remove only former doorway visuals, export a derived model.
 source=REPO/('SourceAssets/B5_StealthLayout/B5_StealthLayout_ArtRepair.blend' if floor=='B5' else 'SourceAssets/B4_StealthLayout/B4_Stealth_Architecture.blend')
 bpy.ops.wm.open_mainfile(filepath=str(source));removed=[]
 for ob in list(bpy.context.scene.objects):
  if ob.name.startswith(('DoorFrame','DoorJamb','DoorLintel','DoorStatus','LockedDoor')):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 original=[o for o in bpy.context.scene.objects if o.type=='MESH'];deps=bpy.context.evaluated_depsgraph_get();batches=defaultdict(list)
 # Evaluate once before linking export objects to avoid repeatedly rebuilding the whole depsgraph.
 evaluated={ob.name:bpy.data.meshes.new_from_object(ob.evaluated_get(deps),depsgraph=deps) for ob in original}
 for ob in original:
  mat=ob.data.materials[0].name;u=24-ob.location.x;v=16-ob.location.y;sector=f'{int(max(0,min(47.9,u))//8)}_{int(max(0,min(31.9,v))//8)}';batches[(mat,sector)].append(ob)
 bpy.ops.wm.save_as_mainfile(filepath=str(SRC/(f'LP_{floor}_Architecture.blend')))
 col=bpy.data.collections.new('LabPolish_Export');bpy.context.scene.collection.children.link(col);exports=[]
 for (mat,sector),obs in batches.items():
  baked=[]
  for ob in obs:
   me=evaluated[ob.name];n=bpy.data.objects.new('Export',me);n.matrix_world=ob.matrix_world.copy();col.objects.link(n);baked.append(n)
  bpy.ops.object.select_all(action='DESELECT')
  for ob in baked:ob.select_set(True)
  bpy.context.view_layer.objects.active=baked[0];bpy.ops.object.join();o=bpy.context.object;o.name=f'LP_{floor}_{mat}_{sector}';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();exports.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in exports:ob.select_set(True)
 bpy.context.view_layer.objects.active=exports[0];path=MODELS/'Environment'/floor/(f'LP_{floor}_Architecture.fbx')
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_custom_props=True,path_mode='AUTO')
 reports.append(dict(asset=f'LP_{floor}_Architecture',removedDoorVisualParts=len(removed),preservedSourceMeshes=len(original),exportMeshes=len(exports),triangles=sum(len(o.data.polygons) for o in exports),source=str(source.relative_to(REPO))))

if '--keypad-only' in sys.argv:
 old=json.loads((SRC/'asset_manifest.json').read_text(encoding='utf-8'))['assets'];reports.extend(r for r in old if r['asset']!='LP_Keypad');keypad()
elif '--worklight-only' in sys.argv:
 old=json.loads((SRC/'asset_manifest.json').read_text(encoding='utf-8'))['assets'];reports.extend(r for r in old if r['asset']!='LP_WorkLight');worklight()
else:
 textures();door();keypad();trolley();cabinet();analyzer();worklight();architecture('B5');architecture('B4')
(SRC/'asset_manifest.json').write_text(json.dumps(dict(title='B5 B4 Lab Polish asset manifest V0.01',author='송예찬',assets=reports),ensure_ascii=False,indent=2),encoding='utf-8');print('LAB_ASSETS_DONE',json.dumps(reports,ensure_ascii=False))
