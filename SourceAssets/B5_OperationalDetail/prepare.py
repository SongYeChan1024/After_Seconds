from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];old=R/'SourceAssets/B5_SpatialRefinement'
s=(old/'common.py').read_text(encoding='utf-8').replace("('RD_','SC_','SR_')","('RD_','SC_','SR_','SF_','OD_')")
(H/'common.py').write_text(s,encoding='utf-8')
for fn,cl in [('Grid.cs','Grid'),('Walk.cs','Walk')]:
 s=(old/fn).read_text(encoding='utf-8').replace('B5_SpatialRefinement','B5_OperationalDetail').replace('Spatial'+cl,'Operational'+cl)
 (H/fn).write_text(s,encoding='utf-8')
(H/'plan.json').write_text((old/'plan.json').read_text(encoding='utf-8'),encoding='utf-8')
print('Helpers ready')
