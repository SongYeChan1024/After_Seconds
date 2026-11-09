import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
for rad in [6,7,8,9,10,11]:
 reset();face=math.sqrt(rad*rad-3.65**2)-.16
 for y in [3.10,3.50]:
  wall=math.sqrt(rad*rad-y*y)-.035;z=face-wall
  box('Wall_Anchor',0,y,z/2,.26,.16,-z+.06,'Steel',.007);box('Anchor_Backplate',0,y,z+.012,.30,.20,.035,'Steel',.006)
  for x in [-.10,.10]:bolt(x,y,.033)
 box('Vertical_Mount',0,3.30,.035,.24,.58,.07,'Coat',.008);box('Cantilever',0,3.335,.29,.20,.07,.52,'Steel',.008)
 tube('Diagonal_Brace',[(0,3.08,.06),(0,3.30,.50)],.022,'Steel');box('Camera_Mount_Plate',0,3.30,.49,.30,.025,.28,'Steel',.006)
 tube('Camera_Power_Conduit',[(.11,3.61,.02),(.11,3.45,.02),(.11,3.39,.10),(.11,3.39,.48),(.08,3.30,.48)],.011,'Dark')
 save('CCTVWallMount_R'+str(rad),'Environment')
print('B3 CCTV mounts ready')
