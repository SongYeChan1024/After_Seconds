import bpy,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).parent
PROJECT=R.parent.parent/'Unity/After_Seconds_Build_V0.01'
assets=json.loads((R/'batch_manifest.json').read_text(encoding='utf-8-sig'))['assets']
# Candidate dimensions in Blender metres, before FBX converts Z-up to Unity Y-up.
spec={'U01':('lengthX',1.0),'U02':('minExtent',.32),'U03':('height',.55),'U04':('lengthX',1.5),'U05':('lengthX',1.0),'U06':('maxExtent',.7),'U07':('height',.28),'P01':('exact',(.8,1.9,.65)),'P02':('height',.75),'P03':('maxExtent',.55),'P04':('height',1.4),'P05':('height',.22),'P06':('height',1.9),'P07':('height',.65),'P08':('width',.4),'P09':('height',.95),'P10':('height',1.65),'P11':('height',1.25),'P12':('exact',(1.2,1.0,.15)),'P13':('exact',(.6,.45,.4))}
def bounds(objects):
    points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));return lo,hi
def input_image(socket):
    if not socket.links:return None
    link=socket.links[0];node=link.from_node
    if node.type=='TEX_IMAGE':return node.image,0
    if node.type=='SEPARATE_COLOR' and node.inputs['Color'].links:
        img=node.inputs['Color'].links[0].from_node
        if img.type=='TEX_IMAGE':return img.image,{'Red':0,'Green':1,'Blue':2}[link.from_socket.name]
    return None
records=[]
for asset in assets:
    code=asset['id'];name=asset['name'];path=R/(code+'_retopo.blend')
    if not path.exists():raise RuntimeError('Retopology candidate missing '+code)
    bpy.ops.wm.open_mainfile(filepath=str(path));objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    mode,value=spec[code]
    if mode=='lengthX':
        lo,hi=bounds(objects);size=hi-lo;axis=max(range(3),key=lambda i:size[i]);direction=Vector(tuple(1 if i==axis else 0 for i in range(3)))
        rotation=direction.rotation_difference(Vector((1,0,0))).to_matrix().to_4x4()
        for o in objects:o.matrix_world=rotation@o.matrix_world
    lo,hi=bounds(objects);size=hi-lo
    if mode=='exact':scale=Vector(tuple(value[i]/size[i] for i in range(3)))
    else:
        divisor=size.x if mode in ['lengthX','width'] else (size.z if mode=='height' else (min(size) if mode=='minExtent' else max(size)))
        scale=Vector((value/divisor,)*3)
    center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));transform=Matrix.Diagonal((*scale,1.0))@Matrix.Translation(-center)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True);o.matrix_world=transform@o.matrix_world
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    category='Environment' if code.startswith('U') else 'Props'
    root=PROJECT/'Assets/Afrer_Seconds/05.Model'/category/'VARCO_V002/Batch02'/(code+'_'+name)
    for kind in ['Models','Textures','Materials','Prefabs']:(root/kind).mkdir(parents=True,exist_ok=True)
    mat=objects[0].data.materials[0];bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    base=input_image(bsdf.inputs['Base Color']);normal_node=bsdf.inputs['Normal'].links[0].from_node;normal=normal_node.inputs['Color'].links[0].from_node.image
    rough=input_image(bsdf.inputs['Roughness']);metal=input_image(bsdf.inputs['Metallic']);ao=None
    for node in mat.node_tree.nodes:
        if node.type=='GROUP' and 'Occlusion' in node.inputs:ao=input_image(node.inputs['Occlusion'])
    def save_source(img,name):
        if max(img.size)>2048:img.scale(round(img.size[0]*2048/max(img.size)),round(img.size[1]*2048/max(img.size)))
        img.filepath_raw=str(root/'Textures'/(name+'.png'));img.file_format='PNG';img.save();return str((root/'Textures'/(name+'.png')).relative_to(PROJECT)).replace('\\','/')
    base_path=save_source(base[0],'BaseColor');normal_path=save_source(normal,'Normal')
    w,h=rough[0].size[:] if rough else [2048,2048]
    def channel(ref,fallback):
        if ref is None:return np.full(w*h,fallback,dtype=np.float32)
        img,ch=ref;pixels=np.empty(len(img.pixels),dtype=np.float32);img.pixels.foreach_get(pixels);return pixels.reshape((-1,4))[:,ch]
    m=channel(metal,bsdf.inputs['Metallic'].default_value);r=channel(rough,bsdf.inputs['Roughness'].default_value);occlusion=channel(ao,1)
    def save_packed(name,data):
        img=bpy.data.images.new(name,width=w,height=h,alpha=True);img.colorspace_settings.name='Non-Color';img.pixels.foreach_set(data.ravel());return save_source(img,name)
    ms=np.zeros((w*h,4),dtype=np.float32);ms[:,0]=m;ms[:,3]=np.clip(1-r,0,1)
    occ=np.ones((w*h,4),dtype=np.float32);occ[:,:3]=occlusion[:,None]
    ms_path=save_packed('MetallicSmoothness',ms);ao_path=save_packed('Occlusion',occ)
    fbx=root/'Models'/(code+'_'+name+'.fbx')
    for o in objects:o.name=code+'_'+name
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='OFF',bake_anim=False,path_mode='STRIP')
    lo,hi=bounds(objects)
    record={'id':code,'name':name,'ko':asset['ko'],'category':category,'sourceFlowId':'f86f4f34-c6fe-45de-8f9b-3ed1303cab0b','sourceHighNode':asset['mesh'],'sourceRetopoFile':str((R/(code+'_retopo.glb')).relative_to(R.parent.parent)).replace('\\','/'),'sourceSha256':hashlib.sha256((R/(code+'_retopo.glb')).read_bytes()).hexdigest(),'modelPath':str(fbx.relative_to(PROJECT)).replace('\\','/'),'modelSha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),'baseMap':base_path,'normalMap':normal_path,'metallicSmoothnessMap':ms_path,'occlusionMap':ao_path,'blenderSizeXYZ':list(hi-lo),'candidateDimensionRule':{'mode':mode,'value':value},'triangles':sum(len(p.vertices)-2 for o in objects for p in o.data.polygons),'visualOnly':True,'status':'Prepared; Unity verification pending','pbrPacking':{'metallic':'R','smoothness':'A=1-source G','occlusion':'G=source R'},'normalStrength':.35}
    (root/'source_manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');records.append(record)
    (R/'unity_prepared_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');print('EXPORTED',code,list(hi-lo),flush=True)
