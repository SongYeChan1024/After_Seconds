"""B1-specific tabletop variants. Existing saved lower furniture is retained."""
from pathlib import Path
import sys,json,math,gzip,collections,os
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01'
sys.path.insert(0,str(R/'SourceAssets/B1_FullFloor'))
import common as c
import bpy,bmesh
from mathutils import Vector,Matrix
box=c.box;cyl=c.cyl;mesh=c.mesh
def tube(name,pts,r,mat='Dark'):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=5;cu.bevel_depth=r;cu.bevel_resolution=1;cu.use_fill_caps=True;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1);coords=[Vector(c.xyz(*v)) for v in pts]
 for i,(p,co) in enumerate(zip(sp.bezier_points,coords)):
  p.co=co;p.handle_left_type='FREE';p.handle_right_type='FREE';prev=coords[max(i-1,0)];nxt=coords[min(i+1,len(coords)-1)];t=(nxt-prev).normalized();a=co-t*(co-prev).length/3;b=co+t*(nxt-co).length/3
  for k in range(3):a[k]=max(min(prev[k],co[k]),min(max(prev[k],co[k]),a[k]));b[k]=max(min(nxt[k],co[k]),min(max(nxt[k],co[k]),b[k]))
  p.handle_left=a;p.handle_right=b
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(c.b.mats[mat]);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
 for p in ob.data.polygons:p.use_smooth=True
 ob.select_set(False);return ob
plan=json.loads((H/'plan.json').read_text(encoding='utf8'));labels=json.loads((R/'SourceAssets/B4_DeskAndCollision/key_labels.json').read_text())
archive=H/'source_geometry.json.gz'
if not archive.exists():
 source={p.stem:json.loads(p.read_text(encoding='utf8')) for p in (H/'mesh_export').glob('*.json')}
 with gzip.open(archive,'wt',encoding='utf8') as f:json.dump(source,f,separators=(',',':'))
else:
 with gzip.open(archive,'rt',encoding='utf8') as f:source=json.load(f)
only=set(filter(None,os.getenv('DP_ONLY','').split(',')))
manifest=json.loads((H/'models.json').read_text()) if only else {};matpaths={};details=[];basecounts=json.loads((H/'retained_geometry.json').read_text()) if only else {}
E='Assets/Afrer_Seconds/05.Model/Environment/B1/Materials/'
def reset():
 c.reset();matpaths.clear();details.clear()
 for key,mat in c.b.mats.items():matpaths[mat.name]=E+'B1M_'+key+'.mat'
 for key,path in [('KeyLegend','Assets/Afrer_Seconds/05.Model/Props/B4/Materials/PD_KeyLegend.mat'),('Print','Assets/Afrer_Seconds/05.Model/Props/B1/Materials/DP_WorkRecords.mat'),('ScreenPrint','Assets/Afrer_Seconds/05.Model/Props/B1/Materials/DP_WorkScreens.mat')]:
  mat=bpy.data.materials.new('DP_'+key);mat.diffuse_color=(.5,.5,.5,1);c.b.mats[key]=mat;matpaths[mat.name]=path
def mark(n,x,z,w,d,y):details.append(dict(kind=n,center=[x,y,z],size=[w,d]))
def group(fn,x=0,y=0,z=0,yaw=0):
 before=set(bpy.context.scene.objects);fn();c.transform(set(bpy.context.scene.objects)-before,x,y,z,yaw)
def quad(n,vs,uv,mat):
 ob=mesh(n,vs,[(0,1,2,3)],mat,0)
 # Printed faces must point up for paper or forward for a screen, never into the substrate.
 if abs(vs[0][1]-vs[1][1])<1e-8 and abs(vs[0][1]-vs[2][1])<1e-8:
  if ob.data.polygons[0].normal.z<0:ob.data.flip_normals()
 else:
  if ob.data.polygons[0].normal.y>0:ob.data.flip_normals()
 layer=ob.data.uv_layers.new(name='UVMap')
 for face in ob.data.polygons:
  for li in face.loop_indices:layer.data[li].uv=uv[ob.data.loops[li].vertex_index]
 ob['display_uv']=True;return ob
