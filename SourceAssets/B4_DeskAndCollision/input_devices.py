"""Right-handed TKL workstation; local source X is reversed by the FBX convention."""
import bpy,math,json
from mathutils import Vector
from pathlib import Path
def build(c,H):
 b=c.b;box=c.box;cyl=c.cyl;labels=[]
 mat=bpy.data.materials.new('PD_KeyLegend');mat.diffuse_color=(.75,.77,.78,1);b.mats['KeyLegend']=mat
 def wire(n,points,r=.0018,mat='Dark'):
  cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=2
  sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
  coords=[Vector(b.xyz(*co)) for co in points]
  for p,co in zip(sp.bezier_points,coords):p.co=co;p.handle_left_type='FREE';p.handle_right_type='FREE'
  for i,p in enumerate(sp.bezier_points):
   prev=coords[max(i-1,0)];nxt=coords[min(i+1,len(coords)-1)];tangent=(nxt-prev).normalized();left=coords[i]-tangent*(coords[i]-prev).length/3;right=coords[i]+tangent*(nxt-coords[i]).length/3
   for axis in range(3):left[axis]=max(min(prev[axis],coords[i][axis]),min(max(prev[axis],coords[i][axis]),left[axis]));right[axis]=max(min(nxt[axis],coords[i][axis]),min(max(nxt[axis],coords[i][axis]),right[axis]))
   p.handle_left=left;p.handle_right=right
  ob=bpy.data.objects.new(n,cu);bpy.context.collection.objects.link(ob);cu.materials.append(b.mats[mat]);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
  for p in ob.data.polygons:p.use_smooth=True
  ob.select_set(False)
 def legend(label,x,y,z,w,d):
  if label not in labels:labels.append(label)
  i=labels.index(label);col=i%16;row=i//16;u0=(col*64+3)/1024;u1=(col*64+61)/1024;v0=1-(row*64+61)/1024;v1=1-(row*64+3)/1024
  ob=c.mesh('Key_Legend',[(x+w/2,y,z-d/2),(x-w/2,y,z-d/2),(x-w/2,y,z+d/2),(x+w/2,y,z+d/2)],[(0,1,2,3)],'KeyLegend',0)
  uv=ob.data.uv_layers.new(name='UVMap');coords=[(u0,v1),(u1,v1),(u1,v0),(u0,v0)]
  for p in ob.data.polygons:
   for li in p.loop_indices:uv.data[li].uv=coords[ob.data.loops[li].vertex_index]
  ob['display_uv']=True
 # 87-key tenkeyless proportions, staggered rows and real wide modifiers.
 kc=.08;kz=.385;w=.378;d=.158;pitch=.0193;left=-w/2+.012
 box('Keyboard_Lower_Shell',kc,.923,kz,w,.016,d,'Dark',.006)
 box('Keyboard_Upper_Frame',kc,.934,kz,w-.003,.010,d-.003,'Steel',.004)
 for xx in [kc-.14,kc+.14]:
  for zz in [kz-.052,kz+.052]:box('Keyboard_Foot',xx,.917,zz,.027,.004,.018,'Rubber',.001)
 def key(label,u,z,units=1,depth=.017,height=.010):
  x=kc-(left+(u+units/2)*pitch);ww=units*pitch-.0020
  box('Keycap_'+label.replace('/','Slash'),x,.944,z,ww,height,depth,'Coat',.0016)
  legend(label,x,.944+height/2+.00045,z,min(ww-.003,.023 if len(label)>2 else .010),.010 if len(label)>2 else .011)
 def row(items,z):
  u=0
  for label,width in items:key(label,u,z,width);u+=width
 rows=[
  [('`',1)]+[(str(i),1) for i in [1,2,3,4,5,6,7,8,9,0]]+[('-',1),('=',1),('Back',2)],
  [('Tab',1.5)]+[(k,1) for k in 'QWERTYUIOP']+[('[',1),(']',1),('\\',1.5)],
  [('Caps',1.75)]+[(k,1) for k in 'ASDFGHJKL']+[(';',1),("'",1),('Enter',2.25)],
  [('Shift',2.25)]+[(k,1) for k in 'ZXCVBNM']+[(',',1),('.',1),('/',1),('Shift',2.75)],
  [('Ctrl',1.25),('Win',1.25),('Alt',1.25),('Space',6.25),('Alt',1.25),('Fn',1.25),('Menu',1.25),('Ctrl',1.25)]
 ]
 for n,items in enumerate(rows):row(items,.339+n*.023)
 key('Esc',0,.317,1,depth=.012,height=.008)
 for i in range(12):key('F'+str(i+1),2+i+(i//4)*.34,.317,.90,depth=.012,height=.008)
 for n,label in enumerate(['Ins','Home','PgUp']):key(label,15.45+n,.339,1)
 for n,label in enumerate(['Del','End','PgDn']):key(label,15.45+n,.362,1)
 key('Up',16.45,.408,1)
 for n,label in enumerate(['Left','Down','Right']):key(label,15.45+n,.431,1)
 for xx in [-.083,-.063]:cyl('Keyboard_Status_LED',(xx,.940,.449),(xx,.942,.449),.0015,'Indicator',10)
 # Source -X becomes the user's right side. A domed palm shell replaces the cube mouse.
 mx=-.43;mz=.390
 box('Mouse_Mat',mx,.918,mz,.17,.004,.20,'Rubber',.005)
 vs=[];fs=[];N=32
 for y,rx,rz,shift in [(0,.026,.046,0),(.005,.031,.054,0),(.015,.030,.052,.003),(.026,.024,.043,.008),(.033,.013,.025,.012),(.035,.001,.001,.013)]:
  for i in range(N):a=math.tau*i/N;vs.append((mx+rx*math.cos(a),.922+y,mz+shift+rz*math.sin(a)))
 for j in range(5):
  for i in range(N):a=j*N+i;bb=j*N+(i+1)%N;fs.append((a,bb,bb+N,a+N))
 fs.extend([tuple(range(N-1,-1,-1)),tuple(5*N+i for i in range(N))])
 c.mesh('Curved_Mouse_Shell',vs,fs,'Dark',0,True)
 def top(z):return .935+.022*math.sqrt(max(0,1-((z-mz-.008)/.057)**2))
 wire('Mouse_Button_Split',[(mx,top(z)+.0006,z) for z in [mz-.045,mz-.037,mz-.024,mz-.011]],.0006,'Steel')
 wire('Palm_Button_Seam',[(mx-.023,.947,mz-.008),(mx-.012,.954,mz-.006),(mx,.956,mz-.006),(mx+.012,.954,mz-.006),(mx+.023,.947,mz-.008)],.0005,'Steel')
 cyl('Rubber_Scroll_Wheel',(mx-.0037,.954,mz-.024),(mx+.0037,.954,mz-.024),.007,'Rubber',20)
 # Cable grommet, rear PC ports and moulded connector boots.
 gx=-.33;gz=-.57
 cyl('Desk_Grommet_Rim',(gx,.915,gz),(gx,.919,gz),.027,'Steel',32)
 cyl('Grommet_Rubber_Insert',(gx,.919,gz),(gx,.920,gz),.023,'Dark',32)
 ports={'Keyboard':(-.74,.978,-.575),'Mouse':(-.69,.978,-.575),'Display':(-.60,1.039,-.575),'Power':(-.54,1.039,-.575)}
 for name,(x,y,z) in ports.items():
  box('Rear_'+name+'_Socket',x,y,z-.004,.028 if name!='Power' else .026,.015,.012,'Steel',.001)
  box(name+'_Plug',x,y,z-.016,.024,.012,.022,'Dark',.002)
  cyl(name+'_Strain_Relief',(x,y,z-.028),(x,y,z-.041),.0032 if name!='Power' else .004,'Dark',12)
 # All wires are continuous to real ports. Most length follows the rear raceway.
 wire('Keyboard_USB',[(.035,.928,.305),(.035,.923,.265),(-.09,.9175,.214),(-.24,.9175,.08),(-.30,.9175,-.30),(gx+.005,.9175,gz+.035),(gx+.005,.88,gz),(-.32,.78,-.59),(-.57,.78,-.71),(-.73,.88,-.71),(-.74,.978,-.626),(-.74,.978,-.616)])
 wire('Mouse_USB',[(mx,.937,mz-.054),(mx,.924,.28),(-.45,.9175,.20),(-.40,.9175,.08),(-.355,.9175,-.16),(gx-.005,.9175,gz+.030),(gx-.005,.88,gz),(-.34,.785,-.60),(-.55,.785,-.72),(-.68,.87,-.72),(-.69,.978,-.626),(-.69,.978,-.616)])
 wire('Display_Data',[ (0,1.176,-.514),(0,1.154,-.548),(-.14,1.04,-.60),(-.35,.945,-.635),(-.52,.98,-.64),(-.60,1.039,-.626),(-.60,1.039,-.616)],.0025)
 wire('Display_Power',[(-.086,1.176,-.514),(-.10,1.13,-.55),(-.17,.98,-.615),(-.235,.91,-.71),(-.235,.81,-.71),(-.22,.783,-.50)],.0028)
 wire('PC_Power',[(-.54,1.039,-.616),(-.54,1.015,-.642),(-.47,.92,-.71),(-.38,.82,-.71),(-.36,.783,-.50)],.0028)
 box('Underdesk_Power_Strip',-.30,.747,-.49,.42,.065,.075,'Dark',.005)
 for xx in [-.36,-.22]:box('Power_Plug',xx,.783,-.49,.046,.022,.046,'Dark',.003)
 for xx in [-.5,-.3,-.1]:box('Cable_Retaining_Clip',xx,.77,-.60,.028,.05,.05,'Dark',.003)
 (H/'key_labels.json').write_text(json.dumps(labels),encoding='utf8')
