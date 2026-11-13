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
reports=[]
for room in site['rooms']+site['tunnels']:
 m=Model('FD_'+room['id']+'_WallTrim')
 for q in [w for w in site['walls'] if w['room']==room['id']]:
  start=len(m.v);a,b=q['a'],q['b'];length=math.dist(a,b);dx,dz=(b[0]-a[0])/length,(b[1]-a[1])/length;h={'C01':9,'C02':7.3}.get(q['room'],q['h'])
  for side in [-1,1]:
   face=side*(q['th']/2+.012)
   # Folded base flashing and end cover strips, with fasteners on the overlaps.
   m.box((length/2,.28,face),(length,.052,.017),'Corrosion');m.box((length/2,.248,face+side*.01),(length,.018,.032),'Steel')
   for x in [.055,length-.055]:
    m.box((x,h/2,face),(.062,h,.016),'Plaster')
    for i in range(int(h/.6)):m.bolt((x,.48+i*.6,face+side*.01),.009,sign=side)
   for i in range(max(1,int(length/.9))):m.bolt(((i+.5)*length/max(1,int(length/.9)),.28,face+side*.012),.010,sign=side)
   op=opening(q)
   if op:
    sill,wh,cell,ww,count=op
    for i in range(count):
     x=(i+.5)*cell;y=sill+wh+.025
     m.box((x,y,face),(ww+.16,.035,.025),'Corrosion');m.box((x,y-.014,face+side*.035),(ww+.18,.022,.045),'Steel')
     for xx in [x-ww/2-.045,x+ww/2+.045]:
      m.box((xx,sill+wh/2,face),(.036,wh+.09,.012),'Steel')
      for yy in [sill+.12,sill+wh-.12]:m.bolt((xx,yy,face+side*.012),.009,sign=side)
  for i in range(start,len(m.v)):
   x,y,z=m.v[i];m.v[i]=(a[0]+dx*x-dz*z,y,a[1]+dz*x+dx*z)
 if m.v:reports.append(m.export())
(H/'walls.json').write_text(json.dumps(reports,indent=2))

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
for qi,q in enumerate(site['walls']):
 if q['room'].startswith('T') or qi%4==0:continue
 a,b=q['a'],q['b'];length=math.dist(a,b)
 if length<2.4:continue
 u=Vector(((b[0]-a[0])/length,0,(b[1]-a[1])/length));op=opening(q)
 for side in [-1,1]:
  normal=Vector((-u.z,0,u.x))*side
  anchors=[length*.22,length*.71] if length<9 else [length*(i+.5)/max(2,int(length/5.5)) for i in range(max(2,int(length/5.5)))]
  for anchor in anchors:
   if op:anchor=round(anchor/op[2])*op[2]+rng.uniform(-.12,.12)
   anchor=max(.35,min(length-.35,anchor));height=rng.uniform(1.7,4.3);vines+=1
   def point(x,y,depth=.03):return Vector((a[0],y,a[1]))+u*x+normal*(q['th']/2+depth)
   def solid(x,y,margin=.12):
    if x<.10 or x>length-.10:return False
    if op:
     sill,wh,cell,ww,count=op
     if sill-margin<y<sill+wh+margin and abs((x%cell)-cell/2)<ww/2+margin:return False
    return True
   stem=[]
   for i in range(int(height/.18)+1):
    y=i*.18;x=anchor+math.sin(y*2+qi)*.075
    if solid(x,y,.015):stem.append(point(x,y))
   if len(stem)>1:m.tube(stem,.009,'IvyBark',6)
   for j in range(1,int(height/.18)):
    y=j*.18;sgn=-1 if j%2 else 1;start=point(anchor+math.sin(y*2+qi)*.075,y);reach=rng.uniform(.18,.55)*(1-y/(height*1.4));tipx=anchor+sgn*reach;tipy=y+rng.uniform(.06,.3)
    if not solid(tipx,tipy):tipx=anchor+sgn*.15
    tip=point(tipx,tipy,.07);middle=(start+tip)/2+normal*.018
    if not solid(tipx,tipy,.05):continue
    m.tube([start,middle,tip],.0045,'IvyBark',5);branches+=1
    for k in range(3):
     t=.45+k*.25;c=start.lerp(tip,t)+u*rng.uniform(-.07,.07)+normal*rng.uniform(.015,.065);s=rng.uniform(.095,.17)*(1-y/(height*3));xx=(c-Vector((a[0],0,a[1]))).dot(u)
     if not solid(xx,c.y,s):continue
     mat=rng.choices(['IvyDark','IvyMid','IvyLight','IvyDry'],[4,5,2,1])[0];root=leaf(c,u,normal,s,rng.uniform(-1.15,1.15),mat);m.beam(start.lerp(tip,t),root,.0025,'IvyBark',4)
report=m.export();report.update(leaves=leaves,branches=branches,vines=vines,windowClearance=True);(H/'ivy.json').write_text(json.dumps(report,indent=2));print('LANDSCAPE_READY',len(reports),report)
