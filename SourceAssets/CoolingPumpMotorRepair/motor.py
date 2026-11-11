"""규칙적인 모터 하우징·방열핀·원형 연결부 V0.01 · 송예찬.
rebuild.py의 Blender 환경에서 실행한다. LOD별 곡면 분할만 줄이고 핀 간격은 유지한다.
"""
def build_motor(level):
 objects=[];segments=32 if level==0 else 16
 def prepare(ob,mat=1,edge=.001):
  weld(ob.data);finish_uv(ob)
  for p in ob.data.polygons:p.material_index=mat
  if edge and level==0:bevel(ob,edge,1)
  objects.append(ob);return ob
 def cuboid(name,center,size,mat=1,edge=.0015,angle=None):
  bpy.ops.mesh.primitive_cube_add(size=1,location=center);ob=bpy.context.object;ob.name=name;ob.dimensions=size
  if angle is not None:ob.rotation_euler.x=angle
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
  for m in [steel,aligned,orange,dark]:ob.data.materials.append(m)
  for u in list(ob.data.uv_layers):ob.data.uv_layers.remove(u)
  return prepare(ob,mat,edge)
 def tube(name,center,axis,length,outer,inner=0,mat=1,n=None,edge=0):
  n=n or segments;axis=Vector(axis).normalized();u=axis.cross(Vector((0,0,1))) if abs(axis.z)<.9 else axis.cross(Vector((0,1,0)));u.normalize();v=axis.cross(u);center=Vector(center);verts=[]
  rings=[(-length/2,outer),(length/2,outer)]
  if inner>0:rings += [(-length/2,inner),(length/2,inner)]
  for along,r in rings:
   for i in range(n):verts.append(center+axis*along+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n)))
  faces=[]
  for i in range(n):
   j=(i+1)%n;faces.append((i,j,n+j,n+i))
   if inner>0:faces += [(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]
  if inner==0:faces += [tuple(reversed(range(n))),tuple(range(n,2*n))]
  return prepare(mesh_obj(name,verts,faces),mat,edge)
 # Motor shaft and bearing flanges, all on one horizontal X axis.
 z=.454
 tube('Motor_CouplingNeck',(-.116,0,z),(1,0,0),.072,.115)
 tube('Motor_FrontBearing',(-.172,0,z),(1,0,0),.062,.184)
 tube('Motor_FrontSeal',(-.205,0,z),(1,0,0),.010,.171,mat=3,edge=0)
 tube('Motor_CylindricalHousing',(-.399,0,z),(1,0,0),.396,.161)
 tube('Motor_RearShoulder',(-.598,0,z),(1,0,0),.022,.180)
 tube('Motor_FanShroud',(-.665,0,z),(1,0,0),.128,.207)
 # 26 straight axial fins. Leave symmetric space for terminal box and mounting feet.
 fin_count=0
 for i in range(32):
  theta=i*math.tau/32
  if abs(math.sin(theta))>.94:continue
  radial=Vector((0,math.cos(theta),math.sin(theta)));tangent=Vector((0,-math.sin(theta),math.cos(theta)))
  verts=[]
  for x in [-.589,-.215]:
   for r,t in [(.158,-.003),(.198,-.003),(.198,.003),(.158,.003)]:verts.append(Vector((x,0,z))+radial*r+tangent*t)
  faces=[(0,3,2,1),(4,5,6,7)]+[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)]
  prepare(mesh_obj('Motor_Fin_'+str(i).zfill(2),verts,faces),1,.0007);fin_count+=1
 # Four feet and two machined mounting pads, resting on the existing repaired skid.
 for x in [-.255,-.535]:
  cuboid('Motor_MountingPad',(x,0,.190),(.132,.422,.020),edge=.002)
  for y in [-.137,.137]:
   cuboid('Motor_MountingFoot',(x,y,.290),(.078,.070,.200),edge=.002)
   tube('Motor_AnchorBolt',(x,y*1.32,.204),(0,0,1),.010,.011,n=6,edge=.0005)
 # Terminal box with a separate lid and four screws, no distorted generated lettering.
 cuboid('Motor_TerminalBox',(-.323,0,.686),(.204,.215,.115),edge=.006)
 cuboid('Motor_TerminalLid',(-.323,0,.752),(.222,.233,.018),edge=.003)
 for x in [-.409,-.237]:
  for y in [-.089,.089]:tube('Terminal_LidScrew',(x,y,.765),(0,0,1),.006,.006,n=6,edge=.0004)
 # Circular side connector: cylindrical neck, gasket, orange annulus, equally spaced bolts.
 tube('Side_PortNeck',(-.385,-.204,.424),(0,1,0),.112,.078,.062,n=segments)
 tube('Side_PortGasket',(-.385,-.264,.424),(0,1,0),.010,.107,.057,mat=3,edge=0)
 tube('Side_PortFlange',(-.385,-.281,.424),(0,1,0),.026,.106,.057,mat=2)
 tube('Side_PortBore',(-.385,-.262,.424),(0,1,0),.046,.061,.055,mat=3,edge=0)
 tube('Side_PortRecess',(-.385,-.238,.424),(0,1,0),.004,.055,mat=3,edge=0)
 for i in range(6):
  a=i*math.tau/6;x=-.385+.084*math.cos(a);zz=.424+.084*math.sin(a)
  tube('Side_FlangeBolt',(x,-.299,zz),(0,1,0),.010,.010,n=6,edge=.0004)
 # Back fan grille: recessed dark screen, concentric rims and straight protecting spokes.
 tube('Fan_DarkScreen',(-.735,0,z),(1,0,0),.004,.192,mat=3,edge=0)
 for r in [.076,.132,.199]:tube('Fan_ConcentricGrille',(-.743,0,z),(1,0,0),.008,r,r-.005,n=segments,edge=0)
 for i in range(4):
  a=i*math.pi/4;cuboid('Fan_RadialGuard',(-.746,0,z),(.006,.394,.006),angle=a,edge=.0005)
 tube('Fan_CenterHub',(-.748,0,z),(1,0,0),.006,.029,n=24 if level==0 else 12,edge=.0006)
 # Bearing fasteners around the front housing.
 for i in range(6):
  a=i*math.tau/6;tube('Bearing_HexBolt',(-.136,.151*math.cos(a),z+.151*math.sin(a)),(1,0,0),.012,.009,n=6,edge=.0004)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();motor=bpy.context.object;motor.name='Rebuilt_Motor_LOD'+str(level);weld(motor.data)
 motor.data.calc_loop_triangles();print('MOTOR_LEVEL',level,'fins',fin_count,'triangles',len(motor.data.loop_triangles),flush=True)
 return motor
