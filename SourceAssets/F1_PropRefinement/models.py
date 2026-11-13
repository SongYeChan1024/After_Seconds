import sys,math,json,random,bpy
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
from mesh import Model
random.seed(1311);reports=[]
def save(m):
 reports.append(m.export());(H/'models.json').write_text(json.dumps(reports,indent=2));print('BUILT',m.name,reports[-1]['triangles'],flush=True)
def scratch(m,p,w=.16,axis='x'):
 x,y,z=p
 for i in range(4):
  a=random.uniform(-w/2,w/2);length=random.uniform(.012,.055)
  m.beam((x+a,y+i*.003,z),(x+a+length,y+i*.0035,z),.0008,'WornSteel',4)
def caster(m,x,z,r=.06,y=.06,w=.058):
 m.wheel((x,y,z),r,w,n=40)
 for side in [-1,1]:m.box((x+side*w*.60,y+r*.52,z-.009),(w*.15,r*1.35,r*.8),'Steel',.005)
 m.box((x,y+r*1.02,z-.009),(w*1.35,.014,r*.8),'Steel',.005)
 m.beam((x,y+r,z-.009),(x,y+r*1.45,z-.009),r*.4,'WornSteel',32)
 m.ring((x,y+r*1.18,z-.009),r*.43,.004,'Steel','y',32)

# Cable reel: individual circular-cut planks, hub recess, end checks and a helical winding.
m=Model('PR_CableReel')
for side in [-1,1]:
 x=side*.46
 for band in range(6):
  ymin=-.73+band*(1.46/6)+.002;ymax=-.73+(band+1)*(1.46/6)-.002
  poly=[(math.sin(i*math.tau/128)*.73,math.cos(i*math.tau/128)*.73) for i in range(128)] # y,z
  for cut,keep in [(ymin,1),(ymax,-1)]:
   clipped=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    ia=(a[0]-cut)*keep>=0;ib=(b[0]-cut)*keep>=0
    if ia:clipped.append(a)
    if ia!=ib:
     t=(cut-a[0])/(b[0]-a[0]);clipped.append((cut,a[1]+(b[1]-a[1])*t))
   poly=clipped
  n=len(poly);vv=[(x+dx,.73+y,z) for dx in [-.045,.045] for y,z in poly]
  m.add(vv,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'Wood' if band%2 else 'WoodPale')
 m.lathe((x,.73,0),[(-.046,.08),(-.046,.15),(-.05,.16),(-.056,.16),(-.056,.08)],'Steel','x',48)
 m.ring((side*.514,.73,0),.125,.014,'WornSteel','x',48)
 m.beam((side*.49,.73,0),(side*.515,.73,0),.078,'Dark',40)
 for i in range(8):
  a=i*math.tau/8;m.bolt((side*.507,.73+.5*math.sin(a),.5*math.cos(a)),.024,'x',side)
 # narrow wood checking near rim, aligned to the planks
 for j in range(10):
  y=.15+j*.12;z=math.sqrt(max(.001,.73**2-(y-.73)**2))-.018;length=random.uniform(.04,.17)
  m.curve([(side*.506,y,z),(side*.506,y+.004,z-length*.5),(side*.506,y+.001,z-length)],.0009,'WoodCrack',4,4)
m.beam((-.412,.73,0),(.412,.73,0),.49,'Dark',72)
pts=[]
for i in range(12*56+1):
 t=i/(12*56);a=t*12*math.tau;pts.append((-.377+t*.754,.73+.526*math.cos(a),.526*math.sin(a)))
m.tube(pts,.029,'Rubber',10)
# Exit from the last coil follows its tangent before sagging to the floor.
m.curve([pts[-1],(.382,1.23,.19),(.39,1.04,.43),(.398,.74,.54),(.404,.41,.58),(.39,.14,.67),(.28,.035,.80),(.04,.031,.87),(-.21,.031,.84),(-.40,.031,.69),(-.43,.031,.51)],.019,'Rubber',9,12)
m.beam((-.43,.031,.51),(-.43,.031,.46),.021,'TireDust',20)
save(m)

