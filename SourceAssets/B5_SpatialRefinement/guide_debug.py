import json,math
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
H=Path(__file__).resolve().parent;D=H.parents[1]/'Docs/검수/2026-11-08_B5_SpatialRefinement';g=json.loads((H/'guidance.json').read_text(encoding='utf8'));routes={r['id']:r for r in g['routes']}
a=np.array(routes['C01_FromVA']['points']);b=np.array(routes['VA_FromC01']['points']);dist=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2);i,j=np.unravel_index(np.argmin(dist),dist.shape);print('closest',a[i],b[j],dist[i,j])
im=Image.open(D/'C02_plan.png');d=ImageDraw.Draw(im);grid=json.loads((H/'grids.json').read_text())['C02']
for r in g['routes']:
 pts=[p for p in r['points'] if math.dist(p,[-22,18])<8]
 if len(pts)>1:d.line([(((p[0]+22)/.18+grid['half'])*5,((p[1]-18)/.18+grid['half'])*5) for p in pts],fill=g['destinations'][r['code']]['color'],width=2)
im.save(D/'C02_guides_debug.png')
