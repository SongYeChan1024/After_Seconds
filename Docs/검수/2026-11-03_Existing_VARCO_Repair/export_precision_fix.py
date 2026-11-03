import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).parent;P=R.parent.parent/'Unity/After_Seconds_Build_V0.01'
for a in json.loads((R/'repair_export_manifest.json').read_text()):
 if a['name'] not in ['Env_MetalWall_4m','Env_CeilingPanel_4m']:continue
 bpy.ops.wm.open_mainfile(filepath=str(R/(a['name']+'_retopo.blend')))
 for o in [x for x in bpy.context.scene.objects if x.type=='MESH']:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,dist=1e-6,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));print(a['name'],'boundary',sum(e.is_boundary for e in bm.edges),'overused',sum(len(e.link_faces)>2 for e in bm.edges),flush=True);bm.to_mesh(o.data);bm.free();o.data.update();o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops));o.data.set_sharp_from_angle(angle=.698)
 bpy.ops.export_scene.fbx(filepath=str(P/a['repairedModelPath']),use_selection=False,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False,path_mode='STRIP',use_mesh_modifiers=True)
