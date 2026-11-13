"""Wall flashing plus connected, curved five-lobed ivy. Window apertures stay clear."""
import sys,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh import *
rng=random.Random(131113)
site=json.loads((H.parent/'F1_AbandonedCamouflage/site.json').read_text(encoding='utf8'))
def opening(q):
 length=math.dist(q['a'],q['b']);h={'C01':9,'C02':7.3}.get(q['room'],q['h'])
 if not (q['window'] or q['room'].startswith('T') and length>5) or length<=2.8:return None
 if h>6:sill=2.8 if h>8 else 2.4;wh=3.15 if h>8 else 2.75;spacing=4;ww=3.1
 elif q['room'].startswith('C'):sill=1.25;wh=1.65;spacing=3.5;ww=2.3
 elif q['room'].startswith('T'):sill=1.65;wh=1.1;spacing=3.4;ww=2
 else:sill=1.9;wh=1.4;spacing=3.4;ww=2.1
 count=max(1,round(length/spacing));cell=length/count;ww=min(ww,cell-.85)
 return sill,wh,cell,ww,count
m=Model('AE_WallIvy');leaves=0;branches=0;vines=0
outline=[(0,-.18),(-.38,-.29),(-.60,-.10),(-.35,.10),(-.67,.38),(-.38,.40),(-.22,.34),(0,1),(.22,.34),(.38,.40),(.67,.38),(.35,.10),(.60,-.10),(.38,-.29)]
# Round the basal outline; retain pointed tips of the three main lobes.
outline=[p for i,c in enumerate(outline) for p in ([c] if i in [0,4,7,10] else [(c[0]*.83+outline[(i-1)%14][0]*.17,c[1]*.83+outline[(i-1)%14][1]*.17),(c[0]*.83+outline[(i+1)%14][0]*.17,c[1]*.83+outline[(i+1)%14][1]*.17)])]
def leaf(c,u,n,size,angle,mat):
 global leaves
 ca,sa=math.cos(angle),math.sin(angle);up=Vector((0,1,0));c=Vector(c);verts=[]
 for x,y in outline:
  xx=(x*ca-y*sa)*size;yy=(x*sa+y*ca)*size;depth=(x*x*.065+y*y*.045)*size
  verts.append(tuple(c+u*xx+up*yy+n*depth))
 center=c+up*(.20*ca*size)-u*(.20*sa*size)+n*.04*size;N=len(verts)
 front=verts+[tuple(center)];faces=[(N,i,(i+1)%N) for i in range(N)]
 m.add(front,faces,mat)
 # Raised midrib/side veins follow the folded surface; narrow enough to stay subdued.
 root=Vector(front[0])+n*.001;ctr=center+n*.002;tip=Vector(front[outline.index((0,1))])+n*.001
 m.add([tuple(root-u*size*.014),tuple(root+u*size*.014),tuple(tip),tuple(ctr+u*size*.012)],[(0,1,3),(0,3,2)],'IvyVein')
 for j in [outline.index((-.67,.38)),outline.index((.67,.38)),3,len(outline)-3]:
  end=Vector(front[j])+n*.001;m.add([tuple(ctr-up*.002),tuple(ctr+up*.002),tuple(end)],[(0,1,2)],'IvyVein')
 leaves+=1
 return Vector(front[0])

