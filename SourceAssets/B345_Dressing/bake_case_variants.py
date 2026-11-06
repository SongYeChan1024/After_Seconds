"""Blender-authored specimen case coating/printed pattern variants, baked to original UVs."""
import bpy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
TEX=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/Common/Textures'
bpy.ops.wm.open_mainfile(filepath=str(HERE/'SD_SpecimenCase.blend'))
ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.context.view_layer.objects.active=ob;ob.select_set(True)
for mod in ob.modifiers:mod.show_render=False
mat=ob.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links
bs=next(t for t in n if t.type=='BSDF_PRINCIPLED');base=bs.inputs['Base Color'].links[0].from_socket;out=next(t for t in n if t.type=='OUTPUT_MATERIAL')
def math(op,a,b=0):
 t=n.new('ShaderNodeMath');t.operation=op
 for i,v in enumerate([a,b]):
  if isinstance(v,(float,int)):t.inputs[i].default_value=v
  else:l.new(v,t.inputs[i])
 return t.outputs[0]
def mul(a,b):return math('MULTIPLY',a,b)
def band(a,lo,hi):return mul(math('GREATER_THAN',a,lo),math('LESS_THAN',a,hi))
coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Generated'],sep.inputs[0]);x,y,z=sep.outputs
geo=n.new('ShaderNodeNewGeometry');ns=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],ns.inputs[0]);side=math('LESS_THAN',math('ABSOLUTE',ns.outputs['Z']),.35)
printZone=mul(band(z,.12,.59),side)
patterns=[band(z,.18,.28),math('MAXIMUM',band(z,.18,.23),band(z,.30,.335)),math('MAXIMUM',band(x,.20,.25),band(y,.74,.79)),mul(band(z,.18,.31),math('GREATER_THAN',math('PINGPONG',math('ADD',mul(x,18),mul(y,18)),1),.5)),mul(band(z,.2,.33),math('LESS_THAN',math('PINGPONG',mul(math('ADD',x,y),11),1),.65)),math('MAXIMUM',band(z,.18,.22),mul(band(x,.68,.73),band(z,.18,.49)))]
colors=[(.07,.26,.25,1),(.43,.28,.10,1),(.12,.22,.34,1),(.43,.32,.15,1),(.22,.31,.23,1),(.37,.16,.12,1)]
names=['TealBand','OchreTwin','BlueVertical','AmberChevrons','SageBlocks','RedSeal']
em=n.new('ShaderNodeEmission');l.new(em.outputs[0],out.inputs['Surface'])
mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';l.new(base,mix.inputs[1]);l.new(mix.outputs[0],em.inputs['Color'])
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=1;sc.render.bake.margin=12
rows=[]
for i,(p,col,name) in enumerate(zip(patterns,colors,names)):
 l.new(mul(p,printZone),mix.inputs[0]);mix.inputs[2].default_value=col
 im=bpy.data.images.new('SD_Case_'+name,width=1024,height=1024,alpha=False);im.colorspace_settings.name='sRGB'
 target=n.new('ShaderNodeTexImage');target.image=im;n.active=target
 bpy.ops.object.bake(type='EMIT')
 im.filepath_raw=str(TEX/('SD_Case_'+name+'_Albedo.png'));im.file_format='PNG';im.save()
 rows.append(dict(name=name,texture=im.filepath_raw,pattern=i))
 n.remove(target)
for mod in ob.modifiers:mod.show_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'SD_CasePatterns.blend'))
(HERE/'case_variants.json').write_text(json.dumps(rows,indent=2))
print('CASE_PATTERNS_DONE',len(rows),flush=True)