# Office chair: upholstered radii, piping, shells, five-star base and twin casters.
m=Model('PR_OfficeChair')
m.beam((0,.14,0),(0,.38,0),.035,'WornSteel',40);m.beam((0,.15,0),(0,.29,0),.048,'Dark',40)
for y in [.155,.185,.215,.245]:m.ring((0,y,0),.047,.004,'Rubber','y',32)
m.box((0,.41,0),(.32,.05,.27),'Dark',.018)
m.box((0,.465,0),(.52,.12,.5),'Fabric',.052);m.box((0,.422,0),(.49,.042,.47),'Dark',.019)
m.box((0,.84,-.216),(.5,.58,.085),'Fabric',.04);m.box((0,.84,-.26),(.47,.55,.025),'Dark',.012)
# Piping is a soft rounded seam rather than a square floating border.
m.curve([(-.205,.48,-.237),(-.247,.48,-.19),(-.247,.48,.18),(-.20,.48,.237),(.20,.48,.237),(.247,.48,.18),(.247,.48,-.19),(.205,.48,-.237),(-.205,.48,-.237)],.0025,'FabricWorn',5,6)
for x in [-.205,.205]:m.curve([(x,.59,-.171),(x,.68,-.169),(x,.95,-.169),(x,1.07,-.178)],.002,'FabricWorn',8,6)
m.curve([(0,.41,-.12),(0,.48,-.22),(0,.64,-.27),(0,.83,-.27)],.024,'Steel',8,12)
for x in [-.3,.3]:
 m.curve([(x*.80,.42,-.12),(x,.47,-.13),(x,.63,-.13),(x,.695,-.08)],.018,'Steel',8,12)
 m.box((x,.72,0),(.066,.045,.35),'Rubber',.021)
 m.box((x,.743,.035),(.048,.0018,.16),'TireDust',.0006)
 for y in [.65,1.04]:m.bolt((x*.63,y,-.276),.009,'z',-1)
m.curve([(.17,.405,.08),(.25,.39,.09),(.28,.39,.10)],.01,'Steel',8,10);m.box((.29,.39,.10),(.1,.022,.045),'Rubber',.01)
for i in range(5):
 a=i*math.tau/5;x=.29*math.cos(a);z=.29*math.sin(a)
 m.curve([(0,.17,0),(x*.35,.166,z*.35),(x*.8,.143,z*.8),(x,.148,z)],.022,'Steel',8,12)
 caster(m,x,z,.052,.052,.062)
save(m)

# Rolling tool cabinet: folded sheet, inset drawer gaps and real swivel mounts.
m=Model('PR_ToolCart')
for x in [-.32,.32]:
 for z in [-.23,.23]:caster(m,x,z,.075,.09,.08)
m.box((0,.51,0),(.75,.64,.57),'Green',.023)
for y in [.29,.43,.57,.71]:
 m.box((0,y,.294),(.697,.127,.02),'Dark',.006);m.box((0,y,.31),(.68,.116,.025),'Coat',.009)
 m.curve([(-.23,y,.326),(-.225,y,.357),(-.19,y,.365),(.19,y,.365),(.225,y,.357),(.23,y,.326)],.012,'WornSteel',6,10)
 m.label((-.24,y,.326),.075,.032);scratch(m,(.08,y+.05,.324),.36)
 for x in [-.30,.30]:m.bolt((x,y,.327),.005)
m.box((0,.858,0),(.79,.045,.62),'Steel',.012);m.box((0,.883,0),(.72,.008,.55),'Rubber',.005)
for x in [-.386,.386]:m.box((x,.905,0),(.026,.07,.62),'Steel',.008)
m.curve([(-.39,.76,-.32),(-.39,.94,-.32),(-.35,1.02,-.32),(.35,1.02,-.32),(.39,.94,-.32),(.39,.76,-.32)],.018,'Steel',8,12)
m.beam((-.22,1.02,-.32),(.22,1.02,-.32),.022,'TireDust',40)
m.box((-.17,.947,-.03),(.30,.12,.28),'Dark',.025);m.box((-.17,.953,.111),(.27,.005,.003),'Steel',.001)
for x in [-.27,-.07]:m.box((x,.95,.115),(.026,.041,.008),'Steel',.003);m.bolt((x,.947,.12),.004)
m.curve([(-.245,1.007,-.03),(-.24,1.055,-.03),(-.10,1.055,-.03),(-.095,1.007,-.03)],.009,'Rubber',7,10)
m.lathe((.2,.89,.06),[(0,.05),(.012,.06),(.15,.06),(.17,.045)],'Hazard','y',48)
m.beam((.2,1.055,.06),(.2,1.075,.06),.027,'Steel',24)
m.curve([(.2,1.071,.06),(.2,1.104,.08),(.2,1.12,.13),(.2,1.12,.18)],.007,'WornSteel',8,10)
save(m)

# Forklift: rounded counterweight, open overhead guard, channel mast, roller chains.
m=Model('PR_Forklift')
m.box((0,.58,-.03),(1.28,.51,2.10),'Hazard',.115)
m.box((0,.85,-.85),(1.42,.75,.52),'Green',.14)
m.box((0,.91,-.25),(1.18,.15,1.05),'Hazard',.05)
for x in [-.7,.7]:
 for z in [-.72,.72]:m.wheel((x,.31,z),.31,.22,n=72)
 # Plate steps and a formed edge instead of a closed block in the driver's opening.
 m.box((x*.86,.57,.12),(.18,.045,.43),'Steel',.015)
 for z in [-.04,.04,.12,.20,.28]:m.box((x*.86,.595,z),(.16,.006,.008),'TireDust',.002)
