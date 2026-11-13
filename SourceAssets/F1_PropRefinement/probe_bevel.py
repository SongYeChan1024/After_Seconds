import bpy,bmesh
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh import Model
m=Model('test');m.box((0,0,0),(1,1,1),'Green',.1)
print('BEVEL VERTS',m.v[:20]);print('BOUNDS',[[min(v[i] for v in m.v),max(v[i] for v in m.v)] for i in range(3)])
bm=bmesh.new();bmesh.ops.create_cube(bm,size=1);bm.normal_update();bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.1,segments=5,affect='EDGES');print('REFERENCE', [tuple(v.co) for v in bm.verts][:20])
