"""Targeted Blender rebuild of AF_C01_ThreePortalRibs; no full layout regeneration."""
from pathlib import Path
import math,json
H=Path(__file__).resolve().parent;R=H.parents[1]
library=R/'SourceAssets/B5_Sector01/build_details.py'
env={'__file__':str(library),'__name__':'rib_helpers'}
exec(compile(library.read_text('utf-8').split('# Structural ribs')[0],str(library),'exec'),env)
env['H']=R/'SourceAssets/B5_FullLayout'
env['reset']()
bpy=env['bpy'];mesh=env['mesh'];cyl=env['cyl'];mats=env['mats']
for key,name,color,metal,rough in [
    ('Rib','AF_C01_RibMetal',(.27,.34,.39,1),.64,.57),
    ('Joint','AF_C01_RibJoint',(.15,.21,.25,1),.68,.5),
    ('Anchor','AF_C01_RibAnchor',(.34,.4,.43,1),.8,.4)]:
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=color
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;mats[key]=mat

def arc(name,deg,lo,hi,width,inner,outer,steps,material,bevel):
    a=math.radians(deg);ca,sa=math.cos(a),math.sin(a);vs=[]
    for tangent in [-width/2,width/2]:
        for radius in [inner,outer]:
            for j in range(steps+1):
                p=math.radians(lo+(hi-lo)*j/steps);rr=radius*math.cos(p)
                vs.append((ca*rr-sa*tangent,radius*math.sin(p),sa*rr+ca*tangent))
    k=steps+1;fs=[]
    for j in range(steps):fs.extend([(j,j+1,k+j+1,k+j),(2*k+j,3*k+j,3*k+j+1,2*k+j+1),(j,2*k+j,2*k+j+1,j+1),(k+j,k+j+1,3*k+j+1,3*k+j)])
    fs.extend([(0,k,3*k,2*k),(k-1,3*k-1,4*k-1,2*k-1)])
    return mesh(name,vs,fs,material,bevel,True)

angles=[32.5+45*i for i in range(8)]
for i,deg in enumerate(angles):
    arc(f'Continuous_Rib_{i+1:02}',deg,0,85.8,.28,9.64,9.98,64,'Rib',.008)
    for j,p in enumerate([22,44,66]):arc(f'Sleeve_{i+1:02}_{j+1}',deg,p-.27,p+.27,.32,9.625,9.99,3,'Joint',.003)
    a=math.radians(deg);ca,sa=math.cos(a),math.sin(a)
    def point(rad,y,tan):return (ca*rad-sa*tan,y,sa*rad+ca*tan)
    v=[point(r,y,t) for r,y,t in [(9.54,0,-.23),(9.98,0,-.23),(9.98,0,.23),(9.54,0,.23),(9.54,.11,-.23),(9.98,.11,-.23),(9.98,.11,.23),(9.54,.11,.23)]]
    mesh(f'Rib_Foot_{i+1:02}',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Joint',.008)
    for radial in [9.59,9.93]:
        for tangent in [-.18,.18]:cyl(f'Anchor_{i+1:02}',point(radial,.11,tangent),point(radial,.127,tangent),.021,'Anchor',6)

# A continuous spherical crown band receives all eight arches at identical elevation.
vs=[];n=64
for radius in [9.64,9.98]:
    for p in [85.25,86.4]:
        a=math.radians(p)
        for j in range(n):
            phi=2*math.pi*j/n;vs.append((radius*math.cos(a)*math.cos(phi),radius*math.sin(a),radius*math.cos(a)*math.sin(phi)))
fs=[]
for j in range(n):
    q=(j+1)%n
    fs.extend([(j,q,n+q,n+j),(2*n+j,3*n+j,3*n+q,2*n+q),(j,2*n+j,2*n+q,q),(n+j,n+q,3*n+q,3*n+j)])
mesh('Continuous_Crown_Ring',vs,fs,'Joint',.005,True)
env['export']('AF_C01_ThreePortalRibs')
manifest=dict(env['manifest']['AF_C01_ThreePortalRibs'])
manifest.update(angles_deg=angles,arc_span_deg=[0,85.8],width_m=.28,inner_radius_m=9.64,outer_radius_m=9.98,wall_inner_radius_m=9.936,projection_m=.296,continuous_beams=8,crown_ring=True,materials=[mats[k].name for k in ['Rib','Joint','Anchor']])
(H/'rib_geometry.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
