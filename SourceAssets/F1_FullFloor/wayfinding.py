import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
manifest.update(json.loads((H/'models_environment.json').read_text(encoding='utf8')));reset()
for words,pos,yaw,w in [('OFFICE  >',(-44,2.65,32.82),180,1.6),('<  LOADING',(44,2.65,-23.18),180,1.7),('<  DISPATCH',(44,2.65,32.82),180,1.7),('EXIT  >',(-17.25,3.75,-13.82),0,1.4)]:
 start=set(bpy.context.scene.objects);box('Sign',(0,0,0),(w,.35,.045),'Dark',.008);text('Letters',words,(0,0,.026),.14,'Paper');turn(set(bpy.context.scene.objects)-start,*pos,yaw)
save('Wayfinding','Environment',False)
