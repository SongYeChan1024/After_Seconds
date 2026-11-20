import bpy, math, pathlib, numpy as np
from mathutils import Vector,Quaternion
from math import sin,cos,pi
PROJECT = pathlib.Path(__file__).resolve().parents[2]
BASE = PROJECT / 'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Player/PlayerDummy_Rigged_V0.3.fbx'
REFERENCES = PROJECT / 'SourceAssets/PlayerSubjectReview'
OUT = pathlib.Path(__file__).resolve().parent / 'Build'
OUT.mkdir(exist_ok=True)

def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=.86
    return m

def make(idx):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(BASE))
    src=next(o for o in bpy.context.scene.objects if o.type=='MESH');arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    arm.animation_data_clear()
    for b in arm.pose.bones:b.matrix_basis.identity()
    cloth=material('WardCotton',(.35,.49,.5) if idx==1 else (.56,.52,.44))
    pants=material('WardTrousers',(.19,.30,.31) if idx==1 else (.31,.30,.28))
    rib=material('WardTrim',(.12,.22,.23) if idx==1 else (.27,.24,.21))
    skin=material('SubjectSkin',(.69,.49,.39) if idx==1 else (.58,.39,.31))
    face=material('SubjectFace',(.7,.5,.4));label=material('WardID',(.76,.79,.72))
    sole=material('WardSole',(.20,.20,.19))
    photo=bpy.data.images.load(str(REFERENCES/('Subject_%02d.png'%idx))); tex=face.node_tree.nodes.new('ShaderNodeTexImage');tex.image=photo;face.node_tree.links.new(tex.outputs['Color'],face.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    solids=[]
    def bodypart(name,V,F,weights,mat,uv=None):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(V,[],F);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat)
        for i,ws in enumerate(weights):
            for k,w in ws.items():
                g=o.vertex_groups.get(k) or o.vertex_groups.new(name=k);g.add([i],w,'REPLACE')
        for poly in mesh.polygons:poly.use_smooth=True
        if uv:
            lay=mesh.uv_layers.new(name='SubjectUV')
            for l in mesh.loops:lay.data[l.index].uv=uv[l.vertex_index]
        mod=o.modifiers.new('Pose','ARMATURE');mod.object=arm;solids.append(o)
        return o
    # Extract head, neck and fingers from the shared anatomical base. The garment supplies the whole torso.
    points=[src.matrix_world@v.co for v in src.data.vertices]
    mask=lambda v:abs(v.x)>.384 and .241<v.z<.343
    faces=[tuple(f.vertices) for f in src.data.polygons if all(mask(points[j]) for j in f.vertices)]
    keys=sorted(set(j for f in faces for j in f));mapping={j:i for i,j in enumerate(keys)}
    V=[points[j] for j in keys]; F=[tuple(mapping[j] for j in f) for f in faces]
    weights=[{src.vertex_groups[g.group].name:g.weight for g in src.data.vertices[j].groups if g.weight>.0001} for j in keys]
    bodypart('Skin',V,F,weights,skin)
    # Cylindrical portrait atlas blends profile skin into the same person's scalp.
    pix=np.empty(len(photo.pixels),np.float32);photo.pixels.foreach_get(pix);pix=pix.reshape(1024,1024,4)[::-1]
    W,H=512,256;vgrid=(np.arange(H)+.5)/H;ugrid=(np.arange(W)+.5)/W;phi=(ugrid-.5)*2*pi
    top,chin=(86,198) if idx==1 else (77,192)
    portrait=np.ones((H,W,4),np.float32); hues=[]
    for yy,q in enumerate(vgrid):
        iy=int(np.clip(chin+(top-chin)*q,0,1023));row=pix[iy,:,0:3]
        sample=row[458:565];col=(sample[:,0]-sample[:,2]>.017)&(sample[:,0]>sample[:,1]); ids=np.flatnonzero(col)+458
        if len(ids)>3:
            left=ids.min()+1;right=ids.max()-1
        else:left,right=506,516
        xs=np.clip((511+np.sin(phi)*(right-left)*.50).astype(int),left,right)
        cheeks=(row[min(right,left+2)]+row[max(left,right-2)])*.5
        # Side and back of the skull use locally sampled skin colour rather than the white backdrop.
        cheeks=np.clip(cheeks,[.19,.105,.075],[.71,.53,.43]);blend=np.clip((np.cos(phi)-.06)/.32,0,1)[:,None]
        portrait[yy,:,:3]=row[xs]*blend+cheeks*(1-blend)
        if .42<q<.48:hues.append(cheeks)
    outimg=bpy.data.images.new('WardFace%02d'%idx,width=W,height=H);outimg.pixels.foreach_set(portrait.ravel());outimg.filepath_raw=str(OUT/('WardFace%02d.png'%idx));outimg.file_format='PNG';outimg.save();tex.image=outimg
    tone=tuple(float(v) for v in np.mean(hues,axis=0));skin.diffuse_color=(*tone,1);skin.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*tone,1)
    rprofile=[(.0,.014,.027,-.009),(.05,.031,.040,-.006),(.16,.042,.048,-.002),(.31,.051,.052,.002),(.46,.055,.055,.004),(.58,.054,.059,.006),(.73,.053,.060,.007),(.84,.049,.056,.008),(.94,.036,.044,.008),(1,.004,.009,.008)]
    V=[];F=[];U=[];weights=[];segments=56;rows=32
    for y in range(rows+1):
        q=y/rows
        rx,ry,cy=[np.interp(q,[a[0] for a in rprofile],[a[col] for a in rprofile]) for col in (1,2,3)]
        for j in range(segments+1):
            u=j/segments;t=(u-.5)*2*pi;xx=sin(t);front=max(0,cos(t));nose=.015*math.exp(-((xx/.18)**2)-(((q-.40)/.12)**2))
            V.append((rx*xx,cy-ry*cos(t)-nose*front**5,.361+.138*q));U.append((u,q));weights.append({'Head':1})
    for y in range(rows):
        for j in range(segments):
            k=y*(segments+1)+j;F.append((k,k+1,k+segments+2,k+segments+1))
    headobj=bodypart('Skull',V,F,weights,face,U)
    def loft(name,rings,mat,axis='z',seg=28):
        vs=[];fs=[];w=[]
        for x,y,z,r1,r2,bone in rings:
            for i in range(seg):
                t=2*pi*i/seg
                vs.append((x+r1*cos(t),y+r2*sin(t),z) if axis=='z' else (x,y+r1*cos(t),z+r2*sin(t)));w.append({bone:1})
        for j in range(len(rings)-1):
            for i in range(seg):
                k=(i+1)%seg;fs.append((j*seg+i,j*seg+k,(j+1)*seg+k,(j+1)*seg+i))
        fs+=[tuple(reversed(range(seg))),tuple((len(rings)-1)*seg+i for i in range(seg))]
        return bodypart(name,vs,fs,w,mat)
    def torso(name,rings,mat):
        return loft(name,[(0,.004,z,rx,ry,b) for z,rx,ry,b in rings],mat)
    torso('Neck',[(.313,.040,.037,'Neck'),(.331,.036,.034,'Neck'),(.365,.035,.033,'Head'),(.387,.037,.038,'Head')],skin)
    torso('Tunic',[(-.050,.140,.086,'Hips'),(-.039,.141,.087,'Hips'),(.035,.137,.082,'Hips'),(.09,.108,.067,'Spine'),(.167,.122,.073,'Spine1'),(.226,.137,.081,'Spine2'),(.267,.142,.074,'Spine2'),(.295,.119,.065,'Spine2'),(.323,.054,.045,'Neck')],cloth)
    torso('NeckBinding',[(.317,.056,.047,'Neck'),(.326,.052,.045,'Neck'),(.332,.048,.043,'Neck')],rib)
    torso('LowerHem',[(-.051,.141,.087,'Hips'),(-.041,.142,.088,'Hips')],rib)
    for side,sg in [('Left',1),('Right',-1)]:
        def armring(v):x,y,z,ry,rz,b=v;return(sg*x,y,z,ry,rz,side+b)
        sleeve=[(.073,.008,.280,.064,.054,'Arm'),(.127,.017,.294,.058,.051,'Arm'),(.202,.021,.292,.048,.042,'Arm'),(.244,.025,.291,.042,.041,'ForeArm'),(.303,.018,.293,.042,.036,'ForeArm'),(.369,.01,.295,.032,.032,'ForeArm'),(.395,.006,.295,.029,.029,'Hand')]
        if sg<0:sleeve=list(reversed(sleeve))
        loft(side+'Sleeve',[armring(a) for a in sleeve],cloth,'x')
        cuff=[(.378,.009,.295,.032,.032,'ForeArm'),(.395,.006,.295,.030,.030,'Hand')]
        loft(side+'Cuff',[armring(a) for a in (cuff if sg>0 else reversed(cuff))],rib,'x')
        leg=[(-.464,.064,.03,.039,.046,'Foot'),(-.438,.065,.033,.044,.049,'Leg'),(-.36,.064,.026,.047,.049,'Leg'),(-.258,.059,.016,.051,.053,'Leg'),(-.207,.057,.013,.055,.056,'Leg'),(-.113,.056,.006,.064,.066,'UpLeg'),(-.016,.054,.008,.07,.07,'UpLeg'),(.047,.05,.006,.063,.066,'UpLeg')]
        loft(side+'Trousers',[(sg*x,y,z,rx,ry,side+b) for z,x,y,rx,ry,b in leg],pants)
        shoe=[(-.498,.042,.076,-.004),(-.49,.046,.079,-.006),(-.474,.046,.077,-.006),(-.454,.036,.061,.008),(-.446,.031,.044,.026)]
        loft(side+'Slipper',[(sg*.065,y,z,rx,ry,side+'Foot') for z,rx,ry,y in shoe],sole)
    # Front chest patch, stitched ID bars and wrist band, all bound to the shirt or cuff.
    def patch(name,cx,cy,cz,sx,sz,mat):
        return bodypart(name,[(cx-sx,cy,cz-sz),(cx+sx,cy,cz-sz),(cx+sx,cy,cz+sz),(cx-sx,cy,cz+sz)],[(0,1,2,3)],[{'Spine2':1}]*4,mat)
    patch('Tag',.043,-.071,.238,.019,.009,label)
    for i in range(3 if idx==1 else 4):patch('IDMark',.033+i*.005,-.072,.238,.0014,.005,rib)
    src.hide_viewport=True;src.hide_render=True
    # Art-directed resting poses, head and eyes remain visible from each room's entrance.
    def rot(name,axis,angle):
        b=arm.pose.bones[name];m=(arm.matrix_world@b.bone.matrix_local).to_quaternion();b.rotation_mode='QUATERNION'
        b.rotation_quaternion=b.rotation_quaternion@Quaternion(m.inverted()@Vector(axis),math.radians(angle))
    for side,sg in [('Left',1),('Right',-1)]:
        rot(side+'Arm',(0,1,0),sg*(67 if idx==1 else 71))
        rot(side+'Arm',(0,0,1),-sg*(9 if idx==1 else 3))
        rot(side+'ForeArm',(0,0,1),-sg*(48 if idx==1 else 18))
        rot(side+'UpLeg',(0,1,0),-sg*(2 if idx==1 else 1))
    rot('Head',(0,0,1),-12 if idx==1 else 18);rot('Head',(1,0,0),5 if idx==1 else 1)
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    parts={'Body':[],'Head':[]}
    for o in solids:
        e=o.evaluated_get(deps);mesh=bpy.data.meshes.new_from_object(e,depsgraph=deps);copy=bpy.data.objects.new('Part',mesh);bpy.context.collection.objects.link(copy)
        if o==headobj:
            parts['Head'].append(copy)
        else:parts['Body'].append(copy)
    objs=[];scale=1.66 if idx==1 else 1.80; width=.92 if idx==1 else 1.03
    neck=Vector((0,.008,.344));base=.498
    for tag, group in parts.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in group:o.select_set(True)
        bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name=tag
        pivot=neck if tag=='Head' else Vector((0,0,-base))
        for v in o.data.vertices:
            v.co-=pivot;v.co.x*=scale*width;v.co.y*=scale;v.co.z*=scale
        o.location=(pivot.x*scale*width,pivot.y*scale,(pivot.z+base)*scale);objs.append(o)
    root=bpy.data.objects.new('Subject%02d'%idx,None);bpy.context.collection.objects.link(root)
    for o in objs:o.parent=root
    bpy.ops.object.select_all(action='DESELECT')
    for o in [root]+objs:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.fbx(filepath=str(OUT/('WardSubject%02d.fbx'%idx)),use_selection=True,object_types={'MESH','EMPTY'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,path_mode='STRIP',mesh_smooth_type='FACE')
    print('SUBJECT_ART',idx,[(o.name,len(o.data.vertices)) for o in objs])
for i in (1,2):make(i)

