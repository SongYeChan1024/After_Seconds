import bpy,numpy as np,json
from pathlib import Path
R=Path(__file__).parent;P=R.parent.parent/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Common/Textures';P.mkdir(parents=True,exist_ok=True)
W,H=1024,2048;rng=np.random.default_rng(71103)
def noise(nx,ny):
 g=rng.random((ny+1,nx+1)).astype(np.float32);g[:,-1]=g[:,0];xx=np.arange(W,dtype=np.float32)*nx/W;yy=np.arange(H,dtype=np.float32)*ny/H;ix=xx.astype(int);iy=yy.astype(int);fx=xx-ix;fy=yy-iy;fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
 return ((g[iy[:,None],ix[None,:]]*(1-fx)+g[iy[:,None],ix[None,:]+1]*fx)*(1-fy[:,None])+(g[iy[:,None]+1,ix[None,:]]*(1-fx)+g[iy[:,None]+1,ix[None,:]+1]*fx)*fy[:,None])
coarse=noise(7,14);medium=noise(32,64);fine=noise(170,340);micro=rng.random((H,W)).astype(np.float32);y=np.arange(H,dtype=np.float32)[:,None]*4/H
paint=(y<1.15).astype(np.float32);trim=((y>=1.15)&(y<1.19)).astype(np.float32);grain=(coarse-.5)*.016+(medium-.5)*.014+(fine-.5)*.014+(micro-.5)*.008
base=np.zeros((H,W,3),np.float32);base[:]=[.74,.755,.77];base=base*(1-paint[:,:,None])+np.array([.54,.56,.58],np.float32)*paint[:,:,None];base=base*(1-trim[:,:,None])+np.array([.19,.21,.23],np.float32)*trim[:,:,None];base+=grain[:,:,None]
pore=(micro>.993).astype(np.float32)*(fine>.59);chip=np.clip((medium-.83)*5,0,.5)*paint;chip*=np.clip((fine-.5)*3,0,1);base=base*(1-chip[:,:,None]) + np.array([.60,.61,.62],np.float32)*chip[:,:,None]
dirt=np.exp(-y/.14)*(.018+coarse*.025);base-=dirt[:,:,None];base-=pore[:,:,None]*.035
# Shallow formwork joins at two-metre intervals, visually sealed rather than geometric cuts.
xx=np.arange(W)[None,:];jointx=np.minimum(xx,W-xx)<1.4;jointy=np.abs(y-2)<.0025;joints=np.maximum(jointx.astype(float),jointy.astype(float)).astype(np.float32);base-=joints[:,:,None]*.035
height=(medium-.5)*.00020+(fine-.5)*.00016+(micro-.5)*.000035-pore*.00015-chip*.00012-joints*.0004
dx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))/(4/W);dy=np.gradient(height,4/H,axis=0);normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=2);normal/=np.linalg.norm(normal,axis=2)[:,:,None];normal=normal*.5+.5
rough=np.clip(.84-paint*.16+grain*.6+chip*.1,.58,.94);ao=np.clip(1-pore*.15-joints*.06,.8,1);mask=np.zeros((H,W,4),np.float32);mask[:,:,1]=ao;mask[:,:,3]=1-rough
def save(name,data,linear=False):
 if data.shape[2]==3:data=np.concatenate([data,np.ones((H,W,1),np.float32)],axis=2)
 im=bpy.data.images.new(name,width=W,height=H,alpha=True);im.colorspace_settings.name='Non-Color' if linear else 'sRGB';im.pixels.foreach_set(np.clip(data,0,1).astype(np.float32).ravel());im.filepath_raw=str(P/(name+'.png'));im.file_format='PNG';im.save()
save('FacilityWall_BaseColor',base);save('FacilityWall_Normal',normal,True);save('FacilityWall_Mask',mask,True)
(R/'texture_spec.json').write_text(json.dumps({'size':[W,H],'tileMetres':[2,4],'maps':['BaseColor','TangentNormal','Mask_RMetallic_GOcclusion_ASmoothness'],'lowerPaintHeightMetres':1.15,'materialCount':1,'seed':71103,'generation':'Deterministic periodic multi-scale procedural noise, shared height-derived normal and roughness; no photographic or AI source'},indent=2),encoding='utf-8')
print('Created 3 coordinated wall PBR maps',flush=True)