roots=[]
groundFile=H.parents[1]/'Docs/Review/2026-11-13_1F_EnvironmentalStory/root_ground.json'
groundSamples=json.loads(groundFile.read_text()) if groundFile.exists() else []
for qi,q in enumerate(site['walls']):
 if q['room'].startswith('T'):continue
 a,b=q['a'],q['b'];length=math.dist(a,b)
 if length<2.8:continue
 u=Vector(((b[0]-a[0])/length,0,(b[1]-a[1])/length));op=opening(q)
 room=next(r for r in site['rooms'] if r['id']==q['room'])
 for side in [-1,1]:
  normal=Vector((-u.z,0,u.x))*side
  outside=(Vector((a[0]-room['x'],0,a[1]-room['z'])).dot(normal)>0)
  if rng.random()>(.88 if outside else .48):continue
  count=max(1,int(length/rng.uniform(7,12)))
  for vi in range(count):
   anchor=rng.uniform(.5,length-.5);height=rng.uniform(1.2,4.3);vines+=1
   if op:height=min(height,op[0]+op[1]+.2)
   def point(x,y,depth=.035):return Vector((a[0],y,a[1]))+u*x+normal*(q['th']/2+depth)
   def solid(x,y,margin=.09):
    if x<.10 or x>length-.10:return False
    if op:
     sill,wh,cell,ww,count=op
     if sill-margin<y<sill+wh+margin and abs((x%cell)-cell/2)<ww/2+margin:return False
    return True
   base=point(anchor,-.16 if outside else .012,.28)
   match=next((g for g in groundSamples if abs(g['x']-base.x)<.001 and abs(g['z']-base.z)<.001),None)
   if match and match['ground']>-2:base.y=match['ground']+.002
   roots.append(dict(wall=q['name'],side=side,x=anchor,world=list(base),height=height))
   # Each root runs through the floor-wall joint before branching, rather than floating above it.
   m.tube([base,point(anchor+.09,.035,.10),point(anchor,.22)],.014,'IvyBark',7)
   paths=[];slant=rng.uniform(-.45,.45)
   for branch in range(rng.choice([2,3,4])):
    pts=[];bh=height*rng.uniform(.45,1);direction=rng.choice([-1,1]);spread=rng.uniform(.35,1.15)*direction
    for j in range(int(bh/.14)+1):
     y=.18+j*.14;xx=anchor+spread*math.sin(min(y/.9,1)*math.pi/2)+math.sin(y*2.2+vi)*.14+slant*y*.3
     if op and y>op[0]-.45:
      pier=round((anchor+spread)/op[2])*op[2];t=min(1,(y-(op[0]-.45))/.3);xx=xx*(1-t)+(pier+math.sin(y*2.4)*.07)*t
     xx=max(.16,min(length-.16,xx))
     if not solid(xx,y,.025):
      if len(pts)>1:paths.append(pts)
      pts=[];continue
     pts.append((xx,y,point(xx,y,.035+math.sin(y*3)*.01)))
    if len(pts)>1:paths.append(pts)
   # Low horizontal runners tie the broad base to narrow upper growth.
   for direction in [-1,1]:
    pts=[];reach=rng.uniform(.55,1.7)
    for j in range(int(reach/.12)+1):
     xx=anchor+direction*j*.12;y=.18+.11*math.sin(j*.34)+j*.028
     if solid(xx,y):pts.append((xx,y,point(xx,y,.06)))
    if len(pts)>1:paths.append(pts)
   for pts in paths:
    m.tube([p[2] for p in pts],rng.uniform(.005,.009),'IvyBark',6)
    for j in range(1,len(pts)):
     if rng.random()<.20:continue
     xx,y,start=pts[j];sgn=rng.choice([-1,1]);reach=rng.uniform(.15,.55);tx=xx+sgn*reach;ty=y+rng.uniform(-.08,.23)
     if not solid(tx,ty):continue
     tip=point(tx,ty,rng.uniform(.07,.14));mid=(start+tip)/2+normal*.015;m.tube([start,mid,tip],.0035,'IvyBark',5);branches+=1
     for k in range(rng.choice([2,3,4])):
      t=.30+k*.21;c=start.lerp(tip,t)+u*rng.uniform(-.10,.10)+Vector((0,rng.uniform(-.1,.1),0))+normal*rng.uniform(.02,.06);size=rng.uniform(.085,.155);lx=(c-Vector((a[0],0,a[1]))).dot(u)
      if not solid(lx,c.y,size*.75):continue
      mat=rng.choices(['IvyDark','IvyMid','IvyLight','IvyDry'],[4,5,1,2])[0];root=leaf(c,u,normal,size,rng.uniform(-1.5,1.5),mat);m.beam(start.lerp(tip,t),root,.0022,'IvyBark',4)
report=m.export();report.update(leaves=leaves,branches=branches,vines=vines,windowClearance=True);(H/'ivy.json').write_text(json.dumps(report,indent=2));(H/'roots.json').write_text(json.dumps(roots,indent=2))
# Dry curled leaves and fine stem litter gather at those same roots, not in regular rows.
m=Model('ES_RootLitter');litter=0
for q in roots:
 x,y,z=q['world'];outside=y<0
 wall=next(w for w in site['walls'] if w['name']==q['wall']);a,b=wall['a'],wall['b'];length=math.dist(a,b);u=Vector(((b[0]-a[0])/length,0,(b[1]-a[1])/length));n=Vector((-u.z,0,u.x))*q['side']
 for j in range(rng.randint(9,20)):
  c=Vector((x,y+.015,z))+u*rng.uniform(-.65,.65)+n*rng.uniform(-.02,.45);sz=rng.uniform(.035,.075);ang=rng.random()*math.tau;v=[]
  for ox,oy in [(0,-.8),(-.55,-.25),(-.6,.3),(0,1),(.6,.3),(.55,-.25)]:
   px,pz=(ox*math.cos(ang)-oy*math.sin(ang))*sz,(ox*math.sin(ang)+oy*math.cos(ang))*sz;v.append((c.x+px,c.y+abs(ox)*sz*.2,c.z+pz))
  v.append((c.x,c.y+.007,c.z));m.add(v,[(6,i,(i+1)%6) for i in range(6)],rng.choice(['IvyDry','DryLeaf','Dust']));litter+=1
 for j in range(3):
  c=Vector((x,y+.015,z))+u*rng.uniform(-.4,.4)+n*.1;m.beam(c,c+u*rng.uniform(.06,.24)+n*.04,.003,'IvyBark',4)
(H/'litter_mesh.json').write_text(json.dumps(dict(v=m.v,f=m.f,fm=m.fm,m=m.m)))
report=m.export();report['leaves']=litter;(H/'litter.json').write_text(json.dumps(report,indent=2));print('IVY_READY',vines,leaves,litter)
