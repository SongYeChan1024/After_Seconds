"""Wall surface variations V0.01. Existing bevelled geometry; four PBR atlases.
Author: 송예찬. No geometry, collision, room, prop or runtime changes.
"""
import bpy,bmesh,numpy as np,math,json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
SRC=Path(__file__).resolve().parent;REPO=SRC.parents[1]
ENV=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment'
TEX=ENV/'Common/Textures';TEX.mkdir(exist_ok=True,parents=True)
families={'Clean':(.79,.80,.79),'Staff':(.73,.75,.74),'Steel':(.63,.66,.67),'Concrete':(.69,.70,.68)}
mapping={'LP_WallSteel':'Steel','WV_WallSteel':'Steel','WV_WallSterile':'Clean','WV_WallConcrete':'Concrete','WV_WallStaff':'Staff','SL_Panel':'Clean','B4_Panel':'Staff','B4_Service':'Steel','B4_Clinical':'Clean','LP_WallStaff':'Staff','LP_WallClean':'Clean'}

def save_image(name,a,base=False):
 im=bpy.data.images.new(name,width=a.shape[1],height=a.shape[0],alpha=True)
 im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.clip(a,0,1).astype(np.float32).ravel());im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save();bpy.data.images.remove(im)

def textures():
 n=1024;y,x=np.mgrid[:n,:n];u=(x/n-.03)/.94;v=(y/n-.03)/.94
 rng=np.random.default_rng(110612)
 fy=np.fft.fftfreq(n)[:,None];fx=np.fft.rfftfreq(n)[None,:]
 def noise(sx,sy=None):
  sy=sy or sx;a=rng.normal(0,1,(n,n));a=np.fft.irfft2(np.fft.rfft2(a)*np.exp(-2*math.pi**2*((fx*sx)**2+(fy*sy)**2)),s=(n,n));return a/(a.std()+1e-8)
 # Organic noise, no repeated symbols, decorative stripes, fasteners or access hatches.
 for family,color in families.items():
  maps={k:np.ones((2*n,2*n,4),np.float32) for k in ('Albedo','Normal','MetallicSmoothness')}
  for tile in range(4):
   grain=rng.normal(0,1,(n,n));coarse=noise(60);medium=noise(15);fine=noise(2)
   steel=family=='Steel';concrete=family=='Concrete';clean=family=='Clean'
   a=np.ones((n,n,4));a[:,:,:3]=np.array(color)*[1,.99,1.008,.995][tile]
   detail=(.004 if concrete else .002)*grain+(.005 if concrete else .003)*medium
   if steel:detail+=noise(110,0.65)*.006
   a[:,:,:3]+=detail[:,:,None]
   height=(.000035 if concrete else .000018)*grain+(.000035 if concrete else .000012)*fine
   smooth=np.full((n,n),.48 if steel else .24 if concrete else .40)+medium*.008
   metal=np.full((n,n),.86 if steel else 0.)
   # All variants have a light irregular deposit at the joins, without painted seam lines.
   side=np.exp(-np.maximum(np.minimum(u,1-u),0)*70)
   dust=side*np.clip(.07+.035*medium,.015,.16)+np.clip(coarse+medium*.35-1.0,0,3)*.008
   wipe=np.zeros((n,n));scuff=np.zeros((n,n));contact=np.zeros((n,n))
   if tile==1: # Floor-level dust; assigned only to panels meeting the floor.
    bottom=np.exp(-np.maximum(v,0)*(17+3*np.tanh(coarse)))
    dust+=bottom*np.clip(.42+.16*coarse+.10*medium+.04*fine,.05,.76)
    dust+=np.exp(-np.maximum(v,0)*55)*np.clip(.14+.07*medium,0,.27)
    scuff+=np.exp(-((v-.13)/.05)**2)*np.clip(noise(60,2)-1.1,0,2)*.027
   elif tile==2: # Wiped surface, handling smudges and small trolley rubs.
    for k in range(5):
     cx=rng.uniform(.15,.85);cy=rng.uniform(.25,.72);ww=rng.uniform(.10,.24);hh=rng.uniform(.025,.07)
     brush=np.exp(-(((u-cx)/ww)**4+((v-cy-.07*(u-cx))/hh)**2))
     wipe+=brush*(.065+.030*np.tanh(noise(50,1.5)))
    for k in range(3):
     cx=rng.uniform(.10,.90);cy=rng.uniform(.35,.68)
     contact+=np.exp(-((u-cx)/.045)**2-((v-cy)/.08)**2)*(.12+.025*np.tanh(fine))
    for k in range(8):
     cx=rng.uniform(.10,.9);cy=rng.uniform(.06,.35);length=rng.uniform(.015,.09)
     scuff+=np.exp(-((u-cx)/length)**6-((v-cy-.03*(u-cx))/.0011)**2)*.10
   elif tile==3: # Faint irregular cleaning residue, suitable for upper panels too.
    residue=np.clip(noise(4,50)-.85,0,2)
    dust+=residue*np.clip(.045+.025*coarse,0,.10)
    wipe+=np.exp(-((v-.54)/.28)**2)*np.clip(noise(70,4),0,2)*.012
   amount=.65 if clean else 1.15 if concrete else 1.
   dust=np.clip(dust*amount,0,.72);contact*=amount;scuff*=amount
   dustcolor=np.array((.32,.30,.25)) if not steel else np.array((.35,.33,.28))
   a[:,:,:3]=a[:,:,:3]*(1-dust[:,:,None])+dustcolor*dust[:,:,None]
   a[:,:,:3]-=(contact*.45+scuff+wipe*.16)[:,:,None]
   # Dust is non-metallic and matte; wipes/skin marks primarily change reflection.
   metal*=1-dust*.95;smooth-=dust*.34+wipe*.75+contact*.6+scuff*.25
   height+=dust*.00003-scuff*.00006
   dx=(np.roll(height,-1,1)-np.roll(height,1,1))*n/3
   dy=(np.roll(height,-1,0)-np.roll(height,1,0))*n/4
   normal=np.stack([-dx,-dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1)[:,:,None]
   norm=np.ones((n,n,4));norm[:,:,:3]=normal*.5+.5
   ms=np.ones((n,n,4));ms[:,:,:3]=metal[:,:,None];ms[:,:,3]=np.clip(smooth,.08,.55)
   ys=slice((tile//2)*n,(tile//2+1)*n);xs=slice((tile%2)*n,(tile%2+1)*n)
   for kind,data in [('Albedo',a),('Normal',norm),('MetallicSmoothness',ms)]:maps[kind][ys,xs]=data
  for kind,data in maps.items():save_image('WS_'+family+'_'+kind,data)

def material(family):
 name='WS_'+family;m=bpy.data.materials.get(name)
 if m:return m
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*families[family],1)
 nodes=m.node_tree.nodes;links=m.node_tree.links;bs=nodes.get('Principled BSDF')
 for kind in ('Albedo','Normal','MetallicSmoothness'):
  tx=nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(TEX/(name+'_'+kind+'.png')),check_existing=True);tx.image.colorspace_settings.name='sRGB' if kind=='Albedo' else 'Non-Color';tx.extension='EXTEND'
  if kind=='Albedo':links.new(tx.outputs['Color'],bs.inputs['Base Color'])
  elif kind=='Normal':nn=nodes.new('ShaderNodeNormalMap');links.new(tx.outputs['Color'],nn.inputs['Color']);links.new(nn.outputs['Normal'],bs.inputs['Normal'])
  else:
   sep=nodes.new('ShaderNodeSeparateColor');links.new(tx.outputs['Color'],sep.inputs['Color']);links.new(sep.outputs['Red'],bs.inputs['Metallic'])
   inv=nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;links.new(tx.outputs['Alpha'],inv.inputs[1]);links.new(inv.outputs[0],bs.inputs['Roughness'])
 return m

def build(floor):
 path=REPO/('SourceAssets/B345_Dressing/SD_B3_Architecture.blend' if floor=='B3' else f'SourceAssets/LevelContinuation/LC_{floor}_Architecture.blend')
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.preferences.filepaths.save_version=0
 targets=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials[0].name in mapping]
 old_batches=set();counts=Counter();rows=[]
 for ob in targets:
  old=ob.data.materials[0].name;family=mapping[old];u=24-ob.location.x;v=16-ob.location.y;sector=(int(max(0,min(47.9,u))//8),int(max(0,min(31.9,v))//8))
  old_batches.add(f'LC_{floor}_{old}_{sector[0]}_{sector[1]}')
  seed=int(hashlib.sha256((floor+'/'+ob.name).encode()).hexdigest()[:8],16);roll=seed%100
  bottom=ob.location.z-ob.dimensions.z/2
  # Ground accumulation never repeats halfway up the wall. Upper panels get faint residue.
  tile=(1 if roll<58 else 2 if roll<86 else 0) if bottom<.45 else (0 if roll<66 else 3)
  ds=sorted(ob.dimensions);tile=0 if ds[1]<.35 else tile
  me=ob.data.copy();ob.data=me;me.materials.clear();me.materials.append(material(family))
  co=np.array([p.co[:] for p in me.vertices]);lo=co.min(0);hi=co.max(0);uv=me.uv_layers.active or me.uv_layers.new(name='UVMap')
  for p in me.polygons:
   axis=max(range(3),key=lambda j:abs(p.normal[j]));axes=[j for j in range(3) if j!=axis]
   for li in p.loop_indices:
    c=me.vertices[me.loops[li].vertex_index].co;uv0=[(c[j]-lo[j])/max(hi[j]-lo[j],1e-6) for j in axes]
    uu=1-uv0[0] if seed%2 else uv0[0]
    uv.data[li].uv=((tile%2+.03+.94*uu)/2,(tile//2+.03+.94*uv0[1])/2)
  ob['wall_surface_variant']=tile;ob['source_material']=old;ob['source_batch']=f'LC_{floor}_{old}_{sector[0]}_{sector[1]}'
  counts[family+'_'+str(tile)]+=1;rows.append({'object':ob.name,'sourceMaterial':old,'family':family,'variant':tile})
 # Keep just these source objects, retaining all bevel modifiers and dimensions.
 keep=set(targets)
 for ob in list(bpy.context.scene.objects):
  if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
 for mat in list(bpy.data.materials):
  if not mat.name.startswith('WS_'):bpy.data.materials.remove(mat)
 bpy.data.orphans_purge(do_recursive=True)
 for im in list(bpy.data.images):
  if im.name.startswith('WS_'):im.reload();im.pack()
  else:bpy.data.images.remove(im)
 bpy.ops.wm.save_as_mainfile(filepath=str(SRC/('WS_'+floor+'_Walls.blend')))
 dep=bpy.context.evaluated_depsgraph_get();batches=defaultdict(list);col=bpy.data.collections.new('Wall_Export');bpy.context.scene.collection.children.link(col)
 for ob in targets:
  me=bpy.data.meshes.new_from_object(ob.evaluated_get(dep),depsgraph=dep);n=bpy.data.objects.new('Export',me);col.objects.link(n);n.matrix_world=ob.matrix_world.copy()
  u=24-ob.location.x;v=16-ob.location.y;batches[(me.materials[0].name,int(max(0,min(47.9,u))//8),int(max(0,min(31.9,v))//8))].append(n)
 output=[]
 for (mat,x,z),obs in batches.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  ob=bpy.context.object;ob.name=f'WS_{floor}_{mat}_{x}_{z}';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();output.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in output:ob.select_set(True)
 bpy.context.view_layer.objects.active=output[0]
 bpy.ops.export_scene.fbx(filepath=str(ENV/floor/f'WS_{floor}_Walls.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,bake_anim=False,mesh_smooth_type='FACE')
 result={'floor':floor,'sourceObjects':len(targets),'triangles':sum(len(o.data.polygons) for o in output),'renderers':len(output),'oldBatches':sorted(old_batches),'variants':dict(counts),'panels':rows}
 (SRC/(floor+'_walls.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print('WALL_DONE',floor,len(targets),result['triangles'],flush=True)

if __name__=='__main__':
 textures()
 for floor in ('B5','B4','B3'):build(floor)