def atlas_uv(tile):
 u=tile%4/4;v=1-(tile//4+1)/4;e=.002
 return [(u+e,v+.25-e),(u+.25-e,v+.25-e),(u+.25-e,v+e),(u+e,v+e)]
def print_top(n,x,y,z,w,d,tile):
 return quad(n,[(x+w/2,y,z-d/2),(x-w/2,y,z-d/2),(x-w/2,y,z+d/2),(x+w/2,y,z+d/2)],atlas_uv(tile),'Print')
def print_front(n,x,y,z,w,h,tile):
 return quad(n,[(x+w/2,y+h/2,z),(x-w/2,y+h/2,z),(x-w/2,y-h/2,z),(x+w/2,y-h/2,z)],atlas_uv(tile),'ScreenPrint')
def base(model,top=None,dining=False):
 q=source[model][0];vs=q['vertices'];faces=[];mi=[]
 for m,ts in enumerate(q['submeshes']):
  for i in range(0,len(ts),3):faces.append(tuple(ts[i:i+3]));mi.append(m)
 parent=list(range(len(vs)))
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 def union(a,b):parent[find(a)]=find(b)
 weld={}
 for i,v in enumerate(vs):
  k=tuple(round(x,5) for x in v)
  if k in weld:union(i,weld[k])
  else:weld[k]=i
 for f in faces:union(f[0],f[1]);union(f[1],f[2])
 groups=collections.defaultdict(list)
 for j,f in enumerate(faces):groups[find(f[0])].append(j)
 keep=[]
 for ids in groups.values():
  inds=set(i for j in ids for i in faces[j]);lo=[min(vs[i][k] for i in inds) for k in range(3)];hi=[max(vs[i][k] for i in inds) for k in range(3)]
  yes=top is None or hi[1]<=top+.0008 or lo[1]<.5 or dining and (lo[2]>.56 or hi[2]<-.56)
  if yes:keep.extend(ids)
 ids=sorted(set(i for j in keep for i in faces[j]));remap={n:i for i,n in enumerate(ids)}
 me=bpy.data.meshes.new('Retained_Furniture');me.from_pydata([c.xyz(*vs[i]) for i in ids],[],[tuple(remap[i] for i in reversed(faces[j])) for j in keep]);me.update()
 for i,path in enumerate(q['materials']):
  name='Saved_'+Path(path).stem
  mat=bpy.data.materials.get(name) or bpy.data.materials.new(name);matpaths[name]=path;me.materials.append(mat)
 for poly,j in zip(me.polygons,keep):poly.material_index=mi[j]
 uv=me.uv_layers.new(name='UVMap')
 if q['uv']:
  for poly in me.polygons:
   for li in poly.loop_indices:uv.data[li].uv=q['uv'][ids[me.loops[li].vertex_index]]
 # Unity -> Blender uses a reflected coordinate basis: reverse triangle winding.
 # Recalculating un-welded hard-edge faces would flip individual furniture panels.
 # Preserve authored split normals for the retained furniture.
 if len(q['normals'])==len(vs):me.normals_split_custom_set_from_vertices([Vector(c.xyz(*q['normals'][i])).normalized() for i in ids])
 ob=bpy.data.objects.new('Retained_Furniture',me);bpy.context.collection.objects.link(ob);ob['display_uv']=True;basecounts[model]={'originalTriangles':len(faces),'retainedTriangles':len(keep)}
 return ob
def keyboard(x,y,z,yaw=0):
 def build():
  w=.378;d=.158;pitch=.0193;left=-w/2+.012
  box('Keyboard_Base',0,.010,0,w,.016,d,'Dark',.004);box('Keyboard_Upper_Rim',0,.020,0,w-.003,.008,d-.003,'Coat',.003)
  for xx in [-.14,.14]:
   for zz in [-.052,.052]:box('Rubber_Foot',xx,.001,zz,.027,.002,.018,'Rubber',.0004)
  def key(label,u,zz,units=1,dep=.017,height=.009):
   xx=-(left+(u+units/2)*pitch);ww=units*pitch-.002
   box('Key_'+label.replace('/','Slash'),xx,.029,zz,ww,height,dep,'Dark',.0013)
   if label=='Space':return
   i=labels.index(label);co=i%16;ro=i//16;u0=(co*64+3)/1024;u1=(co*64+61)/1024;v0=1-(ro*64+61)/1024;v1=1-(ro*64+3)/1024
   lw=min(ww-.003,.023 if len(label)>2 else .010);ld=.010 if len(label)>2 else .011
   quad('Key_Legend_'+label,[(xx+lw/2,.029+height/2+.0004,zz-ld/2),(xx-lw/2,.029+height/2+.0004,zz-ld/2),(xx-lw/2,.029+height/2+.0004,zz+ld/2),(xx+lw/2,.029+height/2+.0004,zz+ld/2)],[(u0,v1),(u1,v1),(u1,v0),(u0,v0)],'KeyLegend')
  rows=[[('`',1)]+[(str(i),1) for i in [1,2,3,4,5,6,7,8,9,0]]+[('-',1),('=',1),('Back',2)],[('Tab',1.5)]+[(k,1) for k in 'QWERTYUIOP']+[('[',1),(']',1),('\\',1.5)],[('Caps',1.75)]+[(k,1) for k in 'ASDFGHJKL']+[(';',1),("'",1),('Enter',2.25)],[('Shift',2.25)]+[(k,1) for k in 'ZXCVBNM']+[(',',1),('.',1),('/',1),('Shift',2.75)],[('Ctrl',1.25),('Win',1.25),('Alt',1.25),('Space',6.25),('Alt',1.25),('Fn',1.25),('Menu',1.25),('Ctrl',1.25)]]
  for n,row in enumerate(rows):
   pos=0
   for label,units in row:key(label,pos,-.046+n*.023,units);pos+=units
  key('Esc',0,-.068,dep=.012,height=.007)
  for i in range(12):key('F'+str(i+1),2+i+i//4*.34,-.068,.9,.012,.007)
  for n,label in enumerate(['Ins','Home','PgUp']):key(label,15.45+n,-.046)
  for n,label in enumerate(['Del','End','PgDn']):key(label,15.45+n,-.023)
  key('Up',16.45,.023)
  for n,label in enumerate(['Left','Down','Right']):key(label,15.45+n,.046)
  for xx in [-.15,-.13]:cyl('Status_LED',(xx,.025,.068),(xx,.026,.068),.0017,'Indicator',10)
 group(build,x,y,z,yaw);mark('keyboard',x,z,.378,.158,y)
def mouse(x,y,z):
 box('Mouse_Mat',x,y+.002,z,.205,.004,.218,'Rubber',.004)
 # One continuous sculpted shell with clean click-panel material boundaries.
 # This avoids overlapping approximate ellipsoids at the button/palm join.
 us=sorted(set([-1,-.92,-.06,0,.06,.92,1]+[i/16 for i in range(-15,16)]))
 zs=sorted(set([-.0498+i*.1116/24 for i in range(25)]+[-.047,.009]))
 nx=len(us);nz=len(zs);vs=[];fs=[];white=[]
 for zz in zs:
  v=(zz-.006)/.056;arc=math.sqrt(max(0,1-v*v))
  for u in us:vs.append((x+.031*arc*u,y+.007+.027*arc*math.sqrt(max(0,1-u*u)),z+zz))
 for j in range(nz-1):
  for i in range(nx-1):
   a=j*nx+i;fs.append((a,a+1,a+nx+1,a+nx));uu=(us[i]+us[i+1])/2;zz=(zs[j]+zs[j+1])/2
   white.append(-.047<=zz<.009 and .06<abs(uu)<.92)
 rim=list(range(nx))+[j*nx+nx-1 for j in range(1,nz)]+[(nz-1)*nx+i for i in range(nx-2,-1,-1)]+[j*nx for j in range(nz-2,0,-1)]
 lower=len(vs)
 for i in rim:vs.append((vs[i][0],y+.004,vs[i][2]))
 center=len(vs);vs.append((x,y+.004,z+.006))
 for i,a in enumerate(rim):
  ni=(i+1)%len(rim);b=rim[ni];fs.extend([(a,b,lower+ni,lower+i),(center,lower+i,lower+ni)]);white.extend([False,False])
 shell=mesh('Sculpted_Mouse_With_Click_Panels',vs,fs,'Dark',0,True);shell.data.materials.append(c.b.mats['Coat'])
 for face,col in zip(shell.data.polygons,white):face.material_index=1 if col else 0
 cyl('Scroll_Wheel',(x-.0035,y+.033,z-.014),(x+.0035,y+.033,z-.014),.007,'Rubber',20)
 for i in range(9):
  a=math.pi*i/8;cyl('Wheel_Rib',(x-.004,y+.033+.0072*math.sin(a),z-.014+.0072*math.cos(a)),(x+.004,y+.033+.0072*math.sin(a),z-.014+.0072*math.cos(a)),.0006,'Steel',6)
 cyl('Cable_Strain_Relief',(x,y+.013,z-.044),(x,y+.013,z-.062),.0035,'Rubber',12)
 for zz in [z+.006,z+.022]:box('Thumb_Button',x+.029,y+.017,zz,.004,.006,.013,'Steel',.001)
 mark('mouse',x,z,.062,.112,y)
def monitor(x,y,z,tile=0,w=.58):
 h=w*.5625
 box('Monitor_Back_Shell',x,y,z-.018,w+.032,h+.034,.042,'Dark',.009)
 box('LCD_Recess',x,y,z+.005,w+.007,h+.008,.006,'Rubber',.001)
 print_front('Display',x,y,z+.0085,w,h,tile)
 box('Lower_Bezel',x,y-h/2-.009,z+.009,w+.022,.014,.012,'Coat',.002)
 cyl('Power_Light',(x-w*.42,y-h/2-.009,z+.015),(x-w*.42,y-h/2-.009,z+.017),.002,'Indicator',10)
 for i in range(11):box('Rear_Vent',x+(i-5)*.025,y+h*.22,z-.040,.017,.024,.002,'Rubber',.0003)
 box('VESA_Cover',x,y,z-.045,.09,.09,.012,'Steel',.003)
 cyl('Tilt_Hinge',(x-.035,y-.035,z-.05),(x+.035,y-.035,z-.05),.018,'Steel',16)
def monitor_on(x,top,z,tile=0,w=.58):
 y=top+.31
 monitor(x,y,z,tile,w);box('Monitor_Foot',x,top+.012,z-.025,.25,.024,.19,'Steel',.009)
 box('Monitor_Stem',x,top+.155,z-.055,.032,.285,.032,'Steel',.006)
 tube('Display_Lead',[(x,top+.27,z-.045),(x+.025,top+.20,z-.07),(x+.025,top+.025,z-.09),(x+.035,top+.003,z-.13)],.002,'Dark')
 mark('monitor',x,z,w+.032,.22,top)
def book(x,y,z,kind=10,yaw=0,opened=False):
 def build():
  w=.31 if not opened else .39;dep=.245
  box('Report_Cover',0,.003,0,w,.006,dep,'Teal' if kind%2 else 'Warm',.002)
  box('Page_Block',0,.010,0,w-.012,.008,dep-.012,'Paper',.001)
  print_top('Readable_Record',0,.0145,0,w-.018,dep-.018,kind)
  if opened:box('Binding_Crease',0,.015,0,.004,.001,dep-.012,'Dark',0)
 group(build,x,y,z,yaw);mark('document',x,z,.40 if opened else .32,.26,y)
def pen(x,y,z,yaw=0):
 def build():
  cyl('Pen_Barrel',(0,.005,-.06),(0,.005,.045),.004,'Teal',12);cyl('Pen_Nib',(0,.005,.045),(0,.005,.057),.0015,'Steel',10);box('Pen_Clip',.003,.009,-.039,.003,.003,.031,'Steel',.0005)
 group(build,x,y,z,yaw)
def cup(x,y,z,handle=True):
 # Revolved wall and real open interior, no capped cylinder masquerading as a cup.
 n=32;profile=[(.029,0),(.035,.008),(.038,.093),(.036,.099),(.032,.098),(.029,.014),(0,.014)];vs=[];fs=[]
 for rr,yy in profile:
  for i in range(n):a=math.tau*i/n;vs.append((x+rr*math.cos(a),y+yy,z+rr*math.sin(a)))
 for j in range(len(profile)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
 fs.append(tuple(range(n-1,-1,-1)));mesh('Open_Ceramic_Cup',vs,fs,'Paper',0,True)
 if handle:tube('Cup_Handle',[(x+.032+.028*math.sin(math.pi*i/16),y+.05+.031*math.cos(math.pi*i/16),z) for i in range(17)],.006,'Paper')
 cyl('Drink_Surface',(x,y+.066,z),(x,y+.067,z),.030,'Warm',32)
 mark('cup',x,z,.12,.08,y)
def tray(x,y,z,tile=11):
 box('Document_Tray',x,y+.006,z,.34,.012,.26,'Steel',.003)
 for xx in [x-.165,x+.165]:box('Tray_Side',xx,y+.031,z,.010,.05,.26,'Steel',.002)
 box('Tray_Back',x,y+.031,z-.125,.32,.05,.01,'Steel',.002)
 for j in range(3):box('Received_Envelope',x+j*.004,y+.014+j*.002,z+j*.002,.285,.002,.20,'Paper',.0003)
 print_top('Intake_Form',x+.008,y+.0195,z+.004,.28,.194,tile)
def telephone(x,y,z):
 box('Phone_Base',x,y+.025,z,.16,.05,.205,'Dark',.009)
 box('Phone_Status',x,y+.053,z-.045,.10,.005,.036,'Lens',.001)
 for j in range(4):
  for i in range(3):
   xx=x+(i-1)*.027;zz=z+.002+j*.025;box('Phone_Key',xx,y+.055,zz,.019,.008,.017,'Dark',.002)
   if j==3 and i!=1:continue
   label=str(1+j*3+i) if j<3 else '0';index=labels.index(label);u0=(index%16*64+3)/1024;u1=(index%16*64+61)/1024;v0=1-(index//16*64+61)/1024;v1=1-(index//16*64+3)/1024
   quad('Dial_Number',[(xx+.004,y+.0594,zz-.004),(xx-.004,y+.0594,zz-.004),(xx-.004,y+.0594,zz+.004),(xx+.004,y+.0594,zz+.004)],[(u0,v1),(u1,v1),(u1,v0),(u0,v0)],'KeyLegend')
 handle=[(x-.073,y+.065,z-.08)]+[(x-.048+.025*math.cos(math.pi-i*math.pi/12),y+.085+.025*math.sin(math.pi-i*math.pi/12),z-.08) for i in range(7)]+[(x+.048+.025*math.cos(math.pi/2-i*math.pi/12),y+.085+.025*math.sin(math.pi/2-i*math.pi/12),z-.08) for i in range(7)]+[(x+.073,y+.065,z-.08)]
 tube('Handset',handle,.010,'Rubber')
 tube('Coiled_Phone_Cord',[(x+.085+.008*math.cos(i*.9),y+.008+.004*math.sin(i*.9),z-.08+i*.002) for i in range(60)],.0018,'Dark')
def cables(kx,top,kz,mx,mz,pc=True):
 gx=.66;gz=-.32
 cyl('Cable_Grommet',(gx,top+.0005,gz),(gx,top+.004,gz),.022,'Steel',24);cyl('Grommet_Insert',(gx,top+.0041,gz),(gx,top+.0048,gz),.018,'Rubber',24)
 tube('Keyboard_USB',[(kx+.05,top+.012,kz-.080),(kx+.05,top+.004,kz-.12),(.29,top+.003,-.08),(.33,top+.003,-.355),(gx,top+.003,gz)],.0017,'Dark')
 tube('Mouse_USB',[(mx,top+.013,mz-.058),(mx,top+.004,mz-.12),(mx-.065,top+.003,-.12),(mx-.065,top+.003,-.35),(.25,top+.003,-.365),(gx,top+.003,gz-.008)],.0017,'Dark')
 if pc:
  tube('Underdesk_USB',[(gx,top,gz),(gx,.70,gz),(.69,.58,-.30),(.62,.42,-.27),(.57,.42,-.245)],.0023,'Dark')
  box('USB_Port',.57,.42,-.244,.03,.016,.009,'Steel',.001);box('USB_Plug',.57,.42,-.256,.025,.012,.019,'Dark',.002)
def document_stand(x,y,z):
 box('Document_Stand_Foot',x,y+.008,z,.30,.016,.25,'Steel',.006)
 vs=[(x+a,y+yy,z+zz) for a,yy,zz in [(-.15,.018,.12),(.15,.018,.12),(.15,.31,-.08),(-.15,.31,-.08),(-.15,.018,.11),(.15,.018,.11),(.15,.31,-.09),(-.15,.31,-.09)]]
 mesh('Sloped_Document_Back',vs,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'Teal',.003)
 ob=quad('Standing_Record',[(x+.14,y+.30,z-.069),(x-.14,y+.30,z-.069),(x-.14,y+.035,z+.115),(x+.14,y+.035,z+.115)],atlas_uv(12),'Print')
 if ob.data.polygons[0].normal.z<0:ob.data.flip_normals()
 box('Page_Ledge',x,y+.023,z+.125,.30,.018,.025,'Steel',.003)
def file_sorter(x,y,z):
 box('Sorter_Base',x,y+.008,z,.31,.016,.25,'Steel',.004)
 for i in range(4):box('Sorter_Divider',x+(i-1.5)*.093,y+.095,z,.009,.18,.25,'Teal',.003)
 for i in range(3):
  xx=x+(i-1)*.093;box('Standing_File',xx,y+.11,z,.035,.20,.215,'Warm' if i%2 else 'Paper',.003);box('File_Tab',xx,y+.217,z+.07,.035,.014,.055,'Paper',.002)
def desk(v):
 reset();base('BL_ResearchDesk',.8225);top=.823
 kx=[.00,-.04,.05,-.02,.035,-.05][v%6];kz=.205 if v%3==1 else .18;mx=kx-.405;mz=kz+([.006,-.018,.024][v%3]);screen=[0,1,2,3,4,6][v%6]
 monitor_on(kx+(v%3-1)*.025,top,-.20,screen,.55 if v%4==1 else .59);keyboard(kx,top,kz,(v%3-1)*2);mouse(mx,top,mz);cables(kx,top,kz,mx,mz)
 if v==4:document_stand(.49,top,.08);pen(.72,top,.12,-6)
 elif v==10:file_sorter(.49,top,.05);pen(.72,top,.15,14)
 elif v==6:telephone(.49,top,.08);box('Memo_Pad',.69,top+.006,.20,.10,.012,.13,'Paper',.002);pen(.72,top,.01,4)
 elif v==7:
  tray(.49,top,.09,11);tray(.49,top+.09,.09,14)
  for xx in [.34,.64]:box('Tray_Stack_Support',xx,top+.055,-.025,.012,.11,.016,'Steel',.002)
 elif v%3==0:book(.48,top,.105,10+(v%6),yaw=7,opened=True)
 elif v%3==1:tray(.49,top,.09,11);pen(.72,top,.12,-6)
 else:book(.50,top,.12,10+(v%6),yaw=-8);pen(.72,top,.13,14)
 if v%4 in [0,1]:cup(.69,top,.29,handle=v%2==0)
 elif v%4==2:box('Personal_Card',.70,top+.002,.29,.11,.004,.065,'Warm',.004)
 if v%4==3:box('Index_Tabs',.71,top+.006,.28,.08,.012,.07,'Paper',.003)
 save('DP_Desk_'+str(v).zfill(2))
def security(letter):
 reset();base('SF_SC_OperatorDesk_'+letter,.8225);top=.823
 monitor_on(.38,top,-.22,5,.69);monitor_on(-.38,top,-.22,4 if letter=='A' else 6,.69)
 keyboard(.03,top,.21);mouse(-.38,top,.23);cables(.03,top,.21,-.38,.23)
 telephone(.75,top,.15 if letter=='A' else .02)
 if letter=='B':book(.55,top,.28,15,yaw=5)
 else:box('Access_Card_Reader',-.75,top+.023,.22,.12,.046,.17,'Teal',.009);box('Card_Slot',-.75,top+.047,.19,.08,.003,.006,'Dark',0)
 save('DP_Security_'+letter)
def review(room):
 reset();base('SF_SC_IncidentReview',.815);top=.8155
 monitor_on(-.10,top,-.20,3 if room=='C03' else 6,.59);keyboard(-.03,top,.19);mouse(-.43,top,.19);cables(-.03,top,.19,-.43,.19,False)
 tray(.50,top,.09,14 if room=='C03' else 15);pen(.75,top,.20,12)
 save('DP_Review_'+room)
def comparison(name,i):
 reset();base('SF_BriefingTable',.805);top=.8055
 if i!=1:monitor_on(0,top,-.40,2 if i!=2 else 4,.55)
 book(.42 if i%2==0 else .15,top,.18,10+i%6,yaw=10,opened=True);book(-.44,top,-.02 if i%2 else .20,14-i%3,yaw=-9)
 pen(-.68,top,.22,18);pen(.69,top,.12,-9)
 if i%2:tray(.52,top,-.36,11)
 else:cup(.69,top,-.22)
 save(name)
def meeting():
 reset();base('BL_ConferenceTable',.7925);top=.793
 for i,(x,z,angle) in enumerate([(-1.35,.47,4),(0,.47,-6),(1.35,.47,0),(-1.35,-.47,177),(.08,-.47,186),(1.35,-.47,180)]):
  if i in [0,3,4]:group(lambda:book(0,top,0,13 if i!=4 else 12,opened=i==0),x,0,z,angle)
  elif i==1:group(lambda:book(0,top,0,15),x,0,z,angle)
  else:box('Closed_Notebook',x,top+.011,z,.25,.022,.27,'Warm' if i==2 else 'Teal',.004)
  if i!=5:pen(x+.19,top,z,angle+13)
 cup(-1.78,top,.42);cup(1.77,top,-.40)
 for x in [-.65,.65]:box('Cable_Lid',x,top+.003,0,.31,.006,.13,'Dark',.003)
 save('DP_Meeting')
def plate(x,y,z):
 n=32;vs=[];fs=[];profile=[(0,0),(.074,.002),(.10,.009),(.108,.016),(.105,.020),(.095,.017),(.071,.006),(0,.006)]
 for r,yy in profile:
  for i in range(n):a=math.tau*i/n;vs.append((x+r*math.cos(a),y+yy,z+r*math.sin(a)))
 for j in range(len(profile)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
 mesh('Ceramic_Plate',vs,fs,'Paper',0,True)
def dining(v):
 reset();base('BL_DiningSet',.7925,True);top=.793
 seats=[(-.48,.21,0),(.48,.21,0),(-.48,-.21,180),(.48,-.21,180)]
 for i,(x,z,yaw) in enumerate(seats):
  if (i+v)%4==0:continue
  def setting():
   plate(0,top,0);cup(.16,top,-.025,False);box('Folded_Napkin',-.155,top+.002,0,.075,.004,.15,'Paper',.001)
   cyl('Spoon_Handle',(-.15,top+.008,-.04),(-.15,top+.008,.058),.003,'Steel',10)
   box('Spoon_Bowl',-.15,top+.009,-.052,.021,.005,.032,'Steel',.008)
  group(setting,x+(v-1.5)*.008,0,z,yaw+(v-i)*2)
 if v==0:book(.0,top,0,15,yaw=8)
 elif v==1:box('Napkin_Dispenser',0,top+.045,0,.17,.09,.14,'Coat',.012)
 elif v==2:cup(0,top,0)
 save('DP_Dining_'+str(v))
def radio(room):
 reset();base('SF_SC_RadioDutyStation',.95);top=.9505
 for i in range(4):
  x=(i-1.5)*.28;box('Charging_Dock',x,top+.018,-.12,.14,.036,.15,'Dark',.007)
  if i==(1 if room=='E01' else 2):continue
  box('Radio_Body',x,top+.14,-.12,.075,.22,.052,'Dark',.012);box('Radio_Display',x,top+.19,-.091,.052,.035,.005,'Lens',.002)
  cyl('Radio_Antenna',(x+.022,top+.24,-.12),(x+.022,top+.41,-.12),.004,'Rubber',12)
  for j in range(4):box('Speaker_Slot',x,top+.12+j*.008,-.091,.045,.003,.003,'Steel',.0002)
  for j in range(3):
   for k in range(2):box('Radio_Button',x+(k-.5)*.025,top+.07+j*.014,-.09,.015,.008,.004,'Coat',.001)
 book(.22 if room=='E01' else -.23,top,.17,15,yaw=3 if room=='E01' else -8);pen(-.34 if room=='E01' else .35,top,.18,8)
 save('DP_Radio_'+room)
def cart(kind):
 reset();ob=base('SF_'+kind)
 # Replace only old optical-face material with an appropriate clinic display.
 for m,mat in enumerate(list(ob.data.materials)):
  path=matpaths[mat.name]
  if 'Display' in path:
   ob.data.materials[m]=c.b.mats['ScreenPrint']
   uv=ob.data.uv_layers.active;tile=7 if kind=='VitalCart' else 8
   for face in ob.data.polygons:
    if face.material_index==m:
     for li in face.loop_indices:
      old=uv.data[li].uv.copy();uv.data[li].uv=((tile%4+old.x)/4,(3-tile//4+old.y)/4)
 top=1.0905
 box('Clinical_Control_Panel',0,top+.018,.10,.33,.036,.25,'Coat',.007)
 for j in range(3):
  for i in range(5):box('Clinical_Key',-.09+i*.035,top+.040,.07+j*.034,.023,.008,.020,'Dark',.003)
 if kind=='UltrasoundCart':
  cyl('Trackball_Socket',(.105,top+.039,.06),(.105,top+.044,.06),.025,'Dark',24)
  bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.021,location=c.xyz(.105,top+.044,.06));bpy.context.object.name='Trackball';bpy.context.object.data.materials.append(c.b.mats['Coat'])
  box('Probe_Cradle',-.21,top+.014,.08,.07,.028,.16,'Dark',.008);box('Probe_Grip',-.21,top+.045,.07,.038,.035,.12,'Coat',.010)
  tube('Probe_Lead',[(-.21,top+.045,.01),(-.27,1.02,-.03),(-.27,.75,-.04),(-.18,.66,-.09)],.0035,'Rubber')
 else:
  box('Folded_Pressure_Cuff',0,.776,0,.24,.025,.18,'Fabric',.01)
  tube('Cuff_Hose',[(.11,.77,0),(.23,.73,.06),(.23,.94,.08),(.19,1.05,.03)],.003,'Rubber')
 save('DP_'+kind)
def recorder():
 reset();box('Recorder_Case',0,.026,0,.10,.052,.19,'Dark',.010);box('Recorder_Bezel',0,.054,-.025,.075,.006,.082,'Steel',.002);print_top('Memo_Screen',0,.0575,-.025,.067,.074,9)
 for x in [-.026,0,.026]:cyl('Playback_Key',(x,.052,.043),(x,.059,.043),.008,'Coat',16)
 for i in range(6):box('Microphone_Grille',-.03+i*.012,.054,-.077,.005,.003,.018,'Steel',.0005)
 box('Record_Key',.038,.054,.074,.014,.008,.016,'Red',.003);box('USB_Socket',0,.027,.095,.022,.008,.002,'Steel',.001)
 save('DP_Recorder')
def save(name):
 src=[o for o in bpy.context.scene.objects if o.type=='MESH'];res=[];dep=bpy.context.evaluated_depsgraph_get()
 for o in src:
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep);ob=bpy.data.objects.new(o.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy()
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  if not me.uv_layers:me.uv_layers.new(name='UVMap')
  if not o.get('display_uv'):
   for p in me.polygons:
    wn=ob.matrix_world.to_3x3()@p.normal;axes=[i for i in range(3) if i!=max(range(3),key=lambda k:abs(wn[k]))]
    for li in p.loop_indices:
     v=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;me.uv_layers.active.data[li].uv=(v[axes[0]]/3,v[axes[1]]/3)
  res.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for o in res:o.select_set(True)
 bpy.context.view_layer.objects.active=res[0];bpy.ops.object.join();o=bpy.context.object;o.name=name+'_LOD0';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 # Explicitly discard zero-area cap centres from revolved cups/plates.
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-12],context='FACES');bm.to_mesh(o.data);bm.free()
 counts=[len(o.data.polygons)];verts=[(-v.co.x,v.co.z,-v.co.y) for v in o.data.vertices];lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 for level,ratio in [(1,.47),(2,.18)]:
  ob=o.copy();ob.data=o.data.copy();bpy.context.collection.objects.link(ob);ob.name=name+'_LOD'+str(level);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Distant_Detail','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name);ob.select_set(True);counts.append(len(ob.data.polygons))
 out=U/'Assets/Afrer_Seconds/05.Model/Props/B1'/(name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
 manifest[name]={'asset':out.relative_to(U).as_posix(),'triangles':counts,'center':[(hi[i]+lo[i])/2 for i in range(3)],'size':[hi[i]-lo[i] for i in range(3)],'materials':{m.name:matpaths[m.name] for m in o.data.materials},'features':list(details)}
 (H/'models.json').write_text(json.dumps(manifest,indent=2));print('SAVED',name,counts,flush=True)
def wanted(n):return not only or n in only
for v in range(12):
 if wanted('DP_Desk_'+str(v).zfill(2)):desk(v)
for letter in ['A','B']:
 if wanted('DP_Security_'+letter):security(letter)
for room in ['C03','S01']:
 if wanted('DP_Review_'+room):review(room)
names=sorted({q['variant'] for q in plan['targets'] if q['variant'].startswith('DP_Comparison')})
for i,name in enumerate(names):
 if wanted(name):comparison(name,i)
if wanted('DP_Meeting'):meeting()
for v in range(4):
 if wanted('DP_Dining_'+str(v)):dining(v)
for room in ['E01','E03']:
 if wanted('DP_Radio_'+room):radio(room)
for kind in ['VitalCart','UltrasoundCart']:
 if wanted('DP_'+kind):cart(kind)
if wanted('DP_Recorder'):recorder()
(H/'retained_geometry.json').write_text(json.dumps(basecounts,indent=2))
print('COMPLETE',len(manifest),flush=True)
