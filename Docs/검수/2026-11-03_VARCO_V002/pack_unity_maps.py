import bpy,json,numpy as np
from pathlib import Path
R=Path(__file__).parent
records=json.loads((R/'unity_export_manifest.json').read_text(encoding='utf-8'))
PROJECT=R.parent.parent/'Unity/After_Seconds_Build_V0.01'
def texture_input(socket):
    if not socket.links:return None
    link=socket.links[0];node=link.from_node
    if node.type=='TEX_IMAGE':return node.image,0
    if node.type=='SEPARATE_COLOR':
        source=node.inputs['Color'].links[0].from_node
        if source.type=='TEX_IMAGE':return source.image,{'Red':0,'Green':1,'Blue':2}[link.from_socket.name]
    return None
for record in records:
    bpy.ops.wm.open_mainfile(filepath=str(R/(record['floor']+'_retopo.blend')))
    obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');mat=obj.data.materials[0];p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    rough=texture_input(p.inputs['Roughness']);metal=texture_input(p.inputs['Metallic'])
    dims=rough[0].size[:] if rough else [2048,2048];w,h=dims
    def channel(ref,fallback):
        if not ref:return np.full(w*h,fallback,dtype=np.float32)
        img,ch=ref;pixels=np.empty(len(img.pixels),dtype=np.float32);img.pixels.foreach_get(pixels);return pixels.reshape((-1,4))[:,ch]
    m=channel(metal,p.inputs['Metallic'].default_value);r=channel(rough,p.inputs['Roughness'].default_value)
    ao=None
    for node in mat.node_tree.nodes:
        if node.type=='GROUP' and 'Occlusion' in node.inputs:
            ao=texture_input(node.inputs['Occlusion'])
    a=channel(ao,1)
    root=PROJECT/Path(record['modelPath']).parent.parent/'Textures'
    def save(name,pixels):
        img=bpy.data.images.new(name,width=w,height=h,alpha=True);img.colorspace_settings.name='Non-Color';img.pixels.foreach_set(pixels.ravel());img.filepath_raw=str(root/(name+'.png'));img.file_format='PNG';img.save();return str((root/(name+'.png')).relative_to(PROJECT)).replace('\\','/')
    ms=np.ones((w*h,4),dtype=np.float32);ms[:,0]=m;ms[:,1:3]=0;ms[:,3]=np.clip(1-r,0,1)
    occ=np.ones((w*h,4),dtype=np.float32);occ[:,:3]=a[:,None]
    record['unityMetallicSmoothness']=save('Unity_MetallicSmoothness',ms);record['unityOcclusion']=save('Unity_Occlusion',occ)
    record['pbrPacking']={'metallic':'R','smoothness':'A=1-roughness','occlusion':'G=source occlusion','sourceRoughnessChannel':rough[1] if rough else None,'sourceMetallicChannel':metal[1] if metal else None,'sourceOcclusionChannel':ao[1] if ao else None}
    (PROJECT/Path(record['modelPath']).parent.parent/'source_manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PBR',record['floor'],record['pbrPacking'],flush=True)
(R/'unity_export_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