for x in [-.59,.59]:
 for z in [-.55,.58]:m.curve([(x,.8,z),(x,1.65,z),(x,2.20,z-.045)],.033,'Dark',3,16)
for x in [-.65,.65]:m.box((x,2.265,0),(.08,.08,1.49),'Green',.018)
for z in [-.71,.71]:m.box((0,2.265,z),(1.36,.08,.08),'Green',.015)
for x in [-.43,-.215,0,.215,.43]:m.box((x,2.28,0),(.055,.035,1.37),'Steel',.008)
m.box((0,1.11,-.23),(.65,.13,.6),'Rubber',.06);m.box((0,1.43,-.48),(.65,.6,.12),'Rubber',.055)
for x in [-.25,.25]:m.curve([(x,1.164,-.44),(x,1.174,-.2),(x,1.157,.015)],.0028,'TireDust',9,6)
m.beam((0,.94,.5),(0,1.48,.42),.035,'Dark',24);m.ring((0,1.5,.42),.205,.018,'Rubber','y',56)
for a in [0,2.1,4.2]:m.beam((0,1.5,.42),(.19*math.cos(a),1.5,.42+.19*math.sin(a)),.012,'Steel',12)
for x in [-.53,.53]:
 # U channel: two flanges and a web leave the sliding guide visible.
 m.box((x,1.65,1.04),(.14,3.15,.032),'Steel',.007)
 for xx in [x-.055,x+.055]:m.box((xx,1.65,1.12),(.027,3.15,.17),'Steel',.006)
 m.box((x,.67,1.252),(.16,.99,.08),'Dark',.012)
 for y in [.35,1.02]:
  m.beam((x-.064,y,1.15),(x+.064,y,1.15),.061,'WornSteel',32)
 # Tapered forged forks and heel radius.
 m.box((x,.61,1.34),(.15,.94,.09),'Steel',.022)
 m.curve([(x,.21,1.34),(x,.145,1.39),(x,.13,1.49)],.055,'Steel',6,12)
 m.add([(x+dx,y,z) for z,yt,yb in [(1.43,.165,.095),(2.60,.155,.104),(2.775,.128,.11)] for dx,y in [(-.075,yb),(.075,yb),(.075,yt),(-.075,yt)]],[(0,3,2,1),(8,9,10,11)]+[(j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i) for j in range(2) for i in range(4)],'WornSteel')
for y in [.35,1.05,2.5,3.1]:m.box((0,y,1.04),(1.15,.09,.09),'Steel',.009)
m.box((0,.56,1.30),(1.18,.12,.10),'Steel',.012);m.box((0,1.06,1.30),(1.18,.1,.10),'Steel',.01)
m.beam((0,.45,1.08),(0,1.88,1.08),.078,'Green',48);m.beam((0,1.86,1.08),(0,3.06,1.08),.045,'WornSteel',48)
for y in [.48,1.82]:m.ring((0,y,1.08),.08,.012,'Steel','y',40)
for x in [-.36,.36]:
 m.beam((x-.035,2.96,1.15),(x+.035,2.96,1.15),.105,'WornSteel',48)
 for i in range(28):
  y=.68+i*.079
  for xx in [x-.018,x+.018]:m.box((xx,y,1.255),(.012,.064,.037),'Steel',.008)
  m.beam((x-.025,y+.025,1.255),(x+.025,y+.025,1.255),.012,'WornSteel',12)
 chain=[(2.88,1.255)]+[(2.96+.105*math.sin(i*math.pi/8),1.15+.105*math.cos(i*math.pi/8)) for i in range(9)]+[(2.88-i*.079,1.045) for i in range(27)]
 for (y,z),(yy,zz) in zip(chain,chain[1:]):
  for xx in [x-.018,x+.018]:m.beam((xx,y,z),(xx,yy,zz),.013,'Steel',6)
  m.beam((x-.025,y,z),(x+.025,y,z),.012,'WornSteel',12)
 m.curve([(x,.54,1.0),(x+.08,.80,.92),(x+.08,2.62,.92),(x,3.04,.93),(x-.09,2.67,.93),(x-.09,1.01,.93)],.016,'Rubber',8,10)
for x in [-.43,.43]:m.box((x,1.96,.59),(.22,.15,.13),'Dark',.035);m.box((x,1.96,.66),(.17,.11,.015),'Lamp',.025)
for i in range(8):m.box((-.44+i*.126,.88,-1.112),(.066,.20,.012),'Dark',.015)
for x in [-.15,.15]:m.box((x,.91,.45),(.13,.032,.2),'TireDust',.014)
for x in [.36,.45]:m.curve([(x,.91,.1),(x,1.14,.16),(x,1.34,.28)],.013,'Steel',6,10);m.box((x,1.36,.28),(.04,.06,.045),'Rubber',.02)
m.label((.31,1.85,1.138),.19,.10)
for x in [-.51,.51]:scratch(m,(x,.825,1.025),.12)
save(m)

