import bpy, math, os
from math import pi,cos,sin
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,c,metal,rough):
    a=bpy.data.materials.new(name);a.diffuse_color=(*c,1);a.use_nodes=True
    node=a.node_tree.nodes['Principled BSDF'];node.inputs['Base Color'].default_value=(*c,1);node.inputs['Metallic'].default_value=metal;node.inputs['Roughness'].default_value=rough
    return a
colors=[mat('DarkMoulding',(.05,.064,.068),.05,.56),mat('Graphite',(.112,.124,.13),.32,.4),mat('FacilityAmber',(.84,.40,.075),.08,.47)]
rings=[(-.227,.010,0),(-.223,.018,0),(-.214,.022,0),(-.207,.021,0),(-.202,.019,0)]
for i in range(9):
    t=-.199+i*.012;rings.extend([(t,.018,0),(t+.003,.0194,0),(t+.007,.0194,0),(t+.01,.018,0)])
rings.extend([(-.084,.019,0),(-.079,.022,1),(-.076,.024,1),(-.070,.024,2),(-.065,.024,1),(-.060,.0205,1),(-.053,.0178,0),(.188,.0154,0),(.208,.0156,1),(.218,.0145,1),(.226,.010,0),(.229,.004,0)])
n=20;vertices=[];faces=[];slots=[]
for z,rad,idx in rings:
    for j in range(n):
        ang=2*pi*j/n;vertices.append((cos(ang)*rad,sin(ang)*rad,z))
for i in range(len(rings)-1):
    for j in range(n):
        k=(j+1)%n;faces.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j));slots.append(rings[i][2])
faces.append(tuple(reversed(range(n))));slots.append(0); faces.append(tuple((len(rings)-1)*n+j for j in range(n)));slots.append(0)
mesh=bpy.data.meshes.new('SecurityBaton');mesh.from_pydata(vertices,[],faces);mesh.update()
obj=bpy.data.objects.new('SecurityBaton',mesh);bpy.context.collection.objects.link(obj)
for m in colors:mesh.materials.append(m)
for poly,s in zip(mesh.polygons,slots):poly.material_index=s;poly.use_smooth=len(poly.vertices)==4
bpy.context.view_layer.objects.active=obj;obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(os.path.dirname(__file__),'Pickup_SecurityBaton.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE')

