"""1F stair copy with flush arrival threshold; B1 source asset stays unchanged."""
import sys,os,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from meshlib import Model
m=Model('FW_VBStairs18m')
for flight in range(10):
 direction=1 if flight%2==0 else -1;x=-.96 if direction==1 else .96;z0=-1.62*direction;y0=flight*1.8
 for i in range(12):
  y=y0+(i+1)*.15;z=z0+direction*(i+.5)*.27;m.box((x,y-.04,z),(1.5,.08,.27),'Steel');m.box((x,y-.115,z-direction*.123),(1.49,.07,.024),'Corrosion')
 for xx in [x-.78,x+.78]:
  m.beam((xx,y0-.08,z0),(xx,y0+1.8-.08,-z0),.055,'Corrosion',10)
  for i in [0,3,6,9,12]:m.beam((xx,y0+i*.15,z0+direction*i*.27),(xx,y0+i*.15+1.06,z0+direction*i*.27),.023,'Corrosion')
  for yy,r in [(1.06,.028),(.54,.016)]:m.beam((xx,y0+yy,z0),(xx,y0+1.8+yy,-z0),r,'Steel')
 y=y0+1.8;z=-z0+direction*.7;m.box((0,y-.08,z),(3.44,.16,1.4),'Steel')
 for xx in [-1.74,1.74]:m.beam((xx,y,z+direction*.65),(xx,y+1.07,z+direction*.65),.023,'Corrosion')
 for yy,r in [(1.07,.028),(.54,.016)]:
  if flight<9:m.beam((-1.74,y+yy,z+direction*.65),(1.74,y+yy,z+direction*.65),r,'Steel')
  else:
   for a,b in [(-1.74,-1.12),(1.12,1.74)]:m.beam((a,y+yy,z+direction*.65),(b,y+yy,z+direction*.65),r,'Steel')
  for xx in [-1.74,1.74]:m.beam((xx,y+yy,-z0),(xx,y+yy,z+direction*.65),r,'Steel')
for x in [-1.78,1.78]:
 for z in [-3.04,3.04]:m.box((x,9,z),(.12,18,.12),'Corrosion')
report=m.export(Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_20261113/candidate')
(HERE/'stair_model.json').write_text(json.dumps(report,indent=2))
