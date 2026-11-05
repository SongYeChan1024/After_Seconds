import bpy
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from mathutils import Vector

REPOSITORY = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).parent
MODEL = REPOSITORY / 'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B4'
PLAN_FILE = REPOSITORY / 'Docs/도면/잠입_탐색/layout.json'
floor_plan = next(floor for floor in json.loads(PLAN_FILE.read_text(encoding='utf-8-sig'))['floors'] if floor['floor'] == 'B4')
MODEL.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
editable = bpy.data.collections.new('B4_Editable_BevelSources')
scene.collection.children.link(editable)
palette = {
    'Panel': (0.72, 0.79, 0.79, 1), 'Clinical': (0.88, 0.90, 0.87, 1),
    'Service': (0.32, 0.40, 0.43, 1), 'Core': (0.14, 0.18, 0.20, 1),
    'Floor': (0.25, 0.33, 0.36, 1), 'Ceiling': (0.65, 0.72, 0.72, 1),
    'Metal': (0.10, 0.14, 0.17, 1), 'Accent': (0.04, 0.47, 0.48, 1),
    'Light': (0.62, 0.91, 1, 1), 'Hazard': (0.85, 0.53, 0.08, 1),
    'Glass': (0.45, 0.74, 0.80, 0.13)
}
materials = {}
for name, color in palette.items():
    material = bpy.data.materials.new('B4_' + name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Metallic'].default_value = 0.65 if name == 'Metal' else 0.12
    shader.inputs['Roughness'].default_value = 0.35 if name in ('Metal', 'Glass') else 0.58
    if name == 'Light':
        shader.inputs['Emission Color'].default_value = color
        shader.inputs['Emission Strength'].default_value = 2
    materials[name] = material

mesh_cache = {}
groups = defaultdict(list)
colliders = []
lights = []
windows = []
source_count = 0

def world(u, height, v):
    return (24 - u, 16 - v, height)

def make_box_mesh(size, material):
    key = tuple(round(value, 5) for value in size) + (material,)
    if key in mesh_cache:
        return mesh_cache[key]
    x, y, z = (value / 2 for value in size)
    vertices = [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh = bpy.data.meshes.new('B4_Box')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(materials[material])
    uv = mesh.uv_layers.new(name='UVMap')
    for polygon in mesh.polygons:
        normal_axis = max(range(3), key=lambda axis: abs(polygon.normal[axis]))
        axes = [axis for axis in range(3) if axis != normal_axis]
        for loop_index in polygon.loop_indices:
            coordinate = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv.data[loop_index].uv = (coordinate[axes[0]] * 0.5, coordinate[axes[1]] * 0.5)
        polygon.use_smooth = True
    mesh_cache[key] = mesh
    return mesh

def finish(obj, material, width, category, u, v):
    global source_count
    bevel = obj.modifiers.new('Manufactured_Bevel', 'BEVEL')
    bevel.width = width
    bevel.segments = 2 if category in ('Rail', 'Window') else 1
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)
    bevel.use_clamp_overlap = True
    bevel.harden_normals = True
    normals = obj.modifiers.new('Weighted_Face_Normals', 'WEIGHTED_NORMAL')
    normals.keep_sharp = True
    obj['bevel_width_m'] = width
    obj['source'] = 'B4 Stealth V0.01'
    sector = f'{int(max(0,min(47.9,u))//8)}_{int(max(0,min(31.9,v))//8)}'
    groups[(category, material, sector)].append(obj)
    source_count += 1
    return obj

def box(name, u, height, v, width, rise, depth, material='Panel', bevel=0.008, collision=False, category='Architecture'):
    obj = bpy.data.objects.new(name, make_box_mesh((width, depth, rise), material))
    editable.objects.link(obj)
    obj.location = world(u, height, v)
    finish(obj, material, min(bevel, min(width, rise, depth)*0.22), category, u, v)
    if collision:
        colliders.append({'name': name, 'center': [u-24, height, v-16], 'size': [width, rise, depth]})
    return obj

def railing(name, points, radius=0.035):
    positions = [Vector(world(*point)) for point in points]
    vertices = []
    faces = []
    sides = 12
    for index, position in enumerate(positions):
        tangent = (positions[min(index+1,len(positions)-1)] - positions[max(index-1,0)]).normalized()
        up = Vector((0,0,1)) if abs(tangent.z) < 0.95 else Vector((0,1,0))
        normal = tangent.cross(up).normalized()
        binormal = tangent.cross(normal).normalized()
        vertices.extend(position + radius*(normal*math.cos(2*math.pi*side/sides) + binormal*math.sin(2*math.pi*side/sides)) for side in range(sides))
    for index in range(len(positions)-1):
        for side in range(sides):
            faces.append((index*sides+side,index*sides+(side+1)%sides,(index+1)*sides+(side+1)%sides,(index+1)*sides+side))
    faces.extend((tuple(reversed(range(sides))), tuple((len(positions)-1)*sides+side for side in range(sides))))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(materials['Metal'])
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    editable.objects.link(obj)
    finish(obj, 'Metal', 0.003, 'Rail', points[0][0], points[0][2])

def edge_rail(name, start, end, elevation, barrier=True):
    railing(name, [(start[0], elevation+1.05, start[1]), (end[0], elevation+1.05, end[1])])
    railing(name+'_Mid', [(start[0], elevation+0.5, start[1]), (end[0], elevation+0.5, end[1])], 0.022)
    length = math.dist(start, end)
    count = max(1, math.ceil(length/1.2))
    for index in range(count+1):
        fraction = index/count
        u = start[0] + fraction*(end[0]-start[0])
        v = start[1] + fraction*(end[1]-start[1])
        box(name+'_Post', u, elevation+0.52, v, 0.045, 1.04, 0.045, 'Metal', 0.006, category='Rail')
        box(name+'_Foot', u, elevation+0.025, v, 0.12, 0.05, 0.12, 'Metal', 0.006, category='Rail')
    if barrier:
        colliders.append({'name':name+'_Barrier','center':[(start[0]+end[0])/2-24,elevation+0.55,(start[1]+end[1])/2-16], 'size':[max(abs(end[0]-start[0]),0.07),1.1,max(abs(end[1]-start[1]),0.07)]})

room_heights = {room['id']: (5.6 if room['id']=='D' else 8.9 if room['id']=='STB' else 4.0) for room in floor_plan['rooms']}
for room in floor_plan['rooms']:
    u, v, width, depth = (room[key] for key in ('x','y','w','h'))
    box('Floor_'+room['id'],u+width/2,-0.12,v+depth/2,width,0.24,depth,'Floor',0.004,True,'Floor')
    for column in range(math.ceil(width/2)):
        for row in range(math.ceil(depth/2)):
            tile_width = min(2,width-column*2)
            tile_depth = min(2,depth-row*2)
            box('FloorFinish_'+room['id'],u+column*2+tile_width/2,-0.002,v+row*2+tile_depth/2,tile_width-0.012,0.012,tile_depth-0.012,'Floor',0.002,category='Floor')
            box('Ceiling_'+room['id'],u+column*2+tile_width/2,room_heights[room['id']]+0.08,v+row*2+tile_depth/2,tile_width-0.012,0.16,tile_depth-0.012,'Ceiling',0.005,category='Ceiling')
    if room['id'] == 'STB':
        continue
    columns, rows = max(1,math.ceil(width/5)), max(1,math.ceil(depth/5))
    for column in range(columns):
        for row in range(rows):
            light_u, light_v = u+(column+0.5)*width/columns, v+(row+0.5)*depth/rows
            height = room_heights[room['id']]-0.15
            body_width, body_depth = (0.32,1.4) if width<depth else (1.4,0.32)
            box('LightBody_'+room['id'],light_u,height,light_v,body_width,0.1,body_depth,'Metal',category='Fixture')
            box('LightLens_'+room['id'],light_u,height-0.06,light_v,body_width-0.1,0.022,body_depth-0.1,'Light',0.003,category='Fixture')
            lights.append({'room':room['id'],'position':[light_u-24,height-0.30,light_v-16],'range':8.0 if height<5 else 10,'intensity':3.0 if height<5 else 4.0})

edges = defaultdict(list)
for room in floor_plan['rooms']:
    u,v,width,depth = (room[key] for key in ('x','y','w','h'))
    for axis,constant,start,end in [('H',v,u,u+width),('H',v+depth,u,u+width),('V',u,v,v+depth),('V',u+width,v,v+depth)]:
        edges[(axis,constant)].append((start,end,room['id']))
window_ranges = [(5.4,7.5),(10.5,12.7),(15.4,17.5),(20.5,22.7)]
for (axis,constant), owners in edges.items():
    doors = [door for door in floor_plan['doors'] if door['axis']==axis and abs((door['y'] if axis=='H' else door['x'])-constant)<0.001]
    cuts = {point for start,end,_ in owners for point in (start,end)}
    for door in doors:
        center = door['x'] if axis=='H' else door['y']
        cuts.update((center-door['width']/2,center+door['width']/2))
    opening_ranges = window_ranges if axis=='V' and constant==12 else []
    for start,end in opening_ranges:
        cuts.update((start,end))
    for start,end in zip(sorted(cuts),sorted(cuts)[1:]):
        midpoint = (start+end)/2
        rooms = [name for low,high,name in owners if low<midpoint<high]
        if not rooms or end-start<0.01:
            continue
        height = max(room_heights[room] for room in rooms)
        is_door = any(abs(midpoint-(door['x'] if axis=='H' else door['y']))<door['width']/2-0.001 for door in doors)
        is_window = any(low<midpoint<high for low,high in opening_ranges)
        sections = [(2.8,height)] if is_door else [(0,1.0),(2.9,height)] if is_window else [(0,height)]
        for bottom,top in sections:
            u,v = (midpoint,constant) if axis=='H' else (constant,midpoint)
            width,depth = (end-start,0.22) if axis=='H' else (0.22,end-start)
            box('WallCore_'+axis+'_'+str(constant),u,(bottom+top)/2,v,width,top-bottom,depth,'Core',0.004,True)
            panel_material = 'Clinical' if any(room in ('A','AN','AS','B','D') for room in rooms) else 'Service' if any(room in ('HVAC','SUP4','STA','STB','LIFT') for room in rooms) else 'Panel'
            panels = max(1,math.ceil((end-start)/1.5))
            rows = max(1,math.ceil((top-bottom)/2))
            for side in (-1,1):
                for column in range(panels):
                    along = start+(column+0.5)*(end-start)/panels
                    for row in range(rows):
                        pu,pv = (along,constant+side*0.119) if axis=='H' else (constant+side*0.119,along)
                        pw,pd = ((end-start)/panels-0.012,0.018) if axis=='H' else (0.018,(end-start)/panels-0.012)
                        box('WallPanel',pu,bottom+(row+0.5)*(top-bottom)/rows,pv,pw,(top-bottom)/rows-0.012,pd,panel_material,0.003)
                for stripe_height,stripe_size,material in [(0.13,0.14,'Metal'),(1.2,0.04,'Accent')]:
                    if not bottom<stripe_height<top:
                        continue
                    pu,pv = (midpoint,constant+side*0.132) if axis=='H' else (constant+side*0.132,midpoint)
                    pw,pd = (end-start-0.012,0.012) if axis=='H' else (0.012,end-start-0.012)
                    box('WallTrim',pu,stripe_height,pv,pw,stripe_size,pd,material,0.002)
        if is_window:
            box('ObservationGlass',12,1.95,midpoint,0.035,1.9,end-start,'Glass',0.003,True,'Window')
            for height in (1.0,2.9):
                box('WindowRail',12,height,midpoint,0.32,0.09,end-start+0.08,'Metal',0.012,category='Window')
            for along in (start,midpoint,end):
                box('WindowMullion',12,1.95,along,0.30,1.95,0.055,'Metal',0.008,category='Window')
            windows.append({'axis':'V','u':12,'vStart':start,'vEnd':end,'sill':1.0,'head':2.9})

for index,door in enumerate(floor_plan['doors']):
    u,v,width = door['x'],door['y'],door['width']
    horizontal = door['axis']=='H'
    for side in (-1,1):
        pu,pv = (u+side*(width/2+0.04),v) if horizontal else (u,v+side*(width/2+0.04))
        box('DoorJamb_'+str(index),pu,1.42,pv,0.08 if horizontal else 0.34,2.84,0.34 if horizontal else 0.08,'Metal',0.012)
    box('DoorLintel_'+str(index),u,2.86,v,width+0.16 if horizontal else 0.34,0.12,0.34 if horizontal else width+0.16,'Metal',0.012)
    box('DoorStatus_'+str(index),u,2.85,v,width-0.12 if horizontal else 0.36,0.025,0.36 if horizontal else width-0.12,'Light' if door['state']=='open' else 'Hazard',0.003)
    if door['state']!='open':
        box('LockedDoor_'+str(index),u,1.35,v,width-0.02 if horizontal else 0.09,2.7,0.09 if horizontal else width-0.02,'Service',0.015,True)

for index,block in enumerate(floor_plan['blocks']):
    if block['kind']=='baffle':
        box('CorridorBaffle_'+str(index),block['x']+block['w']/2,1.75,block['y']+block['h']/2,block['w'],3.5,block['h'],'Panel',0.018,True)
    if block['kind']=='cover':
        box('ConsoleBase' if index==1 else 'EquipmentRack',block['x']+block['w']/2,0.55 if index==1 else 1.15,block['y']+block['h']/2,block['w'],1.1 if index==1 else 2.3,block['h'],'Service',0.025,True)

box('DeckMain',31.55,1.25,17.5,4.9,2.5,5,'Service',0.018,True,'Deck')
box('DeckLanding',28.05,1.25,19.46,2.1,2.5,1.08,'Service',0.018,True,'Deck')
box('DeckFinish',31.55,2.5,17.5,4.86,0.02,4.96,'Floor',0.006,category='Deck')
for index in range(14):
    height = (index+1)*2.5/14
    v = 15+(index+0.5)*0.28
    box('DeckStair_'+str(index+1),28.2,height/2,v,1.6,height,0.292,'Floor',0.012,True,'Deck')
    box('DeckNosing',28.2,height+0.007,v-0.105,1.56,0.014,0.035,'Accent',0.003,category='Deck')
for u in (27.34,29.06):
    railing('DeckStairRail',[(u,1.05,15),(u,3.55,18.92)])
    for index in range(0,14,3):
        height = (index+1)*2.5/14
        v = 15+(index+0.5)*0.28
        box('DeckStairPost',u,height+0.49,v,0.045,0.98,0.045,'Metal',0.005,category='Rail')
edge_rail('DeckWest',(27.12,19.0),(27.12,19.88),2.5)
edge_rail('DeckSouth',(27.12,19.88),(33.88,19.88),2.5)
edge_rail('DeckEast',(33.88,19.88),(33.88,15.12),2.5)
edge_rail('DeckNorth',(33.88,15.12),(29.18,15.12),2.5)
edge_rail('DeckStairVoid',(29.18,15.12),(29.18,18.55),2.5)

stair_rise = 6.4
step_count = 18
step_depth = 0.28
for index in range(step_count):
    lower_top = (index+1)*stair_rise/(step_count*2)
    upper_top = stair_rise/2+lower_top
    box('StairB_Lower_'+str(index+1),46.65,lower_top/2,24.96+(index+0.5)*step_depth,1.55,lower_top,step_depth+0.012,'Floor',0.012,True,'Stair')
    box('StairB_Upper_'+str(index+1),44.75,(stair_rise/2+upper_top)/2,30-(index+0.5)*step_depth,1.55,upper_top-stair_rise/2,step_depth+0.012,'Floor',0.012,True,'Stair')
box('StairB_MidLanding',45.75,3.1,30.72,4.18,0.2,1.44,'Floor',0.012,True,'Stair')
box('StairB_TopLanding',45.75,6.3,23.5,4.18,0.2,2.92,'Floor',0.012,True,'Stair')
for u in (45.82,47.48):
    railing('StairB_LowerRail',[(u,1.05,24.96),(u,4.25,30),(u,4.25,30.7)])
for u in (43.92,45.58):
    railing('StairB_UpperRail',[(u,4.25,30.7),(u,4.25,30),(u,7.45,24.96),(u,7.45,23.8)])
for u,reverse in ((45.82,False),(47.48,False),(43.92,True),(45.58,True)):
    for index in range(0,step_count,3):
        height = (index+1)*3.2/step_count + (3.2 if reverse else 0)
        v = 30-(index+0.5)*step_depth if reverse else 24.96+(index+0.5)*step_depth
        box('StairB_RailPost',u,height+0.49,v,0.045,0.98,0.045,'Metal',0.005,category='Rail')
edge_rail('StairB_MidEnd',(43.92,31.25),(47.48,31.25),3.2)
edge_rail('StairB_InnerTurn',(45.58,30.30),(45.82,30.30),3.2)
edge_rail('StairB_TopEast',(47.48,22.15),(47.48,24.86),6.4)
for u,height,v in ((46.5,4.8,30.9),(44.8,8.3,22.5),(46,3.8,20)):
    box('StairLight',u,height,v,1.1,0.08,0.28,'Light',0.006,category='Fixture')
    lights.append({'room':'STB','position':[u-24,height-0.2,v-16],'range':6,'intensity':3.6})
for name,u,height,v in [('B3_ReviewBoundary',45.75,7.75,22.1),('B5_ReviewBoundary',41.25,1.35,30.8)]:
    box(name,u,height,v,1.7,2.7,0.12,'Service',0.018,True,'Boundary')
    box(name+'_Light',u,height+1.4,v-0.08,1.1,0.05,0.03,'Hazard',0.004,category='Boundary')

scene.cursor.location = (0,0,0)
source_blend = SOURCE / 'B4_Stealth_Architecture.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source_blend))
depsgraph = bpy.context.evaluated_depsgraph_get()
export_collection = bpy.data.collections.new('B4_Export_Baked')
scene.collection.children.link(export_collection)
exports = []
for (category,material,sector), objects in groups.items():
    baked = []
    for original in objects:
        mesh = bpy.data.meshes.new_from_object(original.evaluated_get(depsgraph),depsgraph=depsgraph)
        obj = bpy.data.objects.new('Baked_'+original.name,mesh)
        obj.matrix_world = original.matrix_world.copy()
        export_collection.objects.link(obj)
        baked.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in baked:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = baked[0]
    bpy.ops.object.join()
    combined = bpy.context.object
    combined.name = f'B4_{category}_{material}_{sector}'
    triangulate = combined.modifiers.new('Explicit_Triangles','TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=triangulate.name)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    exports.append(combined)
bpy.ops.object.select_all(action='DESELECT')
for obj in exports:
    obj.select_set(True)
bpy.context.view_layer.objects.active = exports[0]
fbx = MODEL / 'B4_Stealth_Architecture.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_custom_props=True,path_mode='AUTO')
report = {
    'title':'B4 Stealth Architecture V0.01','author':'송예찬','sourcePlanSHA256':hashlib.sha256(PLAN_FILE.read_bytes()).hexdigest(),
    'sourceObjects':source_count,'exportMeshes':len(exports),'triangles':sum(len(obj.data.polygons) for obj in exports),
    'colliders':colliders,'lights':lights,'windows':windows,'materials':palette,'roomHeights':room_heights,
    'deck':{'height':2.5,'steps':14,'riser':2.5/14,'tread':0.28,'stairFootprint':[27.4,15,1.6,3.92]},
    'stairB':{'rise':stair_rise,'steps':36,'riser':stair_rise/36,'tread':0.28,'status':'Provisional section; no B3 transition'},
    'stairA':'Arrival vestibule only; B5 upper landing and B4 door section require reconciliation',
    'coordinates':'Unity (u-24,height,v-16); B4 local datum 0, global floor elevation not finalized'
}
(SOURCE/'architecture_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('B4_ARCHITECTURE_RESULT',json.dumps({key:report[key] for key in ('sourceObjects','exportMeshes','triangles')}))
