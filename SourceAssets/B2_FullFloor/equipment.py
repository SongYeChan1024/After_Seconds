import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
b.H=H/'Equipment';b.H.mkdir(exist_ok=True);b.manifest={}
def save(n,category='Props'):
 b.OUT=b.A/category/'B2';b.raw_export('BM_'+n);b.manifest['BM_'+n]['category']=category;(b.H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
# Fabricated dimensional mechanical equipment; all exposed fabricated edges use bevels.
reset()
for x in [-1,1]:box('SteelSkid',x,.09,0,.13,.18,1.6,'Steel',.012)
box('TransformerTank',0,1.15,0,1.55,1.9,1.1,'Teal',.045)
for x in [-1,1]:
 for k in range(13):box('CoolingFin',x,1.1,-.66+k*.11,.40,1.65,.035,'Steel',.008)
for x in [-.48,0,.48]:
 cyl('InsulatorCore',(x,2.08,0),(x,2.58,0),.075,'Paper',24)
 for y in [2.18,2.29,2.40,2.51]:cyl('InsulatorShed',(x,y-.025,0),(x,y+.025,0),.13,'Paper',24)
 cyl('TerminalLug',(x,2.58,0),(x,2.69,0),.045,'Steel',16)
 tube('CableToConduit',[(x,2.67,0),(x,2.80,-.42),(x,2.80,-.92),(x,.3,-.92)],.026,'Dark')
box('TerminalCabinet',.34,.84,.68,.74,1.04,.30,'Coat',.012);pull(.56,.92,.85,.15);display(-.22,1.45,.565,.50,.24,11)
for x in [-.58,.58]:
 for y in [.38,1.90]:cyl('TankBolt',(x,y,.553),(x,y,.58),.024,'Steel',6)
gauge(-.48,1.10,.67);save('PowerTransformer','Props')

reset()
box('Plinth',0,.10,0,2.6,.2,1.25,'Steel',.014);box('AirHandlingBody',0,1.27,0,2.50,2.16,1.1,'Coat',.025)
for x in [-.78,0,.78]:
 box('FilterFrame',x,1.35,.579,.73,1.83,.08,'Steel',.009)
 box('FilterMedia',x,1.35,.628,.64,1.72,.035,'Dark',.003)
 for k in range(20):box('PleatedFilter',x, .55+k*.083,.657,.61,.018,.022,'Steel',.003)
 for y in [.53,2.17]:
  for dx in [-.31,.31]:cyl('FrameFastener',(x+dx,y,.633),(x+dx,y,.673),.014,'Steel',6)
 pull(x,1.22,.70,.18)
box('DuctOutlet',0,2.42,-.10,.95,.28,.82,'Steel',.012)
display(0,2.28,.573,.62,.14,12);save('AirFilterSkid','Props')

reset()
for x in [-.72,.72]:box('FanFoot',x,.12,0,.20,.24,.85,'Steel',.008)
cyl('DuctBody',(0,1.27,-.47),(0,1.27,.47),1.1,'Steel',64)
cyl('FanRecess',(0,1.27,.475),(0,1.27,.49),1.02,'Dark',64)
for i in range(12):
 a=math.tau*i/12;vs=[]
 for rr,aa in [(.18,a),(.94,a+.15),(.98,a+.40),(.29,a+.48)]:vs.append((rr*math.cos(aa),1.27+rr*math.sin(aa),.515))
 mesh('FanBlade',vs,[(0,1,2,3)],'Steel',.004)
cyl('Hub',(0,1.27,.50),(0,1.27,.60),.23,'Teal',32)
for i in range(-8,9):
 x=i*.115;dy=math.sqrt(max(0,1.02**2-x*x));cyl('SafetyGridV',(x,1.27-dy,.65),(x,1.27+dy,.65),.006,'Steel',6)
 y=i*.115;dx=math.sqrt(max(0,1.02**2-y*y));cyl('SafetyGridH',(-dx,1.27+y,.65),(dx,1.27+y,.65),.006,'Steel',6)
tube('DuctLip',[(1.07*math.cos(math.tau*i/64),1.27+1.07*math.sin(math.tau*i/64),.63) for i in range(65)],.035,'Steel')
display(0,.18,.47,.55,.16,13);save('VentilationFan','Props')

reset()
for x in [-.85,.85]:box('WaterSkid',x,.08,0,.12,.16,1.4,'Steel',.008)
for x in [-.50,.50]:
 for z in [-.35,.35]:cyl('TankLeg',(x+(-.19 if z<0 else .19),.12,z),(x+(-.19 if z<0 else .19),.50,z),.04,'Steel',16)
 cyl('PressureVessel',(x,.45,0),(x,2.25,0),.43,'Steel',48)
 for y in [.55,1.18,2.15]:cyl('VesselBand',(x,y-.023,0),(x,y+.023,0),.45,'Teal',48)
 cyl('TopPort',(x,2.25,0),(x,2.47,0),.09,'Steel',24);flange(x,2.40,0,.09,'y')
 tube('FilterReturn',[(x,2.46,0),(x,2.65,0),(x,2.65,-.57),(x,.40,-.57)],.075,'Steel')
 tube('FilterSupply',[(x,.72,.40),(x,.72,.70),(x,.35,.70)],.065,'Steel');valve(x,.72,.70,.065);gauge(x,1.35,.48)
display(0,1.88,.46,.55,.19,14);save('WaterFilterSkid','Props')

reset()
for x in [-.85,.85]:box('TankSkid',x,.12,0,.15,.24,1.8,'Steel',.01)
cyl('SealedProcessTank',(0,.28,0),(0,2.2,0),.91,'Teal',64)
for y in [.45,1.25,2.12]:cyl('TankSeam',(0,y-.025,0),(0,y+.025,0),.93,'Steel',64)
cyl('InspectionLid',(0,2.20,0),(0,2.32,0),.43,'Steel',48)
for i in range(12):
 a=math.tau*i/12;x,z=.36*math.cos(a),.36*math.sin(a);cyl('LidBolt',(x,2.32,z),(x,2.345,z),.025,'Steel',6)
tube('Outlet',[(0,.5,.85),(0,.5,1.1),(.55,.5,1.1)],.10,'Steel');flange(.35,.5,1.1,.10,'x')
tube('Vent',[(0,2.32,0),(0,2.75,0),(.62,2.75,0),(.62,2.75,-.65)],.065,'Steel');gauge(-.30,1.45,.91)
display(.15,1.7,.924,.60,.24,15);save('SealedProcessTank','Props')

reset()
for x in [-.89,.89]:
 for z in [-.35,.35]:box('RackPost',x,1.15,z,.055,2.30,.055,'Steel',.004)
for y in [.12,.65,1.18,1.71,2.24]:
 box('RackShelf',0,y,0,1.84,.045,.80,'Steel',.006)
 for z in [-.39,.39]:box('ShelfFold',0,y+.045,z,1.84,.09,.025,'Teal',.003)
for k,y in enumerate([.15,.68,1.21,1.74]):
 for j in range(3):
  x=-.56+j*.56
  if k%2==0:
   box('ServiceBox',x,y+.17,0,.45,.34,.55,'Coat',.014);display(x,y+.20,.281,.30,.13,16);pull(x,y+.28,.30,.12)
  else:
   for i in range(2):cyl('SpareCoupling',(x,y+.12,-.12+i*.27),(x,y+.16,-.12+i*.27),.18,'Steel',32)
display(0,2.19,.418,.80,.12,16);save('MechanicalSparesRack','Props')
print('MECHANICAL_EQUIPMENT_READY',flush=True)
