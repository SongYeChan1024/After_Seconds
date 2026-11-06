from pathlib import Path
exec((Path(__file__).parent/'build_environment.py').read_text('utf-8').split('\nreset()\nfor i in range(6)')[0])
OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/Common'
reset()
box('Carcass',0,.65,0,.9,1.2,.55,'Dark',.012)
for x in [-.436,.436]:box('SideSkin',x,.66,0,.028,1.18,.55,'Coat',.008)
box('TopSkin',0,1.24,0,.9,.025,.55,'Coat',.008)
for y,h in [(.37,.52),(.94,.54)]:
 box('SealedDoor',0,y,.292,.85,h,.04,'Coat',.008)
 box('LabelPocket',-.20,y+.12,.318,.18,.06,.012,'Steel',.002)
 for x in [-.36,.36]:
  box('Hinge',x,y+.12,.322,.04,.12,.025,'Steel',.003)
 for x in [-.13,.13]:cyl('HandleStand',(x,y,.315),(x,y,.365),.014)
 cyl('HandleGrip',(-.13,y,.365),(.13,y,.365),.016)
 for x in [-.35,.35]:bolt(x,y-.17,.315)
for x in [-.34,.34]:
 for z in [-.18,.18]:cyl('AdjustableFoot',(x,.01,z),(x,.13,z),.025);cyl('FootPad',(x,.01,z),(x,.035,z),.046,'Dark')
export('CFD_TransferCabinet')
(H/'fallback_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

# Pipe returns connect both service-line ends into the tunnel wall.
OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Common'
base=json.loads((H/'environment_manifest.json').read_text('utf-8'))
for side,label in [(-1,'Start'),(1,'End')]:
 reset();pts=[(0,0,0)]+[(.18-.18*math.cos(math.pi*i/20),0,side*.18*math.sin(math.pi*i/20)) for i in range(1,11)]+[(.38,0,side*.18)]
 # A continuous swept tube with a rounded 90 degree bend, no miter gaps.
 vs=[];steps=20
 for j,p in enumerate(pts):
  tangent=Vector(pts[min(j+1,len(pts)-1)])-Vector(pts[max(j-1,0)]);tangent.normalize();up=Vector((0,1,0));right=tangent.cross(up).normalized()
  for k in range(steps):
   a=k*2*math.pi/steps;v=Vector(p)+.1*(math.cos(a)*up+math.sin(a)*right);vs.append(tuple(v))
 fs=[]
 for j in range(len(pts)-1):
  for k in range(steps):fs.append((j*steps+k,j*steps+(k+1)%steps,(j+1)*steps+(k+1)%steps,(j+1)*steps+k))
 fs.extend([tuple(reversed(range(steps))),tuple(range((len(pts)-1)*steps,len(pts)*steps))]);mesh('Elbow',vs,fs,'Steel',0,True)
 cyl('WallFlange',(.28,0,side*.18),(.32,0,side*.18),.155)
 for a in [math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4]:cyl('FlangeBolt',(.26,.132*math.cos(a),side*.18+.132*math.sin(a)),(.33,.132*math.cos(a),side*.18+.132*math.sin(a)),.012,verts=6)
 export('CFD_PipeReturn'+label);base['CFD_PipeReturn'+label]=manifest['CFD_PipeReturn'+label]
(H/'environment_manifest.json').write_text(json.dumps(base,indent=2),encoding='utf-8')
