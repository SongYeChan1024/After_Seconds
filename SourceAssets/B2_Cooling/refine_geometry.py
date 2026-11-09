import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
src=(H/'build.py').read_text(encoding='utf8');a=src.index('# Continuous closed cooling loop');z=src.index("save('CoolingPipework')",a)+len("save('CoolingPipework')");reset();exec(src[a:z])
reset()
for x,z in [(-8.65,2.65),(3.05,7.25),(0,7.2)]:
 if x<0:
  cyl('WallLightBracket',(-10.34,2.5,z),(x,2.5,z),.025,'Steel',12);box('WallLightMount',-10.35,2.5,z,.04,.28,.24,'Steel',.007)
 else:
  cyl('TaskLightBoom',(x,3.28,5.6),(x,3.28,z),.025,'Steel',12);cyl('FixtureHanger',(x,3.28,z),(x,2.9,z),.025,'Steel',12)
save('ServiceLightSupports')
