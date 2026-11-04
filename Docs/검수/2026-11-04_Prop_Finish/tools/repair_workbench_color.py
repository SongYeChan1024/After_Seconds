"""기존 UV와 세부 텍스처를 유지하고 넓은 판재의 색만 emission으로 다시 베이크한다."""
# 의사코드: 원본 메시·UV → 평면 패치 분류 → 넓은 판재 색 정돈 → 조명 없는 색 베이크.
import bpy,bmesh,json,math,sys,statistics
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]);repo=root.parents[1]
data=next(json.loads(p.read_text(encoding='utf-8-sig')) for p in (root/'input').glob('*.json') if 'LaboratoryWorkbench' in p.name)
project=repo/'Unity/After_Seconds_Build_V0.01'
texture=project/'Assets/Afrer_Seconds/05.Model/Props/Common/Textures/Props_LaboratoryWorkbench_BaseColor.png'
output=texture.with_name('Props_LaboratoryWorkbench_BaseColor_Corrected.png')
bpy.ops.wm.read_factory_settings(use_empty=True)
faces=[t[i:i+3] for t in data['submeshes'] for i in range(0,len(t),3)]
mesh=bpy.data.meshes.new('WorkbenchOriginalUV');mesh.from_pydata(data['vertices'],[],faces);mesh.update()
uv=mesh.uv_layers.new(name='UVMap')
for p in mesh.polygons:
 for li in p.loop_indices:uv.data[li].uv=data['uv'][mesh.loops[li].vertex_index]
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-9);bm.normal_update();bm.faces.ensure_lookup_table()
original=bpy.data.images.load(str(texture));original.colorspace_settings.name='sRGB';pixels=list(original.pixels);w,h=original.size
def sample(tex):
 x=min(w-1,max(0,int(tex.x*w)));y=min(h-1,max(0,int(tex.y*h)));i=(y*w+x)*4
 return pixels[i:i+3]
layer=bm.loops.layers.uv.active;seen=set();patches=[];extent=max(max(v.co[i] for v in bm.verts)-min(v.co[i] for v in bm.verts) for i in range(3))
for seed in bm.faces:
 if seed.index in seen:continue
 seen.add(seed.index);group=[seed];stack=[seed]
 while stack:
  f=stack.pop()
  for edge in f.edges:
   for other in edge.link_faces:
    if other.index not in seen and other.normal.dot(seed.normal)>.992:
     seen.add(other.index);group.append(other);stack.append(other)
 area=sum(f.calc_area() for f in group);normal=seed.normal
 if area<extent*extent*.012 or max(abs(v) for v in normal)<.90:continue
 points=[v.co for f in group for v in f.verts];span=sorted(max(v[i] for v in points)-min(v[i] for v in points) for i in range(3))
 if span[1]<extent*.07 or span[0]>extent*.04:continue
 colors=[sample(sum((l[layer].uv for l in f.loops),Vector((0,0)))/len(f.loops)) for f in group[::max(1,len(group)//100)]]
 median=[statistics.median(c[i] for c in colors) for i in range(3)];light=sum(median)/3
 if light<.10:continue  # 모니터 화면과 어두운 내부는 그대로 보존한다.
 if normal.y>.9 and sum(v.y for v in points)/len(points)>.25:color=(.60,.60,.585,1)
 else:color=tuple(min(.48,max(.20,v)) for v in median)+(1,)
 slot=len(patches)+1
 for f in group:f.material_index=slot
 patches.append({'slot':slot,'faces':len(group),'areaLocal':area,'normal':list(normal),'color':list(color)})
bm.to_mesh(mesh);bm.free();mesh.update()
obj=bpy.data.objects.new('WorkbenchColorRebake',mesh);bpy.context.collection.objects.link(obj);obj.select_set(True);bpy.context.view_layer.objects.active=obj
target=bpy.data.images.new('Workbench_Corrected_2048',width=w,height=h,alpha=True);target.colorspace_settings.name='sRGB';target.pixels=pixels
for slot in range(len(patches)+1):
 mat=bpy.data.materials.new('PreservedDetail' if slot==0 else 'CleanPanel_'+str(slot));mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear()
 out=nodes.new('ShaderNodeOutputMaterial');emit=nodes.new('ShaderNodeEmission');mat.node_tree.links.new(emit.outputs[0],out.inputs['Surface'])
 if slot==0:
  src=nodes.new('ShaderNodeTexImage');src.image=original;mat.node_tree.links.new(src.outputs['Color'],emit.inputs['Color'])
 else:emit.inputs['Color'].default_value=patches[slot-1]['color']
 dest=nodes.new('ShaderNodeTexImage');dest.image=target;nodes.active=dest
 mesh.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=1;scene.render.bake.use_clear=False;scene.render.bake.margin=4
bpy.ops.object.bake(type='EMIT')
target.filepath_raw=str(output);target.file_format='PNG';target.save()
record={'source':str(texture),'output':str(output),'resolution':[w,h],'method':'Native Blender emission rebake, original UVs, retained original details outside selected broad planar patches','patches':patches}
(root/'color_rebake.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(repo/'SourceAssets/PropEdgeFinish/WorkbenchColorRebake.blend'))
print('COLOR_REBAKE_DONE',len(patches),flush=True)
