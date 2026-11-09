import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
reset()
for x in [-.78,.78]:box('SkidRail',x,.08,0,.12,.16,1.1,'Steel',.009)
for z in [-.43,.43]:box('SkidCross',0,.08,z,1.75,.16,.10,'Steel',.007)
for i in range(26):box('HeatTransferPlate',0,.99,-.40+i*.030,1.22,1.40,.018,'Steel',.004)
for z in [-.46,.46]:
 box('EndPlate',0,.99,z,1.40,1.58,.09,'Teal',.018)
 for x in [-.58,.58]:
  for y in [.36,1.58]:cyl('TieRod',(x,y,-.57),(x,y,.57),.025,'Steel',12);flange(x,y,z,.067)
for x in [-.38,.38]:
 for y in [.62,1.35]:cyl('ProcessSocket',(x,y,.50),(x,y,.77),.075,'Steel',24);flange(x,y,.76,.075)
display(0,1.5,.52,.38,.16,7)
save('PlateHeatExchanger','Props')
reset();cabinet(1.12,1.95,.56,'doors','Teal')
for x in [-.27,.27]:
 box('InverterCase',x,1.37,.34,.40,.61,.15,'Dark',.012);vent(x,1.18,.423,.31,.10)
 display(x,1.50,.425,.23,.16,1)
 for dx,c in [(-.07,'Indicator'),(.07,'Red')]:cyl('PushButton',(x+dx,1.30,.42),(x+dx,1.30,.445),.027,c,16)
 for k in range(3):cyl('CableGland',(x+(k-1)*.1,.15,-.3),(x+(k-1)*.1,.15,-.42),.025,'Rubber',12)
display(0,1.82,.296,.65,.12,7)
save('PumpDriveCabinet','Props')
reset()
for x in [-.46,.46]:
 box('FrameFoot',x,.035,0,.24,.07,.55,'Steel',.006);box('PanelLeg',x,.58,-.13,.07,1.1,.07,'Steel',.004)
box('ManifoldBack',0,1.02,-.11,1.1,.95,.08,'Teal',.012)
for x in [-.32,0,.32]:
 cyl('CircuitPipe',(x,.36,.08),(x,1.37,.08),.035,'Steel',16);gauge(x,1.19,.17)
 cyl('ValveStem',(x,.72,.08),(x,.72,.27),.025,'Steel',16)
 tube('ValveWheel',[(x+.095*math.cos(math.tau*i/24),.72+.095*math.sin(math.tau*i/24),.28) for i in range(25)],.012,'Red')
 for i in range(3):
  a=math.tau*i/3;cyl('Spoke',(x,.72,.28),(x+.09*math.cos(a),.72+.09*math.sin(a),.28),.009,'Steel',8)
display(0,1.43,-.058,.55,.12,8)
save('UpperValveStation','Props')
reset()
for x in [-.84,.84]:
 for z in [-.33,.33]:box('BenchLeg',x,.46,z,.065,.92,.065,'Steel',.004);box('BenchFoot',x,.025,z,.13,.05,.13,'Rubber',.005)
box('LowerShelf',0,.22,0,1.76,.04,.72,'Steel',.006);box('BenchTop',0,.94,0,1.9,.09,.88,'Plate',.012)
box('DrawerUnit',-.57,.73,0,.50,.30,.71,'Teal',.008)
for y in [.65,.80]:box('DrawerFront',-.57,y,.375,.46,.13,.035,'Coat',.005);pull(-.57,y,.403,.23)
box('ToolBackboard',0,1.32,-.39,1.78,.64,.045,'Steel',.008)
for i in range(9):
 x=-.70+i*.17;cyl('ToolHook',(x,1.42,-.35),(x,1.42,-.30),.01,'Steel',8)
 if i%2==0:
  box('SpannerHandle',x,1.27,-.29,.032,.24,.014,'Steel',.004);cyl('SpannerHead',(x,1.40,-.30),(x,1.40,-.28),.04,'Steel',12)
 else:box('DriverGrip',x,1.24,-.29,.04,.13,.03,'Red',.008);cyl('DriverShaft',(x,1.30,-.29),(x,1.44,-.29),.008,'Steel',8)
# vice jaws and lead screw, repair pieces in a shallow tray
box('ViceBase',-.62,1.015,.10,.31,.06,.28,'Teal',.008)
for x in [-.72,-.51]:box('ViceJaw',x,1.11,.10,.07,.18,.21,'Steel',.006)
cyl('ViceScrew',(-.82,1.05,.10),(-.35,1.05,.10),.023,'Steel',16);cyl('ViceBar',(-.36,.96,.10),(-.36,1.18,.10),.009,'Steel',10)
box('PartsTray',.42,1.0,.05,.70,.025,.50,'Dark',.005)
for z in [-.20,.30]:box('TrayEdge',.42,1.03,z,.70,.06,.018,'Steel',.003)
for x in [.07,.77]:box('TrayEdge',x,1.03,.05,.018,.06,.50,'Steel',.003)
for x,z,r in [(.25,.05,.08),(.52,.12,.10),(.65,-.1,.05)]:cyl('SealRing',(x,1.02,z),(x,1.038,z),r,'Rubber',24);cyl('SealCenter',(x,1.04,z),(x,1.042,z),r*.65,'Dark',24)
for i in range(5):cyl('LooseBolt',(.16+i*.11,1.04,-.11),(.16+i*.11,1.04,-.02),.011,'Steel',6)
display(.35,1.49,-.36,.48,.21,9)
save('MaintenanceBench','Props')
reset()
for x in [-.32,.32]:
 for z in [-.23,.23]:cyl('Caster',(x-.04,.09,z),(x+.04,.09,z),.075,'Rubber',20);box('CasterFork',x,.17,z,.06,.11,.10,'Steel',.004)
box('CartBody',0,.51,0,.75,.64,.57,'Teal',.012)
for y in [.29,.43,.57,.71]:box('Drawer',0,y,.30,.68,.12,.035,'Coat',.005);pull(0,y,.33,.44)
box('TrayTop',0,.86,0,.79,.045,.62,'Steel',.006)
for x in [-.39,.39]:box('TrayRim',x,.91,0,.025,.09,.62,'Steel',.003)
tube('PushHandle',[(-.39,.76,-.32),(-.39,1.02,-.32),(.39,1.02,-.32),(.39,.76,-.32)],.02,'Steel')
box('ToolCase',-.17,.94,-.03,.30,.12,.28,'Dark',.012);pull(-.17,1.015,-.03,.16)
cyl('OilCan',(.2,.89,.06),(.2,1.06,.06),.06,'Hazard',24);tube('OilNozzle',[(.2,1.06,.06),(.20,1.12,.08),(.2,1.12,.18)],.008,'Steel')
save('ToolTrolley','Props')
reset()
box('WallBackplate',0,0,-.045,.20,.36,.055,'Steel',.012);box('RedLens',0,0,.002,.13,.27,.062,'RedLamp',.04)
for x in [-.075,.075]:cyl('GuardWire',(x,-.17,.07),(x,.17,.07),.008,'Steel',10)
for y in [-.17,-.06,.06,.17]:cyl('CageCross',(-.08,y,.07),(.08,y,.07),.008,'Steel',10)
save('CagedRedLamp')
