"""B5 구역별 벽 마감 제작 V0.02 · 송예찬.
의사코드: 보존한 경량 건축 생성기를 읽기 -> 벽면 생성만 구역별 마감으로 교체
-> 베벨/재질/구역 묶음 -> 새 FBX와 편집 원본. 문/벽 중심선/충돌/기타 형상은 유지.
"""
from pathlib import Path
BASE=Path(__file__).with_name('build_b5_architecture.py')
code=BASE.read_text(encoding='utf-8-sig')
extra=r'''
families={};detail_count=0
surface_palette={'WallConcrete':(.64,.65,.62,1),'WallSterile':(.79,.84,.83,1),'WallSteel':(.62,.68,.70,1),'WallStaff':(.77,.74,.66,1),'WallTeal':(.16,.30,.31,1),'WallPlinth':(.105,.14,.16,1),'WallTrim':(.46,.54,.57,1),'WallGrille':(.065,.085,.095,1)}
for name,color in surface_palette.items():
    m=bpy.data.materials.new('WV_'+name);m.diffuse_color=color;m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=.82 if name=='WallConcrete' else .48
    bs.inputs['Metallic'].default_value=.5 if name in ('WallSteel','WallTrim') else .05
    materials[name]=m

def soft_noise(rng,n,cells):
    a=rng.random((cells,cells));old=np.linspace(0,1,cells);new=np.linspace(0,1,n)
    a=np.array([np.interp(new,old,row) for row in a]);return np.array([np.interp(new,old,col) for col in a.T]).T
def variant_textures():
    n=512;rng=np.random.default_rng(511)
    for family in ('Concrete','Paint','Steel'):
        coarse=soft_noise(rng,n,9)-.5;fine=rng.normal(0,1,(n,n));medium=soft_noise(rng,n,45)-.5
        height=coarse*.35+medium*.18+fine*(.08 if family=='Concrete' else .012)
        if family=='Steel':height=height*.18+np.sin(np.arange(n)[None,:]*.8)*.005
        for kind in ('Base','Normal','MetallicSmoothness'):
            a=np.ones((n,n,4),dtype=np.float32)
            if kind=='Base':
                v=np.clip(.83+coarse*(.11 if family=='Concrete' else .025)+medium*.025+fine*.004,0,1);a[:,:,:3]=v[:,:,None]
            elif kind=='Normal':
                gy,gx=np.gradient(height);normal=np.stack((-gx*1.2,-gy*1.2,np.ones_like(gx)),axis=-1);normal/=np.linalg.norm(normal,axis=-1)[:,:,None];a[:,:,:3]=normal*.5+.5
            else:
                a[:,:,:3]=.02 if family=='Concrete' else .16 if family=='Steel' else .08;a[:,:,3]=np.clip((.18 if family=='Concrete' else .48 if family=='Steel' else .35)+coarse*.04,0,1)
            im=bpy.data.images.new('WV_'+family+'_'+kind,width=n,height=n,alpha=True)
            if kind!='Base':im.colorspace_settings.name='Non-Color'
            im.pixels.foreach_set(a.ravel());im.filepath_raw=str(TEX/('WV_'+family+'_'+kind+'.png'));im.file_format='PNG';im.save()
variant_textures()

# Exposed trims use a separate bare-metal atlas; painted steel wall cladding stays dielectric.
def brushed_trim_textures():
    n=1024;rng=np.random.default_rng(914)
    line=rng.normal(0,1,n)[None,:];long=soft_noise(rng,n,16)-.5
    grain=np.repeat(line,n,axis=0)*.014+long*.018+rng.normal(0,.002,(n,n))
    gy,gx=np.gradient(grain);nn=np.stack((-gx*.85,-gy*.85,np.ones_like(gx)),axis=-1);nn/=np.linalg.norm(nn,axis=-1)[:,:,None]
    for kind in ('Base','Normal','MetallicSmoothness'):
        a=np.ones((n,n,4),dtype=np.float32)
        if kind=='Base':a[:,:,:3]=np.clip(.70+grain[:,:,None]*.65,0,1)
        elif kind=='Normal':a[:,:,:3]=nn*.5+.5
        else:a[:,:,:3]=.96;a[:,:,3]=np.clip(.62+grain*.7,0,1)
        im=bpy.data.images.new('WV_Trim_'+kind,width=n,height=n,alpha=True)
        if kind!='Base':im.colorspace_settings.name='Non-Color'
        im.pixels.foreach_set(a.ravel());im.filepath_raw=str(TEX/('WV_Trim_'+kind+'.png'));im.file_format='PNG';im.save()
brushed_trim_textures()
exec((SOURCE/'wall_material_nodes.py').read_text(encoding='utf-8'))
apply_wall_material_nodes(TEX)
base_finish=finish
def finish(ob,mat,width,sector):
    base_finish(ob,mat,width,sector)
    if mat=='WallTrim':
        ob.modifiers['Manufactured_Bevel'].segments=3;ob['bevel_segments']=3;bevels[-1]['segments']=3
    return ob

def face_room(axis,c,along,side):
    u,v=(along,c+side*.30) if axis=='H' else (c+side*.30,along)
    return next((r for r in plan['rooms'] if r['x']-.001<u<r['x']+r['w']+.001 and r['y']-.001<v<r['y']+r['h']+.001),None)
def family(room):
    if not room:return 'Structure'
    rid=room['id']
    if rid=='A':return 'Sterile'
    if rid in ('B','HVAC','SUP4'):return 'Industrial'
    if rid in ('SUP1','SUP2','SUP3'):return 'Staff'
    if rid in ('STA','STB','LIFT'):return 'Structure'
    return 'Corridor'

def surface_box(name,axis,c,side,along,y,w,h,mat,offset=.139,depth=.028,bevel=.006):
    u,v=(along,c+side*offset) if axis=='H' else (c+side*offset,along)
    sx,sz=(w,depth) if axis=='H' else (depth,w)
    return box(name,u,y,v,sx,h,sz,mat,bevel)
def patch(axis,c,side,a,b,low,high,mat,bay=None,rows=1,prefix='WallFacing'):
    if high-low<.04:return
    count=max(1,math.ceil((b-a)/(bay or max(.1,b-a))));pw=(b-a)/count
    for j in range(count):
        along=a+(j+.5)*pw
        for k in range(rows):
            ph=(high-low)/rows
            surface_box(prefix,axis,c,side,along,low+(k+.5)*ph,max(.035,pw-.018),ph-.018,mat)
def strip(axis,c,side,a,b,y,h,mat='WallTrim'):
    surface_box('FinishBand',axis,c,side,(a+b)/2,y,b-a-.012,h,mat,.160,.020,.004)
def access_panel(axis,c,side,along,y=1.65,w=.70,h=.88):
    global detail_count
    surface_box('Closed_Service_Panel',axis,c,side,along,y,w,h,'WallSteel',.157,.018,.004)
    for s in (-1,1):
        surface_box('ServicePanel_Trim',axis,c,side,along+s*(w/2+.012),y,.026,h+.05,'WallTrim',.168,.020,.003)
        surface_box('ServicePanel_Trim',axis,c,side,along,y+s*(h/2+.012),w,.026,'WallTrim',.168,.020,.003)
    surface_box('ServicePanel_Handle',axis,c,side,along+w*.30,y,.024,.18,'Metal',.169,.020,.003);detail_count+=1
def grille(axis,c,side,along,y=2.95,w=1.0,h=.54):
    global detail_count
    surface_box('Closed_Vent_Backplate',axis,c,side,along,y,w,h,'WallSteel',.157,.018,.004)
    for k in range(6):surface_box('Vent_Louver',axis,c,side,along,y-h*.36+k*h*.145,w-.08,.025,'WallTrim',.169,.020,.004)
    detail_count+=1

def finish_face(axis,c,a,b,side,h,bottom,room):
    kind=family(room);rid=room['id'] if room else 'Exterior';families[rid]=kind
    # High core walls above a lower adjacent ceiling do not need duplicate high cladding.
    h=min(h,room_heights[rid]) if room else h
    if h<=bottom:return
    if kind=='Sterile':
        low=max(bottom,1.0);patch(axis,c,side,a,b,bottom,min(h,1.0),'WallPlinth',2.4)
        patch(axis,c,side,a,b,low,h,'WallSterile',1.8,2 if h-low>4 else 1,'Tall_Sanitary_Panel')
        if bottom<1.0:strip(axis,c,side,a,b,1.015,.055,'WallTeal')
        if b-a>4.5 and bottom<1.0:access_panel(axis,c,side,(a+b)/2,1.65,.64,.90)
    elif kind=='Industrial':
        patch(axis,c,side,a,b,bottom,min(h,1.1),'WallTrim',2.8)
        patch(axis,c,side,a,b,max(bottom,1.1),h,'WallSteel',2.8)
        if bottom<1.1:strip(axis,c,side,a,b,1.12,.055,'Accent')
        start=a+.20
        while start<b-.15:
            if h-max(bottom,1.2)>.1:surface_box('Steel_Vertical_Rib',axis,c,side,start,(max(bottom,1.2)+h)/2,.032,h-max(bottom,1.2)-.06,'WallTrim',.162,.026,.004)
            start+=.66
        if b-a>3.6 and bottom<2.5:grille(axis,c,side,(a+b)/2,min(3.05,h-.55))
    elif kind=='Staff':
        patch(axis,c,side,a,b,bottom,min(h,1.05),'WallTeal',2.7)
        patch(axis,c,side,a,b,max(bottom,1.05),h,'WallStaff',None,1,'Continuous_Plaster_Facing')
        if bottom<1.05:strip(axis,c,side,a,b,1.07,.045)
        if b-a>5.5 and bottom<1:access_panel(axis,c,side,a+(b-a)*.72,1.65,.55,.65)
    else:
        patch(axis,c,side,a,b,bottom,min(h,.32),'WallPlinth',3.5)
        patch(axis,c,side,a,b,max(bottom,.32),h,'WallConcrete',3.5 if kind=='Corridor' else 4.5,1 if h<5 else 3,'Cast_Concrete_Facing')
        if bottom<.32:strip(axis,c,side,a,b,.34,.045)
        count=max(1,math.ceil((b-a)/(3.5 if kind=='Corridor' else 4.5)))
        for j in range(1,count):
            along=a+j*(b-a)/count
            surface_box('Structural_Seam_Cover',axis,c,side,along,(bottom+h)/2,.18,h-bottom-.04,'WallTrim',.161,.026,.005)
        if b-a>6 and kind=='Corridor' and bottom<1:access_panel(axis,c,side,a+(b-a)*.60,1.65)
    # Unified low protection strip, with its face inside the former wall-rail envelope.
    if bottom<.22:strip(axis,c,side,a,b,.18,.065,'WallPlinth')
'''
wall=r'''
wall_count=0
for (axis,c),ranges in edges.items():
    cuts=set(t for a,b,_ in ranges for t in (a,b))
    doors=[d for d in plan['doors'] if d['axis']==axis and abs((d['y'] if axis=='H' else d['x'])-c)<.001]
    for d in doors:
        mid=d['x'] if axis=='H' else d['y'];cuts.update((mid-d['width']/2,mid+d['width']/2))
    cuts=sorted(cuts)
    for a,b in zip(cuts,cuts[1:]):
        mid=(a+b)/2;owners=[rid for lo,hi,rid in ranges if lo-.001<=mid<=hi+.001]
        if not owners or b-a<.05:continue
        h=max(room_heights[o] for o in owners);is_door=any(abs(mid-(d['x'] if axis=='H' else d['y']))<d['width']/2-.001 for d in doors);bottom=2.8 if is_door else 0
        u,v=(mid,c) if axis=='H' else (c,mid);sx,sz=(b-a,.24) if axis=='H' else (.24,b-a)
        box('WallCore',u,(bottom+h)/2,v,sx,h-bottom,sz,'Core',.012,True);wall_count+=1
        for side in (-1,1):finish_face(axis,c,a,b,side,h,bottom,face_room(axis,c,mid,side))
'''
# Preserve base generation and all its coordinates. Replace only the wall finish loop/output names.
code=code.replace('texture_files()\n\ndef world','\n\ndef world',1)
anchor='def rect_difference(rect,cut):'
code=code.replace(anchor,extra+'\n'+anchor,1)
start=code.index('wall_count=0\n');end=code.index('\nfor i,d in enumerate(plan[\'doors\']):',start)
code=code[:start]+wall+code[end:]
code=code.replace("B5_StealthLayout_Lite.blend","B5_StealthLayout_WallVariants.blend").replace("B5_Stealth_Architecture_Lite.fbx","B5_Stealth_WallVariants.fbx").replace("architecture_lite_manifest.json","wall_variants_manifest.json").replace("B5 Stealth Architecture V0.02 Lite","B5 Wall Finishes V0.02").replace("B5_StealthLayout V0.02 Lite","B5 Wall Finishes V0.02")
code=code.replace("'wallSegments':wall_count,","'wallSegments':wall_count,'wallFamilies':families,'finishDetailModules':detail_count,'wallFaceEnvelope_m':.18,")
exec(compile(code,str(BASE),'exec'),{'__file__':str(BASE),'__name__':'__main__'})