# Hydraulic press: machined guide shoes, ram gland, pump/manifold and fitted hoses.
m=Model('PR_Press')
m.box((0,.16,0),(3.3,.32,2.65),'Dark',.08)
for x in [-1.25,1.25]:
 m.box((x,2,0),(.48,3.8,1.7),'Green',.065)
 for y in [.52,3.48]:
  m.box((x,y,.858),(.41,.27,.025),'Steel',.012)
  for xx in [-.15,.15]:
   for yy in [-.08,.08]:m.bolt((x+xx,y+yy,.874),.023)
 for z in [-.8,.8]:m.bolt((x,.326,z),.055,'y')
for x in [-.8,.8]:
 m.beam((x,.62,.35),(x,3.44,.35),.059,'WornSteel',48)
 for y in [1.48,2.65]:m.box((x,y,.35),(.19,.21,.19),'Steel',.016);m.bolt((x,y,.453),.018)
m.box((0,3.8,0),(3.4,.65,1.9),'Green',.075)
m.box((0,1.05,.2),(2.35,.25,1.85),'Steel',.025)
m.box((0,1.27,.2),(1.15,.18,.85),'Dark',.02);m.box((0,2.45,.15),(2,.45,1.45),'Steel',.028)
for x in [-.75,-.25,.25,.75]:m.box((x,1.178,.2),(.025,.004,1.68),'Dark',.001)
m.beam((0,2.68,.15),(0,3.12,.15),.17,'WornSteel',64)
m.beam((0,3.02,.15),(0,3.47,.15),.255,'Green',64)
for y in [3.02,3.42]:
 m.beam((0,y-.035,.15),(0,y+.035,.15),.31,'Steel',64)
 for i in range(8):
  a=i*math.tau/8;m.bolt((.281*math.cos(a),y-.039,.15+.281*math.sin(a)),.019,'y',-1)
m.ring((0,2.979,.15),.183,.016,'Dark','y',48)
m.box((1.75,1.28,1),(.48,.65,.3),'Coat',.035)
for x in [1.62,1.85]:m.beam((x,1.28,1.154),(x,1.28,1.20),.046,'Red' if x<1.7 else 'Indicator',40);m.ring((x,1.28,1.177),.056,.006,'Steel','z',40)
for x in [1.57,1.93]:
 for y in [1.03,1.53]:m.bolt((x,y,1.154),.009)
m.box((0,3.78,.962),(1.5,.28,.014),'Hazard',.006);m.text('PRESS / 04',(0,3.78,.974),.16,'Dark')
m.gauge((.95,3.83,.983),.108)
for x in [-.98,.98]:m.beam((x,.5,1.25),(x,2,1.25),.026,'Hazard',24)
# Pump/reservoir sits inside the existing plinth footprint.
m.box((.8,.58,-.78),(.72,.58,.6),'Green',.045)
m.beam((-.83,.55,-.82),(-.27,.55,-.82),.19,'Green',48)
for x in [-.78+i*.045 for i in range(11)]:m.ring((x,.55,-.82),.19,.011,'Steel','x',32)
m.box((.22,.65,-.77),(.34,.16,.25),'Steel',.012)
m.beam((-.27,.55,-.82),(.08,.55,-.82),.065,'Steel',32)
for x in [.14,.30]:m.bolt((x,.735,-.77),.022,'y')
for j in range(2):
 z=.01+j*.29
 m.beam((.19,3.2+j*.16,z),(.34,3.2+j*.16,z),.044,'Steel',6)
 m.curve([(.33,3.2+j*.16,z),(.60,3.30+j*.14,.55),(.88,3.30+j*.14,.96),(1.30,3.23+j*.10,1.00),(1.54+j*.065,3.05,.94),(1.54+j*.065,2.12,.43),(1.54+j*.065,.90,.10),(1.54+j*.065,.76,-.75),(1.48,.70,-1.00-j*.06),(.72,.70,-1.03-j*.06),(.44,.66,-.96),(.40,.65,-.77)],.026,'Rubber',10,12)
 m.beam((.25,.65,-.77),(.42,.65,-.77),.042,'Steel',6)
 for y in [1.1,2.2]:m.box((1.55,y,.39),(.20,.065,.20),'Steel',.012)
m.curve([(1.75,.95,1),(1.74,.75,.98),(1.52,.43,.80),(1.31,.36,.30)],.017,'Rubber',9,10)
m.label((1.75,1.47,1.155),.25,.075)
scratch(m,(0,1.181,1.06),1.4)
save(m)
