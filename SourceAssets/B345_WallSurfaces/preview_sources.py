import bpy
from pathlib import Path
from mathutils import Vector
SRC=Path(__file__).resolve().parent;REPO=SRC.parents[1]
TEX=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/Common/Textures'
OUT=REPO/'Docs/검수/2026-11-06_B345_WallSurfaces'
for path in SRC.glob('WS_*_Walls.blend'):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.preferences.filepaths.save_version=0
 for mat in list(bpy.data.materials):
  if not mat.name.startswith('WS_'):bpy.data.materials.remove(mat)
 bpy.data.orphans_purge(do_recursive=True)
 for im in list(bpy.data.images):
  if im.name.startswith('WS_'):im.reload();im.pack()
  else:bpy.data.images.remove(im)
 bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(path));print('PACKED_WALL',path.name,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC/'SW_CaseWear.blend'))
source=next(o for o in bpy.context.scene.objects if o.type=='MESH');source.hide_render=True
for index,name in enumerate(['LightDust','CornerDust','Handling','WipeMarks','Scuffed','Stored']):
 ob=source.copy();ob.data=source.data.copy();bpy.context.scene.collection.objects.link(ob);ob.hide_render=False;ob.location=((index%3-1)*.82,(index//3)*.90,0)
 m=bpy.data.materials.new('Preview_'+name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
 for kind in ['Albedo','MetallicSmoothness','Normal']:
  tx=n.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(TEX/(('SD_SpecimenCase' if kind=='Normal' else 'SW_Case_'+name)+'_'+kind+'.png')),check_existing=True);tx.image.colorspace_settings.name='sRGB' if kind=='Albedo' else 'Non-Color'
  if kind=='Albedo':l.new(tx.outputs['Color'],bs.inputs['Base Color'])
  elif kind=='Normal':nn=n.new('ShaderNodeNormalMap');nn.inputs['Strength'].default_value=.8;l.new(tx.outputs['Color'],nn.inputs['Color']);l.new(nn.outputs[0],bs.inputs['Normal'])
  else:
   sep=n.new('ShaderNodeSeparateColor');l.new(tx.outputs['Color'],sep.inputs['Color']);l.new(sep.outputs['Red'],bs.inputs['Metallic']);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.72;l.new(tx.outputs['Alpha'],mul.inputs[0]);inv=n.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;l.new(mul.outputs[0],inv.inputs[1]);l.new(inv.outputs[0],bs.inputs['Roughness'])
 ob.data.materials.clear();ob.data.materials.append(m)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=1500;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
sc.world=bpy.data.worlds.new('Neutral');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.24,.26,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
target=Vector((0,.45,.14))
cd=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',cd);sc.collection.objects.link(cam);cam.location=(1.7,-3.8,3.3);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=3.2;sc.camera=cam
for pos,power,size in [((-2,-3,5),600,4),((3,1,3),400,3),((0,4,4),500,3)]:
 ld=bpy.data.lights.new('Softbox','AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new('Softbox',ld);sc.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str(OUT/'CaseWear_6Variants.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
