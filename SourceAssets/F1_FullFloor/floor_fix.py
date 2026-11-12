import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
manifest.update(json.loads((H/'models_environment.json').read_text(encoding='utf8')))
p=json.loads((H/'plan.json').read_text(encoding='utf8'));reset();vs=[];fs=[]
for tri in p['floorTriangles']:
 k=len(vs);vs.extend((x,0,z) for x,z in tri);fs.append((k+2,k+1,k))
mesh('ContinuousFloor',vs,fs,'Floor');save('GroundFloor','Environment',False)
