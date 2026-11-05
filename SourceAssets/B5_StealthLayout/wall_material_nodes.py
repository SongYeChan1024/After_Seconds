"""B5 벽 마감 Blender PBR 노드 동기화 V0.01 · 송예찬.
의사코드: Unity와 같은 맵/색/금속도/거칠기/노멀/UV 반복을 편집 원본에 연결한다.
Unity 외부의 아트 제작 도구이며 게임 동작 코드는 아니다.
"""
import bpy

def apply_wall_material_nodes(texture_dir):
    colors={'WallConcrete':(.64,.65,.62,1),'WallSterile':(.79,.84,.83,1),'WallSteel':(.62,.68,.70,1),'WallStaff':(.77,.74,.66,1),'WallTeal':(.16,.30,.31,1),'WallPlinth':(.105,.14,.16,1),'WallTrim':(.90,.92,.94,1),'WallGrille':(.065,.085,.095,1)}
    for name,color in colors.items():
        mat=bpy.data.materials.get('WV_'+name)
        if not mat: continue
        family='Trim' if name=='WallTrim' else 'Concrete' if name=='WallConcrete' else 'Steel' if name in ('WallSteel','WallGrille') else 'Paint'
        mat.use_nodes=True;mat.diffuse_color=color
        nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
        uv=nt.nodes.new('ShaderNodeTexCoord');mul=nt.nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(4,4,4) if family=='Trim' else (1,1,1);nt.links.new(uv.outputs['UV'],mul.inputs[0])
        maps={}
        for kind in ('Base','Normal','MetallicSmoothness'):
            tex=nt.nodes.new('ShaderNodeTexImage');path=str(texture_dir/('WV_'+family+'_'+kind+'.png'));tex.image=bpy.data.images.load(path,check_existing=True);tex.image.colorspace_settings.name='sRGB' if kind=='Base' else 'Non-Color';nt.links.new(mul.outputs[0],tex.inputs['Vector']);maps[kind]=tex
        tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=color;nt.links.new(maps['Base'].outputs['Color'],tint.inputs[1]);nt.links.new(tint.outputs[0],bs.inputs['Base Color'])
        metal=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(maps['MetallicSmoothness'].outputs['Color'],metal.inputs[0]);nt.links.new(metal.outputs['Red'],bs.inputs['Metallic'])
        smooth=nt.nodes.new('ShaderNodeMath');smooth.operation='MULTIPLY';smooth.inputs[1].default_value=1 if family=='Trim' else .18 if family=='Concrete' else .4;nt.links.new(maps['MetallicSmoothness'].outputs['Alpha'],smooth.inputs[0]);rough=nt.nodes.new('ShaderNodeMath');rough.operation='SUBTRACT';rough.inputs[0].default_value=1;nt.links.new(smooth.outputs[0],rough.inputs[1]);nt.links.new(rough.outputs[0],bs.inputs['Roughness'])
        normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.32 if family=='Trim' else .25 if family=='Concrete' else .16;nt.links.new(maps['Normal'].outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
        for im in maps.values():im.image.filepath=bpy.path.relpath(im.image.filepath)

