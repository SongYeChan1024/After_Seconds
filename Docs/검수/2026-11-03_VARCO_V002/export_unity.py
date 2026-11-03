import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).parent
PROJECT=R.parent.parent/'Unity/After_Seconds_Build_V0.01'
names={'B5':('IsolationMonitoringConsole',.65),'B4':('ObservationMonitorBank',1.05),'B3':('DecontaminationColumn',2.2),'B2':('ControlDeskIsland',1.45),'B1':('ExperimentServicePanel',1.2),'1F':('SecurityInspectionCounter',1.25)}
reports=[]
for floor,(name,height) in names.items():
    bpy.ops.wm.open_mainfile(filepath=str(R/f'{floor}_retopo.blend'))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:o.select_set(True)
    if floor=='B5':
        rot=Matrix.Rotation(math.pi/2,4,'X')
        for o in meshes:o.matrix_world=rot@o.matrix_world
    points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    scale=height/(hi.z-lo.z);center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    for o in meshes:o.matrix_world=Matrix.Scale(scale,4)@Matrix.Translation(-center)@o.matrix_world
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    root=PROJECT/'Assets/Afrer_Seconds/05.Model/Props/VARCO_V002'/f'{floor}_{name}'
    for kind in ['Models','Textures','Materials','Prefabs']:(root/kind).mkdir(parents=True,exist_ok=True)
    material_records=[]
    for oi,o in enumerate(meshes):
        o.name=f'{floor}_{name}'
        for mi,material in enumerate(o.data.materials):
            maps=[]
            for node in material.node_tree.nodes:
                if node.type!='TEX_IMAGE' or not node.image:continue
                img=node.image
                links=[{'node':link.to_node.type,'socket':link.to_socket.name} for output in node.outputs for link in output.links]
                kind='normal' if any(x['node']=='NORMAL_MAP' for x in links) else ('baseColor' if any(x['socket']=='Base Color' for x in links) else 'packed')
                filename=f'{oi:02}_{mi:02}_{kind}_{len(maps):02}.png'
                path=root/'Textures'/filename
                if max(img.size)>2048:img.scale(round(img.size[0]*2048/max(img.size)),round(img.size[1]*2048/max(img.size)))
                img.filepath_raw=str(path);img.file_format='PNG';img.save()
                maps.append({'kind':kind,'path':str(path.relative_to(PROJECT)).replace('\\','/'),'size':list(img.size),'colorspace':img.colorspace_settings.name,'links':links})
            material_records.append({'name':material.name,'maps':maps})
    fbx=root/'Models'/f'{floor}_{name}.fbx'
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='OFF',use_custom_props=False,bake_anim=False,path_mode='STRIP')
    points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    size=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
    record={'floor':floor,'name':name,'sourceFlowId':'f86f4f34-c6fe-45de-8f9b-3ed1303cab0b','sourceRetopoFile':str(R/f'{floor}_retopo.glb'),'sourceSha256':hashlib.sha256((R/f'{floor}_retopo.glb').read_bytes()).hexdigest(),'modelPath':str(fbx.relative_to(PROJECT)).replace('\\','/'),'modelSha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),'blenderSizeXYZ':size,'targetHeightMeters':height,'triangles':sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),'materialSources':material_records,'b5DisplayReorientedForWallMount':floor=='B5','status':'Prepared FBX; Unity import verification pending','visualOnly':True}
    (root/'source_manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');reports.append(record)
    print('EXPORTED',floor,json.dumps({'size':size,'triangles':record['triangles'],'maps':material_records}),flush=True)
(R/'unity_export_manifest.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
