"""Six irregular use/wear finishes, baked on original case UVs in Blender.
No decorative bands. Original handles, rim, latches, normals and bevel retained.
"""
import bpy,json
from pathlib import Path
SRC=Path(__file__).resolve().parent;REPO=SRC.parents[1]
TEX=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/Common/Textures'
bpy.ops.wm.open_mainfile(filepath=str(REPO/'SourceAssets/B345_Dressing/SD_SpecimenCase.blend'))
bpy.context.preferences.filepaths.save_version=0
ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.context.view_layer.objects.active=ob;ob.select_set(True)
for mod in ob.modifiers:mod.show_render=False
source=ob.data.materials[0];sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=1;sc.render.bake.margin=14
names=['LightDust','CornerDust','Handling','WipeMarks','Scuffed','Stored'];reports=[]
for index,name in enumerate(names):
 mat=source.copy();mat.name='SW_Case_'+name;mat.use_fake_user=True;ob.data.materials[0]=mat
 n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(t for t in n if t.type=='BSDF_PRINCIPLED');base=bs.inputs['Base Color'].links[0].from_socket;out=next(t for t in n if t.type=='OUTPUT_MATERIAL')
 def math(op,a,b=0):
  t=n.new('ShaderNodeMath');t.operation=op
  for i,v in enumerate([a,b]):
   if isinstance(v,(float,int)):t.inputs[i].default_value=v
   else:l.new(v,t.inputs[i])
  return t.outputs[0]
 def mul(a,b):return math('MULTIPLY',a,b)
 def add(a,b):return math('ADD',a,b)
 def sub(a,b):return math('SUBTRACT',a,b)
 def band(a,lo,hi):return mul(math('GREATER_THAN',a,lo),math('LESS_THAN',a,hi))
 def mix(a,b,fac,blend='MIX'):
  t=n.new('ShaderNodeMixRGB');t.blend_type=blend
  for i,v in enumerate([fac,a,b]):
   if isinstance(v,(float,int)):t.inputs[i].default_value=v
   elif isinstance(v,tuple):t.inputs[i].default_value=v
   else:l.new(v,t.inputs[i])
  return t.outputs[0]
 coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Generated'],sep.inputs[0]);x,y,z=sep.outputs
 def noise(scale,detail=3,stretch=None):
  t=n.new('ShaderNodeTexNoise');t.noise_dimensions='4D';t.inputs['Scale'].default_value=scale;t.inputs['Detail'].default_value=detail;t.inputs['Roughness'].default_value=.7;t.inputs['W'].default_value=11.63+index*7.37
  vec=coord.outputs['Generated']
  if stretch:
   q=n.new('ShaderNodeVectorMath');q.operation='MULTIPLY';l.new(vec,q.inputs[0]);q.inputs[1].default_value=stretch;vec=q.outputs[0]
  l.new(vec,t.inputs['Vector']);return t.outputs['Fac']
 broad=noise(5);fine=noise(92,2);patch=math('MAXIMUM',sub(mul(broad,2.2),.72),0)
 # Neutralize the repetitive green printed stripe while keeping bolts/barcode/metal parts.
 rgb=n.new('ShaderNodeSeparateColor');l.new(base,rgb.inputs['Color']);red,green,blue=rgb.outputs[:3]
 printed=mul(math('GREATER_THAN',green,mul(red,1.12)),math('LESS_THAN',red,.30))
 coating=mix(base,(.47,.45,.34,1),printed)
 painted=mul(math('GREATER_THAN',red,mul(blue,1.10)),math('GREATER_THAN',red,.16))
 coating=mix(coating,(.88,.94,1.26,1),math('MAXIMUM',painted,printed),'MULTIPLY')
 tint=[(1,1,1,1),(.98,.98,.96,1),(1.01,1,.98,1),(1,1.01,1.015,1),(.975,.98,.975,1),(.99,.975,.95,1)][index]
 coating=mix(coating,tint,1,'MULTIPLY')
 edge=math('MINIMUM',math('MINIMUM',x,sub(1,x)),math('MINIMUM',y,sub(1,y)))
 rim=math('MAXIMUM',sub(1,mul(edge,15)),0);low=math('MAXIMUM',sub(1,mul(z,7)),0)
 top=math('MAXIMUM',mul(sub(z,.73),3.7),0)
 strengths=[.12,.70,.38,.24,.50,1.1]
 dust=mul(add(add(mul(rim,.45),mul(low,.65)),mul(top,.8)),mul(patch,strengths[index]))
 dust=math('MINIMUM',add(dust,mul(patch,.018)),.80)
 # Grease/handling appears near the gripping area; random masks prevent regular bands.
 touch=mul(mul(band(z,.30,.65),band(x,.23,.77)),math('MAXIMUM',sub(.25,math('MINIMUM',y,sub(1,y))),0))
 touch=mul(touch,mul(patch,3.0 if index==2 else .20))
 wipe=mul(math('MAXIMUM',sub(noise(8,3,(.6,1.5,9)),.40),0),.85 if index==3 else .07)
 scuff=mul(math('GREATER_THAN',noise(35,2,(.25,1,15)),.62),mul(rim,.58 if index==4 else .025))
 albedo=mix(coating,(.14,.125,.10,1),dust)
 albedo=mix(albedo,(.13,.12,.105,1),add(mul(touch,.9),mul(wipe,.20)))
 albedo=mix(albedo,(.24,.25,.245,1),scuff)
 msim=n.new('ShaderNodeTexImage');msim.image=bpy.data.images.load(str(TEX/'SD_SpecimenCase_MetallicSmoothness.png'),check_existing=True);msim.image.colorspace_settings.name='Non-Color'
 mssep=n.new('ShaderNodeSeparateColor');l.new(msim.outputs['Color'],mssep.inputs['Color']);metal=mul(mssep.outputs['Red'],sub(1,mul(dust,.95)))
 smooth=math('MAXIMUM',sub(msim.outputs['Alpha'],add(mul(dust,.65),add(mul(touch,.4),wipe))),.07)
 # Bake albedo and packed metallic RGB / smoothness alpha separately; alpha from a scalar bake.
 em=n.new('ShaderNodeEmission');l.new(em.outputs[0],out.inputs['Surface'])
 baked={}
 for kind,value in [('Albedo',albedo),('Metallic',metal),('Smoothness',smooth)]:
  l.new(value,em.inputs['Color']);im=bpy.data.images.new('SW_Case_'+name+'_'+kind,width=1024,height=1024,alpha=True);im.colorspace_settings.name='sRGB' if kind=='Albedo' else 'Non-Color'
  node=n.new('ShaderNodeTexImage');node.image=im;n.active=node;bpy.ops.object.bake(type='EMIT');baked[kind]=im;n.remove(node)
  if kind=='Albedo':im.filepath_raw=str(TEX/('SW_Case_'+name+'_Albedo.png'));im.file_format='PNG';im.save()
 import numpy as np
 arrays={}
 for k in ('Metallic','Smoothness'):
  arr=np.empty(len(baked[k].pixels),np.float32);baked[k].pixels.foreach_get(arr);arrays[k]=arr.reshape(1024,1024,4)
 packed=arrays['Metallic'].copy();packed[:,:,3]=arrays['Smoothness'][:,:,0]
 im=bpy.data.images.new('SW_Case_'+name+'_MetallicSmoothness',width=1024,height=1024,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(packed.ravel());im.filepath_raw=str(TEX/('SW_Case_'+name+'_MetallicSmoothness.png'));im.file_format='PNG';im.save()
 l.new(bs.outputs[0],out.inputs['Surface']);l.new(albedo,bs.inputs['Base Color']);l.new(metal,bs.inputs['Metallic']);l.new(sub(1,smooth),bs.inputs['Roughness'])
 reports.append({'name':name,'seed':11.63+index*7.37,'dustStrength':strengths[index]});print('CASE_WEAR_DONE',name,flush=True)
for mod in ob.modifiers:mod.show_render=True
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'SW_CaseWear.blend'))
(SRC/'case_wear.json').write_text(json.dumps(reports,indent=2))
