import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
manifest.update(json.loads((H/'models_environment.json').read_text(encoding='utf8')))
p=json.loads((H/'plan.json').read_text(encoding='utf8'))
for r in p['rooms']:
 if r['id'] not in ['C01','C02']:continue
 reset();x,z,w,d,h=[r[k] for k in ['x','z','w','d','h']];rise=1.8
 for side in [-1,1]:
  pts=[(x,h+rise+.3,z-d/2-.35),(x+side*(w/2+.35),h+.26,z-d/2-.35),(x+side*(w/2+.35),h+.26,z+d/2+.35),(x,h+rise+.3,z+d/2+.35)];vs=pts+[(xx,yy-.14,zz) for xx,yy,zz in pts];mesh('RoofPanel',vs,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'Green')
 # Closed gable prisms with a thin eave closure along the side walls.
 for zz in [-d/2,d/2]:
  pts=[(x-w/2,h,z+zz),(x+w/2,h,z+zz),(x+w/2,h+.3,z+zz),(x,h+rise+.3,z+zz),(x-w/2,h+.3,z+zz)];vs=pts+[(xx,yy,zzz+.10) for xx,yy,zzz in pts];fs=[(0,1,2,3,4),(9,8,7,6,5)]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)];mesh('Gable',vs,fs,'Coat')
 for xx in [-w/2,w/2]:box('EaveClosure',(x+xx,h+.12,z),(.15,.24,d),'Coat',0)
 save(r['id']+'_Roof','Environment',False)
reset()
signs=[('PRODUCTION / 04',(-12,5.25,13.82),180,3.2),('LOADING / DISPATCH',(24,4.65,1.82),180,3.2),('STAFF OFFICE',(-16,2.9,31.82),180,1.9),('EXIT / VEHICLE CHECK',(-30,2.95,-32.82),0,2.9),('STAIR A / 1F',(-44,3.45,23.18),0,1.9),('STAIR B / 1F',(44,3.45,-32.82),0,1.9),('CARGO LIFT / 1F',(44,4.0,23.18),0,2.2)]
for words,pos,yaw,w in signs:
 start=set(bpy.context.scene.objects);box('SignBacking',(0,0,0),(w,.40,.045),'Dark',.008);box('SignRim',(0,0,-.029),(w+.06,.46,.02),'Steel',.008);text('SignLetters',words,(0,0,.025),.135,'Paper');turn(set(bpy.context.scene.objects)-start,*pos,yaw)
save('OperationalSigns','Environment',False)
